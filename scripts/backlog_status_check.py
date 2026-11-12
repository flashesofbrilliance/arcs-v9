#!/usr/bin/env python3
"""Read-only gate over _QUEUE/induced-backlog.jsonl `state` (enum in runtime/specs/backlog-status.json).

FAIL (exit 1): a row with an id but no `state`, a `state` outside the enum, a legacy `status`
key (prose belongs in `status_note`), or a RUNNING row without `claimed_by` + `claimed_at`.
STALE (warn; exit 1 only with --strict): RUNNING rows claimed more than --days ago, and with
--gh, non-terminal rows whose status_note cites a PR that is now MERGED or CLOSED, and rows whose
status_note opens with a different state word than `state` (a stale "BLOCKED" note on a DONE row
misled a session, 2026-11-01; the `state` field wins, the note is history).
Always prints counts per state.
ADDED (2026-11-08, route at induction, execute at pickup): with --added, rows whose id is new in the
staged file vs HEAD must carry `route.tool` and `trigger` (older rows are grandfathered). --propose
prints a suggested route + trigger per row from its shape (id + jtbd keywords); it never writes.
Proposals are a hint for the human or session inducing the row, not a verdict (keyword routing
misranks; see the Plain verbs table in .claude/commands/catalog.md).

  backlog_status_check.py --check          gate (pre-commit + CI)
  backlog_status_check.py --check --added  also gate rows added in the staged diff (pre-commit)
  backlog_status_check.py --propose [--last N]  suggest route + trigger (read-only)
  backlog_status_check.py --gh --days 3    also ask gh about cited PRs
  backlog_status_check.py --self-test      prove fail-on-bad / pass-on-good
"""
import argparse, collections, datetime as dt, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
SPEC = json.loads((ROOT / "runtime" / "specs" / "backlog-status.json").read_text())
STATES = SPEC["states"]
PR_RE = re.compile(r"(?:PR\s*#|pull/)(\d+)")
LEAD_RE = re.compile(r"\W*([A-Z]+)\b")


