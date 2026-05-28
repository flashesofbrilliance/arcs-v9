# Implementation Queue

> Auto-maintained by `.github/workflows/adr-queue.yml`
> Read by `/arcs-handoff-pickup` at session start
> Status: READY | BLOCKED | IN_PROGRESS | DONE

| ADR | Title | Pointer | Status | Horizon | Conviction |
|-----|-------|---------|--------|---------|------------|
| 001 | Auth gate: app-level (not RLS) | `src/app/api/` — audit userId filter on all routes | DONE — `25e76e8` | YEAR | HIGH |
| 002 | DB: SQLite dev / Supabase prod | `prisma/schema.prisma` + Vercel env (DATABASE_URL) | IN_PROGRESS — db.ts + schema fixed (`1afe828`); needs Vercel integration prefix fix (ADR-005) | QUARTER | HIGH |
| 003 | arcs.care: COCD as first-class UX primitive | `~/arcs-care-local/components/hero.tsx` + new `loop-diagram.tsx` | IN_PROGRESS — this session | QUARTER | HIGH |
| 004 | mcp.arcs.care DNS fix | Vercel dashboard → perplexity-mcp → add domain `mcp.arcs.care` | DONE — live, 308 redirect confirmed | TODAY | HIGH |
| 005 | Vercel Supabase env injection | Vercel → Integrations → Supabase → fix prefix to `DATABASE` | READY — manual dashboard action, ~2 min | TODAY | HIGH |
| 006 | Supabase Branching for preview DBs | Gate: first external user OR first schema PR | BLOCKED — gate not met | QUARTER | MEDIUM |
| 007 | Prisma migration strategy | `npx prisma db push` → baseline → switch build cmd | BLOCKED — needs ADR-005 first | QUARTER | HIGH |

---

*Last updated: 2026-05-27 — ADR-005/006/007 added; ADR-002/003 → IN_PROGRESS*
