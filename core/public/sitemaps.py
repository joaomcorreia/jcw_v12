from core.seo_caps import get_seo_caps
from core.services.visibility import get_allowed_countries, get_seo_target_cities, normalize_city, normalize_country
from core.seo_utils import build_language_url_for_path
from core.visibility_rules import sync_visibility_from_plan
from core.models import SiteVisibility


def _location_url(request, lang, country_code, city_slug=None):
    country = normalize_country(country_code)
    if city_slug:
        city_slug = normalize_city(city_slug)
        path = f"/locations/{country}/{city_slug}/"
        return build_language_url_for_path(request, lang, path)
    path = f"/locations/{country}/"
    return build_language_url_for_path(request, lang, path)


def get_location_entries_for_site(site, lang, request):
    caps = get_seo_caps(request=request, tenant=site)
    visibility = sync_visibility_from_plan(site)
    visibility_mode = visibility.visibility_mode

    entries = []
    lastmod = None
    if getattr(visibility, "last_updated", None):
        lastmod = visibility.last_updated.date().isoformat()

    if visibility_mode == SiteVisibility.MODE_BASIC or not caps["allow_location_pages"]:
        return entries

    allowed_cities = get_seo_target_cities(site)
    allowed_countries = get_allowed_countries(site)
    if not allowed_countries and allowed_cities:
        allowed_countries = sorted({entry.get("country") for entry in allowed_cities if entry.get("country")})

    for country in sorted(set(allowed_countries)):
        entries.append(
            {
                "loc": _location_url(request, lang, country),
                "lastmod": lastmod,
                "priority": "0.4",
            }
        )

    for entry in allowed_cities:
        country = entry.get("country")
        city = entry.get("city")
        if not country or not city:
            continue
        entries.append(
            {
                "loc": _location_url(request, lang, country, city),
                "lastmod": lastmod,
                "priority": "0.4",
            }
        )

    cap = caps["sitemap_cap"]
    if cap and len(entries) > cap:
        return entries[:cap]
    return entries
