#!/usr/bin/env python3
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import gates
r = gates.evaluate(json.load(open("runtime/specs/farcaster-gate-falsifier-set.json"))["cases"])
print(json.dumps(r, indent=1))
f2f5 = [c for c in json.load(open("runtime/specs/farcaster-gate-falsifier-set.json"))["cases"] if c["id"] in ("F2","F3","F4","F5")]
g0_missed = sum(gates.g0(c["input"]) for c in f2f5)
res = {
 "line1_G2_withholds_all_positives_and_0_true_wrong": not r["G2"]["missed_positives"] and not r["G2"]["wrongly_withheld_true"],
 "line2_G0_misses_ge3_of_F2_F5": g0_missed >= 3,
 "line3_recall_G0<G1<=G2": r["G0"]["recall"] < r["G1"]["recall"] <= r["G2"]["recall"]}
print(json.dumps(res, indent=1))
sys.exit(0 if all(res.values()) else 1)
