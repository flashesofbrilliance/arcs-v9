#!/usr/bin/env bash
# Prospect-safety tripwire for public/ front-ends. Grep-only (no browser), fast,
# runs on every PR that touches public/**. A hit = a drift/decay event: an
# internal-only fact leaked onto a prospect-facing page (blight/neglect of the
# internal↔external air-gap). Exits non-zero so CI blocks the merge; the failure
# is the receipt.
#
# Usage:  scripts/tripwire.sh [file-or-dir ...]   (default: public/*.html)
set -euo pipefail

TARGETS=("$@")
if [ ${#TARGETS[@]} -eq 0 ]; then
  # default: only the federated-family public pages (extend as the family grows)
  TARGETS=(public/playground.html public/monolith.html public/pf-*.html public/forge-pattern.html public/forge-cut.html)
fi

# real counterpart names that must never reach a prospect page
NAMES='kleban|elsamadisi|rayan saleh|periscope|hotes|daniels|zensai|\byuri\b|\bahmed\b|skinner|trabulski|delaney|joe kim|louisville'
# dead-in-public links (claude.ai artifacts are private/authed)
LINKS='claude\.ai/code'
# insider repo jargon (internal paths, generators, SSOT filenames)
JARGON='_ARTIFACTS|_STATE|_INBOX|_CANON|_DECISIONS|_PATTERNS|runtime/specs|arcs_kinematics|forge_counterpart|schema\.prisma|data\.arcs-v9|performer-gauntlet'

fail=0
for f in "${TARGETS[@]}"; do
  [ -f "$f" ] || continue
  for label in "real-name:$NAMES" "dead-link:$LINKS" "jargon:$JARGON"; do
    kind="${label%%:*}"; pat="${label#*:}"
    hits=$(grep -oiE "$pat" "$f" | sort -u | tr '\n' ',' || true)
    # Counterpart-facing exception (2026-08-26): a page whose FILENAME is the
    # counterpart's name (ahmed*.html, wing.html, ...) is their own artifact —
    # their own name belongs on it. Any OTHER counterpart's name still fails.
    if [ "$kind" = "real-name" ] && [ -n "$hits" ]; then
      base=$(basename "$f" | tr '[:upper:]' '[:lower:]')
      kept=""
      IFS=',' read -ra HARR <<< "${hits%,}"
      for hh in "${HARR[@]}"; do
        hlow=$(printf '%s' "$hh" | tr '[:upper:]' '[:lower:]')
        case "$base" in *"$hlow"*) ;; *) kept="$kept$hh,";; esac
      done
      hits="$kept"
    fi
    if [ -n "$hits" ]; then
      echo "TRIPWIRE FAIL [$kind] $f -> ${hits%,}"
      fail=1
    fi
  done
done

if [ "$fail" -ne 0 ]; then
  echo "::error::tripwire caught a prospect-safety drift — an internal fact leaked to a public page. Fix or gate the page before merge."
  exit 1
fi
echo "tripwire clean: ${#TARGETS[@]} target(s), 0 name/link/jargon leaks"
