#!/bin/bash
# SessionStart hook — ARCS v9 (Next.js 16 + Prisma 7)
# Fresh cloud containers start with an empty node_modules. This installs deps
# (and generates the Prisma client via the `postinstall` script) so that
# build / lint / type-check / dev work without a manual `npm install`.
# Synchronous: the session waits until deps are ready — no race conditions.
set -euo pipefail

# Only run in the remote (Claude Code on the web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Idempotent: safe to re-run; a no-op when already up to date.
# `postinstall` runs `prisma generate`, so the Prisma client is built too.
npm install
