#!/usr/bin/env python3
"""
legend.py — the LEGEND: ARCS's working dictionary (acronyms + terms), as data.

Tier model (Zach, 2026-09-27: "bank all these to RAM / ROM / LEGEND so we're working off the
same dictionary / encyclopedia / thesaurus and books of proverbs"):
  RAM     a term used in one session (chat, scratch) — not banked
  LEGEND  runtime/specs/legend.jsonl — banked, gated, append-mostly; the shared dictionary
  ROM     _CANON/ordinals/* — immutable chained vocabulary; MINTED UPSTREAM by the primary
          disciple, this repo only inscribes (see _CANON/ordinals/README.md). Ordinal
          candidates are CUT FROM the LEGEND; the LEGEND never pretends to be an ordinal.
The four books: dictionary = this LEGEND · encyclopedia = _CANON · thesaurus = _SEEDS alias
index + folksonomy · proverbs = _CANON/tao-proverbs.jsonl.

Row schema (runtime/specs/legend.jsonl, one JSON object per line):
  term                  canonical spelling (acronym in caps, or the term as written)
  kind                  "acronym" | "term"
  expansion             what the letters stand for (acronym) or one-line gloss (term)
  operational_definition what it DOES / how you'd recognise it — the clause Zach can hold and reuse
  domain                "arcs" | "engineering" | "finance" | "ops" | ...
  aliases               [] other spellings that resolve to this row
  source                where it is defined authoritatively (path or ordinal), or "session:<date>"
  first_seen            YYYY-MM-DD
  promoted_to           null | ordinal id / ADR when it graduates out of the LEGEND

Usage:
  python3 scripts/legend.py lookup <term>        # print the row (aliases + case-insensitive)
  python3 scripts/legend.py scan <file|->        # acronyms in a text that the LEGEND lacks
  python3 scripts/legend.py render               # regenerate runtime/specs/LEGEND.md
  python3 scripts/legend.py check                # gate: schema, uniqueness, render freshness
  python3 scripts/legend.py --self-test          # proves check fails-on-bad and passes-on-good
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "runtime" / "specs" / "legend.jsonl"
RENDER = ROOT / "runtime" / "specs" / "LEGEND.md"

REQUIRED = ("term", "kind", "expansion", "operational_definition", "domain", "aliases", "source", "first_seen")
KINDS = {"acronym", "term"}
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,7}(?:-[A-Z0-9]{1,6})?\b")
# common words / non-terms the scanner should ignore
SCAN_IGNORE = {"I", "A", "OK", "TODO", "NOTE", "JSON", "JSONL", "HTML", "CSS", "URL", "HTTP", "HTTPS",
               "API", "CLI", "SQL", "ID", "UTC", "EOF", "PASS", "FAIL", "READY", "PARTIAL", "BLOCKED",
               "UNBUILT", "DRIFT", "STALE", "GREEN", "YELLOW", "RED", "FORK", "SCRATCH", "DELTA",
               "PARADOX", "MOIRE", "SHARP", "GRAIN", "DEGRADED", "LOCKED", "OPEN", "CLOSED", "DONE",
               "ZH", "PR", "CI", "MD", "PY", "TS", "TSX", "NY", "US", "UK", "AM", "PM", "GB", "KB", "MB"}


def load() -> list[dict]:
    if not DATA.exists():
        return []
    rows = []
    for i, line in enumerate(DATA.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SystemExit(f"legend.jsonl line {i}: invalid JSON ({e})")
    return rows


def index(rows: list[dict]) -> dict[str, dict]:
    ix: dict[str, dict] = {}
    for r in rows:
        ix[r["term"].lower()] = r
        for a in r.get("aliases", []):
            ix[a.lower()] = r
    return ix


def validate(rows: list[dict]) -> list[str]:
    errs: list[str] = []
    seen: dict[str, str] = {}
    for n, r in enumerate(rows, 1):
        for k in REQUIRED:
            if k not in r or r[k] in ("", None) and k != "aliases":
                errs.append(f"row {n} ({r.get('term','?')}): missing {k}")
        if r.get("kind") not in KINDS:
            errs.append(f"row {n} ({r.get('term','?')}): kind must be one of {sorted(KINDS)}")
        od = r.get("operational_definition", "")
        if len(od) < 25:
            errs.append(f"row {n} ({r.get('term','?')}): operational_definition too thin (<25 chars) — say what it DOES")
        if r.get("kind") == "acronym" and r.get("expansion", "").upper() == r.get("term", "").upper():
            errs.append(f"row {n} ({r.get('term','?')}): acronym expansion just repeats the acronym")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("first_seen", ""))):
            errs.append(f"row {n} ({r.get('term','?')}): first_seen must be YYYY-MM-DD")
        for key in [r.get("term", "")] + list(r.get("aliases", [])):
            k = key.lower()
            if k in seen and seen[k] != r.get("term"):
                errs.append(f"row {n}: '{key}' collides with row for '{seen[k]}'")
            seen[k] = r.get("term", "")
    return errs


def render_md(rows: list[dict]) -> str:
    acr = sorted((r for r in rows if r["kind"] == "acronym"), key=lambda r: r["term"].lower())
    terms = sorted((r for r in rows if r["kind"] == "term"), key=lambda r: r["term"].lower())
    out = ["# LEGEND — the ARCS working dictionary",
           "",
           "> GENERATED from `runtime/specs/legend.jsonl` by `scripts/legend.py render` — do not hand-edit.",
           "> Tier: **LEGEND** (between RAM and the ordinals). Ordinal candidates are cut from here; the",
           "> ordinal chain itself is minted upstream (`_CANON/ordinals/README.md`). Rule of use: every",
           "> acronym gets its expansion + operational definition in parentheses on first use, every message",
           "> (memory `always-expand-acronyms-with-operational-definition`). `python3 scripts/legend.py lookup <term>`.",
           "",
           f"Rows: {len(rows)} ({len(acr)} acronyms · {len(terms)} terms).",
           "",
           "## Acronyms",
           "",
           "| Acronym | Expansion | Operational definition | Domain | Source |",
           "|---|---|---|---|---|"]
    for r in acr:
        out.append(f"| **{r['term']}** | {r['expansion']} | {r['operational_definition']} | {r['domain']} | `{r['source']}` |")
    out += ["", "## Terms", "", "| Term | Gloss | Operational definition | Domain | Source |", "|---|---|---|---|---|"]
    for r in terms:
        al = f" (aka {', '.join(r['aliases'])})" if r.get("aliases") else ""
        out.append(f"| **{r['term']}**{al} | {r['expansion']} | {r['operational_definition']} | {r['domain']} | `{r['source']}` |")
    out.append("")
    return "\n".join(out)


def cmd_lookup(q: str) -> int:
    ix = index(load())
    r = ix.get(q.lower())
    if not r:
        print(f"not in LEGEND: {q}  (add a row to runtime/specs/legend.jsonl, then `legend.py render`)")
        return 1
    print(f"{r['term']} ({r['expansion']}: {r['operational_definition']})")
    print(f"  kind={r['kind']} domain={r['domain']} source={r['source']} first_seen={r['first_seen']}"
          + (f" promoted_to={r['promoted_to']}" if r.get('promoted_to') else ""))
    return 0


def cmd_scan(path: str) -> int:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8", errors="replace")
    ix = index(load())
    lower_words = set(re.findall(r"\b[a-z][a-z0-9]+\b", text))   # a caps token whose lowercase twin appears is shouting, not an acronym
    ref_re = re.compile(r"^(ADR|PR|F|L|OP|RC|NCI|P)-?\d")            # ADR-023, L0, F32, P1 are refs, not acronyms
    found = sorted({m for m in ACRONYM_RE.findall(text)
                    if m not in SCAN_IGNORE and m.lower() not in ix
                    and m.lower() not in lower_words and not ref_re.match(m)})
    if found:
        print("acronyms not in LEGEND: " + ", ".join(found))
        return 1
    print("scan OK: every acronym present is in the LEGEND")
    return 0


def cmd_render() -> int:
    rows = load()
    errs = validate(rows)
    if errs:
        print("\n".join("✖ " + e for e in errs), file=sys.stderr)
        return 2
    RENDER.write_text(render_md(rows), encoding="utf-8")
    print(f"rendered {RENDER.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


def cmd_check() -> int:
    rows = load()
    errs = validate(rows)
    if errs:
        print("\n".join("✖ " + e for e in errs), file=sys.stderr)
        return 1
    if not RENDER.exists() or RENDER.read_text(encoding="utf-8") != render_md(rows):
        print("✖ runtime/specs/LEGEND.md is stale vs legend.jsonl — run: python3 scripts/legend.py render", file=sys.stderr)
        return 1
    print(f"legend OK ({len(rows)} rows, render fresh)")
    return 0


def self_test() -> int:
    good = [{"term": "CPM", "kind": "acronym", "expansion": "critical path method",
             "operational_definition": "find the longest chain of dependent steps; it sets the minimum cost",
             "domain": "ops", "aliases": [], "source": "session:2026-09-27", "first_seen": "2026-09-27", "promoted_to": None}]
    assert validate(good) == [], validate(good)
    bad_thin = [dict(good[0], operational_definition="too short")]
    bad_dup = good + [dict(good[0], term="cpm")]
    bad_kind = [dict(good[0], kind="thing")]
    bad_exp = [dict(good[0], expansion="CPM")]
    fails = 0
    for label, rows in (("thin definition", bad_thin), ("duplicate term", bad_dup), ("bad kind", bad_kind), ("expansion repeats acronym", bad_exp)):
        ok = bool(validate(rows))
        print(f"  {'PASS' if ok else 'FAIL'}  check rejects: {label}")
        fails += 0 if ok else 1
    print(f"  PASS  check accepts: good row")
    ix = index(good)
    ok = ix.get("cpm") is good[0]
    print(f"  {'PASS' if ok else 'FAIL'}  lookup is case-insensitive"); fails += 0 if ok else 1
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    if argv[0] == "--self-test":
        return self_test()
    cmd, args = argv[0], argv[1:]
    if cmd == "lookup" and args:
        return cmd_lookup(" ".join(args))
    if cmd == "scan" and args:
        return cmd_scan(args[0])
    if cmd == "render":
        return cmd_render()
    if cmd == "check":
        return cmd_check()
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
