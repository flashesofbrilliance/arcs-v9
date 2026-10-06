#!/usr/bin/env python3
"""Fail when any Vercel project domain in the team is pinned to a git branch.

Why: on 2026-10-05 chase-intro, cj-brief and growth-intel.arcs.care were pinned to
`claude/brave-chebyshev-cd6452` (deleted from origin). They kept serving its last preview
build, so the retiredFanaticsHosts 308 in next.config.ts never fired. `get_deployment` by
hostname did not show it; only the project-domains API `gitBranch` field did.
Receipt 2026-10-05--retired-hosts-unpin-branch--ZH. Frustration Gate: AGENTS.md gotcha 15.

Scope: every project the `vercel` CLI's current team can list (not only arcs.care owners),
so a pin on a new project is caught without editing a list.

Usage:
  python3 scripts/vercel_branch_pin_gate.py            # live, via `vercel api`
  python3 scripts/vercel_branch_pin_gate.py --fixture f.json   # {"<project>": <domains API JSON>}
  python3 scripts/vercel_branch_pin_gate.py --self-test
Exit: 0 clean, 1 unlisted pin, 2 could not read the API (never a silent pass).
"""
import argparse, json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWLIST = os.path.join(ROOT, "runtime/specs/vercel-branch-pin-allowlist.txt")


def vercel_api(path):
    out = subprocess.run(["vercel", "api", path], capture_output=True, text=True, timeout=90)
    if out.returncode != 0:
        raise RuntimeError(f"vercel api {path}: exit {out.returncode}: {out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def load_allowlist(path):
    allowed = set()
    if os.path.exists(path):
        for line in open(path):
            line = line.split("#", 1)[0].split()
            if len(line) == 2:
                allowed.add((line[0], line[1]))
    return allowed


def live_domains():
    projects = vercel_api("/v9/projects?limit=100")
    if projects.get("pagination", {}).get("next"):
        raise RuntimeError("more than 100 projects: add pagination before trusting a pass")
    names = [p["name"] for p in projects["projects"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        bodies = pool.map(lambda n: vercel_api(f"/v9/projects/{n}/domains?limit=100"), names)
    return dict(zip(names, bodies))


def find_pins(by_project, allowed):
    pins, allowed_hits = [], []
    for project, body in sorted(by_project.items()):
        if body.get("pagination", {}).get("next"):
            raise RuntimeError(f"{project}: more than 100 domains, add pagination")
        for d in body.get("domains", []):
            if d.get("gitBranch"):
                row = (project, d["name"], d["gitBranch"])
                (allowed_hits if (d["name"], d["gitBranch"]) in allowed else pins).append(row)
    return pins, allowed_hits


def run(by_project, allowed):
    pins, ok = find_pins(by_project, allowed)
    ndom = sum(len(b.get("domains", [])) for b in by_project.values())
    for p, d, b in ok:
        print(f"allowlisted pin: {d} -> {b} ({p})")
    for p, d, b in pins:
        print(f"PINNED: {d} -> {b} (project {p}). Unpin: PATCH "
              f"/v9/projects/{p}/domains/{d} with {{\"gitBranch\": null}}, or allowlist it")
    print(f"vercel-branch-pin: {'FAIL' if pins else 'OK'} · {len(by_project)} projects · "
          f"{ndom} domains · {len(pins)} unlisted pin(s)")
    return 1 if pins else 0


def self_test():
    clean = {"arcs-v9": {"domains": [{"name": "arcs.care", "gitBranch": None},
                                     {"name": "good.arcs.care", "gitBranch": None}]},
             "arcs-tripwire": {"domains": [{"name": "tripwire.arcs.care", "gitBranch": None}]}}
    planted = json.loads(json.dumps(clean))
    planted["arcs-v9"]["domains"].append(
        {"name": "chase-intro.arcs.care", "gitBranch": "claude/brave-chebyshev-cd6452"})
    allow = {("chase-intro.arcs.care", "claude/brave-chebyshev-cd6452")}
    cases = [("clean passes", run(clean, set()), 0),
             ("planted pin fails", run(planted, set()), 1),
             ("allowlisted pin passes", run(planted, allow), 0),
             ("allowlist is branch-exact", run(planted, {("chase-intro.arcs.care", "main")}), 1)]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("# comment\nchase-intro.arcs.care claude/brave-chebyshev-cd6452  # reason\n\n")
    cases.append(("allowlist file parses", int(load_allowlist(f.name) == allow), 1))
    os.unlink(f.name)
    bad = [n for n, got, want in cases if got != want]
    print(f"self-test: {len(cases) - len(bad)}/{len(cases)} pass" + (f" FAILED {bad}" if bad else ""))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fixture", help="JSON file {project: domains-API body} instead of live API")
    ap.add_argument("--allowlist", default=ALLOWLIST)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        data = json.load(open(a.fixture)) if a.fixture else live_domains()
    except Exception as e:  # unreadable is not clean
        print(f"vercel-branch-pin: ERROR {e}")
        return 2
    return run(data, load_allowlist(a.allowlist))


if __name__ == "__main__":
    sys.exit(main())
