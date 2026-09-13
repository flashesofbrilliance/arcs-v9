#!/usr/bin/env python3
"""Perplexity scout intake: validate a role dossier in _INBOX/evidence/ and map it onto the jobs board.

stdlib only. The dossier contract is _INBOX/evidence/role-dossier-schema.json (v1). This script is
the drift gate between the Scout (Perplexity) and the board (jobs.arcs.care): a dossier that does
not satisfy the contract is refused, never silently coerced.

  validate <dossier.json> [...]      structural check against the schema's own required/enum/const
                                     fields + the HITL invariant (UNDECIDABLE => human_premortem_required)
  map      <dossier.json> [...]      print the board row(s) the dossier would become (dry run)
  post     <dossier.json> [...]      validate + map + POST to https://jobs.arcs.care/api/jobs
                                     (source=perplexity_scout, band=UNSCORED; skips existing jobids)

Board row shape mirrors src/app/api/jobs/route.ts. Verdict label + rationale land in unscoredWhy,
evidence claim_ids in jdHits, so the scorer and the human see the Scout's basis, not a score.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "_INBOX" / "evidence" / "role-dossier-schema.json"
BOARD = "https://jobs.arcs.care/api/jobs"
UA = {"User-Agent": "ARCS scout-dossier-ingest"}


def _check(obj, schema, path, errs):
    """Minimal JSON-schema walker: type / required / enum / const / properties / items / format(date)."""
    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        ok = any(
            (ty == "object" and isinstance(obj, dict)) or (ty == "array" and isinstance(obj, list)) or
            (ty == "string" and isinstance(obj, str)) or (ty == "boolean" and isinstance(obj, bool)) or
            (ty == "number" and isinstance(obj, (int, float)) and not isinstance(obj, bool)) or
            (ty == "integer" and isinstance(obj, int) and not isinstance(obj, bool)) or
            (ty == "null" and obj is None)
            for ty in types)
        if not ok:
            errs.append(f"{path}: expected {types}, got {type(obj).__name__}")
            return
    if "const" in schema and obj != schema["const"]:
        errs.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} not in {schema['enum']}")
    if schema.get("format") == "date" and isinstance(obj, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", obj):
        errs.append(f"{path}: not a YYYY-MM-DD date: {obj!r}")
    if schema.get("format") == "date-time" and isinstance(obj, str) and not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", obj):
        errs.append(f"{path}: not a date-time: {obj!r}")
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}: missing required '{k}'")
        for k, sub in (schema.get("properties") or {}).items():
            if k in obj:
                _check(obj[k], sub, f"{path}.{k}", errs)
    if isinstance(obj, list) and "items" in schema:
        for i, it in enumerate(obj):
            _check(it, schema["items"], f"{path}[{i}]", errs)


def validate(d: dict, schema: dict) -> list[str]:
    errs: list[str] = []
    _check(d, schema, "$", errs)
    v = d.get("verdict") or {}
    if v.get("label") == "UNDECIDABLE" and v.get("human_premortem_required") is not True:
        errs.append("$.verdict: label UNDECIDABLE requires human_premortem_required=true (HITL invariant)")
    # every evidence field_ref must point at a key that exists in the dossier
    for i, e in enumerate(d.get("evidence") or []):
        ref = e.get("field_ref", "")
        cur = d
        for part in ref.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                errs.append(f"$.evidence[{i}].field_ref '{ref}' does not resolve in the dossier")
                break
    return errs


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def to_row(d: dict) -> dict:
    c = d["core"]
    v = d.get("verdict") or {}
    ev = d.get("evidence") or []
    url = c["jd_url"]
    why = f"scout verdict {v.get('label')}" + (" (human premortem required)" if v.get("human_premortem_required") else "")
    if v.get("rationale"):
        why += f": {v['rationale']}"
    return {
        "jobid": f"scout-{slug(c['company'])}-{hashlib.sha1(url.encode()).hexdigest()[:8]}",
        "title": c["role_title"],
        "company": c["company"],
        "location": (d.get("extension") or {}).get("location") or None,
        "url": url,
        "source": "perplexity_scout",
        "band": "UNSCORED",
        "unscoredWhy": why[:1000],
        "jdHits": [e.get("claim_id") for e in ev if e.get("claim_id")],
        "firstSeen": (c.get("posting_first_seen") or d.get("generated_at") or "")[:10] or None,
        "nextStep": "Scout dossier landed; run the rubric scorer, then human premortem if flagged.",
        "contactType": "dossier",
        "contactDetail": d.get("dossier_id"),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("validate", "map", "post"):
        sys.exit(__doc__)
    schema = json.loads(SCHEMA.read_text())
    rows, bad = [], 0
    for p in argv[1:]:
        d = json.loads(Path(p).read_text())
        errs = validate(d, schema)
        if errs:
            bad += 1
            print(f"INVALID {p}:", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            continue
        print(f"valid   {p}  ({d.get('dossier_id')}, verdict={d.get('verdict', {}).get('label')})", file=sys.stderr)
        if argv[0] != "validate":
            rows.append(to_row(d))
    if argv[0] == "map":
        print(json.dumps(rows, indent=1))
    elif argv[0] == "post" and rows:
        token = os.environ.get("JOBS_PIPELINE_TOKEN")
        if not token:
            sys.exit("JOBS_PIPELINE_TOKEN missing: set -a; . ~/.arcs/jobs-pipeline.env; set +a")
        hdr = {**UA, "Content-Type": "application/json", "x-jobs-token": token}
        with urllib.request.urlopen(urllib.request.Request(BOARD, headers=hdr), timeout=120) as r:
            existing = {x["jobid"] for x in json.loads(r.read())["rows"]}
        new = [r for r in rows if r["jobid"] not in existing]
        print(f"post: {len(rows) - len(new)} already on board, {len(new)} new", file=sys.stderr)
        if new:
            req = urllib.request.Request(BOARD, data=json.dumps(new).encode(), headers=hdr, method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                print(r.read().decode(), file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
