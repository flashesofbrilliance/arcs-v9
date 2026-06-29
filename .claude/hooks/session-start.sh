#!/bin/bash
# SessionStart hook — ARCS v9
# Cloud containers boot with an empty node_modules. Install deps so the
# build, dev server, linter, and type-checker work without manual setup.
# Idempotent: npm install is a no-op when the tree already matches the lockfile.
# `postinstall` (prisma generate) runs automatically as part of npm install.
set -euo pipefail

# --- Session grounding (runs always, local + cloud; guarded to never fail the hook) ---
# (1) Ground the clock so a resumed session never confabulates the time/date.
# (2) Memory 1-1 audit: flag orphan memory files (on disk, missing from MEMORY.md index)
#     at pickup instead of discovering drift several turns in.
echo "session-start: $(date '+%Y-%m-%d %H:%M %Z')"
MEMDIR="$HOME/.claude/projects/-Users-zharris-arcs-v9/memory"
if [ -f "$MEMDIR/MEMORY.md" ]; then
  orphans=$(comm -23 \
    <(ls -1 "$MEMDIR"/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null | grep -v '^MEMORY.md$' | sort) \
    <(grep -oE '\]\([a-zA-Z0-9_-]+\.md\)' "$MEMDIR/MEMORY.md" | tr -d ']()' | sort -u) 2>/dev/null || true)
  if [ -z "${orphans:-}" ]; then echo "memory: 1-1 OK"; else echo "memory: ORPHANS (not in MEMORY.md) -> $(echo $orphans | tr '\n' ' ')"; fi
fi

# Only the dependency bootstrap below is remote-only; the grounding above runs everywhere.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

if [ ! -d node_modules ] || [ ! -x node_modules/.bin/next ]; then
  npm install
fi
