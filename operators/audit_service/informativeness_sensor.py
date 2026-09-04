#!/usr/bin/env python3
"""Informativeness / echo sensor — the deceipt-detector's mechanical core.

Deterministic, stdlib-only, un-counterfeitable: a grep can't confabulate a pass.
Given a JSON array of records + field paths, computes per-field informativeness
(distinct count + normalized Shannon entropy over the value distribution) and flags:
  - DEGENERATE (distinct == 1): present-but-contentless — a deceipt in receipt clothing.
  - THIN (0 < entropy < THIN_H): low information, near-constant.
  - INFORMATIVE: carries real variance.

This is the *echo test* generalized: a signal whose value never varies across the
corpus carries zero information no matter how present it looks. Non-zero exit when any
field is degenerate, so a CI/pre-commit gate can block on a deceipt.

Usage:
  python3 informativeness_sensor.py records.json [field.path ...]
  (dot notation indexes nested dicts; omit fields to auto-scan top-level keys)
"""
import sys, json, math
from collections import Counter

THIN_H = 0.15  # normalized-entropy floor below which a field is "thin"


def _key(v):
    return json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v


def get_path(rec, path):
    cur = rec
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def informativeness(values):
    vals = [_key(v) for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return 0.0, 0, 0
    counts = Counter(vals)
    distinct = len(counts)
    if distinct <= 1:
        return 0.0, distinct, n
    H = -sum((c / n) * math.log2(c / n) for c in counts.values())
    Hmax = math.log2(distinct)
    return (H / Hmax if Hmax > 0 else 0.0), distinct, n


def verdict(distinct, hnorm):
    if distinct <= 1:
        return "DEGENERATE"   # deceipt: present-but-contentless
    if hnorm < THIN_H:
        return "THIN"
    return "INFORMATIVE"


def main():
    if len(sys.argv) < 2:
        print("usage: informativeness_sensor.py records.json [field.path ...]")
        sys.exit(2)
    recs = json.load(open(sys.argv[1]))
    if not isinstance(recs, list):
        recs = [recs]
    fields = sys.argv[2:] or sorted({k for r in recs if isinstance(r, dict) for k in r})
    print(f"INFORMATIVENESS SENSOR · n={len(recs)} records · {len(fields)} fields\n")
    print(f"{'FIELD':<26}{'DISTINCT':>9}{'ENTROPY':>9}  VERDICT")
    print("-" * 58)
    degenerate = []
    for f in fields:
        hnorm, distinct, _ = informativeness([get_path(r, f) for r in recs])
        v = verdict(distinct, hnorm)
        if v == "DEGENERATE":
            degenerate.append(f)
        print(f"{f:<26}{distinct:>9}{hnorm:>9.3f}  {v}")
    print("-" * 58)
    if degenerate:
        print(f"\n⚠ DECEIPTS DETECTED ({len(degenerate)}): {', '.join(degenerate)}")
        print("  present-but-contentless — distinct==1 across the corpus. Zero information.")
    else:
        print("\nno degenerate fields")
    sys.exit(1 if degenerate else 0)


if __name__ == "__main__":
    main()
