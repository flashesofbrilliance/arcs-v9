# ARCS Session State

**Last updated:** 2026-05-28 (v1.5.0)
**Last commit (arcs-v9):** 924fd10 — tokens.ts + Badge component

## Status

- Book II Parts I–III+VI: CANONICAL ✅ | Part IV: DRAFT | Part V: NOT STARTED
- _DECISIONS/: ADR-001 through ADR-009 committed; ADR-010 UNTRACKED (needs commit)
- arcs-v9 Vercel: ✅ LIVE — `arcs-zachharris-3439s-projects.vercel.app`
- Supabase: ✅ 9 tables, RLS enabled (deny-all), `_prisma_migrations` seeded
- arcs-care: ✅ LIVE — COCD hero, loop diagram, Compass + /helpful

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P1: arcs-hq archive | ⏳ Not started | No blocker |
| P2: Perplexity MCP | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P3: Home dir cleanup | 🔒 Hard gate | Audit 51 ahead-of-origin commits first |
| P4: arcs-v9 → Vercel | ✅ Done | First READY deploy 2026-05-28 |
| P5: arcs-care PLG Phase 1 | 🟡 Specced | Compass model swap + Lab offer card |

## Open uncommitted items

1. `src/app/dashboard/page.tsx` — Badge smoke test (marked "remove after visual confirmation")
2. `_DECISIONS/ADR-010-arcs-dewy-pkg-rename.md` — drafted, untracked

## Post-P4 cleanup (still open)

1. **Preview DATABASE_URL** — add via Vercel dashboard (all branches)
2. **RLS policies** — deny-all is live; need real user-scoped policies before launch
3. **DATABASE_URL rotation risk** — manually set, see ADR-005 amendment
4. **Supabase local connection broken** — db push / migrate fail locally; use MCP for DDL

## P5 arcs-care Phase 1 next steps

```
1. app/api/compass/route.ts — remove retired model from fallback chain
2. app/compass/page.tsx — add Lab Offer Card post-result (receipt_id in CTA link)
3. components/lab-offer.tsx — accept receiptId prop, link to /call?receipt=
4. Verify: POST /api/compass → receipt_id in response; Lab CTA renders
```

## Blocking

NONE. Two recommended human actions:
1. Vercel dashboard → add DATABASE_URL to Preview (all branches)
2. Calendar reminder: check DATABASE_URL monthly (rotation risk per ADR-005)
