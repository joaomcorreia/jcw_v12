"""
Tenant Routing Middleware

Determines which URLConf to use based on the request host:
- Main site (justcodeworks.local): uses config.urls
- Tenant subdomains ({tenant}.justcodeworks.local): uses config.tenants.urls

ROUTING INVARIANTS:
- Exactly one Site has is_main=True (enforced by unique DB constraint)
- All tenant Sites MUST have subdomain field set
- Tenant resolution uses Site.subdomain field ONLY (never Site.name or slugify)
- Main site requests bypass tenant template selection entirely
- Unknown hosts fall back to main site URLConf
"""
from django.conf import settings
from django.urls import set_urlconf

from core.models import Site


def _normalize_host(host):
    """Strip port and normalize host to lowercase."""
    return (host or "").split(":", 1)[0].lower().strip()


def _resolve_tenant_by_subdomain(subdomain):
    """
    Resolve a tenant Site by subdomain.

    Only uses the Site.subdomain field for matching.
    Returns None if no matching tenant is found.
    """
    if not subdomain:
        return None
    return Site.objects.filter(subdomain__iexact=subdomain, is_main=False).first()


class TenantRoutingMiddleware:
    """
    Middleware that routes requests to the appropriate URLConf.

    Must be first in MIDDLEWARE stack to set request.urlconf before
    any URL resolution occurs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
        raw_host = request.get_host()
        host = (raw_host or "").split(":", 1)[0].lower().strip()

        # Main site: exact match on MAIN_DOMAIN or local dev hosts
        main_hosts = {
            main_domain,
            "localhost",
            "127.0.0.1",
            "justcodeworks.local",
        }
        if host in main_hosts:
            request.tenant = None
            request.urlconf = "config.urls"
            set_urlconf("config.urls")
            return self.get_response(request)

        # Tenant site: subdomain of MAIN_DOMAIN
        suffix = f".{main_domain}"
        if host.endswith(suffix):
            subdomain = host[: -len(suffix)].strip(".")
            tenant = _resolve_tenant_by_subdomain(subdomain)
            if tenant:
                request.tenant = tenant
                request.urlconf = "config.tenants.urls"
                set_urlconf("config.tenants.urls")
                return self.get_response(request)

        # Fallback: unknown host uses main site URLConf
        request.tenant = None
        request.urlconf = "config.urls"
        set_urlconf("config.urls")
        return self.get_response(request)
