"""
Tenant Resolution Utilities

Provides functions for resolving which Site a request belongs to.
Used by middleware and views to determine content context.

ROUTING INVARIANTS:
- Exactly one Site has is_main=True (enforced by unique DB constraint)
- All tenant Sites MUST have subdomain field set
- Tenant resolution uses Site.subdomain field ONLY (never Site.name)
- Main site requests return None from resolve_active_site()
"""
import logging

from django.conf import settings

from core.models import Site

logger = logging.getLogger(__name__)


def resolve_active_tenant(request):
    """
    Resolve tenant for authenticated user context (dashboard, impersonation).

    Returns the user's owned tenant Site, or impersonated tenant if set.
    Used for dashboard context, NOT for public page routing.
    """
    impersonate_id = request.session.get("impersonate_tenant_id")
    user = getattr(request, "user", None)
    if impersonate_id and user and user.is_authenticated and (user.is_staff or user.is_superuser):
        return Site.objects.filter(id=impersonate_id, is_main=False).first()

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        sites = Site.objects.filter(owner=user, is_main=False).order_by("-created_at")
        if sites.exists():
            return sites.first()

    return None


def _strip_port(host):
    """Strip port from host string and normalize to lowercase."""
    return (host or "").split(":", 1)[0].lower()


def _split_host_port(host):
    host = host or ""
    if host.count(":") == 1:
        hostname, port = host.split(":", 1)
        return hostname, port
    return host, ""


def _normalize_path(path):
    if not path:
        return "/"
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def main_site_url(path="/", request=None, scheme=None):
    """
    Build an absolute URL to the main site using MAIN_DOMAIN.

    Keeps the current request port when available to preserve dev host behavior.
    """
    main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
    path = _normalize_path(path)
    if scheme is None:
        scheme = request.scheme if request else "http"
    port = ""
    if request:
        _host, port = _split_host_port(request.get_host())
    netloc = f"{main_domain}:{port}" if port else main_domain
    return f"{scheme}://{netloc}{path}"


def tenant_site_url(tenant, path="/", request=None, scheme=None):
    """
    Build an absolute URL to a tenant site based on its subdomain.

    Raises ValueError when the tenant or subdomain is missing to prevent
    generating invalid links (e.g., none.justcodeworks.local).
    """
    if not tenant:
        raise ValueError("Tenant is required to build tenant URLs.")
    subdomain = (getattr(tenant, "subdomain", None) or "").strip().lower()
    if not subdomain or subdomain == "none":
        raise ValueError("Tenant subdomain is missing.")
    main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
    path = _normalize_path(path)
    if scheme is None:
        scheme = request.scheme if request else "http"
    port = ""
    if request:
        _host, port = _split_host_port(request.get_host())
    netloc = f"{subdomain}.{main_domain}"
    if port:
        netloc = f"{netloc}:{port}"
    return f"{scheme}://{netloc}{path}"


def _resolve_main_site():
    """
    Resolve the main site (is_main=True).

    There must be exactly one Site with is_main=True.
    Returns None if no main site exists (data integrity issue).
    """
    return Site.objects.filter(is_main=True).first()


def resolve_site_from_host(host):
    """
    Resolve Site from request host.

    Used by SiteResolverMiddleware to set request.site.
    Only uses Site.subdomain for tenant matching (no slugify fallback).
    """
    host = _strip_port(host)
    if not host:
        return None

    main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
    main_hosts = {"127.0.0.1", "localhost", main_domain}

    # Main site: exact match or localhost
    if host in main_hosts or host == f"www.{main_domain}":
        site = _resolve_main_site()
        if site:
            logger.debug("Resolved main host=%s -> %s", host, site.id)
        return site

    # Tenant site: subdomain of main domain
    suffix = f".{main_domain}"
    if host.endswith(suffix):
        subdomain = host[: -len(suffix)]
        # Reserved subdomains resolve to main site
        if subdomain in {"", "www"}:
            site = _resolve_main_site()
            if site:
                logger.debug("Resolved main subdomain=%s -> %s", subdomain, site.id)
            return site
        # Look up tenant by subdomain field
        match = Site.objects.filter(subdomain__iexact=subdomain, is_main=False).first()
        if match:
            logger.debug("Resolved tenant subdomain=%s -> %s", subdomain, match.id)
            return match

    return None


def resolve_active_site(request):
    """
    Resolve Site for content rendering.

    Returns the tenant Site for tenant requests, or None for main site.
    Main site uses different templates, so we return None to trigger main site rendering.
    """
    host = (request.get_host() or "").split(":", 1)[0].lower()
    main_domain = getattr(settings, "MAIN_DOMAIN", "justcodeworks.local").lower()
    main_hosts = {"127.0.0.1", "localhost", "justcodeworks.local", main_domain}
    if host in main_hosts or host == f"www.{main_domain}":
        return None

    site = getattr(request, "site", None)
    if site:
        # Don't return main site - main site uses different templates (core/home.html)
        if site.is_main:
            return None
        impersonate_id = request.session.get("impersonate_tenant_id")
        user = getattr(request, "user", None)
        if impersonate_id and user and user.is_authenticated and (user.is_staff or user.is_superuser):
            impersonated = Site.objects.filter(id=impersonate_id, is_main=False).first()
            if impersonated:
                return impersonated
        return site

    return None


def get_active_tenant(request):
    """Alias for resolve_active_tenant for backwards compatibility."""
    return resolve_active_tenant(request)


def get_public_tenant(request):
    """
    Get tenant for public page context.

    Allows staff users to preview tenant sites via ?tenant=ID parameter.
    """
    tenant = resolve_active_tenant(request)
    if tenant:
        return tenant

    user = getattr(request, "user", None)
    tenant_id = request.GET.get("tenant")
    if tenant_id and user and user.is_staff:
        return Site.objects.filter(id=tenant_id).first()

    return None
