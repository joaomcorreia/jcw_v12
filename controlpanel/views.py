import json
import time
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.db.models import Count, Q

from core.models import (
    Feature,
    MediaAsset,
    Page,
    PageSection,
    Plan,
    PlanSEOSettings,
    RightSidebarPanel,
    SectionContent,
    Site,
    Subscription,
    WebsiteTemplate,
)
from core.tenant import tenant_site_url
from core.seo_utils import build_language_url_for_path
from controlpanel.models import ManagedSite


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


def _control_panel_overview_context():
    tenant_qs = Site.objects.filter(is_main=False)
    last_tenant = tenant_qs.order_by("-created_at").first()
    return {
        "stats": {
            "total_tenants": tenant_qs.count(),
            "total_users": get_user_model().objects.count(),
            "total_active_plans": Plan.objects.filter(is_active=True).count(),
            "total_active_subscriptions": Subscription.objects.filter(
                status=Subscription.STATUS_ACTIVE
            ).count(),
        },
        "last_tenant": last_tenant,
    }


class WebsiteTemplateForm(forms.ModelForm):
    languages = forms.CharField(required=False)
    sections = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 10}))

    class Meta:
        model = WebsiteTemplate
        fields = ("name", "slug", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        if self.instance and self.instance.pk:
            self.fields["languages"].initial = ",".join(self.instance.languages or [])
            self.fields["sections"].initial = json.dumps(self.instance.sections or [], indent=2)
        for field_name in ("name", "slug", "description", "languages", "sections"):
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.setdefault("class", "dashboard-input")
        self.fields["languages"].help_text = _("Comma-separated, e.g. nl,en,fr")
        self.fields["sections"].help_text = _("Paste valid JSON for sections")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or ""
        name = self.cleaned_data.get("name") or ""
        base = slug or slugify(name)
        if not base:
            raise ValidationError(_("Provide a name or slug."))
        base = base[:80]
        candidate = base
        index = 1
        while WebsiteTemplate.objects.filter(slug=candidate).exclude(pk=self.instance.pk).exists():
            candidate = f"{base}-{index}"
            index += 1
        return candidate

    def clean_languages(self):
        raw = self.cleaned_data.get("languages") or ""
        items = [part.strip() for part in raw.split(",") if part.strip()]
        return items or ["nl", "en", "fr", "de", "es", "pt"]

    def clean_sections(self):
        raw = self.cleaned_data.get("sections") or "[]"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(_("Sections must be valid JSON.")) from exc
        if not isinstance(data, list):
            raise ValidationError(_("Sections must be a JSON array."))
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.languages = self.cleaned_data["languages"]
        instance.sections = self.cleaned_data["sections"]
        if commit:
            instance.save()
        return instance


@staff_required
def dashboard(request):
    context = {
        "counts": {
            "pages": Page.objects.count(),
            "sections": PageSection.objects.count(),
            "sidebar_panels": RightSidebarPanel.objects.count(),
            "features": Feature.objects.count(),
            "managed_sites": ManagedSite.objects.count(),
        },
        "links": {
            "pages": reverse("admin:core_page_changelist"),
            "sections": reverse("admin:core_pagesection_changelist"),
            "sidebar_panels": reverse("admin:core_rightsidebarpanel_changelist"),
            "features": reverse("admin:core_feature_changelist"),
            "managed_sites": reverse("admin:controlpanel_managedsite_changelist"),
        },
        "media_asset": MediaAsset.objects.order_by("-created_at").first(),
    }
    return render(request, "controlpanel/dashboard.html", context)


@staff_required
def home(request):
    return render(request, "controlpanel/home.html", _control_panel_overview_context())


@staff_required
def website_builder(request):
    main_site = Site.objects.filter(is_main=True).first()
    if not main_site:
        messages.error(request, _("Main site not found. Run seed_pages first."))
        return redirect("control_panel:home")

    page, _ = Page.objects.get_or_create(
        site=main_site,
        slug="home",
        defaults={"is_active": True, "template_key": main_site.template_key},
    )
    section, _ = PageSection.objects.get_or_create(
        page=page,
        key="home.hero",
        defaults={"order": 0, "is_visible": True},
    )
    content, _ = SectionContent.objects.get_or_create(section=section)

    lang = get_language()
    if hasattr(content, "set_current_language"):
        content.set_current_language(lang)
    if hasattr(content, "has_translation") and not content.has_translation(lang):
        content.heading = ""
        content.subheading = ""
        content.cta_primary_text = ""
        content.cta_primary_url = ""
        content.cta_secondary_text = ""
        content.cta_secondary_url = ""
        content.save()

    view_mode = (request.GET.get("view") or "desktop").strip().lower()
    if view_mode not in {"desktop", "mobile"}:
        view_mode = "desktop"

    if request.method == "POST":
        content.heading = (request.POST.get("hero_title") or "").strip()
        content.subheading = (request.POST.get("hero_subtitle") or "").strip()
        content.cta_primary_text = (request.POST.get("hero_primary_cta_label") or "").strip()
        content.cta_primary_url = (request.POST.get("hero_primary_cta_url") or "").strip()
        content.cta_secondary_text = (request.POST.get("hero_secondary_cta_label") or "").strip()
        content.cta_secondary_url = (request.POST.get("hero_secondary_cta_url") or "").strip()
        content.save()
        messages.success(request, _("Homepage hero saved."))
        cache_buster = int(time.time())
        return redirect(
            f"{reverse('control_panel:website_builder')}?v={cache_buster}&view={view_mode}"
        )

    preview_url = build_language_url_for_path(request, lang, "/")
    cache_buster = request.GET.get("v")
    parts = urlsplit(preview_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["embed"] = "1"
    if cache_buster:
        query["v"] = cache_buster
    preview_url = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query, doseq=True), parts.fragment)
    )

    toggle_query_base = {}
    if cache_buster:
        toggle_query_base["v"] = cache_buster
    toggle_query_desktop = urlencode({**toggle_query_base, "view": "desktop"})
    toggle_query_mobile = urlencode({**toggle_query_base, "view": "mobile"})

    context = {
        "preview_url": preview_url,
        "lang": lang,
        "view_mode": view_mode,
        "toggle_query_desktop": toggle_query_desktop,
        "toggle_query_mobile": toggle_query_mobile,
        "hero_title": content.safe_translation_getter("heading", default="", language_code=lang),
        "hero_subtitle": content.safe_translation_getter("subheading", default="", language_code=lang),
        "hero_primary_cta_label": content.safe_translation_getter("cta_primary_text", default="", language_code=lang),
        "hero_primary_cta_url": content.safe_translation_getter("cta_primary_url", default="", language_code=lang),
        "hero_secondary_cta_label": content.safe_translation_getter("cta_secondary_text", default="", language_code=lang),
        "hero_secondary_cta_url": content.safe_translation_getter("cta_secondary_url", default="", language_code=lang),
    }
    return render(request, "controlpanel/website_builder.html", context)


