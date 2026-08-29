#!/bin/bash
# PreCompact hook — ARCS v9
# Snapshots key session state to scratchpad before context compression so the
# next turn picks up with accurate context instead of re-deriving it.
set -euo pipefail

SCRATCHPAD="${TMPDIR:-/tmp}/arcs-compact-state.md"

{
  echo "# ARCS Session State (pre-compact snapshot)"
  echo "## Captured: $(date '+%Y-%m-%d %H:%M %Z')"
  echo ""

  echo "## Branch"
  git -C "$CLAUDE_PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(unknown)"
  echo ""

  echo "## Last 5 commits"
  git -C "$CLAUDE_PROJECT_DIR" log --oneline -5 2>/dev/null || echo "(none)"
  echo ""

  echo "## Open PRs (this branch)"
  BRANCH=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
  gh pr list --head "$BRANCH" --json number,title,url 2>/dev/null | \
    python3 -c "import sys,json; prs=json.load(sys.stdin); [print(f'  PR #{p[\"number\"]}: {p[\"title\"]} — {p[\"url\"]}') for p in prs]" 2>/dev/null || echo "(none)"
  echo ""

  echo "## Working tree status"
  git -C "$CLAUDE_PROJECT_DIR" status --short 2>/dev/null | head -20 || echo "(clean)"
  echo ""

  # Drift-receipt sweep: the orphaned knowledge lattice has no owner and ships
  # statically to prospect surfaces, so it decays by neglect. Emit a drift
  # receipt at compaction (receipt-only; NOTOMATION — the human re-authors).
  # Inchworm auditor — CLOSE end (advance / needle). Regenerate the mechanical
  # countables (idempotent: writes only on real drift) and emit a receipt.
  echo "## Knowledge-lattice drift (inchworm close)"
  python3 "$CLAUDE_PROJECT_DIR/scripts/lattice_drift_check.py" --regenerate 2>/dev/null || echo "(check unavailable)"

} > "$SCRATCHPAD" 2>/dev/null || true

echo "pre-compact: state snapshot written to $SCRATCHPAD"
