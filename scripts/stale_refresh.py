#!/usr/bin/env python3
"""stale_refresh.py: run the snapshot regenerators the session-start hook reports stale, in one pass.

WHY: the per-commit catalogs stay current because pre-commit runs their --check gates. Snapshot
artifacts drift because they were built once and polled by nobody (memory
one-shot-ingest-decays-wire-into-recurring-loop). This is the recurring loop for them.

What one run does, in a throwaway worktree detached at a fresh origin/main (never your checkout):
  universe snapshot   universe_snapshot_emit.py            content emit (history stamp carried forward)
  lattice             lattice_drift_check.py --regenerate  mechanical countables only; epoch + judgment = Zach
  seedbank            seedbank_drift_check.py --regenerate receipt-only; curation (repo coverage) = Zach
  jtbd graph          universe_jtbd_adapter.py --check     gate result, receipt-only
  night-moves         age of the newest dated digest       receipt-only; the synthesis needs a model
Then: every changed path must be in ALLOW, or the run aborts with no PR. A clean diff opens ONE
data-only PR on branch chore/stale-refresh-<date>; an open PR on that prefix means skip (no pile-up).
The run receipt is appended to <repo>/_INBOX/stale-refresh.jsonl (gitignored).

NOT done here: universe_snapshot_emit.py --refresh (history epoch). It pushes to origin/main by
design and stays human-gated; the PR body says when it is due. Never merges. Never --no-verify.

  python3 scripts/stale_refresh.py --dry-run   # run everything, show diff + PR body, commit nothing
  python3 scripts/stale_refresh.py             # same, then commit, push, open the PR
  python3 scripts/stale_refresh.py --self-test # allowlist guard cases
Stdlib only (plus git and gh on PATH).
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

BRANCH_PREFIX = "chore/stale-refresh-"
ALLOW = (
    "runtime/specs/universe-snapshot.json",
    "runtime/specs/universe/",
    "src/data/universe-field.json",
    "runtime/specs/knowledge-lattice-v1.json",
)
NIGHT_MOVES_MAX_DAYS = 2  # a weekday digest; older than this is a gap


def sh(cmd: list[str], cwd: str, env: dict | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def outside_allow(paths: list[str]) -> list[str]:
    return [p for p in paths if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in ALLOW)]


def changed_paths(wt: str) -> list[str]:
    # name lists, not porcelain: sh() strips output, which would eat a status column
    _, mod = sh(["git", "diff", "--name-only", "HEAD"], wt)
    _, new = sh(["git", "ls-files", "--others", "--exclude-standard"], wt)
    return sorted(set(l for l in (mod + "\n" + new).splitlines() if l.strip()))


def night_moves_age(wt: str) -> tuple[str | None, int | None]:
    days = sorted(os.path.basename(f)[:10] for f in glob.glob(os.path.join(wt, "_STATE/night-moves/*.md"))
                  if re.match(r"\d{4}-\d{2}-\d{2}", os.path.basename(f)))
    if not days:
        return None, None
    return days[-1], (datetime.date.today() - datetime.date.fromisoformat(days[-1])).days


def open_refresh_pr(repo: str) -> str | None:
    rc, out = sh(["gh", "pr", "list", "--state", "open", "--json", "number,headRefName", "--limit", "200"], repo)
    if rc != 0:
        return "unknown (gh failed: %s)" % out[:120]
    for pr in json.loads(out or "[]"):
        if pr["headRefName"].startswith(BRANCH_PREFIX):
            return "#%d" % pr["number"]
    return None


def pick(out: str, pat: str) -> str:
    hits = [l.strip()[:200] for l in out.splitlines() if re.search(pat, l)]
    return "; ".join(hits) if hits else "(no matching line)"


def run(repo: str, dry: bool) -> int:
    today = datetime.date.today().isoformat()
    receipt: dict = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "dry_run": dry, "steps": {}}
    rc, out = sh(["git", "fetch", "--quiet", "origin", "main"], repo)
    if rc != 0:
        print("stale-refresh: fetch failed, nothing run: " + out[:200])
        return 0
    _, head = sh(["git", "rev-parse", "--short", "origin/main"], repo)
    receipt["base"] = head
    blocker = None if dry else open_refresh_pr(repo)
    wt = tempfile.mkdtemp(prefix="stale-refresh-")
    os.rmdir(wt)
    rc, out = sh(["git", "worktree", "add", "--detach", "--quiet", wt, "origin/main"], repo)
    if rc != 0:
        print("stale-refresh: worktree add failed: " + out[:200])
        return 0
    env = dict(os.environ, CLAUDE_PROJECT_DIR=wt)
    try:
        steps = [
            ("universe", ["python3", "scripts/universe_snapshot_emit.py"]),
            ("lattice", ["python3", "scripts/lattice_drift_check.py", "--regenerate"]),
            ("seedbank", ["python3", "scripts/seedbank_drift_check.py", "--regenerate"]),
            ("jtbd-graph", ["python3", "scripts/universe_jtbd_adapter.py", "--check"]),
        ]
        for name, cmd in steps:
            rc, out = sh(cmd, wt, env)
            receipt["steps"][name] = {"rc": rc, "out": out[-4000:]}
            print("[%s] rc=%d" % (name, rc))
            print("  " + "\n  ".join(out.splitlines()[-12:]))
        last, age = night_moves_age(wt)
        nm_gap = age is None or age > NIGHT_MOVES_MAX_DAYS
        receipt["steps"]["night-moves"] = {"last": last, "age_days": age, "gap": nm_gap}
        print("[night-moves] last dated digest %s, %s days old%s" % (last, age, " (GAP: needs the /night-moves synthesis)" if nm_gap else ""))

        paths = changed_paths(wt)
        bad = outside_allow(paths)
        receipt["changed"], receipt["outside_allow"] = paths, bad
        _, stat = sh(["git", "diff", "--stat"], wt)
        print("\n[diff] %d path(s) changed" % len(paths))
        if stat:
            print("  " + "\n  ".join(stat.splitlines()[-15:]))
        if bad:
            receipt["verdict"] = "ABORT: changed paths outside the allowlist"
            print("stale-refresh: ABORT, paths outside ALLOW (no PR): " + ", ".join(bad))
            return 1

        body = pr_body(receipt, head, today)
        if not paths:
            receipt["verdict"] = "nothing to commit"
        elif dry:
            receipt["verdict"] = "dry run: would open a PR"
            print("\n[pr body, not opened]\n" + body)
        elif blocker:
            receipt["verdict"] = "skipped: refresh PR %s still open" % blocker
        else:
            receipt["verdict"] = open_pr(wt, today, body)
        print("\nstale-refresh: " + receipt["verdict"])
        return 0
    finally:
        sh(["git", "worktree", "remove", "--force", wt], repo)
        os.makedirs(os.path.join(repo, "_INBOX"), exist_ok=True)
        with open(os.path.join(repo, "_INBOX", "stale-refresh.jsonl"), "a") as fh:
            fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def pr_body(r: dict, head: str, today: str) -> str:
    s = r["steps"]
    nm = s["night-moves"]
    lines = [
        "Scheduled stale-snapshot refresh from origin/main at `%s` (%s). Data files only; no code." % (head, today),
        "",
        "## What changed (mechanical)",
        *["- `%s`" % p for p in r["changed"]],
        "",
        "## Receipts (judgment stays with Zach)",
        "- universe: " + pick(s["universe"]["out"], r"^universe:"),
        "- lattice: " + pick(s["lattice"]["out"], r"DRIFT \[|advanced") + ". The epoch date and node statuses are hand-authored; re-author them by hand.",
        "- seedbank: " + pick(s["seedbank"]["out"], r"DRIFT \[") + ". Coverage gaps need a hand-written catalog row.",
        "- jtbd-graph `--check`: rc=%d, %s" % (s["jtbd-graph"]["rc"], pick(s["jtbd-graph"]["out"], r"--check: (PASS|FAIL)|exit 1|new finding")),
        "- night-moves: newest dated digest %s (%s days)%s" % (nm["last"], nm["age_days"], ", synthesis needed" if nm["gap"] else ""),
        "",
        "Not run: `universe_snapshot_emit.py --refresh` (history epoch; pushes to main, human-gated).",
        "Generated by `scripts/stale_refresh.py`. Merge only with `scripts/safe_merge.sh` on Zach's word.",
        "",
        "🤖 Generated with [Claude Code](https://claude.com/claude-code)",
    ]
    return "\n".join(lines)


def open_pr(wt: str, today: str, body: str) -> str:
    branch = BRANCH_PREFIX + today
    for cmd in (["git", "checkout", "--quiet", "-b", branch], ["git", "add", "-A"],
                ["git", "commit", "--quiet", "-m",
                 "chore(snapshots): scheduled stale-snapshot refresh %s [NCI:SKIP data]\n\n"
                 "Generated by scripts/stale_refresh.py. Mechanical outputs only.\n\n"
                 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" % today],
                ["git", "push", "--quiet", "-u", "origin", branch]):
        rc, out = sh(cmd, wt)
        if rc != 0:
            return "no PR: `%s` failed: %s" % (" ".join(cmd[:3]), out[-300:])
    rc, out = sh(["gh", "pr", "create", "--base", "main", "--head", branch,
                  "--title", "chore(snapshots): stale-snapshot refresh %s" % today, "--body", body], wt)
    return ("opened " + out.splitlines()[-1]) if rc == 0 else "pushed %s but gh pr create failed: %s" % (branch, out[-300:])


def self_test() -> int:
    cases = [
        ("snapshot allowed", outside_allow(["runtime/specs/universe-snapshot.json"]) == []),
        ("galaxy file allowed", outside_allow(["runtime/specs/universe/ontology.json"]) == []),
        ("lattice allowed", outside_allow(["runtime/specs/knowledge-lattice-v1.json"]) == []),
        ("code refused", outside_allow(["scripts/x.py"]) == ["scripts/x.py"]),
        ("prefix lookalike refused", outside_allow(["runtime/specs/universe-snapshot.json.bak"]) != []),
        ("seed file refused", outside_allow(["_SEEDS/index.jsonl"]) == ["_SEEDS/index.jsonl"]),
    ]
    for name, ok in cases:
        print(("✓ " if ok else "✖ ") + name)
    fails = sum(not ok for _, ok in cases)
    print("stale-refresh self-test: %d/%d" % (len(cases) - fails, len(cases)))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="refresh stale snapshot artifacts in one data-only PR")
    ap.add_argument("--dry-run", action="store_true", help="run and show the diff and PR body; commit nothing")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.repo, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
