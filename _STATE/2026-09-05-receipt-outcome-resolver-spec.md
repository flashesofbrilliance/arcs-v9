# Receipt→outcome resolver — build spec (the seaworthiness path)

**Date:** 2026-09-05 · **Branch:** claude/kind-lamport-dd294a · **Status:** resolver built &
verified (empty + invariant); remainder GATED.

## Why this is the real lever
The git-side ledger is data-floor-limited (~2 low-ruin staked reel-ins after exhaustive
linking — see 2026-09-03 receipt). The only path to a *seaworthy* high-stakes calibration
signal is the receipt→outcome loop with **external adjudication**. Its hard constraint:
`Outcome.matched` is self-graded (decision-maker grades own decision = capture). The ledger
must score **only** outcomes carrying a verdict from someone/something other than the author,
arriving after T0.

## Built this session (runnable, invariant-safe, non-destructive)
`scripts/receipt_outcome_resolver.py` — reads a JSONL export, yields ledger-compatible rows,
scores ONLY `external_verdict ∈ {held, reeled}`; self-graded `matched` is reported, never
scored. Verified: empty export → honest floor; sample → self-graded row excluded, external
rows scored, NCI>100 excluded. No DB / Prisma / prod creds needed.

## Gated remainder (in order)
1. **Schema migration** (consequential — confirm before applying): add to `Outcome`
   - `externalVerdict String?`  // "held" | "reeled" | null(pending)
   - `adjudicatedBy   String?`  // who/what adjudicated (not the author)
   - `adjudicatedAt   DateTime?`
   Additive/nullable → low-risk, but touches dev.db + prod (Postgres). `npx prisma migrate dev`
   in a checkout WITH a dev.db; prod deploy separate/gated. JSON-as-TEXT rule N/A (scalars).
2. **Export producer** — admin-gated route `GET /api/audit/receipt-outcomes` (RBAC via
   `src/lib/admin.ts`) emitting the JSONL contract the resolver consumes. Works on SQLite+Postgres
   (Prisma). Read-only.
3. **Wire into the ledger** — register `ReceiptOutcomeResolver` alongside `GitRevertResolver`
   in `believability_ledger.py` (feed both resolvers' rows to `score_ledger`). **Co-merge
   dependency:** the ledger is on branch `claude/determined-herschel-e59b29` (@867d7fd0), not
   main. Do this only after the ledger lands on main.
4. **Adjudication flow** — the actual product surface that captures an external verdict
   (counterpart confirms / market resolves / third party). Until this exists the resolver
   contributes 0 (honest null), same as today's git floor.

## Honest ceiling
Steps 1–3 make the seam real and testable but yield ~0 calibration signal until step 4 produces
adjudicated data (today: 2/247 outcomes, none external). This is infrastructure ahead of data —
correct to build the seam, honest that the number won't move until verdicts arrive.
