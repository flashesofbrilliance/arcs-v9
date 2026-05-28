# ARCS Session State

**Last updated:** 2026-05-27b
**Last commit (arcs):** 11ba2fc — Prisma 7 adapter pattern
**Last commit (A.R.C.S.):** 6812334 — drift sentinel fixes
**Last commit (arcs-care):** 0240f18 — hero redesign + LoopDiagram

## Status

- Book II Parts I–VI: ALL CANONICAL ✅
- _DECISIONS/: ADR-001 through ADR-007 live on GitHub ✅
- A.R.C.S. working tree: CLEAN ✅ (151 untracked → 0 this session)
- arcs-care working tree: CLEAN ✅
- arcs working tree: CLEAN ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP deploy | ✅ Done | Live at `perplexity-mcp-kohl.vercel.app` |
| P3: arcs-care PLG funnel | 🟡 Specced | Phase 1 next: model swap + Lab CTA in compass |
| P4: arcs-v9 → Vercel preview | 🔴 BLOCKED | Fix Vercel Supabase integration prefix → `DATABASE` |

## P4 exact next steps (unchanged from last session)

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
```

## P3 arcs-care next steps (Phase 1)

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
| 002 | IN_PROGRESS — code fixed, waiting on Vercel integration |
| 003 | DONE |
| 004 | DONE |
| 005 | READY — manual dashboard action (fix prefix) |
| 006 | BLOCKED — gate: first external user or schema PR |
| 007 | BLOCKED — needs ADR-005 first |
| TBD | NEEDED — arcs_dewy.py naming collision → arcs_dewy_pkg rename |

## Known open issues

1. **arcs_dewy.py shadows arcs-dewy/ package** — bridge `_HAS_DEWY` always False until renamed; ADR required
2. **Prisma 7 fix unvalidated** — NCI 79, SOFT PAUSE — run /fated before marking P4 clear
3. **arcs-care Phase 1 not started** — spec approved, no code written yet

## Blocking

**ONE human action required for P4:** Vercel dashboard → Supabase integration → set prefix to `DATABASE`.
Everything else can be done by Claude Code once that fires.
