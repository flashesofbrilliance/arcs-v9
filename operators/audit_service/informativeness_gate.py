#!/usr/bin/env python3
"""Informativeness RATCHET gate — wires informativeness_sensor.py into CI/pre-commit.

The sensor is a pure detector: it flags every degenerate field. But the audit corpus
ALREADY carries known-degenerate signal fields (the SAGE degeneracy this repo diagnosed
2026-09-02) — so a raw sensor gate would be permanently red on an unfixed-but-known problem,
which is noise, not a gate. This wrapper turns it into a ratchet: it blocks only on NEW
degeneracy beyond a committed baseline. Existing debt is frozen and visible; regressions fail.

  exit 0  — degenerate fields ⊆ baseline.known_degenerate  (no new degeneracy)
  exit 1  — a NEW field went degenerate, OR a baselined-informative field regressed

Baseline: operators/audit_service/informativeness_baseline.json (edit deliberately, with a
commit note, when the underlying data problem is genuinely fixed — that is the ratchet turning
the right way). Deterministic, stdlib-only — a grep can't rationalize a pass.
"""
import sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from informativeness_sensor import get_path, informativeness, verdict  # noqa: E402


def load_corpus(path):
    """Accept a JSON array or JSONL; return list of records."""
    full = path if os.path.isabs(path) else os.path.join(HERE, path)
    with open(full) as fh:
        text = fh.read().strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main():
    base_path = os.path.join(HERE, "informativeness_baseline.json")
    baseline = json.load(open(base_path))
    known = set(baseline["known_degenerate"])
    recs = load_corpus(baseline["corpus"])
    fields = baseline["fields"]

    print(f"INFORMATIVENESS RATCHET · corpus={baseline['corpus']} · n={len(recs)} · {len(fields)} fields")
    print(f"{'FIELD':<40}{'DISTINCT':>9}{'ENTROPY':>9}  VERDICT")
    print("-" * 72)
    degenerate = set()
    for f in fields:
        hnorm, distinct, _ = informativeness([get_path(r, f) for r in recs])
        v = verdict(distinct, hnorm)
        if v == "DEGENERATE":
            degenerate.add(f)
        flag = "  (baselined)" if (v == "DEGENERATE" and f in known) else ""
        print(f"{f:<40}{distinct:>9}{hnorm:>9.3f}  {v}{flag}")
    print("-" * 72)

    new_degenerate = sorted(degenerate - known)
    healed = sorted(known - degenerate)
    if healed:
        print(f"↑ HEALED since baseline ({len(healed)}): {', '.join(healed)} "
              f"— tighten the baseline (drop these from known_degenerate).")
    if new_degenerate:
        print(f"\n✗ REGRESSION — NEW degenerate field(s) ({len(new_degenerate)}): {', '.join(new_degenerate)}")
        print("  a field that carried information went constant. Fix the data path or, if intended,")
        print("  add it to informativeness_baseline.json with a commit note explaining why.")
        sys.exit(1)
    print(f"\n✓ no new degeneracy (baseline debt: {len(known & degenerate)} known-degenerate held)")
    sys.exit(0)


if __name__ == "__main__":
    main()
