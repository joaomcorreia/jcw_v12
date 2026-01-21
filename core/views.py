from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.conf import settings
from django.utils.text import slugify

from core.models import BlogCategory, BlogPost, Page, PageSection, Plan, SectionContent, Site, WebsiteTemplate
from core.services.blog import localize_categories, localize_posts
from core.services.drafts import (
    clear_draft_site,
    ensure_draft_site,
    get_draft_site,
    save_draft_site,
)
from core.services.features import get_active_subscription
from core.services.pages import get_page_with_sections, get_sidebar_panel
from core.services.site_settings import get_site_settings
from core.tenant import get_public_tenant


def render_page(request, slug, template_name, extra_context=None):
    page, sections_by_key = get_page_with_sections(slug)
    if page:
        request.current_page = page
    sidebar_panel = get_sidebar_panel(slug)
    plans = None
    subscription = None
    if slug in {
        "billing",
        "billing-checkout",
        "billing-success",
        "billing-cancel",
        "billing-portal",
    }:
        plans = list(Plan.objects.filter(is_active=True).order_by("sort_order", "key"))
        lang = get_language()
        for plan in plans:
            plan.set_current_language(lang)
        subscription = get_active_subscription()
    context = {
        "page": page,
        "sections_by_key": sections_by_key,
        "sidebar_panel": sidebar_panel,
        "plans": plans,
        "subscription": subscription,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def _build_nav_pages(site):
    pages = (
        Page.objects.filter(site=site, is_active=True)
        .prefetch_related("translations")
        .order_by("slug")
    )
    lang = get_language()
    nav_pages = []
    for page in pages:
        if hasattr(page, "set_current_language"):
            page.set_current_language(lang)
        title = None
        if hasattr(page, "safe_translation_getter"):
            title = page.safe_translation_getter("title", any_language=True)
        title = title or getattr(page, "title", None) or page.slug
        nav_pages.append({"slug": page.slug, "title": title})
    nav_pages.sort(key=lambda item: (item["slug"] != "home", item["slug"]))
    return nav_pages


def _build_sections(page):
    sections = []
    for section in page.sections.all().order_by("order", "id"):
        content = getattr(section, "content", None)
        data = content.config_json if content else {}
        section_type = section.key.split(".")[-1] if section.key else "unknown"
        sections.append(
            {
                "key": section.key,
                "type": section_type,
                "data": data,
            }
        )
    return sections


def home(request):
    site = get_public_tenant(request)
    if not site:
        return render(request, "site/home.html", {"sections": []})

    page = (
        Page.objects.filter(site=site, slug="home", is_active=True)
        .prefetch_related("translations", "sections__content__translations")
        .first()
    )
    if not page:
        return render(request, "site/home.html", {"sections": []})

    lang = get_language()
    if hasattr(page, "set_current_language"):
        page.set_current_language(lang)
    page_title = getattr(page, "title", None) or _("Home")
    nav_pages = _build_nav_pages(site)
    sections = _build_sections(page)
    return render(
        request,
        "site/page.html",
        {
            "sections": sections,
            "page_title": page_title,
            "nav_pages": nav_pages,
        },
    )


def public_page(request, slug):
    site = get_public_tenant(request)
    if not site:
        return render(request, "site/home.html", {"sections": []})

    page = (
        Page.objects.filter(site=site, slug=slug, is_active=True)
        .prefetch_related("translations", "sections__content__translations")
        .first()
    )
    if not page:
        return render(request, "site/404.html", status=404)

    lang = get_language()
    if hasattr(page, "set_current_language"):
        page.set_current_language(lang)
    page_title = getattr(page, "title", None) or page.slug
    nav_pages = _build_nav_pages(site)
    sections = _build_sections(page)
    return render(
        request,
        "site/page.html",
        {
            "sections": sections,
            "page_title": page_title,
            "nav_pages": nav_pages,
        },
    )


def websites(request):
    return render_page(request, "websites", "core/websites.html")


def services(request):
    return render_page(request, "services", "core/services.html")


def pos_systems(request):
    return render_page(request, "pos-systems", "core/pos_systems.html")


def pos_systems_retail(request):
    return render_page(request, "pos-systems-retail", "core/pos_systems.html")


def pos_systems_hospitality(request):
    return render_page(
        request, "pos-systems-hospitality", "core/pos_systems.html"
    )


def pos_systems_services(request):
    return render_page(request, "pos-systems-services", "core/pos_systems.html")


def pos_systems_compare(request):
    return render_page(request, "pos-systems-compare", "core/pos_systems.html")


def pos_systems_faq(request):
    return render_page(request, "pos-systems-faq", "core/pos_systems.html")


def help_center(request):
    return render_page(request, "help-center", "core/help_center.html")


def blog_index(request):
    now = timezone.now()
    posts = (
        BlogPost.objects.filter(is_published=True, published_at__lte=now)
        .select_related("category")
        .order_by("-published_at")
    )
    categories = BlogCategory.objects.filter(is_active=True).order_by("slug")
    lang = get_language()
    localize_posts(posts, lang)
    localize_categories(categories, lang)
    return render(
        request,
        "core/blog_index.html",
        {
            "posts": posts,
            "categories": categories,
            "seo_title": _("Blog"),
            "seo_description": _("News and updates from Just Code Works."),
        },
    )


def blog_detail(request, slug):
    now = timezone.now()
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_published=True,
        published_at__lte=now,
    )
    lang = get_language()
    localize_posts([post], lang)
    return render(
        request,
        "core/blog_detail.html",
        {
            "post": post,
            "seo_title": post.localized_title or _("Blog"),
            "seo_description": post.localized_excerpt,
        },
    )


