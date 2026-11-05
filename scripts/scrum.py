#!/usr/bin/env python3
"""scrum.py: the scrum master's deterministic half. Stdlib, no model calls, no network except an optional `gh`.

The ritual (`.claude/skills/scrum/SKILL.md`) does the judgment; this script does the counting, so the same state
always prints the same board (idempotent) and nothing is re-derived by a model.

  scrum.py nudge               one line when the groom is overdue, else nothing (the session-start hook calls it)
  scrum.py standup             three lines: shipped in 24h, today's one thing, what is blocked on Zach
  scrum.py board [--no-gh]     the groom board: rituals kept, WIP vs caps, flow, 10 rows to fate, 1 rule to revisit
  scrum.py log --ritual groom|standup|review [--commit a,b] [--done a] [--rule ID --verdict keep|loosen|cut|move]
               [--minutes N] [--note TEXT]
                               append one line to _STATE/scrum/ledger.jsonl (append-only, the habit record)
  scrum.py fate --compost a,b | --done a | --renew a --review-by YYYY-MM-DD   [--note TEXT] [--dry-run]
                               apply fates Zach approved: rewrites only those rows' state/status_note/review_by,
                               under a lock, every other line byte-identical. Re-running the same fate is a no-op.
  scrum.py --self-test

Caps (one place, change here): sprint commits <= 5 rows, RUNNING rows <= 3, open PRs <= 4, groom every 7 days.
"""
import argparse, datetime as dt, fcntl, glob, json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKLOG = os.path.join(ROOT, "_QUEUE", "induced-backlog.jsonl")
LEDGER = os.path.join(ROOT, "_STATE", "scrum", "ledger.jsonl")
CAPS = {"sprint_rows": 5, "running": 3, "open_prs": 4, "groom_days": 7, "fate_batch": 10, "rule_recheck_days": 90}
LIVE = ("OPEN", "READY", "HELD", "HOLDING", "RUNNING", "BLOCKED")
TERMINAL = ("DONE", "COMPOSTED", "SUPERSEDED")


def today():
    return dt.date.fromisoformat(os.environ.get("SCRUM_TODAY") or dt.date.today().isoformat())


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def day(s):
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(s or ""))
    return dt.date.fromisoformat(m.group(0)) if m else None


def sh(cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


# ---------- rules inventory (for the progressive config review) ----------

def rule_inventory():
    """Every always-loaded rule, with a stable id. Path-scoped rules count too: they still steer behaviour."""
    rules = []
    agents = os.path.join(ROOT, "AGENTS.md")
    if os.path.exists(agents):
        for line in open(agents, encoding="utf-8"):
            m = re.match(r"^(\d+a?)\. \*\*(.+?)\*\*", line)
            if m:
                rules.append(("AGENTS#" + m.group(1), m.group(2)[:110], "AGENTS.md gotcha " + m.group(1)))
    claude = os.path.join(ROOT, "CLAUDE.md")
    if os.path.exists(claude):
        sec, n = None, 0
        for line in open(claude, encoding="utf-8"):
            if line.startswith("# "):
                sec, n = line[2:].strip(), 0
            elif sec == "Token-saving rules" and line.startswith("- "):
                n += 1
                txt = re.sub(r"\*\*", "", line[2:]).strip()
                rules.append(("CLAUDE#token-%d" % n, txt[:110], "CLAUDE.md, Token-saving rules"))
    glob_md = os.path.expanduser("~/.claude/CLAUDE.md")
    if os.path.exists(glob_md):
        on, n = False, 0
        for line in open(glob_md, encoding="utf-8"):
            if line.startswith("## "):
                on, n = line.startswith("## Cross-project rules"), 0
            elif on and line.startswith("- "):
                n += 1
                rules.append(("GLOBAL#cross-%d" % n, line[2:].strip()[:110], "~/.claude/CLAUDE.md, Cross-project rules"))
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "rules", "*.md"))):
        name = os.path.basename(p)[:-3]
        rules.append(("RULES:" + name, "path-scoped rule file " + name, ".claude/rules/" + name + ".md"))
    return rules


def next_rule(ledger, t):
    seen = {}
    for e in ledger:
        if e.get("rule") and day(e.get("date")):
            seen[e["rule"]] = max(seen.get(e["rule"], dt.date.min), day(e["date"]))
    for rid, text, where in rule_inventory():
        last = seen.get(rid)
        if not last or (t - last).days >= CAPS["rule_recheck_days"]:
            return rid, text, where, sum(1 for r in rule_inventory() if r[0] not in seen)
    return None


# ---------- board ----------

