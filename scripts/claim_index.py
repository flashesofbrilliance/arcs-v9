#!/usr/bin/env python3
"""claim_index: every public number (commits, merged PRs, receipts, days) mapped to where it is stated.

Why (Zach, 2026-10-20): velocity outran recall. The repo went from 3,500 to over 5,000 commits and
nobody could say which surfaces still cite the old figure. This script answers "where is X claimed,
what backs it, is it current" from the files themselves, so the answer never comes from memory.

Each index row: claim (the metric), value (the number as stated), locations (file:line, phrase),
kind (running = a "today" figure such as "over 3,500 commits" or a stamped status field;
point = a bare figure such as "859 commits" in a case study, listed but never checked;
history = any figure inside a dated record (a YYYY-MM-DD path, runtime/recoil/generated,
_ARTIFACTS/milestones or atlas): true on its date, no drift computed, never queued for rewording;
unquantified = a claim with no digits such as "thousands of commits", listed so it is findable),
evidence (where the true number lives), recompute (the command), live (recomputed now, or null
when it cannot be recomputed offline), drift (live minus stated, over live).

  python3 scripts/claim_index.py                 # table of every claim
  python3 scripts/claim_index.py --json          # the index as JSON
  python3 scripts/claim_index.py --check         # exit 1 when a running claim drifts past --tol
  python3 scripts/claim_index.py --check --tol 0.10
  python3 scripts/claim_index.py --self-test

Read-only: it never edits a page. Rewording a drifted claim is Zach's call.
Stdlib only. Counts come from origin/main (run `git fetch` first for a fresh number).
"""
import argparse, datetime as dt, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCAN_DIRS = ("public", "_ARTIFACTS", "runtime/recoil/generated")
TEXT_EXT = (".html", ".htm", ".json", ".txt", ".md", ".tsx")
T0 = dt.date(2026, 4, 9)  # Day 0, same anchor as status_floor_emit.py
DEFAULT_TOL = 0.15
# A "N commits" phrase is ambiguous between all commits and non-merge commits. Where a source
# records which one was meant, map it here: (path regex, stated value, metric, where it was decided).
METRIC_OVERRIDES = [
    (r"concourse", 3500, "commits_no_merges",
     "runtime/recoil/generated/2026-10-16-concourse.json: written materials keep the no-merge count"),
]


def _override(metric, rel, value):
    if metric != "commits":
        return metric
    for rx, v, m, _why in METRIC_OVERRIDES:
        if re.search(rx, rel) and (v is None or v == value):
            return m
    return metric


# Frozen copies: every number in them is a dated snapshot, so all their hits are kind "point".
SNAPSHOT_FILES = {
    "public/chan.html": "noindex counterpart copy of status.html frozen at Day 98",
}


def _git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _ref(root):
    return "origin/main" if _git(root, "rev-parse", "--verify", "-q", "origin/main") else "HEAD"


def live_commits(root):
    out = _git(root, "rev-list", "--count", _ref(root))
    return int(out) if out.isdigit() else None


def live_commits_no_merges(root):
    out = _git(root, "rev-list", "--count", "--no-merges", _ref(root))
    return int(out) if out.isdigit() else None


def live_merged_prs(root):
    out = _git(root, "rev-list", "--count", "--merges", "--first-parent", _ref(root))
    return int(out) if out.isdigit() else None


def live_adrs(root):
    nums = set()
    d = os.path.join(root, "_DECISIONS")
    for fn in os.listdir(d) if os.path.isdir(d) else ():
        m = re.match(r"ADR-(\d+)", fn)
        if m:
            nums.add(int(m.group(1)))
    return len(nums) or None


def live_days(root, today=None):
    return ((today or dt.date.today()) - T0).days


METRICS = {
    "commits": {
        "noun": r"commits",
        "evidence": "git history of arcs-v9 main; status.arcs.care paints it live via /api/pulse",
        "recompute": "git fetch -q origin main && git rev-list --count origin/main",
        "live": live_commits,
    },
    "commits_no_merges": {
        "noun": None,  # assigned only through METRIC_OVERRIDES: the text says "commits" either way
        "evidence": "non-merge commits on arcs-v9 main",
        "recompute": "git fetch -q origin main && git rev-list --count --no-merges origin/main",
        "live": live_commits_no_merges,
    },
    "merged_prs": {
        "noun": r"(?:merged PRs|merged pull requests|PRs merged|pull requests merged|merges)",
        "evidence": "merge commits on arcs-v9 main (repo setting forces --merge, AGENTS.md gotcha 17)",
        "recompute": "git rev-list --count --merges --first-parent origin/main",
        "live": live_merged_prs,
    },
    "receipts": {
        "noun": r"(?:decision )?receipts",
        "evidence": "Supabase public.decision_receipt (project xbbpiryokswwvcrcutge); not recomputable offline",
        "recompute": "Supabase execute_sql: select count(*) from public.decision_receipt",
        "live": None,
    },
    "adrs": {
        "noun": r"ADRs",
        "evidence": "distinct ADR numbers in _DECISIONS/ (oracle.py audit adr lists collisions)",
        "recompute": "ls _DECISIONS | grep -oE '^ADR-[0-9]+' | sort -u | wc -l",
        "live": live_adrs,
    },
    "days": {
        "noun": None,  # "over 30 days" is almost always a duration, so only stamped Day fields count
        "evidence": "days since T0 2026-04-09 (status_floor_emit.py)",
        "recompute": "python3 -c \"import datetime as d;print((d.date.today()-d.date(2026,4,9)).days)\"",
        "live": live_days,
    },
}

