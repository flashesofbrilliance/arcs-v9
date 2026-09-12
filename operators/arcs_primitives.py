"""
arcs_primitives.py
ARCS v9 — Core Data Primitives
Phase 2: WRITE

Defines the atomic data structures that every ARCS operator produces and consumes:
  - CoherenceSignal   : The input unit (raw signal + domain context)
  - FATEDReasoning    : Structured reasoning decomposition
  - AxiomCheck        : DNA axiom compliance verification
  - SomaticReading    : Six phenomenological primitive scores
  - CoherenceReceipt  : The output unit (fully receipted decision artifact)

ARCS Law: C = αA - β(S - S_min)² + γW
  A = Alignment with DNA axioms
  S = Surprise (deviation; minimized when S = S_min)
  W = Witness (somatic signal validation)
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import numpy as np


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# ARCS Law coefficients (canonical defaults)
ALPHA = 0.5   # Axiom alignment weight
BETA  = 0.3   # Surprise penalty weight
GAMMA = 0.2   # Witness (somatic) weight

# NCI formula weights
NCI_PURPOSE_WEIGHT       = 0.7
NCI_REVERSIBILITY_WEIGHT = 0.3

# Phase gate thresholds
NCI_GATES = {
    "phase_1": 75,
    "phase_2": 82,
    "phase_3": 85,
    "phase_4": 88,
    "phase_5": 86,
    "phase_6": 88,
    "satoshi": 50,
}

# Axiom answer options
AXIOM_YES     = "YES"
AXIOM_NO      = "NO"
AXIOM_TENSION = "TENSION"

# On-purpose labels
LABEL_ALIGNED             = "aligned"
LABEL_GOOD_PROCESS_BAD_LUCK = "good_process_bad_luck"
LABEL_DUMB                = "dumb"
LABEL_EXPERIMENTAL        = "experimental"

# ── Farm league canonicality tiers ────────────────────────────────────────────
# Operators graduate through these tiers before reaching canonical status.
# Each operator carries a current tier + a promotion path; promotion is opt-in,
# never automatic. Pollination (cross-operator finding exchange) is permitted
# between operators at the same tier or one tier apart.
#
# SEMANTICS (from session pickup, encoded 2026-08-24):
#   SEED        — provisional, not committed to main. Built on disk, executed,
#                 findings logged. May be wrong. Lowest burden of proof.
#   LAB         — can exchange findings with other LAB-tier operators via
#                 pollination. Survived one structured review pass.
#   PLAYGROUND  — can be tested in the wild against real decision contexts.
#                 Findings are visible, not hidden.
#   GEMINATE_CANDIDACY — candidate for dual-instance replication test.
#                 Two independent instances run the same operator on the same
#                 inputs; results must converge within tolerance before graduation.
#   CANONICAL  — (implicit) reached when GEMINATE replication passes.
#                 Not represented as a label here — operators either are or aren't.

LABEL_SEED         = "seed"
LABEL_LAB          = "lab"
LABEL_PLAYGROUND   = "playground"
LABEL_GEMINATE     = "geminate_candidacy"


# ─────────────────────────────────────────────
# INPUT PRIMITIVE: CoherenceSignal
# ─────────────────────────────────────────────

@dataclass
class CoherenceSignal:
    """
    The atomic input unit for ARCS operators.

    Wraps a raw numerical signal with domain context so any operator
    can process it without knowing its origin.

    Examples:
        - A time series of engagement scores (marketing domain)
        - A series of HCI self-ratings over a work session (decision domain)
        - A physiological signal (biometric domain)
        - A sequence of NCI grades over phases (meta domain)
    """
    signal: np.ndarray          # Raw numerical array (1D)
    domain: str                  # e.g. "marketing", "decision", "biometric"
    label: str                   # Human-readable description of what the signal represents
    dt: float = 1.0              # Time step between samples (seconds, default = 1)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.signal, np.ndarray):
            self.signal = np.array(self.signal, dtype=float)
        if self.signal.ndim != 1:
            raise ValueError("CoherenceSignal.signal must be a 1D array.")
        if len(self.signal) < 3:
            raise ValueError("CoherenceSignal.signal must have at least 3 data points.")

    @property
    def length(self) -> int:
        return len(self.signal)

    @property
    def mean(self) -> float:
        return float(np.mean(self.signal))

    @property
    def std(self) -> float:
        return float(np.std(self.signal))

    @property
    def trend(self) -> float:
        """Simple linear trend: positive = rising, negative = falling."""
        x = np.arange(self.length)
        coeffs = np.polyfit(x, self.signal, 1)
        return float(coeffs[0])

    def summary(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "domain": self.domain,
            "length": self.length,
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "trend": round(self.trend, 4),
            "min": float(np.min(self.signal)),
            "max": float(np.max(self.signal)),
        }


# ─────────────────────────────────────────────
# REASONING PRIMITIVE: FATEDReasoning
# ─────────────────────────────────────────────

@dataclass
class FATEDReasoning:
    """
    Structured FATED decomposition of a decision context.

    FATED macro (from Canon):
      F = Facts     : What is objectively true?
      A = Assumptions: What are we treating as true but haven't proven?
      T = Tradeoffs : What are we giving up? What do we gain?
      E = Emotions  : What is the emotional charge? Is it signal or noise?
      D = Direction : Given F + A + T + E, what is the clear next move?
    """
    facts: str
    assumptions: str
    tradeoffs: str
    emotions: str
    direction: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "facts": self.facts,
            "assumptions": self.assumptions,
            "tradeoffs": self.tradeoffs,
            "emotions": self.emotions,
            "direction": self.direction,
        }

    def completeness_score(self) -> float:
        """
        Returns 0.0–1.0 based on how thoroughly each FATED dimension is filled in.
        A dimension with fewer than 10 characters scores 0; 10–50 chars scores 0.5;
        50+ chars scores 1.0.
        """
        scores = []
        for val in [self.facts, self.assumptions, self.tradeoffs, self.emotions, self.direction]:
            n = len(val.strip())
            if n >= 50:
                scores.append(1.0)
            elif n >= 10:
                scores.append(0.5)
            else:
                scores.append(0.0)
        return sum(scores) / len(scores)


# ─────────────────────────────────────────────
# GOVERNANCE PRIMITIVE: AxiomCheck
# ─────────────────────────────────────────────

@dataclass
class AxiomCheck:
    """
    DNA Axiom compliance check (immutable Canon).

    Each axiom is assessed as:
      YES     = Axiom satisfied
      NO      = Axiom violated (triggers review)
      TENSION = Acknowledged tension; proceed with awareness

    The four axioms:
      1. Clarity before Curvature  — Signal before elegance
      2. Agency over Automation    — Human judgment before delegated decision
      3. Minimum Steps to Coherence— Shortest path to real artifact
      4. Kairos over Neuroticism   — Opportune timing over anxiety
    """
    clarity_before_curvature:   str  # YES | NO | TENSION
    agency_over_automation:     str
    minimum_steps_to_coherence: str
    kairos_over_neuroticism:    str

    VALID_VALUES = {AXIOM_YES, AXIOM_NO, AXIOM_TENSION}

    def __post_init__(self):
        for field_name in [
            "clarity_before_curvature",
            "agency_over_automation",
            "minimum_steps_to_coherence",
            "kairos_over_neuroticism",
        ]:
            val = getattr(self, field_name)
            if val not in self.VALID_VALUES:
                raise ValueError(
                    f"AxiomCheck.{field_name} must be one of {self.VALID_VALUES}, got '{val}'"
                )

    def has_violations(self) -> bool:
        """Returns True if any axiom was explicitly violated."""
        return any(
            v == AXIOM_NO for v in [
                self.clarity_before_curvature,
                self.agency_over_automation,
                self.minimum_steps_to_coherence,
                self.kairos_over_neuroticism,
            ]
        )

    def alignment_score(self) -> float:
        """
        Returns 0.0–1.0 alignment with all four axioms.
        YES = 1.0, TENSION = 0.5, NO = 0.0
        """
        mapping = {AXIOM_YES: 1.0, AXIOM_TENSION: 0.5, AXIOM_NO: 0.0}
        scores = [
            mapping[self.clarity_before_curvature],
            mapping[self.agency_over_automation],
            mapping[self.minimum_steps_to_coherence],
            mapping[self.kairos_over_neuroticism],
        ]
        return sum(scores) / len(scores)

    def to_dict(self) -> Dict[str, str]:
        return {
            "clarity_before_curvature": self.clarity_before_curvature,
            "agency_over_automation": self.agency_over_automation,
            "minimum_steps_to_coherence": self.minimum_steps_to_coherence,
            "kairos_over_neuroticism": self.kairos_over_neuroticism,
        }


# ─────────────────────────────────────────────
# SOMATIC PRIMITIVE: SomaticReading
# ─────────────────────────────────────────────

@dataclass
class SomaticReading:
    """
    Six Phenomenological Primitive scores (Somatic / Witness Layer).

    Each score is 0.0–1.0 where:
      0.0 = Primitive absent
      0.5 = Weakly present
      1.0 = Strongly present

    Canonical definitions (from Compendium, Volume II):
      phase_tuning     : Calibration signal (r=0.72 coherence correlation)
      surge_detection  : Pre-decision energy window (30–90 min lead time)
      feels_right      : Gut-level validity check (76% predictive accuracy)
      that_vibes       : Relational resonance indicator (72% stability predictor)
      locked_in        : Deep focus presence (4.2x focus multiplier when present)
      expected_vs_actual: Calibration accuracy (Brier score improvement: 0.25→0.12)
    """
    phase_tuning:         float  # 0.0–1.0
    surge_detection:      float  # 0.0–1.0
    feels_right:          float  # 0.0–1.0
    that_vibes:           float  # 0.0–1.0
    locked_in:            float  # 0.0–1.0
    expected_vs_actual:   float  # 0.0–1.0

    def __post_init__(self):
        for field_name in [
            "phase_tuning", "surge_detection", "feels_right",
            "that_vibes", "locked_in", "expected_vs_actual"
        ]:
            val = getattr(self, field_name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(
                    f"SomaticReading.{field_name} must be between 0.0 and 1.0, got {val}"
                )

    # Canonical weights (from Compendium correlations)
    WEIGHTS = {
        "phase_tuning":       0.20,  # r=0.72 highest correlation
        "surge_detection":    0.15,  # 30-90 min lead time
        "feels_right":        0.25,  # 76% predictive validity (highest)
        "that_vibes":         0.15,  # 72% relationship stability
        "locked_in":          0.15,  # 4.2x multiplier when present
        "expected_vs_actual": 0.10,  # Calibration signal
    }

    def witness_score(self) -> float:
        """
        Computes W (Witness) for ARCS Law: C = αA - β(S - S_min)² + γW
        Returns weighted composite of all six somatic primitives.
        """
        return sum(
            getattr(self, primitive) * weight
            for primitive, weight in self.WEIGHTS.items()
        )

    def dominant_primitive(self) -> str:
        """Returns the somatic primitive with the highest score."""
        scores = {
            "phase_tuning": self.phase_tuning,
            "surge_detection": self.surge_detection,
            "feels_right": self.feels_right,
            "that_vibes": self.that_vibes,
            "locked_in": self.locked_in,
            "expected_vs_actual": self.expected_vs_actual,
        }
        return max(scores, key=scores.get)

    def kairos_window_open(self) -> bool:
        """
        Returns True if surge_detection + locked_in are both > 0.6.
        This is the canonical Kairos window indicator.
        """
        return self.surge_detection > 0.6 and self.locked_in > 0.6

    def to_dict(self) -> Dict[str, float]:
        return {
            "phase_tuning": self.phase_tuning,
            "surge_detection": self.surge_detection,
            "feels_right": self.feels_right,
            "that_vibes": self.that_vibes,
            "locked_in": self.locked_in,
            "expected_vs_actual": self.expected_vs_actual,
            "witness_score": round(self.witness_score(), 4),
            "kairos_window_open": self.kairos_window_open(),
            "dominant_primitive": self.dominant_primitive(),
        }


# ─────────────────────────────────────────────
# OUTPUT PRIMITIVE: CoherenceReceipt
# ─────────────────────────────────────────────

@dataclass
class CoherenceReceipt:
    """
    The atomic output unit of the ARCS system.

    Every operator produces exactly one CoherenceReceipt per invocation.
    Receipts are:
      - Append-only (immutable once written)
      - Self-grading (contain their own NCI score)
      - Composable (satoshis build larger receipts)
      - Auditable (every field is traceable to Canon)

    ARCS Law: C = αA - β(S - S_min)² + γW
    NCI:      NCI = (on_purpose_rate × 0.7) + ((1 - avg_irreversibility) × 0.3)
    """
    # Identity
    operator:     str   # Which operator produced this ("SAGE", "LAB", "BAR", ...)
    phase_id:     str   # Which phase ("phase_1", "phase_2", ...)
    signal_label: str   # What signal was analyzed

    # Coherence Assessment
    nci_score:       float   # 0–100
    on_purpose:      bool    # Was this decision reasoned (not accidental)?
    irreversibility: float   # 0.0 (reversible) – 1.0 (irreversible)
    on_purpose_label: str    # "aligned" | "good_process_bad_luck" | "dumb" | "experimental"

    # Reasoning
    fated:   FATEDReasoning
    axioms:  AxiomCheck

    # Signal Analysis
    kinematic_summary:    Dict[str, float]    # Scalar summary of 12 derivatives
    signal_classification: str                # "strong_signal" | "noise" | "mixed" | "decelerating"
    five_derivatives:     Dict[str, float]    # Velocity, Acceleration, Diffusion, PhaseCancel, Deceleration

    # Somatic Layer
    somatic: SomaticReading

    # HCI/PCI
    hci_score: float   # Human Coherence Index (0–100, self-reported)
    pci_score: float   # Platform Coherence Index (0–100, computed)

    # Outputs
    next_action: str
    artifacts_shipped: List[str] = field(default_factory=list)
    notes: str = ""

    # Auto-computed
    timestamp: float = field(default_factory=time.time)

    # ── Computed Properties ──────────────────

    def coherence_law_score(self) -> float:
        """
        ARCS Law: C = αA - β(S - S_min)² + γW

        A = axiom alignment score (0.0–1.0)
        S = surprise = |hci_score - pci_score| / 100 (normalized deviation)
        S_min = 0 (ideal: no gap between human and platform assessment)
        W = somatic witness score (0.0–1.0)
        """
        A = self.axioms.alignment_score()
        S = abs(self.hci_score - self.pci_score) / 100.0
        S_min = 0.0
        W = self.somatic.witness_score()
        C = ALPHA * A - BETA * (S - S_min) ** 2 + GAMMA * W
        return round(max(0.0, min(1.0, C)), 4)  # Clamp to [0, 1]

    def nci_grade(self) -> str:
        """Returns the human-readable NCI gate tier."""
        if self.nci_score >= 88:
            return "RELEASE_READY"
        elif self.nci_score >= 86:
            return "PHASE_5_READY"
        elif self.nci_score >= 85:
            return "PHASE_3_READY"
        elif self.nci_score >= 82:
            return "PHASE_2_READY"
        elif self.nci_score >= 75:
            return "PHASE_1_READY"
        elif self.nci_score >= 50:
            return "SATOSHI_VALID"
        else:
            return "BELOW_THRESHOLD"

    def is_satoshi(self) -> bool:
        """
        Checks if this receipt qualifies as a satoshi (smallest coherence unit).

        Satoshi criteria:
          ✅ on_purpose = True
          ✅ nci_score >= 50
          ✅ irreversibility <= 0.5
          ✅ All four DNA axioms not explicitly violated (no "NO")
        """
        return (
            self.on_purpose
            and self.nci_score >= NCI_GATES["satoshi"]
            and self.irreversibility <= 0.5
            and not self.axioms.has_violations()
        )

    def hci_pci_gap(self) -> float:
        """
        HCI/PCI divergence score.
        Large gap = human and platform assessments are misaligned.
        Small gap = coherent self-assessment.
        """
        return abs(self.hci_score - self.pci_score)

    # ── Serialization ────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator,
            "phase_id": self.phase_id,
            "signal_label": self.signal_label,
            "timestamp": self.timestamp,
            "nci_score": self.nci_score,
            "nci_grade": self.nci_grade(),
            "on_purpose": self.on_purpose,
            "on_purpose_label": self.on_purpose_label,
            "irreversibility": self.irreversibility,
            "is_satoshi": self.is_satoshi(),
            "coherence_law_score": self.coherence_law_score(),
            "hci_score": self.hci_score,
            "pci_score": self.pci_score,
            "hci_pci_gap": self.hci_pci_gap(),
            "fated": self.fated.to_dict(),
            "axioms": self.axioms.to_dict(),
            "kinematic_summary": self.kinematic_summary,
            "signal_classification": self.signal_classification,
            "five_derivatives": self.five_derivatives,
            "somatic": self.somatic.to_dict(),
            "next_action": self.next_action,
            "artifacts_shipped": self.artifacts_shipped,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary_line(self) -> str:
        """One-line summary for logging/display."""
        satoshi_marker = "⚡" if self.is_satoshi() else "○"
        return (
            f"{satoshi_marker} [{self.operator}] {self.signal_label} | "
            f"NCI={self.nci_score:.1f} ({self.nci_grade()}) | "
            f"C={self.coherence_law_score():.3f} | "
            f"HCI={self.hci_score:.0f}/PCI={self.pci_score:.0f} | "
            f"{self.on_purpose_label.upper()}"
        )


# ─────────────────────────────────────────────
# NCI CALCULATOR
# ─────────────────────────────────────────────

def calculate_nci(on_purpose_rate: float, avg_irreversibility: float) -> float:
    """
    ARCS NCI formula:
      NCI = (on_purpose_rate × 0.7) + ((1 - avg_irreversibility) × 0.3)

    Args:
        on_purpose_rate    : 0.0–1.0 (fraction of decisions that were reasoned)
        avg_irreversibility: 0.0–1.0 (average reversibility cost of decisions)

    Returns:
        NCI score: 0–100
    """
    if not (0.0 <= on_purpose_rate <= 1.0):
        raise ValueError(f"on_purpose_rate must be 0.0–1.0, got {on_purpose_rate}")
    if not (0.0 <= avg_irreversibility <= 1.0):
        raise ValueError(f"avg_irreversibility must be 0.0–1.0, got {avg_irreversibility}")

    raw = (on_purpose_rate * NCI_PURPOSE_WEIGHT) + (
        (1.0 - avg_irreversibility) * NCI_REVERSIBILITY_WEIGHT
    )
    return round(raw * 100, 1)


def check_phase_gate(nci_score: float, phase: str) -> bool:
    """
    Returns True if NCI score meets the gate for the given phase.

    Args:
        nci_score: 0–100
        phase: "phase_1" through "phase_6" or "satoshi"
    """
    if phase not in NCI_GATES:
        raise ValueError(f"Unknown phase '{phase}'. Valid: {list(NCI_GATES.keys())}")
    return nci_score >= NCI_GATES[phase]


# ─────────────────────────────────────────────
# QUICK TEST / SMOKE CHECK
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np

    print("=== ARCS Primitives Smoke Test ===\n")

    # 1. CoherenceSignal
    signal = CoherenceSignal(
        signal=np.array([10, 12, 15, 14, 16, 20, 22, 21, 25, 28], dtype=float),
        domain="decision",
        label="NCI scores across 10 sessions",
    )
    print(f"CoherenceSignal: {signal.summary()}\n")

    # 2. FATEDReasoning
    fated = FATEDReasoning(
        facts="Phase 1 inventory complete. 11 operators missing. NCI 87/100.",
        assumptions="SAGE is the blocking dependency. Zoetrope can hold outputs.",
        tradeoffs="Speed vs coherence: we chose coherence. Receipts add ceremony.",
        emotions="Temptation to skip primitives and jump to SAGE. Resistance noted.",
        direction="Build arcs_primitives.py first. Then SAGE. No shortcuts.",
    )
    print(f"FATED completeness: {fated.completeness_score():.2f}\n")

    # 3. AxiomCheck
    axioms = AxiomCheck(
        clarity_before_curvature=AXIOM_YES,
        agency_over_automation=AXIOM_YES,
        minimum_steps_to_coherence=AXIOM_YES,
        kairos_over_neuroticism=AXIOM_YES,
    )
    print(f"Axiom alignment: {axioms.alignment_score():.2f} | Violations: {axioms.has_violations()}\n")

    # 4. SomaticReading
    somatic = SomaticReading(
        phase_tuning=0.8,
        surge_detection=0.9,
        feels_right=0.85,
        that_vibes=0.7,
        locked_in=0.9,
        expected_vs_actual=0.75,
    )
    print(f"Somatic witness: {somatic.witness_score():.3f} | Kairos open: {somatic.kairos_window_open()}\n")

    # 5. NCI Calculator
    nci = calculate_nci(on_purpose_rate=0.87, avg_irreversibility=0.1)
    print(f"NCI: {nci}/100 | Phase 2 gate passed: {check_phase_gate(nci, 'phase_2')}\n")

    # 6. CoherenceReceipt
    receipt = CoherenceReceipt(
        operator="SAGE",
        phase_id="phase_2",
        signal_label="NCI scores across 10 sessions",
        nci_score=nci,
        on_purpose=True,
        irreversibility=0.1,
        on_purpose_label=LABEL_ALIGNED,
        fated=fated,
        axioms=axioms,
        kinematic_summary={"velocity_mean": 1.9, "acceleration_mean": 0.1},
        signal_classification="strong_signal",
        five_derivatives={
            "velocity": 1.9,
            "acceleration": 0.1,
            "diffusion": 2.3,
            "phase_cancellation": 0.0,
            "deceleration": 0.0,
        },
        somatic=somatic,
        hci_score=88.0,
        pci_score=86.0,
        next_action="Build arcs_operators_sage.py",
        artifacts_shipped=["arcs_primitives.py"],
        notes="Phase 2 primitives complete. SAGE is next.",
    )

    print(f"Receipt summary: {receipt.summary_line()}")
    print(f"Is satoshi: {receipt.is_satoshi()}")
    print(f"Coherence Law score: {receipt.coherence_law_score()}")
    print(f"HCI/PCI gap: {receipt.hci_pci_gap()}")

    print("\n✅ All primitives verified. Ready for SAGE operator.")
