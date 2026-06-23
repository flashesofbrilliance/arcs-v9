# ARCS Session State

**Last updated:** 2026-06-23 (v3.0.0)
**Environment:** Claude Code (local), worktree `claude/dreamy-ardinghelli-56bbfa`
**Branch:** `claude/dreamy-ardinghelli-56bbfa` → merged to `main`
**Last commit (arcs-v9):** 69250b4 — Merge branch 'claude/dreamy-ardinghelli-56bbfa'

## Status

- arcs-v9 Vercel: ✅ LIVE — production deploy Ready, serves **app.arcs.care, www.arcs.care, arcs.care,
  resume.arcs.care** (all one deployment — see Domain correction below)
- arcs-v9 Auth: ✅ magic link fully wired (ADR-016 RESOLVED this session — was open as of the prior
  update). `AUTH_SECRET` confirmed present on BOTH Production and Preview (also resolved — prior
  update flagged it missing on Preview).
- arcs-v9 DB: unchanged — `xbbpiryokswwvcrcutge` / postgres / port 6543 pooler, manual URL parsing
  in `db.ts` (password contains `!`)
- DATABASE_URL: confirmed present on both Production and Preview via `vercel env ls` (this resolves
  another long-standing open item from the global CLAUDE.md P-track)
- CRON_SECRET: new, added ~17h before this snapshot, for `/api/cron/debrief` (ADR-026)
- arcs-care project: ⚠️ now confirmed `live: false` — see Domain correction below

## ⚠️ Domain correction (read this first if picking up cold)

`arcs.care` is **not** a separate site from `app.arcs.care`. Confirmed via `get_deployment`:
both domains (plus `www.arcs.care`, `resume.arcs.care`) alias to *this* repo's production
deployment. The standalone `arcs-care` Vercel project (codebase `~/arcs-care-local`, its own
instrument-panel `/compass` UI + PLG funnel) is inactive — `live: false`. Any "public arcs.care
surface" work belongs in this repo. Full detail + the verification habit going forward: see
`~/.claude/CLAUDE.md` and project memory `arcs-v9-arcs-care-domain-consolidation.md` /
`verify-domain-topology-live-not-from-memory.md`.

## What landed this session (2026-06-23)

S-tier copy rewrite (Home/CompassForm/Brief/prep/emails — retired "L0–L5 pipeline,"
"boardroom-grade," "Cartography Brief," "render through the fog" from all user-facing copy);
FATED grid color-coded per axis; Brief layout restructured (8 Vercel toolbar threads resolved);
**accessibility fix** in `Field.tsx` (every form field now gets a real id/name, was missing
app-wide); 3 real bugs fixed in `ReflectLayer.tsx` (kernel-loss-on-harden, meditate toggle state,
shavasana rebuilt as inline carousel); Vercel CLI upgraded 54.7.1→54.14.5; `vercel.json`→`vercel.ts`
migration started but **left incomplete and unmerged** (see Blocking); full audit of the
domain-topology correction above; audited stale local clone `/Users/zharris/arcs` (2 of 3 orphaned
commits superseded, 1 — full interactive Observatory page — genuinely recoverable, not yet done).

Full detail: `MEMORY.md` `[v3.0.0]` entry, `CLAUDE.md` `# Handoff — v3.0.0`.

## Open items (re-verified 2026-06-23)