RUNNING_QUAL = r"(?:over|more than|upwards of|north of|nearly|almost|about|around|roughly|~|≈)"
NUM = r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?[kK]|\d{2,})(\+)?"
# Stamped status fields are "today" figures by construction.
# Claims with no digits: listed so they are findable, never checked (no number to compare).
WORDY_RE = re.compile(r"\b(?:many |several )?(thousands|hundreds|dozens) of (?:merged )?(commits|PRs|pull requests|receipts|ADRs|decisions)\b", re.I)
WORDY_METRIC = {"commits": "commits", "prs": "merged_prs", "pull requests": "merged_prs",
                "receipts": "receipts", "decisions": "receipts", "adrs": "adrs"}
# Dated records: a number in them was true on their date. Kind "history", listed, never reworded.
HISTORY_RE = re.compile(r"(?:^|/)(?:runtime/recoil/generated|_ARTIFACTS/(?:milestones|atlas))/|\d{4}-\d{2}-\d{2}")
STAMPED_IDS = {"sv-commits": "commits", "stat-days": "days", "hero-day": "days", "era-day": "days"}
STAMP_RE = re.compile(r'id="(%s)"[^>]*>\s*(?:Day\s*)?(\d{1,3}(?:,\d{3})+|\d+)' % "|".join(STAMPED_IDS))


def parse_num(txt):
    t = txt.replace(",", "")
    if t[-1] in "kK":
        return int(round(float(t[:-1]) * 1000))
    return int(float(t))


def _patterns():
    out = []
    for name, m in METRICS.items():
        if not m["noun"]:
            continue
        rx = re.compile(r"(?:(%s)\s+)?%s\s+%s\b" % (RUNNING_QUAL, NUM, m["noun"]), re.I)
        out.append((name, rx))
    return out


def iter_files(root):
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        for dp, dns, fns in os.walk(base):
            dns[:] = [x for x in dns if x not in ("node_modules", ".next")]
            for fn in fns:
                if fn.lower().endswith(TEXT_EXT):
                    yield os.path.join(dp, fn)


def scan(root):
    """Return raw hits: (metric, value, kind, relpath, line, phrase)."""
    hits = []
    pats = _patterns()
    for path in iter_files(root):
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        rel = os.path.relpath(path, root)
        frozen = rel in SNAPSHOT_FILES or bool(HISTORY_RE.search(rel))
        base_point = "history" if HISTORY_RE.search(rel) else "point"
        seen = set()
        for i, line in enumerate(lines, 1):
            for m in STAMP_RE.finditer(line):
                hits.append((STAMPED_IDS[m.group(1)], int(m.group(2).replace(",", "")),
                             base_point if frozen else "running", rel, i, "#%s stamp" % m.group(1)))
            for m in WORDY_RE.finditer(line):
                hits.append((WORDY_METRIC[m.group(2).lower()], None, "unquantified", rel, i, m.group(0)))
            for name, rx in pats:
                for m in rx.finditer(line):
                    qual, num, plus = m.group(1), m.group(2), m.group(3)
                    kind = "running" if (qual or plus or num[-1] in "kK") and not frozen else base_point
                    if (name, i, m.group(0)) in seen:
                        continue
                    seen.add((name, i, m.group(0)))
                    hits.append((name, parse_num(num), kind, rel, i, m.group(0).strip()))
    return hits


def build_index(root, today=None):
    live = {}
    for name, m in METRICS.items():
        fn = m["live"]
        live[name] = None if fn is None else (fn(root, today) if fn is live_days else fn(root))
    rows = {}
    for metric, value, kind, rel, line, phrase in scan(root):
        metric = _override(metric, rel, value)
        key = (metric, value, kind)
        r = rows.setdefault(key, {
            "claim": metric, "value": value, "kind": kind, "locations": [],
            "evidence": METRICS[metric]["evidence"], "recompute": METRICS[metric]["recompute"],
            "live": live[metric], "drift": None,
        })
        r["locations"].append({"file": rel, "line": line, "phrase": phrase})
    for r in rows.values():
        if r["live"] and r["value"] is not None and r["kind"] != "history":
            r["drift"] = round((r["live"] - r["value"]) / r["live"], 3)
    return sorted(rows.values(), key=lambda r: (r["claim"], r["kind"], -(r["value"] or 0)))


