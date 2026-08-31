"""
service.py — operator runner for the audit service.

Each public function takes a primitives dict + llmOutput + fidelity dict,
runs the relevant operator(s), and returns an AuditResponse-shaped dict.

Design:
  - Independent per endpoint (no shared mutable state between calls).
  - LAB and BAR re-run SAGE internally (LAB.run / BAR.run need a SAGE receipt).
  - Defensive: exceptions → ok=False with failureReason, never crash the endpoint.
"""
from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent
_SYSROOT = _HERE.parent
if str(_SYSROOT) not in sys.path:
    sys.path.insert(0, str(_SYSROOT))

from .translator import DecodedPrimitives, build_kintsugi_receipt

# Lazy-loaded operator singletons (import cost is real; defer to first use).
_sage_op = None
_lab_op = None
_bar_op = None
_kintsugi_svc = None


def _sage() -> Any:
    global _sage_op
    if _sage_op is None:
        from arcs_operators_sage import SAGEOperator
        _sage_op = SAGEOperator()
    return _sage_op


def _lab() -> Any:
    global _lab_op
    if _lab_op is None:
        from arcs_operators_lab import LABOperator
        _lab_op = LABOperator()
    return _lab_op


def _bar() -> Any:
    global _bar_op
    if _bar_op is None:
        from arcs_operators_bar import BAROperator
        _bar_op = BAROperator()
    return _bar_op


def _kintsugi() -> Any:
    global _kintsugi_svc
    if _kintsugi_svc is None:
        from arcs_kintsugi import KintsugiService
        _kintsugi_svc = KintsugiService()
    return _kintsugi_svc


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_ms() -> float:
    return time.time() * 1000


def _envelope(
    ok: bool,
    operator: str,
    output: Dict[str, Any],
    primitives_sent: Dict[str, Any],
    fidelity: Dict[str, str],
    t0: float,
    failure_reason: str | None = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "operator": operator,
        "output": output,
        "primitivesSent": primitives_sent,
        "latencyMs": round(_now_ms() - t0, 1),
        "fidelity": fidelity,
        "failureReason": failure_reason,
    }


def _failure_reason(ex: BaseException) -> str:
    s = str(ex)
    return s[:300] if s else type(ex).__name__


# ── SAGE ──────────────────────────────────────────────────────────────────────

def run_sage(
    primitives: Dict[str, Any],
    llm_output: Dict[str, Any],
    fidelity: Dict[str, str],
) -> Dict[str, Any]:
    t0 = _now_ms()
    try:
        decoded = DecodedPrimitives(primitives)
        receipt = _sage().run(
            signal=decoded.signal,
            fated=decoded.fated,
            axioms=decoded.axioms,
            somatic=decoded.somatic,
            hci_score=decoded.hci_score,
            phase_id=decoded.phase_id,
            next_action=decoded.next_action or "Review the decision before acting.",
            on_purpose=decoded.on_purpose,
            irreversibility=decoded.irreversibility,
        )
        output = {
            "nci_score": receipt.nci_score,
            "pci_score": receipt.pci_score,
            "hci_score": receipt.hci_score,
            "signal_classification": receipt.signal_classification,
            "axioms": {
                "clarity_before_curvature": receipt.axioms.clarity_before_curvature,
                "agency_over_automation": receipt.axioms.agency_over_automation,
                "minimum_steps_to_coherence": receipt.axioms.minimum_steps_to_coherence,
                "kairos_over_neuroticism": receipt.axioms.kairos_over_neuroticism,
                "alignment_score": receipt.axioms.alignment_score(),
            },
            "verdict": _sage_verdict(receipt),
            "kinematic_summary": receipt.kinematic_summary,
            "five_derivatives": receipt.five_derivatives,
            "somatic": {
                "phase_tuning": receipt.somatic.phase_tuning,
                "surge_detection": receipt.somatic.surge_detection,
                "feels_right": receipt.somatic.feels_right,
                "that_vibes": receipt.somatic.that_vibes,
                "locked_in": receipt.somatic.locked_in,
                "expected_vs_actual": receipt.somatic.expected_vs_actual,
                "witness_score": receipt.somatic.witness_score(),
            },
            "coherence_law_score": receipt.coherence_law_score(),
            "is_satoshi": receipt.is_satoshi(),
            "nci_grade": receipt.nci_grade(),
        }
        return _envelope(True, "SAGE", output, primitives, fidelity, t0)
    except Exception as e:
        return _envelope(
            False, "SAGE", {}, primitives, fidelity, t0, _failure_reason(e),
        )


