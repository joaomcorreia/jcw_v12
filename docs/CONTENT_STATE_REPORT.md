# Content State Report

## 1) Executive Summary (what’s broken / missing)
- Main marketing home route is currently hard-coded to return a proof string, so the `templates/core/home.html` content is not rendered on main site.
- Tenant public pages mostly render “Coming soon” copy unless tenant pages/sections exist in DB (Page/SectionContent).
- Several dashboard/control-panel templates are placeholders (“Coming soon”, disabled actions).
- PrintLab category start page is a placeholder (“Designer coming soon”).
- Large blocks of marketing copy live in templates (`templates/core/*.html`, `templates/pages/websites/*.html`) and should move to DB to enable editing.

## 2) Master Page Map (Route -> View -> Template)

### Main public site (config/urls.py + core/urls.py)
| Route | View | Template | App | Notes |
| --- | --- | --- | --- | --- |
| `/` | `core.views.home` | n/a (returns plain text) | core | MAIN home currently returns proof text; tenant home redirects to dashboard. |
| `/signup/` | `core.views.signup_view` | `templates/registration/signup.html` | core | Public signup. |
| `/start/` | `core.views.start_design` | `templates/core/onboarding_step1.html` | core | Uses draft form; content in template. |
| `/onboarding/step-1/` | `core.views.onboarding_step1` | `templates/core/onboarding_step1.html` | core | Template has form copy; saves draft. |
| `/onboarding/step-2/` | `core.views.onboarding_step2` | `templates/core/onboarding_step2.html` | core | Template has wizard copy. |
| `/onboarding/step-3/` | `core.views.onboarding_step3` | `templates/core/onboarding_step3.html` | core | Contains iframe preview. |
| `/onboarding/complete/` | `core.views.complete_draft` | redirect | core | No template. |
| `/websites/` | `core.views.websites` | `templates/core/websites.html` | core | Fallback template used when no DB Page. |
| `/services/` | `core.views.services` | `templates/core/services.html` | core | Fallback template used when no DB Page. |
| `/help-center/` | `core.views.help_center` | `templates/core/help_center.html` | core | Fallback template used when no DB Page. |
| `/blog/` | `core.views.blog_index` | `templates/core/blog_index.html` | core | DB-driven posts. |
| `/blog/<slug>/` | `core.views.blog_detail` | `templates/core/blog_detail.html` | core | DB-driven post body. |
| `/print-lab/` | `core.views.print_lab` | `templates/core/print_lab.html` | core | Fallback template used when no DB Page. |
| `/print-lab/products/` | `core.views.print_lab_products` | `templates/core/print_lab_products.html` | core | Fallback template used when no DB Page. |
| `/print-lab/how-it-works/` | `core.views.print_lab_how_it_works` | `templates/core/print_lab_how_it_works.html` | core | Fallback template used when no DB Page. |
| `/print-lab/faq/` | `core.views.print_lab_faq` | `templates/core/print_lab_faq.html` | core | Fallback template used when no DB Page. |
| `/printlab/` | `core.views.printlab` | `templates/core/product_page.html` | core | Fallback template used when no DB Page. |
| `/printlab/start/` | `core.views.printlab_start` | `templates/core/printlab_start.html` | core | Placeholder copy. |
| `/printlab/*` | `core.views.printlab_*` | `templates/core/product_page.html` | core | Fallback template used when no DB Page. |
| `/billing/` | `core.views.billing` | `templates/core/billing.html` | core | Fallback template used when no DB Page. |
| `/billing/*` | `core.views.billing_*` | `templates/core/billing_*.html` | core | Fallback template used when no DB Page. |
| `/printful/` | `core.views.printful` | `templates/core/printful.html` | core | Fallback template used when no DB Page. |
| `/printful/products/` | `core.views.printful_products` | `templates/core/printful_products.html` | core | Fallback template used when no DB Page. |
| `/printful/orders/` | `core.views.printful_orders` | `templates/core/printful_orders.html` | core | Fallback template used when no DB Page. |
| `/products/` | `core.views.products_index` | `templates/core/product_page.html` | core | Fallback template used when no DB Page. |
| `/products/*` | `core.views.product_*` | `templates/core/product_page.html` | core | Fallback template used when no DB Page. |
| `/websites/one-page/` | `core.views.websites_one_page` | `templates/core/websites_one_page_plan.html` | core | Hardcoded copy. |
| `/websites/multi-page/` | `core.views.websites_multi_page` | `templates/pages/websites/multi_page_plan.html` | core | Hardcoded copy + TODO note. |
| `/websites/multi-page-seo/` | `core.views.websites_multi_page_seo` | `templates/pages/websites/multi_page_seo_plan.html` | core | Hardcoded copy + TODO note. |
| `/websites/catalog-site/` | `core.views.websites_catalog_site` | `templates/pages/websites/catalog_site_plan.html` | core | Hardcoded copy. |
| `/websites/eshop-starter/` | `core.views.websites_eshop_starter` | `templates/pages/websites/starter_estore_plan.html` | core | Hardcoded copy. |
| `/websites/eshop-premium/` | `core.views.websites_eshop_premium` | `templates/pages/websites/premium_estore_plan.html` | core | Hardcoded copy. |
| `/websites/custom/` | `core.views.websites_custom` | `templates/pages/websites/custom_website_plan.html` | core | Hardcoded copy + preview placeholder. |
| `/locations/<country>/` | `core.views.location_country` | `templates/site/page.html` | core | Content built in `core/public/locations.py`. |
| `/locations/<country>/<city>/` | `core.views.location_city` | `templates/site/page.html` | core | Content built in `core/public/locations.py`. |
| `/<slug>/` | `core.views.public_page` | `templates/site/page.html` | core | DB Page/SectionContent if present; else 404. |

