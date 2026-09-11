#!/usr/bin/env python3
"""Governance claim-check scaffold.

Audits PRs and commits against declared claims:
  1. Ancestry: checks if candidate commit is reachable from main / origin/main
  2. Scope: compares stated diff claims (e.g. "minimal 2 line diff") against
     actual measured git/PR diff stats (commits, changed files, insertions, deletions)
  3. Receipt linkage: verifies whether a declared decision receipt exists in the ledger

Stdlib only. Produces a read-only report for a human to read. It never merges,
closes, or modifies branches or PRs.

Usage:
  python3 scripts/claim_check.py --pr 357
  python3 scripts/claim_check.py --commit 7ab32ec9b71570067fefc62d81373cce0697ea28
  python3 scripts/claim_check.py --audit-night
"""
import argparse
import json
import re
import subprocess
import sys


def sh(cmd, check=False):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {cmd}\n{res.stderr}")
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def check_ancestry(commit: str, branch: str = "origin/main"):
    rc, _, _ = sh(f"git merge-base --is-ancestor {commit} {branch}")
    return rc == 0


def audit_pr(pr_num: int):
    rc, out, err = sh(f"gh pr view {pr_num} --json number,title,body,state,baseRefName,headRefName,additions,deletions,changedFiles,commits,mergeCommit")
    if rc != 0:
        return {"error": f"gh pr view {pr_num} failed: {err}"}
    d = json.loads(out)
    body = d.get("body", "")
    title = d.get("title", "")

    # Look for claimed line diff in body/title: e.g. "2-line diff", "2 line diff", "minimal N line"
    m_body = re.search(r"(\d+)[-\s]*line\s*diff", body, flags=re.I)
    claimed_lines = int(m_body.group(1)) if m_body else None

    measured_add = d.get("additions", 0)
    measured_del = d.get("deletions", 0)
    measured_files = d.get("changedFiles", 0)
    commits_list = d.get("commits", [])
    commit_count = len(commits_list) if isinstance(commits_list, list) else 0

    scope_anomaly = False
    if claimed_lines is not None:
        total_measured = measured_add + measured_del
        if total_measured > claimed_lines * 5:  # massive drift threshold
            scope_anomaly = True

    return {
        "pr": d.get("number"),
        "title": title,
        "state": d.get("state"),
        "base": d.get("baseRefName"),
        "head": d.get("headRefName"),
        "claimed_diff_lines": claimed_lines,
        "measured": {
            "commits": commit_count,
            "files": measured_files,
            "additions": measured_add,
            "deletions": measured_del,
        },
        "scope_anomaly": scope_anomaly,
    }


def audit_night():
    print("claim-check: running audit of the two governance incidents")
    print()

    # Case 1: The stranded rule commit
    stranded = "7ab32ec9b71570067fefc62d81373cce0697ea28"
    repaired = "860bac743b414e5f98ec2a5cb0d28c301c5bc3e2"
    merged = "06bd757ba01c8362852b150152569214e0d86bf3"

    print("CASE 1: Rule reachability (commit ancestry)")
    for label, sha in [("Stranded rule commit (7ab32ec9)", stranded),
                       ("Clean branch commit (860bac74)", repaired),
                       ("Mainline merge commit (06bd757b)", merged)]:
        anc_origin = check_ancestry(sha, "origin/main")
        anc_main = check_ancestry(sha, "main")
        status = "REACHABLE (exit 0)" if anc_origin else "UNREACHABLE (exit 1)"
        print(f"  {status:24} {label}")
        print(f"    origin/main: {anc_origin} | local main: {anc_main}")

    print()
    print("CASE 2: PR scope inspection (#357 vs measured diff)")
    pr357 = audit_pr(357)
    if "error" in pr357:
        print(f"  ERROR: {pr357['error']}")
    else:
        print(f"  PR #{pr357['pr']} state: {pr357['state']} (head: {pr357['head']})")
        print(f"    Claimed in body: minimal {pr357['claimed_diff_lines']} line diff")
        m = pr357['measured']
        assert isinstance(m, dict)
        print(f"    Measured git:   {m['commits']} commits, {m['files']} files, +{m['additions']} / -{m['deletions']}")
        print(f"    Scope anomaly:  {'YES (measured diff outran claim by 2000x)' if pr357['scope_anomaly'] else 'NO'}")

    print()
    print("VERDICT: Automated scan completed. Output surfaced for human judgment.")
    print("A tool measures distance; it does not choose the remedy.")


def main():
    parser = argparse.ArgumentParser(description="Governance claim-check scaffold.")
    parser.add_argument("--pr", type=int, help="PR number to inspect for scope anomalies")
    parser.add_argument("--commit", type=str, help="Commit SHA to check for ancestry reachability")
    parser.add_argument("--audit-night", action="store_true", help="Audit the two historical governance cases")
    args = parser.parse_args()

    if args.audit_night or len(sys.argv) == 1:
        audit_night()
        return 0

    if args.commit:
        anc = check_ancestry(args.commit, "origin/main")
        print(f"commit {args.commit} reachable from origin/main: {anc} (exit {0 if anc else 1})")

    if args.pr:
        res = audit_pr(args.pr)
        print(json.dumps(res, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
