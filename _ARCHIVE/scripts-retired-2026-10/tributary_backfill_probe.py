#!/usr/bin/env python3
"""tributary_backfill_probe.py: can Receipt.parentTributaryIndex be inferred for existing children? READ-ONLY.

Context (measured 2026-10-06, prod project xbbpiryokswwvcrcutge): 267 receipts, 107 with parentId
set, 0 with parentTributaryIndex. The compass only started recording the index on 2026-10-07
(feat(compass): record tributary follow-through); every earlier follow-up carries the lineage edge
and nothing else. A follow-up's decision text IS the parent's tributary prompt: the receipt and
brief pages hand the prompt to the dashboard as ?q= and the dashboard auto-runs it unedited
(src/app/dashboard/page.tsx, autoRanParent). So most children can be attributed by matching text.
This script measures how many. It never writes anything to any database.

Inputs (exactly one):
  --selftest            synthetic rows through the matcher, then the same rows through a throwaway
                        SQLite file to prove the --sqlite loader. Exit 1 on any mismatch.
  --sqlite PATH         a Prisma SQLite database (dev.db): reads "Receipt" directly.
  --export FILE.json    rows exported from Postgres with the query printed by --emit-sql, as a JSON
                        array of objects (what the Supabase connector returns; psql: wrap in json_agg).
  --emit-sql            print the Postgres export query and exit. The export carries decision text:
                        keep it in the session scratchpad, never commit it.

Outputs:
  a report on stdout: counts only, no decision text (unless --show-unmatched, which prints the first
  80 characters of each unmatched child and its closest prompt, for a human to eyeball).
  --json                the report as JSON instead of text.
  --plan FILE.sql       the UPDATE statements a backfill WOULD run, written to a local file for a
                        human to read and run (or not). This script executes none of them.

Matching, per child, against the parent's prompts (atgTributaries when stored, else the tributaries
array inside rawResponse, which is where /api/brief reads them for rows written before
atgTributaries existed):
  exact        decision == prompt, byte for byte
  normalized   equal after the same scrub the app applies on the way out and in: control characters
               removed and text clamped (src/lib/sanitize.ts clampText), spaced dashes turned into
               ": " / ", " (src/lib/prose.ts scrubDashes), curly quotes straightened, casefolded,
               whitespace collapsed
  prefix       one side hit its clamp length (prompt 1000 in atgTributaries, decision 4000) and the
               other side starts with it
  ambiguous    two or more prompts match equally: reported, never inferred
  near-miss    no match, but difflib ratio >= 0.85 against the closest prompt: reported, never inferred
  unmatched    everything else
A child whose parent has no parseable prompts is counted under no_prompts.

Usage:
  python3 scripts/tributary_backfill_probe.py --selftest
  python3 scripts/tributary_backfill_probe.py --emit-sql
  python3 scripts/tributary_backfill_probe.py --export /path/to/export.json [--json] [--plan plan.sql]
  python3 scripts/tributary_backfill_probe.py --sqlite prisma/dev.db
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

PROMPT_CLAMP = 1000      # compass route: clampText(o.prompt, 1000) into atgTributaries
DECISION_CLAMP = 4000    # compass route: clampText(question, 4000) into Receipt.decision
NEAR_MISS_RATIO = 0.85
MAX_INDEX = 2            # CompassBody.tributaryIndex: 0..2

# src/lib/sanitize.ts CONTROL_CHARS: C0 controls except tab/newline/CR, plus DEL.
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_DASH = re.compile(r"\s*[—―]\s*|\s+–\s+")
_COLON_PUNCT = re.compile(r": ([,.;:])")
_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})
_WS = re.compile(r"\s+")
_TRIB_ARRAY = re.compile(r'"tributaries"\s*:\s*(\[[^\]]*\])')

EXPORT_SQL = r'''
-- scripts/tributary_backfill_probe.py --emit-sql  (READ-ONLY; Postgres 16+ for pg_input_is_valid)
-- One row per child receipt with its parent's tributary prompts. Carries decision text:
-- keep the result out of git. Feed the JSON array to --export.
SELECT c.id                       AS child_id,
       c."parentId"               AS parent_id,
       c.decision,
       c."parentTributaryIndex"   AS parent_tributary_index,
       p."atgTributaries"         AS atg_tributaries,
       CASE WHEN p."atgTributaries" IS NULL THEN COALESCE(
         CASE WHEN pg_input_is_valid(p."rawResponse", 'jsonb')
              THEN (p."rawResponse"::jsonb -> 'tributaries')::text END,
         substring(p."rawResponse" from '"tributaries"\s*:\s*(\[[^\]]*\])')
       ) END                      AS raw_tributaries
FROM "Receipt" c
JOIN "Receipt" p ON p.id = c."parentId"
ORDER BY c."createdAt";
'''.strip()

SQLITE_SQL = '''
SELECT c.id AS child_id, c."parentId" AS parent_id, c.decision,
       c."parentTributaryIndex" AS parent_tributary_index,
       p."atgTributaries" AS atg_tributaries, p."rawResponse" AS raw_response
FROM "Receipt" c JOIN "Receipt" p ON p.id = c."parentId"
ORDER BY c."createdAt"
'''


# ----------------------------------------------------------------------------- text
def clamp(text: object, limit: int) -> str:
    """Mirror of clampText: drop control chars, slice, trim."""
    s = text if isinstance(text, str) else ("" if text is None else str(text))
    return _CONTROL.sub("", s)[:limit].strip()


def scrub_dashes(text: str) -> str:
    """Mirror of src/lib/prose.ts scrubDashes: first spaced dash -> ': ', later ones -> ', '."""
    seen = 0

    def repl(_m: re.Match) -> str:
        nonlocal seen
        seen += 1
        return ": " if seen == 1 else ", "

    return _COLON_PUNCT.sub(r"\1", _DASH.sub(repl, text))


def normalize(text: str) -> str:
    return _WS.sub(" ", scrub_dashes(_CONTROL.sub("", text)).translate(_QUOTES)).strip().casefold()


# ----------------------------------------------------------------------------- prompts
def _prompt_of(t: object) -> str | None:
    if isinstance(t, dict):
        for key in ("prompt", "text"):
            v = t.get(key)
            if isinstance(v, str) and v.strip():
                return v
        return None
    return t if isinstance(t, str) and t.strip() else None


def _loads_tributaries(blob: str) -> list | None:
    """Parse a JSON array, a full response object, or a fenced/prefixed response down to its tributaries."""
    blob = blob.strip()
    for candidate in (blob, re.sub(r"^```(?:json)?\s*|\s*```$", "", blob)):
        try:
            v = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(v, list):
            return v
        if isinstance(v, dict) and isinstance(v.get("tributaries"), list):
            return v["tributaries"]
    m = _TRIB_ARRAY.search(blob)
    if m:
        try:
            v = json.loads(m.group(1))
            return v if isinstance(v, list) else None
        except ValueError:
            return None
    return None


def parent_prompts(row: dict) -> tuple[list[str], str]:
    """(prompts, source) where source is 'atg', 'raw', or 'none'."""
    for key, source in (("atg_tributaries", "atg"), ("raw_tributaries", "raw"), ("raw_response", "raw")):
        blob = row.get(key)
        if not isinstance(blob, str) or not blob.strip():
            continue
        arr = _loads_tributaries(blob)
        if arr is None:
            continue
        prompts = [p for p in (_prompt_of(t) for t in arr) if p is not None]
        if prompts:
            return prompts, source
    return [], "none"


# ----------------------------------------------------------------------------- matcher
def infer(decision: str, prompts: list[str]) -> dict:
    """Return {'kind', 'index', 'ratio'}; index is set only for exact/normalized/prefix."""
    if not prompts:
        return {"kind": "no_prompts", "index": None, "ratio": None}
    d = clamp(decision, DECISION_CLAMP)
    nd = normalize(d)

    def pick(kind: str, hits: list[int]) -> dict | None:
        if len(hits) == 1:
            return {"kind": kind, "index": hits[0], "ratio": 1.0}
        if len(hits) > 1:
            return {"kind": "ambiguous", "index": None, "ratio": 1.0, "candidates": hits}
        return None

    r = pick("exact", [i for i, p in enumerate(prompts) if p == d])
    if r:
        return r
    normed = [normalize(clamp(p, PROMPT_CLAMP)) for p in prompts]
    r = pick("normalized", [i for i, n in enumerate(normed) if n == nd])
    if r:
        return r
    prefix_hits = []
    for i, p in enumerate(prompts):
        np_ = normed[i]
        prompt_clamped = len(clamp(p, PROMPT_CLAMP)) >= PROMPT_CLAMP
        decision_clamped = len(d) >= DECISION_CLAMP
        if (prompt_clamped and np_ and nd.startswith(np_)) or (decision_clamped and nd and np_.startswith(nd)):
            prefix_hits.append(i)
    r = pick("prefix", prefix_hits)
    if r:
        return r
    best_i, best = None, 0.0
    for i, n in enumerate(normed):
        ratio = difflib.SequenceMatcher(None, nd, n).ratio()
        if ratio > best:
            best_i, best = i, ratio
    kind = "near_miss" if best >= NEAR_MISS_RATIO else "unmatched"
    return {"kind": kind, "index": None, "ratio": round(best, 3), "closest": best_i}


INFERRED = ("exact", "normalized", "prefix")


def probe(rows: list[dict]) -> dict:
    kinds: Counter = Counter()
    by_index: Counter = Counter()
    source: Counter = Counter()
    details = []
    plan = []
    already = agree = disagree = out_of_range = 0
    for row in rows:
        prompts, src = parent_prompts(row)
        source[src] += 1
        res = infer(row.get("decision") or "", prompts)
        kind, idx = res["kind"], res["index"]
        if idx is not None and idx > MAX_INDEX:
            out_of_range += 1
            kind, idx = "out_of_range", None
        kinds[kind] += 1
        existing = row.get("parent_tributary_index")
        if existing is not None:
            already += 1
            if idx is not None:
                if idx == existing:
                    agree += 1
                else:
                    disagree += 1
        elif idx is not None:
            by_index[idx] += 1
            plan.append((row["child_id"], idx))
        closest = res.get("closest")
        details.append({
            "child_id": row.get("child_id"), "parent_id": row.get("parent_id"), "source": src, **res,
            # Text heads stay under private keys: --json drops them, --show-unmatched prints them.
            "_decision_head": (row.get("decision") or "")[:80],
            "_closest_head": prompts[closest][:80] if isinstance(closest, int) and closest < len(prompts) else "",
        })
    inferable = sum(kinds[k] for k in INFERRED)
    return {
        "children": len(rows),
        "parents": len({r.get("parent_id") for r in rows}),
        "prompt_source": dict(source),
        "inferable": inferable,
        "inferable_pct": round(100.0 * inferable / len(rows), 1) if rows else 0.0,
        "by_kind": dict(kinds),
        "by_index": {str(k): by_index[k] for k in sorted(by_index)},
        "already_set": {"rows": already, "matcher_agrees": agree, "matcher_disagrees": disagree},
        "out_of_range": out_of_range,
        "plan_updates": len(plan),
        "_plan": plan,
        "_details": details,
    }


# ----------------------------------------------------------------------------- io
def load_export(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and isinstance(data.get("result"), list):   # a saved connector envelope
        data = data["result"]
    if not isinstance(data, list):
        sys.exit(f"{path}: expected a JSON array of rows")
    return data


def load_sqlite(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"{path}: no such file")
    uri = f"file:{path}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(SQLITE_SQL)]
    finally:
        con.close()


def write_plan(path: Path, plan: list[tuple[str, int]]) -> None:
    lines = [
        "-- Proposed backfill of Receipt.parentTributaryIndex. Generated by scripts/tributary_backfill_probe.py.",
        "-- NOT executed by the script. Read the report first; run inside a transaction you can roll back.",
        "BEGIN;",
    ]
    for child_id, idx in plan:
        cid = child_id.replace("'", "''")
        lines.append(f'UPDATE "Receipt" SET "parentTributaryIndex" = {int(idx)} WHERE id = \'{cid}\' AND "parentTributaryIndex" IS NULL;')
    lines.append("-- COMMIT;  (uncomment after reading the row counts)")
    path.write_text("\n".join(lines) + "\n")


def render(report: dict, show_unmatched: bool) -> str:
    k = report["by_kind"]
    out = [
        f"children: {report['children']}  (distinct parents: {report['parents']})",
        f"prompt source: {report['prompt_source']}",
        f"inferable: {report['inferable']} / {report['children']} ({report['inferable_pct']}%)"
        f"  exact {k.get('exact', 0)} · normalized {k.get('normalized', 0)} · prefix {k.get('prefix', 0)}",
        f"by tributary index: {report['by_index'] or '{}'}",
        f"not inferred: ambiguous {k.get('ambiguous', 0)} · near-miss {k.get('near_miss', 0)}"
        f" · unmatched {k.get('unmatched', 0)} · no prompts {k.get('no_prompts', 0)} · out of range {report['out_of_range']}",
        f"already set: {report['already_set']}",
        f"backfill plan: {report['plan_updates']} UPDATE statements (written only with --plan)",
    ]
    if show_unmatched:
        out.append("-- unmatched / near-miss / ambiguous (first 80 chars) --")
        for d in report["_details"]:
            if d["kind"] in INFERRED:
                continue
            out.append(f"{d['child_id']}  {d['kind']}  ratio={d.get('ratio')}  closest={d.get('closest', d.get('candidates'))}")
            out.append(f"    decision: {d['_decision_head']!r}")
            if d["_closest_head"]:
                out.append(f"    closest : {d['_closest_head']!r}")
    return "\n".join(out)


# ----------------------------------------------------------------------------- selftest
def _synthetic_rows() -> tuple[list[dict], dict]:
    atg = json.dumps([
        {"type": "meta", "label": "Meta-Question", "prompt": "What am I really deciding here?"},
        {"type": "challenge", "label": "Need to Hear", "prompt": "Can the team survive a six month delay — honestly?"},
        {"type": "adjacent", "label": "Adjacent Lens", "prompt": "Which supplier contract has the same shape?"},
    ])
    raw = "```json\n" + json.dumps({
        "true_north": "x",
        "tributaries": [
            {"type": "meta", "label": "Meta-Question", "prompt": "Is this about the role or about leaving?"},
            {"type": "challenge", "label": "Need to Hear", "prompt": "Would I take it at the old salary?"},
            {"type": "adjacent", "label": "Adjacent Lens", "prompt": "What did the last move teach me?"},
        ],
    }) + "\n```"
    dup = json.dumps([{"prompt": "Same question twice"}, {"prompt": "Same question twice"}, {"prompt": "Other"}])
    long_prompt = "L" * 1200
    long_atg = json.dumps([{"prompt": long_prompt[:PROMPT_CLAMP]}, {"prompt": "b"}, {"prompt": "c"}])
    rows = [
        {"child_id": "c1", "parent_id": "p1", "decision": "What am I really deciding here?", "parent_tributary_index": None, "atg_tributaries": atg, "raw_response": None},
        {"child_id": "c2", "parent_id": "p1", "decision": "Can the team survive a six month delay: honestly?", "parent_tributary_index": None, "atg_tributaries": atg, "raw_response": None},
        {"child_id": "c3", "parent_id": "p1", "decision": "which supplier  contract has the same shape?", "parent_tributary_index": 2, "atg_tributaries": atg, "raw_response": None},
        {"child_id": "c4", "parent_id": "p2", "decision": "Would I take it at the old salary?", "parent_tributary_index": None, "atg_tributaries": None, "raw_response": raw},
        {"child_id": "c5", "parent_id": "p2", "decision": "Would I take it at the old salary, really?", "parent_tributary_index": None, "atg_tributaries": None, "raw_response": raw},
        {"child_id": "c6", "parent_id": "p2", "decision": "Should we rename the product?", "parent_tributary_index": None, "atg_tributaries": None, "raw_response": raw},
        {"child_id": "c7", "parent_id": "p3", "decision": "Same question twice", "parent_tributary_index": None, "atg_tributaries": dup, "raw_response": None},
        {"child_id": "c8", "parent_id": "p4", "decision": "Anything", "parent_tributary_index": None, "atg_tributaries": None, "raw_response": "not json at all"},
        {"child_id": "c9", "parent_id": "p5", "decision": long_prompt, "parent_tributary_index": None, "atg_tributaries": long_atg, "raw_response": None},
    ]
    expect = {
        "c1": ("exact", 0), "c2": ("normalized", 1), "c3": ("normalized", 2), "c4": ("exact", 1),
        "c5": ("near_miss", None), "c6": ("unmatched", None), "c7": ("ambiguous", None),
        "c8": ("no_prompts", None), "c9": ("prefix", 0),
    }
    return rows, expect


def selftest() -> int:
    rows, expect = _synthetic_rows()
    failures = []

    def check(label: str, report: dict) -> None:
        got = {d["child_id"]: (d["kind"], d["index"]) for d in report["_details"]}
        for cid, want in expect.items():
            if got.get(cid) != want:
                failures.append(f"{label}: {cid} expected {want}, got {got.get(cid)}")
        if report["inferable"] != 5:
            failures.append(f"{label}: inferable expected 5, got {report['inferable']}")
        if report["plan_updates"] != 4:   # c3 is already set, so it is not in the plan
            failures.append(f"{label}: plan expected 4 updates, got {report['plan_updates']}")
        if report["already_set"] != {"rows": 1, "matcher_agrees": 1, "matcher_disagrees": 0}:
            failures.append(f"{label}: already_set {report['already_set']}")
        if report["prompt_source"] != {"atg": 5, "raw": 3, "none": 1}:
            failures.append(f"{label}: prompt_source {report['prompt_source']}")

    check("rows", probe(rows))

    # Same rows through a throwaway Prisma-shaped SQLite file, to prove the --sqlite loader.
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "dev.db"
        con = sqlite3.connect(db)
        con.execute('CREATE TABLE "Receipt" (id TEXT PRIMARY KEY, "parentId" TEXT, decision TEXT NOT NULL, '
                    '"parentTributaryIndex" INTEGER, "atgTributaries" TEXT, "rawResponse" TEXT, "createdAt" TEXT NOT NULL)')
        parents = {}
        for r in rows:
            parents.setdefault(r["parent_id"], (r["atg_tributaries"], r["raw_response"]))
        for pid, (atg, raw) in parents.items():
            con.execute('INSERT INTO "Receipt" VALUES (?,?,?,?,?,?,?)', (pid, None, "seed", None, atg, raw, "2026-10-01"))
        for i, r in enumerate(rows):
            con.execute('INSERT INTO "Receipt" VALUES (?,?,?,?,?,?,?)',
                        (r["child_id"], r["parent_id"], r["decision"], r["parent_tributary_index"], None, None, f"2026-10-02T00:00:{i:02d}"))
        con.commit()
        con.close()
        check("sqlite", probe(load_sqlite(db)))
        plan_path = Path(tmp) / "plan.sql"
        write_plan(plan_path, probe(rows)["_plan"])
        if plan_path.read_text().count("UPDATE ") != 4:
            failures.append("plan file: expected 4 UPDATE lines")

    if failures:
        print("SELFTEST FAIL\n  " + "\n  ".join(failures))
        return 1
    print("SELFTEST OK: 9 synthetic rows, 5 inferable (exact 2, normalized 2, prefix 1), 4 not inferred, sqlite loader and plan writer agree")
    return 0


# ----------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--selftest", action="store_true")
    src.add_argument("--sqlite", metavar="PATH")
    src.add_argument("--export", metavar="FILE.json")
    src.add_argument("--emit-sql", action="store_true")
    ap.add_argument("--json", action="store_true", help="report as JSON")
    ap.add_argument("--plan", metavar="FILE.sql", help="write the proposed UPDATE statements here (never executed)")
    ap.add_argument("--show-unmatched", action="store_true", help="list unmatched/near-miss/ambiguous child ids")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.emit_sql:
        print(EXPORT_SQL)
        return 0
    rows = load_sqlite(Path(a.sqlite)) if a.sqlite else load_export(Path(a.export))
    report = probe(rows)
    if a.plan:
        write_plan(Path(a.plan), report["_plan"])
    if a.json:
        public = {k: v for k, v in report.items() if not k.startswith("_")}
        public["details"] = [{k: v for k, v in d.items() if not k.startswith("_")} for d in report["_details"]]
        print(json.dumps(public, indent=2))
    else:
        print(render(report, a.show_unmatched))
        if a.plan:
            print(f"plan written: {a.plan} ({report['plan_updates']} statements, not executed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
