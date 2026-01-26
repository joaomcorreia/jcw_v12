# JCW Routing Contract

## Tenant home bootstrap
- Tenant home uses `core.views.tenant_home` wired in `core/urls_tenant.py`.
- If `Page(slug="home")` is missing for a tenant, a minimal Page + hero SectionContent is created on first request.
- Content remains editable in the dashboard; no placeholder template copy is used for tenant home.
