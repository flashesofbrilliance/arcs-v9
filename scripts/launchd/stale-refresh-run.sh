#!/bin/bash
# stale-refresh launchd wrapper: run origin/main's copy of scripts/stale_refresh.py, so a stale
# or feature-branch main checkout never decides what runs (AGENTS.md gotcha 14).
# Install (only on Zach's go): cp this file to ~/.arcs/, cp care.arcs.stale-refresh.plist to
# ~/Library/LaunchAgents/, then: launchctl load ~/Library/LaunchAgents/care.arcs.stale-refresh.plist
# Remove: launchctl unload ~/Library/LaunchAgents/care.arcs.stale-refresh.plist
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
REPO="${ARCS_REPO:-/Users/zharris/arcs-v9}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "[$(date '+%Y-%m-%dT%H:%M:%S')] stale-refresh start"
git -C "$REPO" fetch --quiet origin main || { echo "fetch failed; nothing run"; exit 0; }
git -C "$REPO" show origin/main:scripts/stale_refresh.py > "$TMP/stale_refresh.py" || { echo "script not on origin/main; nothing run"; exit 0; }
python3 "$TMP/stale_refresh.py" --repo "$REPO" "$@"