def _sage_verdict(receipt: Any) -> str:
    grade = receipt.nci_grade()
    if grade in {
        "RELEASE_READY", "PHASE_5_READY", "PHASE_3_READY",
        "PHASE_2_READY", "PHASE_1_READY", "SATOSHI_VALID",
    }:
        return "PASS"
    return "TENSION"


# ── LAB (re-runs SAGE internally to get the receipt LAB needs) ───────────────

def run_lab(
    primitives: Dict[str, Any],
    llm_output: Dict[str, Any],
    fidelity: Dict[str, str],
) -> Dict[str, Any]:
    t0 = _now_ms()
    try:
        decoded = DecodedPrimitives(primitives)
        sage_receipt = _sage().run(
            signal=decoded.signal,
            fated=decoded.fated,
            axioms=decoded.axioms,
            somatic=decoded.somatic,
            hci_score=decoded.hci_score,
            phase_id=decoded.phase_id,
            next_action=decoded.next_action or "Review the decision before acting.",
            on_purpose=decoded.on_purpose,
            irreversibility=decoded.irreversibility,
        )
        assessment = _lab().run(sage_receipt, decoded.phase_id)
        output = {
            "lab_threat_level": assessment.lab_threat_level,
            "lab_recommendation": assessment.lab_recommendation,
            "lab_summary": assessment.lab_summary,
            "loki": _loki_to_dict(assessment.loki),
            "advisors": [_advisor_to_dict(a) for a in assessment.advisors],
            "bayesian": _bayesian_to_dict(assessment.bayesian),
        }
        return _envelope(True, "LAB", output, primitives, fidelity, t0)
    except Exception as e:
        return _envelope(
            False, "LAB", {}, primitives, fidelity, t0, _failure_reason(e),
        )


# ── BAR (re-runs SAGE + LAB internally) ──────────────────────────────────────

def run_bar(
    primitives: Dict[str, Any],
    llm_output: Dict[str, Any],
    fidelity: Dict[str, str],
) -> Dict[str, Any]:
    t0 = _now_ms()
    try:
        decoded = DecodedPrimitives(primitives)
        sage_receipt = _sage().run(
            signal=decoded.signal,
            fated=decoded.fated,
            axioms=decoded.axioms,
            somatic=decoded.somatic,
            hci_score=decoded.hci_score,
            phase_id=decoded.phase_id,
            next_action=decoded.next_action or "Review the decision before acting.",
            on_purpose=decoded.on_purpose,
            irreversibility=decoded.irreversibility,
        )
        lab_assessment = _lab().run(sage_receipt, decoded.phase_id)
        bar_assessment = _bar().run(sage_receipt, lab_assessment, decoded.phase_id)
        output = {
            "bar_verdict": bar_assessment.bar_verdict,
            "bar_summary": bar_assessment.bar_summary,
            "baseline": bar_assessment.baseline.to_dict(),
            "asymmetry": bar_assessment.asymmetry.to_dict(),
            "ruin": bar_assessment.ruin.to_dict(),
        }
        return _envelope(True, "BAR", output, primitives, fidelity, t0)
    except Exception as e:
        return _envelope(
            False, "BAR", {}, primitives, fidelity, t0, _failure_reason(e),
        )


# ── KINTSUGI ─────────────────────────────────────────────────────────────────

