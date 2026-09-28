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


def main(argv: list[str]) -> int:
    all_rows = rows()
    by_id = {r["id"]: r for r in all_rows if r.get("id")}
    todo = [r for r in all_rows if r.get("id") and r.get("gh_sync") and not r.get("gh_issue")]
    if "--check" in argv:
        print(f"backlog-sync: {len(todo)} gh_sync row(s) without an issue")
        return 1 if todo else 0
    for r in todo:
        title = f"[backlog] {r['id']}"
        if "--dry-run" in argv:
            print(f"would create: {title}"); continue
        p = subprocess.run(["gh", "issue", "create", "--title", title, "--body", body(r, by_id)], capture_output=True, text=True, cwd=ROOT)
        if p.returncode != 0:
            print(f"✖ {r['id']}: {p.stderr.strip()[:200]}", file=sys.stderr); continue
        url = p.stdout.strip().splitlines()[-1]
        r["gh_issue"] = int(url.rstrip("/").split("/")[-1]); r["gh_url"] = url
        print(f"created #{r['gh_issue']} for {r['id']}")
    if "--dry-run" not in argv:
        write(all_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
