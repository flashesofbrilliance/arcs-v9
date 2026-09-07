"""Coverage hooks for Approach D.

Run alongside the 4 existing operators (SAGE/LAB/BAR/KINTSUGI) and produce
operator_coverage metadata recorded on each benchmark pair.

Design:
- coverage_hooks.py — the 3 hooks + public record_coverage() entry
- persisted as operator_coverage dict on each benchmark pair via the patched
  store_benchmark_fragment(operator_coverage=...) param
- CSM computation EXCLUDES KAIros/OP20/CONTRACT — they are coverage metadata,
  not CSM subtasks. The CSM frame stays for the 4 operators where it's defined.
- Tier labels are explicit so the coverage claim is honest:
  Tier 1 = ran with recorded output, not benchmarked
  Tier 2 = benchmarked with mature output + defined dimension
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ── Input normalization ──────────────────────────────────────────────────────

def _coherence_signal_from_primitives(primitives, llmOutput, auditResult):
    """Build a CoherenceSignal-like dict from the audit pair's three blocks.

    Motivation: KAIrosOperator.detect() expects (signal, receipt, session_context)
    where signal is CoherenceSignal-shaped. The audit store has primitives +
    llmOutput + auditResult across three blocks; a plain dict with their combined
    keys is all detect() needs to inspect. This flattens the three blocks into
    one dict for detect()'s signal param.
    """
    out: Dict[str, Any] = {}
    # primitives block
    for k, v in (primitives or {}).items():
        out[k] = v
    # llmOutput block (LLM side; KAIros may inspect LLM coherence claim)
    for k, v in (llmOutput or {}).items():
        out[f"llm_{k}"] = v
    # auditResult block (operator side; KAIros may compare against operator NCI)
    for k, v in (auditResult or {}).items():
        out[f"audit_{k}"] = v
    return out


def _flat_receipt_for_op20(primitives, llmOutput, auditResult, traceId, sessionVersion):
    """Build a CoherenceReceipt-like flat dict for SeedExtractor.extract().

    Motivation: SeedExtractor.extract(receipt, span) reads a receipt dict looking
    for specific keys: five_derivatives (velocity/acceleration/diffusion/
    phase_cancellation/deceleration), nci_score, irreversibility,
    signal_classification, lab, bar, court, somatic, fated, on_purpose,
    hci_score, timestamp, phase_id, axioms. The audit primitives block has most
    of these under different key names; llmOutput has coherence_pct (proxy for
    hci_score); auditResult has operator output (court, bar, lab, somatic
    sub-dicts). This function maps them into the shape SeedExtractor expects.
    """
    five_derivatives = (primitives or {}).get("five_derivatives") or {}
    somatic = (primitives or {}).get("somatic") or {}
    axioms = (primitives or {}).get("axioms") or {}
    lab_out = (auditResult or {}).get("output") or {}
    lab = lab_out.get("lab") or {}
    bar = lab_out.get("bar") or {}
    court = lab_out.get("court") or {}
    fated = (primitives or {}).get("fated") or {}

    receipt: Dict[str, Any] = {
        "five_derivatives": {
            "velocity": float(five_derivatives.get("velocity") or 0),
            "acceleration": float(five_derivatives.get("acceleration") or 0),
            "diffusion": float(five_derivatives.get("diffusion") or 0),
            "phase_cancellation": float(five_derivatives.get("phase_cancellation") or 0),
            "deceleration": float(five_derivatives.get("deceleration") or 0),
        },
        "nci_score": float((primitives or {}).get("nci_score") or 0),
        "irreversibility": float((primitives or {}).get("irreversibility") or 0),
        "signal_classification": str((primitives or {}).get("signal_classification") or "UNKNOWN"),
        "lab": {
            "loki_threat_level": float(lab.get("loki_threat_level") or 0),
            "lab_summary": str(lab.get("summary") or ""),
        },
        "bar": {
            "ruin_detected": bool(bar.get("ruin_detected") or False),
            "baseline_ok": bool(bar.get("baseline_ok") or False),
            "asymmetry_ratio": float(bar.get("asymmetry_ratio") or 0),
            "kelly_fraction": float(bar.get("kelly_fraction") or 0),
        },
        "court": {
            "verdict": str(court.get("verdict") or "UNKNOWN"),
            "evidence_weight": float(court.get("evidence_weight") or 0),
        },
        "somatic": {
            "phase_tuning": bool(somatic.get("phase_tuning") or False),
            "surge_detection": bool(somatic.get("surge_detection") or False),
            "feels_right": bool(somatic.get("feels_right") or False),
            "that_vibes": bool(somatic.get("that_vibes") or False),
            "locked_in": bool(somatic.get("locked_in") or False),
            "expected_vs_actual": float(somatic.get("expected_vs_actual") or 0),
        },
        "fated": fated,
        "on_purpose": bool((primitives or {}).get("on_purpose") or False),
        "hci_score": float((llmOutput or {}).get("coherence_pct") or 50.0),
        "timestamp": str(traceId),
        "phase_id": str((primitives or {}).get("phase_id") or "UNKNOWN"),
        "axioms": {
            "kairos_over_neuroticism": str(axioms.get("kairos_over_neuroticism") or "UNKNOWN"),
            "phase_cancellation": str(axioms.get("phase_cancellation") or "UNKNOWN"),
            "signal_in_noise": str(axioms.get("signal_in_noise") or "UNKNOWN"),
            "trust_mechanism": str(axioms.get("trust_mechanism") or "UNKNOWN"),
        },
    }
    return receipt


# ── Coverage hooks ────────────────────────────────────────────────────────────

def _run_kairos_annotation(primitives, llmOutput, auditResult):
    """Run KAIrosOperator.detect() on the audit pair and return the annotation.

    KAIros is a pre-SAGE annotation hook. It detects the time mode a signal is
    operating in. In the audit pipeline it runs BEFORE SAGE (the annotation may
    inform SAGE's phase_id selection — that's a product-level concern, not a
    benchmark concern).

    Returns a KAIrosTier + annotation dict:
    - tier: STUB (currently, until Phase 7 implementation lands)
    - annotation: the KairoAnnotation.to_dict() output
    - ran: True (KAIros was invoked)
    """
    from arcs_operator_kairos import KairosAnnotation, KairosOperator

    signal = _coherence_signal_from_primitives(primitives, llmOutput, auditResult)
    receipt = {
        "nci_score": float((primitives or {}).get("nci_score") or 0),
        "signal_classification": str((primitives or {}).get("signal_classification") or "UNKNOWN"),
        "phase_id": str((primitives or {}).get("phase_id") or "UNKNOWN"),
        "timestamp": str((primitives or {}).get("timestamp") or "unknown"),
        "hci_score": float((llmOutput or {}).get("coherence_pct") or 50.0),
        "on_purpose": bool((primitives or {}).get("on_purpose") or False),
    }
    session_context = {
        "session_version": 1,
        "traceId": str((primitives or {}).get("traceId") or "unknown"),
    }
    op = KairosOperator()
    ann: KairosAnnotation = op.detect(signal, receipt, session_context)
    return {
        "tier": "STUB",
        "annotation": ann.to_dict() if hasattr(ann, "to_dict") else {
            "detected_mode": str(getattr(ann, "detected_mode", "CHRONOS")),
            "confidence": float(getattr(ann, "confidence", 0.0)),
            "jurisdiction": str(getattr(ann, "jurisdiction", "UNKNOWN")),
            "gate": str(getattr(ann, "gate", "PASS")),
            "signals_used": int(getattr(ann, "signals_used", 0)),
            "mode_rationale": str(getattr(ann, "mode_rationale", "default")),
        },
        "ran": True,
        "operator_class": "KAIrosOperator",
        "phase": "Phase 7 TARGET / LAB-experimental (stub)",
    }


def _run_op20_seed(primitives, llmOutput, auditResult, traceId, sessionVersion):
    """Run OP20 SeedExtractor.extract() on the audit pair and return the seed.

    OP20 is a corpus-scale operator (DBSCAN taxonomy on 54-dim seed vectors).
    Per-receipt, it extracts a single FolksonomySeed from the receipt. This is
    a PARTIAL operator run — the full output (clusters, branches, quality metrics)
    requires a corpus. The seed extraction is real coverage (seed can be recorded,
    inspected, accumulated across receipts), but it's Tier 1 (not benchmarked —
    taxonomy quality benchmarking requires corpus threshold + non-noise clusters).

    Returns an OP20Tier + seed dict:
    - tier: SEED_EXTRACTION (per-receipt seed, not corpus taxonomy)
    - seed: the FolksonomySeed.to_dict() output
    - ran: True (seed extraction was invoked)
    """
    from arcs_operator20 import FolksonomySeed, SeedExtractor

    receipt = _flat_receipt_for_op20(primitives, llmOutput, auditResult, traceId, sessionVersion)
    span = None  # optional trace span — not in the audit store's scope per-receipt
    extractor = SeedExtractor()
    seed: FolksonomySeed = extractor.extract(receipt, span)
    seed_dict = seed.to_dict() if hasattr(seed, "to_dict") else {}
    return {
        "tier": "SEED_EXTRACTION",
        "seed": {
            "seed_id": seed_dict.get("seed_id") or str(getattr(seed, "seed_id", "unknown")),
            "receipt_id": seed_dict.get("receipt_id") or str(getattr(seed, "receipt_id", "unknown")),
            "phase_id": seed_dict.get("phase_id") or str(getattr(seed, "phase_id", "UNKNOWN")),
            "created_at": seed_dict.get("created_at") or str(getattr(seed, "created_at", None)),
            "vector": [float(x) for x in (seed_dict.get("vector") or getattr(seed, "vector", [0.0] * 54))],
            "labels": seed_dict.get("labels") or getattr(seed, "labels", []),
            "metadata": seed_dict.get("metadata") or getattr(seed, "metadata", {}),
        },
        "ran": True,
        "operator_class": "SeedExtractor",
        "phase": "Phase 5 — Folksonomy Cultivator (per-receipt seed, corpus taxonomy pending)",
    }


def _run_contract_check():
    """Run one-time Phase 6 contract validation on all operators in the audit surface.

    Checks whether SAGE/LAB/BAR/KINTSUGI satisfy the Phase 6 contract:
    - implements ARCSOperator (ABC) OR OperatorProtocol (Protocol)
    - has process(signal: dict) -> dict
    - has validate(signal: dict) -> bool
    - has describe() -> str
    - has name: str
    - has version: str

    Note: the existing 4 operators implement the Phase 4 legacy contract
    (operator_id + analyze(signal: CoherenceSignal, **kwargs) -> Tuple[...]),
    which arcs_operator_contract.py preserves as a compatibility alias. They do
    NOT currently satisfy the Phase 6 contract (no name property, no process/
    validate/describe methods). This function records that finding honestly.

    Returns:
    - tier: ONE_TIME_CHECK
    - results: per-operator contract check results
    - ran: True (contract check was invoked)
    """
    from arcs_operator_contract import (
        CONTRACT_VERSION,
        OperatorProtocol,
        ARCSOperator,
        REGISTERED_OPERATORS,
        validate_operator,
    )
    from arcs_operators_sage import SAGEOperator
    from arcs_operators_lab import LABOperator
    from arcs_operators_bar import BAROperator
    from arcs_kintsugi import KintsugiService

    operators = {
        "SAGE": SAGEOperator(),
        "LAB": LABOperator(),
        "BAR": BAROperator(),
        "KINTSUGI": KintsugiService(),
    }

    results = {}
    for name, op in operators.items():
        # Phase 4 legacy contract check — validate_operator raises ContractViolation
        # if the operator is missing required properties. All 4 implement Phase 4
        # legacy but NOT Phase 6, so they ALL fail this check. Record as False.
        try:
            validate_operator(op)
            legacy_ok: bool = True
        except Exception:
            legacy_ok = False

        # Phase 6 contract check
        has_name = hasattr(op, "name") and isinstance(getattr(op, "name"), str)
        has_version = hasattr(op, "version") and isinstance(getattr(op, "version"), str)
        has_process = hasattr(op, "process") and callable(getattr(op, "process"))
        has_validate = hasattr(op, "validate") and callable(getattr(op, "validate"))
        has_describe = hasattr(op, "describe") and callable(getattr(op, "describe"))

        phase6_ok = has_name and has_version and has_process and has_validate and has_describe

        results[name] = {
            "legacy_contract_passes": legacy_ok,
            "phase6_contract_satisfied": phase6_ok,
            "name_present": has_name,
            "version_present": has_version,
            "process_present": has_process,
            "validate_present": has_validate,
            "describe_present": has_describe,
            "name_value": str(getattr(op, "name", None)) if has_name else None,
            "version_value": str(getattr(op, "version", None)) if has_version else None,
            "registered_in_registry": name in (REGISTERED_OPERATORS or {}),
        }

    return {
        "tier": "ONE_TIME_CHECK",
        "results": results,
        "ran": True,
        "operator_class": "validate_operator (arcs_operator_contract)",
        "phase": "Phase 6 — operator contract",
        "contract_version": str(CONTRACT_VERSION) if CONTRACT_VERSION else "v9.0-phase2",
        "note": "Existing 4 operators implement Phase 4 legacy contract. "
                "Phase 6 contract satisfaction is NOT currently met (no name property, "
                "no process/validate/describe methods). This is an informational finding, "
                "not a blocker — operators still run through their Phase 4 runners.",
    }


# ── Public entry ───────────────────────────────────────────────────────────────

KAIrosTier = {"STUB": "STUB", "READY": "READY"}
OP20Tier = {"SEED_EXTRACTION": "SEED_EXTRACTION", "CORPUS_TAXONOMY": "CORPUS_TAXONOMY"}
ContractTier = {"ONE_TIME_CHECK": "ONE_TIME_CHECK", "RUNNING_GATE": "RUNNING_GATE"}

coverage_meanings = {
    "KAIros|STUB":
        "KAIros stub runs as pre-SAGE annotation hook. Detects CHRONOS with confidence "
        "0.0 and default rationale (gyroscopic detection not implemented). Phase 7 "
        "implementation pending. Not benchmarked.",
    "OP20|SEED_EXTRACTION":
        "OP20 per-receipt seed extraction runs. One FolksonomySeed per receipt (54-dim "
        "vector, phase_1). Taxonomy clustering pending receipt corpus threshold (57+ receipts "
        "per produce() doc). Not benchmarked.",
    "CONTRACT|ONE_TIME_CHECK":
        "One-time Phase 6 contract validation run on all operators in the audit surface. "
        "Result recorded. Running guarantee not yet enforced.",
}


def record_coverage(
    primitives: Dict[str, Any],
    llmOutput: Dict[str, Any],
    auditResult: Dict[str, Any],
    traceId: str,
    sessionVersion: int = 1,
) -> Dict[str, Any]:
    """Run all 3 coverage hooks on one audit pair and return operator_coverage.

    Called ONCE per receipt (not per operator). Returns:
    {
        "operator_coverage": {
            "KAIros":   {"tier": "STUB", "ran": True, "annotation": {...}, "meaning": "..."},
            "OP20":     {"tier": "SEED_EXTRACTION", "ran": True, "seed": {...}, "meaning": "..."},
            "CONTRACT": {"tier": "ONE_TIME_CHECK", "ran": True, "results": {...}, "meaning": "..."},
        },
        "tiers": {
            "KAIros": "STUB",
            "OP20": "SEED_EXTRACTION",
            "CONTRACT": "ONE_TIME_CHECK",
        },
        "coverage_operators": ["KAIros", "OP20", "CONTRACT"],
    }
    """
    kairos = _run_kairos_annotation(primitives, llmOutput, auditResult)
    op20 = _run_op20_seed(primitives, llmOutput, auditResult, traceId, sessionVersion)
    contract = _run_contract_check()

    operator_coverage = {
        "KAIros": {
            "tier": kairos["tier"],
            "meaning": coverage_meanings["KAIros|STUB"],
            "ran": kairos["ran"],
            "annotation": kairos["annotation"],
            "operator_class": kairos["operator_class"],
            "phase": kairos["phase"],
        },
        "OP20": {
            "tier": op20["tier"],
            "meaning": coverage_meanings["OP20|SEED_EXTRACTION"],
            "ran": op20["ran"],
            "seed": op20["seed"],
            "operator_class": op20["operator_class"],
            "phase": op20["phase"],
        },
        "CONTRACT": {
            "tier": contract["tier"],
            "meaning": coverage_meanings["CONTRACT|ONE_TIME_CHECK"],
            "ran": contract["ran"],
            "results": contract["results"],
            "contract_version": contract["contract_version"],
            "note": contract["note"],
            "operator_class": contract["operator_class"],
            "phase": contract["phase"],
        },
    }

    return {
        "operator_coverage": operator_coverage,
        "tiers": {
            "KAIros": kairos["tier"],
            "OP20": op20["tier"],
            "CONTRACT": contract["tier"],
        },
        "coverage_operators": ["KAIros", "OP20", "CONTRACT"],
    }