def run_kintsugi(
    primitives: Dict[str, Any],
    llm_output: Dict[str, Any],
    fidelity: Dict[str, str],
) -> Dict[str, Any]:
    t0 = _now_ms()
    try:
        receipt_dict = build_kintsugi_receipt(primitives, llm_output, primitives.get("traceId", "unknown"))
        svc = _kintsugi()
        diagnosis = svc.diagnose(receipt_dict)
        if not diagnosis.is_healthy:
            diagnosis = svc.repair(diagnosis, receipt_dict)
        repaired = diagnosis.repaired_receipt or {}
        seams = diagnosis.golden_seams or []
        output = {
            "pathogens": [_pathogen_to_dict(pt) for pt in diagnosis.pathogens],
            "is_healthy": diagnosis.is_healthy,
            "repaired": bool(diagnosis.is_repaired),
            "golden_seams": [_seam_to_dict(s) for s in seams],
            "kintsugi_repaired": bool(repaired.get("kintsugi_repaired")),
            "kintsugi_repair_count": len(seams),
            "kintsugi_trust_discount": float(repaired.get("kintsugi_trust_discount", 0.0)),
            "kintsugi_seam_ids": [s.seam_id for s in seams],
            "kintsugi_repaired_at": repaired.get("kintsugi_repaired_at"),
            "kintsugi_version": "v9.0-phase4",
            "nci_score": repaired.get("nci_score"),
            "nci_pre_repair": repaired.get("nci_pre_repair"),
        }
        return _envelope(True, "KINTSUGI", output, primitives, fidelity, t0)
    except Exception as e:
        return _envelope(
            False, "KINTSUGI", {}, primitives, fidelity, t0, _failure_reason(e),
        )


# ── Dict converters ──────────────────────────────────────────────────────────

def _loki_to_dict(loki: Any) -> Dict[str, Any]:
    if loki is None:
        return {}
    return {
        "challenge_statement": getattr(loki, "challenge_statement", ""),
        "failure_modes": getattr(loki, "failure_modes", []),
        "hidden_assumptions": getattr(loki, "hidden_assumptions", []),
        "worst_case_scenario": getattr(loki, "worst_case_scenario", ""),
        "loki_confidence": getattr(loki, "loki_confidence", 0.0),
        "can_be_dismissed": getattr(loki, "can_be_dismissed", False),
        "dismissal_argument": getattr(loki, "dismissal_argument", ""),
        "threat_score": getattr(loki, "threat_score", lambda: 0.0)()
        if callable(getattr(loki, "threat_score", None))
        else getattr(loki, "threat_score", 0.0),
    }


def _advisor_to_dict(a: Any) -> Dict[str, Any]:
    return {
        "advisor_archetype": getattr(a, "advisor_archetype", ""),
        "domain": getattr(a, "domain", ""),
        "stance": getattr(a, "stance", ""),
        "reasoning": getattr(a, "reasoning", ""),
        "confidence": getattr(a, "confidence", 0.0),
    }


def _bayesian_to_dict(b: Any) -> Dict[str, Any]:
    if b is None:
        return {}
    return {
        "prior_confidence": getattr(b, "prior_confidence", 0.0),
        "loki_evidence_weight": getattr(b, "loki_evidence_weight", 0.0),
        "advisor_consensus_weight": getattr(b, "advisor_consensus_weight", 0.0),
        "posterior_confidence": getattr(b, "posterior_confidence", 0.0),
        "belief_shift": getattr(b, "belief_shift", 0.0),
        "proceed_recommended": getattr(b, "proceed_recommended", False),
    }


def _pathogen_to_dict(pt: Any) -> Dict[str, Any]:
    return {
        "pathogen_type": getattr(pt, "pathogen_type", None),
        "severity": getattr(pt, "severity", None),
        "description": getattr(pt, "description", ""),
        "evidence": getattr(pt, "evidence", ""),
        "confidence": getattr(pt, "confidence", None),
    }


def _seam_to_dict(s: Any) -> Dict[str, Any]:
    return {
        "seam_id": getattr(s, "seam_id", ""),
        "seam_type": getattr(s, "seam_type", None),
        "trust_discount": getattr(s, "trust_discount", 0.0),
        "description": getattr(s, "description", ""),
        "repair_description": getattr(s, "repair_description", ""),
    }
