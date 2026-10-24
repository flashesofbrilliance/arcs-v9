#!/usr/bin/env bash
# risk_sweep_cron.sh - zero-token nightly entry for scripts/risk_sweep.py.
# Pure git + python3 stdlib. Reads origin/main by ref, writes only the gitignored local
# register and cursor. Never checks out, commits, pushes, or heals (heal is manual: --heal).
set -euo pipefail
MAIN="${ARCS_MAIN_CHECKOUT:-/Users/zharris/arcs-v9}"
cd "$MAIN" || exit 0
OUT="$MAIN/_STATE/risk-sweep-last.md"
mkdir -p "$MAIN/_STATE"
python3 scripts/risk_sweep.py > "$OUT" 2>&1 || true
# macOS notification only when something high-severity is open
if grep -q '^- \[high/' "$OUT"; then
  osascript -e 'display notification "High-severity change in the risk register" with title "ARCS risk sweep"' >/dev/null 2>&1 || true
fi
