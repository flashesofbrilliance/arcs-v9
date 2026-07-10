#!/bin/bash
# deploy-prod.sh — always run this instead of `vercel --prod`
# Forces deploy from the main worktree regardless of where you call it from.
set -euo pipefail

MAIN_WORKTREE="/Users/zharris/arcs-v9/.claude/worktrees/frosty-kepler-b69f51"

if [ ! -d "$MAIN_WORKTREE" ]; then
  echo "ERROR: Main worktree not found at $MAIN_WORKTREE"
  echo "Check: git worktree list | grep main"
  exit 1
fi

BRANCH=$(git -C "$MAIN_WORKTREE" branch --show-current 2>/dev/null)
if [ "$BRANCH" != "main" ]; then
  echo "ERROR: $MAIN_WORKTREE is on '$BRANCH', not main — cannot deploy"
  exit 1
fi

echo "→ Deploying from main worktree ($MAIN_WORKTREE)"
cd "$MAIN_WORKTREE"
vercel --prod "$@"
