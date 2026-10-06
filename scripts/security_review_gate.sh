#!/usr/bin/env bash
# Fail the security-review job when the scan never actually ran.
#
# anthropics/claude-code-security-review concludes `success` with findings_count=0 even
# when Claude Code errored before reviewing anything: it writes {"error": "..."} to
# claudecode-results.json and the embedded CLI stdout carries "is_error":true and
# "api_error_status":400 (seen 2026-10-05, run 37400262799, API usage cap). A green check
# that never reviewed the diff is a false pass, so this gate turns it red.
#
# Usage: security_review_gate.sh [results.json] [error.log]
#   defaults: $GITHUB_WORKSPACE/claudecode-results.json, $GITHUB_WORKSPACE/claudecode-error.log
#   (the action copies both to the workspace root). Exit 0 = scan ran (or was deduped);
#   exit 1 = it did not.
#
# Dedupe skip (2026-10-06): the action keeps a run-history cache (.claudecode-marker/marker.json,
# restored by its "Check ClaudeCode run history" step) and SKIPS its scan step when this PR was
# already scanned. A skipped scan writes no results file, so a re-run went red (run 37470888306).
# The signal is the action's own `results-file` output: its scan step sets it as its first line,
# so it is empty iff that step never started. Pass it in as SCAN_RESULTS_OUTPUT. Empty output +
# marker present = intentional dedupe skip (pass with a notice). Empty output + no marker = fail.
# Non-empty output = the scan ran, and every check below still applies (API errors stay red).
set -u
ws="${GITHUB_WORKSPACE:-.}"
results="${1:-$ws/claudecode-results.json}"
errlog="${2:-$ws/claudecode-error.log}"
fail() { echo "::error title=Security review did not run::$1"; exit 1; }
marker="${MARKER_FILE:-$ws/.claudecode-marker/marker.json}"

if [ "${SCAN_RESULTS_OUTPUT+set}" = set ] && [ -z "$SCAN_RESULTS_OUTPUT" ]; then
  [ -f "$marker" ] || fail "scan step was skipped but no run-history marker exists; cannot tell why."
  # A PR can commit its own .claudecode-marker/marker.json to make the action skip; only a
  # marker restored from the cache (untracked) for THIS PR counts as a real prior scan.
  if git -C "$ws" ls-files --error-unmatch "$marker" >/dev/null 2>&1; then
    fail "marker.json is committed in the PR, not restored from the run-history cache."
  fi
  pr="${PR_NUMBER:-}"
  if [ -n "$pr" ] && [ "$(jq -r '.pr_number // empty' "$marker" 2>/dev/null)" != "$pr" ]; then
    fail "run-history marker is not for PR #$pr."
  fi
  # Marker fields are echoed into a workflow command: allow only hex / digits.
  prev_sha="$(jq -r '.sha // ""' "$marker" 2>/dev/null | tr -cd '0-9a-f' | head -c 40)"
  prev_run="$(jq -r '.run_id // ""' "$marker" 2>/dev/null | tr -cd '0-9' | head -c 20)"
  echo "::notice title=Security review skipped (already scanned)::this PR was already scanned at ${prev_sha:-unknown} (run ${prev_run:-unknown}); the action's run-history dedupe skipped it."
  exit 0
fi

[ -s "$results" ] || fail "no results file at $results; the scan produced nothing."
jq -e . "$results" >/dev/null 2>&1 || fail "results file is not valid JSON."
if jq -e 'has("error") and .error != null' "$results" >/dev/null 2>&1; then
  fail "$(jq -r '.error' "$results" | grep -m1 -oE 'API Error: [^"]*' || jq -r '.error' "$results" | head -c 300)"
fi
for f in "$results" "$errlog"; do
  [ -f "$f" ] || continue
  if grep -qE '"is_error"[[:space:]]*:[[:space:]]*true|"api_error_status"[[:space:]]*:[[:space:]]*[0-9]' "$f"; then
    fail "Claude Code reported is_error/api_error_status in $(basename "$f")."
  fi
done
echo "security review ran: $(jq -r '.findings | if . == null then 0 else length end' "$results") finding(s)."
