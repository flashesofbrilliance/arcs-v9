#!/usr/bin/env python3
"""
run_real_receipts.py — run the audit instrument over REAL compass receipts.

play_instrument.py runs the SAGE/LAB/BAR/KINTSUGI operators + CSM board on
*synthetic* pairs. This runner does the same on *real* receipts exported from the
prod Prisma `Receipt` table, so the instrument reports on your actual decisions.

WHAT IT DOES (per receipt):
  1. Faithfully map the Receipt row -> operator `primitives` + compass `llmOutput`.
  2. Run all four operators (service.run_sage/lab/bar/kintsugi) -> real auditResult.
  3. Assemble one (receipt, operator) pair each; compute CSM + fidelity weight.
  4. Roll up the board: weighted vs unweighted CSM, per-operator, who-was-right
     (only where an Outcome adjudication is present), and a FIDELITY COVERAGE report.

HONESTY CONTRACT (mirrors prod_receipt_to_op20_seed.py):
  - Only fill a primitive when the row genuinely carries the signal.
  - somatic/axioms are NOT fabricated. Most prod receipts lack a fired SAGE trace,
    so their somatic stays `default` and their fidelity weight is low BY DESIGN —
    fidelity_weight (Task 18) discounts them rather than pretending we can score them.
  - who-was-right is reported ONLY for receipts carrying an Outcome adjudication;
    everything else is counted as UNADJUDICATED, never guessed.

INPUT: a JSON array or JSONL of Receipt rows (camelCase Prisma columns, JSON stored
as TEXT). A joined `sage_signal` field (the SageTrace.signal op20-shaped output) is
used when present to lift REAL somatic/axioms; absent -> defaults.

RUN (from repo root):
    python3 -m operators.audit_service.run_real_receipts <rows.json|rows.jsonl>
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from .schemas import AuditRequest
from .service import run_sage, run_lab, run_bar, run_kintsugi
from .persistence import (
    compute_csm,
    fidelity_weight,
    weighted_csm,
    weighted_csm_by_operator,
)

_OPERATORS = ["SAGE", "LAB", "BAR", "KINTSUGI"]
_RUNNERS = {"SAGE": run_sage, "LAB": run_lab, "BAR": run_bar, "KINTSUGI": run_kintsugi}


# ── Safe accessors for TEXT-stored JSON columns ───────────────────────────────

def _j(row: Dict[str, Any], col: str, default: Any = None) -> Any:
    """Parse a JSON-in-TEXT column; return `default` on absence/parse error."""
    v = row.get(col)
    if v is None:
        return default
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _num(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ── Receipt -> primitives (+ fidelity provenance) ─────────────────────────────

def receipt_to_primitives(row: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, bool]]:
    """Map a Receipt row to operator primitives, honestly.

    Returns (primitives, fidelity, provenance). `fidelity` feeds fidelity_weight;
    `provenance` records which signals were REAL vs defaulted (for the coverage report).
    """
    dewy = _j(row, "dewyVector", {}) or {}
    y = (dewy.get("Y") or {}) if isinstance(dewy, dict) else {}
    w = (dewy.get("W") or {}) if isinstance(dewy, dict) else {}
    fated = _j(row, "fated", {}) or {}
    by_lens = _j(row, "nciByLens", {}) or {}
    sage_signal = _j(row, "sage_signal", None)  # joined SageTrace.signal, if present

    prov = {"somatic_real": False, "axioms_real": False}

    # --- axioms: real if a SAGE trace carried them (the actual source), else the
    #     raw compass response, else default. (SAGE signal is where axioms live.) ---
    raw = _j(row, "rawResponse", {}) or {}
    axioms = None
    if isinstance(sage_signal, dict) and isinstance(sage_signal.get("axioms"), dict):
        axioms = sage_signal["axioms"]
    elif isinstance(raw, dict):
        axioms = raw.get("axioms") or (raw.get("reasoning", {}) or {}).get("axioms")
    if axioms and isinstance(axioms, dict):
        prov["axioms_real"] = True
        axioms_src = "llm_derived"
    else:
        axioms = {k: "TENSION" for k in
                  ("clarity_before_curvature", "agency_over_automation",
                   "minimum_steps_to_coherence", "kairos_over_neuroticism")}
        axioms_src = "default"

    # --- somatic: real ONLY if a SAGE trace is joined; never fabricated ---
    _SOMATIC_KEYS = ("phase_tuning", "surge_detection", "feels_right",
                     "that_vibes", "locked_in", "expected_vs_actual")
    if isinstance(sage_signal, dict) and sage_signal.get("somatic"):
        src_som = sage_signal["somatic"]
        somatic = {k: _num(src_som.get(k), 0.5) for k in _SOMATIC_KEYS}
        somatic["source"] = "user_self_report"
        prov["somatic_real"] = True
        somatic_src = "user_self_report"
    else:
        # No SAGE trace → explicit neutral default (NOT a sensor read); the
        # `default` fidelity marker makes fidelity_weight discount it.
        somatic = {k: 0.5 for k in _SOMATIC_KEYS}
        somatic["source"] = "default"
        somatic_src = "default"

    # --- signal proxy: receipts store no 12-d proxy; derive a short honest proxy
    #     from the DEWY Y-vector + nci. Marked as derived (not a real sensor read). ---
    polarity = _num(y.get("polarity"), 0.0)
    conviction = _num(y.get("conviction"), _num(row.get("nciScore"), 0.0) / 100.0)
    stability = _num(y.get("stability"), 0.5)
    signal_proxy = [
        max(0.0, min(1.0, conviction)),
        max(0.0, min(1.0, (polarity + 1.0) / 2.0)),
        max(0.0, min(1.0, stability)),
    ]

    # --- irreversibility from doorClass (same mapping as the op20 adapter) ---
    door = str(row.get("doorClass") or "").upper()
    irreversibility = {"ONE_WAY": 0.85, "TWO_WAY": 0.20}.get(door, 0.35)

    # --- hci from nci lenses (proxy — never a real self-report here) ---
    hci = _num(by_lens.get("conviction"), 0.0) + _num(by_lens.get("coherence"), 0.0)  # 0-40

    primitives = {
        "signal": {
            "label": (row.get("sharpQuestion") or row.get("decision") or "")[:280],
            "signalProxy": signal_proxy,
            "domain": "decision",
            "phaseId": row.get("phaseId") or row.get("surface") or "ORIENT",
        },
        "fated": {k: fated.get(k, "") for k in
                  ("facts", "assumptions", "tradeoffs", "emotions", "direction")}
                 if isinstance(fated, dict) else {},
        "axioms": axioms,
        "somatic": somatic,
        "hci_score": hci,
        "hci_source": "proxy",
        "pci_score": max(0.0, min(1.0, _num(row.get("coherencePct"), 0.0) / 100.0)),
        "irreversibility": irreversibility,
        "onPurpose": bool(row.get("onPurpose")) if row.get("onPurpose") is not None else True,
        "phaseId": row.get("surface") or "ORIENT",
        "nextAction": row.get("nextAction") or "",
        "signalClassification": _classify(row),
    }
    fidelity = {"somatic": somatic_src, "hci": "proxy", "axioms": axioms_src}
    return primitives, fidelity, prov


def _classify(row: Dict[str, Any]) -> str:
    # Valid schema literals: strong_signal | noise | mixed | decelerating.
    # Real receipts carry no gradient column, so this defaults to the neutral
    # 'mixed' — an honest "no directional signal", not a fabricated verdict.
    g = row.get("gradientMagnitude")
    if g is None:
        return "mixed"
    gv = _num(g, 0.5)
    return "strong_signal" if gv >= 0.6 else ("decelerating" if gv <= 0.4 else "mixed")


def receipt_to_llm_output(row: Dict[str, Any]) -> Dict[str, Any]:
    """Map the receipt's actual compass output into the llmOutput shape."""
    return {
        "nci_score": _num(row.get("nciScore"), 0.0),
        "coherence_pct": _num(row.get("coherencePct"), 0.0),
        "true_north": row.get("trueNorth") or "",
        "reasoning": {
            "fated": _j(row, "fated", {}) or {},
            "court": _j(row, "court", []) or [],
        },
        "meta": {"macro_tags": _j(row, "macroTags", []) or []},
        "axioms": (_j(row, "rawResponse", {}) or {}).get("axioms", {}),
        "loki": row.get("loki") or "",
        "bar": _j(row, "bar", {}) or {},
    }


