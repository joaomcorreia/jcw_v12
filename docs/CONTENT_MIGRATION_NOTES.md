# Content Migration Notes

## Homepage DB Flow
- Main public `/` now renders the DB-driven Page with `slug="home"` on the main site.
- Content is sourced from `Page`, `PageSection`, and `SectionContent` and rendered via `templates/site/page.html` and section includes under `templates/site/sections/`.
- Tenant home behavior is unchanged (tenant root redirects to `/dashboard/`).

## Bootstrap
- Use `python manage.py seed_pages` to create the main site homepage and required sections if missing.
- Sections seeded (keys): `home.hero`, `home.features`, `home.pricing`, `home.printlab`, `home.faq`, `home.cta`.
