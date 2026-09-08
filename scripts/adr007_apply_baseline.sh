#!/usr/bin/env bash
# ADR-007 re-baseline — the live-DB half of the migration history reset.
#
# The local half (new baseline migration generated from schema.prisma, old
# migrations archived to prisma/_ARCHIVE_migrations_pre-postgres-baseline/,
# migration_lock.toml fixed to postgresql) is already committed. This script
# does the part that needs real DATABASE_URL credentials against production,
# which the authoring session could not reach (Supabase MCP is scoped to the
# wrong org for this project; the `supabase` CLI crashed immediately in that
# sandbox — see _PATTERNS/durable-gotchas.md).
#
# Run this from a shell that has the production DATABASE_URL set (e.g. after
# `vercel env pull` against the arcs-v9 project, or your own .env.local).
#
# Safety: this ONLY writes into prisma's own _prisma_migrations bookkeeping
# table (marking the new baseline as already-applied). It does not run any
# DDL against your data tables — that's the point of a resolve, not an apply.
set -euo pipefail

BASELINE="20260908130109_baseline_postgres_init"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is not set. Point it at production (Supabase pooler) before running this." >&2
  exit 1
fi

echo "== Step 1: confirm zero drift between live DB and prisma/schema.prisma =="
npx prisma migrate diff \
  --from-url "$DATABASE_URL" \
  --to-schema prisma/schema.prisma \
  --script > /tmp/adr007_drift_check.sql

if [ -s /tmp/adr007_drift_check.sql ]; then
  echo "DRIFT DETECTED — live DB does not match prisma/schema.prisma exactly." >&2
  echo "Refusing to mark the baseline as applied until this is reconciled." >&2
  echo "Diff written to /tmp/adr007_drift_check.sql for review." >&2
  exit 1
fi
echo "No drift — live schema matches prisma/schema.prisma exactly."

echo "== Step 2: mark the baseline migration as applied (bookkeeping only, no DDL) =="
npx prisma migrate resolve --applied "$BASELINE"

echo "== Done. =="
echo "Next: flip .github/workflows/ci.yml and preview-db-migrate.yml from"
echo "'prisma db push' to 'prisma migrate deploy' in a follow-up commit, then"
echo "verify with a real PR that touches prisma/schema.prisma."