def drifted(index, tol):
    return [r for r in index if r["kind"] == "running" and r["drift"] is not None and abs(r["drift"]) > tol]


def render(index):
    out = []
    for r in index:
        live = "?" if r["live"] is None else r["live"]
        drift = "" if r["drift"] is None else " drift %+.0f%%" % (100 * r["drift"])
        out.append("%-17s %-12s %7s live %s%s  (%d place%s)" % (
            r["claim"], r["kind"], "-" if r["value"] is None else "{:,}".format(r["value"]), live, drift,
            len(r["locations"]), "" if len(r["locations"]) == 1 else "s"))
        for loc in r["locations"]:
            out.append("    %s:%d  %s" % (loc["file"], loc["line"], loc["phrase"]))
    return "\n".join(out)


def self_test():
    import os as _os  # a pre-commit hook exports GIT_DIR / GIT_INDEX_FILE; left set, the scratch git below writes to the REAL repo
    for _k in [k for k in _os.environ if k.startswith("GIT_")]:
        del _os.environ[_k]
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "public"))
        with open(os.path.join(d, "public", "a.txt"), "w") as f:
            f.write("About six months and over 3,500 commits.\nThe case study had 859 commits.\n")
        with open(os.path.join(d, "public", "s.html"), "w") as f:
            f.write('<div id="sv-commits">4,900</div> and 1,200+ merged PRs and 254 receipts\n'
                    'about 4.9k commits, 3500+ commits, thousands of commits, 84 ADRs\n')
        os.makedirs(os.path.join(d, "runtime", "recoil", "generated"))
        with open(os.path.join(d, "runtime", "recoil", "generated", "2026-08-27-x.json"), "w") as f:
            f.write('{"note": "over 1,535 commits"}\n')
        subprocess.run(["git", "-C", d, "init", "-q"], check=True)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "-C", d, "commit", "-q", "--allow-empty", "-m", "x"], check=True, env=env)
        with open(os.path.join(d, "public", "concourse-x.txt"), "w") as f:
            f.write("over 3,500 commits\n")
        idx = build_index(d, today=dt.date(2026, 10, 20))
        assert any(r["claim"] == "commits_no_merges" and r["value"] == 3500 for r in idx), idx
        by = {(r["claim"], r["value"]): r for r in idx if r["claim"] != "commits_no_merges"}
        assert by[("commits", 3500)]["kind"] == "running", by
        assert by[("commits", 859)]["kind"] == "point"
        assert by[("commits", 4900)]["kind"] == "running"  # stamped field
        assert by[("merged_prs", 1200)]["kind"] == "running"  # the "+" marks a running figure
        assert by[("receipts", 254)]["live"] is None  # not recomputable offline, never flagged
        assert by[("commits", 3500)]["live"] == 1
        assert by[("commits", 4900)]["kind"] == "running" and len(by[("commits", 4900)]["locations"]) == 2  # 4.9k
        assert any(r["kind"] == "unquantified" and r["claim"] == "commits" for r in idx)
        assert by[("commits", 1535)]["kind"] == "history"  # dated record, never flagged
        assert by[("adrs", 84)]["kind"] == "point"
        # with a fake live count of 5,065 the 3,500 claim drifts about 31 percent and is flagged
        for r in idx:
            if r["claim"] == "commits" and r["value"] is not None:
                r["live"] = 5065
                r["drift"] = round((5065 - r["value"]) / 5065, 3)
        flagged = {(r["claim"], r["value"]) for r in drifted(idx, DEFAULT_TOL)}
        assert ("commits", 3500) in flagged and ("commits", 4900) not in flagged, flagged
        assert ("commits", 859) not in flagged  # point-in-time claims are listed, never flagged
    print("claim_index self-test: OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL)
    ap.add_argument("--claim", choices=sorted(METRICS), help="only this metric")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    idx = build_index(ROOT)
    if a.claim:
        idx = [r for r in idx if r["claim"] == a.claim]
    if a.check:
        bad = drifted(idx, a.tol)
        for r in bad:
            print("DRIFT %s: stated %s, live %s (%+.0f%%), recompute: %s" % (
                r["claim"], "{:,}".format(r["value"]), "{:,}".format(r["live"]), 100 * r["drift"], r["recompute"]))
            for loc in r["locations"]:
                print("    %s:%d  %s" % (loc["file"], loc["line"], loc["phrase"]))
        print("claim_index: %d running claim(s) past %.0f%% tolerance" % (len(bad), 100 * a.tol))
        return 1 if bad else 0
    print(json.dumps(idx, indent=2) if a.json else render(idx))
    return 0


if __name__ == "__main__":
    sys.exit(main())
