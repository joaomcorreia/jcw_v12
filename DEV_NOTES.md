# JCW v12 Local Host Routing

Local host-based tenancy relies on subdomains under `justcodeworks.local`.

Hosts file entries:
- `127.0.0.1 justcodeworks.local`
- `127.0.0.1 mim.justcodeworks.local`

How routing works:
- `justcodeworks.local` resolves the main site (`Site.is_main=True`).
- `<subdomain>.justcodeworks.local` resolves a tenant by subdomain.
  - The subdomain matches `Site.slug` when present, otherwise it falls back to
    an exact `Site.name` match or a slugified name.

Debug header:
- Responses include `X-JCW-Site` with the resolved site identifier.
