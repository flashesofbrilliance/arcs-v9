#!/usr/bin/env python3
"""status_floor_emit: stamp the no-JS static floor on public/status.html from the repo.

Why: the page paints live values with JS (day count client-side, commits via /api/pulse), but
crawlers, answer engines and no-JS readers get the static HTML. That floor sat at Day 129 /
1,488 commits for six weeks while the live page read Day 173 / 2,792 (fixed 2026-09-29, #650).
A number a script can compute is stamped by the script and guarded by its own --check.

Stamps (by element id): hero-day, era-day, stat-days (days since T0 = 2026-04-09, as of the
stamp date), sv-commits (git rev-list --count HEAD), et-now (the as-of date), and the
tempo-live data-floor (merges to main per week, last 12 Monday-start weeks, from git; the
same metric /api/pulse reads live, 2026-10-06).

  python3 scripts/status_floor_emit.py            # restamp as of today: write _ARTIFACTS/status/floor.json, then rebuild the page
  python3 scripts/status_floor_emit.py --check    # exit 1 if the floor is inconsistent or older than MAX_AGE_DAYS, or the page drifted from its sources

Since 2026-11-12 the page is generated (scripts/status_page_build.py from _ARTIFACTS/status/). This script owns the figures that have a
machine source: floor.json carries commits and tempo (git), the debt counts and State of the Union card items (the issue tracker via gh,
public labels from PUBLIC_ITEMS in src/lib/pulse.ts), each with its source string. If gh is unavailable the previous tracker values are kept
and named stale, never zeroed.
  python3 scripts/status_floor_emit.py --self-test

--check never recounts commits (CI checkouts are shallow). It checks that the three day fields
agree with the stamped as-of date, and that the as-of date is recent. Stdlib only.
"""
import argparse, datetime as dt, hashlib, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "public", "status.html")
FLOOR = os.path.join(ROOT, "_ARTIFACTS", "status", "floor.json")
REPO = "flashesofbrilliance/arcs-v9"
T0 = dt.date(2026, 4, 9)
MAX_AGE_DAYS = 21
DAY_IDS = ("hero-day", "era-day", "stat-days")


def span(id_):
    return re.compile(r'(id="%s">)([^<]*)(<)' % re.escape(id_))


def read_fields(s):
    out = {}
    for id_ in DAY_IDS + ("sv-commits", "et-now"):
        m = span(id_).search(s)
        out[id_] = m.group(2) if m else None
    return out


def stamp(s, today, commits):
    vals = {i: str((today - T0).days) for i in DAY_IDS}
    vals["sv-commits"] = f"{commits:,}"
    vals["et-now"] = today.strftime("%b %-d, %Y")
    for id_, v in vals.items():
        s, n = span(id_).subn(lambda m: m.group(1) + v + m.group(3), s, count=1)
        if n != 1:
            raise SystemExit(f"status_floor_emit: id={id_} not found exactly once")
    return s


TEMPO_RE = re.compile(r"(id=\"tempo-live\" data-floor=')([^']*)(')")
TEMPO_WEEKS = 12


def tempo_floor(today):
    """[[monday_iso, merges], ...] for the last TEMPO_WEEKS weeks, first-parent merges on HEAD."""
    monday = today - dt.timedelta(days=today.weekday())
    weeks = [monday - dt.timedelta(weeks=k) for k in range(TEMPO_WEEKS - 1, -1, -1)]
    out = subprocess.check_output(["git", "log", "--first-parent", "--merges", "--format=%cs",
                                   f"--since={weeks[0].isoformat()}", "HEAD"], cwd=ROOT, text=True)
    counts = {w: 0 for w in weeks}
    for line in out.split():
        d = dt.date.fromisoformat(line)
        w = d - dt.timedelta(days=d.weekday())
        if w in counts:
            counts[w] += 1
    return [[w.isoformat(), counts[w]] for w in weeks]


def public_items():
    """{issue number: public label} parsed from PUBLIC_ITEMS in src/lib/pulse.ts (the one curated map; issue titles never cross)."""
    s = open(os.path.join(ROOT, "src", "lib", "pulse.ts"), encoding="utf-8").read()
    body = re.search(r"PUBLIC_ITEMS: Record<number, string> = \{(.*?)\n\};", s, re.S).group(1)
    return {int(n): lbl for n, lbl in re.findall(r'(\d+):\s*"([^"]+)"', body)}


