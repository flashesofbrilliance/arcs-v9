#!/bin/bash
# SessionStart hook — ARCS v9
# Cloud containers boot with an empty node_modules. Install deps so the
# build, dev server, linter, and type-checker work without manual setup.
# Idempotent: npm install is a no-op when the tree already matches the lockfile.
# `postinstall` (prisma generate) runs automatically as part of npm install.
set -euo pipefail

# Only needed in the remote (cloud) environment; local machines already
# have node_modules from prior work.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

if [ ! -d node_modules ] || [ ! -x node_modules/.bin/next ]; then
  npm install
fi
