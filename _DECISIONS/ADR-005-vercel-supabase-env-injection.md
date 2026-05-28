# ADR-005 — Vercel Supabase Integration: Env Var Injection

> **Status:** DECIDED — EXECUTION DIVERGED (see Amendment below)
> **Date:** 2026-05-27  
> **Amended:** 2026-05-28
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** What is the canonical source of truth for Supabase→Vercel env var injection, and how should DATABASE_URL reach the arcs-v9 Vercel project without manual copy-paste?

---

## E — Entity / System

- Vercel project: `arcs` (`prj_KjhmInzgwA6Pdh7tg8Yx7W8JzEtt`)
- Supabase project: `ARCS` (`owdiiyvphyifukygvxhg`, us-east-2, ACTIVE_HEALTHY)
- `src/lib/db.ts` — runtime consumer of `DATABASE_URL`
- `prisma/schema.prisma` — `url = env("DATABASE_URL")`

---

## W — Window

**Horizon:** TODAY  
**Revisit trigger:** If `vercel env ls production` no longer shows `DATABASE_URL` after an env pull, or if Supabase rotates the pooler endpoint format. Also revisit when enabling Supabase Branching (ADR-006).

---

## Context

The Vercel Supabase integration was installed but misconfigured: the custom env var prefix was set to `STORAGE` instead of `DATABASE`, causing the integration to inject `STORAGE_URL` (or nothing) rather than `DATABASE_URL`. Every arcs-v9 Vercel deployment since the Postgres datasource switch has been ERROR. The Supabase project is confirmed ACTIVE_HEALTHY and reachable via MCP.

*Research summary:* Vercel Marketplace integrations auto-sync env vars including DATABASE_URL when prefix is configured correctly. The integration handles password rotation and branch-specific injection automatically — no manual copy-paste needed after initial setup.

---

## Options Considered

### Option A — Fix integration prefix to "DATABASE"
- Set prefix to `DATABASE` in Vercel → Supabase integration config
- Integration injects `DATABASE_URL` (pooler, 6543) automatically
- Stays in sync on password rotation; no manual steps after initial fix

### Option B — Manually add DATABASE_URL via `vercel env add`
- Grab password from Supabase dashboard, construct pooler URL, paste into Vercel
- Works once but drifts on rotation; no automatic sync

### Option C — Supabase Branching (auto-inject per branch)
- Full per-PR branch isolation; Vercel integration auto-populates per-branch DATABASE_URL
- Right long-term path; premature before branching is enabled (see ADR-006)

---

## Decision

**Chosen:** Option A — fix integration prefix to `DATABASE`

**Rationale:** One-time config fix that makes the integration work as designed. No password handling, no drift, no manual maintenance. Option B works but creates a recurring manual dependency. Option C is the correct eventual state but out of scope for TODAY.

**Trade-offs accepted:** Dependent on the Vercel Supabase integration remaining healthy. If it breaks silently, `DATABASE_URL` disappears from the project without warning.

---

## ⚠️ Amendment — 2026-05-28: Actual execution used Option B

**What happened:** Prefix was changed to `DATABASE` in the Vercel dashboard, but the integration failed to propagate `DATABASE_URL` to the Vercel project on subsequent `vercel env pull`. Root cause unknown (possible: Vercel Supabase integration lag or Supabase IPv4 connectivity issue from local machine).

**Actual execution:** `vercel env add DATABASE_URL production --value <pooler-url>` was run manually (Option B). `DATABASE_URL` is now set for Production and Development environments. Preview is still missing (CLI v53 bug prevents adding to "all preview branches" without specifying a non-main branch).

**Y state correction:** YELLOW / MEDIUM / REVISIT  
The decision intent was Option A; the live state is Option B. This is the rotation-drift risk we explicitly called out as the reason to reject Option B.

**Rotation risk is live:** `DATABASE_URL` is manually set. If the Supabase password is rotated (manually or via breach response), Vercel production will break silently. Required mitigations:
1. Add a calendar reminder: check `vercel env ls production | grep DATABASE_URL` monthly
2. When rotating password: `vercel env rm DATABASE_URL production && vercel env add DATABASE_URL production --value <new-url>`
3. Long-term: re-attempt integration prefix fix or migrate to Supabase Branching (ADR-006)

**Revisit trigger (updated):** When Vercel Supabase integration prefix change is confirmed working, or when DATABASE_URL is verified to auto-sync on password rotation.

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** REVISIT (when Supabase Branching is enabled per ADR-006)

**Loki test:** The integration auto-detects the Supabase region but injects the wrong pooler hostname — `aws-0-us-east-1.pooler.supabase.com` instead of `aws-0-us-east-2.pooler.supabase.com` (ARCS project is us-east-2). Queries would fail silently at runtime with connection timeouts rather than an obvious error. Mitigation: verify `DATABASE_URL` value after first successful env pull with `vercel env pull .env.local --yes` and grep for the region string.

---

## Consequences

- Go to Vercel → Integrations → Supabase → ARCS project → set prefix to `DATABASE` → Save
- Run `vercel env pull .env.local --yes` → verify `DATABASE_URL` present and region matches `us-east-2`
- Re-run `vercel env ls production` to confirm `DATABASE_URL` appears in the project
- Then: `npx prisma db push` (per ADR-007) → trigger deploy

**Implementation pointer:** Vercel dashboard → team integrations page

---

## Linked receipts / ADRs

- ADR-002 — Database split (depends on: DATABASE_URL must be set for P4 deploy)
- ADR-006 — Supabase Branching (supersedes this when branching is enabled)
- ADR-007 — prisma db push vs migrate (blocked on this ADR)
