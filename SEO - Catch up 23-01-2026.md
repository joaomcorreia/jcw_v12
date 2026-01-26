# SEO Catch-up 23-01-2026

## A) Current State Summary
- robots/sitemap endpoints exist only on the main-site URLConf; tenant subdomains do not expose `robots.txt` or `sitemap.xml` today. Main-site routes: `config/urls.py`, handlers in `core/views.py`.
- Sitemap generation includes active Pages (excluding `noindex` and basic-plan slug gating) plus location pages from `SiteVisibility`; no blog URLs, no pagination, no hreflang entries inside sitemap. Logic: `core/views.py`, `core/public/sitemaps.py`, `core/visibility_rules.py`.
- Meta title/description: main-site pages use translated `Page.meta_title/meta_description` via `seo_context`; tenant pages use non-translated `Page.seo_title/seo_description`. Templates: `templates/core/*.html` and `templates/site/base.html`; source fields in `core/models.py`.
- Canonical + hreflang only render for tenant-site templates (`templates/site/base.html`) using `core/seo_utils.py`; main-site templates omit canonical/hreflang entirely.
- JSON-LD is limited to Organization/WebSite/LocalBusiness built from `SiteSettings` and injected only in tenant templates (`templates/site/base.html`) via `core/schema.py`.
- Indexing controls: per-page `noindex` flag on `Page`, per-plan indexability gate using `BASIC_INDEXABLE_SLUGS` and visibility mode, and global `launch_noindex` that sets `X-Robots-Tag`. Files: `core/models.py`, `core/visibility_rules.py`, `core/middleware.py`, `config/settings.py`, `templates/site/base.html`.
- Location pages exist for tenant routes (`/locations/...`) with basic content blocks and SEO title/description; visibility is plan-driven via `SiteVisibility`. Files: `core/urls_tenant.py`, `core/views.py`, `core/services/visibility.py`, `templates/site/sections/location.html`.
- Blog SEO is basic (title/description only) with no canonicalization, JSON-LD Article, OG/Twitter, or pagination handling. Files: `core/views.py`, `templates/core/blog_index.html`, `templates/core/blog_detail.html`.
- Image alt usage exists only in a few templates (blog cards, nav logos); no systemic alt strategy. Files: `templates/core/*`, `templates/components/blog_latest_slider.html`.
- Internal linking helpers are minimal (nav builders + location section links). Files: `core/context_processors.py`, `core/views.py`, `templates/site/sections/location.html`.

## B) Inventory Table (feature -> implemented? -> where)
Feature | Implemented? | Where
--- | --- | ---
robots.txt endpoint | Main site only | `config/urls.py`, `core/views.py`
sitemap.xml + per-language | Main site only | `config/urls.py`, `core/views.py`
Sitemap contents | Pages + locations only | `core/views.py`, `core/public/sitemaps.py`
Meta title/description | Yes (main + tenant) | `core/context_processors.py`, `core/models.py`, `templates/site/base.html`, `templates/core/*.html`
Canonical tags | Tenant only | `templates/site/base.html`, `core/seo_utils.py`
hreflang | Tenant only | `templates/site/base.html`, `core/seo_utils.py`
Open Graph / Twitter meta | No | (not found)
JSON-LD structured data | Limited (Org/WebSite/LocalBusiness) | `core/schema.py`, `templates/site/base.html`
Noindex/nofollow | Yes (page + plan + launch) | `core/models.py`, `core/visibility_rules.py`, `core/middleware.py`, `templates/site/base.html`
Location landing pages | Tenant only | `core/urls_tenant.py`, `core/views.py`, `core/services/visibility.py`
Blog SEO | Minimal | `core/views.py`, `templates/core/blog_index.html`, `templates/core/blog_detail.html`
Image alt strategy | Partial | `templates/core/*`, `templates/components/blog_latest_slider.html`
Internal linking helpers | Minimal | `core/context_processors.py`, `core/views.py`

