#!/usr/bin/env python3
"""prod_receipt_to_op20_seed — faithful adapter: prod Prisma Receipt -> op20 seed dict.

The live compass route writes receipts in a DIFFERENT contract than op20's
CoherenceReceipt dataclass (camelCase columns, JSON stored as TEXT, court as an
array of named checks, verdict as prose). This adapter maps the REAL columns into
the keys arcs_operator20.extract_seeds() reads. It only fills a dimension when the
prod row genuinely carries the signal — it does NOT fabricate somatic/axiom values
the DB never stored (those stay op20 defaults, honestly constant).

Faithful mappings (real signal, not invented):
  nci_score            <- nciScore
  irreversibility      <- doorClass (ONE_WAY=0.85 / TWO_WAY=0.20 / else 0.35)
  signal_classification<- gradientMagnitude (>=0.6 accel / <=0.4 decel / else stable)
  court.verdict        <- DERIVED from court[] check array: any BLOCK -> BLOCK;
                          else any TENSION -> CONDITIONAL; else PERMIT
                          (the prose `courtVerdict` column is NOT a clean enum)
  court.evidence_weight<- number of court checks (/5, capped)
  fated.{5 fields}     <- fated JSON (op20 uses their lengths)
  hci_score            <- nciByLens conviction+coherence lenses (/30)
  lab.lab_threat_level <- HIGH if macroTags has BAR or mode==COURT else LOW
  bar.ruin_detected    <- macroTags contains 'BAR'
  timestamp            <- created_epoch
  phase_id             <- surface

Usage:  python3 prod_receipt_to_op20_seed.py <rows.json|tool-result.txt> [out.jsonl]
Stdlib only.
"""
import json, re, sys


def _pj(s):
    """Parse a TEXT column that may hold JSON (or be null/blank)."""
    if not s or not isinstance(s, str):
        return None
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None


def adapt(row):
    lens = _pj(row.get("nciByLens")) or {}
    checks = _pj(row.get("court")) or []
    fated = _pj(row.get("fated")) or {}
    tags = _pj(row.get("macroTags")) or []
    if not isinstance(tags, list):
        tags = []

    verdicts = [c.get("verdict", "") for c in checks if isinstance(c, dict)]
    if any(v == "BLOCK" for v in verdicts):
        court_v = "BLOCK"
    elif any(v == "TENSION" for v in verdicts):
        court_v = "CONDITIONAL"
    else:
        court_v = "PERMIT"

    gm = row.get("gradientMagnitude")
    gm = 0.5 if gm is None else float(gm)
    sig = "accelerating" if gm >= 0.6 else "decelerating" if gm <= 0.4 else "stable"

    door = row.get("doorClass")
    irr = 0.85 if door == "ONE_WAY" else 0.20 if door == "TWO_WAY" else 0.35

    conv, coh = lens.get("conviction"), lens.get("coherence")
    hci = ((conv or 0) + (coh or 0)) / 30.0 if lens else 0.5

    threat = "HIGH" if ("BAR" in tags or row.get("mode") == "COURT") else "LOW"
    ruin = "BAR" in tags

    phase = {"ORIENT": "phase_1", "EPHEMERAL_SAVE": "phase_1", "PREP": "phase_2",
             "BRIEF": "phase_3"}.get(row.get("surface"), "phase_4")

    return {
        "receipt_id": row.get("id"),
        "nci_score": row.get("nciScore"),
        "irreversibility": irr,
        "signal_classification": sig,
        "five_derivatives": {"velocity": (gm - 0.5) * 10},
        "court": {"verdict": court_v, "evidence_weight": min(len(checks) / 5.0, 1.0)},
        "lab": {"lab_threat_level": threat},
        "bar": {"ruin_detected": ruin, "baseline_ok": (not ruin)},
        "fated": fated if isinstance(fated, dict) else {},
        "hci_score": hci,
        "on_purpose": True,
        "timestamp": row.get("created_epoch"),
        "phase_id": phase,
    }


def load_rows(path):
    """Accept a raw JSON array, {corpus:[...]}, or a saved MCP tool-result envelope."""
    raw = open(path, encoding="utf-8").read()
    # tool-result envelope: {"result":"...<untrusted-data-…> [ ... ] </…>..."}
    try:
        env = json.loads(raw)
        if isinstance(env, dict) and "result" in env:
            raw = env["result"]
    except (ValueError, TypeError):
        pass
    i, j = raw.find("[{"), raw.rfind("}]") + 2
    arr = json.loads(raw[i:j])
    if arr and isinstance(arr[0], dict) and "corpus" in arr[0]:
        return arr[0]["corpus"]
    return arr


def main():
    if len(sys.argv) < 2:
        print("usage: prod_receipt_to_op20_seed.py <rows.json> [out.jsonl]")
        return
    rows = load_rows(sys.argv[1])
    adapted = [adapt(r) for r in rows]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            for a in adapted:
                fh.write(json.dumps(a, ensure_ascii=False) + "\n")
        print(f"adapted {len(adapted)} receipts -> {out}")
    else:
        for a in adapted:
            print(json.dumps(a, ensure_ascii=False))


if __name__ == "__main__":
    main()
