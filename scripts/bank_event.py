#!/usr/bin/env python3
"""bank_event.py - back- and forward-propagation when a lesson is banked.

Spec: runtime/specs/bank-event-propagation-v0.md. Stdlib only, no LLM, no network.

A bank event records that a belief changed (anterior -> posterior), the matchers that find
what was built on the old belief, and a guard that can stop the next occurrence (or the
reason there is none). `record` scans, previews every dependent, and writes only on a yes.
`scan` re-checks: a dependent whose matched text is gone resolves to moot. Nothing is ever
rewritten in the scanned files; the break is shown, not patched.

Usage:
  bank_event.py record --kind failure --axis falsified --source memory:SLUG \\
      --anterior "claim before" --anterior-basis "why we thought so" \\
      --posterior "claim now" --posterior-basis "evidence" \\
      --defeats regex:"gate[^\\n]{0,40}manual" --guard risk-rule:post-create [--yes]
  bank_event.py scan
  bank_event.py list [--unbanked | --open] [--json]
  bank_event.py --self-test

State (append-only, local, gitignored): $BANK_STATE_DIR (default the main checkout's _STATE)
holds bank-events.jsonl and bank-dependents.jsonl. Scanned: git-tracked docs and code, plus the
memory directory. NOT scanned (recorded on every event): chat, the artifact database, untracked files.
"""
import argparse, datetime as dt, fnmatch, hashlib, io, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

DOC_EXT = {".md", ".json", ".jsonl", ".html", ".txt", ".yaml", ".yml"}
CODE_EXT = {".py", ".sh", ".ts", ".tsx", ".js", ".mjs", ".mts"}
EXCLUDE = ("node_modules/", "_ARCHIVE/", "archive/", ".git/")
MAX_BYTES = 1_000_000
DEFAULT_CAP = 25
REVIEW_DAYS = 14
KINDS = {"failure", "pattern"}
AXES = {"falsified", "moot", "molted", "new-pattern"}
MATCH_TYPES = {"regex", "path", "symbol", "adr"}
GUARDS = {"risk-rule", "pre-commit", "defeater-trigger", "session-start"}
BLIND_SPOTS = ["chat", "artifact database", "untracked files"]
REPAIR = {"falsified": "correct and re-warrant", "moot": "vacate and mark with provenance",
          "molted": "keep dated, point to the successor", "new-pattern": "no anterior to repair"}


class Ctx:
    def __init__(self, root, state_dir, memory_dir=None):
        self.root = Path(root)
        self.events = Path(state_dir) / "bank-events.jsonl"
        self.deps = Path(state_dir) / "bank-dependents.jsonl"
        self.memory_dir = Path(memory_dir) if memory_dir else None


def default_ctx():
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
    state = os.environ.get("BANK_STATE_DIR", "/Users/zharris/arcs-v9/_STATE")
    mem = os.environ.get("BANK_MEMORY_DIR", "/Users/zharris/.claude/projects/-Users-zharris-arcs-v9/memory")
    return Ctx(root, state, mem if Path(mem).is_dir() else None)


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def sha(*parts, n=10):
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:n]


def load(path):
    rows = {}
    if path.exists():
        for ln in path.read_text().splitlines():
            if ln.strip():
                e = json.loads(ln)
                rows.setdefault(e["id"], {}).update(e)
    return rows


def append(path, rows):
    if rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")


def event_id(kind, axis, ant, post, defeats):
    return "be-" + sha(json.dumps([kind, axis, ant, post, defeats], sort_keys=True))


def files_in_scope(ctx, scopes):
    out = []
    if scopes & {"docs", "code"}:
        ls = subprocess.run(["git", "ls-files", "-z"], cwd=ctx.root, capture_output=True, text=True).stdout.split("\0")
        for f in ls:
            if not f or f.startswith(EXCLUDE):
                continue
            ext = Path(f).suffix.lower()
            if (ext in DOC_EXT and "docs" in scopes) or (ext in CODE_EXT and "code" in scopes):
                out.append((f, ctx.root / f))
    if "memory" in scopes and ctx.memory_dir:
        for p in sorted(ctx.memory_dir.glob("*.md")):
            out.append((f"memory:{p.name}", p))
    return out


