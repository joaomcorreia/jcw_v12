# Site Routing Map

## 1) Multi-tenant mechanism
- Custom host-based routing via `core/tenant_routing.TenantRoutingMiddleware`.
- Host determines URLConf:
  - Main host (MAIN_DOMAIN / localhost) -> `config.urls`
  - Tenant subdomain `{tenant}.MAIN_DOMAIN` -> `config.tenants.urls`
- Site resolution uses `Site.subdomain` only; main site is `Site.is_main=True`.

## 2) Routing decision sources
- URLConf selection: `core/tenant_routing.TenantRoutingMiddleware`
- Site resolution (request.site, request.tenant):
  - `core.middleware.SiteResolverMiddleware`
  - `core.middleware.TenantMiddleware`
  - `core.tenant.resolve_site_from_host`, `core.tenant.resolve_active_site`

## 3) Mapping Table
| Domain/Host | URLConf | Home view | Template | Content source |
| --- | --- | --- | --- | --- |
| `justcodeworks.local` | `config.urls` | `core.views.home` | `templates/core/home.html` | DB (Page/SectionContent when present) + template defaults |
| `localhost` / `127.0.0.1` | `config.urls` | `core.views.home` | `templates/core/home.html` | DB (Page/SectionContent when present) + template defaults |
| `{tenant}.justcodeworks.local` | `config.tenants.urls` | `core.views.home` | redirect to `/dashboard/` | tenant dashboard (no public home) |

## 4) Template roots by site type
- Main site templates: `templates/core/`, `templates/pages/`
- Tenant public templates: `templates/site/`
- Tenant dashboard templates: `templates/dashboard/`
- Operator control panel: `templates/controlpanel/`

## 5) Verification notes
- Main site `/en/` resolves to `config.urls` and renders `core.views.home` with `templates/core/home.html`.
- Tenant site `/en/` resolves to `config.tenants.urls` and `core.views.home` redirects to `/dashboard/`.