def status_of(i):
    """Mirror of statusOf() in src/lib/pulse.ts: closed wins, else the status: label, else open."""
    if i["state"] == "CLOSED":
        return "done"
    for l in i["labels"]:
        if l.startswith("status:") and l[7:] in ("open", "in-progress", "decision", "done"):
            return l[7:]
    return "open"


def tracker_floor():
    """(debt counts, items by status) from `gh issue list`, or None when gh is unavailable or the read is implausibly empty."""
    try:
        out = subprocess.check_output(["gh", "issue", "list", "--repo", REPO, "--label", "debt", "--state", "all", "--limit", "500",
                                       "--json", "number,state,labels"], cwd=ROOT, text=True, timeout=60)
        issues = [{"number": i["number"], "state": i["state"], "labels": [l["name"] for l in i["labels"]]} for i in json.loads(out)]
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if not issues:
        return None
    debt = {"open": 0, "in-progress": 0, "decision": 0, "done": 0}
    for i in issues:
        debt[status_of(i)] += 1
    by = {i["number"]: i for i in issues}
    items = {k: [] for k in debt}
    for n, label in public_items().items():
        if n in by:
            items[status_of(by[n])].append(label)
    return debt, items


def build_floor(today, commits, prev):
    tr = tracker_floor()
    stale = tr is None
    if stale:
        if not prev:
            raise SystemExit("status_floor_emit: gh unavailable and no previous floor.json to keep")
        debt, items, debt_asof = prev["debt_counts"], prev["items"], prev["tracker_as_of"]
    else:
        debt, items = tr
        debt_asof = today.isoformat()
    return {
        "as_of": today.isoformat(), "day": (today - T0).days, "commits": commits, "tempo": tempo_floor(today),
        "debt": dict(debt), "debt_counts": dict(debt), "items": items, "tracker_as_of": debt_asof,
        "sources": {
            "day": "days since T0 2026-04-09, as of the stamp date (scripts/status_floor_emit.py)",
            "commits": "git rev-list --count HEAD",
            "as_of": "system clock date at stamp time",
            "tempo": "git log --first-parent --merges on HEAD, last 12 Monday-start weeks (same metric as /api/pulse tempo)",
            "debt": "gh issue list --label debt --state all, counted by status label (closed wins); same rule as summarizeDebt in src/lib/pulse.ts"
                    + (" [STALE: gh unavailable, kept from %s]" % debt_asof if stale else ""),
            "items": "PUBLIC_ITEMS in src/lib/pulse.ts (issue number to public label), grouped by the issue's live status",
            "gate_cal, gate_goal": "GATES in src/lib/pulse.ts, read by scripts/status_page_build.py",
        },
    }


def stamp_tempo(s, rows):
    s, n = TEMPO_RE.subn(lambda m: m.group(1) + json.dumps(rows, separators=(",", ":")) + m.group(3), s, count=1)
    if n != 1:
        raise SystemExit("status_floor_emit: tempo-live data-floor not found exactly once")
    return s


def check(s, today):
    f, errs = read_fields(s), []
    try:
        asof = dt.datetime.strptime(f["et-now"] or "", "%b %d, %Y").date()
    except ValueError:
        return [f"et-now is not a stamped date: {f['et-now']!r} (run scripts/status_floor_emit.py)"]
    want = str((asof - T0).days)
    errs += [f"{i}={f[i]!r} but as-of {asof} means day {want}" for i in DAY_IDS if f[i] != want]
    if not re.fullmatch(r"\d{1,3}(,\d{3})*", f["sv-commits"] or ""):
        errs.append(f"sv-commits is not a stamped count: {f['sv-commits']!r}")
    m = TEMPO_RE.search(s)
    try:
        rows = json.loads(m.group(2)) if m else None
        okrows = isinstance(rows, list) and len(rows) == TEMPO_WEEKS and all(
            isinstance(r, list) and len(r) == 2 and isinstance(r[1], int) for r in rows)
    except ValueError:
        okrows = False
    if not okrows:
        errs.append("tempo-live data-floor is missing or not 12 [week, merges] rows (run scripts/status_floor_emit.py)")
    elif all(r[1] == 0 for r in rows):
        errs.append("tempo-live floor is all zeros: a false-zero floor (run scripts/status_floor_emit.py)")
    age = (today - asof).days
    if age > MAX_AGE_DAYS:
        errs.append(f"static floor is {age} days old (max {MAX_AGE_DAYS}); run scripts/status_floor_emit.py")
    return errs


