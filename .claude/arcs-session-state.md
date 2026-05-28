# ARCS Session State

**Last updated:** 2026-05-28 (v1.7.0)
**Last commit (arcs-v9):** b995a63 — handoff v1.6.0 (design system Phase 1, ADRs 009-012)
**Last commit (A.R.C.S.):** af3c303 — ADR-010 Loki fix (rename notice in arcs_dewy_log.py)
**Last commit (arcs-care):** 94a0ab8 — hw-button-orange flat fill fix

## Status

- arcs-v9 Vercel: ✅ LIVE — `arcs-zachharris-3439s-projects.vercel.app`
- arcs-care: ✅ LIVE — PLG Phase 1 shipped (Lab Offer Card, model chain, lens readings)
- Supabase (owdiiyvphyifukygvxhg): 9 tables, RLS policies WRITTEN not yet APPLIED
- ADRs: 001–012 committed in arcs-v9; ADR-008 status = ACCEPTED (not APPLIED)
- A.R.C.S. receipt book: 01×3, 02×3, 03×3, 04×2, 05×4, 06×3 — P1+P2 pass done
- arcs_dewy naming collision: ✅ RESOLVED (ADR-010) — `_HAS_DEWY = True`
- All repos pushed to GitHub ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P4: arcs-v9 → Vercel | ✅ Done | First READY deploy 2026-05-28 |
| P5: arcs-care PLG Phase 1 | ✅ Done | Lab Offer Card + model chain live |

## Requires human dashboard action (no code blocker)

1. **Apply RLS** — paste `arcs/scripts/rls-policies.sql` into Supabase SQL Editor (project `owdiiyvphyifukygvxhg`), then edit `_DECISIONS/ADR-008-rls-policy-design.md`: `status: ACCEPTED` → `status: APPLIED`, commit
2. **Vercel Preview env** — Settings → Environment Variables → add `DATABASE_URL` (Preview, all branches) + `AUTH_SECRET` (Preview) via dashboard (CLI v53 bug blocks CLI add)
3. **Calendar reminder** — monthly check on DATABASE_URL rotation risk (Option B manual, ADR-005)

## Phase 7 open code items (priority order)

1. **receipt-core schema** — unifies BriefReceipt/GuideReceipt/DecisionReceipt; blocks CLUE, NGI, CLI
2. **Receipt Book P3** — quality_score pass on 11 unsealed receipts (`arcs_dewy/helpers/quality_scorer.py`)
3. **CLUE integration** — receipt lifecycle events; blocked on receipt-core
4. **NGI linking** — `receipt_id` on no-go entries; blocked on receipt-core
5. **CLI commands** — `arcs receipt log/inspect/export`

## Known structural notes

- Supabase direct connection (port 5432) still failing from local — all DDL via Supabase MCP
- DATABASE_URL = pooler port 6543 (Prisma 7 + PrismaPg adapter)
- A.R.C.S. has no GitHub remote (local-only runtime, expected)
- `arcs_dewy_log.py` (DEWYLog/DEWYEntry) has zero callers — deferred consolidation into package

## Blocking

NONE. All code items unblocked. Human dashboard actions (A1–A3) are the only open gates.