def compile_matcher(m):
    t, p = m["type"], m["pattern"]
    if t == "regex":
        return re.compile(p)
    if t == "symbol":
        return re.compile(r"\b" + re.escape(p) + r"\b")
    if t == "adr":
        d = re.sub(r"\D", "", p)
        return re.compile(r"ADR-0*" + d + r"\b")
    return None  # path matchers glob file names


def scan_event(ctx, ev, exclude_refs=()):
    """Return {(file, matched_text): hit} for every matcher. Citation of the event id is a mention."""
    scopes = set(ev["scopes_scanned"])
    files = files_in_scope(ctx, scopes)
    hits = {}
    for m in ev["defeats"]:
        rx = compile_matcher(m)
        for name, path in files:
            if name in exclude_refs or any(name.endswith(r) for r in exclude_refs if r):
                continue
            if any(fnmatch.fnmatch(name, g) for g in ev.get("exclude", [])):
                continue
            if m["type"] == "path":
                if fnmatch.fnmatch(name, m["pattern"]):
                    hits.setdefault((name, name), {"file": name, "match": name, "line": 0, "snippet": "(file matches path)"})
                continue
            try:
                if path.stat().st_size > MAX_BYTES:
                    continue
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if ev["id"] in text:
                continue
            for mt in rx.finditer(text):
                key = (name, mt.group(0)[:120])
                if key not in hits:
                    ln = text.count("\n", 0, mt.start()) + 1
                    line = text.splitlines()[ln - 1] if text else ""
                    hits[key] = {"file": name, "match": mt.group(0)[:120], "line": ln, "snippet": line.strip()[:140]}
    return hits


def dep_row(ev, h):
    return {"id": "bd-" + sha(ev["id"], h["file"], h["match"], n=12), "event": ev["id"], "file": h["file"],
            "match": h["match"], "line": h["line"], "snippet": h["snippet"], "status": "unverified",
            "defeated_by": ev["id"], "repair": REPAIR[ev["axis"]], "first_seen": now(),
            "review_by": (dt.date.today() + dt.timedelta(days=REVIEW_DAYS)).isoformat(), "at": now()}


def summary_row(ev, hits):
    files = {h["file"] for h in hits.values()}
    return {"id": "bd-" + sha(ev["id"], "summary", n=12), "event": ev["id"], "file": f"({len(files)} files)",
            "match": f"{len(hits)} hits", "line": 0, "snippet": "broad matcher: one summary row, not one row per hit",
            "status": "unverified", "defeated_by": ev["id"], "repair": REPAIR[ev["axis"]], "first_seen": now(),
            "review_by": (dt.date.today() + dt.timedelta(days=REVIEW_DAYS)).isoformat(), "at": now(), "summary": True}


def build_event(a):
    defeats = []
    for d in a["defeats"]:
        t, _, p = d.partition(":")
        if t not in MATCH_TYPES or not p:
            raise SystemExit(f"bad --defeats {d!r}: use TYPE:PATTERN with TYPE in {sorted(MATCH_TYPES)}")
        defeats.append({"type": t, "pattern": p})
    if not defeats:
        raise SystemExit("at least one --defeats matcher is required")
    guard = None
    if a.get("guard"):
        gt, _, gr = a["guard"].partition(":")
        if gt not in GUARDS or not gr:
            raise SystemExit(f"bad --guard {a['guard']!r}: use TYPE:REF with TYPE in {sorted(GUARDS)}")
        guard = {"type": gt, "ref": gr}
    if guard and a.get("no_guard_reason"):
        raise SystemExit("--guard and --no-guard-reason are mutually exclusive")
    st, _, sr = (a.get("source") or "").partition(":")
    ant = {"claim": a["anterior"], "basis": a.get("anterior_basis") or ""}
    post = {"claim": a["posterior"], "basis": a.get("posterior_basis") or ""}
    ev = {"id": event_id(a["kind"], a["axis"], ant, post, defeats), "kind": a["kind"], "axis": a["axis"], "at": now(),
          "source": {"type": st, "ref": sr}, "anterior": ant, "posterior": post, "defeats": defeats,
          "scopes_scanned": sorted(a.get("scopes") or ["docs", "code", "memory"]), "blind_spots": BLIND_SPOTS,
          "guard": guard, "no_guard_reason": a.get("no_guard_reason"), "banking_level": a.get("level"),
          "tuition": None, "broad": a.get("broad"), "exclude": sorted(a.get("exclude") or [])}
    return ev


