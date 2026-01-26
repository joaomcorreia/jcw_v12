from django.conf import settings
from django.utils.text import slugify

from core.seo_caps import get_seo_caps
from core.seo_utils import is_public_path


class DebugRouteHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only in DEBUG; keep safe in production
        try:
            if not settings.DEBUG:
                return response

            host = (request.get_host() or "").split(":", 1)[0].lower().strip()
            site = getattr(request, "site", None) or getattr(request, "tenant", None)
            site_label = ""
            if site:
                site_label = (
                    getattr(site, "subdomain", None)
                    or getattr(site, "slug", None)
                    or slugify(site.name)
                    or str(site.id)
                )

            header_mode = (request.META.get("HTTP_X_JCW_MODE") or "").strip().lower()
            header_site = (request.META.get("HTTP_X_JCW_SITE") or "").strip().lower()
            is_main = bool(getattr(request, "is_main_site", False))
            is_main = is_main or header_mode == "main" or header_site == "main-site"

            caps = get_seo_caps(request=request, tenant=getattr(request, "tenant", None))

            if getattr(request, "resolver_match", None):
                rm = request.resolver_match
                response["X-JCW-ViewName"] = rm.view_name or ""
                response["X-JCW-ViewFunc"] = f"{rm.func.__module__}.{rm.func.__name__}"
            response["X-JCW-URLConf"] = str(getattr(request, "urlconf", ""))
            response["X-JCW-Path"] = request.path
            response["X-JCW-Host"] = host
            response["X-JCW-Mode"] = "main" if is_main else "tenant"
            response["X-JCW-Site"] = site_label
            response["X-JCW-SEO-Level"] = caps.get("seo_level", caps.get("tier", "local"))
            response["X-JCW-SEO-Indexing"] = caps.get("indexing_scope", caps.get("tier", "local"))
            response["X-JCW-SEO-Forced"] = "1" if caps.get("forced") else "0"
        except Exception:
            pass
        return response


class IframePreviewHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        allow_preview = bool(getattr(settings, "JCW_ALLOW_IFRAME_PREVIEW", False))
        if not settings.DEBUG and not allow_preview:
            return response
        if not getattr(request, "is_main_site", False):
            return response
        if not is_public_path(request.path):
            return response
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response
