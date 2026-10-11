#!/usr/bin/env python3
"""backlog_freshness.py: list induced-backlog rows past their review_by date.

Mechanical only. It decides nothing: it lists rows a human should look at.

review_by (optional, ISO date) on a row always wins. Without it the date is derived:
  anchor  = latest YYYY-MM-DD mentioned anywhere in the row
  P1 = anchor + 7d · P2 / no priority = anchor + 21d · P3 / P4 = anchor + 45d
  HELD / TABLED rows = the first date in `trigger` if it names one, else anchor + 45d
Rows with no date at all are listed as `nodate` (due now).
Terminal rows (DONE / CLOSED / COMPOSTED / SUPERSEDED / LOCKED) are skipped.

In-progress rows (STARTING / DELEGATED / IN PROGRESS) with no commit naming the row id
in the last 7 days (any branch) are flagged `revert-to-OPEN`.

usage:
  backlog_freshness.py [--file F] [--today YYYY-MM-DD] [--json]
  backlog_freshness.py --check       exit 1 if any row is due or a review_by is malformed
  backlog_freshness.py --self-test   synthetic rows, never touches the real file
Unknown flags or extra args exit 2.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
DATE_RE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
WINDOW = {"P0": 7, "P1": 7, "P2": 21, "P3": 45, "P4": 45}
DEFAULT_DAYS = 21
HELD_DAYS = 45
TERMINAL = ("DONE", "CLOSED", "COMPOSTED", "SUPERSEDED", "LOCKED")
HELD = ("HELD", "TABLED")
IN_PROGRESS = ("STARTING", "DELEGATED", "IN PROGRESS")
STALL_DAYS = 7


def _date(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _dates(text):
    return [d for d in (_date(m) for m in DATE_RE.findall(text)) if d]


def _status(row):
    return str(row.get("status_note") or row.get("status") or row.get("state") or "OPEN").upper()


def _priority(row):
    m = re.match(r"P\d", str(row.get("priority") or "").upper())
    return m.group(0) if m else None


def assess(row, today, last_commit):
    """Return a finding dict for a row, or None when nothing is due.
    last_commit(id) -> date | None is injected so the self-test needs no git."""
    status = _status(row)
    if status.startswith(TERMINAL):
        return None
    rid = row.get("id", "?")
    out = {"id": rid, "status": status[:60], "priority": _priority(row)}
    if "review_by" in row:
        rb = _date(row["review_by"])
        if rb is None:
            return {**out, "flag": "malformed-review_by", "review_by": row["review_by"]}
        out["basis"] = "explicit"
    else:
        dates = _dates(json.dumps(row, ensure_ascii=False))
        anchor = max(dates) if dates else None
        if status.startswith(HELD):
            trig = _dates(str(row.get("trigger", "")))
            rb = trig[0] if trig else (anchor + dt.timedelta(HELD_DAYS) if anchor else None)
            out["basis"] = "trigger" if trig else "held+45d"
        else:
            days = WINDOW.get(out["priority"], DEFAULT_DAYS)
            rb = anchor + dt.timedelta(days) if anchor else None
            out["basis"] = f"anchor+{days}d"
        out["anchor"] = anchor.isoformat() if anchor else None
        if rb is None:
            return {**out, "flag": "nodate", "review_by": None, "overdue_days": None}
    out["review_by"] = rb.isoformat()
    flags = []
    if rb <= today:
        flags.append("past-review_by")
    if any(k in status for k in IN_PROGRESS):
        lc = last_commit(rid)
        if lc is None or (today - lc).days > STALL_DAYS:
            flags.append("revert-to-OPEN")
            out["last_commit"] = lc.isoformat() if lc else None
    if not flags:
        return None
    out["flag"] = ",".join(flags)
    out["overdue_days"] = (today - rb).days
    return out


def git_last_commit(rid):
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--all", "-F", "-i", f"--grep={rid}",
             "-1", "--format=%cs"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return _date(r.stdout.strip())


def load(path):
    rows = []
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if "_schema" in row:
            continue
        row["_line"] = n
        rows.append(row)
    return rows


def run(rows, today, last_commit):
    found = [f for f in (assess(r, today, last_commit) for r in rows) if f]
    found.sort(key=lambda f: -(f.get("overdue_days") if f.get("overdue_days") is not None else 10**6))
    return found


def render(found, total, today):
    lines = [f"backlog-freshness {today}: {len(found)} of {total} live-or-open rows need a look"]
    for f in found:
        od = "nodate" if f.get("overdue_days") is None else f"{f['overdue_days']:+d}d"
        lines.append(f"  {od:>7}  {f['flag']:<32} {f['id']}  [{f.get('basis', '')}]")
    lines.append("fates (human): renew (set review_by) · promote · compost · supersede")
    return "\n".join(lines)


def self_test():
    today = dt.date(2026, 10, 4)
    recent = lambda rid: dt.date(2026, 10, 2) if rid == "busy" else None
    cases = [
        ({"id": "a", "status": "OPEN", "priority": "P1", "trigger": "2026-09-20"}, "past-review_by"),
        ({"id": "b", "status": "OPEN", "priority": "P3", "jtbd": "x 2026-09-20"}, None),
        ({"id": "c", "status": "open", "jtbd": "x 2026-09-01"}, "past-review_by"),
        ({"id": "d", "status": "DONE 2026-01-01"}, None),
        ({"id": "e", "status": "HELD", "trigger": "after 2026-12-01"}, None),
        ({"id": "f", "status": "HELD", "trigger": "after 2026-10-01"}, "past-review_by"),
        ({"id": "g", "status": "OPEN"}, "nodate"),
        ({"id": "h", "status": "OPEN", "review_by": "2026-13-40"}, "malformed-review_by"),
        ({"id": "i", "status": "OPEN", "review_by": "2026-11-01", "jtbd": "2025-01-01"}, None),
        ({"id": "busy", "status": "DELEGATED: running", "jtbd": "2026-10-01"}, None),
        ({"id": "idle", "status": "OPEN: STARTING", "jtbd": "2026-10-01"}, "revert-to-OPEN"),
        ({"id": "j", "status": "SUPERSEDED by k", "jtbd": "2020-01-01"}, None),
    ]
    fails = 0
    for row, want in cases:
        f = assess(row, today, recent)
        got = f["flag"] if f else None
        ok = got == want
        fails += not ok
        print(f"  {'ok ' if ok else 'FAIL'} {row['id']}: want {want} got {got}")
    for argv in (["--bogus"], ["extra"], ["--today"], ["--today", "nope"]):
        try:
            parse(argv)
            ok = False
        except SystemExit as e:
            ok = e.code == 2
        fails += not ok
        print(f"  {'ok ' if ok else 'FAIL'} argv {argv} -> exit 2")
    n = len(cases) + 4
    print(f"backlog_freshness self-test: {n - fails}/{n}")
    return 1 if fails else 0


def _iso(s):
    d = _date(s)
    if d is None:
        raise argparse.ArgumentTypeError(f"not an ISO date: {s!r}")
    return d


def parse(argv):
    p = argparse.ArgumentParser(prog="backlog_freshness.py", description=__doc__.split("\n")[0])
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.add_argument("--today", type=_iso, default=None)
    p.add_argument("--json", action="store_true")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--self-test", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    a = parse(sys.argv[1:] if argv is None else argv)
    if a.self_test:
        return self_test()
    today = a.today or dt.date.today()
    rows = load(a.file)
    found = run(rows, today, git_last_commit)
    live = sum(1 for r in rows if not _status(r).startswith(TERMINAL))
    if a.json:
        print(json.dumps({"today": today.isoformat(), "live": live, "due": found}, indent=2))
    else:
        print(render(found, live, today))
    return 1 if (a.check and found) else 0


if __name__ == "__main__":
    sys.exit(main())
