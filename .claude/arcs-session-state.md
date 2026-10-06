# ARCS session state — v3.98.0 (2026-10-05)

- Prod builds run `prisma migrate deploy` (production only) via `experimentalServices.web.buildCommand`.
- Prod migrations in sync with repo (22/22). DIRECT_URL set on arcs-v9 Production.
- Blocking: GitHub Actions billing block (no CI runs).
- Next: fix billing; optional `experimentalServices` -> `services` migration.
