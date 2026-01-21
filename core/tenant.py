from core.models import Site


def get_active_tenant(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None

    impersonate_id = request.session.get("impersonate_tenant_id")
    if user.is_staff and impersonate_id:
        return Site.objects.filter(id=impersonate_id).first()

    sites = Site.objects.filter(owner=user)
    if sites.count() == 1:
        return sites.first()

    return None


def get_public_tenant(request):
    user = getattr(request, "user", None)
    impersonate_id = request.session.get("impersonate_tenant_id")
    if user and user.is_staff and impersonate_id:
        return Site.objects.filter(id=impersonate_id).first()
    if user and user.is_authenticated:
        sites = Site.objects.filter(owner=user)
        if sites.count() == 1:
            return sites.first()
        if sites.exists():
            return sites.order_by("-created_at").first()

    tenant_id = request.GET.get("tenant")
    if tenant_id and user and user.is_staff:
        return Site.objects.filter(id=tenant_id).first()

    return None
