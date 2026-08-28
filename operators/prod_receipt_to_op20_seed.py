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

SAGE ENRICHMENT (dims 22-27 somatic, 40-43 axioms) — no schema change:
  When a row carries `sage_signal` (JSON from the SageTrace.signal column, i.e.
  the SAGE operator's own op20-shaped output), the adapter lifts the REAL
  somatic{} and axioms{} blocks straight out of it, plus SAGE's clean-enum
  court_verdict / signal_classification / five_derivatives. Only ~45/247 prod
  receipts have a fired SAGE trace, so somatic/axiom stay op20-default (honestly
  constant) for the rest — the adapter never fabricates them. Persisting
  somatic/axiom for 100% coverage is a compass write-time schema change (COURT
  one-way door), tracked separately; this read-side join closes the gap for the
  rows that already carry the signal.

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


def _fated_from_row(row):
    """fated dict op20 measures by string length. Two input shapes are honored:
    the raw prod `fated` JSON-TEXT column, or a compact `fated_len` dict of
    integer lengths (used when the corpus was pulled in digest form to avoid
    shipping decision text through a tool boundary). The compact form is
    expanded to placeholder strings of the right length — op20 only ever reads
    len(str(value)), so this is loss-free for the dims it computes."""
    flen = row.get("fated_len")
    if isinstance(flen, dict):
        return {k: ("." * int(v)) for k, v in flen.items() if isinstance(v, (int, float))}
    fated = _pj(row.get("fated"))
    return fated if isinstance(fated, dict) else {}


def adapt(row, use_sage=True):
    lens = _pj(row.get("nciByLens")) or (row.get("nciByLens") if isinstance(row.get("nciByLens"), dict) else {})
    checks = _pj(row.get("court"))
    if checks is None:
        checks = row.get("court") if isinstance(row.get("court"), list) else []
    fated = _fated_from_row(row)
    tags = _pj(row.get("macroTags"))
    if tags is None:
        tags = row.get("macroTags") if isinstance(row.get("macroTags"), list) else []
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

    seed = {
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

    # ── SAGE enrichment: lift real somatic/axiom blocks when the trace fired ──
    sage = row.get("sage_signal") if use_sage else None
    if isinstance(sage, str):
        sage = _pj(sage)
    if isinstance(sage, dict):
        som = sage.get("somatic")
        if isinstance(som, dict):
            seed["somatic"] = som               # dims 22-27 now REAL, not default
        ax = sage.get("axioms")
        if isinstance(ax, dict):
            seed["axioms"] = ax                 # dims 40-43 now REAL, not default
        fd = sage.get("five_derivatives")
        if isinstance(fd, dict):
            seed["five_derivatives"] = fd       # full derivative vector, not just velocity
        # NOTE: court verdict is deliberately NOT taken from SAGE. The court[]
        # check array on the Receipt is the compass route's authoritative court
        # output; SAGE's court_verdict is an independent pre-screen and can
        # disagree. Overriding here would confound the court axis (which the
        # banked full-fidelity run derives from court[]). Likewise SAGE's
        # signal_classification uses a different vocabulary ("noise"/"signal")
        # than op20's gradient tiers, so it is not copied either. This keeps the
        # SAGE enrichment a clean delta: it adds ONLY somatic + axioms +
        # five_derivatives, nothing that already had a faithful mapping.
        seed["_sage_enriched"] = True

    return seed


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
    args = [a for a in sys.argv[1:] if a != "--no-sage"]
    use_sage = "--no-sage" not in sys.argv
    if not args:
        print("usage: prod_receipt_to_op20_seed.py [--no-sage] <rows.json> [out.jsonl]")
        return
    rows = load_rows(args[0])
    adapted = [adapt(r, use_sage=use_sage) for r in rows]
    out = args[1] if len(args) > 1 else None
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
