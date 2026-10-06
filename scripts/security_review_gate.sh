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
#   (the action copies both to the workspace root). Exit 0 = scan ran; exit 1 = it did not.
set -u
ws="${GITHUB_WORKSPACE:-.}"
results="${1:-$ws/claudecode-results.json}"
errlog="${2:-$ws/claudecode-error.log}"
fail() { echo "::error title=Security review did not run::$1"; exit 1; }

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
