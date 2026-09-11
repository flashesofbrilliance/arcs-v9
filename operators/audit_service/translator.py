"""
translator.py — decode the TS-built primitives dict into Python dataclasses
the operators consume. Also builds a receipt dict for Kintsugi.

The TS client (audit-client.ts) already translates on its side; this is the
Python mirror + canonical decoder so the operators get native dataclass instances.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Make operators/ importable regardless of cwd
_HERE = Path(__file__).resolve().parent
_SYSROOT = _HERE.parent  # operators/
if str(_SYSROOT) not in sys.path:
    sys.path.insert(0, str(_SYSROOT))

from arcs_primitives import (
    AxiomCheck,
    CoherenceSignal,
    FATEDReasoning,
    SomaticReading,
)


# ── Dataclass holding decoded primitives ─────────────────────────────────────

class DecodedPrimitives:
    """Native dataclass cluster the operator run() methods consume."""

    def __init__(self, p: Dict[str, Any]) -> None:
        self.signal = CoherenceSignal(
            signal=p["signal"]["signalProxy"],
            domain=p["signal"]["domain"],
            label=p["signal"]["label"],
        )
        self.fated = FATEDReasoning(
            facts=p["fated"]["facts"],
            assumptions=p["fated"]["assumptions"],
            tradeoffs=p["fated"]["tradeoffs"],
            emotions=p["fated"]["emotions"],
            direction=p["fated"]["direction"],
        )
        self.axioms = AxiomCheck(
            clarity_before_curvature=p["axioms"]["clarity_before_curvature"],
            agency_over_automation=p["axioms"]["agency_over_automation"],
            minimum_steps_to_coherence=p["axioms"]["minimum_steps_to_coherence"],
            kairos_over_neuroticism=p["axioms"]["kairos_over_neuroticism"],
        )
        self.somatic = SomaticReading(
            phase_tuning=p["somatic"]["phase_tuning"],
            surge_detection=p["somatic"]["surge_detection"],
            feels_right=p["somatic"]["feels_right"],
            that_vibes=p["somatic"]["that_vibes"],
            locked_in=p["somatic"]["locked_in"],
            expected_vs_actual=p["somatic"]["expected_vs_actual"],
        )
        self.hci_score = float(p["hci_score"])
        self.hci_source = p["hci_source"]
        self.pci_score = float(p["pci_score"])
        self.irreversibility = float(p["irreversibility"])
        self.on_purpose = bool(p["onPurpose"])
        self.next_action = str(p.get("nextAction", ""))
        self.phase_id = str(p["phaseId"])
        self.signal_classification = str(p.get("signalClassification", "mixed"))
        self.fidelity = {
            "somatic": p["somatic"]["source"],
            "hci": p["hci_source"],
            "axioms": p["axioms"]["source"],
        }


# ── Kintsugi receipt dict builder ────────────────────────────────────────────

def build_kintsugi_receipt(
    p: Dict[str, Any],
    llm_output: Dict[str, Any],
    trace_id: str,
) -> Dict[str, Any]:
    """Build the receipt dict KINTSUGI.scan/receive expects."""
    nci = float(llm_output.get("nci_score", p.get("hci_score", 50.0)))
    return {
        "receipt_id": str(trace_id),
        "phase_id": str(p.get("phaseId", "phase_1")),
        "operator": "COMPASS_LLM",
        "signal_label": str(p["signal"]["label"]),
        "nci_score": nci,
        "on_purpose": bool(p.get("onPurpose", True)),
        "irreversibility": float(p.get("irreversibility", 0.3)),
        "hci_score": float(p["hci_score"]),
        "pci_score": float(p["pci_score"]),
        "signal_classification": str(p.get("signalClassification", "mixed")),
        "kinematic_summary": {
            "velocity": 0.6,
            "acceleration": 0.2,
        },
        "five_derivatives": {
            "velocity": 0.6,
            "acceleration": 0.2,
            "diffusion": 0.1,
            "phase_cancel": 0.0,
            "deceleration": 0.05,
        },
        "axioms": {
            "clarity_before_curvature": str(p["axioms"]["clarity_before_curvature"]),
            "agency_over_automation": str(p["axioms"]["agency_over_automation"]),
            "minimum_steps_to_coherence": str(p["axioms"]["minimum_steps_to_coherence"]),
            "kairos_over_neuroticism": str(p["axioms"]["kairos_over_neuroticism"]),
            "alignment_score": _axiom_alignment(p["axioms"]),
        },
        "fated": {
            "facts": str(p["fated"]["facts"]),
            "assumptions": str(p["fated"]["assumptions"]),
            "tradeoffs": str(p["fated"]["tradeoffs"]),
            "emotions": str(p["fated"]["emotions"]),
            "direction": str(p["fated"]["direction"]),
        },
        "somatic": {
            "phase_tuning": float(p["somatic"]["phase_tuning"]),
            "surge_detection": float(p["somatic"]["surge_detection"]),
            "feels_right": float(p["somatic"]["feels_right"]),
            "that_vibes": float(p["somatic"]["that_vibes"]),
            "locked_in": float(p["somatic"]["locked_in"]),
            "expected_vs_actual": float(p["somatic"]["expected_vs_actual"]),
            "witness_score": _witness_score(p["somatic"]),
        },
        "next_action": str(p.get("nextAction", "")),
        "notes": "Audit-layer receipt built from compass primitives.",
    }


def _axiom_alignment(ax: Dict[str, Any]) -> float:
    m = {"YES": 1.0, "TENSION": 0.5, "NO": 0.0}
    vals = [
        ax.get("clarity_before_curvature", "TENSION"),
        ax.get("agency_over_automation", "TENSION"),
        ax.get("minimum_steps_to_coherence", "TENSION"),
        ax.get("kairos_over_neuroticism", "TENSION"),
    ]
    return round(sum(m.get(v, 0.5) for v in vals) / len(vals), 3)


def _witness_score(som: Dict[str, Any]) -> float:
    # SomaticReading.witness_score() uses WEIGHTS; replicate here for the dict.
    weights = {
        "phase_tuning": 0.20,
        "surge_detection": 0.15,
        "feels_right": 0.25,
        "that_vibes": 0.15,
        "locked_in": 0.15,
        "expected_vs_actual": 0.10,
    }
    return round(
        sum(som[k] * w for k, w in weights.items()),
        3,
    )
