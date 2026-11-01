#!/usr/bin/env python3
"""
belief_blame.py: blame the assumption, not the author (read-only, stdlib only).

git blame says who last touched a line. Belief blame says which belief the line encodes, the
commit that first stated it, the evidence that later shifted it, and whether every line that
states it has caught up. Ruled 2026-11-01 (_PROPOSALS/2026-11-01-belief-blame.json, D1-D5).

The join key is the optional `anchors` field on _STATE/assumptions.jsonl and
_STATE/falsification-ledger.jsonl rows: [{path, phrase, role?}]. role `states` (default) means the
line asserts the belief; `lesson` means the line records what a failure of it taught. Both ledgers
are append-only, so an old belief is anchored through a NEW asm row that points back at it.

Verdicts (D2: truth and liveness are separate axes; `exit` on the row says which kind of end):
  CURRENT                no evidence shifted it (open or held)
  SHIFTED-PROPAGATED     falsified, and no `states` anchor still carries the old phrase
  SHIFTED-STALE-SIBLING  falsified, but a `states` anchor still carries the old phrase (K1)
  MOOT                   the question retired (exit moot); vacate and mark, do not correct
  UNREGISTERED           line mode only: no row is anchored to this line
  RELAPSED               falsified, and a `lesson` anchor dated after the falsification does not
                         cite the F-row in its paragraph (K2). Warn only until 2026-12-01 (D4).
  Precedence when several apply: MOOT, STALE-SIBLING, RELAPSED, PROPAGATED.

Usage:
  python3 scripts/belief_blame.py line PATH:N        # the beliefs on one line, entry vs last touch (K3)
  python3 scripts/belief_blame.py belief ID          # one row (asm-NNN or F-NN) and its verdict
  python3 scripts/belief_blame.py edge ROW DEP       # a backlog depends_on edge: when it entered, is it live
  python3 scripts/belief_blame.py scan               # every anchored row; exit 0 (warn only)
  python3 scripts/belief_blame.py check              # anchors schema on both ledgers; exit 1 on error
  python3 scripts/belief_blame.py --self-test        # K1, K2, K3 known-bad and known-good in a temp git repo
  add --json to line, belief, edge or scan for machine output.

Writes nothing, anywhere. Unknown flags and extra arguments exit 2 (argparse).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASM = "_STATE/assumptions.jsonl"
FLEDGER = "_STATE/falsification-ledger.jsonl"
BACKLOG = "_QUEUE/induced-backlog.jsonl"
RELAPSE_GATE_DECISION = "2026-12-01"   # D4: warn only until then
F_ID = re.compile(r"^F\d+$")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assumptions import validate_anchors  # noqa: E402  (one anchors contract for both ledgers)


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def read_jsonl(root: Path, rel: str) -> list[dict]:
    p = root / rel
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_rows(root: Path) -> list[dict]:
    """Both ledgers in one shape: id, ledger, claim, truth, decided_on, decided_ref, exit, anchors, supersedes."""
    out = []
    for r in read_jsonl(root, ASM):
        out.append({"id": r["id"], "ledger": ASM, "claim": r.get("assumption", ""),
                    "truth": r.get("status", "open"), "decided_on": r.get("decided_on"),
                    "decided_ref": r.get("decided_ref"), "exit": r.get("exit"),
                    "anchors": r.get("anchors") or [], "supersedes": r.get("supersedes")})
    for r in read_jsonl(root, FLEDGER):
        v = str(r.get("verdict", "")).upper()
        out.append({"id": r["id"], "ledger": FLEDGER, "claim": r.get("claim", ""),
                    "truth": "falsified" if v == "FALSIFIED" else ("held" if v == "HELD" else v.lower()),
                    "decided_on": r.get("ts"), "decided_ref": r["id"], "exit": r.get("exit"),
                    "anchors": r.get("anchors") or [], "supersedes": None})
    return out


def lines_of(root: Path, rel: str) -> list[str] | None:
    p = root / rel
    try:
        return p.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None


def pickaxe(root: Path, rel: str, phrase: str) -> list[tuple[str, str]]:
    """Commits (oldest first) where the phrase's count changed in that path: (short sha, date)."""
    out = git(root, "log", "--reverse", "--format=%h %ad", "--date=short", "-S", phrase, "--", rel)
    return [tuple(l.split(" ", 1)) for l in out.splitlines() if l.strip()]


