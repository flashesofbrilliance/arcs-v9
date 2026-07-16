#!/bin/bash
# Self-test for scripts/teardown_eval.py - confirms the harness itself still catches what
# it's supposed to catch. Run after any change to teardown_eval.py or its fixtures.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FX="$ROOT/tests/fixtures/teardown-eval"
FAIL=0

run() {
  local desc="$1"; shift
  local expect_exit="$1"; shift
  python3 "$ROOT/scripts/teardown_eval.py" "$@" > /tmp/teardown_selftest_out.txt 2>&1
  local actual=$?
  if [ "$actual" -eq "$expect_exit" ]; then
    echo "  [PASS] $desc (exit $actual, expected $expect_exit)"
  else
    echo "  [FAIL] $desc (exit $actual, expected $expect_exit)"
    sed 's/^/         /' /tmp/teardown_selftest_out.txt
    FAIL=1
  fi
}

echo "teardown_eval.py self-test"
echo

run "sample-pass.html clears all gates" 0 \
  "$FX/sample-pass.html" --fixtures "$FX" --gauntlet-report "$FX/sample-pass.gauntlet.md"

run "sample-fail.html trips 7 hard gates" 1 \
  "$FX/sample-fail.html" --fixtures "$FX" --gauntlet-report "$FX/sample-fail.gauntlet.md"

run "sample-pass.html fails without a gauntlet report" 1 \
  "$FX/sample-pass.html" --fixtures "$FX"

run "sample-pass.html fails without fixtures (fact_check unreachable... actually SKIPs; other gates should still pass)" 0 \
  "$FX/sample-pass.html" --gauntlet-report "$FX/sample-pass.gauntlet.md"

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL SELF-TESTS PASSED"
  exit 0
else
  echo "SELF-TEST FAILURES - the harness itself is not behaving as designed, fix before trusting it"
  exit 1
fi
