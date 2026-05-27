# ADR-001 — Auth Gate Strategy: App-Level vs. Supabase RLS

> **Status:** DECIDED  
> **Date:** 2026-05-27  
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should ARCS v9 enforce access control via Supabase Row Level Security (RLS) or app-level auth gating in Next.js middleware/routes?

---

## E — Entity / System

- `src/lib/auth.ts` — Auth.js v5 magic link config  
- `src/app/api/` — all API routes  
- `prisma/schema.prisma` — User ↔ Receipt relation  
- Supabase (prod datasource)

---

## W — Window

**Horizon:** YEAR  
**Revisit trigger:** If ARCS adds multi-tenant org accounts, shared receipts, or a public API surface — RLS becomes necessary at that point.

---

## Context

ARCS v9 is a single-user-first app. The current auth model is Auth.js v5 magic link: user authenticates via email, session is JWT-backed, every API route checks `auth()` and gates on `session.user.id`. Receipts are associated to users via `userId` FK.

Supabase RLS would add a second enforcement layer at the database level — useful when multiple clients or services have direct DB access, or when you can't trust the app layer. For ARCS v9 right now, there's exactly one access path: the Next.js API routes.

No multi-tenant, no shared receipts, no public API, no direct DB client access from browser.

---

## Options Considered

### Option A — App-level auth gating (current)
- Auth.js session checked in every API route handler
- `userId` filter applied in every Prisma query (`where: { userId: session.user.id }`)
- No RLS policies configured on Supabase
- Pros: simpler, faster to ship, no Supabase policy maintenance
- Cons: relies on route discipline; if a route forgets the userId filter, data leaks are possible

### Option B — Supabase RLS
- Row-level policies enforce `auth.uid() = userId` at the DB layer
- Every query is safe regardless of whether the app layer filters correctly
- Pros: defense in depth, survives accidental app-layer bugs
- Cons: requires Supabase auth JWT to be threaded through Prisma (non-trivial with Prisma 7 + Auth.js v5); significant config overhead; adds latency

### Option C — Both (belt + suspenders)
- App-level gating AND RLS enabled
- Pros: maximum safety
- Cons: double the maintenance surface; complexity cost isn't justified at current scale

---

## Decision

**Chosen:** Option A — App-level auth gating

**Rationale:** Single access path (Next.js API only), single-user-first product, no shared data model yet. The complexity cost of threading Supabase auth JWTs through Prisma 7 is not justified by the safety gain at this stage. Route discipline is enforced by code review + the fact that there are <10 API routes.

**Trade-offs accepted:** If a route ships without userId filtering, there's no DB-layer backstop. Accepted: the route surface is small and auditable.

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** What if a future engineer adds a route that fetches receipts by sessionId without filtering userId? RLS would catch that automatically; app-level gating won't. Counter: the Receipt model's sessionId is itself tied to userId at creation time, and the route surface will be audited before any public launch.

---

## Consequences

- No Supabase RLS policies to configure for P4 deploy — simplifies the Supabase setup to: create project, get connection strings, `prisma db push`
- Auth gate audit required before any public launch: verify every `/api/` route applies `where: { userId: session.user.id }` or equivalent
- Revisit if: multi-tenant orgs, shared receipts, or a public API surface gets scoped

**Implementation pointer:** `src/app/api/` — all route handlers; `src/lib/auth.ts`

---

## Linked receipts / ADRs

- ADR-002 — Database: SQLite dev / Supabase prod split (depends on this)
