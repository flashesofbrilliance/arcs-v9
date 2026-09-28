#!/usr/bin/env python3
"""
lore.py — LORE: the book of stories with their verdicts. LEGEND's uncle.

LEGEND says what a word means (denotation). LORE says what we believe and why, INCLUDING what
we stopped believing. The Tao is lore distilled to one line; canon is lore that graduated to
law; LEGEND is the key for reading all three. Zach, 2026-09-27: "does legend need an uncle
that's named LORE" → yes, and the uncle already had half a house (NFTT posts, great-moments,
witness stubs, WORLD.md, the falsification ledger's verdict column without the story).

Row schema (runtime/specs/lore.jsonl, one JSON object per line, append-mostly):
  id               lore-NNN (sequential; the oracle has no `lore` namespace yet, so the check
                   enforces uniqueness + monotonic order instead)
  class            myth | testimony | aspiration | measurement | practice
                   myth        = a causal story about how the world works (the verdict then grades it)
                   testimony   = someone said a thing; the observation IS the saying (great-moments)
                   aspiration  = a mood board; verdict must be `inspiration`
                   measurement = a number or constant someone measured
                   practice    = a way of working that a story carries (the witness request)
                   Zach 2026-09-27: "MYTH should also be a property / class" — class is WHAT KIND of
                   story; binding_verdict is HOW IT RESOLVED. durable-myth/old-wives-tale need class
                   myth; inspiration needs class aspiration.
  story            the tale as told, one paragraph, in the teller's words where possible
  told_where       where it circulates (NFTT slug, session, textbook, museum guide, WORLD.md ...)
  observation      the real thing people can see/measure that the story explains
  mechanism_claimed the causal link the story asserts
  binding_verdict  true | durable-myth | old-wives-tale | undecided | inspiration
                   durable-myth   = real observation + plausible mechanism + FALSE binding
                   old-wives-tale = rule of thumb with no evidence (dies on first careful contact)
                   undecided      = may be TOLD but not CITED (LORE's unconfirmed column)
                   inspiration    = a mood board for something real: kept for what it points TOWARD,
                                    may be told and cited AS aspiration, never as fact (ADR-044's
                                    aspiration column, given a shelf). Zach 2026-09-27: "some lore
                                    can be inspiration like a mood board for something real"
  test_that_decided the test (or null if undecided) — a verdict of true/durable-myth/old-wives-tale
                   without a test is REJECTED by check
  teaches          the portable lesson, one line
  date             YYYY-MM-DD the row was written
  refs             [] F-rows, receipts, paths, urls, memory links
  superseded_by    null | lore-NNN — a story is NEVER deleted when its verdict flips; a new row
                   is added and this points forward (the molted shell stays)

Usage:
  python3 scripts/lore.py render        # runtime/specs/LORE.md
  python3 scripts/lore.py check         # schema, ids, verdict-needs-test, render freshness
  python3 scripts/lore.py tell <id>     # print one story
  python3 scripts/lore.py --self-test
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "runtime" / "specs" / "lore.jsonl"
RENDER = ROOT / "runtime" / "specs" / "LORE.md"
REQUIRED = ("id", "class", "story", "told_where", "observation", "mechanism_claimed", "binding_verdict", "test_that_decided", "teaches", "date", "refs", "superseded_by")
VERDICTS = ("true", "durable-myth", "old-wives-tale", "undecided", "inspiration")
CLASSES = ("myth", "testimony", "aspiration", "measurement", "practice")
ID_RE = re.compile(r"^lore-(\d{3})$")


def load(path: Path = DATA) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, l in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if l.strip():
            try:
                rows.append(json.loads(l))
            except json.JSONDecodeError as e:
                raise SystemExit(f"lore.jsonl line {i}: invalid JSON ({e})")
    return rows


def validate(rows: list[dict]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    last = 0
    ids = {r.get("id") for r in rows}
    for n, r in enumerate(rows, 1):
        for k in REQUIRED:
            if k not in r:
                errs.append(f"row {n} ({r.get('id','?')}): missing {k}")
        m = ID_RE.match(str(r.get("id", "")))
        if not m:
            errs.append(f"row {n}: id must be lore-NNN")
        else:
            num = int(m.group(1))
            if r["id"] in seen:
                errs.append(f"row {n}: duplicate id {r['id']}")
            if num <= last:
                errs.append(f"row {n}: id {r['id']} not monotonic (append-only; previous {last:03d})")
            seen.add(r["id"]); last = max(last, num)
        c = r.get("class")
        if c not in CLASSES:
            errs.append(f"row {n} ({r.get('id','?')}): class must be one of {CLASSES}")
        v = r.get("binding_verdict")
        if v in ("durable-myth", "old-wives-tale") and c != "myth":
            errs.append(f"row {n} ({r.get('id','?')}): verdict {v} requires class myth")
        if v == "inspiration" and c != "aspiration":
            errs.append(f"row {n} ({r.get('id','?')}): verdict inspiration requires class aspiration")
        if c == "aspiration" and v != "inspiration":
            errs.append(f"row {n} ({r.get('id','?')}): class aspiration resolves only to inspiration")
        if v not in VERDICTS:
            errs.append(f"row {n} ({r.get('id','?')}): binding_verdict must be one of {VERDICTS}")
        elif v not in ("undecided", "inspiration") and not r.get("test_that_decided"):
            errs.append(f"row {n} ({r.get('id','?')}): verdict '{v}' needs test_that_decided (a verdict without a test is a rumor)")
        if len(str(r.get("teaches", ""))) < 20:
            errs.append(f"row {n} ({r.get('id','?')}): teaches too thin (<20 chars)")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("date", ""))):
            errs.append(f"row {n} ({r.get('id','?')}): date must be YYYY-MM-DD")
        sb = r.get("superseded_by")
        if sb and sb not in ids:
            errs.append(f"row {n} ({r.get('id','?')}): superseded_by {sb} does not exist")
    return errs


def render_md(rows: list[dict]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["binding_verdict"]] = counts.get(r["binding_verdict"], 0) + 1
    out = ["# LORE — the book of stories with their verdicts",
           "",
           "> GENERATED from `runtime/specs/lore.jsonl` by `scripts/lore.py render` — do not hand-edit.",
           "> LEGEND's uncle: LEGEND says what a word means; LORE says what we believe and why, including",
           "> what we stopped believing. A story is never deleted when its verdict flips; a new row is",
           "> added and the old one points forward. `undecided` may be told but not cited.",
           "",
           f"Rows: {len(rows)} · " + " · ".join(f"{k}: {v}" for k, v in sorted(counts.items())),
           ""]
    for r in rows:
        badge = {"true": "✓ TRUE", "durable-myth": "✖ DURABLE MYTH", "old-wives-tale": "✖ OLD WIVES' TALE", "undecided": "? UNDECIDED", "inspiration": "◇ INSPIRATION"}[r["binding_verdict"]]
        out += [f"## {r['id']} · {r['class'].upper()} · {badge}" + (f" · superseded by {r['superseded_by']}" if r.get("superseded_by") else ""),
                "",
                f"**Story.** {r['story']}",
                "",
                f"- **Told where:** {r['told_where']}",
                f"- **Observation (real):** {r['observation']}",
                f"- **Mechanism claimed:** {r['mechanism_claimed']}",
                f"- **Test that decided:** {r['test_that_decided'] or ('(a mood board: cite as aspiration, never as fact)' if r['binding_verdict']=='inspiration' else '(none yet; may be told, not cited)')}",
                f"- **Teaches:** {r['teaches']}",
                f"- **Date:** {r['date']} · **Refs:** " + (", ".join(f"`{x}`" for x in r["refs"]) if r["refs"] else "none"),
                ""]
    return "\n".join(out)


def cmd_render() -> int:
    rows = load(); errs = validate(rows)
    if errs:
        print("\n".join("✖ " + e for e in errs), file=sys.stderr); return 2
    RENDER.write_text(render_md(rows), encoding="utf-8")
    print(f"rendered {RENDER.relative_to(ROOT)} ({len(rows)} rows)"); return 0


def cmd_check() -> int:
    rows = load(); errs = validate(rows)
    if errs:
        print("\n".join("✖ " + e for e in errs), file=sys.stderr); return 1
    if not RENDER.exists() or RENDER.read_text(encoding="utf-8") != render_md(rows):
        print("✖ runtime/specs/LORE.md is stale vs lore.jsonl — run: python3 scripts/lore.py render", file=sys.stderr); return 1
    print(f"lore OK ({len(rows)} rows, render fresh)"); return 0


def cmd_tell(i: str) -> int:
    for r in load():
        if r["id"] == i:
            print(render_md([r])); return 0
    print(f"no such story: {i}"); return 1


def self_test() -> int:
    good = {"id": "lore-001", "class": "myth", "story": "s", "told_where": "t", "observation": "o", "mechanism_claimed": "m",
            "binding_verdict": "durable-myth", "test_that_decided": "the calculation", "teaches": "a lesson long enough to count",
            "date": "2026-09-27", "refs": [], "superseded_by": None}
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("good row passes", validate([good]) == [], validate([good]))
    check("verdict without a test is rejected", validate([dict(good, test_that_decided=None)]) != [])
    check("undecided without a test is allowed", validate([dict(good, binding_verdict="undecided", test_that_decided=None)]) == [])
    check("inspiration without a test is allowed (class aspiration)", validate([dict(good, **{"class": "aspiration"}, binding_verdict="inspiration", test_that_decided=None)]) == [])
    check("durable-myth on a non-myth class rejected", validate([dict(good, **{"class": "testimony"})]) != [])
    check("aspiration class must resolve to inspiration", validate([dict(good, **{"class": "aspiration"}, binding_verdict="true")]) != [])
    check("non-monotonic ids rejected (append-only)", validate([dict(good, id="lore-002"), dict(good, id="lore-001")]) != [])
    check("superseded_by must exist", validate([dict(good, superseded_by="lore-099")]) != [])
    check("supersession chain valid", validate([dict(good, superseded_by="lore-002"), dict(good, id="lore-002")]) == [])
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    if argv[0] == "--self-test":
        return self_test()
    if argv[0] == "render":
        return cmd_render()
    if argv[0] == "check":
        return cmd_check()
    if argv[0] == "tell" and len(argv) > 1:
        return cmd_tell(argv[1])
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
