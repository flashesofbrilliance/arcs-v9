# ADR-006 — Supabase Branching for Preview Deployments

> **Status:** DECIDED  
> **Date:** 2026-05-27  
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should Vercel preview deployments for arcs-v9 get isolated Supabase branch databases, or share a single database until a named gate condition is met?

---

## E — Entity / System

- arcs-v9 Vercel project (preview deployments)
- Supabase ARCS project (`owdiiyvphyifukygvxhg`, us-east-2)
- `prisma/schema.prisma` — DDL source of truth
- GitHub PRs / preview URLs

---

## W — Window

**Horizon:** QUARTER  
**Revisit trigger:** First external contributor opens a PR, OR first schema migration after any real user has created a receipt in production.

---

## Context

Supabase Branching creates isolated database branches per PR, with Vercel integration auto-injecting per-branch `DATABASE_URL` into preview deployments. This eliminates the risk of schema migrations in PRs breaking production data. Currently there are zero external users and zero rows in any table — the risk surface is low. Supabase Branching is a paid feature and adds CI/CD complexity before a PR workflow exists.

*Research summary:* Supabase Branching integrates natively with Vercel — on PR open, a branch DB is created and env vars auto-populated in the preview deployment. Schema changes are isolated per branch. On merge, `supabase db push` or `prisma migrate deploy` applies to main.

---

## Options Considered

### Option A — Enable Supabase Branching now
- Per-PR isolated DB; Vercel integration handles env var injection per branch
- Zero risk of preview schema changes breaking production
- Requires Supabase paid plan feature; adds CI/CD surface area before needed

### Option B — All previews share production DB (current default)
- Simple; zero config
- Risk: destructive schema migration in a preview PR could drop production tables
- Acceptable while zero external users and zero data

### Option C — Previews share a separate staging DB (manual)
- Medium safety; manual maintenance burden
- Not worth the overhead at current team size (1)

---

## Decision

**Chosen:** Option B now; Option A at the hard gate.

**Rationale:** Zero rows in production, zero external users, zero PRs. Branching solves a real problem — but not one that exists yet. The complexity and plan cost are not justified. Accept Option B until the gate condition fires.

**Trade-offs accepted:** A destructive migration in a PR could affect production data. This is acceptable only while the hard gate condition has not been met.

---

## Y — Conviction

**Polarity:** YELLOW  
**Conviction:** MEDIUM  
**Stability:** STABLE

**Loki test:** A schema migration (ALTER TABLE, DROP COLUMN) runs in a preview deployment, applies to the shared production DB, and corrupts or drops data for real users. Mitigation today: zero external users + zero rows = no real data to corrupt. Hard gate: **if any external user creates a receipt in production, Supabase Branching becomes mandatory before any subsequent schema migration is merged**. This condition must be checked before every schema-altering PR.

---

## Consequences

- No action today; Option B is the implicit default
- Add to `_QUEUE/PENDING.md`: ADR-006 READY trigger = first external user OR first schema PR
- When gate fires: enable Supabase Branching in dashboard → Vercel integration auto-handles env vars
- Supabase Branching docs: https://supabase.com/docs/guides/deployment/branching

**Implementation pointer:** `_QUEUE/PENDING.md` — add ADR-006 with BLOCKED status and gate condition

---

## Linked receipts / ADRs

- ADR-005 — Vercel Supabase env injection (prerequisite; must be resolved first)
- ADR-007 — prisma db push vs migrate (branching changes migration deployment strategy)

---

## Amendment — Gate Fired, Action Required (2026-06-22)

> **Status:** GATE FIRED, NOT YET ENFORCED — action pending on your side (Supabase dashboard)

### What happened

The hard gate condition in the Loki test above — *"if any external user creates a receipt
in production"* — has fired. Verified precisely via direct query (`Receipt.createdAt` for
`cmqo7hylu000204l1zq0nqm8z`, the first real external sign-in, per `2ebf943`'s commit
message): **2026-06-21 19:55:34 UTC**.

**Correction to an earlier draft of this amendment:** I first wrote that schema changes
(the `SageTrace` table, commit `cb18c28`; the `Receipt.nciSelfGrade` column, commit
`1bf7251`) shipped *after* this gate fired. That was wrong — both commits are timestamped
2026-06-20, a full day *before* the 2026-06-21 19:55:34 gate-fire. There is no documented
violation. The correct framing: the gate fired 2026-06-21 19:55:34, and **no schema-altering
change has been merged since** — so the risk is entirely forward-looking, not retroactive.

Per this ADR's own rule, Supabase Branching became mandatory before any *subsequent*
schema-altering merge — i.e. starting now, the next one.

Confirmed via Supabase MCP this session: `list_branches` errors with "Project reference is
missing when validating permissions" while `list_migrations` succeeds on the same connection
— consistent with Branching never having been enabled on this project (no branches exist to
query).

### Action required (manual, Supabase dashboard — cannot be done via MCP/CLI from here)

1. Supabase dashboard → project `xbbpiryokswwvcrcutge` → **Settings → Branching** → enable
   (this is a paid-plan feature; confirm plan tier covers it before enabling)
2. Connect the Vercel integration if not already connected: Supabase dashboard →
   Integrations → Vercel → confirm `arcs-v9` project is linked
3. Once enabled, Vercel should auto-inject a per-branch `DATABASE_URL` on the next PR/preview
   deploy — verify on the next schema-touching PR specifically (check the preview deployment's
   env vars show a branch-scoped `DATABASE_URL`, not the shared production one)
4. After confirming a real branch-scoped preview works once, update this ADR's status to
   **ENFORCED** and remove the `_QUEUE/PENDING.md` READY flag

### Until enabled

Treat every schema-altering PR as a direct-to-production change (because it is one). No
automated guard exists to stop a destructive migration in a PR from reaching real user data —
this is a process gap, not just a paperwork one, until step 1 above is done.
