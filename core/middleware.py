import logging
import os

from django.conf import settings
from django.utils.text import slugify

from core.services.site_settings import get_site_settings
from core.tenant import resolve_active_tenant, resolve_site_from_host

__path__ = [os.path.join(os.path.dirname(__file__), "middleware")]


class LaunchNoIndexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html"):
            settings_obj = get_site_settings()
            if getattr(settings, "SEO_NOINDEX", False) or settings_obj.launch_noindex:
                response["X-Robots-Tag"] = "noindex, nofollow"
        return response


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        existing_tenant = getattr(request, "tenant", None)
        if existing_tenant is not None:
            return self.get_response(request)
        tenant = resolve_active_tenant(request)
        if not tenant:
            site = getattr(request, "site", None)
            if site and not site.is_main:
                tenant = site
        request.tenant = tenant
        return self.get_response(request)


class SiteResolverMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        request.site = resolve_site_from_host(host)
        request.is_main_site = bool(request.site and request.site.is_main)
        response = self.get_response(request)
        site_label = "-"
        if getattr(request, "site", None):
            site_label = (
                getattr(request.site, "slug", None)
                or slugify(request.site.name)
                or str(request.site.id)
            )
        response["X-JCW-Host"] = host
        response["X-JCW-Site"] = site_label
        response["X-JCW-Mode"] = "main" if request.is_main_site else "tenant"
        if settings.DEBUG:
            logger = logging.getLogger(__name__)
            logger.debug("Host %s resolved to site=%s mode=%s", host, site_label, response["X-JCW-Mode"])
        return response