def flow(rows, t, days=7):
    since = t - dt.timedelta(days=days)
    added = sum(1 for r in rows if (day(r.get("added")) or dt.date.min) >= since)
    closed = 0
    for r in rows:
        if r.get("state") in TERMINAL:
            m = re.search(r"(DONE|COMPOSTED|SUPERSEDED)\D{0,3}(\d{4}-\d{2}-\d{2})", r.get("status_note") or "")
            if m and dt.date.fromisoformat(m.group(2)) >= since:
                closed += 1
    return added, closed


def fate_candidates(rows, t):
    """Rows nobody is moving: live, not RUNNING/READY, and either past review_by or older than 30 days with none.
    Sorted oldest first, ties by id, so the same rows show every time until they get a fate (idempotent)."""
    out = []
    for r in rows:
        if r.get("state") not in ("OPEN", "HELD", "HOLDING", "BLOCKED"):
            continue
        rb, added = day(r.get("review_by")), day(r.get("added"))
        if rb and rb <= t:
            why = "past review_by %s" % rb
        elif not rb and (not added or (t - added).days > 30):
            why = "no review_by, added %s" % (added or "undated")
        else:
            continue
        default = "renew" if r.get("state") == "HELD" and rb else "compost"
        out.append((added or dt.date.min, r["id"], r.get("state"), why, default, (r.get("jtbd") or "")[:90]))
    out.sort()
    return out


def last_ritual(ledger, kind):
    ds = [day(e.get("date")) for e in ledger if e.get("ritual") == kind and day(e.get("date"))]
    return max(ds) if ds else None


def current_sprint(ledger):
    grooms = [e for e in ledger if e.get("ritual") == "groom" and e.get("commit")]
    return grooms[-1] if grooms else None


