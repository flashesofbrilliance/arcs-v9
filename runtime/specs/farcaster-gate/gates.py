#!/usr/bin/env python3
"""Reference gates G0/G1/G2 exactly as defined in _PROPOSALS/farcaster/preregistration.md. Inputs only (case['input'])."""
import json, re, sys
from datetime import date
STOP = set("that this with from have will were been they them then than also into only over such what when your their about which would could should there these those more most some does did not for and the are was but can all any its our out one two use used using".split())
def toks(s): return {t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) >= 4 and t not in STOP}
def d(s): return date.fromisoformat(s)
def g0(i): return i["receipt_resolves"]
def g1(i):
    if not g0(i): return False
    overlap = len(toks(i["claim"]) & toks(i["receipt_excerpt"])) >= 2
    age = (d(i["claim_date"]) - d(i["receipt_date"])).days
    return overlap and 0 <= age <= 30
def g2(i):
    if not g1(i): return False
    first = (i["receipt_author"].split() or [""])[0].lower()
    return first != i["claim_author"].lower()
GATES = {"G0": g0, "G1": g1, "G2": g2}
def evaluate(cases):
    out = {}
    pos = [c for c in cases if c["answer_key"]["expected_verdict"] == "NOT_VERIFIED"]
    neg = [c for c in cases if c["answer_key"]["expected_verdict"] == "VERIFIED"]
    for n, g in GATES.items():
        missed = [c["id"] for c in pos if g(c["input"])]
        wrong = [c["id"] for c in neg if not g(c["input"])]
        out[n] = {"recall": round((len(pos) - len(missed)) / len(pos), 3), "positives": len(pos), "missed_positives": missed, "wrongly_withheld_true": wrong}
    return out
if __name__ == "__main__":
    cases = json.load(open(sys.argv[1]))["cases"]
    print(json.dumps(evaluate(cases), indent=1))
