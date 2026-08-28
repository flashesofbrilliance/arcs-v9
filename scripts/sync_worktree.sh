#!/bin/sh
# sync_worktree.sh — bring a session worktree up to date with origin/main, safely.
#
# Tuition (2026-08-26): a plain `git merge origin/main` in a live worktree aborts on
# the hook-written state files (_INBOX drift receipts, snapshot), and bare `git stash`
# is BANNED here (shared stash stack across worktrees — see CLAUDE.md). The safe dance
# is: WIP-commit the hook-state files, merge, resolve the known state files as OURS
# (freshest hook receipts win; snapshot is rewritten by /handoff anyway). This script
# is that dance.
set -e

STATE_FILES="_INBOX/lattice-drift.jsonl _INBOX/seedbank-drift.jsonl _STATE/snapshot.json public/family-roster.json"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" = "main" ] && { echo "sync_worktree: already on main — nothing to do" >&2; exit 1; }

# WIP-commit hook-state files if dirty (never stash — shared stack)
if [ -n "$(git status --porcelain -- $STATE_FILES)" ]; then
  git add $STATE_FILES
  git commit -m "chore(state): session hook receipts $(date +%F) [NCI:SKIP state receipts]

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
  echo "sync_worktree: hook-state WIP committed"
fi

OTHER=$(git status --porcelain | grep -v '^??' || true)
[ -n "$OTHER" ] && { echo "sync_worktree: other tracked changes present — commit them first:"; echo "$OTHER"; exit 1; }

git fetch -q origin main
if git merge origin/main; then
  echo "sync_worktree: clean merge"
else
  # resolve ONLY the known state files as ours; anything else stays for a human
  CONFLICTS=$(git diff --name-only --diff-filter=U)
  UNKNOWN=""
  for f in $CONFLICTS; do
    case " $STATE_FILES " in
      *" $f "*) git checkout --ours "$f" && git add "$f" ;;
      *) UNKNOWN="$UNKNOWN $f" ;;
    esac
  done
  if [ -n "$UNKNOWN" ]; then
    echo "sync_worktree: UNRESOLVED conflicts need a human:$UNKNOWN" >&2
    exit 1
  fi
  git commit -m "merge origin/main; keep session hook receipts [NCI:SKIP merge]

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
  echo "sync_worktree: merged, state files kept as ours"
fi
