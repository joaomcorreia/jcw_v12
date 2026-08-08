from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language, gettext as _

from core.models import BlogPost, Feature, HeroParticlesSettings, Page
from core.seo_caps import get_seo_caps
from core.seo_utils import (
    build_canonical_url,
    build_hreflang_urls,
    is_public_path,
    resolve_canonical_override,
    resolve_page_seo,
)
from core.services.blog import localize_posts
from core.services.site_settings import get_site_settings
from core.services.features import get_enabled_features_for_plan, resolve_active_plan
from django.conf import settings


def embed_mode(request):
    return {"embed_mode": request.GET.get("embed") == "1"}


def edit_mode(request):
    if request.GET.get("edit") != "1":
        return {"is_edit_mode": False}
    if not request.user.is_authenticated:
        return {"is_edit_mode": False}
    if request.user.is_staff or request.user.is_superuser:
        raw_host = request.get_host()
        host = (raw_host or "").split(":", 1)[0].lower().strip()
        main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
        main_hosts = {
            "localhost",
            "127.0.0.1",
            main_domain,
            "justcodeworks.local",
            f"www.{main_domain}",
        }
        if host in main_hosts:
            return {"is_edit_mode": True}
    return {"is_edit_mode": False}


def site_mode_context(request):
    raw_host = request.get_host()
    host = (raw_host or "").split(":", 1)[0].lower().strip()
    main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
    main_hosts = {
        "localhost",
        "127.0.0.1",
        main_domain,
        "justcodeworks.local",
        f"www.{main_domain}",
    }
    tenant = getattr(request, "tenant", None)
    if tenant and not getattr(tenant, "is_main", False):
        mode = "tenant"
    elif host in main_hosts:
        mode = "main"
    else:
        mode = "other"
    return {"jcw_site_mode": mode, "jcw_site_host": host}


def seo_context(request):
    page = getattr(request, "current_page", None)
    if not page:
        return {}

    lang = getattr(request, "LANGUAGE_CODE", None) or get_language()
    seo = resolve_page_seo(page, lang)
    title = page.safe_translation_getter("title", any_language=True)
    return {
        "seo_title": seo["seo_title"] or title,
        "seo_description": seo["seo_description"],
        "seo_robots": seo["seo_robots"],
    }


def canonical_context(request):
    if not is_public_path(request.path):
        return {}
    caps = get_seo_caps(request=request, tenant=getattr(request, "tenant", None))
    canonical_url = build_canonical_url(request)
    page = getattr(request, "current_page", None)
    if page:
        lang = getattr(request, "LANGUAGE_CODE", None) or get_language()
        seo = resolve_page_seo(page, lang)
        if caps.get("allow_custom_canonical", False):
            override = resolve_canonical_override(request, seo.get("canonical_override") or "")
            if override:
                canonical_url = override
    return {
        "canonical_url": canonical_url,
        "hreflang_urls": build_hreflang_urls(request)
        if caps.get("allow_hreflang", True)
        else [],
    }


def nav_pages(request):
    # Skip for tenant host pages only; main site should always show marketing nav.
    if getattr(request, "tenant", None) and not getattr(request, "is_main_site", False):
        return {}

    nav_items = [
        ("home", _("Home"), "core:home"),
        ("about", _("About"), "core:about"),
        ("what-we-build", _("What We Build"), "core:what_we_build"),
        ("how-we-work", _("How We Work"), "core:how_we_work"),
        ("contact", _("Contact"), "core:contact"),
    ]
    items = []
    for slug, fallback_label, route_name in nav_items:
        url = reverse(route_name)
        items.append({"slug": slug, "label": fallback_label, "url": url})

    websites_dropdown_items = [
        {
            "slug": "jcw-system",
            "label": _("JCW System"),
            "url": reverse("core:websites_jcw_system"),
            "subtitle": _("Simple website setup with guidance, updates, and room to grow."),
        },
        {
            "slug": "websites-wordpress",
            "label": _("WordPress Websites"),
            "url": reverse("core:websites_wordpress"),
            "subtitle": _("One-time website setup with WordPress and full control."),
        },
        {
            "slug": "websites-how-it-works",
            "label": _("How It Works"),
            "url": reverse("core:websites_how_it_works"),
            "subtitle": _("See the steps from signup to launch."),
        },
    ]
    printlab_dropdown_items = [
        {
            "slug": "printlab",
            "label": _("Print Lab"),
            "url": reverse("core:printlab"),
        },
        {
            "slug": "printlab-business-cards",
            "label": _("Business cards"),
            "url": reverse("core:printlab_business_cards"),
        },
        {
            "slug": "printlab-apparel",
            "label": _("Clothing"),
            "url": reverse("core:printlab_apparel"),
        },
        {
            "slug": "printlab-merch",
            "label": _("Merch & gifts"),
            "url": reverse("core:printlab_merch"),
        },
        {
            "slug": "printlab-home",
            "label": _("Home"),
            "url": f"{reverse('core:printlab_start')}?category=home",
        },
    ]
    dropdown_slugs = [
        item["slug"] for item in websites_dropdown_items + printlab_dropdown_items
    ]
    dropdown_pages = (
        Page.objects.filter(
            slug__in=dropdown_slugs, is_active=True, site__isnull=True
        )
        .prefetch_related("translations")
    )
    dropdown_map = {page.slug: page for page in dropdown_pages}

    def build_dropdown(items_list):
        dropdown_items = []
        for item in items_list:
            slug = item["slug"]
            page = dropdown_map.get(slug)
            if page:
                label = (
                    page.safe_translation_getter("nav_label", any_language=True)
                    or page.slug
                )
                subtitle = (
                    page.safe_translation_getter("menu_subtitle", any_language=True)
                    or page.safe_translation_getter("title", any_language=True)
                    or ""
                )
            else:
                label = item["label"]
                subtitle = item.get("subtitle", "")
            dropdown_items.append(
                {"slug": slug, "label": label, "subtitle": subtitle, "url": item["url"]}
            )
        return dropdown_items

    return {
        "nav_pages": items,
        "websites_dropdown_pages": build_dropdown(websites_dropdown_items),
        "printlab_dropdown_pages": build_dropdown(printlab_dropdown_items),
    }


