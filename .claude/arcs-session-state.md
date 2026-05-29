# ARCS Session State

**Last updated:** 2026-05-28 (v1.9.0)
**Last commit (arcs-v9):** c8b2eb5 — ADR-014 + ADR-015 committed
**Last commit (arcs-care):** a3f08f1 — fix: smoke curl -f flag

## Status

- arcs-v9 Vercel: ✅ LIVE — `arcs-zachharris-3439s-projects.vercel.app`
- arcs-care: ✅ LIVE — arcs.care
  - PLG Phase 1: ✅ SHIPPED (5-lens compass, Lab Offer Card)
  - CI/CD pipeline: ✅ SHIPPED (ESLint, GitHub Actions, smoke tests, NOTOMATION circuit breakers)
  - Vercel Toolbar: ✅ INSTALLED
  - ADR-013 Week 1 builds: 🔴 NOT STARTED (item 1 content-blocked; items 2+3 unblocked)
- Supabase (owdiiyvphyifukygvxhg): 9 tables, RLS ✅ APPLIED (2026-05-27)
- ADRs: 001–015 in arcs-v9/_DECISIONS/; ADR-015 is DRAFT (decision field: FILL IN)
- All repos pushed to GitHub ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P4: arcs-v9 → Vercel | ✅ Done | First READY deploy 2026-05-28 |
| P5: arcs-care PLG Phase 1 | ✅ Done | Lab Offer Card + 5-lens compass live |
| P5-ci: arcs-care CI/CD | ✅ Done | NOTOMATION circuit breakers live |
| P5-conversion: ADR-013 | 🟡 Specced | Week 1 builds 2+3 unblocked; item 1 content-gated |

## Requires human action (priority order)

1. **Resolve ADR-015** — confirm: is a founding client outcome shareable? If no → skip to items 2+3
2. **Verify DMARC** — `dig TXT _dmarc.arcs.care` — if monitor-only, emails are in spam. CRITICAL.
3. **Add `compass_receipt_id` column** to Supabase `waitlist` table (for soft-auth reconciliation)
4. **Define "Lab inquiry"** — what counts for the 30-day signal? DM, email, form submit?
5. **Set 30-day calendar reminder** from case study ship date (Option C promotion watchdog)
6. **Vercel Preview env (arcs-v9)** — add DATABASE_URL to Preview via dashboard (CLI v53 bug)

## arcs-care CI/CD topology (for next session orientation)

```
push/PR → ci.yml (lint + build) → gate merge
              ↓ (on Vercel build fail)
         vercel-ai-fix.yml → Claude Code diagnoses + fixes → preview deploy → smoke → Decision Receipt
              ↓ (human reviews receipt)
         promote.yml (workflow_dispatch ONLY) → SIGNAL_PROMOTE_GATE → prod promote → smoke
```

Named circuit signals:
- SIGNAL_PROMOTE_GATE — prod promote requires workflow_dispatch
- SIGNAL_SURFACE_BREACH — fix >3 files / >50 lines / auth/compass touch → human review
- SIGNAL_SCHEMA_DRIFT — compass API contract broken on valid payload
- SIGNAL_ENV_DRIFT — smoke fails post-promote → human diagnoses
- SIGNAL_FIX_LOOP — same failure auto-fixed >2× → escalate

## ADR-013 Week 1 build queue (next session)

```
Item 2 — Email capture on compass result        UNBLOCKED — start now
  compass-widget.tsx: optional field below result panel
  Copy: "Want Zach to send a note on this? One message, no list."
  Reuse /api/waitlist with source: 'compass-result'
  Remove "No email required" from result state only (keep on form state)
  Tag with compass_receipt_id (if column added)

Item 3 — Spots badge elevation in hero          UNBLOCKED — 2h CSS/JSX
  hero.tsx: move "6 of 10 founding spots remaining"
  From: microcopy → To: badge with pulsing dot, above CTA buttons

Item 1 — Case study receipt excerpt             BLOCKED on content
  lab-offer.tsx: above Lab CTA
  Gate: founding client decision + outcome + permission to share
```

## arcs-v9 design system debt (non-urgent)

- Panel component — next after Badge/Button/Card
- Chip component — after Panel
- Barrel trigger fires at 8 components (ADR-011); currently at 3
