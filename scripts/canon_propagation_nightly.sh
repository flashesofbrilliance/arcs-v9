#!/usr/bin/env bash
# canon_propagation_nightly — evening cron entry for the canon-propagation sentinel.
#
# Governance (see _DECISIONS/CANON-COLLISION-rom-vocabulary.md + AGENTS.md gotcha 9):
#   - Auto-applies ONLY the MECHANICAL-mirror DEROT class (provably a partial-mirror
#     completion; git-reversible), and ONLY onto a dedicated review branch.
#   - NEVER pushes. NEVER touches main. NEVER writes ESCALATE/judgment items — those
#     stay in _INBOX/canon-propagation-queue.json for the human `/canon-review`.
#   - Aborts to receipt-only if the sync worktree is dirty or anything is unexpected.
#
# Runs against the MAIN checkout via an isolated worktree so it never disturbs the
# user's active branch or other worktrees (shared-stash safety).
set -euo pipefail

MAIN="${ARCS_MAIN_CHECKOUT:-/Users/zharris/arcs-v9}"
BRANCH="canon-sync/nightly"
WT="$MAIN/.claude/worktrees/canon-sync"
export CLAUDE_PROJECT_DIR="$WT"

log() { echo "[canon-nightly $(date -Iseconds)] $*"; }

cd "$MAIN" || { log "main checkout missing: $MAIN"; exit 0; }

# 1. Ensure the isolated sync worktree exists on the review branch, reset to main.
if [ ! -d "$WT" ]; then
  git worktree add -B "$BRANCH" "$WT" main >/dev/null 2>&1 || { log "worktree add failed; receipt-only"; cd "$WT" 2>/dev/null && python3 "$MAIN/scripts/canon_propagation_check.py" || true; exit 0; }
else
  git -C "$WT" reset --hard main >/dev/null 2>&1 || { log "reset failed; receipt-only"; python3 "$WT/scripts/canon_propagation_check.py" || true; exit 0; }
fi

# 2. Abort auto-apply if somehow dirty (defensive; a fresh reset should be clean).
if [ -n "$(git -C "$WT" status --porcelain)" ]; then
  log "sync worktree unexpectedly dirty; receipt-only, no auto-apply"
  python3 "$WT/scripts/canon_propagation_check.py" || true
  exit 0
fi

# 3. Apply the mechanical de-rot class + emit receipts/queue.
python3 "$WT/scripts/canon_propagation_check.py" --regenerate || true

# 4. Commit any mechanical de-rots to the review branch (no push, no main).
if [ -n "$(git -C "$WT" status --porcelain)" ]; then
  git -C "$WT" add -A
  git -C "$WT" commit -q -m "chore(canon): nightly mechanical de-rot propagation [NCI:SKIP]

Auto-applied mechanical-mirror DEROT items only (partial-mirror completion).
Judgment/ESCALATE items left in _INBOX/canon-propagation-queue.json for /canon-review.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" || true
  log "committed mechanical de-rot(s) to $BRANCH (review + merge via /canon-review; not pushed)"
else
  log "no mechanical de-rot needed tonight; judgment queue (if any) awaits /canon-review"
fi