### Tenant public site (config/tenants/urls.py + core/urls_tenant.py)
| Route | View | Template | App | Notes |
| --- | --- | --- | --- | --- |
| `/` | `core.views.home` | redirect | core | Tenant home redirects to dashboard. |
| `/locations/<country>/` | `core.views.location_country` | `templates/site/page.html` | core | Content built in `core/public/locations.py`. |
| `/locations/<country>/<city>/` | `core.views.location_city` | `templates/site/page.html` | core | Content built in `core/public/locations.py`. |
| `/<slug>/` | `core.views.public_page` | `templates/site/page.html` | core | DB Page/SectionContent required. |

### Tenant dashboard (core/urls_dashboard.py)
| Route | View | Template | App | Notes |
| --- | --- | --- | --- | --- |
| `/dashboard/` | `core.views.dashboard` | `templates/dashboard/home.html` | core | Auth required. |
| `/dashboard/users/` | `core.views.dashboard_users` | `templates/dashboard/users.html` | core | Auth required. |
| `/dashboard/frontend/pages/` | `core.views.dashboard_pages` | `templates/dashboard/pages.html` | core | Plan-gated actions. |
| `/dashboard/frontend/pages/create/` | `core.views.dashboard_create_page` | `templates/dashboard/page_create.html` | core | Plan-gated. |
| `/dashboard/frontend/pages/<id>/edit/` | `core.views.dashboard_edit_page` | `templates/dashboard/page_edit.html` | core | Form-based editing. |
| `/dashboard/frontend/pages/<id>/edit-services/` | `core.views.dashboard_edit_page_services` | `templates/dashboard/page_edit_services.html` | core | Form-based section editing. |
| `/dashboard/frontend/pages/<id>/edit-contact/` | `core.views.dashboard_edit_page_contact` | `templates/dashboard/page_edit_contact.html` | core | Form-based section editing. |
| `/dashboard/frontend/pages/<id>/seo/` | `core.views.dashboard_page_seo` | `templates/dashboard/page_seo.html` | core | Plan-gated indexing options. |
| `/dashboard/frontend/visibility/` | `core.views.dashboard_visibility` | `templates/dashboard/visibility.html` | core | Plan-gated controls. |
| `/dashboard/frontend/menu/` | `core.views.dashboard_menu` | `templates/dashboard/menu.html` | core | Navigation editor. |
| `/dashboard/frontend/site-settings/` | `core.views.dashboard_site_settings` | `templates/dashboard/site_settings.html` | core | Placeholder text. |
| `/dashboard/frontend/blog/` | `core.views.dashboard_blog` | `templates/dashboard/blog.html` | core | Placeholder UI (disabled). |
| `/dashboard/billing/` | `core.views.dashboard_billing` | `templates/dashboard/billing.html` | core | Placeholder UI. |
| `/dashboard/print-studio/` | `core.views.dashboard_print_studio` | `templates/dashboard/print_studio.html` | core | Placeholder UI. |
| `/dashboard/control-panel/` | `core.views.dashboard_control_panel` | `templates/dashboard/control_panel.html` | core | Placeholder UI. |
| `/dashboard/edit-home/` | `core.views.dashboard_edit_home` | `templates/dashboard/edit_home.html` | core | Placeholder UI. |
| `/dashboard/choose-template/` | `core.views.dashboard_choose_template` | `templates/dashboard/choose_template.html` | core | Template selection UI. |
| `/dashboard/main-site/pages/` | `core.views.dashboard_main_site_pages` | `templates/dashboard/pages.html` | core | Staff-only. |
| `/dashboard/main-site/pages/<id>/edit/` | `core.views.dashboard_main_site_edit_page` | `templates/dashboard/page_edit.html` | core | Staff-only. |

