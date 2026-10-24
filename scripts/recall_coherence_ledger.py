#!/usr/bin/env python3
"""recall_coherence_ledger.py: recall of coherence_sweep's contradiction check on the ledger's claim/delta pairs.

Protocol registered as asm-020 in _STATE/assumptions.jsonl BEFORE this ran. For each row of
_STATE/falsification-ledger.jsonl, two pseudo-notes (body = claim, body = delta; date = row ts) go to
coherence_sweep.sweep_memory with today fixed at 2026-10-18 and stale_days 45. A row is caught if any
finding has check == 'contradiction'. Recall = caught / rows. Read-only, stdlib only, deterministic.

  python3 scripts/recall_coherence_ledger.py [--ledger PATH] [--bar 0.5]
"""
import argparse, datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coherence_sweep as cs  # noqa: E402

TODAY = dt.date(2026, 10, 18)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(HERE), "_STATE", "falsification-ledger.jsonl"))
    ap.add_argument("--bar", type=float, default=0.5)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.ledger) if l.strip()]
    caught = []
    for r in rows:
        d = dt.date.fromisoformat(r["ts"][:10])
        notes = {"claim": ({"_date": d}, r["claim"]), "delta": ({"_date": d}, r["delta"])}
        found = [f for f in cs.sweep_memory(notes, "", os.path.dirname(HERE), TODAY, 45) if f["check"] == "contradiction"]
        if found:
            caught.append(r["id"])
    n = len(rows)
    rec = len(caught) / n if n else 0.0
    print(f"rows: {n}  caught: {len(caught)}  recall: {rec:.4f}  bar: {a.bar}  -> {'HOLD' if rec >= a.bar else 'FALSIFIED'}")
    print("caught ids:", ", ".join(caught) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
