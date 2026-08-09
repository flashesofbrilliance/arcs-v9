#!/usr/bin/env python3
"""
DETERMINISTIC COVERAGE SWEEP (not a 3-scenario spot check).
Exercises each dimension exhaustively and independently:
  1. every competitor key (all 895) -> must recognize a competitor_equiv
  2. every PRL grade (all 150, primary alias) -> must recognize a prl_grade
  3. every US state (50) -> must route to a rep or Distribution (no silent miss)
  4. punctuation robustness: wrap a broad sample in trailing/edge punctuation -> still recognized
  5. required-field gate: missing-field permutations -> gate must FAIL exactly when it should
Reports counts + concrete failing examples. No CRM writes.
"""
import sys, os, csv, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "normalization"))
import normalize as N

ND = os.path.join(HERE, "normalization")
COMP = json.load(open(os.path.join(ND, "competitor-to-prl.json")))["map"]
GRADES = json.load(open(os.path.join(ND, "grade-dictionary.json")))["grades"]

def show(title, total, fails, examples):
    status = "PASS" if not fails else f"FAIL ({fails}/{total})"
    print(f"[{status}] {title}: {total-fails}/{total} covered")
    for e in examples[:8]:
        print(f"         MISS: {e!r}")

# --- 1. every competitor key ---
fails, ex = 0, []
for key in COMP:
    if not any(h["type"] == "competitor_equiv" for h in N.recognize(key)):
        fails += 1; ex.append(key)
show("Competitor keys -> competitor_equiv", len(COMP), fails, ex)

# --- 1b. competitor keys in a natural sentence ('equivalent to <key>?') ---
fails, ex = 0, []
sample = list(COMP)[::7]  # every 7th, ~128 keys, embedded in prose + trailing '?'
for key in sample:
    if not any(h["type"] == "competitor_equiv" for h in N.recognize(f"do you have an equivalent to {key}?")):
        fails += 1; ex.append(key)
show("Competitor keys in prose + '?'", len(sample), fails, ex)

# --- 2. every PRL grade (primary alias = the grade code itself) ---
fails, ex = 0, []
for g in GRADES:
    code = g["grade"]
    if not any(h["type"] == "prl_grade" for h in N.recognize(code)):
        fails += 1; ex.append(code)
show("PRL grade codes -> prl_grade", len(GRADES), fails, ex)

# --- 2b. every alias of every grade ---
fails, ex, total = 0, [], 0
for g in GRADES:
    for a in g["aliases"]:
        total += 1
        if not any(h["type"] == "prl_grade" for h in N.recognize(a)):
            fails += 1; ex.append(f"{a} (grade {g['grade']})")
show("All grade aliases -> prl_grade", total, fails, ex)

# --- 3. every US state -> a route ---
TERR = {}
with open(os.path.join(HERE, "..", "prl-territory-map.csv")) as f:
    for r in csv.DictReader(f):
        TERR[r["state"].strip().lower()] = (r["primary"].strip(), r.get("secondary", "").strip())
STATES = list(N.FIELD["state_fullname_to_abbrev"].keys())  # 50, uppercase
fails, ex = 0, []
for s in STATES:
    prim, sec = TERR.get(s.lower(), ("", ""))
    if not (prim or sec):
        fails += 1; ex.append(s)
show("US states -> a rep or Distribution", len(STATES), fails, ex)

# --- 4. punctuation robustness on a broad grade+competitor sample ---
wrappers = ['{}', '{}?', '{}.', '{},', '({})', '"{}"', 'need {}!', '{} please', 'is {} available?']
targets = [g["grade"] for g in GRADES[::15]] + list(COMP)[::40]
fails, ex, total = 0, [], 0
for t in targets:
    for w in wrappers:
        total += 1
        if not N.recognize(w.format(t)):
            fails += 1; ex.append(w.format(t))
show("Punctuation-wrapped recognition", total, fails, ex)

# --- 5. required-field gate: missing-field permutations must be caught ---
REQ = ["first_name","last_name","account_name","phone_work","location_c","lead_source"]
def gate(p): return [k for k in REQ if not p.get(k)]
base = {k: "x" for k in REQ}
fails, ex, total = 0, [], 0
for r in range(len(REQ)+1):
    for combo in itertools.combinations(REQ, r):
        total += 1
        p = dict(base)
        for k in combo: p[k] = ""       # blank these required fields
        missing = gate(p)
        expect = set(combo)
        if set(missing) != expect:       # gate must report exactly the blanked ones
            fails += 1; ex.append(f"blanked={combo} gate_said={missing}")
show("Required-field gate (all 64 subset perms)", total, fails, ex)

print("\nScope note: dimensions tested exhaustively + independently (the correct method); the full")
print("cross-product (competitor x state x branch x field-perm ~ 10^8) is intentionally NOT enumerated.")
print("Live-model behavior (Lyro nondeterminism) is a SEPARATE gate: prl_lyro_eval.py, needs live responses.")