### Control panel (operators, config/urls.py -> controlpanel/urls.py)
| Route | View | Template | App | Notes |
| --- | --- | --- | --- | --- |
| `/control-panel/` | `controlpanel.views.home` | `templates/controlpanel/home.html` | controlpanel | Placeholder “Coming soon.” |
| `/control-panel/dashboard/` | `controlpanel.views.dashboard` | `templates/controlpanel/dashboard.html` | controlpanel | Overview counts. |
| `/control-panel/domains-hosting/` | `controlpanel.views.domains_hosting` | `templates/controlpanel/domains_hosting.html` | controlpanel | Placeholder. |
| `/control-panel/templates/` | `controlpanel.views.templates_list` | `templates/controlpanel/templates_list.html` | controlpanel | Lists WebsiteTemplate records. |
| `/control-panel/templates/new/` | `controlpanel.views.templates_create` | `templates/controlpanel/templates_form.html` | controlpanel | JSON template editor. |
| `/control-panel/templates/<id>/edit/` | `controlpanel.views.templates_edit` | `templates/controlpanel/templates_form.html` | controlpanel | JSON template editor. |
| `/control-panel/users/` | `controlpanel.views.users` | `templates/controlpanel/users.html` | controlpanel | Placeholder. |
| `/control-panel/billing/` | `controlpanel.views.billing` | `templates/controlpanel/billing.html` | controlpanel | Placeholder. |
| `/control-panel/plans/` | `controlpanel.views.plans_list` | `templates/controlpanel/plans_list.html` | controlpanel | Plan list. |
| `/control-panel/plans/create/` | `controlpanel.views.plans_create` | `templates/controlpanel/plans_form.html` | controlpanel | Plan creation. |
| `/control-panel/plans/<id>/edit/` | `controlpanel.views.plans_edit` | `templates/controlpanel/plans_form.html` | controlpanel | Plan edit (no SEO caps here). |
| `/control-panel/tenants/` | `controlpanel.views.tenants` | `templates/controlpanel/tenants.html` | controlpanel | Tenant list. |
| `/control-panel/tenants/<id>/edit/` | `controlpanel.views.tenant_edit` | `templates/controlpanel/tenant_edit.html` | controlpanel | Tenant plan edit. |

### Ops (legacy operator panel, controlpanel/ops_urls.py)
| Route | View | Template | App | Notes |
| --- | --- | --- | --- | --- |
| `/ops/` | `controlpanel.views_ops.ops_home` | `templates/ops/home.html` | controlpanel | Simple overview. |
| `/ops/sites/` | `controlpanel.views_ops.ops_sites_list` | `templates/ops/sites_list.html` | controlpanel | List sites. |
| `/ops/sites/<id>/` | `controlpanel.views_ops.ops_site_detail` | `templates/ops/site_detail.html` | controlpanel | Plan + visibility editing. |

## 3) Public Pages: Content source + status
### Main marketing pages (core)
- `templates/core/home.html`: heavy hardcoded copy + embedded data blocks; not currently used by main home route.
- `templates/core/services.html`, `templates/core/websites.html`, `templates/core/pos_systems*.html`, `templates/core/help_center.html`, `templates/core/print_lab*.html`, `templates/core/printful*.html`, `templates/core/product_page.html`: hardcoded marketing copy with `{% trans %}` strings; fallback used when no DB Page exists.
- `templates/pages/websites/*.html`: full marketing pages with hardcoded copy; TODO notes in some.
- `templates/core/blog_index.html` / `templates/core/blog_detail.html`: dynamic posts from DB with placeholder images.
- `templates/core/billing*.html`: hardcoded copy with optional plan data from DB.

### Tenant public pages (site)
- `templates/site/home.html`: “Coming soon” placeholder.
- `templates/site/page.html`: dynamic content from DB sections (Page/SectionContent).
- `templates/site/location_landing.html` and `templates/site/sections/location.html`: minimal copy generated in `core/public/locations.py`.