```
1. ADR-016 auth.ts wiring                                  RESOLVED — fully wired, confirmed
                                                             working live via agent-browser
2. AUTH_SECRET missing on Preview                           RESOLVED — present on both envs now
3. DATABASE_URL missing on Preview                          RESOLVED — present on both envs now
4. DMARC monitor-only                                        RESOLVED — p=quarantine confirmed
5. vercel.ts migration                                      🔴 INCOMPLETE — main's vercel.json has
                                                             experimentalServices (this project's
                                                             Framework Preset is "Services", not
                                                             autodetected Next.js — see Key infra
                                                             facts) + crons that vercel.ts doesn't
                                                             represent. Aborted mid-merge rather
                                                             than risk dropping either silently.
6. Observatory full interactive page                        🟡 RECOVERABLE — orphaned commit
                                                             35070a3 in stale /Users/zharris/arcs
                                                             clone, never pushed, not superseded
7. Trust contract page                                      🟡 NOT STARTED — _CANON/trust-contract.md
                                                             exists on main but isn't surfaced
                                                             anywhere live; this repo is now
                                                             confirmed the right place for it
8. DATABASE_URL rotation risk (ADR-005 amendment)            OPEN — could not re-verify, Supabase
                                                             MCP was disconnected mid-session
9. Validate SAGE NCI against real with-SAGE Outcomes        OPEN — carried over, infra ready
                                                             (SageTrace + sage_efficacy.js), still
                                                             genuinely no data yet
10. Panel/Chip design system components (ADR-009)            READY — carried over, untouched
11. ADR-006 branching strategy (first-external-user gate)    READY — carried over, untouched
12. arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED          WAITING on Dan Pascone — carried over,
                                                             though note: arcs-care isn't live on
                                                             any domain right now regardless (#8
                                                             Domain correction)
```

## Key infra facts (for next session)

- DB: `xbbpiryokswwvcrcutge` / database `postgres` / port 6543 pooler — manual URL parsing in
  `db.ts` (password contains `!`)
- Vercel project: `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9` / team `zachharris-3439s-projects`
- **Framework Preset is Services** (project-wide, not per-environment) — do not revert this.
  This is *why* `vercel.json` currently has an `experimentalServices` block (the Python `sage`
  microservice route) that the in-progress `vercel.ts` migration doesn't yet represent — confirm
  `@vercel/config`'s typed schema actually supports this advanced/unusual setting before
  re-attempting the migration.
- The actual Vercel CLI binary is a Homebrew install (`vercel-cli` formula at
  `/opt/homebrew/bin/vercel`) — a separate `npm i -g vercel` install exists and gets shadowed in
  `PATH`. Upgrade via `brew upgrade vercel-cli`, not `npm i -g vercel@latest`, or you'll upgrade
  the wrong one and see no version change.
- `/Users/zharris/arcs` is a STALE abandoned clone of this same repo (last commit 2026-06-07) —
  do not use it as a working directory, but it does have one recoverable orphaned commit (see
  Open items #6).
- `arcs_readonly` Postgres role exists for read-only analysis scripts — needs `BYPASSRLS` granted
  (already done) or it will silently see 0 rows under this project's RLS deny-all policies
- `next.config.ts` must keep `turbopack: { root: __dirname }`
- `vercel deploy` (CLI) does NOT attach git-branch metadata — any env var scoped to a specific
  git-branch silently never applies to a CLI-triggered deploy. Scope to "all preview branches"
  unless deploys are git-push-only.

## Prior session highlights (2026-06-19 → 2026-06-21, compressed — full detail in MEMORY.md history)

- SAGE efficacy infra shipped: `SageTrace` table (invisible by construction, never `include`d),
  `scripts/sage_efficacy.js` comparing with/without-SAGE Outcomes, gated at n=20/group
- NCI self-grade rubric (Factual/Sources/Honesty/Action) wired into the live system prompt +
  new `nciSelfGrade` Receipt column — verified genuinely substantive (caught real issues in live
  tests, not performative)
- Found + fixed a real bug: `decision_mode`/`door_class` were silently overwritten by Claude's
  own echoed values in the API response (`...parsed` spread order bug)
- Read-only Postgres role `arcs_readonly` added for analysis scripts — hit and documented the
  "table GRANT SELECT isn't enough under RLS deny-all, need explicit BYPASSRLS" gotcha
- Root-caused and fixed a `DATABASE_URL` auth failure: `!` in the Supabase password was mishandled
  by `pg`'s connection-string URL parser — fixed via manual `new URL()` parsing in `db.ts`

## Next session

`/handoff-pickup` → pick one: trust-contract page on arcs-v9, Observatory commit cherry-pick, or
finish the vercel.ts migration properly (port `experimentalServices` + `crons` first). SAGE
efficacy validation needs no action — just time and real usage. Re-verify DATABASE_URL rotation
status once Supabase MCP reconnects.
