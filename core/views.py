from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import json
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from types import SimpleNamespace

from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.db.models import Count
from django.utils.html import escape, strip_tags
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.i18n import set_language as django_set_language

from core.models import (
    AssistantProfile,
    BlogCategory,
    BlogPost,
    BusinessProfile,
    City,
    MainSiteSectionSettings,
    MainSiteContent,
    Page,
    PageSection,
    Plan,
    SectionContent,
    Site,
    SiteVisibility,
    TenantHeroSettings,
    TenantSEOSettings,
    WebsiteTemplate,
)
from core.forms import BusinessProfileForm
from core.services.blog import localize_categories, localize_posts
from core.services.assistant_engine import AssistantServiceError, request_assistant_response
from core.services.drafts import (
    clear_draft_site,
    ensure_draft_site,
    get_draft_site,
    save_draft_site,
)
from core.services.features import get_active_subscription, resolve_active_plan
from core.services.pages import get_page_with_sections, get_sidebar_panel
from core.services.site_settings import get_site_settings
from core.services.demo_templates import get_demo_showcase_cards, get_demo_template
from core.schema import build_schema
from core.seo_utils import (
    build_canonical_url,
    build_hreflang_urls,
    build_language_path,
    build_language_url_for_path,
    INDEXABLE_PUBLIC_PATHS,
    is_indexable_public_request,
    resolve_canonical_override,
    resolve_page_seo,
)
from core.seo_caps import get_seo_caps
from core.language import language_path_for_request, supported_language_codes
from core.public.sitemaps import get_location_entries_for_site
from core.services.visibility import (
    get_country_name,
    get_seo_target_cities,
    is_location_allowed,
    normalize_city,
)
from core.visibility_rules import (
    get_visibility_limits,
    is_page_indexable,
    is_slug_indexable,
    sync_visibility_from_plan,
)
from core.data.eu_locations import COUNTRIES
from core.seo_utils import build_language_url
from core.tenant import main_site_url, resolve_active_site, resolve_active_tenant, tenant_site_url
from dashboard.forms import HeroContentForm, PageSEOForm

from django.shortcuts import redirect


def language_root(request):
    """Redirect the main-site root using Django's resolved locale preference."""
    language = get_language() or settings.LANGUAGE_CODE
    if language not in supported_language_codes():
        language = "en"
    return redirect(build_language_path(language, "/"))


def language_switch(request):
    """Persist a language choice and move the current route to its prefix."""
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER") or build_language_path("en", "/"))

    language = (request.POST.get("language") or "").lower()
    if language not in supported_language_codes():
        language = "en"

    next_path = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    parsed = urlparse(next_path)
    if parsed.netloc and parsed.netloc != request.get_host():
        next_path = "/"
    else:
        next_path = parsed.path or "/"
        if parsed.query:
            next_path = f"{next_path}?{parsed.query}"

    data = request.POST.copy()
    data["language"] = language
    data["next"] = language_path_for_request(language, next_path)
    request.POST = data
    return django_set_language(request)

def render_page(request, slug, template_name, extra_context=None):
    site = resolve_active_site(request)
    if site:
        page = (
            Page.objects.filter(site=site, slug=slug, is_active=True)
            .prefetch_related("translations", "sections__content__translations")
            .first()
        )
        if not page:
            return render(request, "site/404.html", status=404)
        site_settings = get_site_settings()
        lang = get_language()
        if hasattr(page, "set_current_language"):
            page.set_current_language(lang)
        page_title = None
        if hasattr(page, "safe_translation_getter"):
            page_title = page.safe_translation_getter("title", any_language=True)
        page_title = page_title or getattr(page, "title", None) or page.slug
        seo_context = _resolve_page_seo(page, lang)
        nav_pages = _build_nav_pages(site)
        sections = _build_sections(page)
        schema_json = json.dumps(
            build_schema(site, site_settings, request, page=page), ensure_ascii=False
        )
        caps = get_seo_caps(request=request, tenant=site)
        canonical_url = build_canonical_url(request)
        if caps.get("allow_custom_canonical", False):
            canonical_override = resolve_canonical_override(
                request, seo_context.get("canonical_override")
            )
            if canonical_override:
                canonical_url = canonical_override
        hreflang_urls = (
            build_hreflang_urls(request) if caps.get("allow_hreflang", True) else []
        )
        plan_blocks_indexing = (not is_page_indexable(site, page)) and not page.noindex
        return render(
            request,
            "site/page.html",
            {
                "sections": sections,
                "page_title": page_title,
                "nav_pages": nav_pages,
                "page": page,
                "seo_title": seo_context["seo_title"],
                "seo_description": seo_context["seo_description"],
                "seo_robots": seo_context["seo_robots"],
                "schema_json": schema_json,
                "canonical_url": canonical_url,
                "hreflang_urls": hreflang_urls,
                "plan_blocks_indexing": plan_blocks_indexing,
            },
        )

    main_site = Site.objects.filter(is_main=True).first()
    if main_site:
        page = (
            Page.objects.filter(site=main_site, slug=slug, is_active=True)
            .prefetch_related("translations", "sections__content__translations")
            .first()
        )
        if page:
            request.current_page = page
            site_settings = get_site_settings()
            lang = get_language()
            if hasattr(page, "set_current_language"):
                page.set_current_language(lang)
            page_title = None
            if hasattr(page, "safe_translation_getter"):
                page_title = page.safe_translation_getter("title", any_language=True)
            page_title = page_title or getattr(page, "title", None) or page.slug
            seo_context = _resolve_page_seo(page, lang)
            nav_pages = _build_nav_pages(main_site)
            sections = _build_sections(page)
            schema_json = json.dumps(
                build_schema(main_site, site_settings, request, page=page),
                ensure_ascii=False,
            )
            caps = get_seo_caps(request=request, tenant=main_site)
            canonical_url = build_canonical_url(request)
            if caps.get("allow_custom_canonical", False):
                canonical_override = resolve_canonical_override(
                    request, seo_context.get("canonical_override")
                )
                if canonical_override:
                    canonical_url = canonical_override
            hreflang_urls = (
                build_hreflang_urls(request)
                if caps.get("allow_hreflang", True)
                else []
            )
            return render(
                request,
                "site/page.html",
                {
                    "sections": sections,
                    "page_title": page_title,
                    "nav_pages": nav_pages,
                    "page": page,
                    "seo_title": seo_context["seo_title"],
                    "seo_description": seo_context["seo_description"],
                    "seo_robots": seo_context["seo_robots"],
                    "schema_json": schema_json,
                    "canonical_url": canonical_url,
                    "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": False,
                },
            )

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


def _get_printful_products(limit=6):
    token = (
        getattr(settings, "PRINTFUL_API_TOKEN", "")
        or os.environ.get("PRINTFUL_API_TOKEN", "")
        or os.environ.get("PRINTFUL_TOKEN", "")
    )
    if not token:
        return []

    request = Request(
        "https://api.printful.com/store/products",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return []

    items = payload.get("result") or []
    products = []
    for item in items:
        sync_product = item.get("sync_product") or {}
        sync_variants = item.get("sync_variants") or []
        first_variant = sync_variants[0] if sync_variants else {}
        first_file = (first_variant.get("files") or [{}])[0]
        image_url = (
            sync_product.get("thumbnail_url")
            or first_file.get("preview_url")
            or first_file.get("thumbnail_url")
            or ""
        )
        name = sync_product.get("name") or first_variant.get("name") or ""
        price = first_variant.get("retail_price") or ""
        if not name:
            continue
        products.append(
            {
                "name": name,
                "image_url": image_url,
                "price": price,
            }
        )
        if len(products) >= limit:
            break
    return products


def _build_nav_pages(site):
    pages = (
        Page.objects.filter(site=site, is_active=True, show_in_nav=True)
        .prefetch_related("translations")
        .order_by("nav_order", "slug")
    )
    lang = get_language()
    nav_pages = []
    for page in pages:
        if hasattr(page, "set_current_language"):
            page.set_current_language(lang)
        title = None
        if hasattr(page, "safe_translation_getter"):
            title = page.safe_translation_getter("nav_label", any_language=True)
            if not title:
                title = page.safe_translation_getter("title", any_language=True)
        title = title or getattr(page, "title", None) or page.slug
        nav_pages.append({"slug": page.slug, "title": title})
    return nav_pages


def _build_sections(page):
    sections = []
    for section in page.sections.all().order_by("order", "id"):
        content = getattr(section, "content", None)
        data = content.config_json if content else {}
        data_i18n = content.config_json_i18n if content else {}
        section_type = section.key.split(".")[-1] if section.key else "unknown"
        sections.append(
            {
                "id": section.id,
                "key": section.key,
                "type": section_type,
                "data": data,
                "data_i18n": data_i18n,
            }
        )
    return sections


def _normalize_lang(language_code):
    code = (language_code or "en").strip().lower().replace("_", "-")
    return code.split("-", 1)[0] if code else "en"


def _get_localized_section_data(content, language_code):
    if not content:
        return {}
    fallback = content.config_json if isinstance(content.config_json, dict) else {}
    value_map = (
        content.config_json_i18n if isinstance(content.config_json_i18n, dict) else {}
    )
    lang = _normalize_lang(language_code)
    if isinstance(value_map.get(lang), dict):
        return value_map.get(lang) or {}
    for key, value in value_map.items():
        if _normalize_lang(key) == lang and isinstance(value, dict):
            return value
    return fallback


def _set_localized_section_data(content, language_code, payload):
    value_map = (
        content.config_json_i18n if isinstance(content.config_json_i18n, dict) else {}
    )
    value_map[_normalize_lang(language_code)] = payload
    content.config_json_i18n = value_map


def _set_config_value(data, path, value):
    current = data
    for index, part in enumerate(path):
        is_last = index == len(path) - 1
        if part.isdigit():
            pos = int(part)
            if not isinstance(current, list):
                current_list = []
                if isinstance(data, dict) and index > 0:
                    parent_key = path[index - 1]
                    data[parent_key] = current_list
                current = current_list
            while len(current) <= pos:
                current.append({})
            if is_last:
                current[pos] = value
            else:
                if not isinstance(current[pos], (dict, list)):
                    current[pos] = {}
                current = current[pos]
        else:
            if is_last:
                current[part] = value
            else:
                if part not in current or not isinstance(current[part], (dict, list)):
                    current[part] = {}
                current = current[part]


def _get_tenant_hero_settings(site):
    settings = TenantHeroSettings.objects.filter(site=site).first()
    if settings and isinstance(settings.config_json, dict):
        return settings.config_json
    return {}


def _get_main_section_settings(page_key, section_key):
    record = MainSiteSectionSettings.objects.filter(
        page_key=page_key, section_key=section_key
    ).first()
    if record and isinstance(record.settings_json, dict):
        return record.settings_json
    return {}


def _get_default_plan():
    plan = Plan.objects.filter(key="starter").first()
    if plan:
        return plan
    return Plan.objects.order_by("sort_order", "key").first()


def _build_city_links(request, site, exclude_city=None):
    links = []
    if not site:
        return links
    lang = request.LANGUAGE_CODE
    for entry in get_seo_target_cities(site):
        country_code = entry.get("country")
        city_slug = entry.get("city")
        if not country_code or not city_slug:
            continue
        if exclude_city and normalize_city(exclude_city) == normalize_city(city_slug):
            continue
        city_label = " ".join(normalize_city(city_slug).split("-")).title()
        url = build_language_url_for_path(request, lang, f"/locations/{country_code}/{city_slug}/")
        links.append({"label": city_label, "url": url})
    return links


def _resolve_page_seo(page, lang):
    return resolve_page_seo(page, lang)


def home(request):
    page, sections_by_key = get_page_with_sections("home")
    if page:
        request.current_page = page
    sidebar_panel = get_sidebar_panel("home")
    # Launch-week homepage uses template gettext as the single source of truth.
    # Keep MainSiteContent intact in the database, but ignore those overrides here
    # so all locales fall back to the translated template strings consistently.
    content_map = {}
    hero_defaults = {
        "background": {
            "mode": "color",
            "image_url": "",
            "color": "#0f172a",
            "pattern": "dots",
            "pattern_color": "#ffffff",
            "overlay": 0.2,
        },
        "slider": {
            "autoplay": True,
            "delay": 5000,
            "transition": "fade",
            "text_effect": "none",
        },
        "slides": [
            {
                "title": "",
                "subtitle": "",
                "ctaLabel": "",
                "ctaUrl": "",
                "mediaUrl": "",
            }
        ],
        "effects": {
            "particles": {"enabled": False, "density": 80, "speed": 2, "color": "#ffffff"},
            "snow": {"enabled": False, "intensity": 60},
        },
    }
    hero_settings = _get_main_section_settings("home", "hero") or {}
    merged_hero = dict(hero_defaults)
    merged_hero.update(hero_settings)
    if "background" in hero_settings:
        merged_hero["background"] = {**hero_defaults["background"], **hero_settings["background"]}
    if "slider" in hero_settings:
        merged_hero["slider"] = {**hero_defaults["slider"], **hero_settings["slider"]}
    if "effects" in hero_settings:
        merged_hero["effects"] = {**hero_defaults["effects"], **hero_settings["effects"]}
    particles_config = {
        "particles": {
            "number": {"value": 42, "density": {"enable": True, "value_area": 1200}},
            "color": {"value": "#dbeafe"},
            "shape": {"type": "circle"},
            "opacity": {"value": 0.28, "random": True},
            "size": {"value": 2.2, "random": True},
            "line_linked": {
                "enable": True,
                "distance": 350,
                "color": "#bfdbfe",
                "opacity": 0.4,
                "width": 1,
            },
            "move": {
                "enable": True,
                "speed": 1.1,
                "direction": "none",
                "random": False,
                "straight": False,
                "out_mode": "out",
                "bounce": False,
            },
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {"enable": True, "mode": "grab"},
                "onclick": {"enable": False, "mode": "push"},
                "resize": True,
            },
            "modes": {
                "grab": {"distance": 140, "line_linked": {"opacity": 0.28}},
                "push": {"particles_nb": 2},
            },
        },
        "retina_detect": True,
    }
    return render(
        request,
        "core/home_hq.html",
        {
            "page": page,
            "sections_by_key": sections_by_key,
            "sidebar_panel": sidebar_panel,
            "jcw_hero_settings_json": json.dumps(merged_hero),
            "content_map": content_map,
            "demo_showcase_cards": get_demo_showcase_cards(),
            "printful_products_preview": _get_printful_products(limit=3),
            "marketing_particles_enabled": True,
            "particles_settings_json": particles_config,
            "seo_title": _("Just Code Works | Multilingual Platforms"),
            "seo_description": _("Just Code Works develops multilingual digital platforms for businesses and new ventures."),
        },
    )


