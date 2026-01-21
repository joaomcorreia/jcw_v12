import json
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language, gettext as _

from core.models import BlogPost, Feature, HeroParticlesSettings, Page
from core.services.blog import localize_posts
from core.services.site_settings import get_site_settings
from core.services.features import get_enabled_features_for_plan, resolve_active_plan
from django.conf import settings


def seo_context(request):
    page = getattr(request, "current_page", None)
    if not page:
        return {}

    meta_title = page.safe_translation_getter("meta_title", any_language=True)
    title = page.safe_translation_getter("title", any_language=True)
    meta_description = page.safe_translation_getter("meta_description", any_language=True)
    index = page.safe_translation_getter("meta_robots_index", any_language=True)
    follow = page.safe_translation_getter("meta_robots_follow", any_language=True)

    robots_parts = []
    robots_parts.append("index" if index else "noindex")
    robots_parts.append("follow" if follow else "nofollow")

    return {
        "seo_title": meta_title or title,
        "seo_description": meta_description,
        "seo_robots": ", ".join(robots_parts),
    }


def nav_pages(request):
    nav_items = [
        ("home", _("Home"), "core:home"),
        ("services", _("Services"), "core:services"),
        ("websites", _("Websites"), "core:websites"),
        ("printlab", _("Print Lab"), "core:printlab"),
        ("pos-systems", _("POS Systems"), "core:pos_systems"),
        ("blog", _("Blog"), "core:blog_index"),
        ("help-center", _("Help Center"), "core:help_center"),
    ]
    slugs = [slug for slug, _, _ in nav_items]
    pages = (
        Page.objects.filter(slug__in=slugs, is_active=True, site__isnull=True)
        .prefetch_related("translations")
    )
    page_map = {page.slug: page for page in pages}

    items = []
    for slug, fallback_label, route_name in nav_items:
        page = page_map.get(slug)
        if page:
            label = page.safe_translation_getter("nav_label", any_language=True) or page.slug
        else:
            label = fallback_label
        url = reverse(route_name)
        items.append({"slug": slug, "label": label, "url": url})

    websites_dropdown_items = [
        {
            "slug": "websites",
            "label": _("Websites"),
            "url": reverse("core:websites"),
        },
        {
            "slug": "websites-one-page",
            "label": _("One-page websites"),
            "url": reverse("core:websites_one_page"),
        },
        {
            "slug": "websites-multi-page",
            "label": _("Multi-page websites"),
            "url": reverse("core:websites_multi_page"),
        },
        {
            "slug": "websites-multi-page-seo",
            "label": _("Multi-page SEO"),
            "url": reverse("core:websites_multi_page_seo"),
        },
        {
            "slug": "websites-catalog-site",
            "label": _("Catalog websites"),
            "url": reverse("core:websites_catalog_site"),
        },
        {
            "slug": "websites-eshop-starter",
            "label": _("Starter eStore"),
            "url": reverse("core:websites_eshop_starter"),
        },
        {
            "slug": "websites-eshop-premium",
            "label": _("Premium eStores"),
            "url": reverse("core:websites_eshop_premium"),
        },
        {
            "slug": "websites-custom",
            "label": _("Custom websites"),
            "url": reverse("core:websites_custom"),
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
    plan = resolve_active_plan()
    enabled_map = None
    if plan:
        enabled_map = get_enabled_features_for_plan(plan.key)

    feature = Feature.objects.filter(key="particles_hero").first()
    if enabled_map is not None:
        enabled = bool(enabled_map.get("particles_hero"))
    else:
        enabled = bool(feature and feature.is_enabled)
    particles_settings = None
    settings_json = "null"

    if feature:
        particles_settings = HeroParticlesSettings.objects.filter(feature=feature).first()
        if particles_settings:
            settings_json = json.dumps(particles_settings.config_json)

    return {
        "feature_particles_hero": enabled,
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
    settings = get_site_settings()
    return {
        "launch_noindex": settings.launch_noindex,
        "launch_disallow_robots": settings.launch_disallow_robots,
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
    plan = resolve_active_plan()
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
        "primary_button_url": reverse("core:dashboard_billing"),
        "secondary_link_text": _("Contact support"),
        "secondary_link_url": reverse("core:services"),
        "style": "dashboard-upgrade-cta--compact",
    }

    return {
        "current_plan_name": current_plan_name,
        "upgrade_cta_context": upgrade_cta_context,
    }
