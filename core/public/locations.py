import json
from types import SimpleNamespace

from django.shortcuts import render
from django.utils.translation import get_language

from core.data.eu_locations import COUNTRIES
from core.public.tenant import resolve_active_site
from core.schema import build_schema
from core.seo_caps import get_seo_caps
from core.services.site_settings import get_site_settings
from core.services.visibility import get_seo_target_cities, normalize_city as normalize_city_slug
from core.seo_utils import build_canonical_url, build_hreflang_urls, build_language_url_for_path
from core.visibility_rules import sync_visibility_from_plan
from core.models import Page, SiteVisibility


def normalize_country(code):
    return (code or "").strip().lower()


def slugify_city(name):
    return "-".join((name or "").strip().lower().split())


def _get_country(code):
    code = (code or "").upper()
    for country in COUNTRIES:
        if country.get("code") == code:
            return country
    return None


def _default_location_from_settings(site_settings):
    city = (getattr(site_settings, "city", "") or "").strip()
    country = (getattr(site_settings, "country", "") or "").strip()
    if not city or not country:
        return None
    return {"country": country, "city": city}


def _default_location_from_visibility(site_visibility):
    for item in site_visibility.allowed_cities or []:
        if not isinstance(item, dict):
            continue
        country = (item.get("country") or "").strip()
        city = (item.get("city") or "").strip()
        if country and city:
            return {"country": country, "city": city}
    return None


def _matches_location(entry, country_code, city_name):
    if not entry:
        return False
    country = (entry.get("country") or "").strip()
    city = (entry.get("city") or "").strip()
    return country.upper() == country_code.upper() and city.lower() == city_name.lower()


def get_default_location(site_visibility, site_settings):
    default_location = _default_location_from_visibility(site_visibility)
    if default_location:
        return default_location
    return _default_location_from_settings(site_settings)


def is_location_allowed(site, country_code, city_name=None):
    if not site:
        return False
    caps = get_seo_caps(tenant=site)
    if not caps["allow_location_pages"]:
        return False
    site_settings = get_site_settings()
    visibility = sync_visibility_from_plan(site)
    visibility_mode = visibility.visibility_mode
    if visibility_mode == SiteVisibility.MODE_BASIC:
        return False

    country = _get_country(country_code)
    if not country:
        return False

    if city_name is None:
        if visibility_mode == SiteVisibility.MODE_LOCATIONS:
            for entry in visibility.allowed_cities or []:
                if not isinstance(entry, dict):
                    continue
                if (entry.get("country") or "").strip().upper() == country.get("code"):
                    return True
            return False
        if visibility_mode == SiteVisibility.MODE_EU:
            return True
        return False

    if visibility_mode == SiteVisibility.MODE_LOCATIONS:
        for entry in visibility.allowed_cities or []:
            if not isinstance(entry, dict):
                continue
            if _matches_location(entry, country.get("code"), city_name):
                return True
        return False

    if visibility_mode == SiteVisibility.MODE_EU:
        return any(city.lower() == city_name.lower() for city in country.get("cities", []))

    return False


def _city_from_slug(country_code, city_slug):
    country = _get_country(country_code)
    if not country:
        return None, None
    target = " ".join((city_slug or "").split("-")).strip().lower()
    for city in country.get("cities", []):
        if city.lower() == target:
            return country, city
    return None, None


def _build_nav_pages(site):
    pages = (
        Page.objects.filter(site=site, is_active=True, show_in_nav=True)
        .prefetch_related("translations")
        .order_by("nav_order", "slug")
    )
    lang = get_language()
    nav_pages = []
    for page in pages:
        page.set_current_language(lang)
        title = page.safe_translation_getter("nav_label", any_language=True)
        if not title:
            title = page.safe_translation_getter("title", any_language=True)
        title = title or page.slug
        nav_pages.append({"slug": page.slug, "title": title})
    return nav_pages


def public_location_landing(request, country_code, city_slug=None):
    site = resolve_active_site(request)
    if not site:
        return render(request, "site/404.html", status=404)

    site_settings = get_site_settings()
    sync_visibility_from_plan(site)

    country = _get_country(country_code)
    if not country:
        return render(request, "site/404.html", status=404)

    city = None
    if city_slug:
        country, city = _city_from_slug(country_code, city_slug)
        if not country or not city:
            return render(request, "site/404.html", status=404)
        if not is_location_allowed(site, country.get("code"), city):
            return render(request, "site/404.html", status=404)
    else:
        if not is_location_allowed(site, country.get("code"), None):
            return render(request, "site/404.html", status=404)

    business_name = (getattr(site_settings, "business_name", "") or "").strip() or site.name
    schema_json = json.dumps(build_schema(site, site_settings, request, page=None), ensure_ascii=False)
    canonical_url = build_canonical_url(request)
    hreflang_urls = build_hreflang_urls(request)
    lang = request.LANGUAGE_CODE
    nav_pages = _build_nav_pages(site)

    if city:
        heading = f"{city}, {country['name']}"
        description = f"Visibility landing page for {city}."
    else:
        heading = f"{country['name']}"
        description = f"Visibility landing page for {country['name']}."

    page = SimpleNamespace(
        seo_title=f"{heading} | {business_name}",
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
    city_links = []
    for entry in get_seo_target_cities(site):
        entry_country = entry.get("country")
        entry_city = entry.get("city")
        if not entry_country or not entry_city:
            continue
        if city_slug and normalize_city_slug(entry_city) == normalize_city_slug(city_slug):
            continue
        url = build_language_url_for_path(
            request,
            lang,
            f"/locations/{entry_country}/{entry_city}/",
        )
        label = " ".join(entry_city.split("-")).title()
        city_links.append({"label": label, "url": url})

    return render(
        request,
        "site/page.html",
        {
            "site": site,
            "business_name": business_name,
            "country": country["name"],
            "country_code": country["code"],
            "city": city,
            "schema_json": schema_json,
            "canonical_url": canonical_url,
            "hreflang_urls": hreflang_urls,
            "plan_blocks_indexing": False,
            "nav_pages": nav_pages,
            "page_title": heading,
            "seo_title": page.seo_title,
            "seo_description": page.seo_description,
            "page": page,
            "sections": sections,
            "city_links": city_links,
        },
    )
