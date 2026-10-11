#!/usr/bin/env python3
"""Reticulated dependency sweep (seed: induced-dependency-mapping).

Cross-references open PRs' failing CI checks and file-level diff overlap to
classify open work into what's actually sequential vs what's safe in parallel:

  - BLOCKING ROOT   a failing check name shared by 2+ open PRs — one root cause
                     gating N PRs at once. Fix it once, re-check unblocks all N.
  - UNIQUE DEFECT    a failing check that appears on exactly one PR — that PR's
                     own bug, not a shared blocker.
  - FILE OVERLAP     two open branches touching the same file(s) against main —
                     merge-order risk; land one before rebasing/touching the other.
  - PARALLEL-SAFE    no shared root, no file overlap — independent, fan-out freely.

Inference only by default: never merges, pushes, or comments. stdlib + `gh` + `git`.

With --emit, it additionally makes each discovered blocking root DURABLE instead
of dying on stdout: it finds-or-creates one tracking issue per blocking root and
keeps that issue's body listing the currently-blocked PRs. Additive only — it
never closes, deletes, or unlinks.

PLATFORM CONSTRAINT (verified 2026-09-26, the hard way): GitHub's issue
dependencies and sub-issues are ISSUE-TO-ISSUE ONLY. A pull request cannot carry
either relation, in either direction:
    POST /issues/<pr>/dependencies/blocked_by -> 422 "Source issue may only be an issue"
    POST /issues/<n>/sub_issues               -> 422 "Sub issue may only be an issue"
Critically, the READ endpoint lies: GET /issues/<pr>/dependencies/blocked_by
returns 200 [] for a PR, which looks like support. Only the write path tells the
truth. So the formal dependency graph cannot express "PR blocked by CI root".
The `#NNN` references in the tracking issue body are the best available native
representation — GitHub renders them as cross-links and they appear in each PR's
timeline, so the relation is real and bidirectionally visible, just informal.

Usage:
    python3 scripts/dependency_sweep.py             # markdown report to stdout
    python3 scripts/dependency_sweep.py --json      # raw data for the night-moves digest
    python3 scripts/dependency_sweep.py --emit      # also write the relations to GitHub
    python3 scripts/dependency_sweep.py --emit --dry-run   # print the writes, make none

Why this split: the sweep INFERS relations from CI signal; GitHub's dependency
graph stores DECLARED ones. Neither replaces the other, so the sweep stays the
inference engine and GitHub becomes the durable record.
"""
import json
import subprocess
import sys
from collections import defaultdict