def paragraph(lines: list[str], i: int, cap: int = 12) -> str:
    """The anchor line plus its neighbours up to a blank (or bare comment) line, capped."""
    def blank(s: str) -> bool:
        return s.strip() in ("", "#", "//", "*", "--")
    lo = i
    while lo > 0 and i - lo < cap and not blank(lines[lo - 1]):
        lo -= 1
    hi = i
    while hi + 1 < len(lines) and hi - i < cap and not blank(lines[hi + 1]):
        hi += 1
    return "\n".join(lines[lo:hi + 1])


def f_ref(row: dict) -> str | None:
    ref = str(row.get("decided_ref") or "")
    return ref if F_ID.match(ref) else None


def assess(root: Path, row: dict, rows: list[dict]) -> dict:
    anchors = []
    for a in row["anchors"]:
        rel, phrase, role = a["path"], a["phrase"], a.get("role", "states")
        ls = lines_of(root, rel)
        hits = [n + 1 for n, l in enumerate(ls or []) if phrase in l]
        history = pickaxe(root, rel, phrase)
        anchors.append({"path": rel, "phrase": phrase, "role": role, "lines": hits,
                        "path_exists": ls is not None,
                        "entered_in": history[0][0] if history else None,
                        "entered_on": history[0][1] if history else None,
                        "removed_in": history[-1][0] if history and not hits and len(history) > 1 else None})
    truth = row["truth"]
    liveness = "moot" if row.get("exit") == "moot" else "live"
    states = [a for a in anchors if a["role"] == "states"]
    stale = [f"{a['path']}:{n}" for a in states for n in a["lines"]] if truth == "falsified" else []
    notes = []
    if truth in ("open", "held"):
        notes += [f"anchor lost: phrase no longer in {a['path']}" for a in states if not a["lines"]]
    relapse = []
    fid = f_ref(row)
    if truth == "falsified" and fid:
        for a in anchors:
            if a["role"] != "lesson" or not a["lines"]:
                continue
            if a["entered_on"] and row["decided_on"] and a["entered_on"] <= str(row["decided_on"]):
                continue   # the lesson predates the falsification: not a relapse
            ls = lines_of(root, a["path"]) or []
            for n in a["lines"]:
                if not re.search(rf"\b{re.escape(fid)}\b", paragraph(ls, n - 1)):
                    relapse.append({"at": f"{a['path']}:{n}", "entered_in": a["entered_in"], "cites_missing": fid})
    if liveness == "moot":
        verdict = "MOOT"
    elif truth != "falsified":
        verdict = "CURRENT"
    else:   # precedence: a line still asserting the old belief outranks a lesson that forgot its F-row
        verdict = "SHIFTED-STALE-SIBLING" if stale else ("RELAPSED" if relapse else "SHIFTED-PROPAGATED")
    return {"id": row["id"], "ledger": row["ledger"], "claim": row["claim"], "verdict": verdict,
            "truth": truth, "liveness": liveness, "exit": row.get("exit"),
            "decided_on": row["decided_on"], "decided_ref": row["decided_ref"],
            "supersedes": row.get("supersedes"),
            "superseded_by": [r["id"] for r in rows if r.get("supersedes") == row["id"]],
            "stale_siblings": stale, "relapsed": relapse, "anchors": anchors, "notes": notes}


