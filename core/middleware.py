from core.services.site_settings import get_site_settings
from core.tenant import get_active_tenant


class LaunchNoIndexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html"):
            settings = get_site_settings()
            if settings.launch_noindex:
                response["X-Robots-Tag"] = "noindex, nofollow"
        return response


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = get_active_tenant(request)
        return self.get_response(request)
