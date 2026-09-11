#!/usr/bin/env bash
# night_moves_gather.sh — deterministic raw material for the /night-moves digest.
# Emits the day's shipped commits, net-new tools, ADRs/receipts, and memory writes.
# The model reads this output and synthesizes the interpretive sections (learned /
# JTBD shape / net-new tools). Cheap by design: pure git + find, no network.
#
# Usage: scripts/night_moves_gather.sh [YYYY-MM-DD]   (defaults to today)
set -euo pipefail

DAY="${1:-$(date +%Y-%m-%d)}"
FROM="$DAY 00:00:00"
TO="$DAY 23:59:59"
AUTHOR="${NIGHT_MOVES_AUTHOR:-Zach}"
MEM_DIR="/Users/zharris/.claude/projects/-Users-zharris-arcs-v9/memory"

# --all sweeps every branch/worktree (they share one .git); sort -u dedups the
# same commit landed on multiple branches.
gitlog() { git log --all --since="$FROM" --until="$TO" --author="$AUTHOR" "$@"; }

echo "# night-moves raw material — $DAY"
echo "# generated $(date '+%Y-%m-%d %H:%M %Z') · author filter: $AUTHOR"
echo

echo "## SHIPPED — commits authored today (all branches, deduped by message)"
# key by subject so the same logical change on N worktrees shows once, with its scope
gitlog --pretty='%s%x09%h%x09%ci' | sort -t"$(printf '\t')" -k1,1 -u | sort -k3 \
  || true
echo
echo "### shipped count (unique SHAs): $(gitlog --pretty='%h' | sort -u | wc -l | tr -d ' ')"
echo

echo "## NET-NEW TOOLS — files ADDED today under tool/skill/script/decision dirs"
gitlog --diff-filter=A --name-only --pretty=format: \
  | grep -E '^(scripts/|operators/|\.claude/(skills|workflows|commands)/|src/lib/)' \
  | sort -u || echo "(none)"
echo

echo "## DECISIONS — ADRs / DEWY receipts touched today"
gitlog --name-only --pretty=format: \
  | grep -E '(_DECISIONS/.*ADR|\.dewy\.json$)' | sort -u || echo "(none)"
echo

echo "## MEMORY — auto-memory files written today"
if [ -d "$MEM_DIR" ]; then
  find "$MEM_DIR" -name '*.md' -newermt "$FROM" ! -newermt "$TO" 2>/dev/null \
    | xargs -n1 basename 2>/dev/null | sort -u || echo "(none)"
else
  echo "(memory dir not found: $MEM_DIR)"
fi
echo

echo "## FILES — all paths touched today, by top-level area (for 'JTBD shape')"
gitlog --name-only --pretty=format: | sed '/^$/d' \
  | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn | head -25 || true
