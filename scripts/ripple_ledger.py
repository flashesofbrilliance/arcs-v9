#!/usr/bin/env python3
"""ripple_ledger: one row per decision, with how reversible it is and what it costs to get wrong.

File: _QUEUE/ripple-ledger.jsonl, one JSON object per line:
  id, decision, door ("one-way" | "two-way"), reach (how many things sit downstream), time_cost_h, ruin ("low"|"medium"|"high"|"critical"),
  paths (globs this decision touches), derisk (the test or gate that must pass first), derisk_state ("OPEN"|"PASSED"|"NA"), owner, noted (date)

Rule (WORLD.md, ROM primitive 7 WRITE-LOCK): a one-way door whose ruin is high or critical does not START until derisk_state is PASSED.

  python3 scripts/ripple_ledger.py --check            validate every row; list one-way doors still open
  python3 scripts/ripple_ledger.py --list             the open one-way doors, deepest ruin first
  python3 scripts/ripple_ledger.py --touch a b ...    warn (exit 0) or --gate (exit 1) when the given paths hit an open one-way door
Stdlib only.
"""
import fnmatch, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "_QUEUE/ripple-ledger.jsonl")
RUIN = ["low", "medium", "high", "critical"]
REQ = ["id", "decision", "door", "reach", "time_cost_h", "ruin", "paths", "derisk", "derisk_state", "owner", "noted"]

def rows():
    out = []
    for n, line in enumerate(open(FILE, encoding="utf-8"), 1):
        line = line.strip()
        if line: out.append((n, json.loads(line)))
    return out

def problems(r):
    p = [f"missing {k}" for k in REQ if k not in r]
    if r.get("door") not in ("one-way", "two-way"): p.append("door must be one-way or two-way")
    if r.get("ruin") not in RUIN: p.append("ruin must be low, medium, high or critical")
    if r.get("derisk_state") not in ("OPEN", "PASSED", "NA"): p.append("derisk_state must be OPEN, PASSED or NA")
    if not isinstance(r.get("paths"), list): p.append("paths must be a list")
    if r.get("door") == "one-way" and r.get("derisk_state") == "NA": p.append("a one-way door cannot be NA: say what de-risks it")
    return p

def blocked(r):
    return r.get("door") == "one-way" and r.get("ruin") in ("high", "critical") and r.get("derisk_state") != "PASSED"

def main(a):
    rs = rows(); bad = 0
    for n, r in rs:
        for p in problems(r): print(f"✖ row {n} {r.get('id', '?')}: {p}"); bad += 1
    if "--touch" in a:
        paths = [x for x in a if not x.startswith("--")]; hit = []
        for n, r in rs:
            if blocked(r) and any(fnmatch.fnmatch(pa, g) or pa.startswith(g.rstrip("*")) for pa in paths for g in r.get("paths", [])): hit.append(r)
        for r in hit: print(f"⚠ one-way door not yet de-risked: {r['id']} ({r['ruin']} ruin). Needs first: {r['derisk']}")
        return 1 if (hit and "--gate" in a) else (1 if bad else 0)
    op = sorted([r for _, r in rs if blocked(r)], key=lambda r: -RUIN.index(r["ruin"]))
    if "--list" in a or "--check" in a or len(a) == 0:
        print(f"{len(rs)} decisions, {sum(1 for _, r in rs if r['door'] == 'one-way')} one-way, {len(op)} one-way with high or critical ruin and not yet de-risked")
        for r in op: print(f"  [{r['ruin']}] {r['id']}: {r['decision'][:80]}  -> first: {r['derisk'][:80]}")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
