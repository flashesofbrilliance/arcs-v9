# ARCS Session State

**Last updated:** 2026-05-28 (v2.1.0)
**Last commit (arcs-v9):** 44f40b2 — docs(adr): seal ADR-015/016/017; stub ADR-018 as HELD
**Last commit (arcs-care):** a5dcffc — feat(lab): case study receipt excerpt env-flagged

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

1. **ADR-016 implementation** — unblocked: wire `src/lib/auth.ts` (Auth.js v5 Resend EmailProvider) + remove compass 401 gate + add `/api/receipts/claim` endpoint
2. **DMARC enforcement** — `dig TXT _dmarc.arcs.care` — if monitor-only, emails are in spam. Fix: `p=quarantine` → `p=reject`
3. **30-day calendar reminder** — 2026-06-27 (ADR-013 conversion trigger watchdog; case study shipped 2026-05-28)
4. **Add `compass_receipt_id` column** to Supabase `waitlist` table (soft-auth reconciliation)
5. **Preview DATABASE_URL (arcs-v9)** — add via Vercel dashboard (all branches; CLI v53 bug)
6. **Define "Lab inquiry"** — what counts? DM / email / form submit
7. **ADR-018 Architect packet** — paste Architect prompt (in session transcript) into Perplexity Space ARCS; bring packet back to unblock /helpful rebuild

## Design system debt (arcs-v9)

- Panel component — next after Badge/Button/Card (3 of 8 barrel trigger threshold)
- Chip component — after Panel
- ADR-011 revisit at 8 components; currently at 3

## arcs-care open items

- Second Vercel Toolbar thread `YyvHp8_-4jXX` — API investigation ("Is the API working?") — NOT resolved
- Spots badge hardcoded `SPOTS_REMAINING = 10` — update manually or wire Supabase counter