def receipt_to_adjudication(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """who-was-right ONLY from a joined Outcome; None if unadjudicated (never guessed)."""
    outcome = _j(row, "outcome", None)
    if isinstance(outcome, dict) and outcome.get("who_was_right"):
        return {"who_was_right": outcome["who_was_right"],
                "unresolved": bool(outcome.get("unresolved", False))}
    return None


# ── Build pairs (runs the real operators) ─────────────────────────────────────

def build_pairs(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    primitives_raw, fidelity, prov = receipt_to_primitives(row)
    llm = receipt_to_llm_output(row)
    adjudication = receipt_to_adjudication(row)
    trace_id = row.get("receiptId") or row.get("id") or "unknown"

    # Validate through the production schema so operators receive the exact shape
    # the live service produces (pydantic fills defaults for anything we omit).
    req = AuditRequest(traceId=trace_id, sessionVersion=1, primitives=primitives_raw, llmOutput=llm)
    primitives = req.primitives.model_dump()

    pairs: List[Dict[str, Any]] = []
    for op in _OPERATORS:
        result = _RUNNERS[op](primitives, llm, fidelity)  # RUN the real operator
        pair = {
            "traceId": trace_id,
            "operator": op,
            "primitives": primitives,
            "llmOutput": llm,
            "auditResult": result,  # carries output + fidelity from _envelope
            "_provenance": prov,
        }
        if adjudication:
            pair["adjudication"] = adjudication
        pairs.append(pair)
    return pairs


# ── Runner + board ────────────────────────────────────────────────────────────

def load_receipts(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def run(path: str) -> Dict[str, Any]:
    receipts = load_receipts(path)
    all_pairs: List[Dict[str, Any]] = []
    somatic_real = axioms_real = adjudicated = 0
    for row in receipts:
        ps = build_pairs(row)
        if ps:
            prov = ps[0]["_provenance"]
            somatic_real += 1 if prov["somatic_real"] else 0
            axioms_real += 1 if prov["axioms_real"] else 0
            adjudicated += 1 if "adjudication" in ps[0] else 0
        all_pairs.extend(ps)

    n = len(receipts)
    unweighted = (sum(compute_csm(p) for p in all_pairs) / len(all_pairs)) if all_pairs else 0.0

    # Confidence tiers per RECEIPT (honesty: null = no trustworthy signal yet).
    #   EVIDENCE = real somatic AND real axioms · PARTIAL = one real · NONE = neither.
    tiers = {"EVIDENCE": 0, "PARTIAL": 0, "NONE": 0}
    # who-was-right: only where an Outcome adjudication exists; else null (never guessed).
    who: Dict[str, int] = {}
    seen_receipts = set()
    for p in all_pairs:
        rid = p.get("traceId")
        if rid not in seen_receipts:
            seen_receipts.add(rid)
            prov = p.get("_provenance", {})
            real = int(bool(prov.get("somatic_real"))) + int(bool(prov.get("axioms_real")))
            tiers["EVIDENCE" if real == 2 else "PARTIAL" if real == 1 else "NONE"] += 1
        adj = p.get("adjudication")
        if adj:
            who[adj["who_was_right"]] = who.get(adj["who_was_right"], 0) + 1

    # A headline score is only trustworthy if SOME receipt carries evidence.
    trustworthy = (tiers["EVIDENCE"] + tiers["PARTIAL"]) > 0

    return {
        "receipts": n,
        "pairs": len(all_pairs),
        # null, not a number, when nothing carries trustworthy signal:
        "weighted_csm": round(weighted_csm(all_pairs), 4) if trustworthy else None,
        "unweighted_csm": round(unweighted, 4),  # kept for reference; unweighted ignores fidelity
        "weighted_by_operator": {k: round(v, 4) for k, v in weighted_csm_by_operator(all_pairs).items()} if trustworthy else None,
        "confidence_tiers": tiers,
        "fidelity_coverage": {
            "somatic_real": somatic_real, "somatic_pct": round(100 * somatic_real / n, 1) if n else 0.0,
            "axioms_real": axioms_real, "axioms_pct": round(100 * axioms_real / n, 1) if n else 0.0,
            "mean_fidelity_weight": round(sum(fidelity_weight(p) for p in all_pairs) / len(all_pairs), 4) if all_pairs else 0.0,
        },
        # explicit null when unadjudicated — not a fake "UNADJUDICATED" bucket masquerading as a result:
        "who_was_right": who or None,
        "adjudicated_receipts": adjudicated,
        "unadjudicated_receipts": n - adjudicated,
    }


def _nz(v: Any) -> str:
    """Render null explicitly as 'null (no trustworthy signal yet)'."""
    return "null (no trustworthy signal yet)" if v is None else str(v)


def _print_board(b: Dict[str, Any]) -> None:
    t = b["confidence_tiers"]
    print("=" * 68)
    print(f" REAL-RECEIPT AUDIT BOARD — {b['receipts']} receipts, {b['pairs']} pairs")
    print("=" * 68)
    print(f" TRUST SCORE (fidelity-weighted) : {_nz(b['weighted_csm'])}")
    print(f"   per operator                  : {_nz(b['weighted_by_operator'])}")
    print(f"   (raw, ignores fidelity)       : {b['unweighted_csm']}")
    print("-" * 68)
    print(" CONFIDENCE PER DECISION:")
    print(f"   evidence-backed : {t['EVIDENCE']}")
    print(f"   partial         : {t['PARTIAL']}")
    print(f"   null (no signal): {t['NONE']}   ← scored low-confidence, never faked")
    fc = b["fidelity_coverage"]
    print(f"   somatic real {fc['somatic_real']}/{b['receipts']} ({fc['somatic_pct']}%) · "
          f"axioms real {fc['axioms_real']}/{b['receipts']} ({fc['axioms_pct']}%)")
    print("-" * 68)
    print(f" WHO-WAS-RIGHT : {_nz(b['who_was_right'])}")
    print(f"   ({b['adjudicated_receipts']} adjudicated, {b['unadjudicated_receipts']} null/unproven)")
    print("=" * 68)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 -m operators.audit_service.run_real_receipts <rows.json|rows.jsonl>")
        raise SystemExit(2)
    board = run(sys.argv[1])
    _print_board(board)
    print(json.dumps(board))  # machine-readable trailer
