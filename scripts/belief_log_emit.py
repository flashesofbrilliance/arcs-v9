#!/usr/bin/env python3
"""belief_log_emit.py — render the consolidated ARCS belief-change log.

Reads the append-only falsification ledger (_STATE/falsification-ledger.jsonl)
and emits two distilled views of the corpus record of every belief we held, the
test that overturned it, and what replaced it — newest first, trailing-week
spotlighted:
  - _STATE/belief-log.md    — the readable markdown view
  - _STATE/belief-log.html  — the ARCS Observatory "drift ribbon" view, produced
                              by injecting the ledger into scripts/belief_log_template.html
  - public/belief-log.html  — the public projection (shape only; see PUBLIC_EMBED_KEYS)
  - public/good-agent-receipts-audit.html — NOT regenerated; only the block between
                              AUDIT_STAMP_START / AUDIT_STAMP_END is re-stamped with the
                              falsified count + latest date, so the public offer page can
                              never quietly outrun the ledger (--check covers it too)

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

import projection_factory as pf  # the reusable public-projection base (load + inject)

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
# The audit offer page carries ONE stamped sentence (count + latest date). The
# markers bound the only bytes this script may touch on that page; everything
# else there is hand-authored prose and stays that way.
AUDIT_PAGE = ROOT / "public" / "good-agent-receipts-audit.html"
AUDIT_STAMP_START = "<!--ledger-stamp:start-->"
AUDIT_STAMP_END = "<!--ledger-stamp:end-->"
# The audit page's evidence ledger (case_evidence_lint) must cover every digit on
# the page, so the stamp's evidence row is regenerated with it: the line right
# after EVIDENCE_MARKER is owned by this script; every other line is hand-kept.
AUDIT_EVIDENCE = ROOT / "public" / "good-agent-receipts-audit.evidence.jsonl"
EVIDENCE_MARKER = "# ledger-stamp:"

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
    """Validate + read the ledger via the shared factory base (byte-for-byte the
    same contract this file used to inline: required-key, date, and dup-id checks)."""
    return pf.load(path, REQUIRED_KEYS, id_key="id", date_key="ts")


def _inject(template_path: pathlib.Path, rows: list[dict], keys: tuple[str, ...]) -> str:
    """Inject a keyed projection of the ledger (oldest-first, as the page JS
    expects) into a template — the reusable lawful transform. `<` is escaped so no
    field can break out of the <script> tag; only `keys` are embedded (the air-gap
    for the public file). This file keeps its own `/*BELIEF_DATA*/` marker so its
    output stays byte-identical to the pre-factory version."""
    return pf.inject(template_path, rows, keys, marker=DATA_MARKER, sort_keys=("ts", "id"))


def render_html(rows: list[dict]) -> str:
    return _inject(TEMPLATE, rows, EMBED_KEYS)


def render_public(rows: list[dict]) -> str:
    return _inject(PUBLIC_TEMPLATE, rows, PUBLIC_EMBED_KEYS)


def render_audit_stamp(rows: list[dict]) -> str:
    """The one sentence stamped into the audit offer page: how many beliefs the
    ledger has falsified and the date of the most recent one. Counts only rows
    whose verdict is FALSIFIED (a future HELD fate must not inflate it)."""
    n, latest = audit_stamp_facts(rows)
    noun = "belief" if n == 1 else "beliefs"
    return (f'<p><b>{n}</b> {noun} we held and later falsified are on the record, '
            f'the most recent on <b style="white-space:nowrap">{latest}</b>.</p>')


def audit_stamp_facts(rows: list[dict]) -> tuple[int, str]:
    falsified = [r for r in rows if r["verdict"] == "FALSIFIED"]
    return len(falsified), (max(r["ts"] for r in falsified) if falsified else "none yet")


def render_audit_evidence(rows: list[dict]) -> str:
    """Rewrite the one generated row of the audit page's evidence ledger so the
    stamped sentence traces, verbatim, to the belief log's own summary line."""
    if not AUDIT_EVIDENCE.exists():
        sys.exit(f"AUDIT FAIL: {AUDIT_EVIDENCE.relative_to(ROOT)} not found.")
    n, latest = audit_stamp_facts(rows)
    md_line = render_md(rows).splitlines()[6]  # the "**N beliefs overturned** · ..." line
    row = {
        "pattern": rf"{n}\s+beliefs we held|most recent on {latest}",
        "kind": "fact",
        "page": f"{n} beliefs we held and later falsified are on the record, the most recent on {latest}",
        "source": OUT.relative_to(ROOT).as_posix(),
        "quote": md_line.lstrip("*"),
        "note": "count = ledger rows with verdict FALSIFIED; date = the latest of them. Stamped, not typed.",
    }
    lines = AUDIT_EVIDENCE.read_text(encoding="utf-8").splitlines()
    idx = [i for i, ln in enumerate(lines) if ln.startswith(EVIDENCE_MARKER)]
    if len(idx) != 1 or idx[0] + 1 >= len(lines):
        sys.exit(f"AUDIT FAIL: {AUDIT_EVIDENCE.name} must carry exactly one '{EVIDENCE_MARKER}' "
                 f"line followed by its generated row.")
    lines[idx[0] + 1] = json.dumps(row, ensure_ascii=False)
    return "\n".join(lines) + "\n"


def render_audit(rows: list[dict]) -> str:
    """Re-stamp the marked block of the (hand-authored) audit page. Fails loudly
    if the markers are missing, so a rewrite of that page cannot silently drop
    the count."""
    if not AUDIT_PAGE.exists():
        sys.exit(f"AUDIT FAIL: {AUDIT_PAGE.relative_to(ROOT)} not found.")
    page = AUDIT_PAGE.read_text(encoding="utf-8")
    a, b = page.find(AUDIT_STAMP_START), page.find(AUDIT_STAMP_END)
    if a < 0 or b < 0 or b < a or page.count(AUDIT_STAMP_START) != 1 or page.count(AUDIT_STAMP_END) != 1:
        sys.exit(f"AUDIT FAIL: {AUDIT_PAGE.name} must carry exactly one "
                 f"{AUDIT_STAMP_START} … {AUDIT_STAMP_END} block.")
    a += len(AUDIT_STAMP_START)
    return page[:a] + render_audit_stamp(rows) + page[b:]


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
        (AUDIT_PAGE, render_audit(rows)),   # good.arcs.care/audit: count + latest date only
        (AUDIT_EVIDENCE, render_audit_evidence(rows)),  # its evidence row, same facts
    ]

    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, view in outputs
                 if (p.read_text(encoding="utf-8") if p.exists() else "") != view]
        if stale:
            print(f"DRIFT: {', '.join(stale)} stale — run `python3 scripts/belief_log_emit.py`.")
            return 1
        print(f"OK — belief-log.md + .html + public mirror + audit stamp current ({len(rows)} entries).")
        return 0

    for p, view in outputs:
        p.write_text(view, encoding="utf-8")
    print(f"wrote belief-log.md + .html + public/belief-log.html + audit stamp — {len(rows)} entries (audit clean).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
