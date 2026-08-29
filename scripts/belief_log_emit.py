#!/usr/bin/env python3
"""belief_log_emit.py — render the consolidated ARCS belief-change log.

Reads the append-only falsification ledger (_STATE/falsification-ledger.jsonl)
and emits two distilled views of the corpus record of every belief we held, the
test that overturned it, and what replaced it — newest first, trailing-week
spotlighted:
  - _STATE/belief-log.md    — the readable markdown view
  - _STATE/belief-log.html  — the ARCS Observatory "drift ribbon" view, produced
                              by injecting the ledger into scripts/belief_log_template.html

The ledger is the SSOT; both files are lawful transforms of it (WORLD.md §Field
Geometry). Never hand-edit either — regenerate:

    python3 scripts/belief_log_emit.py            # writes both views
    python3 scripts/belief_log_emit.py --check     # audit only, no write (exit 1 on drift)

stdlib-only (foundation rule). Deterministic: same ledger -> byte-identical views.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "_STATE" / "falsification-ledger.jsonl"
OUT = ROOT / "_STATE" / "belief-log.md"
OUT_HTML = ROOT / "_STATE" / "belief-log.html"
OUT_PUBLIC = ROOT / "public" / "belief-log.html"
TEMPLATE = ROOT / "scripts" / "belief_log_template.html"
PUBLIC_TEMPLATE = ROOT / "scripts" / "belief_log_public_template.html"
DATA_MARKER = "/*BELIEF_DATA*/"
EMBED_KEYS = ("id", "scope", "ts", "claim", "test", "delta", "fix", "confidence", "canon", "refs")
# The PUBLIC projection (status.arcs.care) embeds ONLY the shape — never the
# claim/test/delta/fix/refs prose. This whitelist is the air-gap: internal text
# structurally cannot reach the public file because it is never embedded.
PUBLIC_EMBED_KEYS = ("id", "scope", "ts", "canon")

REQUIRED_KEYS = {"id", "scope", "ts", "claim", "test", "verdict", "delta", "fix", "confidence", "refs", "canon"}
WEEK_DAYS = 7


def first_clause(text: str, cap: int = 160) -> str:
    """First sentence, split on sentence boundaries only (never mid-token like
    'Next.js' or a decimal), with a word-safe length cap as backstop."""
    head = text.split(". ", 1)[0].rstrip(".").strip()
    if len(head) > cap:
        head = head[:cap].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return head


def load(path: pathlib.Path) -> list[dict]:
    rows: list[dict] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"AUDIT FAIL: line {n} is not valid JSON: {e}")
        missing = REQUIRED_KEYS - d.keys()
        if missing:
            sys.exit(f"AUDIT FAIL: entry {d.get('id', '?')} (line {n}) missing keys: {sorted(missing)}")
        dt.date.fromisoformat(d["ts"])  # raises on malformed date
        rows.append(d)
    ids = [r["id"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"AUDIT FAIL: duplicate ledger ids: {dupes}")
    return rows


def _inject(template_path: pathlib.Path, rows: list[dict], keys: tuple[str, ...]) -> str:
    """Inject a keyed projection of the ledger (oldest-first, as the page JS
    expects) into a template. `<` is escaped so no field can break out of the
    <script> tag; only `keys` are embedded (the air-gap for the public file)."""
    ordered = sorted(rows, key=lambda r: (r["ts"], r["id"]))
    data = [{k: r[k] for k in keys} for r in ordered]
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = template_path.read_text(encoding="utf-8")
    if DATA_MARKER not in template:
        sys.exit(f"AUDIT FAIL: {template_path.name} is missing the {DATA_MARKER} injection marker.")
    return template.replace(DATA_MARKER, blob)


def render_html(rows: list[dict]) -> str:
    return _inject(TEMPLATE, rows, EMBED_KEYS)


def render_public(rows: list[dict]) -> str:
    return _inject(PUBLIC_TEMPLATE, rows, PUBLIC_EMBED_KEYS)


def render_md(rows: list[dict]) -> str:
    rows = sorted(rows, key=lambda r: (r["ts"], r["id"]), reverse=True)
    latest = dt.date.fromisoformat(rows[0]["ts"])
    week_floor = latest - dt.timedelta(days=WEEK_DAYS - 1)
    week = [r for r in rows if dt.date.fromisoformat(r["ts"]) >= week_floor]

    scopes: dict[str, int] = {}
    canon = 0
    for r in rows:
        scopes[r["scope"]] = scopes.get(r["scope"], 0) + 1
        canon += 1 if r["canon"] else 0
    scope_line = " · ".join(f"{k} {v}" for k, v in sorted(scopes.items(), key=lambda kv: (-kv[1], kv[0])))

    L: list[str] = []
    L.append("# ARCS — Belief-Change Log")
    L.append("")
    L.append("> The corpus record of what we believed, the test that overturned it, and what replaced it.")
    L.append("> One field, one SSOT: **generated from `_STATE/falsification-ledger.jsonl`** by")
    L.append("> `scripts/belief_log_emit.py`. Do not hand-edit — append to the ledger and regenerate.")
    L.append("")
    L.append(f"**{len(rows)} beliefs overturned** · {canon} promoted to canon · "
             f"span {rows[-1]['ts']} → {rows[0]['ts']}")
    L.append("")
    L.append(f"By scope: {scope_line}")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"## This week — spotlight ({week_floor.isoformat()} → {latest.isoformat()})")
    L.append("")
    if week:
        L.append("The reversals that went most against the grain this week:")
        L.append("")
        for r in week:
            L.append(f"### {r['id']} · {r['ts']} · `{r['scope']}`{'  — CANON' if r['canon'] else ''}")
            L.append(f"- **Held:** {r['claim']}")
            L.append(f"- **Test:** {r['test']}")
            L.append(f"- **{r['verdict']} →** {r['delta']}")
            L.append(f"- **Now:** {r['fix']}")
            L.append(f"- _refs: {', '.join(r['refs'])} · confidence: {r['confidence']}_")
            L.append("")
    else:
        L.append("_No entries in the trailing week._")
        L.append("")
    L.append("---")
    L.append("")
    L.append("## Full ledger — newest first")
    L.append("")
    L.append("| id | date | scope | canon | belief that broke → what replaced it |")
    L.append("|----|------|-------|-------|--------------------------------------|")
    for r in rows:
        claim = first_clause(r["claim"])
        fix = first_clause(r["fix"])
        cell = f"**{claim}** → {fix}".replace("|", "\\|").replace("\n", " ")
        L.append(f"| {r['id']} | {r['ts']} | {r['scope']} | {'✓' if r['canon'] else '—'} | {cell} |")
    L.append("")
    L.append("---")
    L.append(f"_Regenerated by `scripts/belief_log_emit.py` · {len(rows)} entries · "
             f"do not hand-edit — the ledger is the SSOT._")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="audit + verify OUT is current; no write")
    args = ap.parse_args()

    rows = load(LEDGER)
    outputs = [
        (OUT, render_md(rows)),
        (OUT_HTML, render_html(rows)),
        (OUT_PUBLIC, render_public(rows)),  # status.arcs.care mirror (shape only)
    ]

    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, view in outputs
                 if (p.read_text(encoding="utf-8") if p.exists() else "") != view]
        if stale:
            print(f"DRIFT: {', '.join(stale)} stale — run `python3 scripts/belief_log_emit.py`.")
            return 1
        print(f"OK — belief-log.md + .html + public mirror current ({len(rows)} entries).")
        return 0

    for p, view in outputs:
        p.write_text(view, encoding="utf-8")
    print(f"wrote belief-log.md + .html + public/belief-log.html — {len(rows)} entries (audit clean).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