## 4) Product Pages: Content source + clarity gaps
- Product routes use `core/views.product_*` with `templates/core/product_page.html` unless a DB Page exists.
- Hardcoded blocks in `templates/core/product_page.html` include PrintLab content; no clear DB mapping for these sections.
- Suggestion: move product feature lists and CTAs into Page/SectionContent.

## 5) PrintLab Pages: list + content status
| Route | Template | Content present? | Source |
| --- | --- | --- | --- |
| `/print-lab/` | `templates/core/print_lab.html` | yes | hardcoded + DB sections if Page exists |
| `/print-lab/products/` | `templates/core/print_lab_products.html` | yes | hardcoded + DB sections if Page exists |
| `/print-lab/how-it-works/` | `templates/core/print_lab_how_it_works.html` | yes | hardcoded + DB sections if Page exists |
| `/print-lab/faq/` | `templates/core/print_lab_faq.html` | yes | hardcoded + DB sections if Page exists |
| `/printlab/` | `templates/core/product_page.html` | yes | hardcoded fallback |
| `/printlab/start/` | `templates/core/printlab_start.html` | partial | “Designer coming soon.” placeholder |
| `/printlab/*` | `templates/core/product_page.html` | yes | hardcoded fallback |

## 6) Blog: models + content
- Models: `core.models.BlogCategory`, `core.models.BlogPost` (JSON fields for per-language content).
- Routes/templates: `core.views.blog_index` -> `templates/core/blog_index.html`, `core.views.blog_detail` -> `templates/core/blog_detail.html`.
- Seeding: `core/management/commands/seed_blog.py` creates categories + posts.
- Placeholder imagery: blog templates use static placeholder images for posts.

## 7) DB Content Models (content storage)
| Model | Fields (summary) | Where used | Admin registered? | Migrations |
| --- | --- | --- | --- | --- |
| `Page` (Translatable) | slug, template_key, nav fields, translations incl. meta title/description, robots | `render_page`, `public_page` | yes (`core/admin.py`) | yes (`core/migrations/*`) |
| `PageSection` | page FK, key, order, is_visible | page section list | yes | yes |
| `SectionContent` (Translatable) | config_json + translated heading/body/cta | page sections | yes | yes |
| `RightSidebarPanel` (Translatable) | headline/intro/cta, contact fields | `core/services/pages.get_sidebar_panel` | yes | yes |
| `WebsiteTemplate` | name, slug, description, languages, sections JSON | dashboard template selection + control panel editor | yes | yes |
| `BlogCategory` | name JSON, slug, is_active | blog index | yes | yes |
| `BlogPost` | title/excerpt/body JSON, featured_image | blog index/detail | yes | yes |
| `SiteSettings` | business_name, contact, address | SEO/schema + location landing | yes | yes |
| `Feature` | key, name, flags | feature gating | yes | yes |

## 8) Translation implications
- Templates rely on `{% trans %}` / `{% blocktrans %}` and `.po` files in `locale/*/LC_MESSAGES/django.po`.
- DB translations use Parler (Page, SectionContent, Plan, RightSidebarPanel).
- Blog content is per-language JSON in DB, not `.po`.
- Tenant pages depend on DB translations; main marketing templates depend on `.po`.

## 9) Migration plan: move content to DB (priority order)
1) Main home content: move hero, pricing, printlab blocks, and large data blobs from `templates/core/home.html` into Page/SectionContent.
2) Product pages: move `templates/core/product_page.html` copy into Page/SectionContent with consistent section keys.
3) PrintLab pages: move `templates/core/print_lab*.html` copy into DB sections for editability.
4) Plan landing pages under `templates/pages/websites/*.html`: move to Page/SectionContent with section mapping (already noted by TODO).
5) Help center and services pages: convert key copy blocks to sections.
6) Tenant “coming soon” pages: add default Page/SectionContent on site creation to avoid empty content.
7) Footer/legal links: create Page records with slugs and content if required.

## Next Actions (Top 10)
1) Restore main home render to use `templates/core/home.html` or move to DB-first Page/SectionContent.
2) Define canonical section keys for marketing pages (hero, features, cta, etc.).
3) Create DB sections for PrintLab pages and wire templates to sections.
4) Convert `templates/pages/websites/*.html` copy into DB-managed sections.
5) Add default tenant pages/sections on site creation to replace “Coming soon” placeholders.
6) Replace placeholder blog images with media-backed fields (or DB media assets).
7) Build a “content inventory” admin view that lists pages/sections and missing translations.
8) Add content coverage checks (empty sections, missing translations).
9) Add structured content for legal pages (privacy/terms) via Page records.
10) Remove duplicate hardcoded copy once DB content is live and verified.

