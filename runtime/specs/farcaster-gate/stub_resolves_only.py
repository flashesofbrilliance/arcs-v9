#!/usr/bin/env python3
"""Fails-on-bad proof: a stub gate that checks only receipt_resolves. It reads case['input'] only.
It must wrongly VERIFY the false-with-receipt cases; if it does, the set can separate a real gate from a stub."""
import json, sys
path = sys.argv[1] if len(sys.argv) > 1 else "runtime/specs/farcaster-gate-falsifier-set.json"
cases = json.load(open(path))["cases"]
wrong = 0
for c in cases:
    got = "VERIFIED" if c["input"]["receipt_resolves"] else "NOT_VERIFIED"
    exp = c["answer_key"]["expected_verdict"]
    ok = got == exp
    wrong += not ok
    print(f'{c["id"]:4} stub={got:12} expected={exp:12} {"ok" if ok else "WRONG"}')
print(f"stub wrong on {wrong}/{len(cases)}")
sys.exit(0 if wrong >= 4 else 1)  # exit 0 = set caught the stub
