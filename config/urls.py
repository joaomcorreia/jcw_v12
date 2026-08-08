"""
Main Site URL Configuration

This URLConf is used for the MAIN site only: justcodeworks.local
Selected by TenantRoutingMiddleware when host matches MAIN_DOMAIN.

ROUTING STRUCTURE:
- Main site (this file): justcodeworks.local â†’ config.urls
- Tenant sites: {tenant}.justcodeworks.local â†’ config.tenants.urls

WHAT'S AVAILABLE HERE (main site only):
- /admin/ - Django admin
- /control-panel/ - Site operator control panel (NOT for tenants)
- /en/, /nl/, etc. - Main site public pages (core.urls)
- /accounts/ - Authentication

WHAT'S NOT HERE:
- /dashboard/ - Only available on tenant subdomains (see config/tenants/urls.py)
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from core import views as core_views
from core import views_pay as pay_views

urlpatterns = [
    # Admin tools (custom) - keep this before Django admin catch-all.
    path("admin/tools/<slug:slug>/", RedirectView.as_view(pattern_name="control_panel:tool", permanent=False, query_string=True), name="admin_tool"),
    # Django admin
    path('admin/', admin.site.urls),
    path('admin-panel/', RedirectView.as_view(pattern_name='control_panel:home', permanent=False)),
    # Authentication
    path('signup/', core_views.signup_view, name='signup'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('core.urls_accounts')),
    # Onboarding foundation routes (non-prefixed aliases)
    path("onboarding/", core_views.onboarding, name="onboarding_root"),
    path("dashboard/website/preview/", core_views.website_preview, name="website_preview_root"),
    # SEO
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('sitemap.xml', core_views.sitemap_xml, name='sitemap_xml'),
    path('sitemap-<str:lang>.xml', core_views.sitemap_language_xml, name='sitemap_language'),
    # Public payments
    path("pay/", pay_views.pay_invoice, name="pay_invoice"),
    path("pay/success/", pay_views.pay_success, name="pay_success"),
    path("pay/cancel/", pay_views.pay_cancel, name="pay_cancel"),
    path("stripe/webhook/", pay_views.stripe_webhook, name="stripe_webhook"),
    # i18n
    path('i18n/setlang/', core_views.language_switch, name='set_language'),
]

urlpatterns += i18n_patterns(
    path("i18n/setlang/", core_views.language_switch, name="set_language"),
    # Control panel - MAIN SITE ONLY (operators managing tenants)
    # Must come BEFORE core.urls because core.urls has a catch-all <slug:slug>/ pattern
    path('control-panel/', include(('controlpanel.urls', 'controlpanel'), namespace='control_panel')),
    # Auth (i18n-prefixed)
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('core.urls_accounts')),
    path('signup/', core_views.signup_view, name='signup'),
    # Main site public pages (NO dashboard routes)
    path('', include('core.urls')),
)

# The unprefixed root is the only URL that performs language detection.
urlpatterns.insert(0, path('', core_views.language_root, name='language_root'))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