def self_test():
    s = open(PAGE, encoding="utf-8").read()
    today = dt.date(2026, 9, 29)
    good = stamp(s, today, 2792)
    assert not check(good, today), check(good, today)
    assert check(good, today + dt.timedelta(days=MAX_AGE_DAYS + 1)), "stale floor must fail"
    assert check(span("hero-day").sub(r"\g<1>129\3", good, count=1), today), "day mismatch must fail"
    assert check(span("et-now").sub(r"\g<1>…\3", good, count=1), today), "unstamped as-of must fail"
    zero = stamp_tempo(good, [["2026-01-05", 0]] * TEMPO_WEEKS)
    assert check(zero, today), "all-zero tempo floor must fail"
    print("status_floor_emit self-test: PASS (stale, day-mismatch, unstamped all fail; fresh passes)")
    return 0


def _snapshot():
    """sha256 + mtime_ns of the one file the emit mode writes."""
    if not os.path.exists(PAGE):
        return None
    with open(PAGE, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest(), os.stat(PAGE).st_mtime_ns


def argv_self_test():
    """Run the CLI as a subprocess and assert the argv contract: bad args exit 2, --check writes nothing."""
    me = os.path.abspath(__file__)
    fails = total = 0

    def run(*a):
        return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=ROOT)

    def ok(name, cond):
        nonlocal fails, total
        total += 1
        print(("PASS " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    before = _snapshot()
    ok("unknown flag exits 2", run("--chek").returncode == 2)
    ok("unknown flag writes nothing", _snapshot() == before)
    ok("extra positional exits 2", run("extra").returncode == 2)
    ok("extra positional with --check exits 2", run("--check", "extra").returncode == 2)
    ok("extra positional writes nothing", _snapshot() == before)
    r = run("--check")
    ok("--check exits 0 or 1", r.returncode in (0, 1))
    ok("--check writes nothing (hash + mtime)", _snapshot() == before)
    print(f"status_floor_emit self-test: {total - fails}/{total}")
    return 1 if fails else 0


def parse_args(a):
    ap = argparse.ArgumentParser(
        prog="status_floor_emit.py",
        description="Stamp the no-JS static floor on public/status.html. No flag: restamp as of today (writes).",
    )
    # Independent flags, resolved in the original priority order: --self-test > --check.
    ap.add_argument("--self-test", action="store_true", help="argv contract + stamp/check unit asserts (writes nothing)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the floor is inconsistent or stale (read-only)")
    return ap.parse_args(a)


def main(a):
    args = parse_args(a)
    if args.self_test:
        rc = argv_self_test()
        return self_test() or rc
    s = open(PAGE, encoding="utf-8").read()
    today = dt.date.today()
    if args.check:
        errs = check(s, today)
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import status_page_build as spb
        if not os.path.exists(FLOOR):
            errs.append("_ARTIFACTS/status/floor.json is missing (run scripts/status_floor_emit.py)")
        elif spb.check():
            errs.append("the page differs from its sources (run scripts/status_page_build.py)")
        for e in errs: print(f"✖ status floor: {e}")
        if not errs: print("✓ status floor current")
        return 1 if errs else 0
    commits = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=ROOT, text=True).strip())
    prev = json.load(open(FLOOR, encoding="utf-8")) if os.path.exists(FLOOR) else None
    floor = build_floor(today, commits, prev)
    open(FLOOR, "w", encoding="utf-8").write(json.dumps(floor, indent=1, ensure_ascii=False) + "\n")
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import status_page_build as spb
    spb.build()
    rows = floor["tempo"]
    print(f"status_floor_emit: stamped day {floor['day']}, {commits:,} commits, "
          f"{sum(r[1] for r in rows)} merges over {TEMPO_WEEKS} weeks, tracker {floor['debt']} as of {floor['tracker_as_of']}; page rebuilt")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