def cmd_board(a):
    t, rows, ledger = today(), read_jsonl(BACKLOG), read_jsonl(LEDGER)
    live = [r for r in rows if r.get("state") in LIVE]
    by_id = {r["id"]: r for r in rows if "id" in r}
    print("# Scrum board, %s" % t)
    lg = last_ritual(ledger, "groom")
    gap = (t - lg).days if lg else None
    weeks = len({day(e["date"]).isocalendar()[:2] for e in ledger if e.get("ritual") == "groom" and day(e.get("date"))})
    print("\n## 1. Rituals kept (the habit)")
    print("- last groom: %s%s; weeks with a groom: %d" % (
        lg or "never", "" if gap is None else " (%d days ago%s)" % (gap, ", OVERDUE" if gap > CAPS["groom_days"] else ""), weeks))
    sd = sum(1 for e in ledger if e.get("ritual") == "standup" and day(e.get("date")) and (t - day(e["date"])).days < 7)
    print("- standups in the last 7 days: %d of 5" % sd)

    print("\n## 2. Last sprint: said vs did")
    sp = current_sprint(ledger)
    if sp:
        done = [i for i in sp["commit"] if by_id.get(i, {}).get("state") in TERMINAL]
        print("- committed %s: %d rows, %d closed (%d%%)" % (sp["date"], len(sp["commit"]), len(done),
                                                          100 * len(done) // max(1, len(sp["commit"]))))
        for i in sp["commit"]:
            print("  - %-9s %s" % (by_id.get(i, {}).get("state", "MISSING"), i))
    else:
        print("- no sprint committed yet")

    print("\n## 3. WIP vs caps")
    running = [r["id"] for r in live if r.get("state") == "RUNNING"]
    print("- RUNNING rows: %d (cap %d)%s" % (len(running), CAPS["running"], "  OVER" if len(running) > CAPS["running"] else ""))
    if not a.no_gh:
        prs = sh(["gh", "pr", "list", "--state", "open", "--json", "number", "--jq", "length"])
        if prs.isdigit():
            n = int(prs)
            print("- open PRs: %d (cap %d)%s" % (n, CAPS["open_prs"], "  OVER" if n > CAPS["open_prs"] else ""))
        else:
            print("- open PRs: UNKNOWN (gh unavailable)")
    print("- live sessions: ask the app (list_sessions linked), cap 4")

    print("\n## 4. Flow, last 7 days")
    added, closed = flow(rows, t)
    print("- live rows: %d; added %d, closed %d, net %+d" % (len(live), added, closed, added - closed))
    if added > closed:
        print("- the backlog grew; this groom should close more than it opens")

    print("\n## 5. Fate these (oldest first, %d of %d shown; default in brackets)" % (
        min(CAPS["fate_batch"], len(fate_candidates(rows, t))), len(fate_candidates(rows, t))))
    for _, rid, st, why, default, jt in fate_candidates(rows, t)[:CAPS["fate_batch"]]:
        print("- [%s] %s (%s, %s): %s" % (default, rid, st, why, jt))

    print("\n## 6. One rule to revisit (trust the model more?)")
    nr = next_rule(ledger, t)
    if nr:
        rid, text, where, unseen = nr
        print("- %s, %s: %s" % (rid, where, text))
        print("- ask: what bad outcome does it prevent, did that happen in 30 days, would a smarter model avoid it unprompted?")
        print("- verdicts: keep | loosen | cut | move (to a path-scoped rule); %d rules never reviewed" % unseen)
    else:
        print("- every rule reviewed in the last %d days" % CAPS["rule_recheck_days"])
    print("\n## 7. Commit next sprint: at most %d rows, one sprint goal sentence" % CAPS["sprint_rows"])
    ready = [r["id"] for r in live if r.get("state") == "READY"]
    print("- READY now (%d): %s" % (len(ready), ", ".join(ready[:8]) + (" ..." if len(ready) > 8 else "")))
    print("- the graph's order: python3 scripts/backlog_graph.py --top 5")


def cmd_standup(a):
    t, rows, ledger = today(), read_jsonl(BACKLOG), read_jsonl(LEDGER)
    by_id = {r["id"]: r for r in rows if "id" in r}
    merges = sh(["git", "log", "origin/main", "--merges", "--since=24 hours ago", "--format=%s"]).splitlines()
    print("shipped (24h): %d merges to main%s" % (len(merges), (": " + "; ".join(m[:60] for m in merges[:3])) if merges else ""))
    sp = current_sprint(ledger)
    todo = [i for i in (sp or {}).get("commit", []) if by_id.get(i, {}).get("state") not in TERMINAL]
    goal = (sp or {}).get("note") or "no sprint goal yet"
    print("today's one thing: %s  (sprint goal: %s)" % (todo[0] if todo else "groom first, nothing committed", goal))
    loops = sh(["python3", "scripts/open_loops.py", "--summary"]).splitlines()
    print("blocked on you: %s" % (loops[0].replace("open-loops: ", "") if loops else "UNKNOWN (open_loops.py failed)"))
    lg = last_ritual(ledger, "groom")
    if not lg or (t - lg).days > CAPS["groom_days"]:
        print("groom overdue: last %s. Run /scrum groom (25 minutes)." % (lg or "never"))


def cmd_nudge(a):
    lg = last_ritual(read_jsonl(LEDGER), "groom")
    if not lg or (today() - lg).days > CAPS["groom_days"]:
        print("scrum: groom overdue (last %s). /scrum groom, 25 minutes; /scrum for the 2-minute standup" % (lg or "never"))


# ---------- writes ----------

def cmd_log(a):
    if a.commit and len(a.commit) > CAPS["sprint_rows"]:
        sys.exit("refused: %d rows committed, cap is %d. Cut, don't add." % (len(a.commit), CAPS["sprint_rows"]))
    ids = {r.get("id") for r in read_jsonl(BACKLOG)}
    bad = [i for i in (a.commit or []) + (a.done or []) if i not in ids]
    if bad:
        sys.exit("refused: unknown row ids %s" % bad)
    if a.rule and not a.verdict:
        sys.exit("refused: --rule needs --verdict")
    e = {"date": today().isoformat(), "ritual": a.ritual}
    for k in ("commit", "done", "rule", "verdict", "minutes", "note"):
        v = getattr(a, k)
        if v:
            e[k] = v
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("logged:", json.dumps(e))


def apply_fates(path, fates, note, t, dry=False):
    """fates: {id: (state, review_by or None)}. Returns list of (id, action). Only named lines change."""
    with open(path, "r+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        lines = f.readlines()
        changed, seen = [], set()
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            rid = r.get("id")
            if rid not in fates:
                continue
            seen.add(rid)
            state, rb = fates[rid]
            if r.get("state") == state and (rb is None or r.get("review_by") == rb):
                changed.append((rid, "no-op (already %s)" % state))
                continue
            if r.get("state") in TERMINAL:
                changed.append((rid, "refused: already terminal %s" % r["state"]))
                continue
            prior = r.get("state")
            r["state"] = state
            if rb:
                r["review_by"] = rb
            stamp = "%s %s (scrum groom, from %s)%s" % (state if state != "OPEN" else "RENEWED", t, prior,
                                                        ": " + note if note else "")
            r["status_note"] = (stamp + ". " + (r.get("status_note") or "")).strip()
            r.pop("claimed_by", None) if state in TERMINAL else None
            lines[i] = json.dumps(r, ensure_ascii=False) + "\n"
            changed.append((rid, "%s -> %s" % (prior, state)))
        for rid in set(fates) - seen:
            changed.append((rid, "refused: unknown id"))
        if not dry and any("->" in c[1] for c in changed):
            f.seek(0)
            f.writelines(lines)
            f.truncate()
    return changed


def cmd_fate(a):
    fates = {}
    for i in a.compost or []:
        fates[i] = ("COMPOSTED", None)
    for i in a.done or []:
        fates[i] = ("DONE", None)
    if a.renew:
        if not a.review_by:
            sys.exit("refused: --renew needs --review-by")
        for i in a.renew:
            fates[i] = (None, a.review_by)
    rows = {r.get("id"): r for r in read_jsonl(BACKLOG)}
    fates = {k: ((v[0] or rows.get(k, {}).get("state", "OPEN")), v[1]) for k, v in fates.items()}
    for rid, act in apply_fates(BACKLOG, fates, a.note, today(), a.dry_run):
        print("%-40s %s" % (rid, act))
    if not a.dry_run:
        print("next: python3 scripts/backlog_status_check.py --check")


# ---------- self-test ----------

def self_test():
    global BACKLOG, LEDGER
    d = tempfile.mkdtemp()
    BACKLOG, LEDGER = os.path.join(d, "b.jsonl"), os.path.join(d, "l.jsonl")
    os.environ["SCRUM_TODAY"] = "2026-11-05"
    rows = [
        {"id": "old", "state": "OPEN", "jtbd": "x", "added": "2026-08-01"},
        {"id": "fresh", "state": "OPEN", "jtbd": "y", "added": "2026-11-01"},
        {"id": "held", "state": "HELD", "jtbd": "z", "added": "2026-10-01", "review_by": "2026-11-01"},
        {"id": "gone", "state": "DONE", "jtbd": "w", "status_note": "DONE 2026-11-04: merged"},
    ]
    with open(BACKLOG, "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")
    before = open(BACKLOG).read().splitlines()
    c = fate_candidates(rows, today())
    assert [x[1] for x in c] == ["old", "held"], c
    assert [x[4] for x in c] == ["compost", "renew"], c
    assert flow(rows, today()) == (1, 1)
    r1 = apply_fates(BACKLOG, {"old": ("COMPOSTED", None), "gone": ("COMPOSTED", None)}, "test", today())
    after = open(BACKLOG).read().splitlines()
    assert after[1:] == before[1:], "untouched lines must be byte-identical"
    assert json.loads(after[0])["state"] == "COMPOSTED"
    assert dict(r1)["gone"].startswith("refused"), r1
    r2 = apply_fates(BACKLOG, {"old": ("COMPOSTED", None)}, "test", today())
    assert r2[0][1].startswith("no-op") and open(BACKLOG).read().splitlines() == after, "re-run must be a no-op"
    ns = argparse.Namespace(ritual="groom", commit=["fresh"], done=None, rule="AGENTS#1", verdict="keep",
                            minutes=20, note="goal")
    cmd_log(ns)
    led = read_jsonl(LEDGER)
    assert led[0]["commit"] == ["fresh"] and current_sprint(led)["note"] == "goal"
    try:
        cmd_log(argparse.Namespace(ritual="groom", commit=list("abcdef"), done=None, rule=None, verdict=None,
                                   minutes=None, note=None))
        raise AssertionError("cap not enforced")
    except SystemExit as e:
        assert "cap" in str(e)
    assert rule_inventory(), "rule inventory empty"
    print("self-test OK")


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("standup")
    sub.add_parser("nudge")
    b = sub.add_parser("board")
    b.add_argument("--no-gh", action="store_true")
    csv = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    lg = sub.add_parser("log")
    lg.add_argument("--ritual", required=True, choices=["groom", "standup", "review"])
    lg.add_argument("--commit", type=csv)
    lg.add_argument("--done", type=csv)
    lg.add_argument("--rule")
    lg.add_argument("--verdict", choices=["keep", "loosen", "cut", "move"])
    lg.add_argument("--minutes", type=int)
    lg.add_argument("--note")
    ft = sub.add_parser("fate")
    ft.add_argument("--compost", type=csv)
    ft.add_argument("--done", type=csv)
    ft.add_argument("--renew", type=csv)
    ft.add_argument("--review-by")
    ft.add_argument("--note")
    ft.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    {"nudge": cmd_nudge, "standup": cmd_standup, "board": cmd_board, "log": cmd_log, "fate": cmd_fate}[a.cmd](a)


if __name__ == "__main__":
    main()