@staff_required
def domains_hosting(request):
    return render(request, "controlpanel/domains_hosting.html")




@staff_required
def users(request):
    return render(request, "controlpanel/users.html")


@staff_required
def billing(request):
    return render(request, "controlpanel/billing.html")


@staff_required
def content_map(request):
    lang = request.LANGUAGE_CODE or get_language()
    main_site = Site.objects.filter(is_main=True).first()
    pages = (
        Page.objects.filter(Q(site__isnull=True) | Q(site=main_site))
        .prefetch_related("translations", "sections__content")
        .order_by("slug")
    )
    duplicate_keys = set(
        PageSection.objects.filter(page__in=pages)
        .values("page_id", "key")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .values_list("page_id", "key")
    )

    rows = []
    for page in pages:
        if hasattr(page, "set_current_language"):
            page.set_current_language(lang)
        page_title = (
            page.safe_translation_getter("title", any_language=True)
            if hasattr(page, "safe_translation_getter")
            else ""
        )
        page_title = page_title or page.slug
        page_path = "/" if page.slug == "home" else f"/{page.slug}/"
        page_url = build_language_url_for_path(request, lang, page_path)

        sections = list(page.sections.all().order_by("order", "id"))
        if not sections:
            changelist_url = reverse("admin:core_pagesection_changelist")
            query = urlencode({"page__id__exact": page.id})
            rows.append(
                {
                    "page_slug": page.slug,
                    "page_title": page_title,
                    "section_key": _("(no sections)"),
                    "status": _("Missing"),
                    "status_class": "dashboard-badge--warning",
                    "edit_section_url": f"{changelist_url}?{query}",
                    "page_url": page_url,
                }
            )
            continue

        for section in sections:
            is_duplicate = (section.page_id, section.key) in duplicate_keys
            has_content = bool(getattr(section, "content", None))
            if is_duplicate:
                status = _("Duplicate")
                status_class = "dashboard-badge--warning"
            elif not has_content:
                status = _("Missing")
                status_class = "dashboard-badge--warning"
            else:
                status = _("OK")
                status_class = "dashboard-badge--success"

            edit_section_url = ""
            if hasattr(section, "content") and section.content:
                edit_section_url = reverse(
                    "admin:core_sectioncontent_change", args=[section.content.id]
                )
            else:
                edit_section_url = reverse(
                    "admin:core_pagesection_change", args=[section.id]
                )

            if is_duplicate:
                query = urlencode({"page__id__exact": section.page_id, "key": section.key})
                edit_section_url = f"{reverse('admin:core_pagesection_changelist')}?{query}"

            rows.append(
                {
                    "page_slug": page.slug,
                    "page_title": page_title,
                    "section_key": section.key,
                    "status": status,
                    "status_class": status_class,
                    "edit_section_url": edit_section_url,
                    "page_url": page_url,
                }
            )

    return render(
        request,
        "controlpanel/content_map.html",
        {
            "rows": rows,
        },
    )


