# ADR-022 — User Schema Debt: emailVerified + image Missing from 0_init Migration

> **Status:** DECIDED
> **Date:** 2026-06-03

## D — The Decision

**Sharp question:** How should we resolve the missing `emailVerified` and `image` columns on the `User`
table, which were added in a SQLite-only migration (`d732dad`) but never ported to the Postgres baseline?

## E — Entity / System

- `prisma/migrations/0_init/migration.sql` — Postgres baseline; missing `emailVerified TIMESTAMP(3)` and `image TEXT`
- `prisma/schema.prisma` — Prisma model includes both fields (correct)
- `User` table in `xbbpiryokswwvcrcutge` — columns added live via `apply_migration` as emergency fix during ADR-016 execution
- `PrismaAdapter` (Auth.js v5) — requires `emailVerified` to upsert users on sign-in

## Context

During ADR-016 execution, every magic-link sign-in attempt threw:
```
ERROR: column User.emailVerified does not exist
```
Root cause: `prisma/migrations/20260410143234_dewy_v1/migration.sql` is SQLite dialect
(`DATETIME`, `PRAGMA`, inline `PRIMARY KEY`) — it was the original dev migration and was never
converted to Postgres. The `0_init` Postgres baseline was written from `schema.prisma` at the
time, but `emailVerified` and `image` had already been added to the schema in commit `d732dad`
*after* `0_init` was written. The Postgres migration history has a gap.

Emergency fix: `ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "emailVerified" TIMESTAMP(3)` and
`ADD COLUMN IF NOT EXISTS "image" TEXT` applied directly to prod via MCP `apply_migration`.

## Decision

**Accept the live fix as canonical.** Update `0_init` to include both columns so future fresh
deployments don't hit the same gap. No new migration file needed — `0_init` is a baseline
(not a delta), so patching it is correct per ADR-007.

## Implementation

1. Add `"emailVerified" TIMESTAMP(3)` and `"image" TEXT` to the `User` CREATE TABLE block in
   `prisma/migrations/0_init/migration.sql`
2. Verify `prisma/schema.prisma` User model already has both fields (it does — `d732dad`)
3. No prod migration needed — columns already exist via emergency apply

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

## Revisit trigger

When migrating to a second Postgres environment (e.g. staging, branch DB) — run
`prisma migrate deploy` and confirm it applies cleanly without the column-missing error.
