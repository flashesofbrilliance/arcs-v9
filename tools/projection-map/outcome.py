#!/usr/bin/env python3
"""Outcome test, external label: did a later recorded call share a counterpart name/company? Zero model calls."""
import json, re, random, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import projection as P
D = Path(__file__).parent / "projection-data"; random.seed(7)
raw = json.loads((D / "manifest.json").read_text()); aud = {i[:8]: k for k, v in raw.items() if not k.startswith("_") for i in v}
GENERIC = set("""zach harris zachary x and with call interview 1-1 one catch up meeting min mins minute minutes check-in intro introductory
the a of for re to role about new discussion quick review touch base connect part conversation screen screening round panel
recruiter recruiting senior staff engineer product lead manager deployed forward ai fde demo debrief feedback check before 30
2026 hiring video team zoom follow-up follow up phase wrapping 1 2 arcs jam session profile targeting matching""".split())
T = [l.split("\t") for l in (D / "titles.tsv").read_text().splitlines()]
def keys(title): return {w for w in re.findall(r"[a-z][a-z.'-]+", title.lower()) if w not in GENERIC and len(w) > 2}
CUTOFF = "2026-10-26"   # calls after this with no follow-up are too recent to call dead
lab = {}
for cid, date, title in T:
    k = keys(title)
    later = [t for t in T if t[1] > date and keys(t[2]) & k]
    lab[cid] = "A" if later else ("N" if date > CUTOFF else "D")
pooled = json.loads((D / "pooled.json").read_text())
calls = {c["call"][:8]: c for c in pooled["calls"]}
CHK = r"(make sense|you know what i mean)"; FIL = r"\b(basically|literally|like,)"
rows = []
for f in (D / "raw_exact").glob("*.txt"):
    cid = f.stem[:8]
    if cid not in calls or lab.get(cid) not in ("A", "D"): continue
    mine = " ".join(l.split(":", 1)[1] for l in f.read_text().splitlines() if re.match(r"^(\[[\d:]+\] )?Microphone:", l)).lower()
    w = max(1, len(mine.split())); c = calls[cid]
    rows.append({"id": cid, "aud": aud[cid], "out": lab[cid], "mc": 10 * c["midcurve"] / max(1, c["zach_turns"]),
                 "share": c["zach_share"], "chk": 1000 * len(re.findall(CHK, mine)) / w, "fil": 1000 * len(re.findall(FIL, mine)) / w})
def test(R, key):
    a = [r[key] for r in R if r["out"] == "D"]; b = [r[key] for r in R if r["out"] == "A"]
    if min(len(a), len(b)) < 5: return None
    obs = st.mean(a) - st.mean(b); pool = a + b; k = len(a)
    hits = sum(abs(st.mean(x[:k]) - st.mean(x[k:])) >= abs(obs) for x in (random.sample(pool, len(pool)) for _ in range(10000)))
    return round(st.mean(a), 2), round(st.mean(b), 2), len(a), len(b), hits / 10000
from collections import Counter
print("labels:", Counter(lab[c] for c in calls if c in lab), "| by audience:", {a: dict(Counter(r["out"] for r in rows if r["aud"] == a)) for a in ["interview", "recruiter", "client", "peer"]})
def verdict(t, pred):
    if t is None: return "CAN'T TELL (<5 per side)"
    d, a, nd, na, p = t; ok = pred(d, a)
    s = "finding" if p < .05 else ("leaning" if p < .10 else "noise")
    return "%s  died %s vs advanced %s (n=%d/%d, p=%.3f, %s)" % ("TRUE " if ok else "FALSE", d, a, nd, na, p, s)
gt = lambda d, a: d > a; lt = lambda d, a: d < a
for name, scope in [("ALL", rows), ("interview+recruiter", [r for r in rows if r["aud"] in ("interview", "recruiter")]), ("peer", [r for r in rows if r["aud"] == "peer"])]:
    print("\n==", name)
    print("P9  mid-curve higher in died:", verdict(test(scope, "mc"), gt))
    print("P10 talk share higher in died:", verdict(test(scope, "share"), gt))
    print("P11 check-ins lower in died: ", verdict(test(scope, "chk"), lt))
    if name == "interview+recruiter": print("P12 filler higher in died:     ", verdict(test(scope, "fil"), gt))
json.dump(lab, open(D / "outcome_labels.json", "w"))
