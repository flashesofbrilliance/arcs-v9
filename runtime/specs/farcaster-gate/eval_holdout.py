#!/usr/bin/env python3
"""Pre-registered line 4. Interpretation (flagged to parent): hold-out has 4 cases of mixed class, so 'recall >= 3 of 4' is read as G2 verdict correct on >= 3 of 4 cases."""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import gates
cases = json.load(open("runtime/specs/farcaster-gate/sealed/holdout.json"))["cases"]
ok = sum((gates.g2(c["input"]) and "VERIFIED" or "NOT_VERIFIED") == c["answer_key"]["expected_verdict"] for c in cases)
pos = [c for c in cases if c["answer_key"]["expected_verdict"] == "NOT_VERIFIED"]
rec = sum(not gates.g2(c["input"]) for c in pos)
print(json.dumps({"cases": len(cases), "G2_correct": ok, "positives": len(pos), "G2_positives_withheld": rec, "overfit_flag": ok < 3}))
sys.exit(0 if ok >= 3 else 1)
