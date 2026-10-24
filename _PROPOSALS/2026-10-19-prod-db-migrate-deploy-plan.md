# Plan: prod-db-onto-prisma-migrate-deploy (remaining slice)

Date: 2026-10-19. Backlog row: `prod-db-onto-prisma-migrate-deploy` (P1). Memory: `prod-schema-drift-migrate-deploy-not-db-push`.

## What is already true (checked today)

- Prod HAS a `_prisma_migrations` table now (read-only query via Supabase MCP, 2026-10-19). It lists 23 migrations, matching all 23 folders in `prisma/migrations/`. 19 were baselined together on 2026-09-24 14:23 UTC (PR #491, `scripts/baseline-prod-migrations.sh`). 4 later ones finished 2026-10-05 to 10-06. None are rolled back.
- `scripts/vercel-migrate-deploy.sh` runs `prisma migrate deploy` on production builds only, refuses the :6543 transaction pooler, and is wired as the web service `buildCommand` in `vercel.json` (commit be72fa81, 2026-10-05). Before that fix the top-level buildCommand was ignored and migrations were hand-applied.
- `.github/workflows/preview-db-migrate.yml` exists, but GitHub Actions is off by choice since 2026-10-15, so it does not run.

So the row's first two steps (baseline, wire migrate deploy) are done. The row text is stale on that point.

## What is left

1. **Prove the pipeline applied a migration by itself.** The 4 post-baseline rows may have been hand-applied before be72fa81 took effect. Check the build log of the next production deploy that carries a new migration for the line "applying pending Prisma migrations" and a non-empty apply. Until then, "auto-applies" is unconfirmed.
2. **Frustration Gate: un-migrated schema drift fails before merge.** Add a local pre-commit check (Actions is off, so pre-commit is the always-run path): when `prisma/schema.prisma` is staged, run `npx prisma migrate diff --from-migrations prisma/migrations --to-schema-datamodel prisma/schema.prisma --shadow-database-url <local> --exit-code`, or the no-shadow variant against an empty SQLite file if the provider allows. Known-bad fixture: add a column to schema.prisma with no migration, gate fails. Known-good: today's tree, gate passes.
3. **Live drift monitor.** `GET /api/health?deep=1` already probes per-model drift. Add one line to the session-start sentries (or the status page) that calls it with `CRON_SECRET` and flags any missing column, plus "newest Receipt older than N days". This is the standing tripwire the row's adjacent reframe asks for.
4. **Close the row** once 1 to 3 hold: state DONE, with the receipt for the gate PR.

## Gates kept from the row

- No `--accept-data-loss`; migrations stay additive (expand, deploy, contract later).
- Diff a model against prod `information_schema` before any hand fix.
- Open item 3 in the global notes (manually set `DATABASE_URL`, rotation risk) is separate and stays open.

Cost prior: 1 to 2 hours for steps 2 and 3; step 1 waits for the next schema change.
