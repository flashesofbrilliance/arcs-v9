"""
arcs_pipeline_v1.py
ARCS v9 — Integrated Operator Pipeline v1
Phase 3: READ-WRITE

The pipeline orchestrates the full operator sequence:
  SAGE → LAB → BAR → CURATOR → PipelineReceipt

Each operator runs in sequence, passing context forward.
If BAR detects RUIN, the pipeline pauses and returns a BLOCKED receipt.
The pipeline is the minimum viable coherence engine for ARCS Phase 3.

Canon reference: ARCS-SuperAdmin-Orchestrator.md
  "The Orchestrator is a direct accelerant to negentropy, not just a coordinator."
  "Anti-Signal VI: Existential Irrelevance — stop meaningless primitives early."

Phase 4 will add: Constitutional Court gate (auto-triggered on RUIN_RISK)
Phase 5 will add: Yoav Protocol (serialization of parallel futures)
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from arcs_primitives import (
    AXIOM_YES, AXIOM_NO, AXIOM_TENSION,
    AxiomCheck, CoherenceReceipt, CoherenceSignal,
    FATEDReasoning, SomaticReading, calculate_nci,
    LABEL_ALIGNED, LABEL_EXPERIMENTAL,
)
from arcs_operators_sage import SAGEOperator
from arcs_operators_lab import LABOperator, LABAssessment
from arcs_operators_bar import BAROperator, BARAssessment
from arcs_operators_curator import CuratorOperator, CuratorAssessment

PIPELINE_VERSION = "v1.0-phase3"


# ─────────────────────────────────────────────
# PIPELINE RESULT
# ─────────────────────────────────────────────

@dataclass
class PipelineResult:
    """
    Full output of a pipeline run. Contains every operator's output
    plus a synthesized pipeline-level receipt.
    """
    pipeline_version: str
    phase_id:         str
    signal_label:     str
    timestamp:        float = field(default_factory=time.time)

    # Operator outputs (in sequence)
    sage_receipt:      Optional[CoherenceReceipt]  = None
    lab_assessment:    Optional[LABAssessment]      = None
    bar_assessment:    Optional[BARAssessment]      = None
    curator_assessment: Optional[CuratorAssessment] = None

    # Pipeline status
    status:       str   = "COMPLETE"   # "COMPLETE" | "BLOCKED" | "PARTIAL"
    block_reason: str   = ""
    pipeline_nci: float = 0.0
    pipeline_verdict: str = ""         # Synthesized from all operators
    next_action:  str   = ""

    # Operator20 seed vector (for folksonomy clustering)
    operator20_seeds: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_version": self.pipeline_version,
            "phase_id": self.phase_id,
            "signal_label": self.signal_label,
            "timestamp": self.timestamp,
            "status": self.status,
            "block_reason": self.block_reason,
            "pipeline_nci": self.pipeline_nci,
            "pipeline_verdict": self.pipeline_verdict,
            "next_action": self.next_action,
            "sage": self.sage_receipt.to_dict() if self.sage_receipt else None,
            "lab":  self.lab_assessment.to_dict() if self.lab_assessment else None,
            "bar":  self.bar_assessment.to_dict() if self.bar_assessment else None,
            "curator": self.curator_assessment.to_dict() if self.curator_assessment else None,
            "operator20_seeds": self.operator20_seeds,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        nci = self.pipeline_nci
        status_icon = "✅" if self.status == "COMPLETE" else ("🛑" if self.status == "BLOCKED" else "⚠")
        return (
            f"{status_icon} Pipeline [{self.pipeline_version}] | "
            f"NCI={nci:.1f} | {self.pipeline_verdict} | "
            f"Status: {self.status}"
        )


# ─────────────────────────────────────────────
# OPERATOR20 SEED EXTRACTION
# ─────────────────────────────────────────────

def extract_operator20_seeds(result: PipelineResult) -> Dict[str, Any]:
    """
    Extracts Operator20 seed vectors from a completed pipeline run.

    Canon (ARCS-Operator20-FolksonmyCultivator.md, §2.1):
      Seeds = atomic features extracted from receipts for DBSCAN clustering.

    Each seed is a named scalar feature. Together they form a high-dimensional
    vector that Operator20's DBSCAN clusters into emergent taxonomy leaves.

    These seeds are designed for Phase 5 DBSCAN (100-200 dimensions).
    Phase 3 establishes the seed schema; Phase 5 implements clustering.
    """
    if not result.sage_receipt:
        return {}

    sage = result.sage_receipt
    lab  = result.lab_assessment
    bar  = result.bar_assessment
    cur  = result.curator_assessment

    seeds: Dict[str, Any] = {
        # ── SAGE seeds ──────────────────────────────
        "seed_nci_score":            sage.nci_score,
        "seed_irreversibility":      sage.irreversibility,
        "seed_hci_score":            sage.hci_score,
        "seed_pci_score":            sage.pci_score,
        "seed_hci_pci_gap":          sage.hci_pci_gap(),
        "seed_coherence_law":        sage.coherence_law_score(),
        "seed_is_satoshi":           int(sage.is_satoshi()),
        "seed_on_purpose":           int(sage.on_purpose),
        "seed_classification_strong":  int(sage.signal_classification == "strong_signal"),
        "seed_classification_mixed":   int(sage.signal_classification == "mixed"),
        "seed_classification_decel":   int(sage.signal_classification == "decelerating"),
        "seed_classification_noise":   int(sage.signal_classification == "noise"),
        "seed_velocity":             sage.five_derivatives.get("velocity", 0.0),
        "seed_acceleration":         sage.five_derivatives.get("acceleration", 0.0),
        "seed_diffusion":            sage.five_derivatives.get("diffusion", 0.0),
        "seed_phase_cancellation":   sage.five_derivatives.get("phase_cancellation", 0.0),
        "seed_deceleration":         sage.five_derivatives.get("deceleration", 0.0),
        "seed_somatic_witness":      sage.somatic.witness_score(),
        "seed_kairos_open":          int(sage.somatic.kairos_window_open()),
        "seed_axiom_alignment":      sage.axioms.alignment_score(),
        "seed_axiom_violations":     int(sage.axioms.has_violations()),
        "seed_fated_completeness":   sage.fated.completeness_score(),

        # ── LAB seeds ──────────────────────────────
        "seed_loki_threat":           (lab.loki.threat_score() if lab and lab.loki else 0.0),
        "seed_loki_dismissable":      int(lab.loki.can_be_dismissed if lab and lab.loki else True),
        "seed_lab_threat_level_low":  int(lab.lab_threat_level == "LOW" if lab else True),
        "seed_lab_threat_level_med":  int(lab.lab_threat_level == "MEDIUM" if lab else False),
        "seed_lab_threat_level_high": int(lab.lab_threat_level == "HIGH" if lab else False),
        "seed_lab_threat_level_crit": int(lab.lab_threat_level == "CRITICAL" if lab else False),
        "seed_lab_rec_proceed":       int(lab.lab_recommendation == "PROCEED" if lab else True),
        "seed_lab_rec_pause":         int(lab.lab_recommendation == "PAUSE" if lab else False),
        "seed_lab_rec_pivot":         int(lab.lab_recommendation == "PIVOT" if lab else False),
        "seed_lab_rec_abort":         int(lab.lab_recommendation == "ABORT" if lab else False),
        "seed_bayesian_prior":        (lab.bayesian.prior_confidence if lab and lab.bayesian else 0.0),
        "seed_bayesian_posterior":    (lab.bayesian.posterior_confidence if lab and lab.bayesian else 0.0),
        "seed_bayesian_shift":        (lab.bayesian.belief_shift if lab and lab.bayesian else 0.0),
        "seed_advisor_proceed_frac":  (lab.advisor_consensus().get("PROCEED", 0.0) if lab else 0.0),

        # ── BAR seeds ──────────────────────────────
        "seed_bar_floor_nci":         (bar.baseline.floor_nci if bar and bar.baseline else 0.0),
        "seed_bar_floor_acceptable":  int(bar.baseline.floor_is_acceptable if bar and bar.baseline else True),
        "seed_bar_asymmetry_ratio":   (bar.asymmetry.asymmetry_ratio if bar and bar.asymmetry else 1.0),
        "seed_bar_kelly_fraction":    (bar.asymmetry.kelly_fraction if bar and bar.asymmetry else 0.0),
        "seed_bar_bet_strong":        int(bar.asymmetry.bet_quality == "STRONG" if bar and bar.asymmetry else False),
        "seed_bar_bet_acceptable":    int(bar.asymmetry.bet_quality == "ACCEPTABLE" if bar and bar.asymmetry else False),
        "seed_bar_bet_marginal":      int(bar.asymmetry.bet_quality == "MARGINAL" if bar and bar.asymmetry else False),
        "seed_bar_ruin_detected":     int(bar.ruin.ruin_detected if bar and bar.ruin else False),
        "seed_bar_ruin_probability":  (bar.ruin.ruin_probability if bar and bar.ruin else 0.0),
        "seed_bar_court_trigger":     int(bar.ruin.court_trigger if bar and bar.ruin else False),

        # ── Curator seeds ──────────────────────────
        "seed_curator_reframe_type":   (cur.reframe.reframe_type if cur and cur.reframe else "none"),
        "seed_curator_adoption_cost":  (cur.reframe.adoption_cost if cur and cur.reframe else 0.0),
        "seed_curator_worth_adopting": int(cur.reframe.worth_adopting if cur and cur.reframe else False),

        # ── Pipeline meta seeds ─────────────────────
        "seed_pipeline_nci":          result.pipeline_nci,
        "seed_pipeline_status_complete": int(result.status == "COMPLETE"),
        "seed_pipeline_status_blocked":  int(result.status == "BLOCKED"),
        "seed_phase_id":              result.phase_id,
        "seed_timestamp":             result.timestamp,
    }

    return seeds


# ─────────────────────────────────────────────
# PIPELINE ORCHESTRATOR
# ─────────────────────────────────────────────

class ARCSPipeline:
    """
    ARCS Pipeline v1: SAGE → LAB → BAR → CURATOR → Receipt

    The minimum viable coherence engine. Orchestrates all four operators
    in sequence, extracts Operator20 seeds, and produces a signed
    PipelineResult ready for store archival.

    Usage:
        pipeline = ARCSPipeline()
        result = pipeline.run(
            signal=my_signal,
            fated=my_fated,
            axioms=my_axioms,
            somatic=my_somatic,
            hci_score=85.0,
            phase_id="phase_3",
            next_action="Proceed to Phase 4 ROM hardening",
            irreversibility=0.2,
        )
    """

    def __init__(self):
        self.sage    = SAGEOperator()
        self.lab     = LABOperator()
        self.bar     = BAROperator()
        self.curator = CuratorOperator()
        self.version = PIPELINE_VERSION

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
        verbose: bool = False,
    ) -> PipelineResult:
        """
        Run the full operator pipeline.

        Returns PipelineResult with all operator outputs, seeds, and
        synthesized NCI. If BAR detects RUIN_RISK, returns BLOCKED status.
        """
        result = PipelineResult(
            pipeline_version=self.version,
            phase_id=phase_id,
            signal_label=signal.label,
        )

        # ── 1. SAGE ──────────────────────────────────────────────────────────
        if verbose:
            print(f"\n[Pipeline] Running SAGE...")
        sage_receipt = self.sage.run(
            signal=signal,
            fated=fated,
            axioms=axioms,
            somatic=somatic,
            hci_score=hci_score,
            phase_id=phase_id,
            next_action="LAB adversarial challenge",
            on_purpose=on_purpose,
            irreversibility=irreversibility,
            artifacts_shipped=artifacts_shipped or [],
            notes=notes,
        )
        result.sage_receipt = sage_receipt
        if verbose:
            print(f"  SAGE: {sage_receipt.summary_line()}")

        # ── 2. LAB ───────────────────────────────────────────────────────────
        if verbose:
            print(f"[Pipeline] Running LAB...")
        lab_assessment = self.lab.run(
            sage_receipt=sage_receipt,
            phase_id=phase_id,
        )
        result.lab_assessment = lab_assessment
        if verbose:
            print(f"  LAB:  Threat={lab_assessment.lab_threat_level}, Rec={lab_assessment.lab_recommendation}")

        # ── 3. BAR ───────────────────────────────────────────────────────────
        if verbose:
            print(f"[Pipeline] Running BAR...")
        bar_assessment = self.bar.run(
            sage_receipt=sage_receipt,
            lab_assessment=lab_assessment,
            phase_id=phase_id,
        )
        result.bar_assessment = bar_assessment
        if verbose:
            print(f"  BAR:  Verdict={bar_assessment.bar_verdict}")

        # ── RUIN CHECK: Block pipeline if ruin detected ───────────────────────
        if bar_assessment.bar_verdict == "RUIN_RISK":
            result.status = "BLOCKED"
            result.block_reason = (
                f"BAR detected RUIN_RISK. "
                f"Ruin probability: {bar_assessment.ruin.ruin_probability:.3f}. "
                f"Court trigger: {bar_assessment.ruin.court_trigger}. "
                f"Mitigation: {bar_assessment.ruin.mitigation}"
            )
            result.pipeline_nci = 0.0
            result.pipeline_verdict = "BLOCKED — RUIN_RISK DETECTED. Human review required."
            result.next_action = "Invoke Constitutional Court. Do not proceed."
            result.operator20_seeds = extract_operator20_seeds(result)
            if verbose:
                print(f"\n🛑 Pipeline BLOCKED: {result.block_reason}")
            return result

        # ── 4. CURATOR ───────────────────────────────────────────────────────
        if verbose:
            print(f"[Pipeline] Running CURATOR...")
        curator_assessment = self.curator.run(
            sage_receipt=sage_receipt,
            lab_assessment=lab_assessment,
            bar_assessment=bar_assessment,
            phase_id=phase_id,
        )
        result.curator_assessment = curator_assessment
        if verbose:
            print(f"  CUR:  Reframe={curator_assessment.reframe.reframe_type if curator_assessment.reframe else 'none'}")

        # ── 5. Pipeline NCI ──────────────────────────────────────────────────
        # Synthesize NCI from all operator outputs
        sage_nci    = sage_receipt.nci_score / 100.0
        lab_penalty = min(0.15, lab_assessment.lab_assessment_penalty() if hasattr(lab_assessment, 'lab_assessment_penalty') else 0.05)
        bar_penalty = 0.0 if bar_assessment.bar_verdict in {"STRONG", "ACCEPTABLE"} else 0.05
        cur_boost   = 0.02 if (curator_assessment.reframe and curator_assessment.reframe.worth_adopting) else 0.0

        pipeline_on_purpose_rate = sage_receipt.axioms.alignment_score()
        pipeline_irreversibility = irreversibility
        raw_nci = calculate_nci(pipeline_on_purpose_rate, pipeline_irreversibility)
        # Apply lab/bar adjustments
        adjusted_nci = min(95.0, raw_nci - (lab_penalty * 100) - (bar_penalty * 100) + (cur_boost * 100))
        result.pipeline_nci = round(max(0.0, adjusted_nci), 1)

        # ── 6. Verdict ───────────────────────────────────────────────────────
        lab_rec  = lab_assessment.lab_recommendation
        bar_ver  = bar_assessment.bar_verdict
        nci_pass = result.pipeline_nci >= 82  # Phase 2+ gate

        if lab_rec == "PROCEED" and bar_ver in {"STRONG", "ACCEPTABLE"} and nci_pass:
            verdict = f"PROCEED — {bar_ver} risk geometry, LAB cleared"
        elif lab_rec in {"PAUSE", "PIVOT"}:
            verdict = f"{lab_rec} — LAB recommends caution before next step"
        else:
            verdict = f"CAUTION — review BAR ({bar_ver}) and LAB ({lab_rec}) outputs"

        result.pipeline_verdict = verdict
        result.status = "COMPLETE"
        result.next_action = next_action

        # ── 7. Operator20 Seeds ──────────────────────────────────────────────
        result.operator20_seeds = extract_operator20_seeds(result)

        if verbose:
            print(f"\n{result.summary()}")

        return result

    def print_result(self, result: PipelineResult) -> None:
        print("\n" + "═" * 60)
        print(f"  ARCS PIPELINE RESULT")
        print(f"  {result.pipeline_version} | {result.phase_id}")
        print("═" * 60)
        print(f"\nStatus  : {result.status}")
        if result.block_reason:
            print(f"Blocked : {result.block_reason[:80]}...")
        print(f"NCI     : {result.pipeline_nci:.1f}/100")
        print(f"Verdict : {result.pipeline_verdict}")
        print(f"Next    : {result.next_action}")
        print(f"\nOperator20 seed dimensions: {len(result.operator20_seeds)}")
        print("═" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== ARCS Pipeline v1 Smoke Test ===\n")

    signal = CoherenceSignal(
        signal=np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float),
        domain="meta",
        label="ARCS build NCI progression (Phase 3 pipeline test)",
    )
    fated = FATEDReasoning(
        facts="Phases 1-2 complete. SAGE, LAB, BAR, Curator all operational. Pipeline is Phase 3 capstone.",
        assumptions="All four operators function correctly in sequence. BAR will not detect ruin on this signal.",
        tradeoffs="Full pipeline adds latency vs. SAGE-only. We accept the overhead for coherence completeness.",
        emotions="High confidence. This is the moment Phase 3 becomes real — operators working in concert.",
        direction="Run pipeline. Confirm NCI ≥ 85. Extract seeds. Issue Phase 3 receipt.",
    )
    axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
    somatic = SomaticReading(0.85, 0.90, 0.88, 0.80, 0.92, 0.80)

    pipeline = ARCSPipeline()
    result = pipeline.run(
        signal=signal,
        fated=fated,
        axioms=axioms,
        somatic=somatic,
        hci_score=88.0,
        phase_id="phase_3",
        next_action="Build arcs_store.py. Archive this result. Issue Phase 3 decision receipt.",
        irreversibility=0.15,
        artifacts_shipped=[
            "arcs_operators_lab.py",
            "arcs_operators_bar.py",
            "arcs_operators_curator.py",
            "arcs_pipeline_v1.py",
        ],
        notes="Phase 3 READ-WRITE complete. Full operator suite operational.",
        verbose=True,
    )

    pipeline.print_result(result)
    print(f"\nSample seeds (first 10):")
    for k, v in list(result.operator20_seeds.items())[:10]:
        print(f"  {k}: {v}")

    print("\n✅ Pipeline v1 verified.")
