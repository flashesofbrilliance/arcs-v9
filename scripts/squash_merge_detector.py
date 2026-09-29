#!/usr/bin/env python3
"""
squash_merge_detector.py: flag PRs that landed on main WITHOUT a merge commit.

Policy (AGENTS.md gotcha 17): merge with `gh pr merge --merge`, never --squash or --rebase.
A squash or rebase lands as a 1-parent commit, which erases the branch's own commits and
the per-PR boundary that receipts cite. Branch protection cannot enforce this on the free
private plan, so this is detection, not prevention: run daily (.github/workflows/no-squash.yml).

Usage:
  python3 scripts/squash_merge_detector.py [--days N]   # exit 1 if any merged PR lacks a merge commit
  python3 scripts/squash_merge_detector.py --self-test
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys


def parents(sha: str) -> int:
    out = subprocess.run(["git", "rev-list", "--parents", "-n", "1", sha], capture_output=True, text=True)
    return len(out.stdout.split()) - 1 if out.returncode == 0 else -1


def classify(prs: list[dict], parent_count) -> list[str]:
    bad = []
    for p in prs:
        sha = (p.get("mergeCommit") or {}).get("oid")
        n = parent_count(sha) if sha else -1
        if n == 1:
            bad.append(f"#{p['number']} {sha[:8]} landed as a 1-parent commit (squash or rebase): {p.get('title', '')[:70]}")
        elif n < 0:
            bad.append(f"#{p['number']} merge commit {str(sha)[:8]} not found in this clone (fetch-depth 0?)")
    return bad


def self_test() -> int:
    fake = {"aaa": 2, "bbb": 1}
    got = classify([{"number": 1, "mergeCommit": {"oid": "aaa"}}, {"number": 2, "mergeCommit": {"oid": "bbb"}, "title": "x"}], lambda s: fake.get(s, -1))
    ok = len(got) == 1 and got[0].startswith("#2 ")
    print(f"  {'PASS' if ok else 'FAIL'}  merge commit passes, 1-parent flagged  {got}")
    print(f"self-test: {'OK' if ok else '1 FAIL'}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 2
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    r = subprocess.run(["gh", "pr", "list", "--state", "merged", "--base", "main", "--limit", "200",
                        "--search", f"merged:>={since}", "--json", "number,title,mergeCommit"], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr); return 2
    prs = json.loads(r.stdout)
    bad = classify(prs, parents)
    for b in bad:
        print(f"✖ {b}")
    print(f"squash-detector: {len(prs)} PR(s) merged since {since}, {len(bad)} without a merge commit")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
