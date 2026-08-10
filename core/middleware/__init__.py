import logging

from django.conf import settings
from django.utils.text import slugify

from core.models import Site
from core.tenant import resolve_site_from_host
from core.seo_utils import is_indexable_public_request


class LaunchNoIndexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html"):
            if getattr(settings, "SEO_NOINDEX", False) or not is_indexable_public_request(request):

                response["X-Robots-Tag"] = "noindex, nofollow"
        return response


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_site = getattr(request, "site", None)
        tenant = None
        if host_site and not host_site.is_main:
            tenant = host_site
            impersonate_id = request.session.get("impersonate_tenant_id")
            user = getattr(request, "user", None)
            if impersonate_id and user and user.is_authenticated and (user.is_staff or user.is_superuser):
                impersonated = Site.objects.filter(id=impersonate_id, is_main=False).first()
                if impersonated:
                    tenant = impersonated
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
        if settings.DEBUG:
            site_label = "-"
            if getattr(request, "site", None):
                site_label = (
                    getattr(request.site, "slug", None)
                    or slugify(request.site.name)
                    or str(request.site.id)
                )
            mode_label = "main" if request.is_main_site else "tenant"
            logger = logging.getLogger(__name__)
            logger.debug("Host %s resolved to site=%s mode=%s", host, site_label, mode_label)
        return response
