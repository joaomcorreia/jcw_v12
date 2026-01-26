# Routing Audit

## 1) Current Architecture Overview
- Multi-tenant routing is host-based via `core/tenant_routing.TenantRoutingMiddleware`.
- Main site uses `config.urls` (marketing pages, control panel, admin).
- Tenant sites use `config.tenants.urls` (tenant dashboard + tenant public pages).
- LocaleMiddleware is enabled, and `i18n_patterns` is used in both main and tenant URLConfs.

## 2) URLConf Map (include trees)

### `config/urls.py` (main site)
- Non-i18n:
  - `/admin/`
  - `/admin-panel/` -> control panel redirect
  - `/signup/`
  - `/accounts/` (auth + accounts)
  - `/robots.txt`, `/sitemap.xml`, `/sitemap-<lang>.xml`
  - `/i18n/setlang/`
- i18n:
  - `/control-panel/` -> `controlpanel.urls`
  - `/` -> `core.urls`

### `config/tenants/urls.py` (tenant sites)
- Non-i18n:
  - `/robots.txt`, `/sitemap.xml`, `/sitemap-<lang>.xml`
  - `/signup/`
  - `/accounts/` (auth + accounts)
- i18n:
  - `/dashboard/` -> `core.urls_dashboard` (namespace `tenant_dashboard`)
  - `/` -> `core.urls_tenant`

### `core/urls.py` (main public)
- `/` -> `core.views.home`
- `/websites/`, `/services/`, `/help-center/`, `/blog/`, `/blog/<slug>/`
- `/products/*`, `/print-lab/*`, `/printlab/*`, `/billing/*`
- `/locations/*` (location pages)
- `/<slug>/` catch-all -> `core.views.public_page`

### `core/urls_tenant.py` (tenant public)
- `/` -> `core.views.home`
- `/locations/*`
- `/<slug>/` catch-all -> `core.views.public_page`

### `core/urls_dashboard.py` (tenant dashboard)
- `/` -> `core.views.dashboard`
- `/frontend/*` (pages, menu, visibility, blog)
- `/billing/`, `/print-studio/`
- `/main-site/pages/` (staff-only)

### `controlpanel/urls.py` (main control panel)
- `/control-panel/*` (plans, tenants, templates, users)

### `controlpanel/ops_urls.py` (ops/legacy)
- `/ops/*`

## 3) Host Map (host -> urlconf -> home behavior)
| Host | URLConf | `core.views.home` behavior | Template | Content source |
| --- | --- | --- | --- | --- |
| `justcodeworks.local` | `config.urls` | Render marketing homepage | `templates/core/home.html` | DB sections if present + template defaults |
| `localhost` / `127.0.0.1` | `config.urls` | Render marketing homepage | `templates/core/home.html` | DB sections if present + template defaults |
| `{tenant}.justcodeworks.local` | `config.tenants.urls` | Redirect to `/\<lang\>/dashboard/` | redirect | tenant dashboard |

## 4) i18n Rules
- `LocaleMiddleware` is enabled and `i18n_patterns` is used in both main and tenant URLConfs.
- Language-prefixed routes:
  - Main: `/en/`, `/nl/`, etc for public pages and control panel.
  - Tenants: `/en/`, `/nl/`, etc for dashboard and tenant public pages.
- Non-prefixed routes:
  - `/admin/`, `/robots.txt`, `/sitemap.xml`, `/accounts/` and other non-i18n routes.
- Redirects that can drop prefixes:
  - `core.views.home` previously used `"/dashboard/"`, now uses language-aware redirect.
  - Other redirects should be audited if they use hardcoded paths.

## 5) Problems Found
- `core.views.home` uses host-based branching instead of request.urlconf; tenant home always redirects to dashboard even though tenant public pages exist in `core/urls_tenant.py`.
- Catch-all `/<slug>/` exists in both main and tenant URLConfs; order matters and must remain last.
- Main marketing homepage content is mixed: `templates/core/home.html` includes hardcoded copy with DB fallbacks; this conflicts with “DB-only content” goals.

## 6) Proposed Fix Plan
### Step 1 (implemented)
- Ensure tenant redirect is language-aware: redirect to `/\<lang\>/dashboard/` using `build_language_url_for_path`.
- Keep host-based routing stable; avoid major refactors.

### Step 2
- Decide desired tenant public home behavior: render DB page or keep redirect.
- If render: use `core/urls_tenant.py` home to render `templates/site/page.html` with `Page(slug="home")`.

### Step 3
- Consolidate host detection to reuse middleware-resolved `request.site` where possible.
- Remove hardcoded copy from `templates/core/home.html` if DB-only policy is enforced.