# Mechanical/auto-refreshed files that churn every session and don't represent
# a real feature-level collision between two branches (session-start hooks
# rewrite these regardless of what a branch is actually working on).
NOISY_FILES = {
    "_STATE/snapshot.json",
    "_STATE/pulse.json",
    "_INBOX/pulse.jsonl",
    "_INBOX/lattice-drift.jsonl",
    "_INBOX/seedbank-drift.jsonl",
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def gh_json(cmd):
    return json.loads(run(cmd))


def open_prs():
    return gh_json([
        "gh", "pr", "list", "--state", "open", "--limit", "100",
        "--json", "number,title,headRefName",
    ])


def failing_checks(pr_number):
    try:
        data = gh_json(["gh", "pr", "view", str(pr_number), "--json", "statusCheckRollup"])
    except subprocess.CalledProcessError:
        return []
    checks = data.get("statusCheckRollup") or []
    out = []
    for c in checks:
        conclusion = (c.get("conclusion") or c.get("state") or "").upper()
        if conclusion in ("FAILURE", "ERROR", "CANCELLED"):
            out.append(c.get("name") or c.get("context") or "<unnamed check>")
    return sorted(set(out))


def changed_files(branch):
    try:
        run(["git", "fetch", "origin", branch, "--quiet"])
        out = run(["git", "diff", "--name-only", f"origin/main...origin/{branch}"])
    except subprocess.CalledProcessError:
        return set()
    return set(f for f in out.splitlines() if f.strip() and f.strip() not in NOISY_FILES)


def sweep():
    prs = open_prs()
    by_check = defaultdict(list)  # check name -> [pr numbers]
    pr_checks = {}
    pr_files = {}

    for pr in prs:
        n = pr["number"]
        checks = failing_checks(n)
        pr_checks[n] = checks
        for c in checks:
            by_check[c].append(n)
        pr_files[n] = changed_files(pr["headRefName"])

    blocking_roots = {c: nums for c, nums in by_check.items() if len(nums) >= 2}
    unique_defects = {c: nums[0] for c, nums in by_check.items() if len(nums) == 1}

    file_overlaps = []
    nums = list(pr_files.keys())
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            a, b = nums[i], nums[j]
            shared = pr_files[a] & pr_files[b]
            if shared:
                file_overlaps.append({"a": a, "b": b, "files": sorted(shared)})

    blocked_nums = set()
    for nums_ in blocking_roots.values():
        blocked_nums.update(nums_)
    for pair in file_overlaps:
        blocked_nums.add(pair["a"])
        blocked_nums.add(pair["b"])

    parallel_safe = [pr["number"] for pr in prs if pr["number"] not in blocked_nums]

    return {
        "prs": {pr["number"]: pr["title"] for pr in prs},
        "blocking_roots": blocking_roots,
        "unique_defects": unique_defects,
        "file_overlaps": file_overlaps,
        "parallel_safe": parallel_safe,
    }


def render_markdown(data):
    lines = ["## Dependency sweep (reticulated map)", ""]

    lines.append(f"**{len(data['prs'])} open PRs surveyed.**")
    lines.append("")

    if data["blocking_roots"]:
        lines.append("### Blocking roots (fix once, unblocks many)")
        for check, nums in sorted(data["blocking_roots"].items(), key=lambda kv: -len(kv[1])):
            prs_str = ", ".join(f"#{n}" for n in nums)
            lines.append(f"- **{check}** — blocks {len(nums)} PRs: {prs_str}")
        lines.append("")
    else:
        lines.append("### Blocking roots\nNone — no failing check is shared across 2+ PRs.\n")

    if data["file_overlaps"]:
        lines.append("### Sequential pairs (same files touched — merge order matters)")
        for pair in data["file_overlaps"]:
            a, b = pair["a"], pair["b"]
            files_str = ", ".join(pair["files"][:5])
            more = f" (+{len(pair['files']) - 5} more)" if len(pair["files"]) > 5 else ""
            lines.append(f"- **#{a}** <-> **#{b}** share: {files_str}{more}")
        lines.append("")
    else:
        lines.append("### Sequential pairs\nNone — no two open branches touch the same file.\n")

    if data["unique_defects"]:
        lines.append("### Unique defects (that PR's own bug, not systemic)")
        for check, n in data["unique_defects"].items():
            lines.append(f"- #{n}: {check}")
        lines.append("")

    lines.append(f"### Parallel-safe ({len(data['parallel_safe'])})")
    if data["parallel_safe"]:
        for n in data["parallel_safe"]:
            title = data["prs"].get(n, "")
            lines.append(f"- #{n} — {title}")
    else:
        lines.append("None currently — every open PR is entangled with at least one other.")

    return "\n".join(lines)


REPO = "flashesofbrilliance/arcs-v9"
ROOT_ISSUE_PREFIX = "[blocking-root]"


def root_issue_body(check, pr_numbers):
    return (
        f"CI check `{check}` is failing identically on {len(pr_numbers)} open PRs, "
        f"so it is a shared root cause rather than a defect in any one of them. "
        f"Fixing it once unblocks all of them.\n\n"
        f"**Currently blocked:** " + ", ".join(f"#{n}" for n in sorted(pr_numbers, reverse=True))
        + "\n\n---\n"
        "Maintained by `scripts/dependency_sweep.py --emit`; the list above is "
        "refreshed on each run. These are plain `#NNN` cross-references, not formal "
        "issue dependencies, because GitHub's dependency and sub-issue relations are "
        "issue-to-issue only and reject pull requests (422 `Source issue may only be "
        "an issue`). Closing this issue is a human decision."
    )


def find_root_issue(check):
    """Find the tracking issue for a blocking root, by exact title. None if absent."""
    title = f"{ROOT_ISSUE_PREFIX} {check}"
    rows = gh_json([
        "gh", "issue", "list", "--repo", REPO, "--state", "open",
        "--search", f'"{title}" in:title', "--json", "number,title", "--limit", "50",
    ])
    for r in rows:
        if r["title"] == title:
            return r["number"]
    return None


def emit_relations(data, dry_run):
    """Make each blocking root durable as a tracking issue.

    Additive only: find-or-create the issue, then refresh its body with the
    currently-blocked PR list. Never closes, deletes, or unlinks anything.
    See the module docstring for why this is cross-references and not formal
    issue dependencies.
    """
    actions = []
    for check, pr_numbers in sorted(data["blocking_roots"].items(), key=lambda kv: -len(kv[1])):
        title = f"{ROOT_ISSUE_PREFIX} {check}"
        body = root_issue_body(check, pr_numbers)
        root = find_root_issue(check)
        blocked = ", ".join(f"#{n}" for n in sorted(pr_numbers, reverse=True))

        if root is None:
            if dry_run:
                actions.append(f"CREATE {title!r} -> blocks {len(pr_numbers)}: {blocked}")
                continue
            out = run([
                "gh", "issue", "create", "--repo", REPO,
                "--title", title, "--body", body, "--label", "blocked",
            ])
            root = int(out.strip().rstrip("/").split("/")[-1])
            actions.append(f"CREATED #{root} {title!r} -> blocks {len(pr_numbers)}: {blocked}")
            continue

        if dry_run:
            actions.append(f"UPDATE #{root} {title!r} -> blocks {len(pr_numbers)}: {blocked}")
            continue
        try:
            run(["gh", "issue", "edit", str(root), "--repo", REPO, "--body", body,
                 "--add-label", "blocked"])
            actions.append(f"UPDATED #{root} {title!r} -> blocks {len(pr_numbers)}: {blocked}")
        except subprocess.CalledProcessError as e:
            actions.append(f"FAILED #{root}: {e}")
    return actions


def main():
    data = sweep()
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
        return

    print(render_markdown(data))

    if "--emit" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        print("\n### Emitting native GitHub relations" + (" (DRY RUN)" if dry_run else ""))
        for line in emit_relations(data, dry_run):
            print(line)


if __name__ == "__main__":
    main()
