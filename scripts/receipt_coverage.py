#!/usr/bin/env python3
"""receipt_coverage: share of decision receipts since the Sprint 5 start that carry both job_id and tool_id. Stdlib, read-only.

The 2026-11-03 coverage check (test 1, _PATTERNS/2026-10-20-jtbd-s5-preregistration.md: at least 70%, else make the
fields mandatory) as one command. It pre-registers nothing: the bar and the start (runtime/specs/jtbd-s5/config.json,
2026-10-20T16:36:24Z) are read, never set here. Counting reuses jtbd_edge_weights.eligible (distinct receipt_id,
event_at in [start, now]), so this number and the drift report's coverage line can never disagree.

Read path: the repo's existing local export of public.decision_receipt
(_STATE/job-search/universe/sources/decision-receipts.json). --export refreshes it first through
scripts/universe_receipts_adapter.py --export (supabase CLI, a SELECT only). Writes nothing else.

  python3 scripts/receipt_coverage.py [--export] [--json]
  python3 scripts/receipt_coverage.py --self-test
Exit: 0 report printed · 1 no export.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jtbd_edge_weights as jew  # noqa: E402

BAR = 0.70  # pre-registered, test 1; restated here only for the PASS/BELOW label


def coverage(rows, start, now=None):
    el = jew.eligible(rows, start, now)
    both = [r for r in el if r.get("job_id") and r.get("tool_id")]
    missing = [(r["receipt_id"], "job_id" if not r.get("job_id") else "", "tool_id" if not r.get("tool_id") else "")
               for r in el if not (r.get("job_id") and r.get("tool_id"))]
    share = round(len(both) / len(el), 3) if el else None
    return {"start": start.isoformat() if start else None, "receipts_since_start": len(el), "with_job_and_tool": len(both),
            "share": share, "bar": BAR, "verdict": None if share is None else ("PASS" if share >= BAR else "BELOW"),
            "missing": [{"receipt_id": i, "lacks": [x for x in (a, b) if x]} for i, a, b in missing]}


def render(c):
    head = (f"receipt coverage: since {c['start']} · {c['receipts_since_start']} receipts · "
            f"{c['with_job_and_tool']} with job_id and tool_id")
    if c["share"] is None:
        return head + " · no receipts yet"
    lines = [head + f" · {c['share']:.0%} (bar {c['bar']:.0%}: {c['verdict']})"]
    lines += [f"  lacks {'+'.join(m['lacks'])}: {m['receipt_id']}" for m in c["missing"]]
    return "\n".join(lines)


def self_test():
    s = dt.datetime(2026, 10, 20, 16, 36, 24, tzinfo=dt.timezone.utc)
    now = dt.datetime(2026, 11, 3, tzinfo=dt.timezone.utc)
    rows = [{"receipt_id": "old", "event_at": "2026-10-19T00:00:00Z"},
            {"receipt_id": "a", "event_at": "2026-10-21T00:00:00Z", "job_id": "job:backlog:x", "tool_id": "tool:script:y.py"},
            {"receipt_id": "a", "event_at": "2026-10-21T00:00:00Z"},
            {"receipt_id": "b", "event_at": "2026-10-22T00:00:00Z", "job_id": "job:backlog:x"},
            {"receipt_id": "c", "event_at": "2026-10-23 00:00:00.010822+00", "job_id": "job:backlog:x", "tool_id": "tool:script:y.py"},
            {"receipt_id": "future", "event_at": "2026-12-01T00:00:00Z"}]
    c = coverage(rows, s, now)
    ok = [("counts only [start, now], dedup", c["receipts_since_start"] == 3),
          ("both fields", c["with_job_and_tool"] == 2), ("share", c["share"] == 0.667),
          ("below bar", c["verdict"] == "BELOW"), ("names the gap", c["missing"] == [{"receipt_id": "b", "lacks": ["tool_id"]}]),
          ("empty", coverage([], s, now)["share"] is None)]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    return 0 if all(v for _, v in ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--export", action="store_true", help="refresh the local export from the database first (read-only SELECT)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.export:
        subprocess.run([sys.executable, os.path.join(HERE, "universe_receipts_adapter.py"), "--export"], check=True,
                       stdout=subprocess.DEVNULL)
    rows = jew.load_export()
    if rows is None:
        print("no receipt export; run with --export (needs the supabase CLI linked to ARCS_v9)", file=sys.stderr)
        return 1
    c = coverage(rows, jew._ts(jew.load_config().get("start")))
    print(json.dumps(c, indent=1) if a.json else render(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