def _company_page(request, title, description):
    return render(
        request,
        "core/company_page.html",
        {"seo_title": title, "seo_description": description},
    )


def about(request):
    return _company_page(
        request,
        _("About Just Code Works"),
        _("Learn how Just Code Works designs and operates reusable digital systems."),
    )


def what_we_build(request):
    return _company_page(
        request,
        _("What We Build | Just Code Works"),
        _("Explore multilingual, custom, white-label and reseller digital platforms."),
    )


def how_we_work(request):
    return _company_page(
        request,
        _("How We Work | Just Code Works"),
        _("See how Just Code Works turns business models into reusable digital platforms."),
    )


def privacy_cookies(request):
    return render(
        request,
        "core/privacy_cookies.html",
        {
            "seo_title": _("Privacy & Cookies | Just Code Works"),
            "seo_description": _("Privacy and cookies information for the Just Code Works public website."),
        },
    )

def _ensure_tenant_home_page(site, language_code):
    page = (
        Page.objects.filter(site=site, slug="home")
        .prefetch_related("translations", "sections__content__translations")
        .first()
    )
    if not page:
        page = Page.objects.create(
            site=site,
            slug="home",
            is_active=True,
            template_key=site.template_key or "",
        )
        if hasattr(page, "set_current_language"):
            page.set_current_language(language_code)
            page.title = _("Home")
            page.meta_title = page.title
            page.meta_description = ""
            page.save()

    section_defaults = [
        (
            "home.hero",
            0,
            {
                "title": _("Welcome to your website"),
                "subtitle": _("Update this text from your dashboard."),
                "cta_text": _("Contact us"),
                "cta_url": "/contact/",
            },
        ),
        (
            "home.services",
            10,
            {
                "heading": _("What we do"),
                "intro": _("Add your main services here."),
                "items": [
                    {
                        "title": _("Service 1"),
                        "description": _("Briefly describe this service."),
                    },
                    {
                        "title": _("Service 2"),
                        "description": _("Briefly describe this service."),
                    },
                ],
            },
        ),
        (
            "home.cta",
            20,
            {
                "title": _("Ready to get started?"),
                "text": _("Tell visitors how to contact you."),
                "button_text": _("Contact us"),
                "button_url": "/contact/",
            },
        ),
    ]
    for key, order, content in section_defaults:
        section, _created = PageSection.objects.get_or_create(
            page=page,
            key=key,
            defaults={"order": order, "is_visible": True},
        )
        if not hasattr(section, "content"):
            SectionContent.objects.create(section=section, config_json=content)
    return page


def _generate_unique_subdomain(base_value):
    reserved = {
        "www",
        "admin",
        "dashboard",
        "control-panel",
        "accounts",
        "api",
        "static",
        "media",
        "localhost",
        "justcodeworks",
    }
    base_slug = slugify(base_value or "") or "site"
    base_slug = base_slug.strip("-")
    if not base_slug or base_slug in reserved:
        base_slug = "site"
    base_slug = base_slug[:50]
    candidate = base_slug
    counter = 1
    while Site.objects.filter(subdomain__iexact=candidate).exists():
        counter += 1
        suffix = f"-{counter}"
        trimmed = base_slug[: max(1, 63 - len(suffix))]
        candidate = f"{trimmed}{suffix}"
    return candidate


def tenant_home(request):
    site = resolve_active_site(request)
    if not site:
        return render(request, "site/404.html", status=404)

    lang = get_language()
    page = _ensure_tenant_home_page(site, lang)
    if hasattr(page, "set_current_language"):
        page.set_current_language(lang)
    request.current_page = page

    site_settings = get_site_settings()
    seo_context = _resolve_page_seo(page, lang)
    nav_pages = _build_nav_pages(site)
    sections = _build_sections(page)
    schema_json = json.dumps(
        build_schema(site, site_settings, request, page=page), ensure_ascii=False
    )
    caps = get_seo_caps(request=request, tenant=site)
    canonical_url = build_canonical_url(request)
    if caps.get("allow_custom_canonical", False):
        canonical_override = resolve_canonical_override(
            request, seo_context.get("canonical_override")
        )
        if canonical_override:
            canonical_url = canonical_override
    hreflang_urls = (
        build_hreflang_urls(request) if caps.get("allow_hreflang", True) else []
    )
    plan_blocks_indexing = (not is_page_indexable(site, page)) and not page.noindex

    hero_settings_json = json.dumps(
        _get_tenant_hero_settings(site), ensure_ascii=False
    )
    return render(
        request,
        "site/page.html",
        {
            "sections": sections,
            "page_title": page.title or page.slug,
            "nav_pages": nav_pages,
            "page": page,
            "seo_title": seo_context["seo_title"],
            "seo_description": seo_context["seo_description"],
            "seo_robots": seo_context["seo_robots"],
            "schema_json": schema_json,
            "canonical_url": canonical_url,
            "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": plan_blocks_indexing,
            "hero_settings_json": hero_settings_json,
        },
    )


def public_page(request, slug):
    site = resolve_active_site(request)
    if not site:
        main_site = Site.objects.filter(is_main=True).first()
        if main_site:
            page = (
                Page.objects.filter(site=main_site, slug=slug, is_active=True)
                .prefetch_related("translations", "sections__content__translations")
                .first()
            )
            if page:
                request.current_page = page
                site_settings = get_site_settings()
                lang = get_language()
                if hasattr(page, "set_current_language"):
                    page.set_current_language(lang)
                page_title = None
                if hasattr(page, "safe_translation_getter"):
                    page_title = page.safe_translation_getter("title", any_language=True)
                page_title = page_title or getattr(page, "title", None) or page.slug
                seo_context = _resolve_page_seo(page, lang)
                nav_pages = _build_nav_pages(main_site)
                sections = _build_sections(page)
                schema_json = json.dumps(
                    build_schema(main_site, site_settings, request, page=page),
                    ensure_ascii=False,
                )
                caps = get_seo_caps(request=request, tenant=main_site)
                canonical_url = build_canonical_url(request)
                if caps.get("allow_custom_canonical", False):
                    canonical_override = resolve_canonical_override(
                        request, seo_context.get("canonical_override")
                    )
                    if canonical_override:
                        canonical_url = canonical_override
                hreflang_urls = (
                    build_hreflang_urls(request)
                    if caps.get("allow_hreflang", True)
                    else []
                )
                return render(
                    request,
                    "site/page.html",
                    {
                        "sections": sections,
                        "page_title": page_title,
                        "nav_pages": nav_pages,
                        "page": page,
                        "seo_title": seo_context["seo_title"],
                        "seo_description": seo_context["seo_description"],
                        "seo_robots": seo_context["seo_robots"],
                        "schema_json": schema_json,
                        "canonical_url": canonical_url,
                        "hreflang_urls": hreflang_urls,
                        "plan_blocks_indexing": False,
                    },
                )
        return render(request, "site/404.html", status=404)

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
    seo_context = _resolve_page_seo(page, lang)
    nav_pages = _build_nav_pages(site)
    sections = _build_sections(page)
    site_settings = get_site_settings()
    schema_json = json.dumps(
        build_schema(site, site_settings, request, page=page), ensure_ascii=False
    )
    caps = get_seo_caps(request=request, tenant=site)
    canonical_url = build_canonical_url(request)
    if caps.get("allow_custom_canonical", False):
        canonical_override = resolve_canonical_override(
            request, seo_context.get("canonical_override")
        )
        if canonical_override:
            canonical_url = canonical_override
    hreflang_urls = (
        build_hreflang_urls(request) if caps.get("allow_hreflang", True) else []
    )
    plan_blocks_indexing = (not is_page_indexable(site, page)) and not page.noindex
    hero_settings_json = json.dumps(
        _get_tenant_hero_settings(site), ensure_ascii=False
    )
    return render(
        request,
        "site/page.html",
        {
            "sections": sections,
            "page_title": page_title,
            "nav_pages": nav_pages,
            "page": page,
            "seo_title": seo_context["seo_title"],
            "seo_description": seo_context["seo_description"],
            "seo_robots": seo_context["seo_robots"],
            "schema_json": schema_json,
            "canonical_url": canonical_url,
            "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": plan_blocks_indexing,
            "hero_settings_json": hero_settings_json,
        },
    )


