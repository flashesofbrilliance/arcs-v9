"""
arcs_operators_curator.py
ARCS v9 — Curator Operator
Phase 3: READ-WRITE

CURATOR: The Orthogonal Reframe Operator.
  One reframe. Not two. Not three. One.
  The Curator finds the frame shift that reveals what SAGE, LAB, and BAR missed.

Canon: "CUR — Curator (one orthogonal reframe)" from Decision Geometry Macros.
  Orthogonal = perpendicular to current framing.
  If everyone is arguing about X, the Curator asks: "What if X is the wrong question?"

Role in pipeline:
  - Runs AFTER BAR (final lens before pipeline receipt)
  - Takes the full context (SAGE + LAB + BAR) and produces ONE reframe
  - Does NOT override the other operators — it adds a perpendicular view
  - If Curator reframe changes the direction, it loops back to SAGE with new framing

NOTOMATION: Curator offers the reframe. Humans decide whether to adopt it.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from arcs_primitives import CoherenceReceipt
from arcs_operators_lab import LABAssessment
from arcs_operators_bar import BARAssessment

CURATOR_VERSION = "v9.0-phase3"

# ─────────────────────────────────────────────
# REFRAME STRATEGIES
# ─────────────────────────────────────────────

REFRAME_STRATEGIES = {
    "zoom_out": (
        "Zoom out one level. What does this look like from the Galactic (all decisions) "
        "perspective, not just this signal? Is this signal representative of the larger "
        "system, or an edge case?"
    ),
    "invert": (
        "Invert the question. Instead of 'how do we maximize this signal?', ask: "
        "'what would a coherent system look like if this signal didn't exist?' "
        "Is the signal load-bearing, or incidental?"
    ),
    "time_shift": (
        "Shift the time horizon. This analysis is optimized for the current window. "
        "What does the decision look like in 10x the current timeframe? "
        "Does the signal still matter, or does it dissolve?"
    ),
    "identity_check": (
        "Check identity coherence. Is this decision consistent with the system's DNA axioms? "
        "Or is it a Shapeshifter moment — adapting to external pressure in a way that "
        "drifts from core identity?"
    ),
    "constraint_removal": (
        "Remove the primary constraint. The current framing assumes [constraint] is fixed. "
        "What if it isn't? What decision emerges when the constraint is lifted? "
        "Is the constraint real, or inherited?"
    ),
    "second_order": (
        "Ask the second-order question. The immediate signal suggests [action]. "
        "But what does [action] enable or prevent downstream? "
        "The second-order effect may matter more than the first-order signal."
    ),
}


@dataclass
class CuratorReframe:
    """
    The Curator's one orthogonal reframe.
    One frame. Clear. Perpendicular to the current analysis axis.
    """
    reframe_type:     str    # Which reframe strategy was applied
    reframe_question: str    # The exact question that reframes the problem
    reframe_insight:  str    # What this reframe reveals that the other operators missed
    adoption_cost:    float  # 0.0 = costless to adopt, 1.0 = requires full restart
    worth_adopting:   bool   # Curator's own assessment: should human adopt this?
    adoption_note:    str    # Specific guidance if adopted

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reframe_type": self.reframe_type,
            "reframe_question": self.reframe_question,
            "reframe_insight": self.reframe_insight,
            "adoption_cost": self.adoption_cost,
            "worth_adopting": self.worth_adopting,
            "adoption_note": self.adoption_note,
        }


@dataclass
class CuratorAssessment:
    """Full Curator output."""
    signal_label: str
    phase_id:     str
    timestamp:    float = field(default_factory=time.time)
    reframe:      Optional[CuratorReframe] = None
    curator_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_label": self.signal_label,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp,
            "reframe": self.reframe.to_dict() if self.reframe else None,
            "curator_note": self.curator_note,
        }


# ─────────────────────────────────────────────
# CURATOR OPERATOR
# ─────────────────────────────────────────────

class CuratorOperator:
    """
    Curator: One Orthogonal Reframe.

    Selects the reframe strategy most likely to reveal a blind spot
    given the signal state, LAB threats, and BAR risk geometry.
    """

    def __init__(self):
        self.version = CURATOR_VERSION
        self.operator_name = "CURATOR"

    def _select_strategy(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
        bar: BARAssessment,
    ) -> str:
        """
        Selects the most orthogonal reframe strategy based on context.
        Prioritizes based on what the other operators highlighted.
        """
        # If ruin was detected, identity check is most important
        if bar.ruin and bar.ruin.ruin_detected:
            return "identity_check"

        # If LAB had a structural Loki challenge, invert the question
        if lab.loki and not lab.loki.can_be_dismissed and lab.loki.threat_score() > 0.5:
            return "invert"

        # If BAR asymmetry is marginal or unfavorable, check constraints
        if bar.asymmetry and bar.asymmetry.bet_quality in {"MARGINAL", "UNFAVORABLE"}:
            return "constraint_removal"

        # If signal is decelerating, time shift perspective
        if sage_receipt.signal_classification == "decelerating":
            return "time_shift"

        # If NCI is high but HCI/PCI gap is large, second-order check
        if sage_receipt.hci_pci_gap() > 15:
            return "second_order"

        # Default: zoom out for clarity
        return "zoom_out"

    def run(
        self,
        sage_receipt: CoherenceReceipt,
        lab_assessment: LABAssessment,
        bar_assessment: BARAssessment,
        phase_id: str,
    ) -> CuratorAssessment:
        strategy = self._select_strategy(sage_receipt, lab_assessment, bar_assessment)
        strategy_template = REFRAME_STRATEGIES[strategy]

        # Build the reframe question from context
        classification = sage_receipt.signal_classification
        nci = sage_receipt.nci_score
        lab_rec = lab_assessment.lab_recommendation
        bar_verdict = bar_assessment.bar_verdict

        reframe_question = (
            f"[{strategy.upper().replace('_', ' ')}] "
            f"Current framing: '{classification}' signal, NCI {nci:.1f}, "
            f"LAB says {lab_rec}, BAR says {bar_verdict}. "
            f"Reframe: {strategy_template}"
        )

        # Insight: what this specific reframe reveals
        insight_map = {
            "zoom_out": (
                f"At the Galactic level, this '{classification}' signal is one data point "
                f"in a larger NCI arc. The question is not 'is this signal coherent?' but "
                f"'is this signal part of a coherent larger pattern?' Zoom out before committing."
            ),
            "invert": (
                f"Loki's challenge ({lab_assessment.loki.threat_score():.2f} threat) "
                f"is more useful inverted: not 'why might this fail?' but "
                f"'what would have to be true for this to succeed unconditionally?' "
                f"If you can't answer that, you don't understand the signal yet."
            ),
            "time_shift": (
                f"Decelerating at {sage_receipt.five_derivatives.get('deceleration', 0):.0%} of timesteps. "
                f"In 10x the current window, is this deceleration a temporary plateau "
                f"(signal continues after rest) or structural ceiling (the signal is done)? "
                f"The answer changes the entire risk geometry."
            ),
            "identity_check": (
                f"Ruin risk detected (BAR: {bar_verdict}). Before any other consideration: "
                f"does proceeding violate any of the four DNA axioms at their core? "
                f"Specifically: does it compromise Agency over Automation? "
                f"If yes, ruin is being invited, not just risked."
            ),
            "constraint_removal": (
                f"BAR asymmetry is {bar_assessment.asymmetry.bet_quality if bar_assessment.asymmetry else 'unknown'}. "
                f"What is the primary constraint making this bet marginal? "
                f"Is that constraint real (physics, law, hard resource limit) "
                f"or inherited (prior assumption that was never validated)? "
                f"Inherited constraints are reframeable."
            ),
            "second_order": (
                f"HCI/PCI gap is {sage_receipt.hci_pci_gap():.1f} points. "
                f"This gap means human assessment and platform assessment diverge. "
                f"The second-order question: why do they diverge? "
                f"The divergence itself is signal — it may matter more than either score."
            ),
        }
        insight = insight_map.get(strategy, "Reframe applied.")

        # Adoption cost: how much does adopting this reframe cost?
        cost_map = {
            "zoom_out": 0.1,           # Easy — just a perspective shift
            "invert": 0.2,             # Medium — requires re-asking the core question
            "time_shift": 0.15,        # Low — just a mental model shift
            "identity_check": 0.05,    # Very low — a yes/no check
            "constraint_removal": 0.4, # Higher — may invalidate prior work
            "second_order": 0.2,       # Medium — adds analysis depth
        }
        adoption_cost = cost_map.get(strategy, 0.2)
        worth_adopting = adoption_cost < 0.35 or bar_assessment.bar_verdict in {"RUIN_RISK", "CAUTION"}

        adoption_note = (
            f"Adopt by: adding one FATED dimension for '{strategy}' framing. "
            f"{'Low cost — do this before final receipt.' if adoption_cost < 0.2 else 'Medium cost — consider in next phase entry gate.'}"
        )

        reframe = CuratorReframe(
            reframe_type=strategy,
            reframe_question=reframe_question,
            reframe_insight=insight,
            adoption_cost=adoption_cost,
            worth_adopting=worth_adopting,
            adoption_note=adoption_note,
        )

        curator_note = (
            f"One reframe applied: {strategy.upper().replace('_', ' ')}. "
            f"Adoption cost: {adoption_cost:.2f}. "
            f"{'Worth adopting before final receipt.' if worth_adopting else 'Low priority — file for reference.'}"
        )

        return CuratorAssessment(
            signal_label=sage_receipt.signal_label,
            phase_id=phase_id,
            reframe=reframe,
            curator_note=curator_note,
        )

    def print_assessment(self, assessment: CuratorAssessment) -> None:
        print("\n" + "=" * 60)
        print(f"  CURATOR — {assessment.signal_label}")
        print("=" * 60)
        r = assessment.reframe
        print(f"\n  Reframe type   : {r.reframe_type.upper().replace('_', ' ')}")
        print(f"  Worth adopting : {'✅ YES' if r.worth_adopting else '○ No'}")
        print(f"  Adoption cost  : {r.adoption_cost:.2f}")
        print(f"\n  Question:\n    {r.reframe_question[:120]}...")
        print(f"\n  Insight:\n    {r.reframe_insight[:120]}...")
        print(f"\n  Adoption note  : {r.adoption_note}")
        print("=" * 60)


if __name__ == "__main__":
    import numpy as np
    from arcs_operators_sage import SAGEOperator
    from arcs_operators_lab import LABOperator
    from arcs_operators_bar import BAROperator
    from arcs_primitives import FATEDReasoning, SomaticReading, AxiomCheck

    signal = CoherenceSignal(
        signal=np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float),
        domain="meta", label="ARCS build NCI progression",
    )
    fated = FATEDReasoning("Phase 2 complete.", "Curator will find the blind spot.", "Ceremony vs speed.", "Confident.", "Build and ship.")
    axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
    somatic = SomaticReading(0.85, 0.90, 0.88, 0.80, 0.92, 0.80)

    sage = SAGEOperator()
    sage_r = sage.run(signal=signal, fated=fated, axioms=axioms, somatic=somatic,
                      hci_score=88.0, phase_id="phase_3", next_action="curator",
                      irreversibility=0.15)
    lab = LABOperator()
    lab_r = lab.run(sage_r, "phase_3")
    bar = BAROperator()
    bar_r = bar.run(sage_r, lab_r, "phase_3")
    cur = CuratorOperator()
    cur_r = cur.run(sage_r, lab_r, bar_r, "phase_3")
    cur.print_assessment(cur_r)
    print("\n✅ Curator operator verified.")
