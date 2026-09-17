#!/usr/bin/env python3
"""PRL dependency-map reconciliation eval (Frustration-Gate for the recoil->go-live drift class).

Diffs the structured dependency map against the recoil-close SSOT and flags:
  1. broken depends_on edges                          (HARD FAIL)
  2. backward drift: mapped item with no sources       (HARD FAIL)
  3. an OPEN SSOT belief no mapped item bears on        (HARD FAIL)
  4. forward drift: an SSOT next_step not represented   (WARN, heuristic)
  5. items that bear on an OPEN belief                  (INFO, resolve at call)
  6. --baseline <old map>: items whose status changed   (ACTION: re-score linked
     beliefs anterior->posterior)

Stdlib only. Usage:
  python3 prl_depmap_check.py [--map prl-dependency-map.json] [--ssot <path>] [--baseline <old-map.json>]
Exit 0 clean, 1 on any HARD FAIL. Lesson banked in memory
recoil-ssot-compresses-dependency-set-reconcile-vs-buildsheets.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# repo root = three levels up from _ARTIFACTS/prl-1-2-close-loop/
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def words(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default=os.path.join(HERE, "prl-dependency-map.json"))
    ap.add_argument("--ssot", default=None)
    ap.add_argument("--baseline", default=None, help="prior map JSON to diff status against")
    args = ap.parse_args()

    dm = load(args.map)
    items = dm["items"]
    by_id = {it["id"]: it for it in items}
    ssot_path = args.ssot or os.path.join(ROOT, dm["ssot"])
    ssot = load(ssot_path)

    hard, warn, info, action = [], [], [], []

    # 0. investigation pre-work gate (P-1): the plan is not trusted until the corpus is exhausted
    prework = dm.get("investigation_prework")
    if prework is not None:
        status = str(prework.get("status", "")).lower()
        if status != "complete":
            hard.append(f"[pre-work] investigation gate status is '{status or 'unset'}' (not complete) -> plan + execution not trusted until the doc corpus is exhausted (false-null risk)")
            for nr in prework.get("not_yet_reconciled", []):
                info.append(f"[pre-work] not yet reconciled: {nr}")

    # 1. broken edges
    for it in items:
        for dep in it.get("depends_on", []):
            if dep not in by_id:
                hard.append(f"[edge] {it['id']} depends_on '{dep}' which is not in the map")

    # 2. backward drift
    for it in items:
        if not it.get("sources"):
            hard.append(f"[backward] {it['id']} has no sources (mapped but untraceable)")

    # belief tables
    beliefs = {b["id"]: b for b in ssot.get("beliefs", [])}
    open_beliefs = {bid for bid, b in beliefs.items() if str(b.get("verdict", "")).upper() == "OPEN"}
    covered = set()
    for it in items:
        for b in it.get("beliefs", []):
            covered.add(b)
            if b in open_beliefs:
                info.append(f"[open-belief] {it['id']} ({it['jtbd']}) bears on OPEN belief {b} -> resolve/verify")

    # 3. open belief with no coverage
    for b in open_beliefs:
        if b not in covered:
            hard.append(f"[belief-coverage] OPEN belief {b} is not borne by any mapped item")

    # 4. forward drift: SSOT next_steps not represented in map (heuristic keyword overlap)
    item_word_bags = [(it["id"], words(it["jtbd"]) | words(it.get("note", ""))) for it in items]
    for ns in ssot.get("next_steps", []):
        nw = words(ns.get("text", ""))
        # strip generic words
        nw -= {"the","a","an","to","and","of","in","on","for","it","is","that","this","with","be","at","or","do","not","get","run","before","after","then","into","from","your","you","can","will"}
        best = max((len(nw & bag) for _id, bag in item_word_bags), default=0)
        if best < 2:  # weak/no representation
            snippet = (ns.get("text", "")[:80] + "...") if len(ns.get("text", "")) > 80 else ns.get("text", "")
            warn.append(f"[forward] SSOT next_step may be unmapped: \"{snippet}\"")

    # 6. baseline status diff -> belief re-score
    if args.baseline:
        old = {it["id"]: it for it in load(args.baseline)["items"]}
        for it in items:
            o = old.get(it["id"])
            if o and o.get("status") != it.get("status"):
                bl = ",".join(it.get("beliefs", [])) or "(none)"
                action.append(f"[re-score] {it['id']} status {o.get('status')} -> {it.get('status')}; re-score beliefs {bl} (anterior->posterior)")
            if not o:
                bl = ",".join(it.get("beliefs", [])) or "(none)"
                action.append(f"[re-score] {it['id']} is NEW since baseline; check it doesn't move beliefs {bl}")
        for oid in old:
            if oid not in by_id:
                action.append(f"[re-score] {oid} was DROPPED since baseline; confirm intentional, not silent loss")

    def dump(title, rows):
        if rows:
            print(f"\n{title} ({len(rows)})")
            for r in rows:
                print("  " + r)

    print(f"PRL dependency-map check · map={os.path.relpath(args.map, ROOT)} · items={len(items)} · SSOT beliefs={len(beliefs)} (open: {sorted(open_beliefs) or 'none'})")
    dump("HARD FAIL", hard)
    dump("WARN (forward drift, heuristic)", warn)
    dump("INFO (open-belief bearers)", info)
    dump("ACTION (belief re-score)", action)
    if not (hard or warn or info or action):
        print("\nclean: no drift, all edges resolved, all open beliefs covered.")
    print()
    return 1 if hard else 0

if __name__ == "__main__":
    sys.exit(main())
