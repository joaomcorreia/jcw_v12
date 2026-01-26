from core.tenant import resolve_active_site as tenant_resolve_active_site


def resolve_active_site(request):
    return tenant_resolve_active_site(request)
