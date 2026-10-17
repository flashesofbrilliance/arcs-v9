#!/usr/bin/env bash
# Acceptance script: runs every self-test and prints PASS/FAIL per pre-registered line. Run from the repo root.
cd "$(git rev-parse --show-toplevel)"; fail=0
line() { if [ "$2" = 0 ]; then echo "PASS  $1"; else echo "FAIL  $1"; fail=1; fi; }
# hold-out hash must match the one committed in preregistration.md
want=$(grep -o 'HOLDOUT_SHA256: [0-9a-f]\{64\}' _PROPOSALS/farcaster/preregistration.md | cut -d' ' -f2)
got=$(shasum -a 256 runtime/specs/farcaster-gate/sealed/holdout.json | cut -d' ' -f1)
[ -n "$want" ] && [ "$want" = "$got" ]; line "holdout hash matches preregistration" $?
# lines 1-3 (dev set)
out=$(python3 runtime/specs/farcaster-gate/eval_dev.py); echo "$out" | tail -5
for k in line1_G2_withholds_all_positives_and_0_true_wrong line2_G0_misses_ge3_of_F2_F5 line3_recall_G0\<G1\<=G2; do echo "$out" | grep -q "\"$k\": true"; line "dev $k" $?; done
# line 4 (hold-out)
python3 runtime/specs/farcaster-gate/eval_holdout.py; line "line4 hold-out G2 >= 3 of 4 (else set overfit)" $?
# line 5 probes self-test
_PROPOSALS/farcaster/probes/selftest.sh >/dev/null; line "line5 probe fixtures classified 10/10" $?
# line 6 canary
_PROPOSALS/farcaster/probes/canary.sh; line "line6 canary 0 occurrences" $?
# line 7 quickstart
q=_PROPOSALS/farcaster/quickstart.sh
env -u FC_BUDGET_ALERT_ID $q --create >/dev/null 2>&1; [ $? -ne 0 ]; line "line7a no budget id -> refuses" $?
FC_BUDGET_ALERT_ID=x $q --create 2>/dev/null | grep -q "PLAN:"; line "line7b budget id -> prints plan" $?
$q teardown --verify --dry-run | grep -q "FILTER: tag:fc-bounty=2026-10"; line "line7c teardown verify prints tag filter" $?
echo "shellcheck: $(command -v shellcheck >/dev/null && shellcheck $q && echo ran-clean || echo not installed)"
[ $fail = 0 ] && echo "ACCEPT: ALL PASS" || echo "ACCEPT: FAILURES (reported, not repaired in place)"; exit $fail
