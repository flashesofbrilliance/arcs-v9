#!/usr/bin/env python3
"""Pool projection metrics by audience. Usage: pool.py  (reads manifest.json + raw_exact/*.txt)"""
import json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import projection as P
D = Path(__file__).parent / "projection-data"; raw = json.loads((D / "manifest.json").read_text()); UNSURE = set(raw.get("_unsure", []))
man = {k: v for k, v in raw.items() if not k.startswith("_")}
import random; random.seed(7)
EXCL = "--sure-only" in sys.argv
aud = {i: k for k, v in man.items() for i in v}
allc = [dict(P.score(f), audience=aud.get(f.stem, "?")) for f in sorted((D / "raw_exact").glob("*.txt"))]
# Data-quality rule (stated before results): drop near-empty and single-channel recordings.
calls, dropped = [], []
for c in allc:
    tot = c["zach_words"] + c["other_words"]
    if EXCL and c["call"] in UNSURE: continue
    (dropped if tot < 300 or c["other_words"] / max(1, tot) < 0.10 else calls).append(c)
print("dropped:", [(c["call"][:8], c["audience"], c["zach_words"], c["other_words"]) for c in dropped])
m = lambda xs: (round(st.mean(xs), 2) if xs else None)
print("calls scored:", len(calls), {a: sum(c["audience"] == a for c in calls) for a in man})
G = {}
for a in list(man) + ["ALL"]:
    cs = [c for c in calls if a in ("ALL", c["audience"])]; R = [r for c in cs for r in c["rows"]]
    L = [r for r in R if r["laconic"]]; mc = [r for r in L if r["grug"]]; lp = [r for r in L if not r["grug"]]
    G[a] = {"calls": len(cs), "talk_share": m([c["zach_share"] for c in cs]),
            "q_ratio_zach_over_them": m([c["zach_questions"] / max(1, c["other_questions"]) for c in cs]),
            "long_turn_share": m([len([r for r in c["rows"] if r["laconic"]]) / max(1, c["zach_turns"]) for c in cs]),
            "midcurve_per10": m([10 * c["midcurve"] / max(1, c["zach_turns"]) for c in cs]),
            "lift_midcurve": m([r["lift"] for r in mc if r["lift"] is not None]), "n_mc": len([r for r in mc if r["lift"] is not None]),
            "lift_long_plain": m([r["lift"] for r in lp if r["lift"] is not None]), "n_lp": len([r for r in lp if r["lift"] is not None]),
            "lift_short": m([r["lift"] for r in R if not r["laconic"] and r["lift"] is not None])}
for a, g in G.items(): print(a, g)
v = {}
v["P5b pooled: midcurve lift < long-plain lift"] = None if G["ALL"]["n_mc"] < 3 else G["ALL"]["lift_midcurve"] < G["ALL"]["lift_long_plain"]
gt = lambda a, b: None if None in (a, b) else a > b
v["P6 talk share peer > interview"] = gt(G["peer"]["talk_share"], G["interview"]["talk_share"])
v["P7 midcurve rate peer > interview"] = gt(G["peer"]["midcurve_per10"], G["interview"]["midcurve_per10"])
for a in man:
    v["P8 [%s] midcurve lift < long-plain lift" % a] = None if G[a]["n_mc"] < 3 or G[a]["lift_long_plain"] is None else G[a]["lift_midcurve"] < G[a]["lift_long_plain"]
def perm(R):
    a = [r["lift"] for r in R if r["grug"]]; b = [r["lift"] for r in R if not r["grug"]]
    if len(a) < 3 or len(b) < 3: return None
    obs = st.mean(a) - st.mean(b); pool = a + b; k = len(a); hits = 0
    for _ in range(10000):
        random.shuffle(pool)
        if abs(st.mean(pool[:k]) - st.mean(pool[k:])) >= abs(obs): hits += 1
    return {"gap": round(obs, 2), "n_dense": len(a), "n_plain": len(b), "p": hits / 10000}
PT = {}
for a in list(man) + ["ALL"]:
    R = [r for c in calls if a in ("ALL", c["audience"]) for r in c["rows"] if r["laconic"] and r["lift"] is not None]
    PT[a] = perm(R); print("permutation", a, PT[a])
for k, x in v.items(): print("TRUE " if x else ("FALSE" if x is False else "CAN'T TELL"), k)
(D / ("pooled_sure.json" if EXCL else "pooled.json")).write_text(json.dumps({"sure_only": EXCL, "permutation": PT, "groups": G, "verdicts": v, "calls": [{k: c[k] for k in c if k != "rows"} for c in calls]}, indent=1))
