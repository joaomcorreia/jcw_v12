from django.urls import reverse
from django.utils.translation import gettext as _

from core.services.features import resolve_active_plan

PLAN_NAMES = {
    "starter": "Starter",
    "growth": "Growth",
    "pro": "Pro",
}


def get_plan_name_for_request(request):
    plan = resolve_active_plan()
    if plan and plan.key in PLAN_NAMES:
        return PLAN_NAMES[plan.key]
    return "Starter"


def get_feature_flags(plan_name):
    plan = plan_name or "Starter"
    if plan == "Pro":
        return {
            "can_use_blog": True,
            "can_use_custom_pages": True,
            "can_use_seo_widgets": True,
            "can_use_indexing_widget": True,
            "can_use_activity_feed": True,
            "can_use_print_studio": True,
            "can_use_multilang_controls": True,
            "can_use_advanced_seo": True,
        }
    if plan == "Growth":
        return {
            "can_use_blog": True,
            "can_use_custom_pages": True,
            "can_use_seo_widgets": True,
            "can_use_indexing_widget": True,
            "can_use_activity_feed": True,
            "can_use_print_studio": True,
            "can_use_multilang_controls": True,
            "can_use_advanced_seo": False,
        }
    return {
        "can_use_blog": False,
        "can_use_custom_pages": False,
        "can_use_seo_widgets": False,
        "can_use_indexing_widget": False,
        "can_use_activity_feed": True,
        "can_use_print_studio": True,
        "can_use_multilang_controls": False,
        "can_use_advanced_seo": False,
    }


def build_upgrade_cta(feature_key, plan_name, lang=None):
    titles = {
        "seo": _("Unlock SEO insights"),
        "indexing": _("Unlock indexing insights"),
        "blog": _("Unlock the blog"),
        "custom_pages": _("Unlock custom pages"),
        "print_studio": _("Unlock Print Studio"),
    }
    messages = {
        "seo": _("Upgrade to see SEO progress and recommendations."),
        "indexing": _("Upgrade to monitor indexing status."),
        "blog": _("Upgrade to create and publish blog posts."),
        "custom_pages": _("Upgrade to create custom pages."),
        "print_studio": _("Upgrade to access Print Studio tools."),
    }
    return {
        "title": titles.get(feature_key, _("Upgrade your plan")),
        "message": messages.get(feature_key, _("Upgrade to access this feature.")),
        "primary_button_text": _("See upgrades"),
        "primary_button_url": reverse("core:dashboard_billing"),
        "secondary_link_text": _("Contact support"),
        "secondary_link_url": reverse("core:services"),
        "style": "dashboard-upgrade-cta--compact",
    }