def print_lab(request):
    return render_page(request, "print-lab", "core/print_lab.html")


def print_lab_products(request):
    return render_page(request, "print-lab-products", "core/print_lab_products.html")


def print_lab_how_it_works(request):
    return render_page(request, "print-lab-how-it-works", "core/print_lab_how_it_works.html")


def print_lab_faq(request):
    return render_page(request, "print-lab-faq", "core/print_lab_faq.html")


def billing(request):
    return render_page(request, "billing", "core/billing.html")


def billing_checkout(request):
    return render_page(request, "billing-checkout", "core/billing_checkout.html")


def billing_success(request):
    return render_page(request, "billing-success", "core/billing_success.html")


def billing_cancel(request):
    return render_page(request, "billing-cancel", "core/billing_cancel.html")


def billing_portal(request):
    return render_page(request, "billing-portal", "core/billing_portal.html")


def printful(request):
    return render_page(request, "printful", "core/printful.html")


def printful_products(request):
    return render_page(request, "printful-products", "core/printful_products.html")


def printful_orders(request):
    return render_page(request, "printful-orders", "core/printful_orders.html")


def products_index(request):
    return render_page(request, "products", "core/product_page.html")


def product_websites(request):
    return render_page(request, "products-websites", "core/product_page.html")


def product_seo(request):
    return render_page(request, "products-seo", "core/product_page.html")


def product_print_studio(request):
    return render_page(request, "products-print-studio", "core/product_page.html")


def product_pos_systems(request):
    return render_page(request, "products-pos-systems", "core/product_page.html")


def product_ads(request):
    return render_page(request, "products-ads", "core/product_page.html")


def product_uptime_status(request):
    return render_page(request, "products-uptime-status", "core/product_page.html")


def product_support(request):
    return render_page(request, "products-support", "core/product_page.html")


def product_maintenance(request):
    return render_page(request, "products-maintenance", "core/product_page.html")


def product_ecommerce(request):
    return render_page(request, "products-ecommerce", "core/product_page.html")


def websites_one_page(request):
    return render_page(
        request, "websites-one-page", "core/websites_one_page_plan.html"
    )


def websites_multi_page(request):
    return render_page(
        request, "websites-multi-page", "pages/websites/multi_page_plan.html"
    )


def websites_multi_page_seo(request):
    return render_page(
        request, "websites-multi-page-seo", "pages/websites/multi_page_seo_plan.html"
    )


def websites_catalog_site(request):
    return render_page(
        request, "websites-catalog-site", "pages/websites/catalog_site_plan.html"
    )


def websites_eshop_starter(request):
    return render_page(
        request, "websites-eshop-starter", "pages/websites/starter_estore_plan.html"
    )


def websites_eshop_premium(request):
    return render_page(
        request, "websites-eshop-premium", "pages/websites/premium_estore_plan.html"
    )


def websites_custom(request):
    return render_page(
        request, "websites-custom", "pages/websites/custom_website_plan.html"
    )


def printlab(request):
    return render_page(request, "printlab", "core/product_page.html")


def printlab_business_cards(request):
    return render_page(request, "printlab-business-cards", "core/product_page.html")


def printlab_flyers(request):
    return render_page(request, "printlab-flyers", "core/product_page.html")


