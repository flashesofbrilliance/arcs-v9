# Implementation Queue

> Auto-maintained by `.github/workflows/adr-queue.yml`
> Read by `/arcs-handoff-pickup` at session start
> Status: READY | BLOCKED | IN_PROGRESS | DONE

| ADR | Title | Pointer | Status | Horizon | Conviction |
|-----|-------|---------|--------|---------|------------|
| 001 | Auth gate: app-level (not RLS) | `src/app/api/` — audit userId filter on all routes | DONE — `25e76e8` | YEAR | HIGH |
| 002 | DB: SQLite dev / Supabase prod | `prisma.config.ts` + Vercel env (DATABASE_URL, DIRECT_URL) | BLOCKED: needs Supabase creds on Vercel | QUARTER | HIGH |
| 003 | arcs.care: COCD as first-class UX primitive | `flashesofbrilliance/arcs-care` — hero copy + loop diagram + CTA sequencing | BLOCKED: needs ADR-004 DNS fix first for API docs | QUARTER | HIGH |
| 004 | mcp.arcs.care DNS fix | Vercel dashboard → perplexity-mcp → add domain `mcp.arcs.care` | READY — no code, 10 min manual step | TODAY | HIGH |

---

*Last updated: 2026-05-27 — ADR-003 (COCD weave) + ADR-004 (DNS fix) added*
