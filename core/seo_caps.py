import logging

from django.conf import settings

from core.models import PlanSEOSettings


DEFAULT_CAPS = {
    "tier": "local",
    "max_cities": 1,
    "schema_level": "basic",
    "sitemap_cap": 200,
    "multilingual_meta": "basic",
    "allow_location_pages": True,
    "allow_service_location_pages": False,
    "allow_city_switching": True,
    "allow_country_visibility": False,
    "allow_eu_visibility": False,
    "allow_custom_canonical": False,
    "allow_hreflang": True,
    "allow_indexing": True,
    "forced": False,
}


def _forced_caps():
    return _finalize_caps(
        {
        "tier": "eu",
        "max_cities": 9999,
        "schema_level": "full",
        "sitemap_cap": 5000,
        "multilingual_meta": "full",
        "allow_location_pages": True,
        "allow_service_location_pages": True,
        "allow_city_switching": True,
        "allow_country_visibility": True,
        "allow_eu_visibility": True,
        "allow_custom_canonical": True,
        "allow_hreflang": True,
        "allow_indexing": True,
        "forced": True,
        }
    )


def _normalize_host(host):
    return (host or "").split(":", 1)[0].lower().strip()


def _is_main_request(request):
    if not request:
        return False
    mode = (request.META.get("HTTP_X_JCW_MODE") or "").strip().lower()
    site_flag = (request.META.get("HTTP_X_JCW_SITE") or "").strip().lower()
    return mode == "main" or site_flag == "main-site"


def _log_forced_caps(reason):
    if settings.DEBUG:
        logging.getLogger(__name__).debug("SEO caps forced to EU for main site (%s).", reason)


def _caps_from_settings(seo_settings):
    if not seo_settings:
        return _finalize_caps(dict(DEFAULT_CAPS))
    return _finalize_caps(
        {
        "tier": seo_settings.seo_tier,
        "max_cities": seo_settings.max_cities,
        "schema_level": seo_settings.schema_level,
        "sitemap_cap": seo_settings.sitemap_url_cap,
        "multilingual_meta": seo_settings.multilingual_meta_level,
        "allow_location_pages": seo_settings.allow_location_pages,
        "allow_service_location_pages": seo_settings.allow_service_location_pages,
        "allow_city_switching": seo_settings.allow_city_switching,
        "allow_country_visibility": seo_settings.allow_country_visibility,
        "allow_eu_visibility": seo_settings.allow_eu_visibility,
        "allow_custom_canonical": seo_settings.allow_custom_canonical,
        "allow_hreflang": seo_settings.allow_hreflang,
        "allow_indexing": seo_settings.allow_indexing,
        "forced": False,
        }
    )


def _clamp_tier(caps):
    tier = caps["tier"]
    if tier == "eu" and not caps["allow_eu_visibility"]:
        return "country" if caps["allow_country_visibility"] else "local"
    if tier == "country" and not caps["allow_country_visibility"]:
        return "local"
    return tier


def _finalize_caps(caps):
    caps = dict(caps)
    caps["tier"] = _clamp_tier(caps)
    if caps["tier"] == "local":
        caps["max_cities"] = 1
        caps["allow_country_visibility"] = False
        caps["allow_eu_visibility"] = False
        caps["allow_city_switching"] = False
    caps["seo_level"] = caps["tier"]
    caps["allow_country_targeting"] = caps["allow_country_visibility"]
    caps["allow_eu_targeting"] = caps["allow_eu_visibility"]
    caps["allow_city_change"] = caps["allow_city_switching"]
    caps["indexing_scope"] = caps["tier"]
    caps["is_local"] = caps["tier"] == "local"
    caps["is_country"] = caps["tier"] == "country"
    caps["is_eu"] = caps["tier"] == "eu"
    return caps


def get_seo_caps(request=None, tenant=None):
    """Return normalized SEO plan caps for all SEO enforcement.

    Main site always receives maximum (EU) caps; tenants use plan settings.
    """
    host = None
    if request is not None:
        host = _normalize_host(request.get_host())
    main_domain = _normalize_host(getattr(settings, "MAIN_DOMAIN", ""))

    if host and main_domain and host == main_domain:
        _log_forced_caps("host")
        return _forced_caps()

    if tenant is None and request is not None:
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            site = getattr(request, "site", None)
            if site and not getattr(site, "is_main", False):
                tenant = site

    if tenant is not None and getattr(tenant, "is_main", False):
        _log_forced_caps("site.is_main")
        return _forced_caps()

    if _is_main_request(request):
        _log_forced_caps("header")
        return _forced_caps()

    if tenant is None:
        return _finalize_caps(dict(DEFAULT_CAPS))

    plan = getattr(tenant, "plan", None)
    if not plan:
        return _finalize_caps(dict(DEFAULT_CAPS))

    seo_settings = PlanSEOSettings.objects.filter(plan=plan).first()
    if not seo_settings:
        return _finalize_caps(dict(DEFAULT_CAPS))

    return _caps_from_settings(seo_settings)