def websites(request):
    return render_page(request, "websites", "core/websites_overview.html")


def websites_jcw_system(request):
    return render_page(request, "jcw-system", "core/jcw_system.html")


def websites_wordpress(request):
    return render_page(request, "wordpress", "core/wordpress.html")


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


def help_page(request):
    return render_page(request, "help", "core/help.html")


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
    site_settings = get_site_settings()
    main_site = Site.objects.filter(is_main=True).first()
    schema_json = json.dumps(
        build_schema(main_site, site_settings, request, page=post), ensure_ascii=False
    )
    return render(
        request,
        "core/blog_detail.html",
        {
            "post": post,
            "seo_title": post.localized_title or _("Blog"),
            "seo_description": post.localized_excerpt,
            "schema_json": schema_json,
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
        request,
        "websites-one-page",
        "core/websites_one_page_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_multi_page(request):
    return render_page(
        request,
        "websites-multi-page",
        "pages/websites/multi_page_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_multi_page_seo(request):
    return render_page(
        request,
        "websites-multi-page-seo",
        "pages/websites/multi_page_seo_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_catalog_site(request):
    return render_page(
        request,
        "websites-catalog-site",
        "pages/websites/catalog_site_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_eshop_starter(request):
    return render_page(
        request,
        "websites-eshop-starter",
        "pages/websites/starter_estore_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_eshop_premium(request):
    return render_page(
        request,
        "websites-eshop-premium",
        "pages/websites/premium_estore_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def websites_custom(request):
    return render_page(
        request,
        "websites-custom",
        "pages/websites/custom_website_plan.html",
        extra_context={"demo_showcase_cards": get_demo_showcase_cards()},
    )


def pricing(request):
    return render_page(
        request,
        "pricing",
        "core/pricing.html",
        extra_context={
            "seo_title": _("Pricing"),
            "seo_description": _(
                "Pricing for online presence setup, website plans, and Facebook visibility support."
            ),
        },
    )


def contact(request):
    return _company_page(
        request,
        _("Contact | Just Code Works"),
        _("Discuss a custom, white-label, reseller or partnership platform with Just Code Works."),
    )

def facebook_visibility(request):
    return render_page(
        request,
        "facebook-visibility",
        "core/facebook_visibility.html",
        extra_context={
            "seo_title": _("Facebook Visibility"),
            "seo_description": _(
                "Ongoing Facebook posting support to keep your business active and visible."
            ),
        },
    )


def online_marketing(request):
    return render_page(
        request,
        "online-marketing",
        "core/online_marketing.html",
        extra_context={
            "seo_title": _("Online Marketing"),
            "seo_description": _(
                "Online marketing services that can be added as your business grows."
            ),
        },
    )


def demo_preview(request, slug):
    demo = get_demo_template(slug)
    if not demo:
        return render(request, "site/404.html", status=404)

    return render(
        request,
        "core/demo_preview.html",
        {
            "demo": demo,
            "seo_title": demo.title,
            "seo_description": demo.description,
        },
    )


def printlab(request):
    return render_page(request, "printlab", "core/product_page.html")


def print_overview(request):
    return render_page(request, "print-overview", "core/print_overview.html")


def printlab_business_cards(request):
    return render_page(request, "printlab-business-cards", "core/product_page.html")


def print_business(request):
    return render_page(request, "print-business", "core/print_business.html")


def printlab_flyers(request):
    return render_page(request, "printlab-flyers", "core/product_page.html")


def printlab_brochures(request):
    return render_page(request, "printlab-brochures", "core/product_page.html")


def printlab_stickers(request):
    return render_page(request, "printlab-stickers", "core/product_page.html")


def printlab_apparel(request):
    return render_page(request, "printlab-apparel", "core/product_page.html")


def print_merch(request):
    return render_page(
        request,
        "print-merch",
        "core/print_merch.html",
        {"printful_products": _get_printful_products(limit=6)},
    )


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
        city = (request.POST.get("city") or "").strip()
        country = (request.POST.get("country") or "").strip()
        preferred_language = request.POST.get("preferred_language") or request.LANGUAGE_CODE
        if not business_name:
            error = _("Business name is required.")
        else:
            draft["business_name"] = business_name
            draft["business_type"] = business_type
            draft["city"] = city
            draft["country"] = country
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
    default_plan = _get_default_plan()
    site = Site.objects.create(
        owner=request.user,
        name=draft.get("business_name") or _("My site"),
        language=draft.get("preferred_language") or request.LANGUAGE_CODE,
        template_key=draft.get("selected_template_key") or "",
        status=Site.STATUS_DRAFT,
        plan=default_plan,
    )
    city_input = (draft.get("city") or "").strip()
    country_input = (draft.get("country") or "").strip().upper()
    country_code = country_input if len(country_input) == 2 else ""
    active_city = None
    if city_input and country_code:
        city_slug = normalize_city(city_input)
        active_city = City.objects.filter(
            slug__iexact=city_slug, country_code__iexact=country_code
        ).first()
    TenantSEOSettings.objects.get_or_create(
        tenant=site,
        defaults={
            "target_country_code": country_code,
            "active_city": active_city,
        },
    )
    clear_draft_site(request)
    return redirect("core:dashboard")


def signup(request):
    if request.method == "POST":
        lang = request.LANGUAGE_CODE or get_language()
        next_url = request.POST.get("next") or build_language_url_for_path(
            request, lang, "/"
        )
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_staff or user.is_superuser:
                user.is_staff = False
                user.is_superuser = False
                user.save(update_fields=["is_staff", "is_superuser"])
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect(next_url)

            draft = get_draft_site(request) or {}
            business_name = (draft.get("business_name") or "").strip()
            site_name = (
                business_name
                or getattr(user, "get_full_name", lambda: "")()
                or user.username
                or _("My site")
            )
            language = (
                (draft.get("preferred_language") or "").strip()
                or request.LANGUAGE_CODE
                or get_language()
            )
            template_key = (draft.get("selected_template_key") or "").strip()
            subdomain_source = business_name or user.username or site_name
            subdomain = _generate_unique_subdomain(subdomain_source)
            default_plan = _get_default_plan()
            site = Site.objects.create(
                owner=user,
                name=site_name,
                subdomain=subdomain,
                language=language,
                template_key=template_key,
                status=Site.STATUS_DRAFT,
                plan=default_plan,
            )
            city_input = (draft.get("city") or "").strip()
            country_input = (draft.get("country") or "").strip().upper()
            country_code = country_input if len(country_input) == 2 else ""
            active_city = None
            if city_input and country_code:
                city_slug = normalize_city(city_input)
                active_city = City.objects.filter(
                    slug__iexact=city_slug, country_code__iexact=country_code
                ).first()
            TenantSEOSettings.objects.get_or_create(
                tenant=site,
                defaults={
                    "target_country_code": country_code,
                    "active_city": active_city,
                },
            )
            _ensure_tenant_home_page(site, language)
            clear_draft_site(request)

            dashboard_path = f"/{language}/dashboard/"
            return redirect(tenant_site_url(site, dashboard_path, request=request))
    else:
        lang = request.LANGUAGE_CODE or get_language()
        next_url = request.GET.get("next") or build_language_url_for_path(
            request, lang, "/"
        )
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form, "next": next_url})


@login_required
def dashboard(request):
    site = getattr(request, "tenant", None)
    # Block dashboard on main site
    if not site or getattr(site, "is_main", False):
        if request.user.is_staff or request.user.is_superuser:
            return redirect("control_panel:home")
        return redirect("core:home")

    # Allow only owner/staff/impersonation for tenant dashboards
    impersonating = request.session.get("impersonate_tenant_id") == site.id
    if not (
        request.user.is_staff
        or request.user.is_superuser
        or impersonating
        or site.owner_id == request.user.id
    ):
        return HttpResponseForbidden("Forbidden")
    template_name = None
    pages_count = 0
    default_language = None
    lang = request.LANGUAGE_CODE or "en"
    try:
        open_url = tenant_site_url(site, f"/{lang}/", request=request)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
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
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect("tenant_dashboard:dashboard")
    return render(request, "dashboard/users.html")


def _control_panel_url(request, path="/control-panel/"):
    lang = request.LANGUAGE_CODE or get_language() or "en"
    return main_site_url(build_language_path(lang, path), request=request)


@login_required
def legacy_dashboard_users(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect(_control_panel_url(request, "/control-panel/users/"))
    return redirect("tenant_dashboard:dashboard")


@login_required
def dashboard_pages(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    has_home = Page.objects.filter(site=site, slug="home").exists()
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
        {
            "site": site,
            "page_rows": page_rows,
            "debug_counts": debug_counts,
            "has_home": has_home,
            "main_site": False,
            "edit_url_name": "tenant_dashboard:page_edit",
        },
    )


@login_required
def dashboard_content_map(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect("core:dashboard")

    lang = request.LANGUAGE_CODE or get_language()
    pages = (
        Page.objects.filter(site=site)
        .prefetch_related("translations", "sections__content")
        .order_by("slug")
    )
    duplicate_keys = set(
        PageSection.objects.filter(page__site=site)
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
            rows.append(
                {
                    "page_slug": page.slug,
                    "page_title": page_title,
                    "section_key": _("(no sections)"),
                    "status": _("Missing"),
                    "status_class": "dashboard-badge--warning",
                    "page_edit_url": reverse("tenant_dashboard:page_edit", args=[page.id]),
                    "section_edit_url": "",
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
                status = _("Missing content")
                status_class = "dashboard-badge--warning"
            else:
                status = _("OK")
                status_class = "dashboard-badge--success"

            section_edit_url = ""
            if request.user.is_staff:
                try:
                    section_edit_url = reverse(
                        "admin:core_pagesection_change", args=[section.id]
                    )
                except Exception:
                    section_edit_url = ""

            rows.append(
                {
                    "page_slug": page.slug,
                    "page_title": page_title,
                    "section_key": section.key,
                    "status": status,
                    "status_class": status_class,
                    "page_edit_url": reverse("tenant_dashboard:page_edit", args=[page.id]),
                    "section_edit_url": section_edit_url,
                    "page_url": page_url,
                }
            )

    return render(
        request,
        "dashboard/content_map.html",
        {
            "rows": rows,
        },
    )


@login_required
def dashboard_menu(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    pages = (
        Page.objects.filter(site=site)
        .prefetch_related("translations")
        .order_by("nav_order", "slug")
    )
    if request.method == "POST":
        lang = get_language()
        for page in pages:
            page.set_current_language(lang)
            page.show_in_nav = request.POST.get(f"show_in_nav_{page.id}") == "on"
            page.nav_label = (request.POST.get(f"nav_label_{page.id}") or "").strip()
            nav_order_raw = request.POST.get(f"nav_order_{page.id}") or "100"
            try:
                page.nav_order = int(nav_order_raw)
            except ValueError:
                page.nav_order = 100
            page.save()
        messages.success(request, _("Menu updated."))
        return redirect(reverse("tenant_dashboard:menu"))

    lang = get_language()
    page_rows = []
    for page in pages:
        page.set_current_language(lang)
        title = page.title or page.slug
        nav_label = page.nav_label or ""
        page_rows.append(
            {
                "id": page.id,
                "title": title,
                "slug": page.slug,
                "show_in_nav": page.show_in_nav,
                "nav_label": nav_label,
                "nav_order": page.nav_order,
            }
        )

    return render(
        request,
        "dashboard/menu.html",
        {"site": site, "page_rows": page_rows},
    )


@login_required
def dashboard_visibility(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    plan = resolve_active_plan(site)
    plan_key = plan.key if plan else "starter"
    caps = get_seo_caps(tenant=site)
    seo_level = caps["seo_level"]
    is_local = caps["is_local"]
    is_country = caps["is_country"]
    is_eu = caps["is_eu"]
    visibility = sync_visibility_from_plan(site)

    plan_name = None
    if plan and hasattr(plan, "safe_translation_getter"):
        plan_name = plan.safe_translation_getter("name", any_language=True)
    plan_name = plan_name or plan_key.title()

    mode_labels = {
        SiteVisibility.MODE_BASIC: _("Basic SEO - visible via core pages only"),
        SiteVisibility.MODE_LOCATIONS: _("Location-based visibility (limited)"),
        SiteVisibility.MODE_EU: _("EU-wide visibility"),
    }

    limits = get_visibility_limits(site)
    max_countries = limits["max_countries"]
    max_cities = limits["max_cities"]

    visibility_errors = []
    seo_errors = []
    selected_countries = list(visibility.allowed_countries or [])
    selected_cities = list(visibility.allowed_cities or [])
    selected_city_keys = {
        f"{item.get('country')}|{item.get('city')}"
        for item in selected_cities
        if isinstance(item, dict)
    }

    if request.method == "POST" and visibility.visibility_mode == SiteVisibility.MODE_LOCATIONS and request.POST.get("visibility_submit"):
        if not caps["allow_location_pages"]:
            visibility_errors.append(_("Location pages are disabled for this plan."))
            return render(
                request,
                "dashboard/visibility.html",
                {
                    "site": site,
                    "plan_name": plan_name,
                    "seo_level": visibility.seo_level,
                    "visibility_mode_label": mode_labels.get(visibility.visibility_mode, ""),
                    "is_pro": visibility.visibility_mode == SiteVisibility.MODE_EU,
                    "visibility_mode": visibility.visibility_mode,
                    "countries": COUNTRIES,
                    "selected_countries": selected_countries,
                    "selected_city_keys": selected_city_keys,
                    "selected_cities": selected_cities,
                    "max_countries": max_countries,
                    "max_cities": max_cities,
                    "errors": visibility_errors,
                    "seo_level": seo_level,
                    "seo_is_local": is_local,
                    "seo_is_country": is_country,
                    "seo_is_eu": is_eu,
                    "target_country_code": "",
                    "available_cities": [],
                    "active_city_id": None,
                    "active_city_label": "",
                    "active_country_label": "",
                    "starter_missing_city": False,
                    "focus_city_ids": [],
                    "max_focus_cities": caps["max_cities"],
                    "max_focus_reached": False,
                    "max_focus_hint": "",
                    "max_countries_reached": False,
                    "max_cities_reached": False,
                    "show_city_change_warning": False,
                    "allow_city_switching": caps["allow_city_switching"],
                    "allow_location_pages": caps["allow_location_pages"],
                    "location_locked_hint": _("Available on Country plan."),
                    "city_switch_locked_hint": _("Upgrade to change the active city."),
                    "multi_city_hint": _("Upgrade to Country plan to select multiple cities."),
                    "seo_errors": seo_errors,
                    "allow_indexing": caps.get("allow_indexing", True),
                },
            )
        if max_countries == 1:
            selected_countries = [request.POST.get("countries")] if request.POST.get("countries") else []
        else:
            selected_countries = request.POST.getlist("countries")
            if not selected_countries:
                selected_countries = request.POST.getlist("countries[]")
        if max_cities == 1:
            raw_cities = [request.POST.get("cities")] if request.POST.get("cities") else []
        else:
            raw_cities = request.POST.getlist("cities")
            if not raw_cities:
                raw_cities = request.POST.getlist("cities[]")
        city_entries = []
        for raw in raw_cities:
            if "|" not in raw:
                continue
            country_code, city = raw.split("|", 1)
            if country_code not in selected_countries:
                continue
            city_entries.append({"country": country_code, "city": city})

        if max_countries is not None and len(selected_countries) > max_countries:
            visibility_errors.append(
                _("You can select up to %(count)s countries on your plan.")
                % {"count": max_countries}
            )
        if max_cities is not None and len(city_entries) > max_cities:
            visibility_errors.append(
                _("You can select up to %(count)s cities on your plan.")
                % {"count": max_cities}
            )

        if not visibility_errors:
            visibility.allowed_countries = selected_countries
            visibility.allowed_cities = city_entries
            visibility._from_sync = True
            visibility.save(update_fields=["allowed_countries", "allowed_cities", "last_updated"])
            messages.success(request, _("Visibility locations saved."))
            return redirect(reverse("tenant_dashboard:visibility"))

            selected_cities = city_entries
            selected_city_keys = {
                f"{item.get('country')}|{item.get('city')}"
                for item in selected_cities
                if isinstance(item, dict)
            }

    seo_settings, _created = TenantSEOSettings.objects.get_or_create(
        tenant=site,
        defaults={
            "target_country_code": (selected_countries[0] if selected_countries else ""),
        },
    )
    focus_city_ids = list(seo_settings.focus_cities.values_list("id", flat=True))
    if request.method == "POST" and request.POST.get("seo_settings_submit"):
        if not caps["allow_location_pages"]:
            seo_errors.append(_("Location pages are disabled for this plan."))
        target_country = (request.POST.get("target_country") or "").upper().strip()
        seo_settings.target_country_code = target_country

        active_city_id = request.POST.get("active_city") or ""
        active_city = City.objects.filter(id=active_city_id).first() if active_city_id else None

        focus_city_ids = request.POST.getlist("focus_cities")
        if not focus_city_ids:
            focus_city_ids = request.POST.getlist("focus_cities[]")
        focus_cities = list(City.objects.filter(id__in=focus_city_ids))

        max_focus = caps["max_cities"]
        requires_active = is_local

        if is_local:
            if requires_active and not active_city:
                seo_errors.append(_("Select one active city for Local SEO."))
            if focus_cities:
                seo_errors.append(_("Local SEO does not allow focus cities."))
        elif is_country:
            if max_focus is not None and len(focus_cities) > max_focus:
                seo_errors.append(
                    _("You can select up to %(count)s focus cities on your plan.")
                    % {"count": max_focus}
                )
        if not caps["allow_city_switching"] and active_city_id and active_city:
            if seo_settings.active_city_id and seo_settings.active_city_id != active_city.id:
                seo_errors.append(_("Active city changes are disabled for this plan."))

        if not is_eu and target_country:
            if active_city and active_city.country_code.upper() != target_country:
                seo_errors.append(_("Active city must match the selected country."))
            for city in focus_cities:
                if city.country_code.upper() != target_country:
                    seo_errors.append(_("All focus cities must match the selected country."))

        if not seo_errors:
            if is_local and active_city:
                if seo_settings.active_city_id != active_city.id:
                    seo_settings.last_city_change_at = timezone.now()
            seo_settings.active_city = active_city if is_local else active_city
            seo_settings.save(update_fields=["target_country_code", "active_city", "last_city_change_at"])
            if is_local:
                seo_settings.focus_cities.set([])
            elif is_country:
                seo_settings.focus_cities.set(focus_cities)
            else:
                seo_settings.focus_cities.set(focus_cities)
            messages.success(request, _("SEO targeting saved."))
            return redirect(reverse("tenant_dashboard:visibility"))

    if is_country and not focus_city_ids and seo_settings.target_country_code:
        defaults = (
            City.objects.filter(
                country_code__iexact=seo_settings.target_country_code,
                is_top_city=True,
            )
            .order_by("name")[: caps["max_cities"]]
        )
        focus_city_ids = [city.id for city in defaults]

    target_country_code = seo_settings.target_country_code
    available_cities = City.objects.filter(country_code__iexact=target_country_code).order_by("name")
    active_city_id = seo_settings.active_city_id
    cooldown_days = getattr(settings, "SEO_ACTIVE_CITY_COOLDOWN_DAYS", 0)
    show_city_change_warning = False
    if cooldown_days and seo_settings.last_city_change_at:
        delta = timezone.now() - seo_settings.last_city_change_at
        if delta.days < cooldown_days:
            show_city_change_warning = True
    active_city_label = ""
    active_country_label = ""
    if seo_settings.active_city:
        active_city_label = seo_settings.active_city.name
        active_country_label = seo_settings.active_city.country_code
    elif target_country_code:
        active_country_label = target_country_code
    starter_missing_city = bool(is_local and not active_city_label)
    max_focus_cities = caps["max_cities"]
    max_focus_reached = bool(max_focus_cities and len(focus_city_ids) >= max_focus_cities)
    max_focus_hint = _("Upgrade to add more cities.") if max_focus_reached else ""
    max_countries_reached = bool(max_countries and len(selected_countries) >= max_countries)
    max_cities_reached = bool(max_cities and len(selected_city_keys) >= max_cities)

    return render(
        request,
        "dashboard/visibility.html",
        {
            "site": site,
            "plan_name": plan_name,
            "seo_level": visibility.seo_level,
            "visibility_mode_label": mode_labels.get(visibility.visibility_mode, ""),
            "is_pro": visibility.visibility_mode == SiteVisibility.MODE_EU,
            "visibility_mode": visibility.visibility_mode,
            "countries": COUNTRIES,
            "selected_countries": selected_countries,
            "selected_city_keys": selected_city_keys,
            "selected_cities": selected_cities,
            "max_countries": max_countries,
            "max_cities": max_cities,
            "errors": visibility_errors,
            "seo_level": seo_level,
            "seo_is_local": is_local,
            "seo_is_country": is_country,
            "seo_is_eu": is_eu,
            "target_country_code": target_country_code,
            "available_cities": available_cities,
            "active_city_id": active_city_id,
            "active_city_label": active_city_label,
            "active_country_label": active_country_label,
            "starter_missing_city": starter_missing_city,
            "focus_city_ids": focus_city_ids,
            "max_focus_cities": max_focus_cities,
            "max_focus_reached": max_focus_reached,
            "max_focus_hint": max_focus_hint,
            "max_countries_reached": max_countries_reached,
            "max_cities_reached": max_cities_reached,
            "show_city_change_warning": show_city_change_warning,
            "allow_city_switching": caps["allow_city_switching"],
            "allow_location_pages": caps["allow_location_pages"],
            "location_locked_hint": _("Available on Country plan."),
            "city_switch_locked_hint": _("Upgrade to change the active city."),
            "multi_city_hint": _("Upgrade to Country plan to select multiple cities."),
            "seo_errors": seo_errors,
            "allow_indexing": caps.get("allow_indexing", True),
        },
    )


@login_required
def dashboard_site_settings(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    settings_obj = get_site_settings()
    return render(
        request,
        "dashboard/site_settings.html",
        {"site": site, "settings": settings_obj},
    )


def _get_main_site_or_create(request):
    site = Site.objects.filter(is_main=True).first()
    if site:
        return site
    default_plan = _get_default_plan()
    site = Site.objects.create(
        owner=request.user,
        name="Main Site",
        language=request.LANGUAGE_CODE,
        template_key="",
        status=Site.STATUS_PUBLISHED,
        is_main=True,
        plan=default_plan,
    )
    return site


@login_required
def dashboard_main_site_pages(
    request,
    *,
    dashboard_base_template="dashboard/base_dashboard.html",
    edit_url_name="tenant_dashboard:main_site_page_edit",
    page_list_url_name=None,
):
    if not request.user.is_staff:
        return redirect("core:dashboard")

    site = _get_main_site_or_create(request)
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

    return render(
        request,
        "dashboard/pages.html",
        {
            "site": site,
            "page_rows": page_rows,
            "debug_counts": None,
            "has_home": Page.objects.filter(site=site, slug="home").exists(),
            "main_site": True,
            "edit_url_name": edit_url_name,
            "dashboard_base_template": dashboard_base_template,
            "page_list_url": reverse(page_list_url_name) if page_list_url_name else "",
        },
    )


@login_required
def legacy_dashboard_main_site_pages(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect(_control_panel_url(request, "/control-panel/main-site/pages/"))
    return redirect("tenant_dashboard:dashboard")


@login_required
def dashboard_blog(request):
    return render(request, "dashboard/blog.html")


@login_required
def dashboard_billing(request):
    site = getattr(request, "tenant", None)
    current_plan_name = _("No active plan")
    current_site_status = _("Not connected")
    if site:
        if getattr(site, "plan", None):
            current_plan_name = site.plan.display_name
        if getattr(site, "status", None):
            current_site_status = site.get_status_display()
    return render(
        request,
        "dashboard/billing.html",
        {
            "current_plan_name": current_plan_name,
            "current_site_status": current_site_status,
            "site": site,
        },
    )


@login_required
def dashboard_account(request):
    profile = BusinessProfile.objects.filter(user=request.user).first()
    site = getattr(request, "tenant", None)
    return render(
        request,
        "dashboard/account.html",
        {
            "profile": profile,
            "site": site,
        },
    )


@login_required
def dashboard_domains(request):
    site = getattr(request, "tenant", None)
    return render(
        request,
        "dashboard/domains.html",
        {"site": site},
    )


@login_required
def dashboard_website_details(request):
    site = getattr(request, "tenant", None)
    template_name = ""
    if site and getattr(site, "template_key", None):
        template = WebsiteTemplate.objects.filter(slug=site.template_key).first()
        if template:
            template_name = template.name
    return render(
        request,
        "dashboard/website_details.html",
        {
            "site": site,
            "template_name": template_name,
        },
    )


def _render_dashboard_placeholder_page(request, template_name, title, intro, status_title, status_body):
    return render(
        request,
        template_name,
        {
            "page_title": title,
            "page_intro": intro,
            "status_title": status_title,
            "status_body": status_body,
        },
    )


@login_required
def dashboard_media_manager(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/media_manager.html",
        _("Media Manager"),
        _("This page will become the place where you manage the media used across your website."),
        _("Media status"),
        _("Your media manager is being prepared so files and images can be managed from one stable area."),
    )


@login_required
def dashboard_subscriptions(request):
    site = getattr(request, "tenant", None)
    current_plan_name = _("No active plan")
    if site and getattr(site, "plan", None):
        current_plan_name = site.plan.display_name
    return render(
        request,
        "dashboard/subscriptions.html",
        {
            "site": site,
            "current_plan_name": current_plan_name,
        },
    )


@login_required
def dashboard_google_analytics(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/google_analytics.html",
        _("Google Analytics"),
        _("This page will show your website analytics connection and reporting status once the dashboard connection step is added."),
        _("Analytics status"),
        _("Your analytics dashboard is not connected here yet. When this area is activated, connection status and reporting access will appear in this section."),
    )


@login_required
def dashboard_facebook_insights(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/facebook_insights.html",
        _("Facebook Insights"),
        _("This page will show your Facebook connection and page insights when the customer dashboard support is activated."),
        _("Insights status"),
        _("Facebook insights are not connected in this dashboard yet. When this area is activated, page status and reporting summaries will appear here."),
    )


@login_required
def dashboard_social_content_planning(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/social_content_planning.html",
        _("Social Content Planning"),
        _("This page will organize future social content planning connected to your website and services."),
        _("Planning status"),
        _("Social content planning is being prepared so this area can become a clear starting point for future content work."),
    )


@login_required
def dashboard_tool_image_resizer(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/tool_image_resizer.html",
        _("Image Resizer"),
        _("This page will provide a simple way to prepare website and social images from your dashboard."),
        _("Tool status"),
        _("The image resizer is being prepared and will appear here as a stable dashboard tool later."),
    )


@login_required
def dashboard_tool_qr_code_maker(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/tool_qr_code_maker.html",
        _("QR Code Maker"),
        _("This page will provide a simple way to create QR codes connected to your website and print materials."),
        _("Tool status"),
        _("The QR code maker is being prepared and will appear here as a stable dashboard tool later."),
    )


@login_required
def dashboard_help(request):
    return _render_dashboard_placeholder_page(
        request,
        "dashboard/help.html",
        _("Help"),
        _("Use this area to understand where dashboard help and support options will appear."),
        _("Support status"),
        _("Dashboard help is being prepared so customers can find guidance and support in one place."),
    )


@login_required
def dashboard_print_studio(request):
    return render(request, "dashboard/print_studio.html")


@login_required
def marketplace_jcw(request):
    return render(request, "dashboard/marketplace_jcw.html")


@login_required
def marketplace_printlab(request):
    return render(request, "dashboard/marketplace_printlab.html")


@login_required
def marketplace_card_payments(request):
    return render(request, "dashboard/marketplace_card_payments.html")


def _business_profile_is_complete(profile):
    if not profile:
        return False
    if hasattr(profile, "profile_completed"):
        return bool(profile.profile_completed)
    required_fields = [
        "business_name",
        "category",
        "city",
        "country",
        "website_goal",
    ]
    return all((getattr(profile, field, "") or "").strip() for field in required_fields)


@login_required
def post_login_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")
    tenant = resolve_active_tenant(request)
    if tenant:
        lang = request.LANGUAGE_CODE or getattr(tenant, "language", None) or get_language()
        dashboard_path = build_language_path(lang or "en", "/dashboard/")
        return redirect(tenant_site_url(tenant, dashboard_path, request=request))
    profile = BusinessProfile.objects.filter(user=request.user).first()
    if _business_profile_is_complete(profile):
        return redirect("core:website_preview")
    return redirect("core:onboarding")


@login_required
def onboarding(request):
    entry_type = (request.GET.get("entry_type") or "website").strip().lower()
    if entry_type not in {"website", "wordpress", "wordpress_shop", "print_business_cards"}:
        entry_type = "website"
    profile, _ = BusinessProfile.objects.get_or_create(
        user=request.user,
        defaults={"email_public": request.user.email or ""},
    )
    if _business_profile_is_complete(profile):
        return redirect("core:website_preview")

    if request.method == "POST":
        form = BusinessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.profile_completed = True
            profile.save()
            return redirect("core:website_preview")
    else:
        form = BusinessProfileForm(instance=profile)

    return render(
        request,
        "onboarding/onboarding_form.html",
        {
            "form": form,
            "entry_type": entry_type,
        },
    )


@login_required
def website_preview(request):
    profile = BusinessProfile.objects.filter(user=request.user).first()
    if not _business_profile_is_complete(profile):
        return redirect("core:onboarding")
    return render(
        request,
        "dashboard/website/preview.html",
        {"profile": profile},
    )


def signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("control_panel:home")
        lang = request.LANGUAGE_CODE or get_language()
        tenant = getattr(request, "tenant", None)
        if not tenant or getattr(tenant, "is_main", False):
            tenant = resolve_active_tenant(request)
        if tenant:
            dashboard_path = build_language_path(
                lang, reverse("tenant_dashboard:dashboard")
            )
            return redirect(tenant_site_url(tenant, dashboard_path, request=request))
        return redirect(build_language_url_for_path(request, lang, "/"))
    return signup(request)


def logout_view(request):
    logout(request)
    messages.success(request, _("You have been logged out."))
    return redirect(reverse("core:home"))


@login_required
def dashboard_control_panel(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect(_control_panel_url(request))
    return redirect("tenant_dashboard:dashboard")


@login_required
def dashboard_edit_home(request):
    return render(request, "dashboard/edit_home.html")


@require_POST
@login_required
def dashboard_inline_save(request):
    site = getattr(request, "tenant", None)
    if not site or getattr(site, "is_main", False):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    impersonating = request.session.get("impersonate_tenant_id") == site.id
    if not (
        request.user.is_staff
        or request.user.is_superuser
        or impersonating
        or site.owner_id == request.user.id
    ):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    field_id = payload.get("field_id") or payload.get("fieldId")
    page_id = payload.get("page_id") or payload.get("pageId")
    section_id = payload.get("section_id") or payload.get("sectionId")
    field_key = payload.get("field_key") or payload.get("fieldKey")
    value = payload.get("value", "")

    if field_id and not (page_id and section_id and field_key):
        match = re.match(r"p(?P<page>\d+)-s(?P<section>\d+)-(?P<field>.+)", field_id)
        if match:
            page_id = int(match.group("page"))
            section_id = int(match.group("section"))
            field_key = match.group("field")

    if not (page_id and section_id and field_key):
        return JsonResponse({"ok": False, "error": "Missing field identifiers"}, status=400)

    page = Page.objects.filter(id=page_id, site=site).first()
    if not page:
        return JsonResponse({"ok": False, "error": "Page not found"}, status=404)

    section = PageSection.objects.filter(id=section_id, page=page).first()
    if not section:
        return JsonResponse({"ok": False, "error": "Section not found"}, status=404)

    content, _created = SectionContent.objects.get_or_create(section=section)
    language_code = request.LANGUAGE_CODE or get_language()
    data = _get_localized_section_data(content, language_code)
    clean_value = strip_tags(value or "").strip()

    path = field_key.split(".")
    section_type = (section.key or "").split(".")[-1]
    if path and path[0] == section_type:
        path = path[1:]
    if not path:
        return JsonResponse({"ok": False, "error": "Invalid field key"}, status=400)

    _set_config_value(data, path, clean_value)
    content.config_json = data
    _set_localized_section_data(content, language_code, data)
    content.save(update_fields=["config_json", "config_json_i18n"])

    return JsonResponse({"ok": True, "value": clean_value})


@require_POST
@login_required
def dashboard_section_settings(request):
    site = getattr(request, "tenant", None)
    if not site or getattr(site, "is_main", False):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    # Verify request is NOT from main site host
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
        return JsonResponse({"ok": False, "error": "Forbidden: tenant endpoint only"}, status=403)

    impersonating = request.session.get("impersonate_tenant_id") == site.id
    if not (
        request.user.is_staff
        or request.user.is_superuser
        or impersonating
        or site.owner_id == request.user.id
    ):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    section_key = payload.get("section_key") or payload.get("sectionKey")
    settings_data = payload.get("settings") or {}
    if not isinstance(settings_data, dict):
        return JsonResponse({"ok": False, "error": "Invalid settings"}, status=400)

    if section_key not in ("hero", "home.hero", "page.hero"):
        return JsonResponse({"ok": False, "error": "Unsupported section"}, status=400)

    record, _created = TenantHeroSettings.objects.get_or_create(site=site)
    current = record.config_json if isinstance(record.config_json, dict) else {}
    current.update(settings_data)
    record.config_json = current
    record.save(update_fields=["config_json", "updated_at"])

    return JsonResponse({"ok": True, "settings": current})


@require_POST
@login_required
def main_section_settings(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    # Verify request is from main site (not tenant subdomain)
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
    if host not in main_hosts:
        return JsonResponse({"ok": False, "error": "Forbidden: main site only"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    page_key = payload.get("page") or payload.get("page_key") or "home"
    section_key = payload.get("section_key") or payload.get("sectionKey")
    settings_data = payload.get("settings") or {}
    if not section_key or not isinstance(settings_data, dict):
        return JsonResponse({"ok": False, "error": "Invalid settings"}, status=400)

    record, _created = MainSiteSectionSettings.objects.get_or_create(
        page_key=page_key, section_key=section_key
    )
    current = record.settings_json if isinstance(record.settings_json, dict) else {}
    current.update(settings_data)
    record.settings_json = current
    record.save(update_fields=["settings_json", "updated_at"])
    return JsonResponse({"ok": True, "settings": current})


@require_POST
@login_required
def main_inline_save(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

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
    if host not in main_hosts:
        return JsonResponse({"ok": False, "error": "Forbidden: main site only"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    allowed_keys = {
        "home.faq.q1.answer",
        "home.faq.q1.question",
        "home.faq.q2.answer",
        "home.faq.q2.question",
        "home.faq.q3.answer",
        "home.faq.q3.question",
        "home.faq.q4.answer",
        "home.faq.q4.question",
        "home.faq.q5.answer",
        "home.faq.q5.question",
        "home.faq.q6.answer",
        "home.faq.q6.question",
        "home.faq.title",
        "home.footer.company.link1.label",
        "home.footer.company.link1.url",
        "home.footer.company.link2.label",
        "home.footer.company.link2.url",
        "home.footer.company.link3.label",
        "home.footer.company.link3.url",
        "home.footer.company.link4.label",
        "home.footer.company.link4.url",
        "home.footer.company.link5.label",
        "home.footer.company.link5.url",
        "home.footer.company.link6.label",
        "home.footer.company.link6.url",
        "home.footer.company.title",
        "home.footer.copyright.rights",
        "home.footer.description",
        "home.footer.legal.link1.label",
        "home.footer.legal.link1.url",
        "home.footer.legal.link2.label",
        "home.footer.legal.link2.url",
        "home.footer.legal.link3.label",
        "home.footer.legal.link3.url",
        "home.footer.legal.link4.label",
        "home.footer.legal.link4.url",
        "home.footer.location",
        "home.footer.newsletter.subscribe_label",
        "home.footer.newsletter.title",
        "home.footer.services.link1.label",
        "home.footer.services.link1.url",
        "home.footer.services.link2.label",
        "home.footer.services.link2.url",
        "home.footer.services.link3.label",
        "home.footer.services.link3.url",
        "home.footer.services.link4.label",
        "home.footer.services.link4.url",
        "home.footer.services.link5.label",
        "home.footer.services.link5.url",
        "home.footer.services.link6.label",
        "home.footer.services.link6.url",
        "home.footer.services.title",
        "home.footer.support.link1.label",
        "home.footer.support.link1.url",
        "home.footer.support.link2.label",
        "home.footer.support.link2.url",
        "home.footer.support.link3.label",
        "home.footer.support.link3.url",
        "home.footer.support.link4.label",
        "home.footer.support.link4.url",
        "home.footer.support.link5.label",
        "home.footer.support.link5.url",
        "home.footer.support.link6.label",
        "home.footer.support.link6.url",
        "home.footer.support.title",
        "home.footer.tools.link1.label",
        "home.footer.tools.link1.url",
        "home.footer.tools.link2.label",
        "home.footer.tools.link2.url",
        "home.footer.tools.link3.label",
        "home.footer.tools.link3.url",
        "home.footer.tools.link4.label",
        "home.footer.tools.link4.url",
        "home.footer.tools.link5.label",
        "home.footer.tools.link5.url",
        "home.footer.tools.link6.label",
        "home.footer.tools.link6.url",
        "home.footer.tools.title",
        "home.hero.card1_text",
        "home.hero.card1_title",
        "home.hero.card2_text",
        "home.hero.card2_title",
        "home.hero.card3_text",
        "home.hero.card3_title",
        "home.hero.cta_primary",
        "home.hero.cta_print_label",
        "home.hero.cta_secondary",
        "home.hero.subtitle",
        "home.hero.title",
        "home.pricing.cta_button_label",
        "home.pricing.cta_button_url",
        "home.pricing.cta_title",
        "home.pricing.disclaimer",
        "home.pricing.provider1.cta_label",
        "home.pricing.provider1.cta_url",
        "home.pricing.provider1.description",
        "home.pricing.provider1.good_for",
        "home.pricing.provider1.name",
        "home.pricing.provider2.cta_label",
        "home.pricing.provider2.cta_url",
        "home.pricing.provider2.description",
        "home.pricing.provider2.good_for",
        "home.pricing.provider2.name",
        "home.pricing.provider3.cta_label",
        "home.pricing.provider3.cta_url",
        "home.pricing.provider3.description",
        "home.pricing.provider3.good_for",
        "home.pricing.provider3.name",
        "home.pricing.subtitle",
        "home.pricing.title",
        "home.pricing.type1.bullet1",
        "home.pricing.type1.bullet2",
        "home.pricing.type1.bullet3",
        "home.pricing.type1.cta_label",
        "home.pricing.type1.cta_url",
        "home.pricing.type1.label",
        "home.pricing.type1.subtitle",
        "home.pricing.type2.bullet1",
        "home.pricing.type2.bullet2",
        "home.pricing.type2.bullet3",
        "home.pricing.type2.cta_label",
        "home.pricing.type2.cta_url",
        "home.pricing.type2.label",
        "home.pricing.type2.subtitle",
        "home.pricing.type3.bullet1",
        "home.pricing.type3.bullet2",
        "home.pricing.type3.bullet3",
        "home.pricing.type3.cta_label",
        "home.pricing.type3.cta_url",
        "home.pricing.type3.label",
        "home.pricing.type3.subtitle",
        "home.quick_start.card1.body",
        "home.quick_start.card1.title",
        "home.quick_start.card2.body",
        "home.quick_start.card2.title",
        "home.quick_start.card3.body",
        "home.quick_start.card3.title",
        "home.quick_start.card4.body",
        "home.quick_start.card4.title",
        "home.quick_start.label",
        "home.quick_start.title",
        "home.solutions.card1.badge",
        "home.solutions.card1.body",
        "home.solutions.card1.bullet1",
        "home.solutions.card1.bullet2",
        "home.solutions.card1.bullet3",
        "home.solutions.card1.cta_label",
        "home.solutions.card1.icon",
        "home.solutions.card1.title",
        "home.solutions.card2.badge",
        "home.solutions.card2.body",
        "home.solutions.card2.bullet1",
        "home.solutions.card2.bullet2",
        "home.solutions.card2.bullet3",
        "home.solutions.card2.cta_label",
        "home.solutions.card2.icon",
        "home.solutions.card2.title",
        "home.solutions.card3.badge",
        "home.solutions.card3.body",
        "home.solutions.card3.bullet1",
        "home.solutions.card3.bullet2",
        "home.solutions.card3.bullet3",
        "home.solutions.card3.cta_label",
        "home.solutions.card3.icon",
        "home.solutions.card3.title",
        "home.solutions.card4.badge",
        "home.solutions.card4.body",
        "home.solutions.card4.cta_label",
        "home.solutions.card4.cta_url",
        "home.solutions.card4.title",
        "home.solutions.card5.badge",
        "home.solutions.card5.body",
        "home.solutions.card5.cta_label",
        "home.solutions.card5.cta_url",
        "home.solutions.card5.title",
        "home.solutions.card6.badge",
        "home.solutions.card6.body",
        "home.solutions.card6.cta_label",
        "home.solutions.card6.cta_url",
        "home.solutions.card6.title",
        "home.solutions.card7.badge",
        "home.solutions.card7.body",
        "home.solutions.card7.cta_label",
        "home.solutions.card7.cta_url",
        "home.solutions.card7.title",
        "home.solutions.card8.badge",
        "home.solutions.card8.body",
        "home.solutions.card8.cta_label",
        "home.solutions.card8.cta_url",
        "home.solutions.card8.title",
        "home.solutions.card9.badge",
        "home.solutions.card9.body",
        "home.solutions.card9.cta_label",
        "home.solutions.card9.cta_url",
        "home.solutions.card9.title",
        "home.solutions.subtitle",
        "home.solutions.title",
    }
    icon_keys = {
        "home.solutions.card1.icon",
        "home.solutions.card2.icon",
        "home.solutions.card3.icon",
    }
    url_keys = {key for key in allowed_keys if key.endswith(".url") or key.endswith("_url")}
    icon_value_pattern = re.compile(r"^[a-z0-9_-]{0,40}$")
    max_value_length = 2000

    def _is_valid_url(value):
        if not value:
            return True
        lowered = value.strip().lower()
        if lowered.startswith("javascript:"):
            return False
        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"}:
            return True
        if parsed.scheme == "" and (
            value.startswith("/")
            or value.startswith("#")
            or value.startswith("./")
            or value.startswith("../")
        ):
            return True
        return False
    content_map = {}
    if isinstance(payload, dict):
        field_key = payload.get("field_key") or payload.get("fieldKey")
        if field_key:
            content_map = {field_key: payload.get("value", "")}
        else:
            content_map = payload
    if not isinstance(content_map, dict):
        return JsonResponse({"ok": False, "error": "Invalid payload"}, status=400)

    lang = request.LANGUAGE_CODE or get_language()
    updated = False
    for key, value in content_map.items():
        if key not in allowed_keys:
            continue
        clean_value = strip_tags(value or "").strip()
        if len(clean_value) > max_value_length:
            clean_value = clean_value[:max_value_length]
        if key in icon_keys and not icon_value_pattern.match(clean_value):
            return JsonResponse({"ok": False, "error": "Invalid icon key"}, status=400)
        if key in url_keys and not _is_valid_url(clean_value):
            return JsonResponse({"ok": False, "error": "Invalid URL"}, status=400)
        MainSiteContent.objects.update_or_create(
            key=key, language=lang, defaults={"value": clean_value}
        )
        updated = True

    if not updated:
        return JsonResponse({"ok": False, "error": "No valid fields"}, status=400)

    return JsonResponse({"ok": True})


@login_required
def _render_page_edit(
    request,
    page,
    redirect_name,
    *,
    dashboard_base_template="dashboard/base_dashboard.html",
    page_list_url_name=None,
):
    display_title = None
    if hasattr(page, "safe_translation_getter"):
        display_title = page.safe_translation_getter("title", any_language=True)
    display_title = display_title or page.slug

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
        "title": "Your headline",
        "subtitle": "Your subtitle",
        "cta_text": "Get started",
        "cta_url": "/contact/",
    }
    content, created = SectionContent.objects.get_or_create(
        section=hero_section,
        defaults={"config_json": default_hero},
    )
    language_code = request.LANGUAGE_CODE or get_language()
    data = _get_localized_section_data(content, language_code)
    if not data:
        data = dict(default_hero)

    initial = {
        "title": data.get("title", ""),
        "subtitle": data.get("subtitle", ""),
        "cta_text": data.get("cta_text", ""),
        "cta_url": data.get("cta_url", ""),
    }
    if request.method == "POST":
        form = HeroContentForm(request.POST)
        if form.is_valid():
            updated = dict(data)
            updated.update(form.cleaned_data)
            content.config_json = updated
            _set_localized_section_data(content, language_code, updated)
            content.save(update_fields=["config_json", "config_json_i18n"])
            messages.success(request, _("Hero content saved."))
            return redirect(reverse(redirect_name, args=[page.id]))
    else:
        form = HeroContentForm(initial=initial)

    public_url = (
        reverse("core:home")
        if page.slug == "home"
        else reverse("core:public_page", args=[page.slug])
    )

    context = {
        "page": page,
        "display_title": display_title,
        "public_url": public_url,
        "form": form,
        "dashboard_base_template": dashboard_base_template,
        "page_list_url": reverse(page_list_url_name) if page_list_url_name else "",
    }
    return render(request, "dashboard/page_edit.html", context)


def dashboard_edit_page(request, page_id):
    tenant = getattr(request, "tenant", None)
    site = None
    if tenant:
        site = Site.objects.filter(id=tenant.id).first()
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = get_object_or_404(Page, id=page_id, site=site)
    return _render_page_edit(request, page, "tenant_dashboard:page_edit")


@login_required
def dashboard_edit_page_services(request, page_id):
    tenant = getattr(request, "tenant", None)
    site = None
    if tenant:
        site = Site.objects.filter(id=tenant.id).first()
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = get_object_or_404(Page, id=page_id, site=site)

    services_section = None
    for section in page.sections.all().order_by("order", "id"):
        key = section.key or ""
        if key.split(".")[-1] == "services":
            services_section = section
            break
    if not services_section:
        services_section = PageSection.objects.create(
            page=page,
            key=f"{page.slug}.services",
            order=0,
            is_visible=True,
        )

    default_services = {
        "heading": "Services",
        "intro": "",
        "items": [
            {"title": "Service 1", "description": "", "icon": ""},
        ],
    }
    content, _created = SectionContent.objects.get_or_create(
        section=services_section,
        defaults={"config_json": default_services},
    )
    language_code = request.LANGUAGE_CODE or get_language()
    data = _get_localized_section_data(content, language_code)
    if not data:
        data = dict(default_services)

    errors = {}
    if request.method == "POST":
        action = request.POST.get("action") or "save"
        heading = (request.POST.get("heading") or "").strip()
        intro = (request.POST.get("intro") or "").strip()
        try:
            item_count = int(request.POST.get("item_count") or 0)
        except ValueError:
            item_count = 0

        items = []
        for index in range(max(item_count, 0)):
            title = (request.POST.get(f"item_title_{index}") or "").strip()
            description = (request.POST.get(f"item_desc_{index}") or "").strip()
            icon = (request.POST.get(f"item_icon_{index}") or "").strip()
            items.append({"title": title, "description": description, "icon": icon})

        if action == "save":
            if not heading:
                errors["heading"] = _("Heading is required.")
            cleaned_items = [item for item in items if item.get("title")]
            if not errors:
                payload = {
                    "heading": heading,
                    "intro": intro,
                    "items": cleaned_items,
                }
                content.config_json = payload
                _set_localized_section_data(content, language_code, payload)
                content.save(update_fields=["config_json", "config_json_i18n"])
                messages.success(request, _("Services content saved."))
                return redirect(reverse("tenant_dashboard:page_edit_services", args=[page.id]))
        else:
            items.append({"title": "", "description": "", "icon": ""})
            item_count = len(items)
    else:
        heading = data.get("heading", "")
        intro = data.get("intro", "")
        items = data.get("items") if isinstance(data.get("items"), list) else []
        if not items:
            items = [{"title": "Service 1", "description": "", "icon": ""}]
        item_count = len(items)

    public_url = (
        reverse("core:home")
        if page.slug == "home"
        else reverse("core:public_page", args=[page.slug])
    )

    return render(
        request,
        "dashboard/page_edit_services.html",
        {
            "page": page,
            "heading_value": heading,
            "intro_value": intro,
            "items": items,
            "item_count": item_count,
            "errors": errors,
            "public_url": public_url,
        },
    )


@login_required
def dashboard_edit_page_contact(request, page_id):
    tenant = getattr(request, "tenant", None)
    site = None
    if tenant:
        site = Site.objects.filter(id=tenant.id).first()
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = get_object_or_404(Page, id=page_id, site=site)

    contact_section = None
    for section in page.sections.all().order_by("order", "id"):
        key = section.key or ""
        if key.split(".")[-1] == "contact":
            contact_section = section
            break
    if not contact_section:
        contact_section = PageSection.objects.create(
            page=page,
            key=f"{page.slug}.contact",
            order=0,
            is_visible=True,
        )

    default_contact = {
        "heading": "Contact",
        "intro": "Short text",
        "phone": "",
        "email": "",
        "address_line1": "",
        "address_line2": "",
        "postal_code": "",
        "city": "",
        "country": "",
        "map_embed_url": "",
        "cta_text": "Send message",
        "cta_url": "",
    }
    content, _created = SectionContent.objects.get_or_create(
        section=contact_section,
        defaults={"config_json": default_contact},
    )
    language_code = request.LANGUAGE_CODE or get_language()
    data = _get_localized_section_data(content, language_code)
    if not data:
        data = dict(default_contact)

    errors = {}
    if request.method == "POST":
        heading = (request.POST.get("heading") or "").strip()
        intro = (request.POST.get("intro") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        email = (request.POST.get("email") or "").strip()
        address_line1 = (request.POST.get("address_line1") or "").strip()
        address_line2 = (request.POST.get("address_line2") or "").strip()
        postal_code = (request.POST.get("postal_code") or "").strip()
        city = (request.POST.get("city") or "").strip()
        country = (request.POST.get("country") or "").strip()
        map_embed_url = (request.POST.get("map_embed_url") or "").strip()
        cta_text = (request.POST.get("cta_text") or "").strip()
        cta_url = (request.POST.get("cta_url") or "").strip()

        if not heading:
            errors["heading"] = _("Heading is required.")

        if not errors:
            payload = {
                "heading": heading,
                "intro": intro,
                "phone": phone,
                "email": email,
                "address_line1": address_line1,
                "address_line2": address_line2,
                "postal_code": postal_code,
                "city": city,
                "country": country,
                "map_embed_url": map_embed_url,
                "cta_text": cta_text,
                "cta_url": cta_url,
            }
            content.config_json = payload
            _set_localized_section_data(content, language_code, payload)
            content.save(update_fields=["config_json", "config_json_i18n"])
            messages.success(request, _("Contact content saved."))
            return redirect(reverse("tenant_dashboard:page_edit_contact", args=[page.id]))
    else:
        heading = data.get("heading", "")
        intro = data.get("intro", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        address_line1 = data.get("address_line1", "")
        address_line2 = data.get("address_line2", "")
        postal_code = data.get("postal_code", "")
        city = data.get("city", "")
        country = data.get("country", "")
        map_embed_url = data.get("map_embed_url", "")
        cta_text = data.get("cta_text", "")
        cta_url = data.get("cta_url", "")

    public_url = (
        reverse("core:home")
        if page.slug == "home"
        else reverse("core:public_page", args=[page.slug])
    )

    return render(
        request,
        "dashboard/page_edit_contact.html",
        {
            "page": page,
            "heading_value": heading,
            "intro_value": intro,
            "phone_value": phone,
            "email_value": email,
            "address_line1_value": address_line1,
            "address_line2_value": address_line2,
            "postal_code_value": postal_code,
            "city_value": city,
            "country_value": country,
            "map_embed_url_value": map_embed_url,
            "cta_text_value": cta_text,
            "cta_url_value": cta_url,
            "errors": errors,
            "public_url": public_url,
        },
    )


@login_required
def dashboard_page_seo(request, page_id):
    tenant = getattr(request, "tenant", None)
    site = None
    if tenant:
        site = Site.objects.filter(id=tenant.id).first()
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = get_object_or_404(Page, id=page_id, site=site)
    caps = get_seo_caps(tenant=site)
    allow_indexing = caps.get("allow_indexing", True)
    plan_blocks_indexing = (not is_page_indexable(site, page)) and not page.noindex
    lang = get_language()
    if hasattr(page, "set_current_language"):
        page.set_current_language(lang)

    if request.method == "POST":
        form = PageSEOForm(request.POST)
        if form.is_valid():
            meta_title = form.cleaned_data.get("meta_title") or ""
            meta_description = form.cleaned_data.get("meta_description") or ""
            if hasattr(page, "set_current_language"):
                page.set_current_language(lang)
            page.meta_title = meta_title
            page.meta_description = meta_description
            page.seo_title = meta_title
            page.seo_description = meta_description
            requested_noindex = bool(form.cleaned_data.get("noindex"))
            if allow_indexing:
                page.noindex = requested_noindex
            elif requested_noindex != page.noindex:
                messages.error(
                    request, _("Indexing controls are locked for your plan.")
                )
            page.save()
            messages.success(request, _("SEO settings saved."))
            return redirect(reverse("tenant_dashboard:page_seo", args=[page.id]))
    else:
        translated_title = None
        translated_description = None
        if hasattr(page, "safe_translation_getter"):
            translated_title = page.safe_translation_getter("meta_title", any_language=True)
            translated_description = page.safe_translation_getter("meta_description", any_language=True)
        form = PageSEOForm(
            initial={
                "meta_title": translated_title or page.seo_title,
                "meta_description": translated_description or page.seo_description,
                "noindex": page.noindex,
            }
        )
    if not allow_indexing:
        form.fields["noindex"].disabled = True

    title_count = len(form.data.get("meta_title", "")) if request.method == "POST" else len(form.initial.get("meta_title") or "")
    description_count = len(form.data.get("meta_description", "")) if request.method == "POST" else len(form.initial.get("meta_description") or "")

    return render(
        request,
        "dashboard/page_seo.html",
        {
            "page": page,
            "form": form,
            "title_count": title_count,
            "description_count": description_count,
            "plan_blocks_indexing": plan_blocks_indexing,
            "allow_indexing": allow_indexing,
            "indexing_locked_hint": _("Upgrade your plan to control indexing."),
        },
    )


@login_required
def dashboard_main_site_edit_page(
    request,
    page_id,
    *,
    dashboard_base_template="dashboard/base_dashboard.html",
    redirect_name="tenant_dashboard:main_site_page_edit",
    page_list_url_name=None,
):
    if not request.user.is_staff:
        return redirect("core:dashboard")

    site = _get_main_site_or_create(request)
    page = get_object_or_404(Page, id=page_id, site=site)
    return _render_page_edit(
        request,
        page,
        redirect_name,
        dashboard_base_template=dashboard_base_template,
        page_list_url_name=page_list_url_name,
    )


@login_required
def legacy_dashboard_main_site_edit_page(request, page_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect(_control_panel_url(request, f"/control-panel/main-site/pages/{page_id}/edit/"))
    return redirect("tenant_dashboard:dashboard")


@login_required
@require_POST
def dashboard_create_home(request):
    site = getattr(request, "tenant", None)
    if not site:
        return redirect(f"{reverse('core:dashboard_choose_template')}?notice=choose-template")

    page = Page.objects.filter(site=site, slug="home").first()
    if not page:
        page = Page.objects.create(
            site=site,
            slug="home",
            is_active=True,
            template_key=site.template_key,
        )
        lang = get_language()
        page.set_current_language(lang)
        page.title = _("Home")
        page.meta_title = page.title
        page.meta_description = ""
        page.save()

    return redirect(reverse("tenant_dashboard:page_edit", args=[page.id]))


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
    default_plan = _get_default_plan()
    site, _created = Site.objects.get_or_create(
        owner=request.user,
        defaults={
            "name": f"{request.user.username} Site",
            "language": language,
            "template_key": template.slug,
            "status": Site.STATUS_DRAFT,
            "plan": default_plan,
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


def public_assistant_chat(request):
    site = getattr(request, "site", None)
    if not site or not site.is_main:
        return JsonResponse({"error": "Assistant unavailable."}, status=404)
    profile = AssistantProfile.objects.filter(site=site, enabled=True, frontend_enabled=True).first()
    if not profile:
        return JsonResponse({"error": "Assistant unavailable."}, status=404)

    session_key = f"public_assistant_thread:{site.id}"
    if request.POST.get("action") == "clear":
        request.session.pop(session_key, None)
        request.session.modified = True
        return JsonResponse({"cleared": True})

    language = (request.POST.get("conversation_language") or getattr(request, "LANGUAGE_CODE", "en")).lower()
    if language not in supported_language_codes():
        language = "en"
    message = (request.POST.get("message") or "").strip()
    if len(message) > 1200:
        return JsonResponse({"error": "Please keep the message under 1,200 characters."}, status=400)
    history = request.session.get(session_key, [])
    try:
        answer, context = request_assistant_response(
            profile,
            message=message,
            conversation_language=language,
            content_language=language,
            surface="frontend",
            history=history,
        )
    except AssistantServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    history = (history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ])[-12:]
    request.session[session_key] = history
    request.session.modified = True
    return JsonResponse({
        "answer": answer,
        "conversation_language": context["languages"]["conversation_language"],
    })

def robots_txt(request):
    if getattr(settings, "SEO_NOINDEX", False) or not getattr(getattr(request, "site", None), "is_main", False):
        content = "User-agent: *\nDisallow: /\n"
        return HttpResponse(content, content_type="text/plain")

    lines = ["User-agent: *", "Disallow: /"]
    for code, _name in settings.LANGUAGES:
        for public_path in INDEXABLE_PUBLIC_PATHS:
            path = build_language_path(code, public_path)
            lines.append(f"Allow: {path}$")
    lines.append(f"Sitemap: {request.build_absolute_uri(reverse('sitemap_xml'))}")
    lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain")

def tenant_robots_txt(request):
    tenant = resolve_active_site(request)
    if not tenant:
        content = "\n".join(
            [
                "User-agent: *",
                "Disallow: /",
                "",
            ]
        )
        return HttpResponse(content, content_type="text/plain")

    if getattr(settings, "SEO_NOINDEX", False):
        content = "\n".join(
            [
                "User-agent: *",
                "Disallow: /",
                "",
            ]
        )
        return HttpResponse(content, content_type="text/plain")

    settings_obj = get_site_settings()
    sitemap_url = request.build_absolute_uri(reverse("tenant_sitemap_xml"))
    lines = [
        "User-agent: *",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "Disallow: /control-panel/",
    ]
    if settings_obj.launch_disallow_robots:
        lines.append("Disallow: /")
    lines.append(f"Sitemap: {sitemap_url}")
    lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    sitemap_urls = [
        request.build_absolute_uri(reverse("sitemap_language", args=[code]))
        for code, _name in settings.LANGUAGES
    ]
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in sitemap_urls:
        xml.extend(["  <sitemap>", f"    <loc>{escape(loc)}</loc>", "  </sitemap>"])
    xml.append("</sitemapindex>")
    return HttpResponse("\n".join(xml), content_type="application/xml")
def tenant_sitemap_xml(request):
    tenant = resolve_active_site(request)
    if not tenant:
        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            "</sitemapindex>",
        ]
        return HttpResponse("\n".join(xml), content_type="application/xml")

    sitemap_urls = []
    for code, _name in settings.LANGUAGES:
        loc = request.build_absolute_uri(
            reverse("tenant_sitemap_language", args=[code])
        )
        sitemap_urls.append(loc)

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in sitemap_urls:
        xml.append("  <sitemap>")
        xml.append(f"    <loc>{escape(loc)}</loc>")
        xml.append("  </sitemap>")
    xml.append("</sitemapindex>")
    return HttpResponse("\n".join(xml), content_type="application/xml")


def sitemap_language_xml(request, lang):
    valid_langs = {code for code, _name in settings.LANGUAGES}
    if lang not in valid_langs:
        return HttpResponse(status=404)
    paths = [(build_language_path(lang, path), priority) for path, priority in [
        ("/", "1.0"),
        ("/about/", "0.8"),
        ("/what-we-build/", "0.8"),
        ("/how-we-work/", "0.8"),
        ("/contact/", "0.8"),
        ("/privacy-cookies/", "0.5"),
    ]]
    urlset = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority in paths:
        urlset.extend([
            "  <url>",
            f"    <loc>{escape(request.build_absolute_uri(path))}</loc>",
            "    <changefreq>weekly</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ])
    urlset.append("</urlset>")
    return HttpResponse("\n".join(urlset), content_type="application/xml")
def tenant_sitemap_language_xml(request, lang):
    valid_langs = {code for code, _name in settings.LANGUAGES}
    if lang not in valid_langs:
        return HttpResponse(status=404)

    site = resolve_active_site(request)
    if not site:
        urlset = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            "</urlset>",
        ]
        return HttpResponse("\n".join(urlset), content_type="application/xml")

    pages = list(
        Page.objects.filter(site=site, is_active=True, noindex=False).order_by("slug")
    )

    entries = []
    has_home = False
    for page in pages:
        if not is_page_indexable(site, page):
            continue
        if page.slug == "home":
            has_home = True
            loc = request.build_absolute_uri(f"/{lang}/")
            priority = "1.0"
        else:
            loc = request.build_absolute_uri(f"/{lang}/{page.slug}/")
            priority = "0.6"
        lastmod = page.updated_at.date().isoformat() if getattr(page, "updated_at", None) else None
        entry = {"loc": loc, "lastmod": lastmod, "priority": priority}
        entries.append(entry)

    if not has_home and is_slug_indexable(site, "home"):
        entries.insert(
            0,
            {
                "loc": request.build_absolute_uri(f"/{lang}/"),
                "lastmod": None,
                "priority": "1.0",
            },
        )

    for entry in get_location_entries_for_site(site, lang, request):
        entries.append(entry)

    urlset = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for entry in entries:
        urlset.append("  <url>")
        urlset.append(f"    <loc>{escape(entry['loc'])}</loc>")
        if entry.get("lastmod"):
            urlset.append(f"    <lastmod>{entry['lastmod']}</lastmod>")
        urlset.append("    <changefreq>weekly</changefreq>")
        urlset.append(f"    <priority>{entry['priority']}</priority>")
        urlset.append("  </url>")
    urlset.append("</urlset>")
    return HttpResponse("\n".join(urlset), content_type="application/xml")

def location_country(request, country):
    site = resolve_active_site(request)
    if not site:
        return render(request, "site/404.html", status=404)
    if not is_location_allowed(site, country, city=None):
        return render(request, "site/404.html", status=404)

    country_name = get_country_name(country)
    heading = _("Services in %(country)s") % {"country": country_name}
    description = _("Visibility landing page for %(country)s.") % {"country": country_name}
    lang = request.LANGUAGE_CODE

    page = SimpleNamespace(
        seo_title=f"{heading} | {site.name}",
        seo_description=description,
        noindex=False,
    )
    sections = [
        {
            "type": "location",
            "data": {
                "heading": heading,
                "description": description,
                "services_url": build_language_url_for_path(request, lang, "/services/"),
                "contact_url": build_language_url_for_path(request, lang, "/contact/"),
            },
        }
    ]

    caps = get_seo_caps(request=request, tenant=site)
    canonical_url = build_canonical_url(request)
    hreflang_urls = (
        build_hreflang_urls(request) if caps.get("allow_hreflang", True) else []
    )
    schema_json = json.dumps(build_schema(site, get_site_settings(), request, page=None), ensure_ascii=False)
    city_links = _build_city_links(request, site, exclude_city=None)

    return render(
        request,
        "site/page.html",
        {
            "page": page,
            "page_title": heading,
            "seo_title": page.seo_title,
            "seo_description": page.seo_description,
            "seo_robots": "index, follow",
            "schema_json": schema_json,
            "canonical_url": canonical_url,
            "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": False,
            "sections": sections,
            "nav_pages": _build_nav_pages(site),
            "city_links": city_links,
        },
    )


def location_city(request, country, city):
    site = resolve_active_site(request)
    if not site:
        return render(request, "site/404.html", status=404)
    if not is_location_allowed(site, country, city=city):
        return render(request, "site/404.html", status=404)

    country_name = get_country_name(country)
    city_name = " ".join(normalize_city(city).split("-")).title()
    heading = _("Services in %(city)s, %(country)s") % {"city": city_name, "country": country_name}
    description = _("Visibility landing page for %(city)s.") % {"city": city_name}
    lang = request.LANGUAGE_CODE

    page = SimpleNamespace(
        seo_title=f"{heading} | {site.name}",
        seo_description=description,
        noindex=False,
    )
    sections = [
        {
            "type": "location",
            "data": {
                "heading": heading,
                "description": description,
                "services_url": build_language_url_for_path(request, lang, "/services/"),
                "contact_url": build_language_url_for_path(request, lang, "/contact/"),
            },
        }
    ]

    caps = get_seo_caps(request=request, tenant=site)
    canonical_url = build_canonical_url(request)
    hreflang_urls = (
        build_hreflang_urls(request) if caps.get("allow_hreflang", True) else []
    )
    schema_json = json.dumps(build_schema(site, get_site_settings(), request, page=None), ensure_ascii=False)
    city_links = _build_city_links(request, site, exclude_city=city)

    return render(
        request,
        "site/page.html",
        {
            "page": page,
            "page_title": heading,
            "seo_title": page.seo_title,
            "seo_description": page.seo_description,
            "seo_robots": "index, follow",
            "schema_json": schema_json,
            "canonical_url": canonical_url,
            "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": False,
            "sections": sections,
            "nav_pages": _build_nav_pages(site),
            "city_links": city_links,
        },
    )

# Create your views here.
