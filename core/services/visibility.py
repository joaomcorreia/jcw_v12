from django.conf import settings

from core.data.eu_locations import COUNTRIES
from core.models import SiteVisibility
from core.seo_caps import get_seo_caps
from core.visibility_rules import get_visibility_limits, sync_visibility_from_plan
from core.models import TenantSEOSettings


def normalize_country(country):
    return (country or "").strip().lower()


def normalize_city(city):
    return "-".join((city or "").strip().lower().split())


def _get_visibility(site):
    if not site:
        return None
    return sync_visibility_from_plan(site)


def get_allowed_countries(site):
    visibility = _get_visibility(site)
    if not visibility:
        return []
    mode = visibility.visibility_mode
    if mode == SiteVisibility.MODE_BASIC:
        return []
    if mode == SiteVisibility.MODE_LOCATIONS:
        allowed = [normalize_country(code) for code in (visibility.allowed_countries or [])]
        if not allowed:
            for entry in visibility.allowed_cities or []:
                if not isinstance(entry, dict):
                    continue
                country = normalize_country(entry.get("country"))
                if country:
                    allowed.append(country)
        limits = get_visibility_limits(site)
        max_countries = limits["max_countries"]
        if max_countries is not None:
            allowed = allowed[:max_countries]
        return allowed
    if mode == SiteVisibility.MODE_EU:
        return [normalize_country(country["code"]) for country in COUNTRIES]
    return []


def get_allowed_cities(site):
    visibility = _get_visibility(site)
    if not visibility:
        return []
    mode = visibility.visibility_mode
    if mode == SiteVisibility.MODE_BASIC:
        return []
    if mode == SiteVisibility.MODE_LOCATIONS:
        allowed = []
        for entry in visibility.allowed_cities or []:
            if not isinstance(entry, dict):
                continue
            country = normalize_country(entry.get("country"))
            city = normalize_city(entry.get("city"))
            if country and city:
                allowed.append({"country": country, "city": city})
        limits = get_visibility_limits(site)
        max_cities = limits["max_cities"]
        if max_cities is not None:
            allowed = allowed[:max_cities]
        return allowed
    if mode == SiteVisibility.MODE_EU:
        cap = getattr(settings, "LOCATION_SITEMAP_CAP", 50)
        allowed = []
        for country in COUNTRIES:
            for city in country.get("cities", []):
                allowed.append(
                    {
                        "country": normalize_country(country.get("code")),
                        "city": normalize_city(city),
                    }
                )
                if len(allowed) >= cap:
                    break
            if len(allowed) >= cap:
                break
        return allowed
    return []


def _country_in_dataset(country_code):
    for country in COUNTRIES:
        if normalize_country(country.get("code")) == normalize_country(country_code):
            return True
    return False


def is_location_allowed(site, country, city=None):
    visibility = _get_visibility(site)
    if not visibility:
        return False
    caps = get_seo_caps(tenant=site)
    if not caps["allow_location_pages"]:
        return False
    mode = visibility.visibility_mode
    if mode == SiteVisibility.MODE_BASIC:
        return False
    country_norm = normalize_country(country)
    if not country_norm:
        return False
    if mode == SiteVisibility.MODE_EU:
        return True
    if mode == SiteVisibility.MODE_LOCATIONS:
        allowed_countries = set(get_allowed_countries(site))
        if country_norm not in allowed_countries:
            return False
        if city is None:
            return True
        city_norm = normalize_city(city)
        for entry in get_allowed_cities(site):
            if entry["country"] == country_norm and entry["city"] == city_norm:
                return True
        return False
    return False


def get_seo_target_cities(site):
    if not site:
        return []
    caps = get_seo_caps(tenant=site)
    is_local = caps["is_local"]
    is_country = caps["is_country"]
    is_eu = caps["is_eu"]
    if not caps["allow_location_pages"]:
        return []
    settings = TenantSEOSettings.objects.filter(tenant=site).first()
    if settings:
        if is_local and settings.active_city:
            return [
                {
                    "country": (settings.active_city.country_code or "").lower(),
                    "city": (settings.active_city.slug or "").lower(),
                }
            ]
        if is_country:
            focus = list(settings.focus_cities.all())
            if focus:
                target = [
                    {
                        "country": (city.country_code or "").lower(),
                        "city": (city.slug or "").lower(),
                    }
                    for city in focus
                ]
                max_cities = caps["max_cities"]
                if max_cities is not None:
                    target = target[:max_cities]
                return target
        if is_eu:
            focus = list(settings.focus_cities.all())
            if focus:
                target = [
                    {
                        "country": (city.country_code or "").lower(),
                        "city": (city.slug or "").lower(),
                    }
                    for city in focus
                ]
                max_cities = caps["max_cities"]
                if max_cities is not None:
                    target = target[:max_cities]
                return target
    target = get_allowed_cities(site)
    max_cities = caps["max_cities"]
    if max_cities is not None:
        target = target[:max_cities]
    return target


def get_country_name(country_code):
    code = normalize_country(country_code)
    for country in COUNTRIES:
        if normalize_country(country.get("code")) == code:
            return country.get("name") or code.upper()
    return code.upper() if code else ""
