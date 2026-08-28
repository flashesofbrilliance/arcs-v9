#!/bin/sh
# ship_docs.sh — push committed docs-only work, open a PR, merge it. One command
# for the commit->push->PR->merge loop this repo runs constantly on docs/state changes.
#
# Tuition (2026-08-26): `git push` hung 7+ minutes TWICE on stuck credential-prompt
# processes; the pre-push hook's `npm run build` adds minutes a docs-only push never
# needs. The house rule (teardown skill efficiency contract #4) already sanctions
# --no-verify for docs-only pushes — this script ENFORCES the docs-only check instead
# of trusting the caller, kills stale push processes first, and retries.
#
# Usage: scripts/ship_docs.sh "PR title" ["PR body"]
#   - Requires all work already committed (refuses on dirty tracked files besides
#     the known hook-state files).
#   - Docs-only gate: if the diff vs origin/main touches src/, prisma/, package*.json,
#     or next.config.*, it REFUSES --no-verify and runs a full verified push instead.
#   - public/*.html changes also force the verified path (tripwire must run).
set -e

TITLE="$1"
BODY="${2:-Shipped via scripts/ship_docs.sh}"
[ -z "$TITLE" ] && { echo "usage: ship_docs.sh \"PR title\" [\"body\"]" >&2; exit 2; }

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" = "main" ] && { echo "ship_docs: refusing to run on main — branch first" >&2; exit 1; }

DIRTY=$(git status --porcelain | grep -vE '_INBOX/|_STATE/snapshot.json|public/family-roster.json' || true)
[ -n "$DIRTY" ] && { echo "ship_docs: uncommitted tracked changes — commit first:"; echo "$DIRTY"; exit 1; }

git fetch -q origin main 2>/dev/null || true
GUARDED=$(git diff --name-only origin/main...HEAD -- 'src/*' 'prisma/*' 'package.json' 'package-lock.json' 'next.config.*' 'public/*.html' 2>/dev/null || true)

# kill stale push processes (the 7-minute-hang class: stuck credential prompts)
pkill -f "git push" 2>/dev/null && sleep 1 || true

push() {
  if [ -n "$GUARDED" ]; then
    echo "ship_docs: guarded paths changed — running FULL verified push (hooks on):"
    echo "$GUARDED" | sed 's/^/  /'
    GIT_TERMINAL_PROMPT=0 git push
  else
    GIT_TERMINAL_PROMPT=0 git push --no-verify
  fi
}
push || { echo "ship_docs: push failed once, retrying in 5s..."; sleep 5; push; }

URL=$(gh pr create --title "$TITLE" --body "$BODY

🤖 Generated with [Claude Code](https://claude.com/claude-code)")
echo "PR: $URL"
sleep 5
NUM=$(gh pr list --head "$BRANCH" --state open --json number --jq '.[0].number')
gh pr merge --merge "$NUM" || { echo "ship_docs: merge failed — PR $NUM left open for review"; exit 1; }
echo "MERGED: PR #$NUM"
