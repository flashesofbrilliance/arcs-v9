#!/usr/bin/env python3
"""Second hold-out (H5-H8), separately labelled. Not a pre-registered pass line; reported as information. Reports per-gate verdict correctness."""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import gates
cases = json.load(open("runtime/specs/farcaster-gate/sealed/holdout2.json"))["cases"]
res = {}
for n, g in gates.GATES.items():
    res[n] = {c["id"]: ("VERIFIED" if g(c["input"]) else "NOT_VERIFIED") for c in cases}
exp = {c["id"]: c["answer_key"]["expected_verdict"] for c in cases}
out = {n: {"correct": sum(v[i] == exp[i] for i in exp), "of": len(exp), "wrong": [i for i in exp if v[i] != exp[i]]} for n, v in res.items()}
print(json.dumps({"label": "hold-out 2 (scope/outcome mismatch), post-seal, not a pre-registered line", "expected": exp, **out}, indent=1))