## C) Gap Report by Tier
### Local Plan SEO (city-limited)
- Missing tenant robots/sitemap endpoints; needed for subdomain SEO. Add to `config/tenants/urls.py`.
- No per-tenant or per-language SEO fields (tenant uses non-translated `Page.seo_title/seo_description`). Needs multilingual SEO fields for tenant pages.
- LocalBusiness schema exists but is global and not location-specific; needs location-page schema + local keywords per city.
- City selector UI exists only for location visibility under "locations" mode; no "single city" or "user-chosen city" UX specifically tied to Local plan.
- No OG/Twitter metadata on tenant pages or main site.

### Country Plan SEO (6 city selector + internal linking)
- No structured "top cities list" UI; current visibility UI allows arbitrary countries/cities and depends on plan limits. Needs fixed 6-city selector UX and storage.
- No location landing page clusters or internal linking logic (e.g., "services in City" pages list / hub pages).
- Sitemap does not include any blog or location-cluster logic beyond current visibility. No city landing rule set or per-plan inclusion rules.
- No canonical or hreflang on main site, so country-wide pages on main marketing site will not be SEO-clean.

### EU Plan SEO (max)
- Structured data is far below requirement: no Service/FAQ/Article/Breadcrumb/Review schema; no per-page schema composition.
- No multi-country language strategy beyond URL prefix; no per-language metadata for tenant pages, no hreflang on main site.
- No indexing controls for drafts/custom pages beyond `Page.noindex` and basic plan gating; needs per-page indexing settings and plan gating.
- No sitemap segmentation (by content type, by language/country); missing canonical/hreflang rules for blog and location pages.

## D) Recommended Next Steps (priority checklist + file pointers)
1) Add tenant robots/sitemap routing and handlers
- Add `robots.txt` + `sitemap.xml` routes to `config/tenants/urls.py` pointing at existing `core/views.py` handlers.
- Ensure absolute URLs use tenant host via `request.build_absolute_uri` (already done in `core/views.py`).

2) Normalize SEO data model for multilingual tenant pages
- Add translated SEO fields to tenant pages (or move to a `SEOProfile`/`PageSEOTranslation` model) and use them in `templates/site/base.html`.
- Review `core/models.py`, `core/views.py`, `dashboard/page_seo.html`, `dashboard/forms.py`.

3) Plan-aware SEO settings + gating
- Define tier flags (Local/Country/EU) in a single config (settings or model) and enforce in views/services: `core/visibility_rules.py`, `core/services/features.py`, `dashboard/plan_features.py`.
- Use `SiteVisibility` plus explicit plan tiers to gate meta controls, schema types, sitemap inclusion, and location selector UX.

4) Sitemap expansion + rules
- Include blog posts + location pages + custom pages per plan; split into index + per-type sitemaps.
- Add rules for draft/noindex exclusion and per-language URL inclusion.
- Files: `core/views.py`, `core/public/sitemaps.py`, `core/visibility_rules.py`.

5) Canonical + hreflang for main site (and blog)
- Add canonical and hreflang tags to `templates/core/base.html` (and blog templates), using `core/seo_utils.py`.
- Add blog canonicalization and pagination support if pagination is introduced.

6) Structured data strategy by page type
- Extend `core/schema.py` to emit Organization, LocalBusiness, Service, FAQ, Article, Breadcrumb based on page type.
- Pass per-page context from `core/views.py` (page type + blog post details) into schema builder.

7) Location targeting UX + storage
- Local: single city selector + default location in `SiteSettings` or a `LocationTargeting` model.
- Country: fixed "6 cities" selector with stored list + landing pages + internal linking rules.
- EU: multi-country/city targeting + sitemap cap rules (currently `LOCATION_SITEMAP_CAP` only).
- Files: `core/models.py`, `core/views.py`, `templates/dashboard/visibility.html`, `core/services/visibility.py`.

8) Meta + social metadata coverage
- Add OG/Twitter tags to tenant + main templates.
- Files: `templates/site/base.html`, `templates/core/base.html`, `templates/core/blog_*`.
