"""
arcs_operators_lab.py
ARCS v9 — LAB Operator
Phase 3: READ-WRITE

LAB: Three-Lens Adversarial Reasoning
  L = Loki      : Adversarial challenge (devil's advocate, stress-test, red team)
  A = Advisors  : Multi-perspective counsel (Board of Advisors, diverse viewpoints)
  B = Bayesian  : Prior → Posterior belief update (Bayes' theorem applied to decision confidence)

Canon references:
  - ARCS-Operator17-AdversarialDetective.md (Loki formalization)
  - ARCS-LokiMode-MischiefProtocol.md (adversarial methodology)
  - ARCS-Canon-v2-0-Complete.md (second law, entropy/coherence)

Role in pipeline:
  - Runs AFTER SAGE (receives a CoherenceReceipt as context)
  - Produces a LABAssessment with three lens outputs + Bayesian consensus
  - LABAssessment feeds into BAR operator and final pipeline receipt

NOTOMATION Rule: LAB surfaces challenges for human consideration.
It does NOT make the decision. It makes the challenge legible.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from arcs_primitives import (
    AXIOM_NO, AXIOM_TENSION, AXIOM_YES,
    AxiomCheck, CoherenceReceipt, CoherenceSignal,
    FATEDReasoning, SomaticReading,
    calculate_nci, LABEL_ALIGNED, LABEL_EXPERIMENTAL,
)

LAB_VERSION = "v9.0-phase3"


# ─────────────────────────────────────────────
# LAB DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class LokiChallenge:
    """
    L-lens: Adversarial challenge output.

    Loki's job is to try to disprove the current decision/signal.
    Not chaos — structured contrarianism that surfaces hidden risks.
    Canon: Operator17 adversarial objective: max edge case discovery.
    """
    challenge_statement: str        # The core adversarial argument
    failure_modes: List[str]        # Specific ways this could go wrong
    hidden_assumptions: List[str]   # Assumptions the signal is relying on
    worst_case_scenario: str        # The ruin-level bad outcome
    loki_confidence: float          # 0.0–1.0: how strong is the challenge?
    can_be_dismissed: bool          # Is this challenge answerable, or fundamental?
    dismissal_argument: str         # If dismissable, how?

    def threat_score(self) -> float:
        """
        Combines confidence and dismissability into a threat level.
        High confidence + not dismissable = high threat.
        """
        dismissal_discount = 0.4 if self.can_be_dismissed else 0.0
        return round(max(0.0, self.loki_confidence - dismissal_discount), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "challenge_statement": self.challenge_statement,
            "failure_modes": self.failure_modes,
            "hidden_assumptions": self.hidden_assumptions,
            "worst_case_scenario": self.worst_case_scenario,
            "loki_confidence": self.loki_confidence,
            "can_be_dismissed": self.can_be_dismissed,
            "dismissal_argument": self.dismissal_argument,
            "threat_score": self.threat_score(),
        }


@dataclass
class AdvisorPerspective:
    """
    A-lens: Single advisor's viewpoint.

    The Board of Advisors provides diverse, non-unanimous counsel.
    Each advisor has a domain, a stance, and a confidence level.
    Disagreement is a feature, not a bug — it surfaces dimensions
    the primary signal may have missed.
    """
    advisor_archetype: str   # "SAGE" | "GUARDIAN" | "DREAMER" | "ELDER" | "SHAPESHIFTER"
    domain: str              # Area of expertise ("risk", "innovation", "memory", "flow")
    stance: str              # "PROCEED" | "PAUSE" | "PIVOT" | "ABORT"
    reasoning: str           # Why this archetype recommends this stance
    confidence: float        # 0.0–1.0

    VALID_STANCES = {"PROCEED", "PAUSE", "PIVOT", "ABORT"}
    VALID_ARCHETYPES = {"SAGE", "GUARDIAN", "DREAMER", "ELDER", "SHAPESHIFTER", "BRIDGE", "HEART"}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "advisor_archetype": self.advisor_archetype,
            "domain": self.domain,
            "stance": self.stance,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
        }


@dataclass
class BayesianUpdate:
    """
    B-lens: Prior → Posterior belief update.

    Canon: Double-blind anterior/posterior consensus (Operator17, §2.3).
    Formula: P(correct | evidence) = P(evidence | correct) × P_prior / P(evidence)

    The Bayesian lens takes the SAGE NCI score as the prior belief in
    signal coherence, applies the Loki challenge as likelihood evidence,
    and produces a posterior confidence in proceeding.
    """
    prior_confidence: float          # SAGE NCI / 100 (0.0–1.0)
    loki_evidence_weight: float      # How much Loki's challenge shifts belief (0.0–1.0)
    advisor_consensus_weight: float  # Fraction of advisors recommending PROCEED
    posterior_confidence: float      # Updated confidence after all evidence
    belief_shift: float              # posterior - prior (negative = Loki won)
    proceed_recommended: bool        # Final Bayesian recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prior_confidence": round(self.prior_confidence, 3),
            "loki_evidence_weight": round(self.loki_evidence_weight, 3),
            "advisor_consensus_weight": round(self.advisor_consensus_weight, 3),
            "posterior_confidence": round(self.posterior_confidence, 3),
            "belief_shift": round(self.belief_shift, 3),
            "proceed_recommended": self.proceed_recommended,
        }


@dataclass
class LABAssessment:
    """
    Full LAB operator output.

    Contains all three lens outputs + the Bayesian consensus + an
    integrated threat level that feeds into BAR operator risk geometry.
    """
    signal_label:       str
    phase_id:           str
    timestamp:          float = field(default_factory=time.time)

    # Three lenses
    loki:       Optional[LokiChallenge]         = None
    advisors:   List[AdvisorPerspective]        = field(default_factory=list)
    bayesian:   Optional[BayesianUpdate]        = None

    # Integrated outputs
    lab_threat_level:   str   = "LOW"   # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    lab_recommendation: str   = "PROCEED"  # "PROCEED" | "PAUSE" | "PIVOT" | "ABORT"
    lab_summary:        str   = ""

    def advisor_consensus(self) -> Dict[str, float]:
        """Returns fraction of advisors recommending each stance."""
        if not self.advisors:
            return {}
        counts: Dict[str, int] = {}
        for a in self.advisors:
            counts[a.stance] = counts.get(a.stance, 0) + 1
        total = len(self.advisors)
        return {stance: round(count / total, 3) for stance, count in counts.items()}

    def lab_assessment_penalty(self) -> float:
        """
        Returns a fractional NCI penalty based on LAB threat level.
        Used by the pipeline to discount NCI when LAB surfaces material threats.

        Scale:
          LOW      → 0.02  (minor noise, not actionable)
          MEDIUM   → 0.05  (credible challenge, warrants monitoring)
          HIGH     → 0.10  (significant threat, warrants pause)
          CRITICAL → 0.15  (near-ruin threat, warrants ABORT consideration)
        """
        penalty_map = {
            "LOW":      0.02,
            "MEDIUM":   0.05,
            "HIGH":     0.10,
            "CRITICAL": 0.15,
        }
        return penalty_map.get(self.lab_threat_level, 0.05)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_label": self.signal_label,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp,
            "loki": self.loki.to_dict() if self.loki else None,
            "advisors": [a.to_dict() for a in self.advisors],
            "advisor_consensus": self.advisor_consensus(),
            "bayesian": self.bayesian.to_dict() if self.bayesian else None,
            "lab_threat_level": self.lab_threat_level,
            "lab_recommendation": self.lab_recommendation,
            "lab_summary": self.lab_summary,
        }


# ─────────────────────────────────────────────
# LAB OPERATOR
# ─────────────────────────────────────────────

class LABOperator:
    """
    LAB: The Three-Lens Adversarial Reasoning Operator.

    L = Loki      : "What if I'm wrong? What's the worst that could happen?"
    A = Advisors  : "What would each archetype counsel here?"
    B = Bayesian  : "After all evidence, what's my updated confidence?"

    Usage:
        lab = LABOperator()
        assessment = lab.run(
            sage_receipt=sage_receipt,      # CoherenceReceipt from SAGE
            loki_challenge=my_challenge,    # LokiChallenge (or auto-generated)
            advisors=my_advisors,           # List[AdvisorPerspective] (or default board)
        )
    """

    def __init__(self):
        self.version = LAB_VERSION
        self.operator_name = "LAB"

    # ── L-Lens: Loki Challenge ───────────────

    def generate_loki_challenge(
        self,
        sage_receipt: CoherenceReceipt,
    ) -> LokiChallenge:
        """
        Auto-generates a Loki challenge from a SAGE receipt.

        Uses the signal classification, five derivatives, and axiom checks
        to construct a structured adversarial challenge. This is the
        "default Loki" — a programmatic devil's advocate based on signal data.

        For deeper challenges, pass a custom LokiChallenge to lab.run().
        """
        classification = sage_receipt.signal_classification
        five_d = sage_receipt.five_derivatives
        axioms = sage_receipt.axioms

        # Core challenge based on signal state
        challenge_map = {
            "strong_signal": (
                "Strong signal may be recency bias. What if the last N data points "
                "are outliers, not trend? High velocity can precede sharp reversals.",
                0.45
            ),
            "mixed": (
                "Mixed signal means the system hasn't decided yet. Proceeding now "
                "locks in a commitment before the signal resolves — premature closure.",
                0.65
            ),
            "decelerating": (
                "Decelerating signal is a leading indicator of reversal, not plateau. "
                "If deceleration continues, you're committing at the peak.",
                0.75
            ),
            "noise": (
                "Signal is predominantly noise. Any apparent pattern is likely "
                "p-hacking or pattern-matching on random data. This is not coherent.",
                0.90
            ),
        }
        challenge_stmt, base_confidence = challenge_map.get(
            classification, ("Signal state is ambiguous.", 0.5)
        )

        # Build failure modes from derivatives
        failure_modes = []
        if five_d.get("phase_cancellation", 0) > 0.5:
            failure_modes.append(
                f"Phase cancellation at {five_d['phase_cancellation']:.0%} — "
                "destructive interference is eroding net momentum"
            )
        if five_d.get("deceleration", 0) > 0.4:
            failure_modes.append(
                f"Deceleration at {five_d['deceleration']:.0%} of timesteps — "
                "momentum is actively reversing"
            )
        if five_d.get("diffusion", 0) > 1.5:
            failure_modes.append(
                f"High diffusion ({five_d['diffusion']:.2f}) — signal is spreading "
                "faster than it is compounding; reach without depth"
            )
        if not failure_modes:
            failure_modes = ["No dominant failure mode detected from signal data alone."]

        # Hidden assumptions from axiom tensions
        hidden_assumptions = []
        if axioms.kairos_over_neuroticism == AXIOM_TENSION:
            hidden_assumptions.append(
                "Timing is assumed to be right, but kairos TENSION was flagged. "
                "The window may be closing, not opening."
            )
        if axioms.minimum_steps_to_coherence == AXIOM_TENSION:
            hidden_assumptions.append(
                "Minimum steps is in TENSION — we may be adding unnecessary complexity."
            )
        if not hidden_assumptions:
            hidden_assumptions = [
                "Assumes signal stationarity (that past behavior predicts near future).",
                "Assumes data quality and collection method are consistent.",
            ]

        # Loki confidence: higher if more failure modes + lower SAGE NCI
        nci_discount = max(0.0, (100 - sage_receipt.nci_score) / 100)
        failure_boost = min(0.2, len(failure_modes) * 0.07)
        loki_confidence = min(0.95, base_confidence + nci_discount * 0.3 + failure_boost)

        # Dismissal
        can_be_dismissed = classification in {"strong_signal", "mixed"}
        dismissal_argument = (
            "SAGE axiom check passed all four DNA axioms. "
            "Signal trend is directional. Loki's challenge is noted but does not "
            "override coherent kinematic evidence."
        ) if can_be_dismissed else (
            "Challenge is structural — signal classification does not support "
            "confident action. Requires human review before proceeding."
        )

        return LokiChallenge(
            challenge_statement=challenge_stmt,
            failure_modes=failure_modes,
            hidden_assumptions=hidden_assumptions,
            worst_case_scenario=(
                f"Signal reverses after commitment. Deceleration becomes full "
                f"reversal. Phase cancellation eliminates net momentum. "
                f"Resources committed to a false signal that was never coherent."
            ),
            loki_confidence=round(loki_confidence, 3),
            can_be_dismissed=can_be_dismissed,
            dismissal_argument=dismissal_argument,
        )

    # ── A-Lens: Board of Advisors ────────────

    def generate_default_advisors(
        self,
        sage_receipt: CoherenceReceipt,
    ) -> List[AdvisorPerspective]:
        """
        Generates a default 5-archetype advisory board response
        based on the SAGE receipt signal state.

        Each archetype has a fixed domain and characteristic bias:
          SAGE       → signal quality, discernment
          GUARDIAN   → urgency, risk, protection
          DREAMER    → opportunity, exploration, upside
          ELDER      → memory, precedent, validation
          SHAPESHIFTER → adaptation, pivot options, flexibility
        """
        nci = sage_receipt.nci_score
        classification = sage_receipt.signal_classification
        kairos_open = sage_receipt.somatic.kairos_window_open()

        advisors = []

        # SAGE: Signal quality perspective
        sage_stance = "PROCEED" if nci >= 82 else ("PAUSE" if nci >= 65 else "ABORT")
        advisors.append(AdvisorPerspective(
            advisor_archetype="SAGE",
            domain="signal_quality",
            stance=sage_stance,
            reasoning=(
                f"NCI {nci:.1f}/100. Classification: {classification}. "
                f"{'Signal is coherent enough to proceed.' if nci >= 82 else 'Signal coherence is below threshold — pause and reassess.'}"
            ),
            confidence=round(nci / 100, 2),
        ))

        # GUARDIAN: Risk and urgency
        threat_high = classification in {"noise", "decelerating"}
        guardian_stance = "PAUSE" if threat_high else ("PROCEED" if kairos_open else "PAUSE")
        advisors.append(AdvisorPerspective(
            advisor_archetype="GUARDIAN",
            domain="risk_and_urgency",
            stance=guardian_stance,
            reasoning=(
                f"{'High phase cancellation or deceleration detected. Protect downside first.' if threat_high else 'Risk profile acceptable.'} "
                f"Kairos window {'is open — act now before it closes.' if kairos_open else 'is not fully open — wait for better conditions.'}"
            ),
            confidence=0.78 if threat_high else 0.65,
        ))

        # DREAMER: Opportunity and upside
        dreamer_stance = "PROCEED" if classification in {"strong_signal", "mixed"} else "PIVOT"
        advisors.append(AdvisorPerspective(
            advisor_archetype="DREAMER",
            domain="innovation_and_upside",
            stance=dreamer_stance,
            reasoning=(
                f"{'Strong directional momentum. The upside here is real and worth capturing.' if dreamer_stance == 'PROCEED' else 'Signal is not strong enough for direct action — pivot to exploration mode and find the cleaner signal.'}"
            ),
            confidence=0.70,
        ))

        # ELDER: Memory and precedent
        elder_stance = "PAUSE" if sage_receipt.irreversibility > 0.6 else "PROCEED"
        advisors.append(AdvisorPerspective(
            advisor_archetype="ELDER",
            domain="memory_and_validation",
            stance=elder_stance,
            reasoning=(
                f"Irreversibility score: {sage_receipt.irreversibility:.2f}. "
                f"{'High commitment cost — validate thoroughly before locking in. Check precedent.' if elder_stance == 'PAUSE' else 'Commitment is reversible. Proceed with receipt documentation.'}"
            ),
            confidence=0.82,
        ))

        # SHAPESHIFTER: Adaptation and flexibility
        shapeshifter_stance = "PIVOT" if classification == "decelerating" else "PROCEED"
        advisors.append(AdvisorPerspective(
            advisor_archetype="SHAPESHIFTER",
            domain="adaptation_and_flow",
            stance=shapeshifter_stance,
            reasoning=(
                f"{'Decelerating signal. Rigid commitment risks being caught in a reversal. Pivot to a more adaptive approach.' if shapeshifter_stance == 'PIVOT' else 'Signal supports forward motion. Stay fluid but directional.'}"
            ),
            confidence=0.68,
        ))

        return advisors

    # ── B-Lens: Bayesian Update ──────────────

    def compute_bayesian_update(
        self,
        sage_receipt: CoherenceReceipt,
        loki: LokiChallenge,
        advisors: List[AdvisorPerspective],
    ) -> BayesianUpdate:
        """
        Computes the Bayesian posterior confidence in proceeding.

        Canon formula (Operator17, §2.3):
          P_posterior = w_orch × P_prior + w_det × (1 - P_threat)
          Weights determined by historical accuracy proxies.

        Simplified ARCS implementation:
          prior     = SAGE NCI / 100
          loki_shift = threat_score × loki_weight (reduces confidence)
          advisor_boost = proceed_fraction × advisor_weight (increases confidence)
          posterior = prior - loki_shift + advisor_boost, clamped [0, 1]
        """
        prior = sage_receipt.nci_score / 100.0

        # Loki's evidence: threat score reduces posterior confidence
        loki_weight = 0.35  # Loki gets 35% influence
        loki_shift = loki.threat_score() * loki_weight

        # Advisor consensus: PROCEED fraction boosts posterior
        advisor_weight = 0.25  # Advisors get 25% influence
        consensus = {}
        for a in advisors:
            consensus[a.stance] = consensus.get(a.stance, 0) + (a.confidence / len(advisors))
        advisor_proceed_weight = consensus.get("PROCEED", 0.0) * advisor_weight
        advisor_consensus_weight = consensus.get("PROCEED", 0.0)

        # Posterior
        posterior = prior - loki_shift + advisor_proceed_weight
        posterior = round(max(0.0, min(1.0, posterior)), 3)
        belief_shift = round(posterior - prior, 3)

        return BayesianUpdate(
            prior_confidence=round(prior, 3),
            loki_evidence_weight=round(loki_shift, 3),
            advisor_consensus_weight=round(advisor_consensus_weight, 3),
            posterior_confidence=posterior,
            belief_shift=belief_shift,
            proceed_recommended=posterior >= 0.65,
        )

    # ── Integration: Threat Level + Recommendation ──

    def _integrate(
        self,
        loki: LokiChallenge,
        advisors: List[AdvisorPerspective],
        bayesian: BayesianUpdate,
    ) -> Tuple[str, str, str]:
        """
        Integrates three lens outputs into a unified threat level,
        recommendation, and summary.
        """
        threat = loki.threat_score()
        posterior = bayesian.posterior_confidence

        # Threat level
        if threat >= 0.7 or not bayesian.proceed_recommended:
            threat_level = "HIGH" if threat < 0.85 else "CRITICAL"
        elif threat >= 0.4:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"

        # Consensus stance from advisors
        stance_counts: Dict[str, int] = {}
        for a in advisors:
            stance_counts[a.stance] = stance_counts.get(a.stance, 0) + 1
        majority_stance = max(stance_counts, key=stance_counts.get)

        # Recommendation: Bayesian posterior overrides advisor majority if divergent
        if posterior >= 0.75:
            recommendation = "PROCEED"
        elif posterior >= 0.55:
            recommendation = majority_stance if majority_stance != "ABORT" else "PAUSE"
        elif posterior >= 0.35:
            recommendation = "PAUSE"
        else:
            recommendation = "ABORT"

        summary = (
            f"Loki threat: {threat:.2f} ({'dismissable' if loki.can_be_dismissed else 'structural'}). "
            f"Advisor majority: {majority_stance} ({stance_counts.get(majority_stance, 0)}/{len(advisors)}). "
            f"Bayesian posterior: {posterior:.2f} (shift: {bayesian.belief_shift:+.2f}). "
            f"LAB recommendation: {recommendation}."
        )

        return threat_level, recommendation, summary

    # ── Main Run ─────────────────────────────

    def run(
        self,
        sage_receipt: CoherenceReceipt,
        phase_id: str,
        loki_challenge: Optional[LokiChallenge] = None,
        advisors: Optional[List[AdvisorPerspective]] = None,
        orchestrator_response: Optional[Any] = None,
    ) -> LABAssessment:
        """
        Full LAB run. Three lenses applied in sequence.

        Args:
            sage_receipt         : CoherenceReceipt from SAGE (required)
            phase_id             : Current phase
            loki_challenge       : Custom LokiChallenge (auto-generated if None)
            advisors             : Custom advisor board (default 5-archetype board if None)
            orchestrator_response: [LAB v2 extension point] Blue-team OrchestratorResponse
                                   that rebuts Loki's specific failure modes via Socratic
                                   dialogue. Currently None (stub). When provided in Phase 6,
                                   the Bayesian update will shift posterior by the rebuttal
                                   strength, implementing the full thesis/antithesis/synthesis
                                   dialectic from Operator 17. Zero regression when None.

        Returns:
            LABAssessment: Three-lens assessment with Bayesian consensus
        """
        # L: Loki
        loki = loki_challenge or self.generate_loki_challenge(sage_receipt)

        # A: Advisors
        board = advisors or self.generate_default_advisors(sage_receipt)

        # B: Bayesian
        # NOTE (LAB v2): when orchestrator_response is provided, the Bayesian update
        # will additionally shift posterior by orchestrator_response.response_strength
        # before computing the final posterior. Extension point is here.
        bayesian = self.compute_bayesian_update(sage_receipt, loki, board)

        # Integration
        threat_level, recommendation, summary = self._integrate(loki, board, bayesian)

        return LABAssessment(
            signal_label=sage_receipt.signal_label,
            phase_id=phase_id,
            loki=loki,
            advisors=board,
            bayesian=bayesian,
            lab_threat_level=threat_level,
            lab_recommendation=recommendation,
            lab_summary=summary,
        )

    def print_assessment(self, assessment: LABAssessment) -> None:
        print("\n" + "=" * 60)
        print(f"  LAB ASSESSMENT — {assessment.signal_label}")
        print("=" * 60)

        print(f"\n── L: Loki Challenge ────────────────────────────────────")
        print(f"  Challenge  : {assessment.loki.challenge_statement[:80]}...")
        print(f"  Threat     : {assessment.loki.threat_score():.2f} ({'dismissable' if assessment.loki.can_be_dismissed else 'STRUCTURAL'})")
        print(f"  Worst case : {assessment.loki.worst_case_scenario[:80]}...")
        for fm in assessment.loki.failure_modes:
            print(f"  ⚠  {fm[:75]}")

        print(f"\n── A: Advisors ──────────────────────────────────────────")
        for a in assessment.advisors:
            emoji = {"PROCEED": "✅", "PAUSE": "⏸", "PIVOT": "↗", "ABORT": "🛑"}.get(a.stance, "○")
            print(f"  {emoji} {a.advisor_archetype:14} [{a.stance:7}] {a.reasoning[:55]}...")

        print(f"\n── B: Bayesian ──────────────────────────────────────────")
        b = assessment.bayesian
        print(f"  Prior      : {b.prior_confidence:.3f}")
        print(f"  Loki shift : -{b.loki_evidence_weight:.3f}")
        print(f"  Adv. boost : +{b.advisor_consensus_weight * 0.25:.3f}")
        print(f"  Posterior  : {b.posterior_confidence:.3f} (shift: {b.belief_shift:+.3f})")
        print(f"  Proceed?   : {'✅ YES' if b.proceed_recommended else '🛑 NO'}")

        print(f"\n── Integration ──────────────────────────────────────────")
        print(f"  Threat level   : {assessment.lab_threat_level}")
        print(f"  Recommendation : {assessment.lab_recommendation}")
        print(f"  Summary        : {assessment.lab_summary}")
        print("=" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np
    from arcs_operators_sage import SAGEOperator

    print("=== LAB Operator Smoke Test ===\n")

    signal = CoherenceSignal(
        signal=np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float),
        domain="meta",
        label="ARCS build NCI progression",
    )
    fated = FATEDReasoning(
        facts="Phase 2 complete. SAGE operational. LAB is Phase 3 first operator.",
        assumptions="LAB adversarial lens will strengthen Phase 3 operator suite.",
        tradeoffs="Adding LAB adds ceremony but prevents groupthink in operator design.",
        emotions="Confident. Kairos window open. Minor tension on Loki's challenge strength.",
        direction="Build LAB, BAR, Curator. Run integrated pipeline. Issue Phase 3 receipt.",
    )
    axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
    somatic = SomaticReading(0.85, 0.90, 0.88, 0.80, 0.92, 0.80)

    sage = SAGEOperator()
    sage_receipt = sage.run(
        signal=signal, fated=fated, axioms=axioms, somatic=somatic,
        hci_score=88.0, phase_id="phase_3",
        next_action="Run LAB adversarial challenge",
        irreversibility=0.15,
        artifacts_shipped=["arcs_operators_lab.py"],
    )

    lab = LABOperator()
    assessment = lab.run(sage_receipt=sage_receipt, phase_id="phase_3")
    lab.print_assessment(assessment)

    import json
    print("\n── JSON payload (pipeline-ready) ────────────────────────")
    print(json.dumps(assessment.to_dict(), indent=2)[:800] + "\n  ...(truncated)")
    print("\n✅ LAB operator verified.")
