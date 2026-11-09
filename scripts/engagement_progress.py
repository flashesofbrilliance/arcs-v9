#!/usr/bin/env python3
"""engagement_progress.py: log progress on an engagement row, re-render, sync the hub, gate.

Progress lives in the engagement record (engagement.json "progress", append-only). The renderer
folds it into out/step1_tree.json, and scripts/myally_hub_sync.py inlines that into the hub, so the
Step 1 tab and its "Where things stand" band on myally.arcs.care read one block.

  python3 scripts/engagement_progress.py w1a start  "Reading the code"   # in progress
  python3 scripts/engagement_progress.py w1a done   "Read the code and database rules" --hours 2.5
  python3 scripts/engagement_progress.py w0b block  "Waiting on the GitHub invite"
  python3 scripts/engagement_progress.py w1a review "The three piles are written up"  # ready for the client
  python3 scripts/engagement_progress.py w1a reset                        # back to not started
  python3 scripts/engagement_progress.py --comments 3 --next-call 2026-11-11   # comments batched for the call
  python3 scripts/engagement_progress.py --list                           # where every row stands
  python3 scripts/engagement_progress.py --ship                           # PR + safe merge of what is logged

States: start (in_progress), review (ready for the client's review), done, block (blocked),
reset (not_started). A review entry also writes a client notice to <engagement>/drafts/notices.md for
the channel the client chose (record "notify_channel": tab, email or slack). Nothing is ever sent:
Zach sends every client message. Slack is a stub until its connector is authorised and the client is
known to use it. --comments N and --next-call DATE set the "batched for the next review call" line. --date YYYY-MM-DD backdates
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
ALIAS = {"start": "in_progress", "in_progress": "in_progress", "review": "review", "done": "done", "block": "blocked",
         "blocked": "blocked", "reset": "not_started", "not_started": "not_started"}
WORD = {"not_started": "not started", "in_progress": "in progress", "review": "ready for review", "done": "done",
        "blocked": "blocked"}
TAB_URL = "https://myally.arcs.care/light-audit"
CHANNELS = ("tab", "email", "slack")


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


def slack_stub(text: str) -> str:
    """Placeholder for a shared-channel post. Not wired: the Slack connector is not authorised and it is
    not known whether the client uses Slack. It never posts; it says so, and the draft is the deliverable."""
    return "slack: not wired (draft only; Zach posts it himself if the client uses a shared channel)"


def write_notice(d: str, rec: dict, label: str, date: str) -> str:
    """Append a client-facing notice draft for a review item. Never sends anything."""
    channel = rec.get("notify_channel", "email")
    if channel not in CHANNELS:
        sys.exit(f"engagement_progress: notify_channel must be one of {CHANNELS}")
    text = (f"Ready for your review on the Step 1 tab ({TAB_URL}): {label}. Send comments whenever suits you; "
            f"I batch them for the next review call.")
    if "\u2014" in text:
        sys.exit("engagement_progress: notice has an em-dash")
    os.makedirs(os.path.join(d, "drafts"), exist_ok=True)
    path = os.path.join(d, "drafts", "notices.md")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"- {date} · channel {channel} · NOT SENT · {text}\n")
    msg = f"  notice drafted for {channel} in {os.path.relpath(path, ROOT)} (not sent; you send it)"
    if channel == "tab":
        msg = "  channel is the tab: the band shows it; a notice draft is kept anyway in drafts/notices.md"
    if channel == "slack":
        msg += "\n  " + slack_stub(text)
    return msg


def apply_and_gate(d: str, before: str, rec: dict) -> None:
    errs = er.validate_progress(rec)
    if errs:
        sys.exit("engagement_progress: refused: " + "; ".join(errs))
    path = rec_path(d)
    open(path, "w", encoding="utf-8").write(dump(rec))
    try:
        sync_and_gate(d)
    except SystemExit:
        open(path, "w", encoding="utf-8").write(before)  # leave the record as it was
        er.write(d)
        run([sys.executable, "scripts/myally_hub_sync.py"], check=False)
        raise


def set_batch(d: str, comments, next_call) -> None:
    path = rec_path(d)
    before = open(path, encoding="utf-8").read()
    rec = json.loads(before)
    rb = dict(rec.get("review_batch") or {"pending": 0, "next_call": None})
    if comments is not None:
        rb["pending"] = comments
    if next_call is not None:
        rb["next_call"] = next_call or None
    rec["review_batch"] = rb
    apply_and_gate(d, before, rec)
    print(f"review batch: {rb['pending']} comment(s) for the call on {rb.get('next_call') or 'a date not yet set'}")


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
    if "\u2014" in note:
        sys.exit("engagement_progress: refused: note has an em-dash")
    apply_and_gate(d, before, rec)
    label = er.Ctx(rec, er.resolve(rec)).sub(rows[row][1]["label"])
    print(f"logged {row} {WORD[state]} on {date}: {label}" + (f" ({note})" if note else ""))
    if state == "review":
        print(write_notice(d, rec, label, date))
    print("  not live yet: run with --ship when you're ready to publish")


def listing(d: str) -> None:
    rec = json.load(open(rec_path(d), encoding="utf-8"))
    ctx = er.Ctx(rec, er.resolve(rec))
    for name in rec.get("exports", []):
        block = er.fold_progress(rec[name], rec.get("progress", []), rec.get("review_batch"))
        if not isinstance(block, dict) or "rows" not in block:
            continue
        p = block["progress"]
        print(f"{name}: {p['hours_done']} of {p['hours_total']} hours done, {p['items_done']} of {p['items_total']} items, "
              f"{len(p['review'])} ready for review, {p['batched']} comment(s) batched for {p['next_call'] or 'no call set'}")
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
    ap.add_argument("--comments", type=int, help="comments batched for the next review call")
    ap.add_argument("--next-call", help="date of the next review call, YYYY-MM-DD (empty string clears it)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ship", action="store_true")
    a = ap.parse_args()
    d = os.path.abspath(a.dir)
    if a.list:
        listing(d)
        return 0
    if a.comments is not None or a.next_call is not None:
        set_batch(d, a.comments, a.next_call)
    if a.row:
        if not a.state:
            ap.error("give a state: start, review, done, block or reset")
        log(d, a.row, ALIAS[a.state], a.note.strip(), a.date, a.hours)
    if a.ship:
        ship(d)
    elif not a.row and a.comments is None and a.next_call is None:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
