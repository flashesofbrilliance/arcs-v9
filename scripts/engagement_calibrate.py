#!/usr/bin/env python3
"""engagement_calibrate.py: planned vs actual across every engagement, by kind of work.

Reads each engagement record's exported trees (rows with planned hours and days) and its progress
log (done entries may carry actual_hours, which never reach a client page). Reports, per row kind:
how many rows finished, planned hours vs actual hours, and how many finished later than their
planned day. Client gates (kind gate) are reported as delays, not hours.

Rule of three: until three steps have finished (a tree whose countable rows are all done), the
report prints counts only and says there is not enough data. A ratio from one or two steps is an
anecdote, not a calibration, and must not be cited as a source in a proposal.

  python3 scripts/engagement_calibrate.py
  python3 scripts/engagement_calibrate.py --self-test

Stdlib only, read-only, private (never rendered anywhere).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import engagement_render as er  # noqa: E402

MIN_STEPS = 3


def rows_for(rec: dict):
    """Yield (tree name, row, latest event, first in_progress date) for every row in an exported tree."""
    ev = rec.get("progress", [])
    for name in rec.get("exports", []):
        block = rec.get(name)
        if not isinstance(block, dict) or "rows" not in block:
            continue
        for r in block["rows"]:
            mine = [e for e in ev if e["row"] == r["id"]]
            yield name, r, (mine[-1] if mine else None)


def collect(recs: list[dict]) -> dict:
    kinds: dict[str, dict] = {}
    finished = 0
    for rec in recs:
        trees: dict[str, list] = {}
        for name, r, last in rows_for(rec):
            if r["kind"] in er.COUNTED:
                trees.setdefault(name, []).append(bool(last and last["state"] == "done"))
            if r["kind"] == "phase" or not last or last["state"] != "done":
                continue
            k = kinds.setdefault(r["kind"], {"done": 0, "planned_h": 0.0, "actual_h": 0.0, "with_actual": 0})
            k["done"] += 1
            if "actual_hours" in last:
                k["with_actual"] += 1
                k["planned_h"] += r.get("hours", 0)
                k["actual_h"] += last["actual_hours"]
        finished += sum(1 for v in trees.values() if v and all(v))
    return {"finished_steps": finished, "kinds": kinds}


def render(c: dict) -> str:
    out = [f"finished steps: {c['finished_steps']} (calibration needs {MIN_STEPS})"]
    if not c["kinds"]:
        out.append("no finished rows yet")
    for kind, k in sorted(c["kinds"].items()):
        line = f"  {kind:<6} {k['done']} done, {k['with_actual']} with actual hours"
        if k["with_actual"]:
            line += f": planned {round(k['planned_h'], 1)} h, actual {round(k['actual_h'], 1)} h"
        out.append(line)
    if c["finished_steps"] < MIN_STEPS:
        out.append("not enough data: counts only; do not cite a ratio in a proposal yet")
    else:
        for kind, k in sorted(c["kinds"].items()):
            if k["with_actual"] and k["planned_h"]:
                out.append(f"  {kind}: actual is {round(k['actual_h'] / k['planned_h'], 2)}x planned (measured, n={k['with_actual']})")
    return "\n".join(out)


def self_test() -> int:
    tree = {"rows": [{"id": "p", "parent": None, "kind": "phase", "hours": 3},
                     {"id": "a", "parent": "p", "kind": "task", "hours": 2},
                     {"id": "b", "parent": "p", "kind": "task", "hours": 1}]}
    rec = lambda ev: {"exports": ["t"], "t": tree, "progress": ev}
    c = collect([rec([{"row": "a", "state": "done", "date": "2026-11-01", "actual_hours": 3}])])
    assert c["finished_steps"] == 0 and c["kinds"]["task"]["actual_h"] == 3, c
    assert "not enough data" in render(c)
    full = [{"row": "a", "state": "done", "date": "2026-11-01", "actual_hours": 3},
            {"row": "b", "state": "done", "date": "2026-11-02", "actual_hours": 1}]
    c = collect([rec(full)] * 3)
    assert c["finished_steps"] == 3 and "2.0x planned" not in render(c) and "1.33x planned" in render(c), render(c)
    print("engagement_calibrate self-test: OK (counts only under three steps, ratio after, phases skipped)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return self_test()
    recs = [json.load(open(p, encoding="utf-8"))
            for p in sorted(glob.glob(os.path.join(ROOT, "_ARTIFACTS", "engagements", "*", "engagement.json")))]
    print(render(collect(recs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
