#!/usr/bin/env bash
# Baseline the PRODUCTION database into Prisma migrate history (one-time).
#
# WHY: prod was bootstrapped with `prisma db push` and has NO _prisma_migrations table,
# so `prisma migrate deploy` cannot run (it would try to replay all migrations, including
# one legacy SQLite-dialect PRAGMA migration, against a DB that already has every object).
# This caused the 2026-09-24 batonId P0 (a migration shipped in code, never reached prod).
#
# WHAT: `migrate resolve --applied` RECORDS each migration as already-applied WITHOUT running
# its SQL. Prod already matches schema.prisma (verified 2026-09-24: all 30 signature objects
# present), so marking them applied is truthful. After this, `migrate deploy` applies only
# FUTURE migrations.
#
# SAFETY: non-destructive. Creates _prisma_migrations + inserts rows. Runs NO DDL. Idempotent
# (re-running a resolved migration is a no-op). Does NOT touch application data.
#
# REQUIRES: DATABASE_URL pointing at PROD (pooler). Run once, by an operator who holds prod creds.
#   DATABASE_URL="postgres://...prod..." bash scripts/baseline-prod-migrations.sh
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "✖ DATABASE_URL not set. Export the PROD connection string first." >&2
  exit 1
fi

echo "→ Baselining prod migrate history. Target host: $(echo "$DATABASE_URL" | sed -E 's#.*@([^/:]+).*#\1#')"
echo "  (marks each migration --applied; runs NO SQL)"
read -r -p "Proceed against THIS database? [y/N] " ok
[ "$ok" = "y" ] || { echo "aborted."; exit 1; }

for d in $(ls -1 prisma/migrations | grep -vE 'migration_lock|\.toml' | sort); do
  echo "  resolve --applied $d"
  npx prisma migrate resolve --applied "$d"
done

echo "→ Verifying: migrate status should now report 'Database schema is up to date'"
npx prisma migrate status
echo "✓ Baseline complete. Future migrations now apply via 'prisma migrate deploy'."
