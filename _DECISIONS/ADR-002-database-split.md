# ADR-002 — Database Strategy: SQLite Dev / Supabase Prod Split

> **Status:** DECIDED  
> **Date:** 2026-05-27  
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** How should ARCS v9 manage the dev/prod database split, and what's the migration strategy for moving from SQLite to Supabase Postgres?

---

## E — Entity / System

- `prisma/schema.prisma` — datasource block  
- `prisma.config.ts` — Prisma 7 connection config  
- `prisma/migrations/` — migration history  
- Supabase project (prod)  
- `dev.db` (local SQLite)

---

## W — Window

**Horizon:** QUARTER  
**Revisit trigger:** When P4 deploy lands and Supabase is the live datasource.

---

## Context

Prisma 7 introduced a breaking change (P1012): `url` and `directUrl` can no longer live in `schema.prisma`. Connection URLs must be in `prisma.config.ts`. This was the root cause of 6 consecutive Vercel build failures (fixed at commit `42852d4`).

Current setup:
- `prisma.config.ts` uses `process.env["DATABASE_URL"] ?? "file:./dev.db"` — SQLite fallback for local, Postgres URL for prod
- `schema.prisma` datasource has `provider = "postgresql"` only (no url field)
- Local dev runs entirely on SQLite with 17+ receipts
- Vercel has `ANTHROPIC_API_KEY`, `AUTH_SECRET`, `RESEND_API_KEY` set but NOT `DATABASE_URL` / `DIRECT_URL` yet → build passes prisma generate but Next.js compile may still fail

Prisma supports SQLite in dev and Postgres in prod via the env fallback. The provider mismatch (schema says postgresql, dev uses sqlite) works because Prisma 7 resolves the actual driver at runtime from `prisma.config.ts`, not from the schema provider field.

---

## Options Considered

### Option A — SQLite dev, Supabase prod (current)
- Local: `file:./dev.db` — zero config, fast, no network dependency
- Prod: Supabase Postgres via pooler URL (port 6543) + direct URL (port 5432)
- Pros: local dev is instant, no Supabase dependency for daily work
- Cons: schema drift risk if SQLite-only migrations don't get tested against Postgres

### Option B — Supabase for everything (local + prod)
- Local dev points at Supabase dev branch or local Supabase Docker
- Pros: eliminates any SQLite/Postgres behavioral differences
- Cons: network dependency for local dev, Docker overhead, Supabase branch management

### Option C — PlanetScale / Neon instead of Supabase
- Alternative Postgres providers
- Not evaluated — Supabase already selected and consistent with arcs-care

---

## Decision

**Chosen:** Option A — SQLite dev / Supabase prod split

**Rationale:** Local dev velocity is the priority. SQLite zero-config is a feature, not a compromise. The Prisma 7 fallback pattern (`?? "file:./dev.db"`) was explicitly designed for this use case. Schema drift risk is manageable: `prisma db push` on Supabase before each deploy validates compatibility.

**Trade-offs accepted:** Any SQLite-specific behavior (e.g. TEXT vs JSON column types, case sensitivity) won't surface until push to Supabase. All JSON arrays are stored as TEXT strings anyway (per WORLD.md), which is Postgres-compatible.

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** What if a migration that works in SQLite fails silently on Postgres and corrupts prod data? Counter: `prisma db push` is the gate before any deploy; it runs against the live Supabase instance and will fail fast on incompatibilities.

---

## Consequences

**P4 unblock checklist:**
1. Supabase dashboard → Settings → Database → Connection Strings
   - Pooler URL (port 6543, Transaction mode) = `DATABASE_URL`
   - Direct URL (port 5432) = `DIRECT_URL`
2. Supabase dashboard → Settings → API → service_role key = `SUPABASE_SERVICE_ROLE_KEY`
3. Set all three on Vercel (project env vars, production + preview)
4. Run `npx prisma db push` against Supabase to sync schema
5. `vercel deploy`

**Implementation pointer:** `prisma.config.ts`, `prisma/schema.prisma`

---

## Linked receipts / ADRs

- ADR-001 — Auth Gate Strategy (upstream; auth model affects userId FK in Receipt)
- ADR-003 — P4 Vercel deploy sequence (downstream; this ADR defines the unblock checklist)

---

## Amendment — 2026-05-28 — Trigger Fired / Decision Closed

**Revisit trigger fired:** P4 deploy landed (`arcs-zachharris-3439s-projects.vercel.app`, commit `11ba2fc`).
Supabase is now the live production datasource. This ADR's unblock checklist is complete.

**Actual execution divergence (from ADR-005/007 amendments):**
- `DATABASE_URL` was set manually via `vercel env add` (not Supabase integration — ADR-005 Option B)
- Schema bootstrap used Supabase MCP `apply_migration` (not `prisma db push` — ADR-007 Option C)
- Steps 4 and 5 of the P4 checklist were fulfilled by equivalent means

**Status update:** DECIDED → CLOSED. Decision was correct; trade-offs accepted held.
SQLite/Postgres behavioral gap did not produce any issues during bootstrap.

**Residual open item:** DATABASE_URL rotation risk (manually set, not integration-managed).
Calendar reminder recommended. See ADR-005 amendment for mitigation steps.