def printlab_brochures(request):
    return render_page(request, "printlab-brochures", "core/product_page.html")


def printlab_stickers(request):
    return render_page(request, "printlab-stickers", "core/product_page.html")


def printlab_apparel(request):
    return render_page(request, "printlab-apparel", "core/product_page.html")


def printlab_merch(request):
    return render_page(request, "printlab-merch", "core/product_page.html")


def printlab_start(request):
    category = (request.GET.get("category") or "").strip()
    category_titles = {
        "cards-flyers": _("Business cards & flyers"),
        "clothing": _("Clothing"),
        "merch-gifts": _("Merch & gifts"),
        "home": _("Home & office items"),
    }
    title = category_titles.get(category, _("PrintLab category"))
    return render(
        request,
        "core/printlab_start.html",
        {
            "category": category,
            "category_title": title,
        },
    )


def start_design(request):
    ensure_draft_site(request)
    return redirect("core:onboarding_step1")


def onboarding_step1(request):
    draft = ensure_draft_site(request)
    languages = settings.LANGUAGES
    error = ""
    if request.method == "POST":
        business_name = (request.POST.get("business_name") or "").strip()
        business_type = (request.POST.get("business_type") or "").strip()
        preferred_language = request.POST.get("preferred_language") or request.LANGUAGE_CODE
        if not business_name:
            error = _("Business name is required.")
        else:
            draft["business_name"] = business_name
            draft["business_type"] = business_type
            draft["preferred_language"] = preferred_language
            save_draft_site(request, draft)
            return redirect("core:onboarding_step2")
    return render(
        request,
        "core/onboarding_step1.html",
        {"draft": draft, "languages": languages, "error": error},
    )


def onboarding_step2(request):
    draft = ensure_draft_site(request)
    templates = [
        {"key": "starter", "name": _("Starter Template")},
        {"key": "bold", "name": _("Bold Template")},
        {"key": "minimal", "name": _("Minimal Template")},
    ]
    error = ""
    if request.method == "POST":
        selected = request.POST.get("template_key") or ""
        if not selected:
            error = _("Please select a template.")
        else:
            draft["selected_template_key"] = selected
            save_draft_site(request, draft)
            return redirect("core:onboarding_step3")
    return render(
        request,
        "core/onboarding_step2.html",
        {"draft": draft, "templates": templates, "error": error},
    )


def onboarding_step3(request):
    draft = ensure_draft_site(request)
    home_url = reverse("core:home")
    preview_url = f"{home_url}?preview=1"
    login_url = f"{reverse('login')}?next={reverse('core:complete_draft')}"
    signup_url = f"{reverse('core:signup')}?next={reverse('core:complete_draft')}"
    return render(
        request,
        "core/onboarding_step3.html",
        {
            "draft": draft,
            "preview_url": preview_url,
            "login_url": login_url,
            "signup_url": signup_url,
        },
    )


@login_required
def complete_draft(request):
    draft = get_draft_site(request)
    if not draft:
        return redirect("core:dashboard")
    site = Site.objects.create(
        owner=request.user,
        name=draft.get("business_name") or _("My site"),
        language=draft.get("preferred_language") or request.LANGUAGE_CODE,
        template_key=draft.get("selected_template_key") or "",
        status=Site.STATUS_DRAFT,
    )
    clear_draft_site(request)
    return redirect("core:dashboard")


def signup(request):
    if request.method == "POST":
        next_url = request.POST.get("next") or reverse("core:dashboard")
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(next_url)
    else:
        next_url = request.GET.get("next") or reverse("core:dashboard")
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form, "next": next_url})


