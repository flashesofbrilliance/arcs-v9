"""
arcs_operators_bar.py
ARCS v9 — BAR Operator
Phase 3: READ-WRITE

BAR: Risk Geometry Analysis
  B = Baseline   : What is the floor? Minimum viable / worst acceptable outcome.
  A = Asymmetric : What is the upside/downside ratio? Is the bet worth taking?
  R = Ruin       : Is there a non-recoverable failure mode? Can this kill the system?

Canon foundation:
  - ARCS Law entropy/coherence (second law: minimize wasted energy)
  - Nassim Taleb anti-fragility (Operator17 reference)
  - BAR macro (Canon v9, Decision Geometry Macros)

Role in pipeline:
  - Runs AFTER LAB (receives LABAssessment + SAGEReceipt)
  - Produces BARAssessment with three geometry outputs
  - Flags any RUIN-level risk → triggers Constitutional Court in Phase 4
  - Feeds into Curator + final pipeline receipt

CRITICAL: If ruin_detected = True, the pipeline MUST pause for human review.
NOTOMATION Rule: BAR identifies ruin — humans decide whether to proceed.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from arcs_primitives import (
    AXIOM_YES, AXIOM_NO, AXIOM_TENSION,
    CoherenceReceipt,
)
from arcs_operators_lab import LABAssessment

BAR_VERSION = "v9.0-phase3"


# ─────────────────────────────────────────────
# BAR DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class BaselineAssessment:
    """
    B-geometry: Floor analysis.
    What is the minimum acceptable outcome?
    What happens if nothing works as planned?
    """
    floor_scenario: str          # Description of worst-acceptable (not ruin) outcome
    floor_nci: float             # NCI at floor scenario (0–100)
    floor_is_acceptable: bool    # Is the floor acceptable to operate from?
    floor_confidence: float      # How confident are we this is the real floor (not ruin)?
    recovery_path: str           # How do we recover from the floor if hit?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "floor_scenario": self.floor_scenario,
            "floor_nci": self.floor_nci,
            "floor_is_acceptable": self.floor_is_acceptable,
            "floor_confidence": self.floor_confidence,
            "recovery_path": self.recovery_path,
        }


@dataclass
class AsymmetryAssessment:
    """
    A-geometry: Upside/downside ratio.
    Canonical question: Is the potential gain worth the potential loss?
    Good bets have asymmetric upside. Bad bets have symmetric or negative asymmetry.
    """
    upside_scenario: str         # Best realistic outcome
    downside_scenario: str       # Worst realistic (non-ruin) outcome
    upside_magnitude: float      # Estimated gain (normalized 0–1)
    downside_magnitude: float    # Estimated loss (normalized 0–1)
    asymmetry_ratio: float       # upside / downside (>1 = favorable)
    bet_quality: str             # "STRONG" | "ACCEPTABLE" | "MARGINAL" | "UNFAVORABLE"
    kelly_fraction: float        # Optimal bet sizing: f = (p*b - q) / b

    def to_dict(self) -> Dict[str, Any]:
        return {
            "upside_scenario": self.upside_scenario,
            "downside_scenario": self.downside_scenario,
            "upside_magnitude": round(self.upside_magnitude, 3),
            "downside_magnitude": round(self.downside_magnitude, 3),
            "asymmetry_ratio": round(self.asymmetry_ratio, 3),
            "bet_quality": self.bet_quality,
            "kelly_fraction": round(self.kelly_fraction, 3),
        }


@dataclass
class RuinAssessment:
    """
    R-geometry: Non-recoverable failure detection.
    Ruin = irreversible loss of the ability to play the game again.

    Canon: Ruin-level risk → auto-triggers Constitutional Court (Phase 4).
    Ruin is defined by:
      - irreversibility_score > 0.7 (from SAGE receipt)
      - OR explicit identification of system-killing failure mode
      - OR Loki threat_score > 0.7 AND can_be_dismissed = False
    """
    ruin_detected: bool           # Is ruin possible?
    ruin_scenario: str            # How ruin happens
    ruin_probability: float       # Estimated probability (0.0–1.0)
    irreversibility_score: float  # From SAGE receipt
    court_trigger: bool           # Should Constitutional Court be invoked?
    mitigation: str               # How to reduce ruin probability

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruin_detected": self.ruin_detected,
            "ruin_scenario": self.ruin_scenario,
            "ruin_probability": round(self.ruin_probability, 3),
            "irreversibility_score": self.irreversibility_score,
            "court_trigger": self.court_trigger,
            "mitigation": self.mitigation,
        }


@dataclass
class BARAssessment:
    """Full BAR operator output."""
    signal_label:   str
    phase_id:       str
    timestamp:      float = field(default_factory=time.time)

    baseline:   Optional[BaselineAssessment]   = None
    asymmetry:  Optional[AsymmetryAssessment]  = None
    ruin:       Optional[RuinAssessment]       = None

    bar_verdict:    str = "ACCEPTABLE"  # "STRONG" | "ACCEPTABLE" | "CAUTION" | "RUIN_RISK"
    bar_summary:    str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_label": self.signal_label,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp,
            "baseline": self.baseline.to_dict() if self.baseline else None,
            "asymmetry": self.asymmetry.to_dict() if self.asymmetry else None,
            "ruin": self.ruin.to_dict() if self.ruin else None,
            "bar_verdict": self.bar_verdict,
            "bar_summary": self.bar_summary,
        }


# ─────────────────────────────────────────────
# BAR OPERATOR
# ─────────────────────────────────────────────

class BAROperator:
    """
    BAR: Risk Geometry Operator.

    Takes SAGE + LAB outputs and maps the full risk geometry:
      - Where is the floor? (Baseline)
      - Is the bet worth taking? (Asymmetry)
      - Can this kill us? (Ruin)
    """

    def __init__(self):
        self.version = BAR_VERSION
        self.operator_name = "BAR"

    # ── B: Baseline ──────────────────────────

    def assess_baseline(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
    ) -> BaselineAssessment:
        nci = sage_receipt.nci_score
        irreversibility = sage_receipt.irreversibility
        lab_rec = lab.lab_recommendation

        # Floor NCI: estimated NCI if we proceed and Loki is partially right
        threat = lab.loki.threat_score() if lab.loki else 0.3
        floor_nci = round(nci * (1.0 - threat * 0.4), 1)
        floor_nci = max(0.0, floor_nci)

        floor_is_acceptable = floor_nci >= 50  # Satoshi validity threshold

        floor_scenario = (
            f"If Loki's challenge ({threat:.0%} threat) materializes partially: "
            f"NCI drops from {nci:.1f} to ~{floor_nci:.1f}. "
            f"{'Still above satoshi threshold (50). Recoverable.' if floor_is_acceptable else 'Falls below satoshi threshold. Requires rework.'}"
        )

        recovery_path = (
            "Revert to last stable receipt. Re-run SAGE with updated signal. "
            "Apply FATED reasoning to understand what changed. Issue correction receipt."
            if floor_is_acceptable else
            "Full phase rollback required. Run Phase 1 READ again on updated signal state. "
            "Do not proceed to next phase until NCI re-establishes above 75."
        )

        return BaselineAssessment(
            floor_scenario=floor_scenario,
            floor_nci=floor_nci,
            floor_is_acceptable=floor_is_acceptable,
            floor_confidence=round(1.0 - irreversibility, 3),
            recovery_path=recovery_path,
        )

    # ── A: Asymmetry ─────────────────────────

    def assess_asymmetry(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
    ) -> AsymmetryAssessment:
        nci = sage_receipt.nci_score
        posterior = lab.bayesian.posterior_confidence if lab.bayesian else 0.6
        threat = lab.loki.threat_score() if lab.loki else 0.3

        # Upside: if everything works as SAGE suggests
        upside_magnitude = round(posterior * (nci / 100), 3)

        # Downside: if Loki is right (threat materializes)
        downside_magnitude = round(threat * (1.0 - posterior), 3)
        downside_magnitude = max(0.01, downside_magnitude)  # avoid div/0

        asymmetry_ratio = round(upside_magnitude / downside_magnitude, 2)

        # Bet quality
        if asymmetry_ratio >= 3.0:
            bet_quality = "STRONG"
        elif asymmetry_ratio >= 1.5:
            bet_quality = "ACCEPTABLE"
        elif asymmetry_ratio >= 1.0:
            bet_quality = "MARGINAL"
        else:
            bet_quality = "UNFAVORABLE"

        # Kelly fraction: f* = (p*b - q) / b
        # p = posterior (probability of success)
        # b = upside_magnitude / downside_magnitude (the odds)
        # q = 1 - p
        p = posterior
        q = 1.0 - p
        b = asymmetry_ratio
        kelly = round(max(0.0, (p * b - q) / b) if b != 0.0 else 0.0, 3)

        upside_scenario = (
            f"Signal proceeds as SAGE classified ({sage_receipt.signal_classification}). "
            f"NCI maintains above {nci:.0f}. Posterior confidence: {posterior:.2f}."
        )
        downside_scenario = (
            f"Loki's challenge ({threat:.0%} threat) materializes. "
            f"Signal reverses or stalls. Rework required."
        )

        return AsymmetryAssessment(
            upside_scenario=upside_scenario,
            downside_scenario=downside_scenario,
            upside_magnitude=upside_magnitude,
            downside_magnitude=downside_magnitude,
            asymmetry_ratio=asymmetry_ratio,
            bet_quality=bet_quality,
            kelly_fraction=kelly,
        )

    # ── R: Ruin ──────────────────────────────

    def assess_ruin(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
    ) -> RuinAssessment:
        irreversibility = sage_receipt.irreversibility
        loki_threat = lab.loki.threat_score() if lab.loki else 0.0
        loki_structural = (lab.loki and not lab.loki.can_be_dismissed) if lab.loki else False
        lab_rec = lab.lab_recommendation

        # Ruin conditions (Canon: Phase 4 Constitutional Court trigger thresholds)
        ruin_by_irreversibility = irreversibility > 0.7

        # Ceiling-adjusted Loki ruin threshold.
        # A decelerating signal at NCI 95 is approaching a natural ceiling — not collapsing.
        # Ruin requires an overwhelming Loki challenge (>0.95) near a coherence peak.
        # A decelerating signal at NCI 70 carries normal ruin risk (threshold stays 0.70).
        # This prevents false BLOCKED results on healthy plateau-approaching signals.
        nci = sage_receipt.nci_score
        signal_cls = sage_receipt.signal_classification
        if nci > 90 and signal_cls == "decelerating":
            # Ceiling-adjacent: signal is near peak coherence; deceleration is natural plateau
            loki_ruin_threshold = 0.95
        elif nci > 85 and signal_cls == "decelerating":
            # High but not ceiling-adjacent: give some benefit of the doubt
            loki_ruin_threshold = 0.85
        else:
            # Standard threshold for all other cases
            loki_ruin_threshold = 0.70
        ruin_by_loki = loki_threat > loki_ruin_threshold and loki_structural
        ruin_by_abort = lab_rec == "ABORT"

        ruin_detected = ruin_by_irreversibility or ruin_by_loki or ruin_by_abort

        # Ruin probability estimate
        ruin_prob = 0.0
        if ruin_by_irreversibility:
            ruin_prob += irreversibility * 0.4
        if ruin_by_loki:
            ruin_prob += loki_threat * 0.4
        if ruin_by_abort:
            ruin_prob += 0.3
        ruin_prob = round(min(1.0, ruin_prob), 3)

        # Court trigger: ruin detected OR explicit ABORT
        court_trigger = ruin_detected and (irreversibility > 0.7 or ruin_by_abort)

        ruin_scenario = (
            f"{'High irreversibility (' + str(irreversibility) + ') — commitment cannot be undone. ' if ruin_by_irreversibility else ''}"
            f"{'Structural Loki challenge cannot be dismissed — fundamental flaw detected. ' if ruin_by_loki else ''}"
            f"{'LAB board voted ABORT — consensus is to not proceed. ' if ruin_by_abort else ''}"
            if ruin_detected else
            "No ruin-level risk detected. Signal and commitment profile are within recoverable bounds."
        )

        mitigation = (
            "STOP. Do not commit resources. Invoke Constitutional Court review (Phase 4). "
            "Run Kintsugi diagnostic on existing receipts. "
            "Reframe with Curator operator before reconsidering."
            if ruin_detected else
            "Standard monitoring. Log receipt. Proceed with normal phase gate check."
        )

        return RuinAssessment(
            ruin_detected=ruin_detected,
            ruin_scenario=ruin_scenario,
            ruin_probability=ruin_prob,
            irreversibility_score=irreversibility,
            court_trigger=court_trigger,
            mitigation=mitigation,
        )

    # ── Main Run ─────────────────────────────

    def run(
        self,
        sage_receipt: CoherenceReceipt,
        lab_assessment: LABAssessment,
        phase_id: str,
    ) -> BARAssessment:
        baseline  = self.assess_baseline(sage_receipt, lab_assessment)
        asymmetry = self.assess_asymmetry(sage_receipt, lab_assessment)
        ruin      = self.assess_ruin(sage_receipt, lab_assessment)

        # Verdict
        if ruin.ruin_detected:
            verdict = "RUIN_RISK"
        elif asymmetry.bet_quality == "STRONG" and baseline.floor_is_acceptable:
            verdict = "STRONG"
        elif asymmetry.bet_quality in {"ACCEPTABLE", "MARGINAL"} and baseline.floor_is_acceptable:
            verdict = "ACCEPTABLE"
        else:
            verdict = "CAUTION"

        summary = (
            f"Baseline floor NCI: {baseline.floor_nci:.1f} ({'acceptable' if baseline.floor_is_acceptable else 'BELOW THRESHOLD'}). "
            f"Asymmetry ratio: {asymmetry.asymmetry_ratio:.2f}x ({asymmetry.bet_quality}). "
            f"Kelly fraction: {asymmetry.kelly_fraction:.2f}. "
            f"Ruin: {'⚠ DETECTED' if ruin.ruin_detected else '✓ clear'}. "
            f"BAR verdict: {verdict}."
        )

        return BARAssessment(
            signal_label=sage_receipt.signal_label,
            phase_id=phase_id,
            baseline=baseline,
            asymmetry=asymmetry,
            ruin=ruin,
            bar_verdict=verdict,
            bar_summary=summary,
        )

    def print_assessment(self, assessment: BARAssessment) -> None:
        print("\n" + "=" * 60)
        print(f"  BAR ASSESSMENT — {assessment.signal_label}")
        print("=" * 60)
        b, a, r = assessment.baseline, assessment.asymmetry, assessment.ruin

        print(f"\n── B: Baseline ──────────────────────────────────────────")
        print(f"  Floor NCI   : {b.floor_nci:.1f} ({'✅ acceptable' if b.floor_is_acceptable else '❌ BELOW THRESHOLD'})")
        print(f"  Recovery    : {b.recovery_path[:75]}...")

        print(f"\n── A: Asymmetry ─────────────────────────────────────────")
        print(f"  Upside      : {a.upside_magnitude:.3f}")
        print(f"  Downside    : {a.downside_magnitude:.3f}")
        print(f"  Ratio       : {a.asymmetry_ratio:.2f}x — {a.bet_quality}")
        print(f"  Kelly       : {a.kelly_fraction:.2f} (optimal bet size fraction)")

        print(f"\n── R: Ruin ──────────────────────────────────────────────")
        ruin_icon = "🛑" if r.ruin_detected else "✅"
        print(f"  Ruin detected : {ruin_icon} {r.ruin_detected}")
        print(f"  Probability   : {r.ruin_probability:.3f}")
        print(f"  Court trigger : {'⚖  YES' if r.court_trigger else 'No'}")
        if r.ruin_detected:
            print(f"  Scenario      : {r.ruin_scenario[:80]}...")

        print(f"\n── Verdict ──────────────────────────────────────────────")
        print(f"  {assessment.bar_verdict}: {assessment.bar_summary}")
        print("=" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np
    from arcs_operators_sage import SAGEOperator
    from arcs_operators_lab import LABOperator

    print("=== BAR Operator Smoke Test ===\n")

    signal = CoherenceSignal(
        signal=np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float),
        domain="meta", label="ARCS build NCI progression",
    )
    from arcs_primitives import FATEDReasoning, SomaticReading
    fated = FATEDReasoning(
        facts="Phase 2 complete. SAGE + LAB operational.",
        assumptions="BAR will confirm favorable risk geometry for Phase 3.",
        tradeoffs="BAR adds risk assessment overhead; prevents ruin-level commits.",
        emotions="Confident. No ruin signals expected for this build phase.",
        direction="Build BAR, Curator, pipeline, store. Issue Phase 3 receipt.",
    )
    axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
    somatic = SomaticReading(0.85, 0.90, 0.88, 0.80, 0.92, 0.80)

    from arcs_primitives import AxiomCheck
    sage = SAGEOperator()
    sage_receipt = sage.run(
        signal=signal, fated=fated, axioms=axioms, somatic=somatic,
        hci_score=88.0, phase_id="phase_3",
        next_action="BAR risk assessment",
        irreversibility=0.15,
    )

    lab = LABOperator()
    lab_assessment = lab.run(sage_receipt=sage_receipt, phase_id="phase_3")

    bar = BAROperator()
    bar_assessment = bar.run(sage_receipt, lab_assessment, phase_id="phase_3")
    bar.print_assessment(bar_assessment)
    print("\n✅ BAR operator verified.")
