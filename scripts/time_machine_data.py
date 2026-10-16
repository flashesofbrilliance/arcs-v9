#!/usr/bin/env python3
"""time_machine_data: the numbers behind _ARTIFACTS/arcs-time-machine.html, regenerated from git (and Downloads when present).

For each month Oct 2025 to Oct 2026: non-merge commits on origin/main, lines added and deleted (lockfiles, snapshots, generated reports,
state files and .jsonl excluded), defensive layers first added that month (gates, checks, lints, detectors, audits, specs, workflows, hooks),
and counts of non-personal videos, mp3s and ARCS-named documents in ~/Downloads by file birth or modified month (file dates, not creation dates).
Months before the first commit have no git numbers (null), never zeros.

  python3 scripts/time_machine_data.py            print the JSON
  python3 scripts/time_machine_data.py --write    write _ARTIFACTS/arcs-time-machine-data.json
  python3 scripts/time_machine_data.py --git      only the git part (what a check can reproduce on any machine)
Stdlib only.
"""
import collections, datetime, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS = [f"2025-{m:02d}" for m in (10, 11, 12)] + [f"2026-{m:02d}" for m in range(1, 11)]
EXCL = re.compile(r"(package-lock|\.lock$|\.snap$|node_modules|\.next/|_STATE/|runtime/recoil/generated|\.jsonl$)")
LAYER = re.compile(r"(^scripts/.*(gate|_check|lint|detector|audit).*\.(py|mjs|sh)$|^tests/.*\.spec\.ts$|^\.github/workflows/.*\.yml$|^scripts/git-hooks/)")

def git(*a): return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, timeout=280).stdout

def gitpart():
    commits = collections.Counter(); add = collections.Counter(); dele = collections.Counter(); cur = None
    for l in git("log", "origin/main", "--no-merges", "--numstat", "--pretty=@%ad", "--date=format:%Y-%m").split("\n"):
        if l.startswith("@"): cur = l[1:]; commits[cur] += 1; continue
        p = l.split("\t")
        if len(p) == 3 and cur and p[0].isdigit() and p[1].isdigit() and not EXCL.search(p[2]): add[cur] += int(p[0]); dele[cur] += int(p[1])
    layers = collections.Counter(); seen = set(); cur = None
    for l in git("log", "origin/main", "--diff-filter=A", "--name-only", "--pretty=@%ad", "--date=format:%Y-%m").split("\n"):
        if l.startswith("@"): cur = l[1:]
        elif l and LAYER.search(l) and l not in seen: seen.add(l); layers[cur] += 1
    first = min(commits) if commits else None
    return {m: ({"commits": commits[m], "added": add[m], "deleted": dele[m], "layers": layers[m]} if first and m >= first else None) for m in MONTHS}

def downloads():
    D = os.path.expanduser("~/Downloads"); out = {m: {"videos": 0, "mp3": 0, "docs": 0} for m in MONTHS}
    if not os.path.isdir(D): return None
    for root, _, fs in os.walk(D):
        if "pvt" in root or "memories" in root: continue
        for f in fs:
            if any(p in f for p in ("IMG_", "About_Milo", "Milo")): continue
            try: st = os.stat(os.path.join(root, f))
            except OSError: continue
            m = datetime.datetime.fromtimestamp(min(getattr(st, "st_birthtime", st.st_mtime), st.st_mtime)).strftime("%Y-%m"); e = f.lower().rsplit(".", 1)[-1]
            if m not in out: continue
            if e in ("mp4", "mov", "m4v"): out[m]["videos"] += 1
            elif e == "mp3": out[m]["mp3"] += 1
            elif e in ("md", "pdf", "docx") and any(k in f.lower() for k in ("arcs", "manifesto", "salaryman", "canon", "notomation", "covenant")): out[m]["docs"] += 1
    return out

OTHER = ["arcs_cfa", "Wayfinder-concept-visuals---Fork", "Wayfinder---FE-Prototype-v0---Fork", "arcs-decision-receipts", "ARCS-Iron-Chef-Challenge", "ARCS-Marketing-Landing-Page", "Decision-Card-Worksheet"]

def others():
    """Commit counts per month in the other ARCS repos that predate arcs-v9 (first commit 2026-04-09), read with the gh CLI. None if gh is unavailable."""
    out = {m: {} for m in MONTHS}
    for r in OTHER:
        try: o = subprocess.run(["gh", "api", f"repos/flashesofbrilliance/{r}/commits?per_page=100", "--paginate", "--jq", ".[].commit.author.date[0:7]"], capture_output=True, text=True, timeout=120)
        except Exception: return None
        if o.returncode != 0: return None
        for m, n in collections.Counter(o.stdout.split()).items():
            if m in out: out[m][r] = n
    return out

def main(a):
    g = gitpart(); out = {"generated": datetime.date.today().isoformat(), "git": g, "sources": {"git": "origin/main non-merge commits; lines exclude lockfiles, snapshots, generated, state, jsonl", "layers": "gate, check, lint, detector, audit scripts, tests, workflows and hooks, counted in the month each file first appears"}}
    if "--git" not in a:
        out["other_repos"] = others(); out["sources"]["other_repos"] = "commit counts in older ARCS repos (arcs_cfa, the Wayfinder forks, arcs-decision-receipts, ARCS-Iron-Chef-Challenge, ARCS-Marketing-Landing-Page, Decision-Card-Worksheet) via the gh CLI, by author date"
        d = downloads(); out["downloads"] = d; out["sources"]["downloads"] = "non-personal files in ~/Downloads by birth or modified month; file dates are not creation dates"
    s = json.dumps(out, indent=1)
    if "--write" in a: open(os.path.join(ROOT, "_ARTIFACTS/arcs-time-machine-data.json"), "w").write(s + "\n"); print("wrote _ARTIFACTS/arcs-time-machine-data.json")
    else: print(s)

if __name__ == "__main__": main(sys.argv[1:])
