# ARCS Session State

**Last updated:** 2026-05-27
**Last commit:** 7869e26 — PENDING.md updated; all repos clean + pushed

## Status

- Book II Parts I–VI: ALL CANONICAL ✅
- _DECISIONS/: ADR-001 through ADR-007 live on GitHub ✅
- arcs-care COCD hero: COMMITTED + PUSHED (`0240f18`) ✅
- Working tree (arcs-v9): CLEAN ✅
- Working tree (arcs-care): CLEAN ✅
- Working tree (perplexity-mcp): CLEAN ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP deploy | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P4: arcs-v9 → Vercel preview | 🔴 BLOCKED | Fix Vercel Supabase integration prefix: `DATABASE` (not `STORAGE`) → env pull → prisma db push → deploy |

## P4 exact next steps (unblock sequence)

```
1. Vercel dashboard → Integrations → Supabase → ARCS project
   → set Custom Environment Variable Prefix to: DATABASE
   → Save Changes

2. vercel env pull .env.local --yes
   → verify DATABASE_URL appears + check region string contains "us-east-2"

3. npx prisma db push
   → pushes v9 schema to Supabase (all tables empty — safe)

4. npx prisma migrate diff \
     --from-schema-datasource prisma/schema.prisma \
     --to-schema-datamodel prisma/schema.prisma \
     --script > prisma/migrations/0_init.sql
   npx prisma migrate resolve --applied 0_init
   → baseline migration (ADR-007 step 2)

5. git add prisma/migrations/ && git commit + push

6. vercel deploy (or push triggers auto-deploy)
   → watch for first READY deployment
```

## ADR queue state

| ADR | Status |
|---|---|
| 001 | DONE — `25e76e8` |
| 002 | IN_PROGRESS — code fixed, waiting on Vercel integration |
| 003 | DONE — hero + loop diagram committed to arcs-care (`0240f18`) |
| 004 | DONE — mcp.arcs.care live |
| 005 | READY — manual dashboard action (fix prefix) |
| 006 | BLOCKED — gate: first external user or schema PR |
| 007 | BLOCKED — needs ADR-005 first |

## New capabilities added this session

- `~/.claude/commands/ultrareview.md` — `/ultrareview` DEWY-native ADR quality gate
- `~/arcs-care-local/components/loop-diagram.tsx` — COCD SVG loop diagram component

## Blocking

**ONE human action required:** Vercel dashboard → fix Supabase integration prefix to `DATABASE`.
Everything else (prisma db push, baseline migration, deploy) can be done by Claude Code once that fires.