@login_required
def dashboard(request):
    site = getattr(request, "tenant", None)
    template_name = None
    pages_count = 0
    default_language = None
    open_url = reverse("core:home")
    if site:
        pages_count = site.pages.count()
        default_language = site.language
        if site.template_key:
            template = WebsiteTemplate.objects.filter(slug=site.template_key).first()
            if template:
                template_name = template.name
    context = {
        "site": site,
        "template_name": template_name,
        "pages_count": pages_count,
        "default_language": default_language,
        "open_url": open_url,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def dashboard_users(request):
    return render(request, "dashboard/users.html")


@login_required
def dashboard_pages(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    pages = (
        Page.objects.filter(site=site)
        .prefetch_related("translations")
        .order_by("slug")
    )
    page_rows = []
    for page in pages:
        title = None
        if hasattr(page, "safe_translation_getter"):
            title = page.safe_translation_getter("title", any_language=True)
        title = title or getattr(page, "title", None) or page.slug
        page_rows.append(
            {
                "id": page.id,
                "slug": page.slug,
                "is_active": page.is_active,
                "updated_at": page.updated_at,
                "title": title,
            }
        )

    debug_counts = None
    if settings.DEBUG:
        debug_counts = {
            "site_exists": bool(site),
            "site_id": site.id if site else None,
            "count_site": pages.count() if site else 0,
            "count_global": Page.objects.count(),
            "count_null": Page.objects.filter(site__isnull=True).count(),
        }

    return render(
        request,
        "dashboard/pages.html",
        {"site": site, "page_rows": page_rows, "debug_counts": debug_counts},
    )


@login_required
def dashboard_blog(request):
    return render(request, "dashboard/blog.html")


@login_required
def dashboard_billing(request):
    return render(request, "dashboard/billing.html")


@login_required
def dashboard_print_studio(request):
    return render(request, "dashboard/print_studio.html")


@login_required
def dashboard_control_panel(request):
    return render(request, "dashboard/control_panel.html")


@login_required
def dashboard_edit_home(request):
    return render(request, "dashboard/edit_home.html")


@login_required
def dashboard_edit_page(request, page_id):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = get_object_or_404(Page, id=page_id, site=site)
    hero_section = None
    for section in page.sections.all().order_by("order", "id"):
        key = section.key or ""
        if key.split(".")[-1] == "hero":
            hero_section = section
            break
    if not hero_section:
        hero_section = PageSection.objects.create(
            page=page,
            key=f"{page.slug}.hero",
            order=0,
            is_visible=True,
        )

    default_hero = {
        "title": "Hero title",
        "subtitle": "Hero subtitle",
        "cta_text": "Get started",
        "cta_url": "#",
    }
    content, created = SectionContent.objects.get_or_create(
        section=hero_section,
        defaults={"config_json": default_hero},
    )
    data = content.config_json if isinstance(content.config_json, dict) else {}
    if created and not data:
        data = default_hero

    errors = {}
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        subtitle = (request.POST.get("subtitle") or "").strip()
        cta_text = (request.POST.get("cta_text") or "").strip()
        cta_url = (request.POST.get("cta_url") or "").strip()

        if not title:
            errors["title"] = _("Title is required.")

        if not errors:
            updated = dict(data) if isinstance(data, dict) else {}
            updated.update(
                {
                    "title": title,
                    "subtitle": subtitle,
                    "cta_text": cta_text,
                    "cta_url": cta_url,
                }
            )
            content.config_json = updated
            content.save(update_fields=["config_json"])
            return redirect(
                f"{reverse('core:dashboard_edit_page', args=[page.id])}?saved=1"
            )
    else:
        title = data.get("title", "")
        subtitle = data.get("subtitle", "")
        cta_text = data.get("cta_text", "")
        cta_url = data.get("cta_url", "")

    context = {
        "page": page,
        "title_value": title,
        "subtitle_value": subtitle,
        "cta_text_value": cta_text,
        "cta_url_value": cta_url,
        "errors": errors,
        "saved": request.GET.get("saved") == "1",
    }
    return render(request, "dashboard/page_edit.html", context)


@login_required
def dashboard_choose_template(request):
    if request.user.is_staff:
        return redirect("core:dashboard")
    if Site.objects.filter(owner=request.user).exists():
        return redirect("core:dashboard")
    templates = WebsiteTemplate.objects.filter(is_published=True).order_by("name")
    return render(
        request,
        "dashboard/choose_template.html",
        {"templates": templates},
    )


def _build_page_from_template(site, slug, sections, language):
    page = Page.objects.filter(
        site__isnull=True,
        slug=slug,
        template_key=site.template_key,
    ).first()
    if page:
        page.site = site
        page.save(update_fields=["site"])
        created = False
    else:
        page, created = Page.objects.get_or_create(
            site=site,
            slug=slug,
            defaults={
                "is_active": True,
                "template_key": site.template_key,
            },
        )
    if created:
        page.set_current_language(language)
        page.title = slug.replace("-", " ").title()
        page.meta_title = page.title
        page.meta_description = ""
        page.save()

    for order, section in enumerate(sections):
        key = section.get("key") or f"{slug}.section{order + 1}"
        page_section, created_section = PageSection.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                "order": order,
                "is_visible": True,
            },
        )
        defaults = section.get("defaults") or {}
        content, created_content = SectionContent.objects.get_or_create(
            section=page_section,
            defaults={
                "config_json": defaults,
            },
        )
        if created_content:
            content.set_current_language(language)
            content.heading = defaults.get("title", "")
            content.subheading = defaults.get("subtitle", "")
            content.body = defaults.get("text", "")
            content.cta_primary_text = defaults.get("cta_text", "")
            content.cta_primary_url = defaults.get("cta_url", "")
            content.save()


