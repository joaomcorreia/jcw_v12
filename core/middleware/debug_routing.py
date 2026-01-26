from django.urls import get_urlconf, resolve
from django.urls.exceptions import Resolver404


class DebugRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        normalized_host = (host or "").split(":", 1)[0].lower().strip()
        tenant = getattr(request, "tenant", None)
        urlconf = getattr(request, "urlconf", None)
        active_urlconf = get_urlconf()
        print(
            "[routing] host=%s http_host=%s normalized=%s path=%s path_info=%s urlconf=%s active_urlconf=%s tenant=%s"
            % (
                host,
                request.META.get("HTTP_HOST"),
                normalized_host,
                request.path,
                request.path_info,
                urlconf,
                active_urlconf,
                getattr(tenant, "id", None) or tenant,
            )
        )
        try:
            match = resolve(request.path_info)
            print(
                "[routing] resolved view=%s func=%s route=%s"
                % (
                    match.view_name,
                    getattr(match.func, "__name__", str(match.func)),
                    getattr(match, "route", ""),
                )
            )
        except Resolver404 as exc:
            print("[routing] resolve error: %s" % exc)

        response = self.get_response(request)
        response["X-Debug-Routing"] = "1"
        response["X-Debug-Host"] = normalized_host
        return response
