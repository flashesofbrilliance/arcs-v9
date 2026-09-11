# ADR-048 — Secrets Inventory & Rotation

**Status:** ACCEPTED · 2026-07-19
**Y:** YELLOW / MEDIUM / REVISIT (inventory is current-as-of-today; rotation cadence needs a human owner)
**Tributary:** J6 (ATG, ratified 2026-07-19)

## Context

This session alone touched or referenced five distinct secrets across two stores
(Vercel env + GitHub Actions secrets), on top of live rotation risks carried in the
handoff chain (Supabase DB password, `DATABASE_URL`). There has never been a single
inventory, so no one knows what exists, where it lives, or when it's due to rotate —
the precondition for a rotation-drift outage or a silent-exposure incident.

## Inventory (source of truth as of 2026-07-19)

| Secret | Where it lives | Used by | Rotation | Notes |
|--------|----------------|---------|----------|-------|
| `ANTHROPIC_API_KEY` | Vercel env (prod/preview/dev) | `/api/compass` Claude pipeline | on staff change / suspected leak | rotated once already (stale KCjY… → QhFmFd…) |
| `ANTHROPIC_API_KEY` (2nd copy) | **needed** in GitHub → Secrets → Actions | `security.yml` (claude-code-security-review) | mirror of above | NOT yet set — action no-ops until added |
| `AUTH_SECRET` | Vercel env | Auth.js v5 session signing | 12 mo / on leak | rotating invalidates all sessions |
| `AUTH_RESEND_KEY` | Vercel env | magic-link email (Resend) | on leak | Resend dashboard |
| `DATABASE_URL` (+ `DIRECT_URL`) | Vercel env | Prisma → Supabase | tied to DB password | manually set, NOT integration-managed → drift risk (ADR-005) |
| Supabase DB password | Supabase dashboard | source of `DATABASE_URL` | **overdue** — set a reminder | handoff-flagged rotation risk, unrotated |
| `SUPABASE_SERVICE_ROLE_KEY` | Vercel env (if present) | server-side Supabase | on leak | bypasses RLS — highest blast radius |
| `GITHUB_TOKEN` | Vercel env (proposed, J-track) | `/api/pulse` (public-repo read, 5000/hr) | low sensitivity | public-repo read only; unscoped classic or fine-grained read |
| Resend MCP key | Resend dashboard | session email tooling | **stale** — flagged unrotated in handoffs | blocks automated email |

## Decision

1. This table is the canonical inventory; update it in place when a secret is added,
   moved, or rotated (append a dated line to the changelog below).
2. **Rotation cadence** (needs a human owner to enforce — no session can):
   - Session-signing (`AUTH_SECRET`): 12 months.
   - Provider API keys (Anthropic, Resend): on staff change or suspected leak.
   - DB password + `DATABASE_URL`/`DIRECT_URL`: rotate together; set a recurring
     calendar reminder (the drift risk is that they're manual, not managed).
   - `SERVICE_ROLE_KEY`: treat as highest-value; rotate on any exposure immediately.
3. **Never** commit a secret; both stores (Vercel env, GH Actions Secrets) are the
   only sanctioned homes. A secret in git history is a rotation event, not a fix.

## Consequences

- Two immediate human actions surface: (a) mirror `ANTHROPIC_API_KEY` into GH Actions
  Secrets so `security.yml` can run; (b) rotate the overdue Supabase DB password and
  the stale Resend MCP key, then set recurring reminders.
- Revisit trigger: first external user, or any new secret added.

## Changelog
- 2026-07-19 — v1.0 — initial inventory (J6/ATG).
