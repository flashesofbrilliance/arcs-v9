"""
arcs_constitutional_court.py
ARCS v9 — Constitutional Court (Immune System)
Phase 4: WRITE-LOCK

The Constitutional Court is the ARCS immune system.
It is triggered whenever BAR detects RUIN_RISK in a pipeline run.

The Court does not block blindly — it adjudicates.
It runs three constitutional tests against the ruin claim:
  1. AXIOM TEST    — Does proceeding violate a DNA axiom?
  2. EVIDENCE TEST — Is the Loki challenge actually strong enough to warrant ruin?
  3. IDENTITY TEST — Is the signal consistent with ARCS' constitutional DNA?

Court verdicts:
  PERMIT      — Ruin claim is unfounded; pipeline may proceed
  CONDITIONAL — Ruin risk is real but manageable; proceed with stated conditions
  BLOCK       — Ruin confirmed; pipeline is halted; Kintsugi repair required

Design philosophy:
  - The Court is the last line of defense before commitment.
  - It does NOT replace human judgment — it structures it.
  - A PERMIT from the Court is not a guarantee; it is a reasoned clearance.
  - A BLOCK from the Court cannot be overridden by the pipeline.
  - Only a human reviewer with FATED reasoning can unlock a BLOCK.

NOTOMATION: The Court issues verdicts. Humans execute them.

Canon references:
  - ARCS-SuperAdmin-Orchestrator.md ("immune system logic")
  - ARCS-Canon-v2-0-Complete.md (second law: minimize wasted energy)
  - Phase 3 decision receipt (RUIN_RISK as feature, not bug)
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from arcs_primitives import CoherenceReceipt
from arcs_operators_lab import LABAssessment
from arcs_operators_bar import BARAssessment, RuinAssessment
from arcs_rom import ARCSRom, RUIN_THRESHOLDS, DNA_AXIOMS, ROM_VERSION
from arcs_no_go_inventory import get_ngi, NGIClass

COURT_VERSION = "v9.0-phase4"

# ─────────────────────────────────────────────
# COURT DATA STRUCTURES
# ─────────────────────────────────────────────

VERDICT_PERMIT      = "PERMIT"
VERDICT_CONDITIONAL = "CONDITIONAL"
VERDICT_BLOCK       = "BLOCK"


@dataclass
class ConstitutionalTest:
    """
    Result of a single constitutional test.

    Each test asks one focused question about the ruin claim.
    PASSES = the claim does not survive this test (Court leans toward PERMIT).
    FAILS  = the claim survives this test (Court leans toward BLOCK).
    """
    test_name:     str
    question:      str    # The constitutional question being asked
    finding:       str    # What the test found
    passes:        bool   # True = ruin claim fails this test (lean PERMIT)
    weight:        float  # Importance weight in final verdict (0.0–1.0)
    evidence:      str    # The evidence supporting the finding

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "question": self.question,
            "finding": self.finding,
            "passes": self.passes,
            "weight": self.weight,
            "evidence": self.evidence,
        }


@dataclass
class CourtCondition:
    """
    A condition that must be met for a CONDITIONAL verdict to proceed.
    """
    condition_id:  str
    description:   str   # What must be true before proceeding
    urgency:       str   # "BEFORE_NEXT_STEP" | "BEFORE_PHASE_EXIT" | "MONITOR"
    verifiable:    bool  # Can this condition be verified mechanically?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "description": self.description,
            "urgency": self.urgency,
            "verifiable": self.verifiable,
        }


@dataclass
class CourtVerdict:
    """
    The Constitutional Court's final ruling on a RUIN_RISK case.

    A verdict contains:
      - The ruling (PERMIT / CONDITIONAL / BLOCK)
      - The three constitutional test results
      - Conditions (if CONDITIONAL)
      - The reasoning trail (Canon-auditable)
      - The evidence weight (how much evidence supported ruin vs cleared it)
    """
    # Identity
    case_id:          str
    signal_label:     str
    phase_id:         str
    timestamp:        float = field(default_factory=time.time)

    # Verdict
    verdict:          str = VERDICT_BLOCK     # PERMIT | CONDITIONAL | BLOCK
    verdict_summary:  str = ""
    evidence_weight:  float = 0.0            # 0.0=fully cleared, 1.0=fully blocked

    # Tests
    tests:            List[ConstitutionalTest] = field(default_factory=list)

    # Conditions (only set if CONDITIONAL)
    conditions:       List[CourtCondition] = field(default_factory=list)

    # Metadata
    court_version:    str = COURT_VERSION
    rom_version:      str = ROM_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "signal_label": self.signal_label,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp,
            "verdict": self.verdict,
            "verdict_summary": self.verdict_summary,
            "evidence_weight": round(self.evidence_weight, 3),
            "tests": [t.to_dict() for t in self.tests],
            "conditions": [c.to_dict() for c in self.conditions],
            "court_version": self.court_version,
            "rom_version": self.rom_version,
        }


# ─────────────────────────────────────────────
# CONSTITUTIONAL COURT
# ─────────────────────────────────────────────

class ConstitutionalCourt:
    """
    ARCS Constitutional Court — Immune System Gate.

    Adjudicates RUIN_RISK cases flagged by the BAR operator.
    Runs three constitutional tests; issues PERMIT, CONDITIONAL, or BLOCK.

    The Court is independent of the pipeline — it does not run unless
    explicitly invoked on a RUIN_RISK result. It is not a default step.
    """

    def __init__(self):
        self.version = COURT_VERSION
        self.operator_name = "COURT"
        self.rom = ARCSRom()
        self._case_counter = 0

    def _make_case_id(self, phase_id: str) -> str:
        self._case_counter += 1
        return f"case_{phase_id}_{int(time.time())}_{self._case_counter:03d}"

    # ── Test 1: Axiom Test ────────────────────

    def _axiom_test(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
        bar: BARAssessment,
    ) -> ConstitutionalTest:
        """
        AXIOM TEST: Does proceeding violate a DNA axiom?

        The Court's first question is constitutional:
        "Would proceeding require breaking an immutable axiom?"

        If YES → test FAILS → lean toward BLOCK
        If NO  → test PASSES → lean toward PERMIT on this dimension
        """
        axiom_dict = {
            "clarity_before_curvature":    sage_receipt.axioms.clarity_before_curvature,
            "agency_over_automation":      sage_receipt.axioms.agency_over_automation,
            "minimum_steps_to_coherence":  sage_receipt.axioms.minimum_steps_to_coherence,
            "kairos_over_neuroticism":     sage_receipt.axioms.kairos_over_neuroticism,
        }
        rom_result = self.rom.validate_axioms(axiom_dict)

        violated = [v for v in rom_result.violations if "VIOLATED" in v]
        tensions = [w for w in rom_result.warnings if "TENSION" in w]

        if violated:
            return ConstitutionalTest(
                test_name="AXIOM_TEST",
                question="Does proceeding violate a DNA axiom?",
                finding=f"FAIL — axiom violation detected: {violated[0]}",
                passes=False,
                weight=0.45,
                evidence=f"Violated axioms: {violated}. Tensions: {tensions}.",
            )

        if tensions:
            return ConstitutionalTest(
                test_name="AXIOM_TEST",
                question="Does proceeding violate a DNA axiom?",
                finding=f"PARTIAL — axiom tension detected but not violated: {tensions[0]}",
                passes=True,
                weight=0.45,
                evidence=f"No violations. Tensions to monitor: {tensions}.",
            )

        return ConstitutionalTest(
            test_name="AXIOM_TEST",
            question="Does proceeding violate a DNA axiom?",
            finding="PASS — all four DNA axioms are intact (YES or TENSION only).",
            passes=True,
            weight=0.45,
            evidence=f"Checked: {list(axiom_dict.keys())}. All passed or in tension.",
        )

    # ── Test 2: Evidence Test ─────────────────

    def _evidence_test(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
        bar: BARAssessment,
    ) -> ConstitutionalTest:
        """
        EVIDENCE TEST: Is the ruin claim actually well-evidenced?

        The Court applies a stricter evidentiary standard than BAR:
          - BAR flags ruin at loki_threat > threshold (single test)
          - Court asks: is the Loki challenge independently strong,
            or is it amplified by signal classification alone?

        If the ruin is based only on classification (not on multiple
        independent evidence sources), the claim is weaker.
        """
        ruin = bar.ruin
        loki = lab.loki
        nci = sage_receipt.nci_score
        classification = sage_receipt.signal_classification

        # How many independent ruin triggers fired?
        ruin_triggers = sum([
            ruin.ruin_detected and ruin.irreversibility_score > RUIN_THRESHOLDS["irreversibility_ruin"],
            bool(loki and not loki.can_be_dismissed and loki.threat_score() > RUIN_THRESHOLDS["loki_ruin_standard"]),
            lab.lab_recommendation == "ABORT",
        ])

        # Is the Loki challenge dismissible on second review?
        loki_strong = loki and not loki.can_be_dismissed and loki.threat_score() > 0.6
        nci_healthy = nci >= 82

        # If NCI is healthy and only one trigger fired based on classification,
        # the evidence is borderline — the ruin claim is not fully established.
        evidence_strong = ruin_triggers >= 2 or (ruin_triggers == 1 and not nci_healthy)

        if evidence_strong:
            return ConstitutionalTest(
                test_name="EVIDENCE_TEST",
                question="Is the ruin claim well-evidenced beyond classification alone?",
                finding=f"FAIL — {ruin_triggers} independent ruin trigger(s) confirm the claim.",
                passes=False,
                weight=0.35,
                evidence=(
                    f"Ruin triggers: {ruin_triggers}. "
                    f"Loki threat: {loki.threat_score():.2f} (undismissable: {loki and not loki.can_be_dismissed}). "
                    f"NCI: {nci:.1f}. LAB rec: {lab.lab_recommendation}."
                ),
            )

        return ConstitutionalTest(
            test_name="EVIDENCE_TEST",
            question="Is the ruin claim well-evidenced beyond classification alone?",
            finding=(
                f"PASS — ruin claim has only {ruin_triggers} trigger and NCI is "
                f"{'healthy' if nci_healthy else 'low'} ({nci:.1f}). Claim is borderline."
            ),
            passes=True,
            weight=0.35,
            evidence=(
                f"Ruin triggers: {ruin_triggers}. NCI: {nci:.1f} ({'healthy' if nci_healthy else 'weak'}). "
                f"Classification: {classification}. "
                f"Loki dismissible: {loki.can_be_dismissed if loki else 'N/A'}."
            ),
        )

    # ── Test 3: Identity Test ─────────────────

    def _identity_test(
        self,
        sage_receipt: CoherenceReceipt,
        lab: LABAssessment,
        bar: BARAssessment,
    ) -> ConstitutionalTest:
        """
        IDENTITY TEST: Is this consistent with ARCS' constitutional DNA?

        The deepest test: even if axioms are intact and evidence is weak,
        does this decision feel like a Shapeshifter moment — adapting to
        external pressure in a way that compromises core identity?

        Identity failure signals:
          - "agency_over_automation" in TENSION (delegating judgment)
          - Very low HCI/PCI gap (system is overriding human assessment)
          - LAB ABORT with majority advisor consensus

        Identity strength signals:
          - Kairos window open (somatic alignment with timing)
          - HCI and PCI agree (human and platform coherent)
          - SAGE NCI above satoshi threshold
        """
        nci = sage_receipt.nci_score
        hci_pci_gap = sage_receipt.hci_pci_gap()
        kairos_open = sage_receipt.somatic.kairos_window_open()
        agency_axiom = sage_receipt.axioms.agency_over_automation
        consensus = lab.advisor_consensus()
        abort_fraction = consensus.get("ABORT", 0.0)

        identity_risks = []
        identity_strengths = []

        if agency_axiom == "NO":
            identity_risks.append("Agency over Automation VIOLATED — automation is overriding human judgment.")
        elif agency_axiom == "TENSION":
            identity_risks.append("Agency over Automation in TENSION — judgment boundary is blurring.")

        if abort_fraction >= 0.6:
            identity_risks.append(f"Majority of advisors ({abort_fraction:.0%}) recommend ABORT — consensus ruin.")

        if hci_pci_gap > 20:
            identity_risks.append(f"HCI/PCI gap {hci_pci_gap:.1f} is extreme — human and platform severely misaligned.")

        if kairos_open:
            identity_strengths.append("Kairos window is open — somatic alignment supports timing.")
        if nci >= 82:
            identity_strengths.append(f"NCI {nci:.1f} is above satoshi threshold — coherence is healthy.")
        if hci_pci_gap <= 10:
            identity_strengths.append(f"HCI/PCI gap {hci_pci_gap:.1f} — human and platform in agreement.")

        identity_fails = len(identity_risks) >= 2 or (agency_axiom == "NO")

        if identity_fails:
            return ConstitutionalTest(
                test_name="IDENTITY_TEST",
                question="Is this decision consistent with ARCS' constitutional DNA?",
                finding=f"FAIL — {len(identity_risks)} identity risk(s): {identity_risks[0]}",
                passes=False,
                weight=0.20,
                evidence=f"Risks: {identity_risks}. Strengths: {identity_strengths}.",
            )

        return ConstitutionalTest(
            test_name="IDENTITY_TEST",
            question="Is this decision consistent with ARCS' constitutional DNA?",
            finding=f"PASS — {len(identity_strengths)} identity strength(s). Risks: {len(identity_risks)}.",
            passes=True,
            weight=0.20,
            evidence=f"Strengths: {identity_strengths}. Risks: {identity_risks}.",
        )

    # ── Verdict Logic ─────────────────────────

    def _compute_verdict(
        self,
        tests: List[ConstitutionalTest],
        bar: BARAssessment,
        sage_receipt: CoherenceReceipt,
    ) -> Tuple[str, float, str, List[CourtCondition]]:
        """
        Computes final verdict from test results.

        Returns (verdict, evidence_weight, summary, conditions).

        Evidence weight formula:
          evidence_weight = sum(test.weight for test that FAILS)
          0.0 = all tests passed (ruin claim fully cleared)
          1.0 = all tests failed (ruin fully confirmed)

          weight > threshold_block  → BLOCK
          weight < threshold_permit → PERMIT
          otherwise                 → CONDITIONAL
        """
        total_weight = sum(t.weight for t in tests)
        fail_weight = sum(t.weight for t in tests if not t.passes)
        evidence_weight = round(fail_weight / total_weight, 3) if total_weight > 0 else 0.0

        permit_threshold = RUIN_THRESHOLDS["court_permit_threshold"]
        block_threshold  = RUIN_THRESHOLDS["court_block_threshold"]

        conditions: List[CourtCondition] = []

        if evidence_weight <= (1.0 - permit_threshold):
            # Most evidence cleared the claim
            verdict = VERDICT_PERMIT
            summary = (
                f"PERMIT — Court finds ruin claim insufficiently evidenced "
                f"(evidence weight {evidence_weight:.2f}, below block threshold). "
                f"Pipeline may proceed. Receipt must be logged."
            )

        elif evidence_weight >= block_threshold + 0.30:
            # Strong evidence confirms ruin
            verdict = VERDICT_BLOCK
            summary = (
                f"BLOCK — Court confirms ruin risk "
                f"(evidence weight {evidence_weight:.2f}). "
                f"Pipeline is halted. Human review required. Kintsugi repair recommended."
            )

        else:
            # Middle ground: proceed with explicit conditions
            verdict = VERDICT_CONDITIONAL
            summary = (
                f"CONDITIONAL — Ruin risk is real but not disqualifying "
                f"(evidence weight {evidence_weight:.2f}). "
                f"Proceed only if stated conditions are met."
            )
            # Generate conditions based on what failed
            for test in tests:
                if not test.passes:
                    if test.test_name == "AXIOM_TEST":
                        conditions.append(CourtCondition(
                            condition_id="resolve_axiom_tension",
                            description=(
                                "Resolve the flagged axiom tension before the next phase exit. "
                                "Add a FATED entry addressing the specific tension. Log in receipt."
                            ),
                            urgency="BEFORE_PHASE_EXIT",
                            verifiable=True,
                        ))
                    elif test.test_name == "EVIDENCE_TEST":
                        conditions.append(CourtCondition(
                            condition_id="monitor_loki_signal",
                            description=(
                                "Monitor the Loki challenge across the next 3 pipeline runs. "
                                "If threat_score remains above 0.7, escalate to full BLOCK review."
                            ),
                            urgency="MONITOR",
                            verifiable=True,
                        ))
                    elif test.test_name == "IDENTITY_TEST":
                        conditions.append(CourtCondition(
                            condition_id="identity_review",
                            description=(
                                "Before committing, run a manual FATED identity check: "
                                "'Is this the ARCS canonical direction, or external pressure adaptation?' "
                                "Document the answer in the next receipt."
                            ),
                            urgency="BEFORE_NEXT_STEP",
                            verifiable=False,
                        ))

        return verdict, evidence_weight, summary, conditions

    # ── Main Run ─────────────────────────────

    def adjudicate(
        self,
        sage_receipt: CoherenceReceipt,
        lab_assessment: LABAssessment,
        bar_assessment: BARAssessment,
        phase_id: str,
    ) -> CourtVerdict:
        """
        Adjudicates a RUIN_RISK case.

        Takes the full SAGE/LAB/BAR context.
        Runs three constitutional tests.
        Issues a verdict.

        This method should only be called when BAR verdict == RUIN_RISK.
        Calling it on non-ruin cases is wasteful but harmless.
        """
        case_id = self._make_case_id(phase_id)

        # Run three constitutional tests
        axiom_test    = self._axiom_test(sage_receipt, lab_assessment, bar_assessment)
        evidence_test = self._evidence_test(sage_receipt, lab_assessment, bar_assessment)
        identity_test = self._identity_test(sage_receipt, lab_assessment, bar_assessment)
        tests = [axiom_test, evidence_test, identity_test]

        # Compute verdict
        verdict, evidence_weight, summary, conditions = self._compute_verdict(
            tests, bar_assessment, sage_receipt
        )

        court_verdict = CourtVerdict(
            case_id=case_id,
            signal_label=sage_receipt.signal_label,
            phase_id=phase_id,
            verdict=verdict,
            verdict_summary=summary,
            evidence_weight=evidence_weight,
            tests=tests,
            conditions=conditions,
        )

        # NGI v1 — log BLOCK and CONDITIONAL verdicts to No-Go Inventory
        if verdict in (VERDICT_BLOCK, VERDICT_CONDITIONAL):
            ngi_class = NGIClass.BSS_WALL if verdict == VERDICT_BLOCK else NGIClass.KINTSUGI_SCAR
            receipt_id = getattr(sage_receipt, "receipt_id", None)
            get_ngi().log(
                ngi_class=ngi_class,
                trigger=f"Court {verdict} — {summary[:120]}",
                receipt_id=receipt_id,
                notes=f"case_id={case_id} evidence_weight={evidence_weight:.2f}",
            )

        return court_verdict

    def print_verdict(self, verdict: CourtVerdict) -> None:
        symbol = {"PERMIT": "✅", "CONDITIONAL": "⚠️ ", "BLOCK": "🛑"}.get(verdict.verdict, "?")
        print("\n" + "=" * 60)
        print(f"  CONSTITUTIONAL COURT — Case {verdict.case_id}")
        print("=" * 60)
        print(f"\n  {symbol} VERDICT: {verdict.verdict}")
        print(f"  Evidence weight: {verdict.evidence_weight:.2f}")
        print(f"\n  {verdict.verdict_summary[:120]}")
        print("\n  Constitutional Tests:")
        for t in verdict.tests:
            icon = "✓" if t.passes else "✗"
            print(f"    {icon} [{t.test_name}] {t.finding[:80]}")
        if verdict.conditions:
            print("\n  Conditions to meet:")
            for c in verdict.conditions:
                print(f"    • [{c.urgency}] {c.description[:80]}")
        print("=" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np
    from arcs_primitives import (
        FATEDReasoning, SomaticReading, AxiomCheck, CoherenceSignal,
        AXIOM_YES, AXIOM_NO, AXIOM_TENSION,
    )
    from arcs_operators_sage import SAGEOperator
    from arcs_operators_lab import LABOperator
    from arcs_operators_bar import BAROperator

    print("=== ARCS Constitutional Court Smoke Test ===\n")

    court = ConstitutionalCourt()

    # Test 1: Healthy high-NCI decelerating signal (should PERMIT or CONDITIONAL)
    print("─── Case 1: Healthy ceiling-adjacent decelerating signal ─────")
    signal = CoherenceSignal(
        signal=np.array([65, 72, 78, 81, 83, 84, 86, 87, 88, 90], dtype=float),
        domain="meta", label="Ceiling-adjacent decelerating (NCI ~95)",
    )
    fated = FATEDReasoning(
        "Phase 3 complete. NCI 95+.",
        "Deceleration is plateau, not collapse.",
        "Speed vs ceremony.",
        "Satisfied — immune system is working.",
        "Proceed to Phase 4.",
    )
    axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
    somatic = SomaticReading(0.85, 0.90, 0.88, 0.80, 0.92, 0.80)

    sage = SAGEOperator()
    sage_r = sage.run(signal=signal, fated=fated, axioms=axioms, somatic=somatic,
                      hci_score=88.0, phase_id="phase_3", next_action="test", irreversibility=0.15)
    lab = LABOperator()
    lab_r = lab.run(sage_r, "phase_3")
    bar = BAROperator()
    bar_r = bar.run(sage_r, lab_r, "phase_3")

    print(f"  BAR verdict: {bar_r.bar_verdict}")
    verdict1 = court.adjudicate(sage_r, lab_r, bar_r, "phase_3")
    court.print_verdict(verdict1)

    # Test 2: Genuinely problematic signal — noise with axiom violation
    print("\n─── Case 2: Noise signal with agency_over_automation violation ─")
    signal2 = CoherenceSignal(
        signal=np.array([72, 68, 75, 63, 70, 67, 73, 65, 71, 64], dtype=float),
        domain="meta", label="Noisy signal with axiom violation",
    )
    axioms_bad = AxiomCheck(AXIOM_YES, AXIOM_NO, AXIOM_YES, AXIOM_TENSION)
    fated2 = FATEDReasoning(
        "Mixed signal. Automated system made the call.",
        "Assuming automation is correct here.",
        "Speed favored over human review.",
        "Uncertain — this feels wrong.",
        "Proceed anyway.",
    )
    somatic2 = SomaticReading(0.4, 0.3, 0.35, 0.4, 0.3, 0.45)

    sage_r2 = sage.run(signal=signal2, fated=fated2, axioms=axioms_bad, somatic=somatic2,
                       hci_score=55.0, phase_id="phase_test", next_action="test", irreversibility=0.80)
    lab_r2 = lab.run(sage_r2, "phase_test")
    bar_r2 = bar.run(sage_r2, lab_r2, "phase_test")

    print(f"  BAR verdict: {bar_r2.bar_verdict}")
    verdict2 = court.adjudicate(sage_r2, lab_r2, bar_r2, "phase_test")
    court.print_verdict(verdict2)

    print(f"\n✅ Constitutional Court verified. Cases adjudicated: 2.")
    print(f"  Case 1 verdict: {verdict1.verdict}")
    print(f"  Case 2 verdict: {verdict2.verdict}")
