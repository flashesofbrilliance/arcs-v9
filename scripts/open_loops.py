#!/usr/bin/env python3
"""open_loops.py: one front door over the stores ARCS already keeps. Read-only, no new store.

Answers "what loops are open" in one call instead of six. Sections, each capped (default 5)
with a count of the rest, because the point is less load, not a bigger list:

  1. Waiting on Zach's go   open PRs: mergeable + no failing check, and drafts needing review
  2. Closable in <15 min    open backlog rows whose cost_prior is <= 15 min
  3. Rotting                backlog past review_by (or untouched > 21d), unclaimed handoff
                            checkpoints > 7d, conflicting PRs > 14d
  3b. Ripe or secretly done backlog rows whose trigger fired, deps cleared, or status already
                            cites a merged PR (scripts/backlog_ripeness.py)
  4. Captured today         seeds planted and /witness stubs from today, not yet filed
  5. Coming up              scheduled one-time reminders (from --scheduled JSON; the scheduled
                            task store has no on-disk fire times, so the /loops command passes
                            a snapshot from list_scheduled_tasks)

Sources: `gh pr list`, _QUEUE/induced-backlog.jsonl, every worktree's
_STATE/handoff-progress.jsonl, _SEEDS/ledger.jsonl, _STATE/witness/<today>.jsonl.
A source that cannot be read is named in the output, never silently treated as empty.

Usage:
  python3 scripts/open_loops.py                 # ranked page
  python3 scripts/open_loops.py --summary       # 3 lines (SessionStart hook)
  python3 scripts/open_loops.py --spoken        # ~60 second read-aloud digest
  python3 scripts/open_loops.py --json
  python3 scripts/open_loops.py --scheduled snap.json --cap 3
  python3 scripts/open_loops.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE_RE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
DONE_RE = re.compile(r"^\s*(DONE|CLOSED|BUILT|LOCKED|COMPOSTED|SUPERSEDED|ROUTED)\b", re.I)
HELD_RE = re.compile(r"\b(HELD|HOLDING|TABLED)\b", re.I)
BACKLOG_STALE_DAYS = 21
CHECKPOINT_STALE_DAYS = 7
PR_CONFLICT_STALE_DAYS = 14
QUICK_MINUTES = 15


def _date(s) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def _minutes(cost) -> int | None:
    m = re.match(r"\s*(\d+)\s*min", str(cost or ""))
    return int(m.group(1)) if m else None


def _clip(s: str, n: int) -> str:
    """Trim at a word boundary and drop em-dashes that ride in from PR titles or backlog prose."""
    s = str(s).replace("\u2014", ",").replace("\u2013", "-")
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."


def _item(text: str, why: str, ref: str = "", score: float = 0.0) -> dict:
    return {"text": _clip(text, 80), "why": why, "ref": ref, "score": score}


# ---------------------------------------------------------------- gatherers (pure where possible)

def pr_loops(prs: list[dict], today: dt.date) -> tuple[list, list]:
    """-> (waiting_on_go, conflicting_stale)."""
    go, rot = [], []
    for p in prs:
        states = {(c.get("conclusion") or c.get("state") or "").upper() for c in p.get("statusCheckRollup") or []}
        failing = bool(states & {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED"})
        upd = _date(p.get("updatedAt")) or today
        age = (today - upd).days
        ref = f"#{p['number']}"
        title = p.get("title", "")
        if p.get("mergeable") == "CONFLICTING":
            if age > PR_CONFLICT_STALE_DAYS:
                rot.append(_item(f"{ref} {title}", f"conflicting, untouched {age}d", ref, age))
            continue
        if p.get("mergeable") == "MERGEABLE" and not failing:
            if p.get("isDraft"):
                go.append(_item(f"{ref} {title}", "draft, needs your review", ref, 50 - age))
            else:
                go.append(_item(f"{ref} {title}", "mergeable, checks green", ref, 100 - age))
    return go, rot


def backlog_loops(rows: list[dict], today: dt.date) -> tuple[list, list]:
    """-> (closable_quick, rotting)."""
    quick, rot = [], []
    for r in rows:
        if "id" not in r:
            continue
        status = str(r.get("status_note") or r.get("status") or r.get("state") or "open")
        if DONE_RE.match(status):
            continue
        rid = r["id"]
        jtbd = str(r.get("jtbd") or rid)
        if HELD_RE.search(status):
            continue  # trigger-gated by design; not rot until the trigger fires
        mins = _minutes(r.get("cost_prior"))
        if mins is not None and mins <= QUICK_MINUTES:
            quick.append(_item(jtbd, f"{mins} min, {rid}", rid, 100 - mins))
        due = _date(r.get("review_by"))
        if due:
            if due < today:
                rot.append(_item(jtbd, f"past review_by {due}", rid, (today - due).days))
            continue
        dates = [d for d in (_date(x) for x in DATE_RE.findall(json.dumps(r))) if d and d <= today]
        last = max(dates) if dates else None
        if last is None:
            rot.append(_item(jtbd, "no date on record", rid, 1))
        elif (today - last).days > BACKLOG_STALE_DAYS:
            rot.append(_item(jtbd, f"untouched {(today - last).days}d", rid, (today - last).days))
    return quick, rot


def checkpoint_loops(ledgers: list[tuple[str, dict]], today: dt.date, here: str = "") -> tuple[list, list]:
    """ledgers: [(worktree_name, last_row)]. -> (this_worktree, stale_others)."""
    mine, rot = [], []
    for name, r in ledgers:
        if not r or r.get("handoff_done"):
            continue
        d = _date(r.get("ts"))
        age = (today - d).days if d else 999
        it = _item(f"{name} ({r.get('branch', '')})", f"unclaimed {age}d, dirty={len(r.get('dirty') or [])}", name, age)
        if name == here:
            mine.append(it)
        elif age > CHECKPOINT_STALE_DAYS:
            rot.append(it)
    return mine, rot


def archived_trail_loops(trails: list[tuple[str, dict, bool]], archive: str) -> list:
    """trails: [(name, last_row, claimed_marker)]. One rolled-up item, counted once, never one per trail."""
    open_ = [n for n, r, claimed in trails if r and not r.get("handoff_done") and not claimed]
    if not open_:
        return []
    return [_item(f"{len(open_)} archived handoff trails unclaimed", f"compaction pass pending, {archive}", archive, len(open_))]


def captured_today(seed_rows: list[dict], witness_rows: list[dict], today: dt.date) -> list:
    out = []
    for s in seed_rows:
        if _date(s.get("ts")) == today and s.get("event") == "planted":
            out.append(_item(f"seed {s.get('seed', s.get('seed_id'))}", "planted today; route it or let it sleep", s.get("seed_id", ""), 2))
    for w in witness_rows:
        if not w.get("promoted"):
            out.append(_item(f"\"{w.get('quote', '')}\"", "witness stub, not promoted", "", 1))
    return out


def coming_up(sched: list[dict], now: dt.datetime) -> list:
    out = []
    for t in sched:
        when = t.get("fireAt") or t.get("next_run") or t.get("nextRunAt")
        if not when or t.get("cronExpression") or t.get("enabled") is False:
            continue
        try:
            at = dt.datetime.fromisoformat(str(when).replace("Z", "+00:00"))
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.astimezone()
        if at >= now:
            hrs = (at - now).total_seconds() / 3600
            out.append(_item(t.get("taskId") or t.get("name", "?"), f"in {hrs:.0f}h ({at:%a %m-%d %H:%M})", "", -hrs))
    return out


# ---------------------------------------------------------------- I/O

def _jsonl(p: Path) -> list[dict]:
    rows = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def _worktree_ledgers() -> list[tuple[str, dict]]:
    out = subprocess.run(["git", "-C", str(ROOT), "worktree", "list", "--porcelain"],
                         capture_output=True, text=True, timeout=10).stdout
    res = []
    for wt in (l[9:] for l in out.splitlines() if l.startswith("worktree ")):
        for rel in ("_STATE/handoff-progress.jsonl", ".claude/handoff-progress.jsonl"):
            p = Path(wt) / rel
            if p.is_file():
                rows = _jsonl(p)
                if rows:
                    res.append((os.path.basename(wt), rows[-1]))
    return res


def gather(scheduled: Path | None, today: dt.date, now: dt.datetime) -> dict:
    gaps: list[str] = []
    try:
        prs = json.loads(subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--limit", "100", "--json",
             "number,title,isDraft,mergeable,updatedAt,statusCheckRollup"],
            capture_output=True, text=True, timeout=10, cwd=ROOT, check=True).stdout)
    except Exception as e:  # noqa: BLE001  named, not swallowed
        prs, _ = [], gaps.append(f"gh pr list unreadable ({type(e).__name__})")
    go, pr_rot = pr_loops(prs, today)

    bl = ROOT / "_QUEUE/induced-backlog.jsonl"
    quick, bl_rot = backlog_loops(_jsonl(bl), today) if bl.is_file() else ([], [])
    if not bl.is_file():
        gaps.append("backlog missing")
    ripe = []
    if bl.is_file():
        try:  # ripeness: trigger fired / depends_on cleared / status already says it landed
            sys.path.insert(0, str(ROOT / "scripts"))
            import backlog_ripeness as br
            for f in br.run(_jsonl(bl), today):
                if f["verdict"] in ("SECRETLY-DONE", "RIPE", "BLOCKED"):
                    ripe.append(_item(f["id"], f"{f['verdict']}: {f['evidence'][:80]}", f["id"],
                                      {"SECRETLY-DONE": 3, "RIPE": 2, "BLOCKED": 1}[f["verdict"]]))
        except Exception as e:  # noqa: BLE001
            gaps.append(f"backlog ripeness unreadable ({type(e).__name__})")

    try:
        mine, cp_rot = checkpoint_loops(_worktree_ledgers(), today, ROOT.name)
    except Exception as e:  # noqa: BLE001
        mine, cp_rot = [], []
        gaps.append(f"worktree ledgers unreadable ({type(e).__name__})")

    # Archived trails from pruned worktrees (2026-10-04). Reads ONLY handoff-progress.jsonl and the
    # CLAIMED marker; the archive also holds .env* and dev.db copies, which are never opened here.
    arc_rot = []
    for arc in sorted(Path.home().glob("arcs-worktree-bundles/handoff-trails/*")):
        trails = []
        for wt in sorted(p for p in arc.iterdir() if p.is_dir()):
            led = wt / "_STATE/handoff-progress.jsonl"
            if led.is_file():
                rows = _jsonl(led)
                trails.append((wt.name, rows[-1] if rows else {}, (wt / "CLAIMED").exists()))
        arc_rot += archived_trail_loops(trails, str(arc).replace(str(Path.home()), "~"))

    seeds = ROOT / "_SEEDS/ledger.jsonl"
    wit = ROOT / f"_STATE/witness/{today}.jsonl"
    cap = captured_today(_jsonl(seeds) if seeds.is_file() else [], _jsonl(wit) if wit.is_file() else [], today)

    sched = []
    if scheduled:
        try:
            raw = json.loads(scheduled.read_text())
            sched = raw.get("tasks", raw) if isinstance(raw, dict) else raw
        except Exception as e:  # noqa: BLE001
            gaps.append(f"scheduled snapshot unreadable ({type(e).__name__})")
    else:
        gaps.append("coming-up not checked (pass --scheduled, or run /loops)")

    return {
        "date": str(today),
        "this_worktree": mine,
        "sections": [
            ["Waiting on your go", go],
            ["Closable in under 15 min", quick],
            ["Rotting", pr_rot + bl_rot + cp_rot + arc_rot],
            ["Ripe or secretly done", ripe],
            ["Captured today, not filed", cap],
            ["Coming up", coming_up(sched, now)],
        ],
        "gaps": gaps,
    }


# ---------------------------------------------------------------- renderers

def _top(items: list, cap: int) -> tuple[list, int]:
    s = sorted(items, key=lambda i: -i["score"])
    return s[:cap], max(0, len(s) - cap)


def render_page(d: dict, cap: int) -> str:
    out = [f"Open loops, {d['date']}"]
    for it in d["this_worktree"]:
        out.append(f"  THIS worktree has an unclaimed checkpoint: {it['why']}. Run /handoff-pickup.")
    for i, (title, items) in enumerate(d["sections"], 1):
        top, rest = _top(items, cap)
        out.append(f"\n{i}. {title} ({len(items)})")
        out += [f"   - {it['text']}  [{it['why']}]" for it in top] or ["   - nothing"]
        if rest:
            out.append(f"   + {rest} more (--cap to see them)")
    if d["gaps"]:
        out.append("\nNot read: " + "; ".join(d["gaps"]))
    return "\n".join(out)


def render_summary(d: dict) -> str:
    n = {t: len(i) for t, i in d["sections"]}
    go, quick, rot = d["sections"][0][1], d["sections"][1][1], d["sections"][2][1]
    first = _top(go, 1)[0] or _top(quick, 1)[0]
    lines = [
        f"open-loops: {n['Waiting on your go']} wait on your go · {n['Closable in under 15 min']} closable <15m · "
        f"{n['Rotting']} rotting · {n['Captured today, not filed']} captured today",
        f"open-loops: start with {first[0]['text']} [{first[0]['why']}]" if first else "open-loops: nothing waiting",
        "open-loops: full page -> /loops" + ("  (this worktree: unclaimed checkpoint, /handoff-pickup)" if d["this_worktree"] else ""),
    ]
    return "\n".join(lines)


def render_spoken(d: dict) -> str:
    """About 150 words: one breath per section, numbers said plainly, top item named."""
    say = [f"Good morning. Here is where things stand on {dt.date.fromisoformat(d['date']):%A}."]
    phr = {
        "Waiting on your go": "{n} things are waiting on your yes. The first is {t}.",
        "Closable in under 15 min": "{n} could close in under fifteen minutes. The quickest is {t}.",
        "Rotting": "{n} are going stale. The oldest is {t}.",
        "Ripe or secretly done": "{n} backlog rows are ripe, done, or blocked. First up is {t}.",
        "Captured today, not filed": "You caught {n} ideas today that have no home yet, starting with {t}.",
        "Coming up": "Coming up: {t}.",
    }
    for title, items in d["sections"]:
        if not items:
            continue
        top = _top(items, 1)[0][0]
        t = re.sub(r"^#(\d+)", r"pull request \1,", top["text"]).strip('".')
        say.append(phr[title].format(n=len(items), t=t))
    say.append("One loop closed beats three opened. Pick the first one and finish it.")
    return " ".join(say)


# ---------------------------------------------------------------- self-test

def self_test() -> int:
    today, ok, fails = dt.date(2026, 10, 4), 0, []

    def check(name, cond):
        nonlocal ok
        ok += 1 if cond else 0
        cond or fails.append(name)

    prs = [
        {"number": 1, "title": "green", "isDraft": False, "mergeable": "MERGEABLE", "updatedAt": "2026-10-04", "statusCheckRollup": [{"conclusion": "SUCCESS"}]},
        {"number": 2, "title": "red", "isDraft": False, "mergeable": "MERGEABLE", "updatedAt": "2026-10-04", "statusCheckRollup": [{"conclusion": "FAILURE"}]},
        {"number": 3, "title": "draft", "isDraft": True, "mergeable": "MERGEABLE", "updatedAt": "2026-10-03", "statusCheckRollup": []},
        {"number": 4, "title": "old conflict", "isDraft": False, "mergeable": "CONFLICTING", "updatedAt": "2026-09-01", "statusCheckRollup": []},
        {"number": 5, "title": "fresh conflict", "isDraft": False, "mergeable": "CONFLICTING", "updatedAt": "2026-10-01", "statusCheckRollup": []},
    ]
    go, rot = pr_loops(prs, today)
    check("green PR waits on go", [i["ref"] for i in go] == ["#1", "#3"])
    check("red PR excluded", all(i["ref"] != "#2" for i in go))
    check("old conflict rots, fresh does not", [i["ref"] for i in rot] == ["#4"])
    check("draft ranks below ready", _top(go, 1)[0][0]["ref"] == "#1")

    rows = [
        {"_schema": "x"},
        {"id": "q", "jtbd": "quick", "status": "open", "cost_prior": "10 min", "added": "2026-10-01"},
        {"id": "slow", "jtbd": "slow", "status": "open", "cost_prior": "45 min", "added": "2026-10-01"},
        {"id": "old", "jtbd": "old", "status": "OPEN", "added": "2026-08-01"},
        {"id": "done", "status": "DONE 2026-08-01"},
        {"id": "held", "status": "HELD trigger-gated", "added": "2026-07-01"},
        {"id": "due", "status": "open", "review_by": "2026-10-01"},
        {"id": "notdue", "status": "open", "review_by": "2026-10-11", "added": "2026-01-01"},
    ]
    quick, brot = backlog_loops(rows, today)
    check("quick only <=15m", [i["ref"] for i in quick] == ["q"])
    rr = {i["ref"] for i in brot}
    check("old rots", "old" in rr)
    check("done and held skipped", not rr & {"done", "held"})
    check("review_by wins both ways", "due" in rr and "notdue" not in rr)

    led = [("here", {"ts": "2026-10-03", "branch": "b"}), ("a", {"ts": "2026-09-01"}),
           ("b", {"ts": "2026-10-02"}), ("c", {"ts": "2026-08-01", "handoff_done": True})]
    mine, crot = checkpoint_loops(led, today, "here")
    check("this worktree surfaced", [i["ref"] for i in mine] == ["here"])
    check("only >7d others rot", [i["ref"] for i in crot] == ["a"])

    cap = captured_today([{"ts": "2026-10-04", "event": "planted", "seed": "s"}, {"ts": "2026-10-03", "event": "planted"}],
                         [{"quote": "that's it"}, {"quote": "x", "promoted": "ADR-1"}], today)
    check("captured today", len(cap) == 2)
    arc = archived_trail_loops([("a", {"ts": "x"}, False), ("b", {"ts": "x"}, True), ("c", {"handoff_done": True}, False), ("d", {}, False)], "~/x")
    check("archive rolls up to one item, claimed excluded", len(arc) == 1 and arc[0]["text"].startswith("1 "))

    now = dt.datetime(2026, 10, 4, 9, tzinfo=dt.timezone.utc)
    up = coming_up([{"taskId": "r1", "fireAt": "2026-10-05T09:00:00Z"}, {"taskId": "r0", "fireAt": "2026-10-01T09:00:00Z"},
                    {"taskId": "cron", "cronExpression": "0 9 * * *", "fireAt": "2026-10-05T09:00:00Z"}], now)
    check("future one-time only", [i["text"] for i in up] == ["r1"])

    d = {"date": str(today), "this_worktree": [], "gaps": [],
         "sections": [["Waiting on your go", go], ["Closable in under 15 min", quick], ["Rotting", rot + brot + crot],
                      ["Captured today, not filed", cap], ["Coming up", up]]}
    page = render_page(d, 1)
    check("cap shows remainder", "+ 1 more" in page)
    check("summary is 3 lines", len(render_summary(d).splitlines()) == 3)
    sp = render_spoken(d)
    check("spoken ~60s (<=170 words)", len(sp.split()) <= 170)
    check("em-dash in source is stripped", "\u2014" not in _item("a \u2014 b", "")["text"])
    check("no em-dashes anywhere", "—" not in page + sp + render_summary(d))

    total = ok + len(fails)
    print(f"open_loops self-test: {ok}/{total}" + ("" if not fails else "  FAIL: " + ", ".join(fails)))
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--json", action="store_true")
    mode.add_argument("--summary", action="store_true", help="3 lines for the SessionStart hook")
    mode.add_argument("--spoken", action="store_true", help="~60 second read-aloud digest")
    mode.add_argument("--self-test", action="store_true")
    ap.add_argument("--cap", type=int, default=5, help="items per section (default 5)")
    ap.add_argument("--scheduled", type=Path, help="JSON snapshot of list_scheduled_tasks")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    now = dt.datetime.now().astimezone()
    d = gather(a.scheduled, now.date(), now)
    if a.json:
        print(json.dumps(d, indent=2))
    elif a.summary:
        print(render_summary(d))
    elif a.spoken:
        print(render_spoken(d))
    else:
        print(render_page(d, a.cap))
    return 0


if __name__ == "__main__":
    sys.exit(main())