def blame_line(root: Path, rel: str, n: int) -> dict:
    ls = lines_of(root, rel)
    if ls is None or not 1 <= n <= len(ls):
        raise SystemExit(f"belief_blame: {rel}:{n} is not a line in this checkout")
    text = ls[n - 1]
    porcelain = git(root, "blame", "-w", "-C", "-L", f"{n},{n}", "--porcelain", "--", rel)
    last = porcelain.split(" ", 1)[0][:9] if porcelain else None
    rows = load_rows(root)
    beliefs = []
    for r in rows:
        if any(a["path"] == rel and a["phrase"] in text for a in r["anchors"]):
            b = assess(root, r, rows)
            mine = next(a for a in b["anchors"] if a["path"] == rel and n in a["lines"])
            b["on_this_line"] = {"phrase": mine["phrase"], "role": mine["role"], "entered_in": mine["entered_in"]}
            for pid in filter(None, [b["supersedes"]]):
                prev = next((x for x in rows if x["id"] == pid), None)
                if prev:
                    pv = assess(root, prev, rows)
                    b["predecessor"] = {k: pv[k] for k in ("id", "verdict", "exit", "decided_ref", "stale_siblings")}
            beliefs.append(b)
    return {"line": f"{rel}:{n}", "text": text, "last_touched_in": last,
            "verdict": None if beliefs else "UNREGISTERED", "beliefs": beliefs}


def blame_edge(root: Path, row_id: str, dep: str) -> dict:
    rows = read_jsonl(root, BACKLOG)
    by = {r.get("id"): r for r in rows}
    if row_id not in by:
        raise SystemExit(f"belief_blame: no backlog row {row_id}")
    if dep not in (by[row_id].get("depends_on") or []):
        raise SystemExit(f"belief_blame: {row_id} does not depend on {dep}")
    pat = '"id": "%s".*"depends_on": \\[[^]]*"%s"' % (re.escape(row_id), re.escape(dep))
    out = git(root, "log", "--reverse", "--format=%h %ad", "--date=short", "-G", pat, "--", BACKLOG)
    first = out.splitlines()[0].split(" ", 1) if out.strip() else [None, None]
    target = by.get(dep, {})
    state = target.get("state", "MISSING")
    verdict = "MOOT" if state in ("COMPOSTED", "SUPERSEDED", "MISSING") else "CURRENT"
    return {"edge": f"{row_id} -> {dep}", "belief": f"{row_id} cannot finish until {dep} is done",
            "entered_in": first[0], "entered_on": first[1], "target_state": state,
            "satisfied": state == "DONE", "verdict": verdict}


def scan(root: Path) -> list[dict]:
    rows = load_rows(root)
    return [assess(root, r, rows) for r in rows if r["anchors"]]


def check(root: Path) -> list[str]:
    errs = []
    for rel in (ASM, FLEDGER):
        for r in read_jsonl(root, rel):
            errs += [f"{rel} {r.get('id','?')}: {e}" for e in validate_anchors(r)]
    return errs


# ---- output -------------------------------------------------------------------------------

def fmt_belief(b: dict, indent: str = "") -> list[str]:
    out = [f"{indent}{b['id']}  {b['verdict']}  truth={b['truth']} liveness={b['liveness']}"
           + (f" exit={b['exit']}" if b["exit"] else "")
           + (f"  decided {b['decided_on']} by {b['decided_ref']}" if b["truth"] != "open" else ""),
           f"{indent}  belief: {b['claim']}"]
    for a in b["anchors"]:
        where = ",".join(map(str, a["lines"])) or ("gone" if a["path_exists"] else "path missing")
        out.append(f"{indent}  {a['role']:<7} {a['path']}:{where}  entered {a['entered_in'] or '?'}"
                   + (f" {a['entered_on']}" if a["entered_on"] else "")
                   + (f", removed {a['removed_in']}" if a["removed_in"] else ""))
    if b["stale_siblings"]:
        out.append(f"{indent}  STALE: the old belief is still stated at {', '.join(b['stale_siblings'])}; rewrite it and cite {b['decided_ref']}")
    for x in b["relapsed"]:
        out.append(f"{indent}  RELAPSED (warn until {RELAPSE_GATE_DECISION}): {x['at']} entered {x['entered_in']} does not cite {x['cites_missing']}")
    if b["superseded_by"]:
        out.append(f"{indent}  superseded by {', '.join(b['superseded_by'])}")
    out += [f"{indent}  note: {n}" for n in b["notes"]]
    return out


