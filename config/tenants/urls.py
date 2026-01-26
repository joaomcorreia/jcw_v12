"""
Tenant URL Configuration

This URLConf is used for all tenant subdomains: {tenant}.justcodeworks.local
Selected by TenantRoutingMiddleware when host matches a tenant subdomain.

ROUTING INVARIANTS:
- Exactly one Site has is_main=True (enforced by DB constraint)
- All tenant Sites must have subdomain field set
- Tenant resolution uses Site.subdomain field only (never Site.name)
- Main site (justcodeworks.local) uses config.urls, NOT this file
- /dashboard/ routes are tenant-only (defined here)
- /control-panel/ routes are main-site-only (NOT available to tenants)
"""
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    # SEO (tenant subdomains)
    path("robots.txt", core_views.tenant_robots_txt, name="tenant_robots_txt"),
    path("sitemap.xml", core_views.tenant_sitemap_xml, name="tenant_sitemap_xml"),
    path(
        "sitemap-<str:lang>.xml",
        core_views.tenant_sitemap_language_xml,
        name="tenant_sitemap_language",
    ),
    path("signup/", core_views.signup_view, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("core.urls_accounts")),
]

urlpatterns += i18n_patterns(
    # Non-namespaced aliases for legacy reverse("dashboard") / reverse("signup")
    path("dashboard/", core_views.dashboard, name="dashboard"),
    path("signup/", core_views.signup_view, name="signup"),
    # Auth (i18n-prefixed)
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("core.urls_accounts")),
    # Tenant dashboard - only available on tenant subdomains
    path("dashboard/", include(("core.urls_dashboard", "dashboard"), namespace="tenant_dashboard")),
    # Tenant public pages (home, locations, slug pages)
    path("", include("core.urls_tenant")),
)
