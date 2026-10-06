#!/usr/bin/env bash
# Production-only migration apply, for the Vercel build pipeline.
# Runs `prisma migrate deploy` ONLY on production deploys, so a preview build never
# migrates the prod database. Safe to run on every build: it is a no-op when there are
# no pending migrations, and it never runs on preview/development.
#
# Wired as experimentalServices.web.buildCommand in vercel.json. A TOP-LEVEL buildCommand is
# ignored once experimentalServices is present (each service builds with its own command; the
# 2026-10-06 #830 prod log ran plain `npm run build`, so migrations were hand-applied).
# migrate deploy is forward-only and non-interactive; it applies committed migrations and
# fails loud (blocking the deploy) if one cannot apply — which is the guard we want.
set -euo pipefail

if [ "${VERCEL_ENV:-}" = "production" ]; then
  echo "→ production deploy: applying pending Prisma migrations"
  # DATABASE_URL is the Supavisor transaction pooler (:6543), where migrate's advisory lock
  # is unreliable. Prefer DIRECT_URL; else the session-mode pooler on the same host (:5432).
  MIGRATE_URL="${DIRECT_URL:-${DATABASE_URL/:6543\//:5432/}}"
  HOSTPORT=$(printf '%s' "$MIGRATE_URL" | sed -E 's#^[^@]*@([^/?]+).*#\1#')
  echo "→ migrate target: ${HOSTPORT}"
  case "$HOSTPORT" in *:6543) echo "✗ refusing migrate on transaction pooler :6543; set DIRECT_URL" >&2; exit 1;; esac
  # On failure (P3009 on later deploys): fix forward with a new migration, after
  # `prisma migrate resolve --rolled-back <name>`. App rollback does not roll back schema:
  # keep migrations additive (expand, deploy, then contract in a later deploy).
  DATABASE_URL="$MIGRATE_URL" npx prisma migrate deploy
else
  echo "→ ${VERCEL_ENV:-local} build: skipping migrate deploy (production-only)"
fi
