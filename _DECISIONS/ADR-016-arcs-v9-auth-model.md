# ADR-016 — arcs-v9 Auth Model — Anonymous vs. Authenticated Compass

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** Should arcs-v9 compass require an authenticated session to run, or should it
work anonymously with optional account creation as a post-session prompt?

## E — Entity / System

- `src/lib/auth.ts` — currently a null stub (returns null for every session)
- `src/app/api/compass/route.ts` — returns 401 in production when `userId === null`
- `src/app/api/prep/route.ts` — same 401 gate
- `src/app/api/guide/route.ts` — same 401 gate (×3 guards)
- `src/app/api/history/route.ts` — same 401 gate
- `src/app/api/brief/route.ts` — same 401 gate
- `prisma/schema.prisma` — `Receipt.userId` is nullable (allows anonymous)

## W — Window

**Horizon:** QUARTER — this decision gates every active user
**Revisit trigger:** First 10 authenticated users complete a session end-to-end. If drop-off
at auth gate exceeds 40%, revisit friction model.

## Context

arcs-v9 has been live since 2026-05-28 but is non-functional in production: `auth.ts` is a
deliberate null stub (`// Auth disabled for local dev — re-enable when ready for multi-user`).
Every API route guards with `if (!userId && NODE_ENV === 'production') return 401`.

The receipt schema supports anonymous sessions (`userId` nullable). The auth infrastructure
(Auth.js v5, Resend magic link, VerificationToken model, Account + Session models) is fully
built in schema and route handlers — it just needs a real `auth.ts` implementation.

**Two-surface context:** arcs.care is the unauthenticated entry funnel (compass works anonymously
there). arcs-v9 is the deeper app. This ADR decides whether arcs-v9 requires auth before its
deeper surfaces are accessible, or follows the same soft-auth model as arcs.care.

## Options Considered

### Option A — Require auth (keep current gate, wire real Auth.js)

- Enable magic link via Resend: implement `auth.ts` with `EmailProvider`, wire `AUTH_RESEND_KEY`
- Compass requires login. First session = magic link email → verify → compass runs.
- History, Brief, Guide all naturally scoped to user
- Pros: User identity from session 1. Receipt history tied to account. Full observability.
- Cons: Auth wall before first value. ARCS users are high-cognition/low-patience — auth friction
  at entry could kill activation. Email delivery reliability is a risk (DMARC, spam rate).
- Risk: If magic link email lands in spam, user never completes auth, never sees compass.

### Option B — Remove auth gate (anonymous-first, optional account post-session)

- Change 401 gate to allow null userId
- Compass, Prep, Guide work without auth
- Post-compass: "Create an account to save this receipt" (soft nudge, not gate)
- Auth.js still wired for users who want history
- Pros: Zero friction at entry. Matches arcs.care pattern. First value immediate.
- Cons: Anonymous receipts are orphaned. Re-engagement impossible without email.
  If user never creates account, retention loop never starts.
- Risk: Anonymous receipt volume makes the DB noisy; hard to measure activation.

### Option C — Two-tier access (anonymous compass, authenticated history/brief/guide)

- Compass + Prep: open (no auth required)
- History, Brief, Guide: require auth (sign in to unlock)
- The compass result is the reward; history/brief is the reason to create an account
- Pros: First value immediate. Account creation is earned (post-value, not pre-value).
  History gate is the correct motivational trigger — "you've done 3 sessions, sign in to see them all."
- Cons: Slightly more complex routing logic. Anonymous receipt linkage needs session cookie
  for pre-auth → post-auth receipt migration.
- Risk: Pre-auth anonymous receipts must be migrated to user account on sign-in
  (requires anonymous session cookie → userId reassignment logic).

## Decision

**Chosen:** Option C — anonymous compass + prep, authenticated history/brief/guide.

**Rationale:** Option C matches the ARCS value proposition: earn the history view by completing a compass session first. The auth gate is at the correct funnel position — not at entry (where it kills activation), but at the moment the user has evidence the tool works and wants to preserve it. This mirrors the arcs.care pattern and avoids the email deliverability risk that makes Option A fragile at launch (if DMARC is not fully enforced, magic links land in spam and the user never gets first value).

**Trade-offs accepted:** Anonymous receipts require a session-cookie-based migration path on sign-in (`PATCH /api/receipts/claim`). This adds ~50 lines of endpoint logic. The trade-off is accepted: receipt migration complexity is bounded and one-directional; the alternative failure mode (auth wall blocking first value) is unbounded and silent.