def record(ctx, a, out=sys.stdout, tty=None):
    ev = build_event(a)
    cap = a.get("cap") or DEFAULT_CAP
    refs = {ev["source"]["ref"]} if ev["source"]["ref"] else set()
    hits = scan_event(ctx, ev, refs)
    print(f"event {ev['id']}  kind={ev['kind']} axis={ev['axis']}  matchers={len(ev['defeats'])}  hits={len(hits)}  cap={cap}", file=out)
    print(f"scanned: {', '.join(ev['scopes_scanned'])}. not scanned: {', '.join(BLIND_SPOTS)}.", file=out)
    if len(hits) > cap and not ev["broad"]:
        print(f"refused: {len(hits)} hits is over the cap of {cap}. Narrow the matcher, or pass --broad REASON.", file=out)
        return 2
    for h in sorted(hits.values(), key=lambda x: (x["file"], x["line"])):
        print(f"  {h['file']}:{h['line']}  {h['snippet']}", file=out)
    if not ev["guard"] and not ev["no_guard_reason"]:
        print("note: no guard and no reason, so this event is UNBANKED (stays at level 4 or below).", file=out)
    if not a.get("yes"):
        if tty if tty is not None else sys.stdin.isatty():
            if input("Write this event and its dependents? [y/N] ").strip().lower() != "y":
                print("not written.", file=out)
                return 3
        else:
            print("preview only. Pass --yes to write.", file=out)
            return 3
    events, deps = load(ctx.events), load(ctx.deps)
    new_ev = [] if ev["id"] in events else [ev]
    rows = [summary_row(ev, hits)] if (len(hits) > cap and ev["broad"]) else [dep_row(ev, h) for h in hits.values()]
    new_deps = [r for r in rows if r["id"] not in deps]
    append(ctx.events, new_ev)
    append(ctx.deps, new_deps)
    print(f"wrote {len(new_ev)} event, {len(new_deps)} new dependents.", file=out)
    return 0


def rescan(ctx, out=sys.stdout):
    events, deps = load(ctx.events), load(ctx.deps)
    cap = DEFAULT_CAP
    new, moot, reopened = [], [], []
    for ev in events.values():
        refs = {ev["source"]["ref"]} if ev["source"]["ref"] else set()
        hits = scan_event(ctx, ev, refs)
        broad = bool(ev.get("broad")) and len(hits) > cap
        current = [summary_row(ev, hits)] if (broad and hits) else ([] if broad else [dep_row(ev, h) for h in hits.values()])
        cur_ids = {r["id"] for r in current}
        for r in current:
            if r["id"] not in deps:
                new.append(r)
            elif deps[r["id"]]["status"] == "moot":
                reopened.append({"id": r["id"], "status": "unverified", "at": now(), "why": "matched text reappeared"})
        for d in deps.values():
            if d["event"] == ev["id"] and d["status"] != "moot" and d["id"] not in cur_ids:
                moot.append({"id": d["id"], "status": "moot", "at": now(), "why": "matched text or file is gone"})
    append(ctx.deps, new + moot + reopened)
    print(f"scan: {len(events)} events | new {len(new)} | moot {len(moot)} | reopened {len(reopened)}", file=out)
    return 0


