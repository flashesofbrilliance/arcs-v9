#!/usr/bin/env python3
"""
assumptions.py — the ASSUMPTIONS LEDGER: premises held BEFORE they are tested, with the test
that would decide them, so a belief has an OPEN state anyone can see before it becomes an
F-row (falsified) or a HELD row.

Gap it closes (Zach, 2026-09-27: "do we have an assumption ledger where those have been proven /
disproven?"): the falsification ledger records claims AFTER a test (40 rows, all FALSIFIED);
LORE holds stories with verdicts; source-trust records outcomes per source; the job-search
hypothesis ledger pre-registers, but only for one domain. Today's assumptions ("everything can be
orchestrated or choreographed", "the harness cap is a constant") went from unstated straight to
held/falsified with no open state. This is the ethereal-stage ledger of the hyperstition pipeline.

Discipline (borrowed from _STATE/job-search/hypothesis-ledger.md): register BEFORE counting; the
commit timestamp is the write-lock; never edit a decided row, add a new one and point back.

Row schema (_STATE/assumptions.jsonl, append-only):
  id                    asm-NNN (monotonic; no oracle namespace yet, check enforces order)
  assumption            one sentence, stated so it can be false
  held_by               zach | claude-fable | both | <source key from source-trust-sources.json>
  held_since            YYYY-MM-DD
  depends_on_it         [] what breaks if it is false (paths, seeds, ADRs, decisions)
  test_that_would_decide one sentence; REQUIRED even while open (an assumption with no test is a belief)
  status                open | held | falsified
  decided_on            YYYY-MM-DD | null
  decided_ref           F-row id | receipt id | path | null   (REQUIRED when status != open)
  notes                 free text
  supersedes            asm-NNN | null

Usage:
  python3 scripts/assumptions.py check      # schema, ids, open-needs-test, decided-needs-ref, render fresh
  python3 scripts/assumptions.py render     # _STATE/assumptions.md
  python3 scripts/assumptions.py open       # list open rows (the ones a session can test)
  python3 scripts/assumptions.py --self-test
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_STATE" / "assumptions.jsonl"
RENDER = ROOT / "_STATE" / "assumptions.md"
REQUIRED = ("id", "assumption", "held_by", "held_since", "depends_on_it", "test_that_would_decide", "status", "decided_on", "decided_ref", "notes", "supersedes")
STATUSES = ("open", "held", "falsified")
ID_RE = re.compile(r"^asm-(\d{3})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(path: Path = DATA) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def validate(rows: list[dict]) -> list[str]:
    errs: list[str] = []
    last = 0
    ids = {r.get("id") for r in rows}
    for n, r in enumerate(rows, 1):
        for k in REQUIRED:
            if k not in r:
                errs.append(f"row {n} ({r.get('id','?')}): missing {k}")
        m = ID_RE.match(str(r.get("id", "")))
        if not m:
            errs.append(f"row {n}: id must be asm-NNN")
        else:
            num = int(m.group(1))
            if num <= last:
                errs.append(f"row {n}: id {r['id']} not monotonic (append-only)")
            last = max(last, num)
        if r.get("status") not in STATUSES:
            errs.append(f"row {n} ({r.get('id','?')}): status must be one of {STATUSES}")
        if len(str(r.get("test_that_would_decide", ""))) < 20:
            errs.append(f"row {n} ({r.get('id','?')}): test_that_would_decide is required and must be a real test (an assumption with no test is a belief)")
        if r.get("status") != "open":
            if not r.get("decided_ref"):
                errs.append(f"row {n} ({r.get('id','?')}): status {r.get('status')} needs decided_ref (F-row, receipt, or path)")
            if not DATE_RE.match(str(r.get("decided_on") or "")):
                errs.append(f"row {n} ({r.get('id','?')}): status {r.get('status')} needs decided_on")
        if not DATE_RE.match(str(r.get("held_since", ""))):
            errs.append(f"row {n} ({r.get('id','?')}): held_since must be YYYY-MM-DD")
        if r.get("supersedes") and r["supersedes"] not in ids:
            errs.append(f"row {n} ({r.get('id','?')}): supersedes {r['supersedes']} does not exist")
    return errs


def render_md(rows: list[dict]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    out = ["# Assumptions ledger — premises held before they were tested",
           "",
           "> GENERATED from `_STATE/assumptions.jsonl` by `scripts/assumptions.py render` — do not hand-edit.",
           "> The ethereal stage of the hyperstition pipeline, given a book. A row is registered while it is",
           "> still an assumption, with the test that would decide it. When the test runs it closes to `held`",
           "> or `falsified` and points at its F-row / receipt; the row is never edited, a successor is added.",
           "",
           f"Rows: {len(rows)} · " + " · ".join(f"{k}: {v}" for k, v in sorted(counts.items())),
           "",
           "| id | status | assumption | held by | since | test that would decide | decided |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        dec = f"{r['decided_on']} · `{r['decided_ref']}`" if r["status"] != "open" else "open"
        out.append(f"| {r['id']} | **{r['status']}** | {r['assumption']} | {r['held_by']} | {r['held_since']} | {r['test_that_would_decide']} | {dec} |")
    out.append("")
    return "\n".join(out)


def self_test() -> int:
    good = {"id": "asm-001", "assumption": "x is y", "held_by": "zach", "held_since": "2026-09-27", "depends_on_it": [],
            "test_that_would_decide": "measure y directly and compare to x", "status": "open", "decided_on": None, "decided_ref": None, "notes": "", "supersedes": None}
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("open row with a test passes", validate([good]) == [], validate([good]))
    check("open row without a test is rejected", validate([dict(good, test_that_would_decide="")]) != [])
    check("held row without decided_ref is rejected", validate([dict(good, status="held", decided_on="2026-09-27")]) != [])
    check("falsified row with ref + date passes", validate([dict(good, status="falsified", decided_on="2026-09-27", decided_ref="F38")]) == [])
    check("non-monotonic ids rejected", validate([dict(good, id="asm-002"), dict(good, id="asm-001")]) != [])
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    rows = load()
    if argv[:1] == ["render"]:
        errs = validate(rows)
        if errs:
            print("\n".join("✖ " + e for e in errs), file=sys.stderr); return 2
        RENDER.write_text(render_md(rows), encoding="utf-8"); print(f"rendered {RENDER.relative_to(ROOT)} ({len(rows)} rows)"); return 0
    if argv[:1] == ["check"]:
        errs = validate(rows)
        if errs:
            print("\n".join("✖ " + e for e in errs), file=sys.stderr); return 1
        if not RENDER.exists() or RENDER.read_text(encoding="utf-8") != render_md(rows):
            print("✖ _STATE/assumptions.md stale — run: python3 scripts/assumptions.py render", file=sys.stderr); return 1
        print(f"assumptions OK ({len(rows)} rows, render fresh)"); return 0
    if argv[:1] == ["open"]:
        for r in rows:
            if r["status"] == "open":
                print(f"{r['id']}  {r['assumption']}\n      test: {r['test_that_would_decide']}")
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
