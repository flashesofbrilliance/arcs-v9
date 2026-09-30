#!/usr/bin/env python3
"""status_floor_emit: stamp the no-JS static floor on public/status.html from the repo.

Why: the page paints live values with JS (day count client-side, commits via /api/pulse), but
crawlers, answer engines and no-JS readers get the static HTML. That floor sat at Day 129 /
1,488 commits for six weeks while the live page read Day 173 / 2,792 (fixed 2026-09-29, #650).
A number a script can compute is stamped by the script and guarded by its own --check.

Stamps (by element id): hero-day, era-day, stat-days (days since T0 = 2026-04-09, as of the
stamp date), sv-commits (git rev-list --count HEAD), et-now (the as-of date).

  python3 scripts/status_floor_emit.py            # restamp as of today (ET date from the system clock)
  python3 scripts/status_floor_emit.py --check    # exit 1 if the floor is inconsistent or older than MAX_AGE_DAYS
  python3 scripts/status_floor_emit.py --self-test

--check never recounts commits (CI checkouts are shallow). It checks that the three day fields
agree with the stamped as-of date, and that the as-of date is recent. Stdlib only.
"""
import datetime as dt, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "public", "status.html")
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
    print("status_floor_emit self-test: PASS (stale, day-mismatch, unstamped all fail; fresh passes)")
    return 0


def main(a):
    if "--self-test" in a:
        return self_test()
    s = open(PAGE, encoding="utf-8").read()
    today = dt.date.today()
    if "--check" in a:
        errs = check(s, today)
        for e in errs: print(f"✖ status floor: {e}")
        if not errs: print("✓ status floor current")
        return 1 if errs else 0
    commits = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=ROOT, text=True).strip())
    open(PAGE, "w", encoding="utf-8").write(stamp(s, today, commits))
    print(f"status_floor_emit: stamped day {(today - T0).days}, {commits:,} commits, as of {today}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
