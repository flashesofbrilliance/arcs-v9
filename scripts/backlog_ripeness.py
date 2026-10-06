#!/usr/bin/env python3
"""backlog_ripeness.py: which induced-backlog rows have RIPENED (their spark plug fired).

Companion to backlog_freshness.py. Freshness asks "is this row past its review_by" (staleness,
the expiration sticker). Ripeness asks "did the thing this row was waiting on happen" (the fruit
is ready, pick it). Vocabulary from the ripeness-resolution family (composted / molted /
superseded / pulse): this script detects, it never resolves. Fates stay human (NOTOMATION).

Verdicts, per non-terminal row (DONE/CLOSED/COMPOSTED/SUPERSEDED/LOCKED/BUILT rows are skipped):
  SECRETLY-DONE  status is OPEN/INDUCED but cites LANDED / merged / a receipt id, and every PR it
                 cites is MERGED (a receipt id with no PR also counts; LANDED alone does not)
  BLOCKED        a depends_on id is missing, or targets a COMPOSTED/SUPERSEDED row (re-point it)
  RIPE           every depends_on resolves to DONE/CLOSED/LANDED/BUILT, or the trigger is
                 mechanically checkable and now true:
                   "PR #N merges|merged|lands"  -> gh pr view N --json state == MERGED
                   "after|from|on|by|until|resets|window|not before <ISO date>"  -> date <= today
                   "ADR-NNN accepted"           -> _DECISIONS/ADR-NNN-*.md Status line says ACCEPTED
                 " OR " clauses: any true clause ripens the row.
  WAITING        checkable, not yet true (dependency open, PR open, date ahead, ADR not accepted)
  NEEDS-HUMAN    trigger is human or unparseable, or gh could not answer. Never guessed.

usage:
  backlog_ripeness.py [--file F] [--today YYYY-MM-DD] [--json] [--all]
  backlog_ripeness.py --check          exit 1 if any row is RIPE or SECRETLY-DONE
  backlog_ripeness.py --self-test      inline fixture, gh stubbed, no network, no real file
  backlog_ripeness.py --apply-closes   rewrite status of SECRETLY-DONE rows ONLY (never HELD /
                                       TABLED / COMPOSTED / consent-gated). Default off.
Env BACKLOG_RIPENESS_GH_STUB='{"598":"MERGED"}' replaces gh entirely (unknown PR -> UNKNOWN).
Stdlib only. Read-only unless --apply-closes.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
ADR_DIR = ROOT / "_DECISIONS"

TERMINAL = ("DONE", "CLOSED", "COMPOSTED", "SUPERSEDED", "LOCKED", "BUILT", "MOSTLY_DONE")
DEP_DONE = ("DONE", "CLOSED", "LANDED", "BUILT", "MOSTLY_DONE", "LOCKED")
DEP_DEAD = ("COMPOSTED", "SUPERSEDED")
NEVER_APPLY = ("HELD", "TABLED", "COMPOSTED")
OPENISH = ("OPEN", "INDUCED")

PR_RE = re.compile(r"(?:\bPR\s*#?|(?<![\w/])#)(\d{2,5})\b", re.I)
RECEIPT_RE = re.compile(r"\b20\d\d-\d\d-\d\d--[\w.\-]+--[A-Z]{2,}\b")
DONE_MARK_RE = re.compile(r"\bLANDED\b|\bmerged\b|\bshipped\b", re.I)
TRIG_PR_RE = re.compile(r"\bPR\s*#?(\d{2,5})\s+(?:merges|merged|lands|landed|is merged)\b", re.I)
TRIG_DATE_RE = re.compile(
    r"\b(?:after|from|on|by|until|resets|window(?: opens)?|not before|starting)\s+(20\d\d-\d\d-\d\d)\b", re.I)
BARE_DATE_RE = re.compile(r"^\s*(20\d\d-\d\d-\d\d)\s*$")
TRIG_ADR_RE = re.compile(r"\bADR-(\d{3})\s+(?:is\s+)?accepted\b", re.I)

_gh_cache = {}


def _status(row):
    return str(row.get("status") or "OPEN").strip()


def _starts(status, prefixes):
    return status.upper().startswith(prefixes)


def _deps(row):
    d = row.get("depends_on")
    if not d:
        return []
    if isinstance(d, str):
        d = re.split(r"[,\s]+", d)
    return [x.strip() for x in d if str(x).strip()]


def pr_state(n):
    """MERGED / OPEN / CLOSED / UNKNOWN. Cached per process; gh failure is UNKNOWN, never a guess."""
    n = str(n)
    if n in _gh_cache:
        return _gh_cache[n]
    stub = os.environ.get("BACKLOG_RIPENESS_GH_STUB")
    if stub is not None:
        try:
            st = str(json.loads(stub).get(n, "UNKNOWN")).upper()
        except ValueError:
            st = "UNKNOWN"
    else:
        try:
            out = subprocess.run(["gh", "pr", "view", n, "--json", "state"], capture_output=True,
                                 text=True, timeout=15, cwd=ROOT)
            st = json.loads(out.stdout).get("state", "UNKNOWN").upper() if out.returncode == 0 else "UNKNOWN"
        except Exception:  # noqa: BLE001  named as UNKNOWN in the verdict
            st = "UNKNOWN"
    _gh_cache[n] = st
    return st


def adr_status(num, adr_dir):
    hits = sorted(Path(adr_dir).glob(f"ADR-{num}-*.md")) + sorted(Path(adr_dir).glob(f"ADR-{num}.md"))
    if not hits:
        return None
    for line in hits[0].read_text(errors="replace").splitlines()[:40]:
        if re.search(r"status", line, re.I):
            return line.strip()
    return ""


def _clause(text, today, adr_dir):
    """-> (state, evidence); state in True / False / None (not checkable)."""
    m = TRIG_PR_RE.search(text)
    if m:
        st = pr_state(m.group(1))
        if st == "UNKNOWN":
            return None, f"PR #{m.group(1)} state UNKNOWN (gh)"
        return st == "MERGED", f"PR #{m.group(1)} {st}"
    m = TRIG_ADR_RE.search(text)
    if m:
        line = adr_status(m.group(1), adr_dir)
        if line is None:
            return None, f"ADR-{m.group(1)} file not found"
        return bool(re.search(r"\bACCEPTED\b", line, re.I)), f"ADR-{m.group(1)} {line[:60] or 'no status line'}"
    m = TRIG_DATE_RE.search(text) or BARE_DATE_RE.match(text)
    if m:
        d = dt.date.fromisoformat(m.group(1))
        return d <= today, f"date {d} {'passed' if d <= today else 'ahead'}"
    return None, ""


def assess(row, by_id, today, adr_dir=ADR_DIR):
    """-> (verdict, evidence) or None for terminal rows."""
    status = _status(row)
    if _starts(status, TERMINAL):
        return None
    up = status.upper()

    # 1. SECRETLY-DONE: the status prose already says it happened.
    if _starts(status, OPENISH) or up == "OPEN":
        receipts = RECEIPT_RE.findall(status)
        prs = sorted(set(PR_RE.findall(RECEIPT_RE.sub(" ", status))), key=int)
        if DONE_MARK_RE.search(status) or receipts:
            if prs:
                states = {p: pr_state(p) for p in prs}
                ev = ", ".join(f"#{p} {s}" for p, s in states.items())
                if all(s == "MERGED" for s in states.values()):
                    return "SECRETLY-DONE", f"status cites {ev}" + (f"; receipt {receipts[0]}" if receipts else "")
                if any(s == "UNKNOWN" for s in states.values()):
                    return "NEEDS-HUMAN", f"cites landing but {ev}"
                # some cited PR still open/closed: fall through to the trigger check
            elif receipts:
                return "SECRETLY-DONE", f"status cites receipt {receipts[0]}"
            else:
                return "NEEDS-HUMAN", "status says LANDED/merged but cites no PR or receipt to verify"
        elif prs:
            closed = [p for p in prs if pr_state(p) == "CLOSED"]
            if closed:
                return "NEEDS-HUMAN", "status cites PR " + ", ".join(f"#{p}" for p in closed) + " CLOSED unmerged"

    # 2. depends_on
    deps = _deps(row)
    if deps:
        missing = [d for d in deps if d not in by_id]
        if missing:
            return "BLOCKED", "missing depends_on: " + ", ".join(missing)
        dead = [d for d in deps if _starts(_status(by_id[d]), DEP_DEAD)]
        if dead:
            return "BLOCKED", "depends_on resolved dead: " + ", ".join(
                f"{d} ({_status(by_id[d]).split()[0]})" for d in dead)
        pending = [d for d in deps if not _starts(_status(by_id[d]), DEP_DONE)]
        if not pending:
            return "RIPE", "all depends_on done: " + ", ".join(deps)
        dep_ev = "waiting on " + ", ".join(pending)
        secret = [d for d in pending if (assess(by_id[d], by_id, today, adr_dir) or ("",))[0] == "SECRETLY-DONE"]
        if secret:
            dep_ev += " (secretly done: " + ", ".join(secret) + "; ripe once closed)"
    else:
        dep_ev = ""

    # 3. trigger
    trig = str(row.get("trigger") or "")
    results = [_clause(c, today, adr_dir) for c in re.split(r"\s+OR\s+", trig)] if trig else []
    checkable = [(s, e) for s, e in results if s is not None]
    if not deps:
        for s, e in checkable:
            if s:
                return "RIPE", "trigger: " + e
        if checkable:
            return "WAITING", "trigger: " + "; ".join(e for _, e in checkable)
        unknown = [e for s, e in results if s is None and e]
        return "NEEDS-HUMAN", unknown[0] if unknown else ("human trigger" if trig else "no trigger, no depends_on")
    return "WAITING", dep_ev


def run(rows, today, adr_dir=ADR_DIR):
    by_id = {r["id"]: r for r in rows if "id" in r}
    out = []
    for r in rows:
        if "id" not in r:
            continue
        v = assess(r, by_id, today, adr_dir)
        if v:
            out.append({"id": r["id"], "verdict": v[0], "evidence": v[1]})
    return out


ORDER = ["SECRETLY-DONE", "RIPE", "BLOCKED", "WAITING", "NEEDS-HUMAN"]


def render(found, today, show_all=False):
    counts = {k: sum(1 for f in found if f["verdict"] == k) for k in ORDER}
    lines = [f"backlog ripeness {today}: " + " · ".join(f"{k} {v}" for k, v in counts.items())]
    shown = sorted((f for f in found if show_all or f["verdict"] in ORDER[:3]),
                   key=lambda f: (ORDER.index(f["verdict"]), f["id"]))
    if shown:
        w = max(len(f["id"]) for f in shown)
        for f in shown:
            lines.append(f"  {f['id']:<{w}}  {f['verdict']:<13}  {f['evidence'][:110]}")
    if not show_all and (counts["WAITING"] or counts["NEEDS-HUMAN"]):
        lines.append("  (WAITING / NEEDS-HUMAN rows hidden; --all to list)")
    return "\n".join(lines)


def load(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def apply_closes(path, found, today):
    """Rewrite status of SECRETLY-DONE rows only. Line-preserving for every other row."""
    targets = {f["id"]: f["evidence"] for f in found if f["verdict"] == "SECRETLY-DONE"}
    lines = Path(path).read_text().splitlines()
    changed = []
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        r = json.loads(l)
        rid = r.get("id")
        if rid not in targets:
            continue
        old = _status(r)
        gates = json.dumps(r.get("gates", "")).lower()
        if _starts(old, NEVER_APPLY) or re.search(r"\b(HELD|TABLED)\b", old) or "consent" in gates \
                or "consent" in old.lower():
            continue
        r["status"] = f"DONE {today} (ripeness: {targets[rid]}) || prior: {old}"
        lines[i] = json.dumps(r, ensure_ascii=False)
        changed.append(rid)
    if changed:
        Path(path).write_text("\n".join(lines) + "\n")
    return changed


def self_test():
    today = dt.date(2026, 10, 6)
    tmp = Path(tempfile.mkdtemp())
    (tmp / "ADR-090-x.md").write_text("# ADR-090\n> **Status:** ACCEPTED 2026-10-01\n")
    (tmp / "ADR-091-y.md").write_text("# ADR-091\n> **Status:** DRAFT\n")
    os.environ["BACKLOG_RIPENESS_GH_STUB"] = json.dumps({"598": "MERGED", "599": "OPEN", "700": "MERGED", "444": "CLOSED"})
    _gh_cache.clear()
    rows = [
        {"_schema": "induced-backlog-v1"},
        {"id": "dep-done", "status": "DONE 2026-10-01"},
        {"id": "dep-landed", "status": "LANDED 2026-10-02"},
        {"id": "dep-open", "status": "OPEN"},
        {"id": "dep-composted", "status": "COMPOSTED 2026-10-04"},
        {"id": "ripe-deps", "status": "INDUCED — HOLDING until depends_on clear", "depends_on": ["dep-done", "dep-landed"]},
        {"id": "ripe-pr", "status": "OPEN", "trigger": "PR #598 merges"},
        {"id": "ripe-date", "status": "HELD", "trigger": "revisit after 2026-10-01"},
        {"id": "ripe-adr", "status": "OPEN", "trigger": "ADR-090 accepted"},
        {"id": "ripe-or", "status": "OPEN", "trigger": "Zach decides OR PR #700 merged"},
        {"id": "secret-pr", "status": "OPEN — LANDED 2026-09-28: PR #700 merged", "trigger": "x"},
        {"id": "secret-receipt", "status": "OPEN — shipped, receipt 2026-10-05--thing-pr757--ZH"},
        {"id": "not-secret", "status": "OPEN — PR #599 OPEN, LANDED partially", "trigger": "PR #599 merges"},
        {"id": "landed-noproof", "status": "OPEN — LANDED somewhere"},
        {"id": "blocked-missing", "status": "INDUCED", "depends_on": "ghost-row"},
        {"id": "blocked-dead", "status": "INDUCED", "depends_on": ["dep-composted"]},
        {"id": "wait-deps", "status": "INDUCED", "depends_on": ["dep-open", "dep-done"]},
        {"id": "wait-pr", "status": "OPEN", "trigger": "PR #599 merges"},
        {"id": "wait-date", "status": "OPEN", "trigger": "cap resets 2026-11-01"},
        {"id": "wait-adr", "status": "OPEN", "trigger": "ADR-091 accepted"},
        {"id": "human", "status": "OPEN", "trigger": "Zach, 2026-09-16: 'I want X'"},
        {"id": "unknown-pr", "status": "OPEN", "trigger": "PR #123 merges"},
        {"id": "closed-pr", "status": "OPEN — PR #444 open, conflicting", "trigger": "ranked #5"},
        {"id": "wait-secret", "status": "INDUCED", "depends_on": ["secret-pr"]},
        {"id": "secret-held", "status": "OPEN — LANDED: PR #598 merged", "gates": ["Zach consent before close"]},
    ]
    want = {
        "ripe-deps": "RIPE", "ripe-pr": "RIPE", "ripe-date": "RIPE", "ripe-adr": "RIPE", "ripe-or": "RIPE",
        "secret-pr": "SECRETLY-DONE", "secret-receipt": "SECRETLY-DONE", "secret-held": "SECRETLY-DONE",
        "not-secret": "WAITING", "landed-noproof": "NEEDS-HUMAN",
        "blocked-missing": "BLOCKED", "blocked-dead": "BLOCKED",
        "wait-deps": "WAITING", "wait-pr": "WAITING", "wait-date": "WAITING", "wait-adr": "WAITING",
        "dep-open": "NEEDS-HUMAN", "human": "NEEDS-HUMAN", "unknown-pr": "NEEDS-HUMAN",
        "closed-pr": "NEEDS-HUMAN", "wait-secret": "WAITING",
    }
    got = {f["id"]: f["verdict"] for f in run(rows, today, tmp)}
    fails = [f"{k}: want {v} got {got.get(k)}" for k, v in want.items() if got.get(k) != v]
    if "dep-done" in got or "dep-composted" in got:
        fails.append("terminal rows must be skipped")

    # --check semantics: fail-on-bad (fixture above has RIPE) AND pass-on-good.
    good = [r for r in rows if r.get("id", "").startswith(("dep-", "wait-", "human", "blocked"))]
    bad_hits = [f for f in run(rows, today, tmp) if f["verdict"] in ("RIPE", "SECRETLY-DONE")]
    good_hits = [f for f in run(good, today, tmp) if f["verdict"] in ("RIPE", "SECRETLY-DONE")]
    if not bad_hits:
        fails.append("--check would pass on the bad fixture")
    if good_hits:
        fails.append(f"--check would fail on the good fixture: {good_hits}")

    # --apply-closes: only SECRETLY-DONE, never the consent-gated one, other lines byte-identical.
    f = tmp / "b.jsonl"
    f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    before = f.read_text().splitlines()
    changed = apply_closes(f, run(load(f), today, tmp), today)
    after = f.read_text().splitlines()
    if sorted(changed) != ["secret-pr", "secret-receipt"]:
        fails.append(f"apply-closes changed {changed}")
    diff = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    if len(diff) != 2 or len(before) != len(after):
        fails.append(f"apply-closes touched {len(diff)} lines")
    if not any("|| prior: OPEN — LANDED 2026-09-28" in l for l in after):
        fails.append("apply-closes did not keep prior status")

    del os.environ["BACKLOG_RIPENESS_GH_STUB"]
    _gh_cache.clear()
    if fails:
        print("self-test FAIL\n  " + "\n  ".join(fails))
        return 1
    print(f"self-test OK ({len(want)} verdict cases, check fail-on-bad + pass-on-good, apply-closes scoped)")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="backlog_ripeness.py", description=__doc__.split("\n")[0])
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.add_argument("--today", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--all", action="store_true")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--apply-closes", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    found = run(load(a.file), today)
    if a.apply_closes:
        changed = apply_closes(a.file, found, today)
        print(f"apply-closes: {len(changed)} row(s) closed: {', '.join(changed) or 'none'}")
        return 0
    if a.json:
        print(json.dumps({"date": str(today), "rows": found}, indent=1))
    else:
        print(render(found, today, a.all))
    if a.check:
        return 1 if any(f["verdict"] in ("RIPE", "SECRETLY-DONE") for f in found) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
