# ARCS Session State

**Last updated:** 2026-05-28 (v2.0.0)
**Last commit (arcs-v9):** 6ae6582 — ADR-009/011/012 ultrareview patches + PLG Phase 1 decided
**Last commit (arcs-care):** a54e5dd — P5 model swap + conviction-gated Lab card

## Status

- arcs-v9 Vercel: ✅ LIVE — `arcs-zachharris-3439s-projects.vercel.app`
- arcs-care: ✅ LIVE — arcs.care
  - PLG Phase 1: ✅ SHIPPED — `claude-sonnet-4-6` model + conviction-gated Lab card (NCI≥65)
  - Lab card href: `/call?receipt=${receipt_id}` ✅
  - CI/CD pipeline: ✅ LIVE (NOTOMATION circuit breakers)
  - Case study (Dan Pascone): ✅ LIVE — env-flagged via `NEXT_PUBLIC_CASE_STUDY_APPROVED`
  - Email capture on compass result: ✅ LIVE
  - Spots badge elevation: ✅ LIVE
- ANTHROPIC_API_KEY: ✅ ROTATED — new key synced to all 3 Vercel envs (Prod/Preview/Dev)
- Supabase (owdiiyvphyifukygvxhg): 9 tables, RLS ✅ APPLIED (2026-05-27)
- ADRs: 001–018 range in arcs-v9/_DECISIONS/ (ADR-016/017 sealed; ADR-018 HELD)
- All repos pushed to GitHub ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P4: arcs-v9 → Vercel | ✅ Done | First READY deploy 2026-05-28 |
| P5: arcs-care PLG Phase 1 | ✅ Done | Model swap + conviction-gated Lab card live |
| P5-ci: arcs-care CI/CD | ✅ Done | NOTOMATION circuit breakers live |
| P5-conversion: ADR-013 | ✅ Done | Week 1 items 1+2+3 all shipped |

## ADR ledger (from /receipt-book-curator this session)

| ADR | Status | Y |
|---|---|---|
| 001–005 | ✅ DECIDED | GREEN/HIGH/STABLE or REVISIT |
| 006 | YELLOW/MEDIUM/STABLE | Deferred — gate: first external contributor PR |
| 007–010 | ✅ DECIDED | GREEN/HIGH/STABLE |
| 011 | ✅ DECIDED | GREEN/MEDIUM/REVISIT (Turbopack unconfirmed) |
| 012 | ✅ DECIDED | YELLOW/MEDIUM/REVISIT |
| 013–017 | ✅ DECIDED/SEALED | varies |
| 018 | HELD | — |

## Requires human action (priority order)

1. **Verify end-to-end on production** — hit arcs.care/compass with real question; confirm NCI≥65 Lab card renders + href correct
2. **DMARC enforcement** — `dig TXT _dmarc.arcs.care` — if monitor-only, emails are in spam. Fix: `p=quarantine` → `p=reject`
3. **Add `compass_receipt_id` column** to Supabase `waitlist` table (soft-auth reconciliation)
4. **Preview DATABASE_URL (arcs-v9)** — add via Vercel dashboard (all branches; CLI v53 bug)
5. **30-day signal watchdog** — calendar reminder from case study ship date (ADR-013 Option C trigger)
6. **Define "Lab inquiry"** — what counts? DM / email / form submit

## Design system debt (arcs-v9)

- Panel component — next after Badge/Button/Card (3 of 8 barrel trigger threshold)
- Chip component — after Panel
- ADR-011 revisit at 8 components; currently at 3

## arcs-care open items

- Second Vercel Toolbar thread `YyvHp8_-4jXX` — API investigation ("Is the API working?") — NOT resolved
- Spots badge hardcoded `SPOTS_REMAINING = 10` — update manually or wire Supabase counter
