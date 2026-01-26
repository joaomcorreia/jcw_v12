from django.conf import settings

from core.models import Plan, PlanSEOSettings, SiteVisibility
from core.seo_caps import get_seo_caps

SEO_TIER_LOCAL = "local"
SEO_TIER_COUNTRY = "country"
SEO_TIER_EU = "eu"


def get_seo_tier(plan_key):
    if not plan_key:
        return SEO_TIER_LOCAL
    plan = Plan.objects.filter(key=plan_key).first()
    if plan:
        settings_obj = PlanSEOSettings.objects.filter(plan=plan).first()
        if settings_obj:
            return settings_obj.seo_tier
    return SEO_TIER_LOCAL


def plan_seo_to_visibility_mode(plan_seo_level):
    if plan_seo_level in {SEO_TIER_LOCAL, SEO_TIER_COUNTRY, SEO_TIER_EU}:
        seo_tier = plan_seo_level
    else:
        seo_tier = get_seo_tier(plan_seo_level)
    if seo_tier == SEO_TIER_EU:
        return SiteVisibility.MODE_EU
    return SiteVisibility.MODE_LOCATIONS


def get_visibility_limits(site):
    caps = get_seo_caps(tenant=site)
    tier = caps["tier"]
    if tier == SEO_TIER_EU:
        return {"max_countries": None, "max_cities": caps["max_cities"]}
    return {"max_countries": 1, "max_cities": caps["max_cities"]}


def sync_visibility_from_plan(site, *, force=False):
    caps = get_seo_caps(tenant=site)
    seo_tier = caps["tier"]
    visibility_mode = plan_seo_to_visibility_mode(seo_tier)
    visibility, created = SiteVisibility.objects.get_or_create(
        site=site,
        defaults={
            "seo_level": seo_tier,
            "visibility_mode": visibility_mode,
            "allowed_countries": [],
            "allowed_cities": [],
            "is_manual_override": False,
        },
    )
    if created:
        return visibility

    if force or not visibility.is_manual_override:
        visibility.seo_level = seo_tier
        visibility.visibility_mode = visibility_mode
        visibility.is_manual_override = False
        visibility._from_sync = True
        visibility.save(update_fields=["seo_level", "visibility_mode", "is_manual_override", "last_updated"])
    return visibility


def _get_visibility_mode(site):
    visibility = getattr(site, "visibility", None)
    visibility_mode = getattr(visibility, "visibility_mode", None)
    if visibility_mode:
        return visibility_mode
    caps = get_seo_caps(tenant=site)
    return plan_seo_to_visibility_mode(caps["tier"])


def is_slug_indexable(site, slug):
    caps = get_seo_caps(tenant=site)
    if not caps.get("allow_indexing", True):
        return False
    visibility_mode = _get_visibility_mode(site)
    if visibility_mode != "basic":
        return True
    allowed = getattr(settings, "BASIC_INDEXABLE_SLUGS", [])
    return slug in allowed


def is_page_indexable(site, page):
    if not page or not site:
        return False
    caps = get_seo_caps(tenant=site)
    if not caps.get("allow_indexing", True):
        return False
    if not page.is_active:
        return False
    if page.noindex:
        return False
    visibility_mode = _get_visibility_mode(site)
    if visibility_mode == "basic":
        allowed = getattr(settings, "BASIC_INDEXABLE_SLUGS", [])
        return page.slug in allowed
    return True
