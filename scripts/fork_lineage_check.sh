#!/usr/bin/env bash
# Fork Lineage drift check (J17) — conditional action.
#
# Rule: if the number of commits since the last state-sync exceeds THRESHOLD,
# TRIGGER a state-sync (the snapshot's semantic fields are overdue). The git
# fields auto-refresh via the SessionStart hook, but session_summary /
# next_action / blocking do NOT — they silently drift (chronos-sequencer,
# ADR-032). This is the guard that catches "worked past the handoff."
#
# Properties (ADR-032 conformance):
#   - Terminating: running the sync advances snapshot.head_sha -> count resets
#     to 0. Cannot loop.
#   - Fail-safe: if the snapshot is missing/unreadable/head not in history, it
#     treats that as drifted (exit 2), never a silent pass.
#   - Advisory action: it SIGNALS (message + non-zero exit) rather than
#     auto-committing — semantic-field sync needs judgment, not automation.
#     Wire into a stop/pre-push hook or run at handoff time.
#
# Exit codes: 0 = within threshold · 1 = threshold exceeded (sync now) ·
#             2 = cannot measure (treat as drifted).
set -euo pipefail

THRESHOLD="${FORK_LINEAGE_THRESHOLD:-5}"
SNAP="_STATE/snapshot.json"

[ -f "$SNAP" ] || { echo "⚠ J17: snapshot missing ($SNAP) — cannot measure drift; run init-state-sync."; exit 2; }

HEAD_SHA="$(python3 -c "import json,sys; print(json.load(open('$SNAP'))['git']['head_sha'])" 2>/dev/null || true)"
[ -n "${HEAD_SHA:-}" ] || { echo "⚠ J17: snapshot head_sha unreadable — treat as drifted; run init-state-sync."; exit 2; }

git cat-file -e "${HEAD_SHA}^{commit}" 2>/dev/null || { echo "⚠ J17: snapshot head_sha ${HEAD_SHA} not in history — treat as drifted; run init-state-sync."; exit 2; }

DRIFT="$(git rev-list --count "${HEAD_SHA}..HEAD")"

if [ "$DRIFT" -gt "$THRESHOLD" ]; then
  echo "⚠ J17 THRESHOLD EXCEEDED: ${DRIFT} commits since last state-sync (> ${THRESHOLD})."
  echo "  ACTION: run init-state-sync (Fork Lineage) — the snapshot's semantic fields are overdue."
  echo "  (git fields auto-refresh; session_summary / next_action / blocking do NOT — they drift.)"
  exit 1
fi

echo "J17 OK: ${DRIFT} commit(s) since last state-sync (<= ${THRESHOLD})."
exit 0
