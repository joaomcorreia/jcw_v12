# Template State Report

## Overview
JCW uses multiple template systems split by site type: main marketing site, tenant public sites, tenant dashboard, operator control panel, and an ops mini-panel. Language prefixes are handled at the URLConf level (i18n patterns) with LocaleMiddleware enabled.

### Template Systems Map
| System name | Template root | URL namespace | Base template | Main views |
| --- | --- | --- | --- | --- |
| Main public site (marketing) | `templates/core/` + `templates/pages/` | `core` (main site only) | `templates/core/base.html` | `core.views.home`, `core.views.services`, `core.views.websites`, `core.views.pos_systems*`, `core.views.printlab*`, `core.views.blog_*`, `core.views.product_*`, `core.views.public_page` |
| Tenant public site | `templates/site/` | `core` (tenant urlconf) | `templates/site/base.html` | `core.views.home`, `core.views.location_*`, `core.views.public_page` via `core/urls_tenant.py` |
| Tenant dashboard | `templates/dashboard/` | `tenant_dashboard` | `templates/dashboard/base_dashboard.html` | `core.views.dashboard_*` via `core/urls_dashboard.py` |
| Control panel (operator) | `templates/controlpanel/` | `control_panel` | `templates/controlpanel/base_controlpanel.html` | `controlpanel.views.*` |
| Ops panel (legacy) | `templates/ops/` | `ops` | `templates/ops/base.html` | `controlpanel.views_ops.*` |
| Shared components | `templates/components/` | n/a | n/a | included from other templates |
| Legacy/import | `_import/templates/` | n/a | n/a | not referenced in URLConfs (not found) |

## Public Site Templates (JCW marketing)
### Wired templates (main site)
- Home: `templates/core/home.html` via `core.views.home` (`core/urls.py`)
- Products and services: `templates/core/services.html`, `templates/core/websites.html`, `templates/core/pos_systems*.html`, `templates/core/print_lab*.html`, `templates/core/printful*.html`
- Blog: `templates/core/blog_index.html`, `templates/core/blog_detail.html`
- Help center: `templates/core/help_center.html`
- Billing pages: `templates/core/billing*.html`
- Product-style pages: `templates/core/product_page.html` (used by many `product_*` views)
- Plan landing pages: `templates/pages/websites/*.html` (multi-page, SEO, catalog, etc.)
- Shared layout: `templates/core/base.html`, `templates/core/main_nav.html`, `templates/core/footer.html`

### Missing or placeholder
- `templates/dashboard/edit_home.html` has a "coming soon" placeholder (dashboard view).

## User/Dashboard Templates (customer control panel)
### Wired templates
- Dashboard shell: `templates/dashboard/base_dashboard.html`
- Main landing: `templates/dashboard/home.html`
- Pages list + edit forms: `templates/dashboard/pages.html`, `templates/dashboard/page_edit.html`, `templates/dashboard/page_edit_services.html`, `templates/dashboard/page_edit_contact.html`
- SEO UI: `templates/dashboard/page_seo.html`
- Visibility: `templates/dashboard/visibility.html`
- Navigation editor: `templates/dashboard/menu.html`
- Site settings: `templates/dashboard/site_settings.html`
- Blog UI: `templates/dashboard/blog.html`
- Billing UI: `templates/dashboard/billing.html`
- Template chooser: `templates/dashboard/choose_template.html`
- Home editor placeholder: `templates/dashboard/edit_home.html`

### Plan gating UI patterns
- Upgrade CTA components: `templates/components/upgrade_cta.html`
- Disabled controls and plan notes in `templates/dashboard/pages.html`, `templates/dashboard/page_seo.html`, `templates/dashboard/visibility.html`

## Site Types and Routing
- Main site uses `config/urls.py` with `i18n_patterns` and includes `core/urls.py` for public pages.
- Tenant sites use `config/tenants/urls.py` with `i18n_patterns` and include `core/urls_tenant.py` for public pages plus `core/urls_dashboard.py` for dashboard.
- LocaleMiddleware is enabled for language-prefixed URLs.

## Editing Readiness (current state)
### What exists now
- Simple form-based editing for page content and sections:
  - Page hero fields: `templates/dashboard/page_edit.html` with `dashboard/forms.py:HeroContentForm`
  - Services section editor: `templates/dashboard/page_edit_services.html`
  - Contact section editor: `templates/dashboard/page_edit_contact.html`
- SEO editing per page: `templates/dashboard/page_seo.html` with `dashboard/forms.py:PageSEOForm`
- Template selection for tenants: `templates/dashboard/choose_template.html`
- Operator template JSON editor: `templates/controlpanel/templates_form.html`
- Onboarding preview iframe: `templates/core/onboarding_step3.html`

