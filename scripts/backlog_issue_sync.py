#!/usr/bin/env python3
"""
backlog_issue_sync.py — mirror induced-backlog rows to GitHub issues (create-only, idempotent).

A row opts in with "gh_sync": true. On sync, a row with no "gh_issue" gets an issue created
(title = id, body = jtbd + route + gates + trigger + depends_on + unblocks + fates) and the
number written back into the row. Rows that already carry gh_issue are left alone (edits to
issue bodies are a human/GitHub-side act; this script never rewrites an issue). Dependencies
are rendered as "Blocked by #N" / "Unblocks #N" lines once the referenced rows have numbers,
so GitHub's own cross-reference links carry the second-order map.

The backlog stays the SSOT; the issue is a projection (ADR-065). stdlib + `gh` CLI.

Usage:
  python3 scripts/backlog_issue_sync.py            # create missing issues, write numbers back
  python3 scripts/backlog_issue_sync.py --dry-run  # print what would be created
  python3 scripts/backlog_issue_sync.py --check    # exit 1 if any gh_sync row lacks gh_issue
  python3 scripts/backlog_issue_sync.py board      # air-traffic board: open rows, blockers, 2nd/3rd/4th-order unblocks
  python3 scripts/backlog_issue_sync.py --self-test  # argv contract in a temp repo with a stubbed gh
--check, --dry-run and board are read-only: they never write the backlog and never call gh.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "_QUEUE" / "induced-backlog.jsonl"


def rows() -> list[dict]:
    return [json.loads(l) for l in BACKLOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def write(all_rows: list[dict]) -> None:
    BACKLOG.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_rows), encoding="utf-8")


def body(r: dict, by_id: dict[str, dict]) -> str:
    def ref(i: str) -> str:
        n = by_id.get(i, {}).get("gh_issue")
        return f"#{n} (`{i}`)" if n else f"`{i}` (no issue yet)"
    lines = [f"**JTBD.** {r.get('jtbd','')}", "",
             f"**Route.** `{json.dumps(r.get('route', {}))}`",
             f"**Gates.** " + ("; ".join(r.get("gates", [])) or "none"),
             f"**Trigger.** {r.get('trigger','')}",
             f"**Fates.** " + (", ".join(r.get("fates", [])) or "none"),
             f"**Status at sync.** {r.get('status','')}"]
    if r.get("depends_on"):
        lines.append("**Blocked by.** " + ", ".join(ref(i) for i in r["depends_on"]))
    if r.get("unblocks"):
        lines.append("**Unblocks.** " + ", ".join(ref(i) for i in r["unblocks"]))
    if r.get("chip"):
        lines += ["", "**Chip (cold-molt prompt).** " + r["chip"]]
    lines += ["", f"_Mirrored from `_QUEUE/induced-backlog.jsonl` id `{r['id']}` by scripts/backlog_issue_sync.py; the backlog row is the SSOT._"]
    return "\n".join(lines)


def board(all_rows: list[dict]) -> None:
    """Air-traffic control without a conductor: what each open row waits on, and what its landing
    clears at depth 2, 3, 4. Level-triggered by construction: a blocker is CLEAR when its row's
    status no longer starts OPEN (or it has landed on main); nothing here schedules anything."""
    by_id = {r["id"]: r for r in all_rows if r.get("id")}
    def is_open(i: str) -> bool:
        r = by_id.get(i); st = str(r.get("status", "")).upper() if r else ""
        # a row is open until its status records a landing (statuses are append-only, so the
        # landing note sits AFTER the original OPEN prefix)
        landed = any(t in st for t in ("LANDED", "MERGED", "DONE", "CLOSED", "SHIPPED", "INSTRUMENTED")) and "IN PROGRESS" not in st
        return bool(r) and (st.startswith("OPEN") or st.startswith("INDUCED")) and not landed
    def unblocks(i: str) -> list[str]:
        direct = list(by_id.get(i, {}).get("unblocks", []))
        direct += [k for k, r in by_id.items() if i in (r.get("depends_on") or []) and k not in direct]
        return direct
    def chain(i: str, depth: int, seen: set) -> list[tuple[int, str]]:
        out = []
        for j in unblocks(i):
            if j in seen: continue
            seen.add(j); out.append((depth, j))
            if depth < 4: out += chain(j, depth + 1, seen)
        return out
    tracked = [r for r in all_rows if r.get("id") and (r.get("gh_sync") or r.get("depends_on") or r.get("unblocks"))]
    print(f"{'issue':<6} {'row':<40} {'state':<9} blocked-by -> clears (depth)")
    for r in sorted(tracked, key=lambda r: (str(r.get('rank', 99)), r['id'])):
        blockers = [f"{b}{'(OPEN)' if is_open(b) else '(clear/absent)'}" for b in (r.get("depends_on") or [])]
        st = "HOLDING" if any(is_open(b) for b in (r.get("depends_on") or [])) else ("READY" if is_open(r["id"]) else "LANDED?")
        downstream = chain(r["id"], 2, set())
        ds = ", ".join(f"{j}@{d}" for d, j in downstream) or "-"
        print(f"#{str(r.get('gh_issue') or '-'):<5} {r['id'][:40]:<40} {st:<9} {'; '.join(blockers) or '-'} -> {ds}")


def build_parser():
    import argparse
    ap = argparse.ArgumentParser(prog="backlog_issue_sync.py",
                                 description="Mirror gh_sync backlog rows to GitHub issues (create-only).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if any gh_sync row lacks gh_issue (read-only)")
    mode.add_argument("--dry-run", action="store_true", help="print what would be created (read-only)")
    mode.add_argument("--self-test", action="store_true", help="argv contract in a temp repo, stubbed gh")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("board", help="air-traffic board (read-only)")
    return ap


def main(argv: list[str]) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.self_test:
        if a.cmd:
            ap.error("--self-test takes no subcommand")
        return self_test()
    if a.cmd == "board" and (a.check or a.dry_run):
        ap.error("board takes no --check/--dry-run")
    all_rows = rows()
    by_id = {r["id"]: r for r in all_rows if r.get("id")}
    if a.cmd == "board":
        board(all_rows); return 0
    todo = [r for r in all_rows if r.get("id") and r.get("gh_sync") and not r.get("gh_issue")]
    if a.check:
        print(f"backlog-sync: {len(todo)} gh_sync row(s) without an issue")
        return 1 if todo else 0
    for r in todo:
        title = f"[backlog] {r['id']}"
        if a.dry_run:
            print(f"would create: {title}"); continue
        p = subprocess.run(["gh", "issue", "create", "--title", title, "--body", body(r, by_id)], capture_output=True, text=True, cwd=ROOT)
        if p.returncode != 0:
            print(f"✖ {r['id']}: {p.stderr.strip()[:200]}", file=sys.stderr); continue
        url = p.stdout.strip().splitlines()[-1]
        r["gh_issue"] = int(url.rstrip("/").split("/")[-1]); r["gh_url"] = url
        print(f"created #{r['gh_issue']} for {r['id']}")
    if not a.dry_run:
        write(all_rows)
    return 0


def _snapshot(paths: list[Path]) -> dict:
    import hashlib
    return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) if p.exists() else None
            for p in paths}


def self_test() -> int:
    """Copy this script into a temp repo, put a recording gh stub first on PATH, assert the argv contract."""
    import os, shutil, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="backlog-sync-selftest-")).resolve()
    fails = total = 0
    try:
        (tmp / "scripts").mkdir(); (tmp / "_QUEUE").mkdir(); (tmp / "bin").mkdir()
        me = tmp / "scripts" / "backlog_issue_sync.py"
        shutil.copy2(Path(__file__).resolve(), me)
        log = tmp / "gh-calls.log"
        gh = tmp / "bin" / "gh"
        gh.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\necho https://github.com/x/y/issues/42\n', encoding="utf-8")
        gh.chmod(0o755)
        backlog = tmp / "_QUEUE" / "induced-backlog.jsonl"
        backlog.write_text(json.dumps({"id": "row-a", "gh_sync": True, "status": "OPEN"}) + "\n"
                           + json.dumps({"id": "row-b", "status": "OPEN", "depends_on": ["row-a"]}) + "\n", encoding="utf-8")
        env = dict(os.environ, PATH=f"{tmp / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}")

        def run(*a):
            return subprocess.run([sys.executable, str(me), *a], capture_output=True, text=True, cwd=tmp, env=env)

        def ok(name, cond):
            nonlocal fails, total
            total += 1; fails += 0 if cond else 1
            print(("  PASS  " if cond else "  FAIL  ") + name)

        before = _snapshot([backlog])
        ok("unknown flag exits 2", run("--dryrun").returncode == 2)
        ok("extra positional exits 2", run("board", "extra").returncode == 2)
        ok("unknown subcommand exits 2", run("bored").returncode == 2)
        ok("--check with --dry-run exits 2", run("--check", "--dry-run").returncode == 2)
        ok("board with --check exits 2", run("board", "--check").returncode == 2)
        r = run("--check")
        ok("--check exits 1 on an unsynced row", r.returncode == 1 and "1 gh_sync row" in r.stdout)
        r = run("--dry-run")
        ok("--dry-run previews the create", r.returncode == 0 and "would create: [backlog] row-a" in r.stdout)
        r = run("board")
        ok("board renders", r.returncode == 0 and "row-b" in r.stdout)
        ok("read-only modes write nothing", _snapshot([backlog]) == before)
        ok("read-only modes and bad argv call no gh", not log.exists())
        r = run()
        rows_after = [json.loads(l) for l in backlog.read_text(encoding="utf-8").splitlines() if l.strip()]
        ok("real sync (stubbed gh) writes the number back", r.returncode == 0 and rows_after[0].get("gh_issue") == 42)
        ok("real sync called gh issue create once", log.exists() and log.read_text().count("issue create") == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"backlog_issue_sync self-test: {total - fails}/{total}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