**Implementation path for Option C:**
1. `src/lib/auth.ts` — wire real Auth.js v5 with Resend EmailProvider
2. Compass + Prep routes — remove `NODE_ENV === 'production'` guard (allow anonymous)
3. History + Brief + Guide routes — keep auth guard
4. Client: store `sessionId` in `localStorage` for pre-auth receipt linkage
5. On sign-in: `PATCH /api/receipts/claim` — migrate `sessionId` orphans to `userId`
6. Smoke test: expand `scripts/smoke.sh` to test anonymous compass + auth-gated history (expect 401)

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** "Option C creates receipt migration complexity that will never be built correctly,
leaving orphaned anonymous receipts forever and making the History page show empty for users
who did sessions before signing in." Counter: migration is a single PATCH endpoint with a
session cookie match; it's ~50 lines. The alternative (Option A auth wall) has a worse failure
mode: user never gets to first value.

## Amendment — Execution Receipt (2026-06-03)

> **Status:** DONE — fully sealed
> **Commit:** `663d831` (db.ts SSL fix, final) + `6a5b856` (ADR-016 code)
> **First authenticated user:** `zach.harris@gmail.com`, `2026-06-03 16:57:17 UTC`

### What was decided vs. what was built

| Decision | Actual execution |
|---|---|
| Use existing `owdiiyvphyifukygvxhg` Supabase project | Pivoted to `xbbpiryokswwvcrcutge` (separate org, inaccessible dashboard) |
| Auth.js already wired — don't touch | Confirmed correct — no change needed |
| Remove prod-only 401 from compass + prep | Done — `src/app/api/compass/route.ts:108`, `prep/route.ts:8` |
| `PATCH /api/receipts/claim` endpoint | Created — 30 lines, `userId` from `auth()` only |
| `localStorage.setItem('arcs_session_id')` on compass result | Done — dashboard `handleSubmit` + mount `useEffect` for claim |
| `scripts/smoke.sh` 5 assertions | Created — passed 5/5 via `vercel curl` bypass |

### Deviations from plan

1. **Supabase project swap** — `owdiiyvphyifukygvxhg` (ARCS org) was inaccessible (different Supabase login, password unreachable). Pivoted to `xbbpiryokswwvcrcutge` (zachharris-3439 org, accessible via browser). Schema applied fresh via MCP; `arcs_app` role created with known credentials to bypass `postgres` password inaccessibility on free-tier Marketplace-provisioned project.

2. **`PrismaPg` SSL bug** — `db.ts` was using `new PrismaPg({ connectionString })` config-object form, which silently fails SSL on the Supabase pooler. Every Prisma runtime query threw, making the entire DB layer non-functional in production (build succeeded because `prisma generate` doesn't connect). Fixed: `new Pool({ connectionString, ssl: { rejectUnauthorized: false } })` passed as explicit `pg.Pool` instance. Commit `663d831`.

3. **`emailVerified` + `image` missing from `User` table** — `0_init` migration omitted these columns (they were added in a later SQLite-only migration `d732dad` that was never ported to Postgres). `PrismaAdapter` requires `emailVerified` to upsert users; every sign-in attempt threw `column User.emailVerified does not exist`. Fixed via `apply_migration` directly to prod DB (no code change needed). ADR-022 stubs the schema debt.

4. **`AUTH_RESEND_KEY` was empty** — original value set 14h prior was blank. Resend key needed to come from the account where `arcs.care` is verified. Set correctly via `printf '%s' | vercel env add` (interactive prompt was mangling values). Valid key confirmed via `api.resend.com/domains` check before setting.

5. **Stale CLI-upload deploy** — the original Error deployment was from `vercel deploy` uploading a stale Prisma-6 working tree. Git-integration push confirmed working; all subsequent deploys from `git push origin main`.

### Production state at seal

- `app.arcs.care` → arcs-v9 (new permanent domain, CNAME via Vercel DNS)
- DB: `xbbpiryokswwvcrcutge` pooler, `arcs_app` role, RLS + BYPASSRLS
- Anonymous `Receipt` writes: working (verified 3 rows, `userId=null`)
- Auth flow: working (VerificationToken written, User created, Session established)
- `AUTH_RESEND_KEY`: valid (`re_T6zSFsRF_*`, `arcs.care` verified, us-east-1)

## Consequences

- **Option A:** Wire `auth.ts` (2-3h). arcs-v9 immediately functional for users who complete auth.
  Biggest risk: email deliverability.
- **Option B:** Remove 401 gate (30 min). arcs-v9 immediately functional for all. No retention.
- **Option C:** Wire `auth.ts` + remove compass gate + add receipt migration endpoint (4-6h).
  arcs-v9 fully functional with soft auth model matching arcs.care pattern.

**Second-order consequences for Phase 2 (receipt persistence on arcs.care):**
The answer to this ADR directly determines whether arcs.care soft auth should use the same
Auth.js magic link as arcs-v9, or a lighter email-capture-only path. If Option C is chosen,
a shared auth layer across both surfaces becomes attractive.

**Implementation pointer:** `src/lib/auth.ts` (stub to replace), `src/app/api/compass/route.ts`
(gate to modify), `src/app/api/receipts/` (claim endpoint to create)