### What is missing
- No live preview or iframe in dashboard editing flows (only "View page" links).
- No section selection or click-to-edit inside the rendered page (no postMessage or selection logic found).
- "Edit homepage" dashboard view is a placeholder (`templates/dashboard/edit_home.html`).
- No in-dashboard sidebar editor tied to page sections (only static marketing right sidebar).

## Evidence Snippets (key findings)
### Main vs tenant routing
`config/urls.py`:
```python
urlpatterns += i18n_patterns(
    path('control-panel/', include(('controlpanel.urls', 'controlpanel'), namespace='control_panel')),
    path('', include('core.urls')),
)
```

`config/tenants/urls.py`:
```python
urlpatterns += i18n_patterns(
    path("dashboard/", include(("core.urls_dashboard", "dashboard"), namespace="tenant_dashboard")),
    path("", include("core.urls_tenant")),
)
```

### Base templates
`templates/core/base.html`:
```html
<link rel="stylesheet" href="{% static 'jcw/all-styles.css' %}">
<title>{{ seo_title|default:"JustCodeWorks" }}</title>
<meta name="robots" content="{% if launch_noindex %}noindex, nofollow{% else %}{{ seo_robots|default:'index, follow' }}{% endif %}">
```

`templates/site/base.html`:
```html
<title>
  {% if seo_title %}{{ seo_title }}{% elif page_title %}{{ page_title }}{% else %}{% trans "Coming soon" %}{% endif %}
</title>
<meta name="robots" content="{% if page and page.noindex %}noindex, nofollow{% elif plan_blocks_indexing %}noindex, nofollow{% elif seo_robots %}{{ seo_robots }}{% else %}index, follow{% endif %}">
```

### Plan gating in dashboard
`templates/dashboard/pages.html`:
```html
{% if feature_flags.can_use_custom_pages %}
  <a class="dashboard-button" href="{% url 'tenant_dashboard:dashboard_pages_create' %}">{% trans "Create page" %}</a>
{% else %}
  <button class="dashboard-button" type="button" disabled>{% trans "Create page" %}</button>
{% endif %}
```

### Editing preview (onboarding only)
`templates/core/onboarding_step3.html`:
```html
<iframe title="Homepage preview" src="{{ preview_url }}" class="w-full" style="min-height: 720px; border: 0;"></iframe>
```

### Placeholder editor
`templates/dashboard/edit_home.html`:
```html
<h1 class="dashboard-title">{% trans "Edit homepage" %}</h1>
<p class="dashboard-muted">{% trans "This editor is coming soon." %}</p>
```

## Public Site Templates: Wired vs Missing
### Wired
- Marketing home and sections: `templates/core/home.html`
- Marketing pages: `templates/core/services.html`, `templates/core/websites.html`, `templates/core/pos_systems*.html`, `templates/core/print_lab*.html`
- Printful pages: `templates/core/printful*.html`
- Blog: `templates/core/blog_index.html`, `templates/core/blog_detail.html`
- Billing: `templates/core/billing*.html`
- Product page wrapper: `templates/core/product_page.html`
- Plans content: `templates/pages/websites/*.html`

### Missing or uncertain
- `_import/templates/*.html` (no URLConf references found)

## User/Dashboard Templates: Wired vs Missing
### Wired
- Pages and section editors: `templates/dashboard/page_edit*.html`
- SEO editor: `templates/dashboard/page_seo.html`
- Visibility UI: `templates/dashboard/visibility.html`
- Blog, billing, template chooser: `templates/dashboard/blog.html`, `templates/dashboard/billing.html`, `templates/dashboard/choose_template.html`

### Missing or placeholder
- Home editor placeholder: `templates/dashboard/edit_home.html` (no editing UI yet)

## Quick Wins (next 3 commits)
1) Add a minimal dashboard preview panel for page editing (iframe on edit pages, similar to onboarding preview).
2) Add "Edit this page" button on tenant public pages for staff/owners (link to dashboard edit form).
3) Normalize section editing by mapping page sections to form groups (start with hero + services + contact).

## Risk / Chaos List
- `templates/core/base.html` has repeated `meta name="description"` lines (duplicate output).
- `_import/templates/` appears orphaned (not wired to URLConfs).
- `templates/components/test_delete.py` exists under templates (unexpected file type in template tree).
- `templates/core/home.html` contains large inline data blobs (hard to edit in templates; likely generated content).

## Frontend Editing Plan (Proposed)
### Phase 1 (minimal)
- Add "Edit this page" button for logged-in tenant owners on tenant public pages.
- Add sidebar form (existing dashboard forms) and save endpoint (reuse existing dashboard views).
- No live preview or clicking; just form edits + save.

### Phase 2
- Add iframe preview on edit pages and map clicks to section focus (postMessage stub).
- Sync currently selected section in the sidebar.

### Phase 3
- Add AI suggestion hooks per field (stub-only: store suggestions, no auto-apply).

