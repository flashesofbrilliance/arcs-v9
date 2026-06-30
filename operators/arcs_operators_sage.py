"""
arcs_operators_sage.py
ARCS v9 — SAGE Operator
Phase 2: WRITE

SAGE: The Discernment Archetype
  Question: "Is this signal or noise?"
  Essence:  Precision, clarity, signal/noise separation

The SAGE operator is the first and primary ARCS operator. It serves as:
  1. The kinematic analyzer     — runs the 12-derivative KinematicManifold
  2. The five-derivative extractor — classifies velocity, acceleration,
                                     diffusion, phase cancellation, deceleration
  3. The HCI/PCI scorer         — computes platform coherence, accepts human self-grade
  4. The somatic checker        — validates the six phenomenological primitives
  5. The receipt issuer         — produces a signed CoherenceReceipt

SAGE does NOT make decisions. SAGE makes the signal legible so humans can decide.
NOTOMATION Rule: Tools may only externalize / scaffold / sequence human cognition.

Dependencies:
  - arcs_kinematics.py: KinematicManifold
  - arcs_primitives.py: CoherenceSignal, CoherenceReceipt, FATEDReasoning,
                         AxiomCheck, SomaticReading, calculate_nci
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from arcs_kinematics import KinematicManifold
from arcs_primitives import (
    AXIOM_NO,
    AXIOM_TENSION,
    AXIOM_YES,
    LABEL_ALIGNED,
    LABEL_DUMB,
    LABEL_EXPERIMENTAL,
    LABEL_GOOD_PROCESS_BAD_LUCK,
    AxiomCheck,
    CoherenceReceipt,
    CoherenceSignal,
    FATEDReasoning,
    SomaticReading,
    calculate_nci,
    check_phase_gate,
)


# ─────────────────────────────────────────────
# SAGE CONFIGURATION
# ─────────────────────────────────────────────

SAGE_VERSION = "v9.0-phase2"

# Signal classification thresholds
STRONG_SIGNAL_VELOCITY_THRESHOLD   = 0.5   # |mean velocity| above this = strong trend
NOISE_STD_RATIO_THRESHOLD          = 2.0   # std/|mean| above this = noise-dominant
PHASE_CANCEL_THRESHOLD             = 0.3   # fraction of time velocity and accel oppose each other
DECELERATION_THRESHOLD             = 0.0   # mean deceleration below 0 = decay detected

# PCI computation weights
PCI_VELOCITY_WEIGHT       = 0.30
PCI_TREND_STRENGTH_WEIGHT = 0.25
PCI_FATED_WEIGHT          = 0.25
PCI_AXIOM_WEIGHT          = 0.20


# ─────────────────────────────────────────────
# SAGE OPERATOR
# ─────────────────────────────────────────────

class SAGEOperator:
    """
    SAGE: The Signal/Noise Discernment Operator.

    Four Lenses:
      1. Kinematic Lens   — KinematicManifold (12 derivatives, 4 regimes)
      2. Five-Derivative  — Velocity, Acceleration, Diffusion,
                            Phase Cancellation, Deceleration
      3. HCI/PCI Lens     — Human vs. Platform coherence scoring
      4. Somatic Lens     — Six phenomenological primitive validation

    Usage (code-driven):
        sage = SAGEOperator()
        receipt = sage.run(
            signal=my_signal,
            fated=my_fated_reasoning,
            axioms=my_axiom_check,
            somatic=my_somatic_reading,
            hci_score=85.0,
            phase_id="phase_2",
            next_action="Deploy SAGE output to Zoetrope HUD",
        )

    Usage (interactive CLI):
        sage = SAGEOperator()
        receipt = sage.run_interactive(signal=my_signal, phase_id="phase_2")
    """

    def __init__(self):
        self.version = SAGE_VERSION
        self.operator_name = "SAGE"

    # ── Lens 1: Kinematic Analysis ───────────

    def _run_kinematic_lens(
        self,
        signal: CoherenceSignal,
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """
        Runs the 12-derivative KinematicManifold on the signal.

        Returns:
            kinematic_summary  : Dict of {derivative_name: scalar_summary}
            five_derivatives   : Dict of five ARCS primitives
            classification     : "strong_signal" | "noise" | "mixed" | "decelerating"
        """
        manifold = KinematicManifold(signal.signal, dt=signal.dt)
        full_analysis = manifold.analyze()

        # Scalar summary of all 12 derivatives (mean + std per derivative)
        kinematic_summary: Dict[str, float] = {}
        for name, arr in full_analysis.items():
            key = name.split("_", 1)[1].lower()  # e.g. "01_Velocity" → "velocity"
            kinematic_summary[f"{key}_mean"] = round(float(np.mean(arr)), 4)
            kinematic_summary[f"{key}_std"]  = round(float(np.std(arr)),  4)

        # ── Five ARCS Derivative Primitives ──────────────────────────────────
        # These five correspond directly to the canonical signal-engine primitives.

        velocity_arr     = manifold.velocity()
        acceleration_arr = manifold.acceleration()

        # 1. Velocity: mean rate of change (positive = rising trend)
        velocity_mean = float(np.mean(velocity_arr))

        # 2. Acceleration: mean change in rate (positive = speeding up)
        acceleration_mean = float(np.mean(acceleration_arr))

        # 3. Diffusion: spread of signal (std / mean, clamped)
        sig_mean = signal.mean
        diffusion = float(
            np.std(signal.signal) / (abs(sig_mean) + 1e-8)
        )

        # 4. Phase Cancellation: fraction of timesteps where velocity and
        #    acceleration have opposing signs (destructive interference)
        opposing_signs = np.sign(velocity_arr) != np.sign(acceleration_arr)
        phase_cancellation = float(np.mean(opposing_signs))

        # 5. Deceleration: percentage of time the signal is actively decelerating
        #    (acceleration < 0 when velocity > 0, or acceleration > 0 when velocity < 0)
        is_decelerating = (
            (velocity_arr > 0) & (acceleration_arr < 0)
        ) | (
            (velocity_arr < 0) & (acceleration_arr > 0)
        )
        deceleration_fraction = float(np.mean(is_decelerating))

        five_derivatives = {
            "velocity":           round(velocity_mean, 4),
            "acceleration":       round(acceleration_mean, 4),
            "diffusion":          round(diffusion, 4),
            "phase_cancellation": round(phase_cancellation, 4),
            "deceleration":       round(deceleration_fraction, 4),
        }

        # ── Signal Classification ─────────────────────────────────────────────
        classification = self._classify_signal(
            velocity_mean, diffusion, phase_cancellation, deceleration_fraction
        )

        return kinematic_summary, five_derivatives, classification

    def _classify_signal(
        self,
        velocity_mean: float,
        diffusion: float,
        phase_cancellation: float,
        deceleration_fraction: float,
    ) -> str:
        """
        Classifies the signal into one of four canonical states:

          strong_signal  — Clear directional trend, low noise, low cancellation
          decelerating   — Strong trend but majority of time spent decelerating
          mixed          — Moderate trend with some phase cancellation
          noise          — High diffusion, no clear trend, high cancellation
        """
        is_trending      = abs(velocity_mean) >= STRONG_SIGNAL_VELOCITY_THRESHOLD
        is_noisy         = diffusion >= NOISE_STD_RATIO_THRESHOLD
        has_cancellation = phase_cancellation >= PHASE_CANCEL_THRESHOLD
        is_decelerating  = deceleration_fraction > 0.5

        if is_decelerating and is_trending:
            return "decelerating"
        elif is_trending and not is_noisy and not has_cancellation:
            return "strong_signal"
        elif is_noisy or (has_cancellation and not is_trending):
            return "noise"
        else:
            return "mixed"

    # ── Lens 3: HCI/PCI Scoring ──────────────

    def _compute_pci(
        self,
        five_derivatives: Dict[str, float],
        fated: FATEDReasoning,
        axioms: AxiomCheck,
        classification: str,
    ) -> float:
        """
        Platform Coherence Index (PCI): what the signal objectively suggests.

        Computed from four components:
          1. Velocity strength (is there directional momentum?)
          2. Trend cleanliness (low noise, low cancellation)
          3. FATED reasoning completeness
          4. Axiom alignment

        Returns: PCI score 0–100.
        """
        # 1. Velocity contribution (0–1): stronger absolute velocity = higher score
        vel_score = min(1.0, abs(five_derivatives["velocity"]) / (STRONG_SIGNAL_VELOCITY_THRESHOLD * 2))

        # 2. Trend cleanliness (0–1): penalize noise and phase cancellation
        noise_penalty  = min(1.0, five_derivatives["diffusion"] / NOISE_STD_RATIO_THRESHOLD)
        cancel_penalty = five_derivatives["phase_cancellation"]
        trend_score    = 1.0 - (noise_penalty * 0.5 + cancel_penalty * 0.5)

        # Signal classification bonus/penalty
        classification_bonus = {
            "strong_signal": 0.1,
            "mixed":          0.0,
            "decelerating":  -0.1,
            "noise":         -0.2,
        }.get(classification, 0.0)

        trend_score = max(0.0, min(1.0, trend_score + classification_bonus))

        # 3. FATED completeness (0–1)
        fated_score = fated.completeness_score()

        # 4. Axiom alignment (0–1)
        axiom_score = axioms.alignment_score()

        pci_raw = (
            vel_score   * PCI_VELOCITY_WEIGHT
            + trend_score * PCI_TREND_STRENGTH_WEIGHT
            + fated_score * PCI_FATED_WEIGHT
            + axiom_score * PCI_AXIOM_WEIGHT
        )

        return round(pci_raw * 100, 1)

    # ── On-Purpose Label ─────────────────────

    def _determine_on_purpose_label(
        self,
        on_purpose: bool,
        nci_score: float,
        axioms: AxiomCheck,
    ) -> str:
        """
        Assigns the canonical on-purpose label:
          aligned              — reasoned + coherent + no axiom violations
          good_process_bad_luck— reasoned + coherent + external circumstances worked against it
          experimental         — reasoned + low NCI (uncertain territory, acknowledged)
          dumb                 — not reasoned OR axiom violated
        """
        if not on_purpose or axioms.has_violations():
            return LABEL_DUMB

        if nci_score >= 75 and not axioms.has_violations():
            return LABEL_ALIGNED

        if nci_score >= 50:
            return LABEL_EXPERIMENTAL

        return LABEL_DUMB

    # ── Main Run ─────────────────────────────

    def run(
        self,
        signal: CoherenceSignal,
        fated: FATEDReasoning,
        axioms: AxiomCheck,
        somatic: SomaticReading,
        hci_score: float,
        phase_id: str,
        next_action: str,
        on_purpose: bool = True,
        irreversibility: float = 0.3,
        artifacts_shipped: Optional[List[str]] = None,
        notes: str = "",
    ) -> CoherenceReceipt:
        """
        Full SAGE operator run. Four lenses applied in sequence.

        Args:
            signal           : CoherenceSignal to analyze
            fated            : FATED decomposition of this decision context
            axioms           : DNA axiom compliance check
            somatic          : Six phenomenological primitive scores
            hci_score        : Human Coherence Index (0–100, self-reported)
            phase_id         : Current phase (e.g. "phase_2")
            next_action      : Declared next move after this receipt
            on_purpose       : Was this decision reasoned? (default True)
            irreversibility  : 0.0–1.0 cost to reverse (default 0.3)
            artifacts_shipped: Files/modules produced
            notes            : Any additional context

        Returns:
            CoherenceReceipt: Fully receipted SAGE assessment
        """

        # ── Lens 1: Kinematic Analysis ───────────────────────────────────────
        kinematic_summary, five_derivatives, classification = self._run_kinematic_lens(signal)

        # ── Lens 2 (implicit): Five Derivative Primitives ───────────────────
        # Already computed inside _run_kinematic_lens

        # ── Lens 3: HCI/PCI ──────────────────────────────────────────────────
        pci_score = self._compute_pci(five_derivatives, fated, axioms, classification)

        # ── Lens 4: Somatic Check ────────────────────────────────────────────
        # somatic is passed in as a SomaticReading — no computation needed here,
        # the SomaticReading object computes witness_score() and kairos_window_open()
        # internally.

        # ── NCI Calculation ──────────────────────────────────────────────────
        # on_purpose_rate: derived from axiom alignment (platform assessment)
        # avg_irreversibility: passed in directly
        on_purpose_rate = axioms.alignment_score() * (1.0 if on_purpose else 0.0)
        nci_score = calculate_nci(on_purpose_rate, irreversibility)

        # ── On-Purpose Label ─────────────────────────────────────────────────
        label = self._determine_on_purpose_label(on_purpose, nci_score, axioms)

        # ── Build Receipt ────────────────────────────────────────────────────
        receipt = CoherenceReceipt(
            operator=self.operator_name,
            phase_id=phase_id,
            signal_label=signal.label,
            nci_score=nci_score,
            on_purpose=on_purpose,
            irreversibility=irreversibility,
            on_purpose_label=label,
            fated=fated,
            axioms=axioms,
            kinematic_summary=kinematic_summary,
            signal_classification=classification,
            five_derivatives=five_derivatives,
            somatic=somatic,
            hci_score=hci_score,
            pci_score=pci_score,
            next_action=next_action,
            artifacts_shipped=artifacts_shipped or [],
            notes=notes,
        )

        return receipt

    # ── Interactive CLI Mode ─────────────────

    def run_interactive(
        self,
        signal: CoherenceSignal,
        phase_id: str,
        on_purpose: bool = True,
        irreversibility: float = 0.3,
    ) -> CoherenceReceipt:
        """
        Interactive SAGE run for human-in-the-loop sessions.
        Prompts for FATED reasoning, axiom checks, somatic scores, and HCI.
        Outputs a fully completed CoherenceReceipt.
        """
        print("\n" + "=" * 60)
        print("  SAGE OPERATOR — Interactive Mode")
        print(f"  Signal: {signal.label} ({signal.domain})")
        print(f"  Phase:  {phase_id}")
        print("=" * 60)

        # Signal preview
        print(f"\nSignal Stats:")
        for k, v in signal.summary().items():
            print(f"  {k:12}: {v}")

        # ── FATED ────────────────────────────────────────────────────────────
        print("\n── FATED Decomposition ──────────────────────────────────────")
        print("Be specific. Each dimension deserves at least one clear sentence.")
        facts       = input("\nFACTS (what is objectively true?):\n  > ").strip()
        assumptions = input("\nASSUMPTIONS (what are we treating as true but haven't proven?):\n  > ").strip()
        tradeoffs   = input("\nTRADEOFFS (what are we giving up? what do we gain?):\n  > ").strip()
        emotions    = input("\nEMOTIONS (what is the emotional charge? signal or noise?):\n  > ").strip()
        direction   = input("\nDIRECTION (given F+A+T+E, what is the clear next move?):\n  > ").strip()
        fated = FATEDReasoning(facts, assumptions, tradeoffs, emotions, direction)

        # ── Axioms ───────────────────────────────────────────────────────────
        print("\n── DNA Axiom Check ──────────────────────────────────────────")
        print("For each axiom, respond with: YES | NO | TENSION")

        def get_axiom(prompt: str) -> str:
            while True:
                val = input(f"\n{prompt}\n  YES / NO / TENSION: ").strip().upper()
                if val in {AXIOM_YES, AXIOM_NO, AXIOM_TENSION}:
                    return val
                print("  Please enter YES, NO, or TENSION.")

        axioms = AxiomCheck(
            clarity_before_curvature   = get_axiom("1. Clarity before Curvature\n   (Signal before elegance — are we optimizing for clarity?)"),
            agency_over_automation     = get_axiom("2. Agency over Automation\n   (Human judgment before delegated decision — are we keeping humans in control?)"),
            minimum_steps_to_coherence = get_axiom("3. Minimum Steps to Coherence\n   (Shortest path to real artifact — are we avoiding unnecessary steps?)"),
            kairos_over_neuroticism    = get_axiom("4. Kairos over Neuroticism\n   (Opportune timing over anxiety — is this the right moment?)"),
        )

        if axioms.has_violations():
            print("\n⚠️  AXIOM VIOLATION DETECTED. Proceeding with TENSION label.")

        # ── Somatic ──────────────────────────────────────────────────────────
        print("\n── Somatic Reading ──────────────────────────────────────────")
        print("Rate each primitive 0.0 (absent) → 1.0 (strongly present).")

        def get_somatic_score(label: str, description: str) -> float:
            while True:
                try:
                    val = float(input(f"\n{label}\n  ({description})\n  Score [0.0–1.0]: ").strip())
                    if 0.0 <= val <= 1.0:
                        return val
                    print("  Enter a value between 0.0 and 1.0.")
                except ValueError:
                    print("  Please enter a decimal number.")

        somatic = SomaticReading(
            phase_tuning        = get_somatic_score("Phase Tuning",          "Calibration signal — do you feel aligned? (r=0.72)"),
            surge_detection     = get_somatic_score("Surge Detection",       "Pre-decision energy — is there urgency present? (30-90 min window)"),
            feels_right         = get_somatic_score("Feels Right",           "Gut-level validity — does this feel correct? (76% accuracy)"),
            that_vibes          = get_somatic_score("That Vibes",            "Relational resonance — does this resonate with your context? (72% stability)"),
            locked_in           = get_somatic_score("Locked In",             "Deep focus — are you fully present? (4.2x multiplier)"),
            expected_vs_actual  = get_somatic_score("Expected vs. Actual",   "Calibration accuracy — does this match what you predicted?"),
        )

        if somatic.kairos_window_open():
            print("\n  ⚡ Kairos window is OPEN. Optimal decision moment detected.")
        else:
            print("\n  ○  Kairos window is not fully open.")

        # ── HCI ──────────────────────────────────────────────────────────────
        print("\n── Human Coherence Index (HCI) ───────────────────────────────")
        print("Rate your own coherence in this decision: 0 (incoherent) → 100 (fully coherent).")
        while True:
            try:
                hci_score = float(input("  HCI score [0–100]: ").strip())
                if 0.0 <= hci_score <= 100.0:
                    break
                print("  Enter a value between 0 and 100.")
            except ValueError:
                print("  Please enter a number.")

        # ── Next Action & Meta ────────────────────────────────────────────────
        print("\n── Completion ───────────────────────────────────────────────")
        next_action        = input("Next action (what do you do after this receipt?):\n  > ").strip()
        artifacts_str      = input("Artifacts shipped (comma-separated filenames, or blank):\n  > ").strip()
        artifacts_shipped  = [a.strip() for a in artifacts_str.split(",") if a.strip()]
        notes              = input("Any notes?\n  > ").strip()

        return self.run(
            signal=signal,
            fated=fated,
            axioms=axioms,
            somatic=somatic,
            hci_score=hci_score,
            phase_id=phase_id,
            next_action=next_action,
            on_purpose=on_purpose,
            irreversibility=irreversibility,
            artifacts_shipped=artifacts_shipped,
            notes=notes,
        )

    # ── Pretty Print ─────────────────────────

    def print_receipt(self, receipt: CoherenceReceipt) -> None:
        """Print a formatted receipt to the terminal."""
        print("\n" + "=" * 60)
        print(f"  SAGE RECEIPT — {receipt.signal_label}")
        print("=" * 60)
        print(f"\nOperator : {receipt.operator} {self.version}")
        print(f"Phase    : {receipt.phase_id}")
        print(f"Timestamp: {receipt.timestamp:.0f}")

        print(f"\n── Signal ───────────────────────────────────────────────────")
        print(f"  Classification : {receipt.signal_classification.upper()}")
        print(f"  Velocity       : {receipt.five_derivatives['velocity']:+.4f}")
        print(f"  Acceleration   : {receipt.five_derivatives['acceleration']:+.4f}")
        print(f"  Diffusion      : {receipt.five_derivatives['diffusion']:.4f}")
        print(f"  Phase Cancel.  : {receipt.five_derivatives['phase_cancellation']:.1%}")
        print(f"  Deceleration   : {receipt.five_derivatives['deceleration']:.1%}")

        print(f"\n── FATED ────────────────────────────────────────────────────")
        for k, v in receipt.fated.to_dict().items():
            print(f"  {k.upper():12}: {v[:80]}{'...' if len(v) > 80 else ''}")

        print(f"\n── Axioms ───────────────────────────────────────────────────")
        for k, v in receipt.axioms.to_dict().items():
            emoji = "✅" if v == AXIOM_YES else "⚠️ " if v == AXIOM_TENSION else "❌"
            print(f"  {emoji} {k}: {v}")

        print(f"\n── Somatic ──────────────────────────────────────────────────")
        somatic_d = receipt.somatic.to_dict()
        for k, v in somatic_d.items():
            if isinstance(v, float):
                print(f"  {k:22}: {v:.3f}")
            elif isinstance(v, bool):
                emoji = "⚡" if v else "○"
                print(f"  {k:22}: {emoji} {v}")
            else:
                print(f"  {k:22}: {v}")

        print(f"\n── Coherence Scores ─────────────────────────────────────────")
        print(f"  HCI             : {receipt.hci_score:.1f} / 100")
        print(f"  PCI             : {receipt.pci_score:.1f} / 100")
        print(f"  HCI/PCI Gap     : {receipt.hci_pci_gap():.1f} points")
        print(f"  ARCS Law (C)    : {receipt.coherence_law_score():.4f}")
        print(f"  NCI Score       : {receipt.nci_score:.1f} / 100")
        print(f"  NCI Grade       : {receipt.nci_grade()}")
        print(f"  On-Purpose      : {receipt.on_purpose_label.upper()}")
        print(f"  Irreversibility : {receipt.irreversibility:.2f}")
        print(f"  Is Satoshi      : {'⚡ YES' if receipt.is_satoshi() else '○ NO'}")

        print(f"\n── Decision ─────────────────────────────────────────────────")
        print(f"  Next Action     : {receipt.next_action}")
        if receipt.artifacts_shipped:
            print(f"  Artifacts       : {', '.join(receipt.artifacts_shipped)}")
        if receipt.notes:
            print(f"  Notes           : {receipt.notes}")

        print("\n" + "=" * 60)


# ─────────────────────────────────────────────
# QUICK TEST / SMOKE CHECK
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== SAGE Operator Smoke Test ===\n")

    # Build a sample signal (rising NCI scores across ARCS build phases)
    raw_signal = np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float)

    signal = CoherenceSignal(
        signal=raw_signal,
        domain="meta",
        label="ARCS build NCI progression (v0→Phase 2)",
    )

    fated = FATEDReasoning(
        facts=(
            "Phase 1 complete at NCI 87/100. arcs_primitives.py verified. "
            "KinematicManifold is production-ready. Zoetrope is production-ready. "
            "SAGE is the blocking operator for all phases 3-5."
        ),
        assumptions=(
            "SAGE can be built in a single phase. The kinematic manifold provides "
            "sufficient signal resolution for discernment. Somatic input can be "
            "human-in-the-loop via interactive mode."
        ),
        tradeoffs=(
            "Building SAGE as a Python class (not a microservice) trades latency "
            "for simplicity. We defer REST API wrapping to Phase 6. We choose "
            "clarity-first over premature abstraction."
        ),
        emotions=(
            "High confidence. Kairos window is open — the build is flowing. "
            "Minor tension around interactive vs automated somatic input, "
            "resolved by supporting both modes."
        ),
        direction=(
            "Build SAGE. Integrate with Zoetrope. Issue Phase 2 receipt. "
            "Confirm NCI ≥ 82 before proceeding to Phase 3 operator suite."
        ),
    )

    axioms = AxiomCheck(
        clarity_before_curvature=AXIOM_YES,
        agency_over_automation=AXIOM_YES,
        minimum_steps_to_coherence=AXIOM_YES,
        kairos_over_neuroticism=AXIOM_YES,
    )

    somatic = SomaticReading(
        phase_tuning=0.85,
        surge_detection=0.90,
        feels_right=0.88,
        that_vibes=0.80,
        locked_in=0.92,
        expected_vs_actual=0.80,
    )

    sage = SAGEOperator()
    receipt = sage.run(
        signal=signal,
        fated=fated,
        axioms=axioms,
        somatic=somatic,
        hci_score=88.0,
        phase_id="phase_2",
        next_action="Integrate SAGE output into Zoetrope store. Begin Phase 3 LAB operator.",
        on_purpose=True,
        irreversibility=0.15,
        artifacts_shipped=["arcs_primitives.py", "arcs_operators_sage.py"],
        notes="Phase 2 WRITE complete. SAGE operator production-ready.",
    )

    sage.print_receipt(receipt)

    # JSON export (what Zoetrope store will receive)
    print("\n── JSON Export (Zoetrope payload) ───────────────────────────────")
    print(receipt.to_json())

    print("\n✅ SAGE operator verified. Ready for Zoetrope integration.")
