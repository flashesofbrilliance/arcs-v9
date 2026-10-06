#!/usr/bin/env python3
"""Fail if any Vercel project domain in the team is pinned to a git branch.

A domain with `gitBranch` set serves that branch's latest preview, never
production, so redirects/rewrites shipped to main never reach it. If the branch
is deleted, the host stays frozen on its last build. On 2026-10-05 three retired
arcs.care hosts were found that way (receipt
2026-10-05--retired-hosts-unpin-branch--ZH). `get_deployment(<host>)` does not
show the pin; only the project-domains API does.

Auth: VERCEL_TOKEN env var (CI), else the logged-in `vercel` CLI (`vercel api`).
Intentional pins go in scripts/vercel_branch_pin_allowlist.txt, one host per line.

Usage:
  python3 scripts/vercel_branch_pin_gate.py            # exit 1 on unlisted pins
  python3 scripts/vercel_branch_pin_gate.py --self-test
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

TEAM = os.environ.get("VERCEL_TEAM_ID", "team_narCbxUgS4eiieJKRv1QMfff")  # arcs-care
ALLOWLIST = Path(__file__).with_name("vercel_branch_pin_allowlist.txt")


def api(path):
    sep = "&" if "?" in path else "?"
    token = os.environ.get("VERCEL_TOKEN")
    if token:
        req = urllib.request.Request(
            f"https://api.vercel.com{path}{sep}teamId={TEAM}",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    out = subprocess.run(["vercel", "api", path], capture_output=True, text=True, timeout=180)
    if out.returncode != 0:
        sys.exit(f"vercel api {path} failed: {out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def paged(path, key):
    items, until = [], None
    while True:
        page = api(path + (f"&until={until}" if until else ""))
        items += page.get(key, [])
        until = (page.get("pagination") or {}).get("next")
        if not until:
            return items


def load_allowlist(path=ALLOWLIST):
    if not path.exists():
        return set()
    return {l.split("#")[0].strip() for l in path.read_text().splitlines() if l.split("#")[0].strip()}


def find_pins(domains_by_project, allow):
    """Return [(project, host, branch)] for pinned domains not in the allowlist."""
    return [
        (proj, d["name"], d["gitBranch"])
        for proj, domains in domains_by_project.items()
        for d in domains
        if d.get("gitBranch") and d["name"] not in allow
    ]


def self_test():
    clean = {"arcs-v9": [{"name": "app.arcs.care", "gitBranch": None}]}
    planted = {"arcs-v9": [{"name": "app.arcs.care", "gitBranch": None},
                           {"name": "old.arcs.care", "gitBranch": "claude/dead-branch"}]}
    checks = [
        ("clean passes", find_pins(clean, set()) == []),
        ("planted pin fails", find_pins(planted, set()) == [("arcs-v9", "old.arcs.care", "claude/dead-branch")]),
        ("allowlisted pin passes", find_pins(planted, {"old.arcs.care"}) == []),
    ]
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    projects = paged("/v9/projects?limit=100", "projects")
    domains = {p["name"]: paged(f"/v9/projects/{p['id']}/domains?limit=100", "domains") for p in projects}
    pins = find_pins(domains, load_allowlist())
    total = sum(len(v) for v in domains.values())
    if pins:
        for proj, host, branch in pins:
            print(f"::error::{host} (project {proj}) is pinned to branch {branch}; it serves that preview, not production")
        print(f"branch-pin gate: FAIL, {len(pins)} pinned of {total} domains across {len(projects)} projects")
        print("fix: vercel api /v9/projects/<project>/domains/<host> -X PATCH with body {\"gitBranch\": null}, or allowlist it")
        return 1
    print(f"branch-pin gate: OK, 0 pinned of {total} domains across {len(projects)} projects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