def print_line(r: dict) -> None:
    print(f"{r['line']}  last touched {r['last_touched_in']}")
    print(f"  {r['text'][:160]}{'...' if len(r['text']) > 160 else ''}")
    if not r["beliefs"]:
        print("  UNREGISTERED: no assumptions or F-row is anchored to this line; register an asm row with a test")
    for b in r["beliefs"]:
        o = b["on_this_line"]
        print(f"  [{o['role']}] \"{o['phrase']}\" entered {o['entered_in']} (blame says {r['last_touched_in']})")
        for l in fmt_belief(b, "    "):
            print(l)
        if b.get("predecessor"):
            p = b["predecessor"]
            print(f"    predecessor {p['id']}: {p['verdict']} exit={p['exit']} shifted by {p['decided_ref']}"
                  + (f"; stale at {', '.join(p['stale_siblings'])}" if p["stale_siblings"] else ""))


# ---- self-test ----------------------------------------------------------------------------

def self_test() -> int:
    fails = 0

    def ok(label: str, cond: bool, detail: object = "") -> None:
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail if not cond else ''}")
        fails += 0 if cond else 1

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        env_dates: dict[str, str] = {}

        def sh(*a: str) -> None:
            subprocess.run(["git", *a], cwd=t, check=True, capture_output=True,
                           env={"GIT_AUTHOR_DATE": env_dates.get("d", "2026-10-20T12:00:00"),
                                "GIT_COMMITTER_DATE": env_dates.get("d", "2026-10-20T12:00:00"),
                                "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                                "GIT_COMMITTER_EMAIL": "t@t", "HOME": tmp, "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})

        def write(rel: str, text: str) -> None:
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            (t / rel).write_text(text, encoding="utf-8")

        def commit(msg: str, date: str) -> str:
            env_dates["d"] = date
            sh("add", "-A")
            sh("commit", "-q", "-m", msg)
            return git(t, "rev-parse", "--short=7", "HEAD").strip()

        def ledgers(asm: list[dict], f: list[dict]) -> None:
            write(ASM, "".join(json.dumps(r) + "\n" for r in asm))
            write(FLEDGER, "".join(json.dumps(r) + "\n" for r in f))

        sh("init", "-q")
        old = "Branch protection cannot enforce this on the free plan"
        write("AGENTS.md", f"intro\n\n17. Merge with --merge. {old}, so detect daily.\n")
        write("detector.py", f'"""\nPolicy: merge commits only.\n{old}, so this is detection.\n"""\n')
        write("rule.md", "rule: never squash merges here\n")
        c1 = commit("c1 states the belief", "2026-09-28T12:00:00")
        write("AGENTS.md", "intro\n\n17. Merge with --merge. Enforced since 2026-10-06 by the merge-method setting.\n")
        write("rule.md", "RULE (amended): never squash merges here, ok\nalso, never squash merges here\n")
        c2 = commit("c2 shifts it in AGENTS.md only", "2026-10-06T12:00:00")

        f26 = {"id": "F26", "scope": "process", "ts": "2026-07-24", "claim": "watch then merge is enough",
               "test": "merged on red", "verdict": "FALSIFIED", "delta": "d", "fix": "f", "confidence": "high",
               "refs": [], "canon": False}
        base = {"held_by": "both", "held_since": "2026-09-28", "depends_on_it": [], "notes": "",
                "test_that_would_decide": "read the repo merge-method setting via the API", "supersedes": None}
        b_old = dict(base, id="asm-001", assumption="branch protection cannot enforce merge commits",
                     status="falsified", decided_on="2026-10-06", decided_ref=c2, exit="revealed-incompleteness",
                     anchors=[{"path": "AGENTS.md", "phrase": old}, {"path": "detector.py", "phrase": old}])
        b_new = dict(base, id="asm-002", assumption="the merge-method setting refuses squash on any plan",
                     held_since="2026-10-06", status="held", decided_on="2026-10-06", decided_ref=c2, supersedes="asm-001",
                     anchors=[{"path": "AGENTS.md", "phrase": "Enforced since 2026-10-06 by the merge-method setting"}])
        lesson = "a wait loop merged while Vercel was still PENDING"
        relapse_row = dict(base, id="asm-003", assumption="waiting for checks to finish is a sufficient gate",
                           status="falsified", decided_on="2026-07-24", decided_ref="F26", exit="revealed-incompleteness",
                           anchors=[{"path": "merge.sh", "phrase": lesson, "role": "lesson"}])
        rule_row = dict(base, id="asm-004", assumption="squash merges erase the PR boundary", status="open",
                        decided_on=None, decided_ref=None, anchors=[{"path": "rule.md", "phrase": "never squash merges here"}])
        moot_row = dict(base, id="asm-005", assumption="the old recoil password gate protects /recoil", status="held",
                        decided_on="2026-10-01", decided_ref="AGENTS.md", exit="moot",
                        anchors=[{"path": "rule.md", "phrase": "RULE (amended)"}])
        write("merge.sh", f"#!/bin/sh\n# Tuition (2026-10-20): {lesson}.\n# one helper fails the class.\n\necho merge\n")
        ledgers([b_old, b_new, relapse_row, rule_row, moot_row], [f26])
        write(BACKLOG, json.dumps({"id": "a", "state": "DONE", "depends_on": []}) + "\n")
        commit("c3 ledgers, Tuition without F26", "2026-10-20T12:00:00")
        write(BACKLOG, json.dumps({"id": "a", "state": "DONE", "depends_on": []}) + "\n"
              + json.dumps({"id": "b", "state": "OPEN", "depends_on": ["a"]}) + "\n")
        c4 = commit("c4 adds edge b -> a", "2026-10-21T12:00:00")

        snap = {p: p.read_bytes() for p in t.rglob("*") if p.is_file() and ".git" not in p.parts}
        rows = load_rows(t)
        get = lambda i: assess(t, next(r for r in rows if r["id"] == i), rows)  # noqa: E731

        k1 = get("asm-001")
        ok("K1 bad: stale sibling flagged with its path and the shift commit",
           k1["verdict"] == "SHIFTED-STALE-SIBLING" and k1["stale_siblings"] == ["detector.py:3"] and k1["decided_ref"] == c2, k1)
        ok("K1 bad: the rewritten line reports removed_in the shift commit",
           next(a for a in k1["anchors"] if a["path"] == "AGENTS.md")["removed_in"] == c2)
        ok("D2: truth and liveness and exit are fields", (k1["truth"], k1["liveness"], k1["exit"]) == ("falsified", "live", "revealed-incompleteness"))

        k2 = get("asm-003")
        ok("K2 bad: Tuition dated after F26 without citing it is RELAPSED",
           k2["verdict"] == "RELAPSED" and len(k2["relapsed"]) == 1 and k2["relapsed"][0]["at"] == "merge.sh:2" and k2["relapsed"][0]["cites_missing"] == "F26", k2["relapsed"])

        k3 = blame_line(t, "rule.md", 1)
        on = k3["beliefs"][0]["on_this_line"] if k3["beliefs"] else {}
        ok("K3 bad->good: entry is the first commit that stated the phrase, not blame's last touch",
           on.get("entered_in") == c1 and k3["last_touched_in"].startswith(c2), (on, k3["last_touched_in"], c1, c2))

        ok("line on a shifted line names the successor CURRENT and the predecessor's stale sibling",
           (lambda r: r["beliefs"] and r["beliefs"][0]["id"] == "asm-002" and r["beliefs"][0]["verdict"] == "CURRENT"
            and r["beliefs"][0]["predecessor"]["stale_siblings"] == ["detector.py:3"])(blame_line(t, "AGENTS.md", 3)))
        ok("UNREGISTERED when no row is anchored", blame_line(t, "AGENTS.md", 1)["verdict"] == "UNREGISTERED")
        ok("MOOT on the liveness axis, not falsified", (lambda b: b["verdict"] == "MOOT" and b["truth"] == "held")(get("asm-005")))
        e = blame_edge(t, "b", "a")
        ok("edge: entered in the commit that added it, satisfied when the target is DONE",
           e["entered_in"] == c4 and e["satisfied"] and e["verdict"] == "CURRENT", e)
        ok("check passes on valid anchors", check(t) == [])
        ok("read-only: nothing in the tree changed", snap == {p: p.read_bytes() for p in t.rglob("*") if p.is_file() and ".git" not in p.parts})

        write("detector.py", '"""\nPolicy: merge commits only.\nThe merge-method setting enforces it; this detector is a backstop.\n"""\n')
        write("merge.sh", f"#!/bin/sh\n# Tuition (2026-10-20): {lesson} (see F26).\n# one helper fails the class.\n\necho merge\n")
        commit("c5 propagate and cite", "2026-10-22T12:00:00")
        rows = load_rows(t)
        ok("K1 good: rewriting the sibling gives SHIFTED-PROPAGATED", get("asm-001")["verdict"] == "SHIFTED-PROPAGATED")
        ok("K2 good: the same Tuition with (see F26) is silent", (lambda b: b["relapsed"] == [] and b["verdict"] == "SHIFTED-PROPAGATED")(get("asm-003")))

        write("merge.sh", f"#!/bin/sh\n# Tuition: {lesson}.\n")
        ledgers([dict(relapse_row, decided_on="2026-11-30")], [])
        commit("c6 lesson predates the falsification", "2026-10-23T12:00:00")
        rows = load_rows(t)
        ok("K2 good: a lesson older than the falsification is not a relapse", get("asm-003")["relapsed"] == [])
        ledgers([dict(rule_row, anchors=[{"path": "/abs", "phrase": "short"}])], [])
        ok("check rejects bad anchors", len(check(t)) == 1)

        me = Path(__file__).resolve()
        for args in (["scan", "--bogus"], ["line"], ["belief", "a", "b"], ["frobnicate"]):
            ok(f"argument error exits 2: {' '.join(args)}", subprocess.run([sys.executable, str(me), *args],
               capture_output=True).returncode == 2)

    total = 19
    print(f"belief_blame self-test: {total - fails}/{total}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="belief_blame.py", description="Blame the assumption, not the author (read-only).")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("line"); p.add_argument("target", help="PATH:N"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("belief"); p.add_argument("id"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("edge"); p.add_argument("row"); p.add_argument("dep"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("scan"); p.add_argument("--json", action="store_true")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cmd == "line":
        rel, _, n = a.target.rpartition(":")
        if not rel or not n.isdigit():
            ap.error("line takes PATH:N")
        r = blame_line(ROOT, rel, int(n))
        print(json.dumps(r, indent=1)) if a.json else print_line(r)
    elif a.cmd == "belief":
        rows = load_rows(ROOT)
        row = next((r for r in rows if r["id"] == a.id), None)
        if row is None:
            print(f"belief_blame: no row {a.id} in either ledger", file=sys.stderr)
            return 1
        b = assess(ROOT, row, rows)
        print(json.dumps(b, indent=1)) if a.json else print("\n".join(fmt_belief(b)))
    elif a.cmd == "edge":
        r = blame_edge(ROOT, a.row, a.dep)
        if a.json:
            print(json.dumps(r, indent=1))
        else:
            print(f"{r['edge']}  {r['verdict']}  entered {r['entered_in'] or 'uncommitted'} {r['entered_on'] or ''}  target {r['target_state']}"
                  f"{' (satisfied)' if r['satisfied'] else ''}\n  belief: {r['belief']}")
    elif a.cmd == "scan":
        res = scan(ROOT)
        if a.json:
            print(json.dumps(res, indent=1))
        else:
            for b in res:
                print("\n".join(fmt_belief(b)))
            n_stale = sum(1 for b in res if b["stale_siblings"])
            n_rel = sum(len(b["relapsed"]) for b in res)
            print(f"belief_blame scan: {len(res)} anchored rows, {n_stale} with stale siblings, {n_rel} relapse warnings"
                  f" (warn only until {RELAPSE_GATE_DECISION})")
    elif a.cmd == "check":
        errs = check(ROOT)
        for e in errs:
            print(e, file=sys.stderr)
        print(f"belief_blame check: {'FAIL' if errs else 'OK'} ({len(errs)} anchor errors)")
        return 1 if errs else 0
    else:
        ap.error("a command is required")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
