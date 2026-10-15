#!/usr/bin/env python3
"""Interlock invariant over a log of routed tasks (stdlib only, read-only).

Tiers: 0 mechanical, 1 small, 2 mid, 3 top. One JSON object per line:
  {"task": "t1", "irreversible": false, "steps": [{"tier": 0, "passed": false}, {"tier": 1, "passed": true}]}
Invariant: a task enters at tier 0; each next step is exactly one tier up;
a step is added only after a failed check, or (irreversible tasks) after any
check below the top; a reversible task ends on a pass or at the top; an
irreversible task ends at the top gate. See _PATTERNS/2026-10-15-tier-fit-goldilocks.md.

  tier_ladder_check.py LOG.jsonl     exit 1 on any violation
  tier_ladder_check.py --self-test   clean logs pass; planted skip and downgrade must fail
"""
import json, sys

TOP = 3


def violations(task):
    v, steps = [], task.get("steps", [])
    if not steps:
        return ["no steps"]
    if steps[0]["tier"] != 0:
        v.append(f"enters at tier {steps[0]['tier']}, not 0")
    irr = bool(task.get("irreversible"))
    for a, b in zip(steps, steps[1:]):
        if b["tier"] != a["tier"] + 1:
            v.append(f"skip or regress {a['tier']} -> {b['tier']}")
        if a["passed"] and not (irr and a["tier"] < TOP):
            v.append(f"escalated after a pass at tier {a['tier']}")
    last = steps[-1]
    if irr and last["tier"] != TOP:
        v.append(f"irreversible task exits at tier {last['tier']}, below top")
    if not irr and not last["passed"] and last["tier"] != TOP:
        v.append(f"reversible task stopped at tier {last['tier']} without a pass")
    return v


def check(rows):
    bad = {}
    for t in rows:
        x = violations(t)
        if x:
            bad[t.get("task", "?")] = x
    return bad


def s(*pairs):
    return [{"tier": t, "passed": p} for t, p in pairs]


def self_test():
    clean = [
        {"task": "cheap", "irreversible": False, "steps": s((0, True))},
        {"task": "climb", "irreversible": False, "steps": s((0, False), (1, False), (2, True))},
        {"task": "irr", "irreversible": True, "steps": s((0, True), (1, True), (2, True), (3, True))},
    ]
    skip = [{"task": "skip", "irreversible": False, "steps": s((0, False), (2, True))}]
    down = [{"task": "down", "irreversible": True, "steps": s((0, True), (1, True))}]
    ok = not check(clean) and bool(check(skip)) and bool(check(down))
    print("self-test:", "PASS" if ok else "FAIL",
          f"(clean={len(check(clean))} skip={len(check(skip))} downgrade={len(check(down))} violations)")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    bad = check(rows)
    for k, x in bad.items():
        print(f"VIOLATION {k}: {'; '.join(x)}")
    print(f"{len(rows)} tasks, {len(bad)} violating")
    sys.exit(1 if bad else 0)
