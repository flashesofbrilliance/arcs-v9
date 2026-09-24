# Runbook: put arcs-v9 prod on `prisma migrate deploy` (P1 prod-db-onto-prisma-migrate-deploy)

Root cause of the 2026-09-24 batonId P0: prod was `prisma db push`-bootstrapped, has **no
`_prisma_migrations` table**, so committed migrations ship in code but never reach prod, silently,
until a query hits a missing column. Diagnosis (2026-09-24, read-only): prod already contains **all
30 signature objects** of every migration — it is structurally in sync with `schema.prisma` (the
batonId/Tribune hotfix closed the last gap). `provider = "postgresql"`; 18 of 19 migrations are
Postgres-native, 1 is a legacy SQLite `PRAGMA` rebuild (harmless — see below).

## Sequence (order matters)

1. **Baseline prod (one-time, needs prod creds).** `migrate resolve --applied` records each migration
   as applied WITHOUT running its SQL, so the legacy PRAGMA migration never re-executes and the
   already-present objects are not recreated. Non-destructive; touches no app data.
   ```bash
   DATABASE_URL="<prod pooler URL>" bash scripts/baseline-prod-migrations.sh
   ```
   Verify it ends with `migrate status` → "Database schema is up to date".

2. **Enable auto-apply on deploy (only after step 1).** Set in `vercel.json`:
   ```json
   "buildCommand": "bash scripts/vercel-migrate-deploy.sh && npm run build"
   ```
   The wrapper runs `migrate deploy` ONLY when `VERCEL_ENV=production`, so previews never migrate
   prod. Forward-only; fails the deploy loud if a migration cannot apply (the guard).

3. **CI drift gate (frustration-gate).** Add a check that fails when `schema.prisma` has changes not
   captured in a migration, so "edited schema, forgot the migration" can't merge. Needs a shadow DB:
   ```bash
   npx prisma migrate diff --from-migrations prisma/migrations \
     --to-schema-datamodel prisma/schema.prisma --shadow-database-url "$SHADOW_DB" --exit-code
   ```
   Non-zero exit = uncaptured drift. Wire into the always-run path (`npm test` / a CI job).

## Guardrails (from the ticket)
- Never `--accept-data-loss`. A destructive diff must fail loud and go to a human.
- The hand-applied tribune DDL is accounted for: step 1 marks `20260906000000_tribune` applied, so
  history and reality agree.
- Verify each step against the DB, not memory.

## What still needs an operator (prod creds)
Step 1 (baseline) and enabling step 2. Steps' scripts are committed and reviewed; running step 1
against prod is the one action that needs the prod `DATABASE_URL` (Vercel env, not in the repo).
