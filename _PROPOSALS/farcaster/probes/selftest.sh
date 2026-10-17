#!/usr/bin/env bash
# Offline self-test for both probes. Pass = every fixture classified as its expected_verdict (4/4 broken + good, per probe).
cd "$(dirname "$0")"; pass=0; total=0
for f in fixtures/*.json; do
  case $f in *events-*) p=events-probe.mjs;; *) p=write-path-probe.mjs;; esac
  exp=$(python3 -c "import json,sys;print(json.load(open('$f'))['expected_verdict'])")
  out=$(node $p --fixture $f); got=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['verdict'])")
  total=$((total+1)); if [ "$got" = "$exp" ]; then pass=$((pass+1)); r=ok; else r=WRONG; fi; echo "$r $f expected=$exp got=$got"
done
echo "selftest $pass/$total"; [ "$pass" = "$total" ]