def feature_flags(request):
    tenant = getattr(request, "tenant", None)
    plan = resolve_active_plan(tenant)
    enabled_map = None
    if tenant and plan:
        enabled_map = get_enabled_features_for_plan(plan.key)

    particles_settings = (
        HeroParticlesSettings.objects.filter(
            feature__key="particles_hero",
            apply_to="home",
            is_enabled=True,
        ).first()
    )
    settings_json = None
    enabled = False
    if particles_settings:
        enabled = True
        settings_json = particles_settings.config_json

    return {
        "feature_particles_hero": enabled,
        "marketing_particles_enabled": enabled,
        "feature_print_studio": bool(enabled_map.get("print_studio"))
        if enabled_map is not None
        else bool(Feature.objects.filter(key="print_studio", is_enabled=True).exists()),
        "feature_pos_affiliates": bool(enabled_map.get("pos_affiliates"))
        if enabled_map is not None
        else bool(Feature.objects.filter(key="pos_affiliates", is_enabled=True).exists()),
        "particles_settings": particles_settings,
        "particles_settings_json": settings_json,
    }


def launch_settings(request):
    settings_obj = get_site_settings()
    path = (request.path or "/").rstrip("/") or "/"
    launch_paths = {f"/{code}{suffix}" for code, _name in settings.LANGUAGES for suffix in ("", "/about", "/what-we-build", "/how-we-work", "/contact")}
    main_site_legacy_path = not getattr(request, "tenant", None) and path not in launch_paths
    force_noindex = getattr(settings, "SEO_NOINDEX", False) or main_site_legacy_path
    return {
        "launch_noindex": force_noindex or settings_obj.launch_noindex,
        "launch_disallow_robots": force_noindex or settings_obj.launch_disallow_robots,
    }


def latest_blog_posts(request):
    now = timezone.now()
    posts = (
        BlogPost.objects.filter(is_published=True, published_at__lte=now)
        .select_related("category")
        .order_by("-published_at")[:3]
    )
    localize_posts(posts, get_language())
    return {"latest_blog_posts": posts}


def debug_env(request):
    if not settings.DEBUG:
        return {}
    tenant = getattr(request, "tenant", None)
    tenant_label = None
    if tenant:
        tenant_label = f"{tenant.name}#{tenant.id}"
    return {
        "DEBUG_ENV": {
            "project": "JCW_12",
            "db": str(settings.DATABASES.get("default", {}).get("NAME", "")),
            "user": request.user.username if request.user.is_authenticated else "anon",
            "tenant": tenant_label or "none",
            "impersonate": request.session.get("impersonate_tenant_id") or "none",
        }
    }


def dashboard_plan_context(request):
    # Skip for main site - dashboard URLs only exist on tenant subdomains
    # This context processor is only useful for tenant dashboard pages
    if not getattr(request, "tenant", None):
        return {}
    if getattr(request, "urlconf", None) != "config.tenants.urls":
        return {}

    tenant = getattr(request, "tenant", None)
    plan = resolve_active_plan(tenant)
    if plan:
        current_plan_name = plan.safe_translation_getter("name", any_language=True) or plan.key
    else:
        current_plan_name = _("Starter")

    upgrade_cta_context = {
        "title": _("Unlock more features"),
        "message": _(
            "Upgrade your plan to access advanced tools and higher limits."
        ),
        "primary_button_text": _("See upgrades"),
        "primary_button_url": reverse("tenant_dashboard:dashboard_billing"),
        "secondary_link_text": _("Contact support"),
        "secondary_link_url": reverse("core:home"),  # Tenant home, not main site services
        "style": "dashboard-upgrade-cta--compact",
    }

    return {
        "current_plan_name": current_plan_name,
        "upgrade_cta_context": upgrade_cta_context,
    }
