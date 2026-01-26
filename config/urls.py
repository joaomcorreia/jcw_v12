"""
Main Site URL Configuration

This URLConf is used for the MAIN site only: justcodeworks.local
Selected by TenantRoutingMiddleware when host matches MAIN_DOMAIN.

ROUTING STRUCTURE:
- Main site (this file): justcodeworks.local → config.urls
- Tenant sites: {tenant}.justcodeworks.local → config.tenants.urls

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
from django.views.i18n import set_language

from core import views as core_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    path('admin-panel/', RedirectView.as_view(pattern_name='control_panel:home', permanent=False)),
    # Authentication
    path('signup/', core_views.signup_view, name='signup'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('core.urls_accounts')),
    # SEO
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('sitemap.xml', core_views.sitemap_xml, name='sitemap_xml'),
    path('sitemap-<str:lang>.xml', core_views.sitemap_language_xml, name='sitemap_language'),
    # i18n
    path('i18n/setlang/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
