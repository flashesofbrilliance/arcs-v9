# ARCS Session State

**Last updated:** 2026-05-28
**Last commit (arcs-v9):** 2aa6904 — ADR-005/007 amendments; P4 READY

## Status

- Book II Parts I–VI: ALL CANONICAL ✅
- _DECISIONS/: ADR-001 through ADR-007 live on GitHub ✅ (ADR-005/007 amended with actual execution)
- arcs-v9 Vercel: ✅ FIRST READY DEPLOY — `arcs-zachharris-3439s-projects.vercel.app`
- arcs-care working tree: CLEAN ✅
- arcs-v9 working tree: CLEAN ✅
- Supabase schema: ✅ 9 tables, 0 rows, `_prisma_migrations` seeded with `0_init`

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP deploy | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P4: arcs-v9 → Vercel | ✅ DONE | First READY deploy confirmed |
| P3: arcs-care PLG funnel | 🟡 Specced | Phase 1 next: compass model swap + Lab CTA |

## What's still open (post-P4 cleanup)

1. **Preview DATABASE_URL missing** — add via Vercel dashboard: Settings → Environment Variables → `DATABASE_URL` → Preview → All branches (CLI v53 bug prevents CLI add)
2. **RLS disabled** on all 9 Supabase tables — enable before first external user; requires RLS policies first
3. **DATABASE_URL rotation risk** — Option B (manual) is live, not Option A (integration). See ADR-005 amendment. Set calendar reminder.
4. **Supabase direct connection failing locally** — `db push` / `migrate resolve` can't connect from local machine. All DDL must go through Supabase MCP until resolved.
5. **AUTH_SECRET missing from Preview env** — verify magic link auth works on the live production deploy

## P3 arcs-care Phase 1 next steps

```
1. app/api/compass/route.ts — remove retired model from fallback chain
2. app/compass/page.tsx — add Lab Offer Card post-result (receipt_id in CTA link)
3. components/lab-offer.tsx — accept receiptId prop, update link to /call?receipt=
4. Verify: POST /api/compass → receipt_id in response; Lab CTA renders
```

## ADR queue state

| ADR | Status |
|---|---|
| 001 | DONE |
| 002 | DONE (Prisma 7 / Supabase live) |
| 003 | DONE (COCD hero + loop diagram) |
| 004 | DONE (mcp.arcs.care live) |
| 005 | DONE — amended: Option B live, rotation risk documented |
| 006 | BLOCKED — gate: first external user or schema PR |
| 007 | DONE — amended: bootstrap via MCP, baseline registered |
| TBD | NEEDED — RLS policy design (pre-first-user gate) |

## Blocking

NO human blockers for current deploy. Two recommended actions:
1. Vercel dashboard → add `DATABASE_URL` to Preview environment (all branches)
2. Set calendar reminder: check `vercel env ls production | grep DATABASE_URL` monthly (rotation risk)