def _when(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def check(rows, now, days, pr_state=None):
    fails, stale, counts = [], [], collections.Counter()
    for n, r in rows:
        if "id" not in r:
            continue
        rid, st = r["id"], r.get("state")
        if "status" in r:
            fails.append(f"line {n} {rid}: legacy `status` key; move prose to `status_note`")
        if st not in STATES:
            fails.append(f"line {n} {rid}: state {st!r} not in {sorted(STATES)}")
            continue
        counts[st] += 1
        for k in STATES[st].get("requires", []):
            if not r.get(k):
                fails.append(f"line {n} {rid}: {st} requires `{k}`")
        lead = LEAD_RE.match(str(r.get("status_note", "")))
        if lead and lead.group(1) in STATES and lead.group(1) != st:
            stale.append(f"{rid}: state {st} but status_note opens {lead.group(1)} (state wins; note is stale)")
        if st == "RUNNING":
            at = _when(r.get("claimed_at", ""))
            if r.get("claimed_at") and at is None:
                fails.append(f"line {n} {rid}: claimed_at not ISO-8601")
            elif at and (now - at).days > days:
                stale.append(f"{rid}: RUNNING since {r['claimed_at']} (> {days}d), claimed_by {r.get('claimed_by')}")
        if pr_state and not STATES[st]["terminal"]:
            for pr in sorted(set(PR_RE.findall(str(r.get("status_note", "")) + " " + str(r.get("claimed_by", ""))))):
                ps = pr_state(pr)
                if ps in ("MERGED", "CLOSED"):
                    stale.append(f"{rid}: {st} but cites PR #{pr} which is {ps}")
    return fails, stale, counts


# Shape -> route, first match wins (Zach, 2026-11-08). Heavy tools run at pickup, never at induction.
SHAPES = [
    ("tool renamed/moved/removed", re.compile(r"\b(renam\w*|mov(?:e|ed|es)|remov\w*|retir\w*|deprecat\w*)\s+(?:\S+\s+){0,2}(?:tool|script|skill|command|agent)s?\b"
                r"|\b(?:tool|script|skill|command|agent)s?\s+(?:\S+\s+){0,2}(?:renam|mov|remov|retir|deprecat)", re.I),
     "catalog-verb-table-drift-check (pre-commit + CI, not induction)",
     "pre-commit and CI, on any rename, move or delete of a tool the catalog names"),
    ("net-new client / first page", re.compile(r"\b(client|counterpart|prospect|first page|one-?pager|onboard)", re.I),
     "decompose (GAP: decompose-page-atomic-params), then /forge",
     "at pickup, before any page is built for the client"),
    ("prior updated", re.compile(r"\b(priors?\b|belief|supersed|revis|recalibrat|falsif)", re.I),
     "/thread-recoil",
     "at pickup, when the prior's evidence changes"),
    ("novel idea / problem shape", re.compile(r"\b(novel|idea|new shape|seed|insight|hypothes)", re.I),
     "/echo-scan, plus /witness",
     "at pickup; /witness in the moment the idea lands"),
]


def propose(r):
    text = f"{r.get('id', '')} {r.get('jtbd', '')}"
    for shape, rx, tool, trig in SHAPES:
        if rx.search(text):
            return shape, tool, trig
    return None, "/catalog <jtbd> (no shape matched; pick by hand)", "at pickup"


def missing_route(r):
    route = r.get("route")
    out = []
    if not (isinstance(route, dict) and route.get("tool")):
        out.append("route.tool")
    if not r.get("trigger"):
        out.append("trigger")
    return out


def check_added(old_text, new_text):
    """Rows whose id is not in old_text must carry route.tool and trigger."""
    old = {json.loads(l).get("id") for l in old_text.splitlines() if l.strip()}
    fails = []
    for n, l in enumerate(new_text.splitlines(), 1):
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("id") and r["id"] not in old:
            miss = missing_route(r)
            if miss:
                _, tool, trig = propose(r)
                fails.append(f"line {n} {r['id']}: new row missing {' + '.join(miss)}; proposed tool: {tool}; trigger: {trig}")
    return fails


def git_text(spec):
    p = subprocess.run(["git", "show", spec], capture_output=True, text=True, cwd=ROOT)
    return p.stdout if p.returncode == 0 else ""


def gh_pr_state(pr, _cache={}):
    if pr not in _cache:
        p = subprocess.run(["gh", "pr", "view", pr, "--json", "state", "--jq", ".state"], capture_output=True, text=True)
        _cache[pr] = p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    return _cache[pr]


def load(path):
    return [(i, json.loads(l)) for i, l in enumerate(path.read_text().splitlines(), 1) if l.strip()]


def self_test():
    now = dt.datetime(2026, 10, 10, tzinfo=dt.timezone.utc)
    good = [(1, {"_schema": "x"}),
            (2, {"id": "a", "state": "OPEN", "status_note": "OPEN"}),
            (3, {"id": "b", "state": "RUNNING", "claimed_by": "PR #1", "claimed_at": "2026-10-09T00:00:00Z"})]
    f, s, c = check(good, now, 3, pr_state=lambda p: "OPEN")
    ok = not f and not s and c == {"OPEN": 1, "RUNNING": 1}
    bad = [(1, {"id": "x"}), (2, {"id": "y", "state": "INDUCED"}), (3, {"id": "z", "state": "RUNNING"}),
           (4, {"id": "w", "state": "OPEN", "status": "OPEN"})]
    f, _, _ = check(bad, now, 3)
    ok &= len(f) == 5  # x missing, y invalid, z claimed_by + claimed_at, w legacy key
    old = [(1, {"id": "o", "state": "RUNNING", "claimed_by": "PR #9", "claimed_at": "2026-10-01T00:00:00Z"})]
    _, s, _ = check(old, now, 3, pr_state=lambda p: "MERGED")
    ok &= len(s) == 2  # aged claim + merged PR
    _, s, _ = check([(1, {"id": "d", "state": "DONE", "status_note": "BLOCKED on #1"})], now, 3)
    ok &= len(s) == 1  # note contradicts state
    old = '{"id": "a", "state": "OPEN"}\n'
    bad_new = old + '{"id": "n", "state": "OPEN", "jtbd": "first page for a new client"}\n'
    good_new = old + '{"id": "n", "state": "OPEN", "jtbd": "x", "route": {"tool": "/forge"}, "trigger": "at pickup"}\n'
    ok &= len(check_added(old, bad_new)) == 1 and not check_added(old, good_new) and not check_added(old, old)
    ok &= propose({"id": "x", "jtbd": "rename a tool"})[0] == "tool renamed/moved/removed"
    ok &= propose({"id": "x", "jtbd": "zzz"})[0] is None
    ok &= propose({"id": "x", "jtbd": "a cited value moved; rank by priority"})[0] is None  # 2026-11-08 dry-run false positives
    print("self-test", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="gate mode (default behaviour; flag kept for hooks)")
    ap.add_argument("--file", type=pathlib.Path, default=QUEUE)
    ap.add_argument("--days", type=int, default=SPEC.get("running_stale_days_default", 3))
    ap.add_argument("--gh", action="store_true", help="look up cited PRs with gh pr view")
    ap.add_argument("--strict", action="store_true", help="STALE rows also fail")
    ap.add_argument("--added", action="store_true", help="rows new in the staged file vs HEAD need route.tool + trigger")
    ap.add_argument("--propose", action="store_true", help="print a suggested route + trigger per row (read-only)")
    ap.add_argument("--last", type=int, default=10, help="with --propose: how many trailing rows")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.propose:
        for _, r in [x for x in load(a.file) if "id" in x[1]][-a.last:]:
            shape, tool, trig = propose(r)
            have = (r.get("route") or {}).get("tool") if isinstance(r.get("route"), dict) else None
            print(f"{r['id']}\n  shape: {shape or '-'}\n  proposed: {tool} | trigger: {trig}\n  current: {have or '-'} | trigger: {r.get('trigger') or '-'}")
        return 0
    fails, stale, counts = check(load(a.file), dt.datetime.now(dt.timezone.utc), a.days, gh_pr_state if a.gh else None)
    print("backlog states: " + " · ".join(f"{k} {counts.get(k, 0)}" for k in STATES))
    for s in stale:
        print(f"STALE {s}")
    if a.added:
        rel = a.file.resolve().relative_to(ROOT)
        fails += check_added(git_text(f"HEAD:{rel}"), git_text(f":{rel}"))
    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    return 1 if fails or (a.strict and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
