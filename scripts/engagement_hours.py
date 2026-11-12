#!/usr/bin/env python3
"""engagement_hours.py: how many hours an engagement has cost, and how many of them were unpaid.

Each engagement folder may hold investment.json, a private ledger kept beside the record (never
rendered to a client page):

  {"cap_hours": 10,                      # unpaid discovery cap; past it, --check warns
   "paid_from": null | "YYYY-MM-DD",     # first paid step started; hours before it are unpaid
   "work_paths": ["public/myally-hub.html", ...],   # repo paths that belong to this engagement
   "calls":  [{"date", "minutes", "source", "basis"}],   # basis: measured | estimated | reported
   "emails": {"sent", "minutes_each", "basis", "counted_through"}}

Work sessions are computed from commit times on work_paths across all refs (each commit once):
a gap over 90 minutes starts a new session. Low counts each session's span; high adds 30
minutes of lead-in per session. Emails count half their assumed minutes at low, all at high.
Calls count the same at both. Every part prints its basis; only calls can be measured.

  python3 scripts/engagement_hours.py                  # every engagement with an investment.json
  python3 scripts/engagement_hours.py --dir <folder>
  python3 scripts/engagement_hours.py --check          # exit 1 when unpaid low hours pass the cap
  python3 scripts/engagement_hours.py --self-test

Stdlib only, read-only. Warns; it never blocks a commit (free work is sometimes a choice).
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GAP_MIN, LEAD_MIN = 90, 30
BASES = {"measured", "estimated", "reported"}


def commit_times(paths: list[str]) -> list[dt.datetime]:
    out = subprocess.run(["git", "log", "--all", "--format=%H %aI", "--", *paths],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    seen, times = set(), []
    for ln in out.splitlines():
        h, t = ln.split(" ", 1)
        if h not in seen:
            seen.add(h)
            times.append(dt.datetime.fromisoformat(t))
    return sorted(times)


def sessions(times: list[dt.datetime]) -> list[tuple[dt.datetime, dt.datetime, int]]:
    out: list[list] = []
    for t in times:
        if out and (t - out[-1][1]).total_seconds() <= GAP_MIN * 60:
            out[-1][1] = t
            out[-1][2] += 1
        else:
            out.append([t, t, 1])
    return [tuple(s) for s in out]


def tally(inv: dict, times: list[dt.datetime]) -> dict:
    paid = inv.get("paid_from")
    unpaid = lambda d: paid is None or d < paid
    ss = [s for s in sessions(times)]
    span = lambda s: (s[1] - s[0]).total_seconds() / 3600
    calls = inv.get("calls", [])
    em = inv.get("emails") or {"sent": 0, "minutes_each": 0}
    em_h = em.get("sent", 0) * em.get("minutes_each", 0) / 60
    parts = {}
    for label, keep in (("unpaid", unpaid), ("paid", lambda d: not unpaid(d))):
        s_in = [s for s in ss if keep(s[0].date().isoformat())]
        c_in = [c for c in calls if keep(c["date"])]
        e_in = em_h if label == "unpaid" else 0.0  # emails are counted through a date, all before paid work so far
        call_h = sum(c["minutes"] for c in c_in) / 60
        low = call_h + sum(span(s) for s in s_in) + e_in / 2
        high = call_h + sum(span(s) + LEAD_MIN / 60 for s in s_in) + e_in
        parts[label] = {"calls_h": round(call_h, 1), "calls": len(c_in), "sessions": len(s_in),
                        "commits": sum(s[2] for s in s_in), "emails_h": round(e_in, 1),
                        "low": round(low, 1), "high": round(high, 1)}
    return parts


def validate(inv: dict) -> list[str]:
    errs = []
    if not isinstance(inv.get("cap_hours"), (int, float)):
        errs.append("cap_hours must be a number")
    if not inv.get("work_paths"):
        errs.append("work_paths is empty")
    for i, c in enumerate(inv.get("calls", [])):
        if c.get("basis") not in BASES or not isinstance(c.get("minutes"), (int, float)):
            errs.append(f"calls[{i}]: minutes and basis ({'/'.join(sorted(BASES))}) required")
    return errs


def report(d: str) -> tuple[str, bool]:
    inv = json.load(open(os.path.join(d, "investment.json"), encoding="utf-8"))
    errs = validate(inv)
    name = os.path.basename(d)
    if errs:
        return f"{name}: invalid investment.json: " + "; ".join(errs), True
    p = tally(inv, commit_times(inv["work_paths"]))
    u, cap = p["unpaid"], inv["cap_hours"]
    over = u["low"] > cap
    lines = [f"{name}: unpaid {u['low']} to {u['high']} h (cap {cap} h){'  OVER CAP' if over else ''}"
             + ("" if inv.get("paid_from") else "; no paid step started yet"),
             f"  calls     {u['calls_h']} h over {u['calls']} call(s) ("
             + ", ".join(f"{c['date']} {c['minutes']} min {c['basis']}" for c in inv.get("calls", [])) + ")",
             f"  sessions  {u['sessions']} from {u['commits']} commits (estimated from commit times)",
             f"  emails    {u['emails_h']} h at most ({inv.get('emails', {}).get('basis', 'assumed')}, "
             f"counted through {inv.get('emails', {}).get('counted_through', '?')})"]
    if inv.get("paid_from"):
        q = p["paid"]
        lines.append(f"  paid since {inv['paid_from']}: {q['low']} to {q['high']} h")
    return "\n".join(lines), over


def self_test() -> int:
    t0 = dt.datetime(2026, 11, 1, 9, 0)
    m = lambda mins: t0 + dt.timedelta(minutes=mins)
    times = [m(0), m(60), m(120), m(400), m(401)]  # two sessions: 2 h span, then 1 min
    ss = sessions(times)
    assert [s[2] for s in ss] == [3, 2], ss
    inv = {"cap_hours": 2, "paid_from": None, "work_paths": ["x"],
           "calls": [{"date": "2026-11-01", "minutes": 60, "source": "t", "basis": "measured"}],
           "emails": {"sent": 4, "minutes_each": 15}}
    p = tally(inv, times)["unpaid"]
    assert p["low"] == round(1 + 2 + 1 / 60 + 0.5, 1), p
    assert p["high"] == round(1 + 2 + 1 / 60 + 1 + 1, 1), p
    inv["paid_from"] = "2026-11-01"
    q = tally(inv, times)
    assert q["unpaid"]["sessions"] == 0 and q["paid"]["sessions"] == 2, q
    assert validate({"cap_hours": "x", "work_paths": [], "calls": [{"minutes": 5}]}) and not validate(
        {"cap_hours": 10, "work_paths": ["a"], "calls": []})
    print("engagement_hours self-test: OK (sessions split on a 90-minute gap, low/high math, paid split, bad ledger refused)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    dirs = [os.path.abspath(a.dir)] if a.dir else sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(ROOT, "_ARTIFACTS", "engagements", "*", "investment.json")))
    any_over = False
    for d in dirs:
        text, over = report(d)
        any_over |= over
        print(text)
    return 1 if (a.check and any_over) else 0


if __name__ == "__main__":
    sys.exit(main())
