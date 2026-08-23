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
  # default: federated-family showcase pages + the two Todd-facing pages that
  # had leaked flags (2026-08-23). NOTE: the OTHER Todd/PRL pages (todd-teardown,
  # todd-logictree, prl-status-*) legitimately carry the counterpart's OWN name
  # (Hotes) and so cannot join the blanket real-name check below without per-page
  # own-name allowlisting — deliberately kept out of the default set until that
  # exists. They still get link/jargon/dynamic-input coverage if named explicitly.
  TARGETS=(public/playground.html public/monolith.html public/pf-*.html public/forge-pattern.html public/forge-cut.html public/prl-chatbot.html public/todd-call.html)
fi

# real counterpart names that must never reach a prospect page
NAMES='kleban|elsamadisi|rayan saleh|periscope|hotes|daniels|zensai|\byuri\b|\bahmed\b|skinner|trabulski|delaney|joe kim|louisville'
# dead-in-public links (claude.ai artifacts are private/authed)
LINKS='claude\.ai/code'
# insider repo jargon (internal paths, generators, SSOT filenames)
JARGON='_ARTIFACTS|_STATE|_INBOX|_CANON|_DECISIONS|_PATTERNS|runtime/specs|arcs_kinematics|forge_counterpart|schema\.prisma|data\.arcs-v9|performer-gauntlet'
# unfilled dynamic inputs — template tokens that should have been rendered away,
# plus stray dev markers. Scoped to signals that never appear in legitimate
# client copy or JS: mustache/handlebars {{...}}, and TKTK/FIXME markers.
# (Bare ${...} is excluded on purpose — it is valid JS template-literal syntax
# on the interactive pages.)
DYNAMIC='\{\{[^}]*\}\}|\bTKTK\b|\bFIXME\b'

fail=0
for f in "${TARGETS[@]}"; do
  [ -f "$f" ] || continue
  for label in "real-name:$NAMES" "dead-link:$LINKS" "jargon:$JARGON" "dynamic-input:$DYNAMIC"; do
    kind="${label%%:*}"; pat="${label#*:}"
    hits=$(grep -oiE "$pat" "$f" | sort -u | tr '\n' ',' || true)
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
echo "tripwire clean: ${#TARGETS[@]} target(s), 0 name/link/jargon/dynamic-input leaks"
