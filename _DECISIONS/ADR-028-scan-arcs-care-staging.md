# ADR-028 — Profile Scan staging route (`/scan`, mock-first, behind `SCAN_ENABLED`)

**Status:** DECIDED (implementation), DEFERRED (canonical content model — see Open questions)
**Date:** 2026-06-24
**Author:** delegated subordinate (Claude Code), executing the TEI-budgeted plan from the
2026-06-24 Profile Scan Spec v1 session.

## D — The Decision

Stand up `/scan` in this repo as a flag-gated, mock-data-only render of the canonical
`profile` document type (`src/document/screens/ProfileScan.tsx`), as the staging surface
for an eventual `scan.arcs.care` subdomain.

**Build now (cheap, mechanical, unblocked):**
- `src/lib/flags.ts` — `scanEnabled` flag, default OFF (`SCAN_ENABLED=true` to render)
- `src/app/scan/page.tsx` — `notFound()` when flag is off; otherwise renders `<ProfileScan />`
  with its own built-in `PROFILE_SAMPLE` mock data (no new mock file needed — the screen
  component already ships a complete sample, confirmed by reading
  `src/document/screens/ProfileScan.tsx`)

**Explicitly NOT built this session (per the TEI plan's own allocation — negative-EV or Zach-cost):**
- A generation pipeline (LinkedIn PDF/export → populated `ProfileScanResponse`) — unscoped,
  separate spec (`runtime/flows/profile-scan-flow-v0.1.md`, not yet written)
- The `mode=` (recruiting/partnership/relationship) and `audience-direction`
  (internal/external) param enums — inferred from 3 Gamma docs this session, not confirmed
  canon; routed to Zach as a decision, not guessed into a schema here
- Any amendment to ADR-020/ADR-023's receipt-count gate — flagged only, not changed
- Porting/committing `arcs_cfa`'s `linkedin_export.py`/`primitives.py` changes — separate
  repo, separate disposition decision, left untouched per "leave alone for now"

## E — Entity / System

- `src/lib/flags.ts` — new `scanEnabled` flag
- `src/app/scan/page.tsx` — new route
- `src/document/screens/ProfileScan.tsx` — existing, unmodified; confirmed (Assumption B1,
  resolved 2026-06-24) as the canonical, in-repo, committed source for the `profile`
  document type — not a Downloads-folder orphan
- `src/document/registry.ts` — existing `DOC_TYPES['profile']` entry, unmodified

## W — Window / Why now

The standing build checklist ("land the plane on the profile scan so I can stage a
scan.arcs.care subdomain") was blocked only on Assumption B1 (was `patterns.jsx`'s
in-repo port actually the real build target?). That assumption resolved DONE
2026-06-24 — `src/document/` is committed, faithfully ported, demoed at `/design-test`.
With the blocker cleared, this slice of the checklist is cheap and mechanical: render an
existing component behind an existing flag pattern. Per the TEI plan's own math, this is
exactly the kind of item the plan said should still happen (mechanical, downshift-eligible,
not resting on an unconfirmed foundation) — distinct from the full Phase 1–7 build (schema,
generation pipeline, mode/audience params), which the same plan correctly flags as
negative-EV until the Zach-cost decisions below land.

## Y — Y-gate

GREEN/HIGH/STABLE for the implementation slice above — purely additive, flag-defaulted-off,
zero runtime risk to any existing route, build-verified clean (`npx next build`, all 15
routes including `/scan` compiled and prerendered).

YELLOW/MEDIUM/HOLD for the canonical content model (mode enum, audience-direction enum,
term-collision resolution for Thread/Signal/5D/Genome) — explicitly not decided here, routed
to Zach per the TEI plan's "route unblocking decisions as cheap questions" allocation.

## Open questions — RESOLVED 2026-06-25 (Zach)

1. ~~`mode=` enum~~ — **LOCKED**: `recruiting-eval` / `partnership-eval` / `relationship-building`,
   as inferred from the 3 Gamma docs. Refine later only if a 4th mode shows up in practice.
2. ~~`audience-direction`~~ — **LOCKED**: `internal` / `external` is the complete enum.
3. ~~`arcs_cfa` disposition~~ — **PORTED**: `linkedin_export.py` + `primitives.py`
   (jerk/`pre_peak_warning` included) copied into `operators/linkedin_pipeline/` in this
   repo, sourced from `arcs_cfa` commit `fd6ea07`. `arcs_cfa`'s own copies left in place
   (port, not move) until the generation pipeline confirms arcs-v9 is the sole consumer.
   Not yet wired into any route — parser/primitive layer only.

## Still open (not asked this round)

4. Whether to pursue the inbound-email-PDF-attachment path (Resend inbound parse) as an
   alternative to an upload UI for the eventual generation pipeline

## Consequences

- `/scan` is live in the build graph but returns 404 in every environment until
  `SCAN_ENABLED=true` is set — no behavior change to any deployed environment from this
  commit alone.
- When `scan.arcs.care` is ready to stage, set `SCAN_ENABLED=true` on that environment only
  (Preview or a dedicated Vercel env), not Production — keeps the mock surface off the main
  domain.
- Next real increment is the generation pipeline spec, which depends on the four Zach-cost
  decisions above landing first.
