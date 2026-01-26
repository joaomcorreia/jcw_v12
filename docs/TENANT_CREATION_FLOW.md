# Tenant Creation Flow

This document describes how tenant sites and subdomains are created during website signups.

## When tenant is created
- During `POST` to `core.views.signup`, after the user account is created and logged in.
- Staff/superuser signups are excluded from auto-creation.

## Subdomain generation
- Source: draft business name (if present) or username.
- Normalization: `slugify`, lowercased, trimmed, with reserved names avoided.
- Uniqueness: increments suffix (`mybiz`, `mybiz-2`, `mybiz-3`, ...) until unused.

## Content seeded
- A `Page` record with `slug="home"` is created for the tenant site if missing.
- Sections created (only if missing):
  - `home.hero`
  - `home.services`
  - `home.cta`
- Each section gets minimal default `config_json` so the tenant home renders and is editable.

## Redirect after signup
- Users are redirected to the tenant dashboard on the subdomain:
  - `http://{subdomain}.{MAIN_DOMAIN}/{lang}/dashboard/`
- Language prefix uses `request.LANGUAGE_CODE` (fallback to active language).
