import json

from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext as _

from core.models import Feature, MediaAsset, Page, PageSection, RightSidebarPanel, Site, WebsiteTemplate
from controlpanel.models import ManagedSite


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


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
    return render(request, "controlpanel/home.html")


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
def tenants(request):
    sites = Site.objects.select_related("owner").order_by("-created_at")
    return render(request, "controlpanel/tenants.html", {"sites": sites})


@staff_required
def tenant_impersonate(request, tenant_id):
    site = Site.objects.filter(id=tenant_id).first()
    if site:
        request.session["impersonate_tenant_id"] = site.id
    return redirect("core:dashboard")


@staff_required
def tenant_stop_impersonate(request):
    if "impersonate_tenant_id" in request.session:
        del request.session["impersonate_tenant_id"]
    return redirect("controlpanel:tenants")


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
            return redirect("controlpanel:templates_list")
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
            return redirect("controlpanel:templates_list")
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
    return redirect("controlpanel:templates_list")
