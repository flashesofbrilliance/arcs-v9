#!/usr/bin/env python3
"""engagement_progress.py: log progress on an engagement row, re-render, sync the hub, gate.

Progress lives in the engagement record (engagement.json "progress", append-only). The renderer
folds it into out/step1_tree.json, and scripts/myally_hub_sync.py inlines that into the hub, so the
Step 1 tab and its "Where things stand" band on myally.arcs.care read one block.

  python3 scripts/engagement_progress.py w1a start  "Reading the code"   # in progress
  python3 scripts/engagement_progress.py w1a done   "Read the code and database rules" --hours 2.5
  python3 scripts/engagement_progress.py w0b block  "Waiting on the GitHub invite"
  python3 scripts/engagement_progress.py w1a reset                        # back to not started
  python3 scripts/engagement_progress.py --list                           # where every row stands
  python3 scripts/engagement_progress.py --ship                           # PR + safe merge of what is logged

States: start (in_progress), done, block (blocked), reset (not_started). --date YYYY-MM-DD backdates
(default today). Log as often as you like; --ship once (say at the end of a working day) commits the
record, its outputs and the hub on a fresh branch, opens a PR and runs scripts/safe_merge.sh.
The site updates when Vercel finishes deploying main. Write the decision receipt from the template
safe_merge.sh prints. Notes are client-facing: first person singular, plain language, no em-dash.

Stdlib only. Writes the record, its out/ folder and public/myally-hub.html; --ship also runs git/gh.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import engagement_render as er  # noqa: E402

DEFAULT_DIR = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld")
HUB = "public/myally-hub.html"
ALIAS = {"start": "in_progress", "in_progress": "in_progress", "done": "done", "block": "blocked",
         "blocked": "blocked", "reset": "not_started", "not_started": "not_started"}
WORD = {"not_started": "not started", "in_progress": "in progress", "done": "done", "blocked": "blocked"}


def run(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode:
        sys.exit(f"engagement_progress: {' '.join(cmd)} failed:\n{p.stdout}{p.stderr}")
    return p


def rec_path(d: str) -> str:
    return os.path.join(d, "engagement.json")


def dump(rec: dict) -> str:
    return json.dumps(rec, indent=2, ensure_ascii=False) + "\n"


def sync_and_gate(d: str) -> None:
    er.write(d)
    run([sys.executable, "scripts/myally_hub_sync.py"])
    gates = [
        [sys.executable, "scripts/engagement_render.py", "--check", "--dir", os.path.relpath(d, ROOT)],
        [sys.executable, "scripts/myally_hub_sync.py", "--check"],
        [sys.executable, "scripts/artifact_wrap_lint.py", HUB],
        [sys.executable, "scripts/page_gate.py", "--counterpart", HUB],
    ]
    for g in gates:
        p = run(g, check=False)
        name = os.path.basename(g[1])
        if p.returncode:
            sys.exit(f"engagement_progress: gate {name} failed:\n{p.stdout}{p.stderr}")
        print(f"  gate ok: {name}")


def log(d: str, row: str, state: str, note: str, date: str, hours=None) -> None:
    path = rec_path(d)
    before = open(path, encoding="utf-8").read()
    rec = json.loads(before)
    rows = er.tree_rows(rec)
    if row not in rows:
        sys.exit(f"engagement_progress: unknown row {row!r}; try --list")
    entry = {"row": row, "state": state, "date": date, "note": note}
    if hours is not None:
        entry["actual_hours"] = hours
    rec.setdefault("progress", []).append(entry)
    errs = er.validate_progress(rec) + (["note has an em-dash"] if "\u2014" in note else [])
    if errs:
        sys.exit("engagement_progress: refused: " + "; ".join(errs))
    open(path, "w", encoding="utf-8").write(dump(rec))
    try:
        sync_and_gate(d)
    except SystemExit:
        open(path, "w", encoding="utf-8").write(before)  # leave the record as it was
        er.write(d)
        run([sys.executable, "scripts/myally_hub_sync.py"], check=False)
        raise
    label = rows[row][1]["label"]
    print(f"logged {row} {WORD[state]} on {date}: {label}" + (f" ({note})" if note else ""))
    print("  not live yet: run with --ship when you're ready to publish")


def listing(d: str) -> None:
    rec = json.load(open(rec_path(d), encoding="utf-8"))
    ctx = er.Ctx(rec, er.resolve(rec))
    for name in rec.get("exports", []):
        block = er.fold_progress(rec[name], rec.get("progress", []))
        if not isinstance(block, dict) or "rows" not in block:
            continue
        p = block["progress"]
        print(f"{name}: {p['hours_done']} of {p['hours_total']} hours done, {p['items_done']} of {p['items_total']} items")
        for r in block["rows"]:
            st = r.get("status", {})
            pad = "" if r["kind"] == "phase" else "  "
            tail = f"  {st['date']} {st.get('note', '')}".rstrip() if st else ""
            print(f"  {pad}{r['id']:<5} {WORD[st.get('state', 'not_started')]:<12} {ctx.sub(r['label'])[:60]}{tail}")


def ship(d: str) -> None:
    rel = os.path.relpath(d, ROOT)
    run(["git", "fetch", "-q", "origin", "main"])
    if run(["git", "rev-list", "origin/main..HEAD"]).stdout.strip():
        sys.exit("engagement_progress --ship: HEAD has commits that are not on origin/main; ship from a checkout of main")
    allowed = (rel + "/", HUB)
    dirty = [ln[3:] for ln in run(["git", "status", "--porcelain"]).stdout.splitlines()]
    other = [f for f in dirty if not f.startswith(allowed)]
    if other:
        sys.exit("engagement_progress --ship: other files are changed; ship only progress:\n  " + "\n  ".join(other))
    if not dirty:
        sys.exit("engagement_progress --ship: nothing logged since the last ship")
    if run(["git", "rev-parse", "HEAD"]).stdout != run(["git", "rev-parse", "origin/main"]).stdout:
        sys.exit("engagement_progress --ship: HEAD is behind origin/main; update the checkout first (the log stays in your working tree)")
    sync_and_gate(d)
    rec = json.load(open(rec_path(d), encoding="utf-8"))
    branch = "claude/myally-progress-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    last = (rec.get("progress") or [{}])[-1]
    title = f"chore(myally): progress update, latest {last.get('row')} {WORD.get(last.get('state'), '')} [NCI:SKIP content]"
    run(["git", "switch", "-c", branch])
    run(["git", "add", rel, HUB])
    run(["git", "commit", "-q", "-m", title])
    run(["git", "push", "-q", "-u", "origin", branch])
    body = ("Progress log update for the My Ally Step 1 tab (record -> render -> hub sync). "
            "Gates run: engagement_render --check, myally_hub_sync --check, artifact_wrap_lint, page_gate --counterpart.")
    url = run(["gh", "pr", "create", "--base", "main", "--head", branch, "--title", title, "--body", body]).stdout.strip()
    pr = url.rstrip("/").split("/")[-1]
    sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    print(f"PR {url} at {sha}; merging with scripts/safe_merge.sh (waits for checks)")
    p = subprocess.run(["scripts/safe_merge.sh", pr, sha], cwd=ROOT)
    if p.returncode:
        sys.exit(f"engagement_progress --ship: safe_merge refused; PR {url} stays open")
    print("merged. Write the decision receipt from the template above; the site updates when Vercel deploys main.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("row", nargs="?")
    ap.add_argument("state", nargs="?", choices=sorted(ALIAS))
    ap.add_argument("note", nargs="?", default="")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--hours", type=float, help="actual hours spent, on done (private; never shown to the client)")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ship", action="store_true")
    a = ap.parse_args()
    d = os.path.abspath(a.dir)
    if a.list:
        listing(d)
        return 0
    if a.row:
        if not a.state:
            ap.error("give a state: start, done, block or reset")
        log(d, a.row, ALIAS[a.state], a.note.strip(), a.date, a.hours)
    if a.ship:
        ship(d)
    elif not a.row:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