@staff_required
def tenants(request):
    lang = request.LANGUAGE_CODE or get_language() or "en"
    sites = Site.objects.select_related("owner", "plan").order_by("-created_at")
    host = request.get_host() or ""
    current_port = ""
    if ":" in host:
        current_port = host.split(":", 1)[1]

    tenant_rows = []
    for site in sites:
        try:
            dashboard_url = tenant_site_url(site, f"/{lang}/dashboard/", request=request)
            site_url = tenant_site_url(site, f"/{lang}/", request=request)
        except ValueError:
            dashboard_url = ""
            site_url = ""

        domain_label = "--"
        if site.subdomain:
            domain_label = f"{site.subdomain}.{settings.MAIN_DOMAIN}"
            if current_port:
                domain_label = f"{domain_label}:{current_port}"

        tenant_rows.append(
            {
                "site": site,
                "domain_label": domain_label,
                "dashboard_url": dashboard_url,
                "site_url": site_url,
            }
        )
    return render(request, "controlpanel/tenants.html", {"tenant_rows": tenant_rows})


class PlanForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "dashboard-input"}))

    class Meta:
        model = Plan
        fields = ("slug", "is_active")
        widgets = {
            "slug": forms.TextInput(attrs={"class": "dashboard-input"}),
        }

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip().lower()
        if not slug:
            raise ValidationError(_("Slug is required."))
        return slug

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            name = self.instance.safe_translation_getter("name", any_language=True)
            if name:
                self.fields["name"].initial = name

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.key = instance.slug
        lang = get_language() or "en"
        if hasattr(instance, "set_current_language"):
            instance.set_current_language(lang)
            instance.name = self.cleaned_data.get("name") or instance.key
        if commit:
            instance.save()
        return instance


class TenantPlanForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ("plan",)
        widgets = {
            "plan": forms.Select(attrs={"class": "dashboard-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = Plan.objects.filter(is_active=True).order_by("sort_order", "key")


@staff_required
def plans_list(request):
    plans = Plan.objects.select_related("seo_settings").order_by("sort_order", "key")
    return render(request, "controlpanel/plans_list.html", {"plans": plans})


@staff_required
def plans_create(request):
    if request.method == "POST":
        plan_form = PlanForm(request.POST)
        if plan_form.is_valid():
            plan = plan_form.save()
            PlanSEOSettings.objects.get_or_create(plan=plan)
            messages.success(request, _("Plan created."))
            return redirect("control_panel:plans_list")
    else:
        plan_form = PlanForm()
    return render(
        request,
        "controlpanel/plans_form.html",
        {"plan_form": plan_form, "is_create": True},
    )


@staff_required
def plans_edit(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    is_frozen = plan.is_frozen
    if request.method == "POST":
        if is_frozen:
            messages.error(request, _("This plan is frozen and cannot be edited."))
            return redirect("control_panel:plans_list")
        plan_form = PlanForm(request.POST, instance=plan)
        if plan_form.is_valid():
            plan_form.save()
            messages.success(request, _("Plan updated."))
            return redirect("control_panel:plans_list")
    else:
        plan_form = PlanForm(instance=plan)
    if is_frozen:
        for field in plan_form.fields.values():
            field.disabled = True
    return render(
        request,
        "controlpanel/plans_form.html",
        {
            "plan_form": plan_form,
            "plan_obj": plan,
            "is_create": False,
            "is_frozen": is_frozen,
        },
    )


@staff_required
def plans_freeze(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == "POST":
        plan.is_frozen = True
        plan.save(update_fields=["is_frozen"])
        messages.success(request, _("Plan frozen."))
    return redirect("control_panel:plans_list")


@staff_required
def tenant_edit(request, tenant_id):
    site = get_object_or_404(Site, id=tenant_id)
    if request.method == "POST":
        form = TenantPlanForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, _("Tenant updated."))
            return redirect("control_panel:tenants")
    else:
        form = TenantPlanForm(instance=site)
    return render(
        request,
        "controlpanel/tenant_edit.html",
        {"site": site, "form": form},
    )


@staff_required
def tenant_impersonate(request, tenant_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Impersonation is restricted to superusers.")

    site = Site.objects.filter(id=tenant_id).first()
    if site and not site.is_main:
        request.session["impersonate_tenant_id"] = site.id
    lang = get_language() or "en"
    try:
        target = tenant_site_url(site, f"/{lang}/dashboard/", request=request)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return redirect(target)


@staff_required
def tenant_stop_impersonate(request):
    if "impersonate_tenant_id" in request.session:
        del request.session["impersonate_tenant_id"]
    return redirect("control_panel:tenants")


@staff_required
def templates_list(request):
    templates = WebsiteTemplate.objects.order_by("-updated_at", "-created_at")
    return render(request, "controlpanel/templates_list.html", {"templates": templates})


@staff_required
def templates_create(request):
    if request.method == "POST":
        form = WebsiteTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("control_panel:templates_list")
    else:
        form = WebsiteTemplateForm()
    return render(request, "controlpanel/templates_form.html", {"form": form})


@staff_required
def templates_edit(request, template_id):
    template = get_object_or_404(WebsiteTemplate, id=template_id)
    if request.method == "POST":
        form = WebsiteTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect("control_panel:templates_list")
    else:
        form = WebsiteTemplateForm(instance=template)
    return render(
        request,
        "controlpanel/templates_form.html",
        {"form": form, "template_obj": template},
    )


@staff_required
def templates_toggle_publish(request, template_id):
    template = get_object_or_404(WebsiteTemplate, id=template_id)
    if request.method == "POST":
        template.is_published = not template.is_published
        template.save(update_fields=["is_published", "updated_at"])
    return redirect("control_panel:templates_list")