def list_cmd(ctx, unbanked=False, open_only=False, as_json=False, out=sys.stdout):
    events, deps = load(ctx.events), load(ctx.deps)
    today = dt.date.today()
    if open_only:
        rows = [d for d in deps.values() if d["status"] != "moot"]
        if as_json:
            print(json.dumps(rows, indent=1), file=out)
        for d in sorted(rows, key=lambda x: x.get("review_by", "")):
            print(f"[{d['status']}] {d['file']}:{d['line']} defeated_by={d['defeated_by']} review_by={d.get('review_by')}  {d['snippet']}", file=out)
        if not rows:
            print("(no open dependents)", file=out)
        return 0
    rows = [e for e in events.values() if not unbanked or (not e["guard"] and not e["no_guard_reason"])]
    if as_json:
        print(json.dumps(rows, indent=1), file=out)
        return 0
    for e in sorted(rows, key=lambda x: x["at"]):
        age = (today - dt.date.fromisoformat(e["at"][:10])).days
        state = "guarded" if e["guard"] else ("reasoned" if e["no_guard_reason"] else "UNBANKED")
        n = sum(1 for d in deps.values() if d["event"] == e["id"] and d["status"] != "moot")
        print(f"{e['id']}  {state:8}  age {age}d  open dependents {n}  {e['posterior']['claim'][:70]}", file=out)
    if not rows:
        print("(none)", file=out)
    return 0