@login_required
def dashboard_use_template(request, template_id):
    if request.user.is_staff:
        return redirect("core:dashboard")
    if Site.objects.filter(owner=request.user).exists():
        return redirect("core:dashboard")

    template = WebsiteTemplate.objects.filter(id=template_id, is_published=True).first()
    if not template:
        return redirect("core:dashboard_choose_template")

    language = (template.languages or ["nl"])[0]
    site, _created = Site.objects.get_or_create(
        owner=request.user,
        defaults={
            "name": f"{request.user.username} Site",
            "language": language,
            "template_key": template.slug,
            "status": Site.STATUS_DRAFT,
        },
    )
    if site.template_key != template.slug:
        site.template_key = template.slug
        site.save(update_fields=["template_key"])

    sections = template.sections if isinstance(template.sections, list) else []
    pages_by_slug = {}
    for section in sections:
        key = section.get("key", "")
        slug = key.split(".")[0] if "." in key else "home"
        pages_by_slug.setdefault(slug, []).append(section)

    for slug, page_sections in pages_by_slug.items():
        _build_page_from_template(site, slug, page_sections, language)

    return redirect("core:dashboard")


@login_required
def dashboard_create_page(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    errors = {}
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        slug = (request.POST.get("slug") or "").strip()
        is_active = request.POST.get("is_active") == "on"

        if not title:
            errors["title"] = _("Title is required.")
        slug = slugify(slug or title)
        if not slug:
            errors["slug"] = _("Slug is required.")
        elif Page.objects.filter(site=site, slug=slug).exists():
            errors["slug"] = _("This slug is already used for this site.")

        if not errors:
            page = Page.objects.create(
                site=site,
                slug=slug,
                is_active=is_active,
                template_key=site.template_key,
            )
            lang = get_language()
            page.set_current_language(lang)
            page.title = title
            page.meta_title = title
            page.meta_description = ""
            page.save()
            return redirect("core:dashboard_pages")
    else:
        title = ""
        slug = ""
        is_active = True

    return render(
        request,
        "dashboard/page_create.html",
        {"title_value": title, "slug_value": slug, "is_active": is_active, "errors": errors},
    )


@login_required
def dashboard_reset_site(request):
    if not request.user.is_staff:
        return redirect("core:dashboard")
    if not request.session.get("impersonate_tenant_id"):
        return redirect("core:dashboard")
    site = getattr(request, "tenant", None)
    if site:
        Page.objects.filter(site=site).delete()
        site.delete()
        if request.session.get("impersonate_tenant_id") == site.id:
            del request.session["impersonate_tenant_id"]
    return redirect("core:dashboard")


@login_required
def dashboard_widgets_demo(request):
    context = {
        "site_status": {
            "is_online": True,
            "response_time_ms": 182,
            "ssl_days_left": 42,
        },
        "seo_progress": {
            "percent": 76,
            "optimized_pages": 19,
            "total_pages": 25,
            "schema_status": _("Partial"),
            "next_crawl": _("Tomorrow 02:00"),
        },
        "indexing": {
            "indexed": 120,
            "crawled": 18,
            "not_indexed": 6,
        },
        "activity": [
            {"message": _("Homepage audit completed"), "time": _("2 hours ago")},
            {"message": _("New sitemap submitted"), "time": _("Yesterday")},
            {"message": _("SSL renewed"), "time": _("3 days ago")},
        ],
        "quick_links": [
            {"label": _("Open website"), "url": "#"},
            {"label": _("View reports"), "url": "#"},
            {"label": _("Edit settings"), "url": "#"},
        ],
        "milestones": [
            _("SSL active"),
            _("Schema ready"),
            _("First crawl done"),
        ],
    }
    return render(request, "dashboard/widgets_autofix_pack_demo.html", context)


def robots_txt(request):
    settings = get_site_settings()
    if settings.launch_disallow_robots:
        content = "User-agent: *\nDisallow: /\n"
    else:
        content = "User-agent: *\nDisallow:\n"
    return HttpResponse(content, content_type="text/plain")

# Create your views here.
