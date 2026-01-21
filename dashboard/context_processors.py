from django.utils.translation import gettext as _

from dashboard.plan_features import build_upgrade_cta, get_feature_flags, get_plan_name_for_request


def dashboard_plan_flags(request):
    plan_name = get_plan_name_for_request(request)
    feature_flags = get_feature_flags(plan_name)
    upgrade_ctas = {
        "seo": build_upgrade_cta("seo", plan_name),
        "indexing": build_upgrade_cta("indexing", plan_name),
        "blog": build_upgrade_cta("blog", plan_name),
        "custom_pages": build_upgrade_cta("custom_pages", plan_name),
        "print_studio": build_upgrade_cta("print_studio", plan_name),
    }

    widget_demo = {
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

    return {
        "current_plan_name": plan_name,
        "feature_flags": feature_flags,
        "upgrade_ctas": upgrade_ctas,
        **widget_demo,
    }