def self_test():
    t0 = time.time()
    real = Path(os.environ.get("BANK_STATE_DIR", "/Users/zharris/arcs-v9/_STATE")) / "bank-events.jsonl"
    before = real.stat().st_mtime if real.exists() else None
    ok = []

    def check(name, cond):
        ok.append(cond)
        print(("PASS " if cond else "FAIL ") + name)

    with tempfile.TemporaryDirectory() as td:
        repo, state = Path(td) / "repo", Path(td) / "state"
        repo.mkdir()
        sh = lambda *c: subprocess.run(c, cwd=repo, capture_output=True, text=True)
        sh("git", "init", "-q")
        sh("git", "config", "user.email", "t@t")
        sh("git", "config", "user.name", "t")
        (repo / "stale.md").write_text("# Notes\nThe integrity gate is manual and runs only by hand.\n")
        (repo / "fresh.md").write_text("Nothing relevant here.\n")
        for i in range(8):
            (repo / f"common{i}.md").write_text(f"common word {i}\n")
        sh("git", "add", "-A")
        sh("git", "commit", "-qm", "init")
        ctx = Ctx(repo, state)
        base = {"kind": "failure", "axis": "falsified", "source": "memory:test", "anterior": "gate is manual",
                "anterior_basis": "read a stale doc", "posterior": "gate runs at pre-commit",
                "posterior_basis": "ran it", "defeats": [r"regex:gate is manual"], "yes": True}
        sink = io.StringIO()
        check("record flags the planted stale claim", record(ctx, dict(base), sink) == 0 and len(load(ctx.deps)) == 1)
        d = next(iter(load(ctx.deps).values()))
        check("dependent is unverified, points at stale.md", d["status"] == "unverified" and d["file"] == "stale.md")
        before_n = len(load(ctx.deps))
        record(ctx, dict(base), sink)
        check("second record writes 0 new rows (idempotent)", len(load(ctx.deps)) == before_n and len(load(ctx.events)) == 1)
        broad = dict(base, defeats=[r"regex:common word"], posterior="other", cap=5, yes=True)
        check("matcher over the cap is refused without --broad", record(ctx, dict(broad), sink) == 2)
        check("...and allowed with --broad as ONE summary row", record(ctx, dict(broad, broad="test"), sink) == 0
              and sum(1 for x in load(ctx.deps).values() if x.get("summary")) == 1)
        eid = event_id("failure", "falsified", {"claim": "gate is manual", "basis": "read a stale doc"},
                       {"claim": "gate runs at pre-commit", "basis": "ran it"}, [{"type": "regex", "pattern": "gate is manual"}])
        (repo / "cite.md").write_text(f"This note about {eid} says the gate is manual was wrong.\n")
        sh("git", "add", "-A")
        sh("git", "commit", "-qm", "cite")
        rescan(ctx, sink)
        (repo / "mention.md").write_text("A table quoting the matcher: gate is manual\n")
        sh("git", "add", "-A")
        sh("git", "commit", "-qm", "mention")
        rescan(ctx, sink)
        check("a mention-only file IS flagged until it is excluded", any(x["file"] == "mention.md" for x in load(ctx.deps).values()))
        ex = dict(base, posterior="excluded one", exclude=["mention.md"], yes=True)
        record(ctx, ex, sink)
        check("--exclude keeps a mention-only file out of a new event", not any(x["file"] == "mention.md" and x["event"] == event_id("failure", "falsified", {"claim": "gate is manual", "basis": "read a stale doc"}, {"claim": "excluded one", "basis": "ran it"}, [{"type": "regex", "pattern": "gate is manual"}]) for x in load(ctx.deps).values()))
        check("a file that cites the event id is not flagged for THAT event", not any(x["file"] == "cite.md" and x["event"] == eid for x in load(ctx.deps).values()))
        (repo / "stale.md").write_text("# Notes\nThe integrity gate runs at pre-commit.\n")
        sh("git", "add", "-A")
        sh("git", "commit", "-qm", "fix")
        rescan(ctx, sink)
        check("removing the stale text resolves the dependent to moot", load(ctx.deps)[d["id"]]["status"] == "moot")
        ev2 = io.StringIO()
        list_cmd(ctx, unbanked=True, out=ev2)
        check("an event with no guard and no reason is listed as UNBANKED", "UNBANKED" in ev2.getvalue())
        guarded = dict(base, posterior="guarded one", guard="risk-rule:post-create", yes=True)
        record(ctx, guarded, sink)
        ev3 = io.StringIO()
        list_cmd(ctx, unbanked=True, out=ev3)
        check("a guarded event is not listed as unbanked", "guarded one" not in ev3.getvalue())
        try:
            build_event(dict(base, guard="risk-rule:x", no_guard_reason="y"))
            check("guard and no_guard_reason together are rejected", False)
        except SystemExit:
            check("guard and no_guard_reason together are rejected", True)
    after = real.stat().st_mtime if real.exists() else None
    check("the real state file was never touched", before == after)
    secs = time.time() - t0
    check(f"finished in under 5 seconds ({secs:.2f}s)", secs < 5)
    print(f"self-test: {sum(ok)}/{len(ok)}")
    return 0 if all(ok) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("record")
    r.add_argument("--kind", choices=sorted(KINDS), required=True)
    r.add_argument("--axis", choices=sorted(AXES), required=True)
    r.add_argument("--source", required=True, help="TYPE:REF, e.g. memory:slug or witness:2026-10-06")
    r.add_argument("--anterior", required=True)
    r.add_argument("--anterior-basis", default="")
    r.add_argument("--posterior", required=True)
    r.add_argument("--posterior-basis", default="")
    r.add_argument("--defeats", action="append", default=[], help="TYPE:PATTERN, repeatable")
    r.add_argument("--scope", action="append", choices=["docs", "code", "memory"], dest="scopes")
    r.add_argument("--guard")
    r.add_argument("--no-guard-reason")
    r.add_argument("--level", type=int, choices=range(1, 6))
    r.add_argument("--exclude", action="append", metavar="GLOB", help="skip files that only MENTION the claim, repeatable")
    r.add_argument("--broad", metavar="REASON")
    r.add_argument("--cap", type=int)
    r.add_argument("--yes", action="store_true")
    sub.add_parser("scan")
    l = sub.add_parser("list")
    l.add_argument("--unbanked", action="store_true")
    l.add_argument("--open", action="store_true", dest="open_only")
    l.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.cmd:
        ap.print_help()
        return 2
    ctx = default_ctx()
    if a.cmd == "record":
        return record(ctx, vars(a))
    if a.cmd == "scan":
        return rescan(ctx)
    return list_cmd(ctx, a.unbanked, a.open_only, a.json)


if __name__ == "__main__":
    sys.exit(main())
