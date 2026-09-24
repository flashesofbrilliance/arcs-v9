#!/usr/bin/env bash
# Production-only migration apply, for the Vercel build pipeline.
# Runs `prisma migrate deploy` ONLY on production deploys, so a preview build never
# migrates the prod database. Safe to run on every build: it is a no-op when there are
# no pending migrations, and it never runs on preview/development.
#
# Enable (AFTER scripts/baseline-prod-migrations.sh has been run once against prod):
#   vercel.json → "buildCommand": "bash scripts/vercel-migrate-deploy.sh && npm run build"
# migrate deploy is forward-only and non-interactive; it applies committed migrations and
# fails loud (blocking the deploy) if one cannot apply — which is the guard we want.
set -euo pipefail

if [ "${VERCEL_ENV:-}" = "production" ]; then
  echo "→ production deploy: applying pending Prisma migrations"
  npx prisma migrate deploy
else
  echo "→ ${VERCEL_ENV:-local} build: skipping migrate deploy (production-only)"
fi
