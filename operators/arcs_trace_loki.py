"""
arcs_trace_loki.py — Phase 5 Loki Debug Layer
Advanced adversarial tracing: Loki perturbations, BarRaiser (configurable threshold,
ballet-style invocable), AbductiveCalibrator (TP/FP inference without manual labeling),
SocraticTraceDialogue, PreMortemGenerator, AntifragilityMeter.

Canon references:
  - ARCS-LokiMode-MischiefProtocol.md  → Loki Mode as epistemic engine
  - ARCS-Operator17-AdversarialDetective.md → Adversarial validation protocol

Architecture:
    Loki perturbations are NOT re-runs of the pipeline.
    They are trace-level boundary injections — the span corpus IS the Loki learning loop.
    Every TraceAnomaly is a Loki-discovered boundary marker.

BarRaiser threshold design:
    - Default: 0.65 (flag if bar_score < 0.65)
    - Configurable: expose as slider in debug mode (FE integration hook provided)
    - Dynamic weighting supported: context-aware threshold adjustment
    - Three tests: Independence, Gate Smell, Socratic Reread
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from arcs_trace import (
    AnomalyType,
    BranchTag,
    EventType,
    TraceAnnotation,
    TraceAnomaly,
    TraceEvent,
    TraceLogger,
    TraceSpan,
    _new_id,
)


# ---------------------------------------------------------------------------
# Loki Perturbation Types
# ---------------------------------------------------------------------------

class LokiPerturbationType(str, Enum):
    # Rule-level perturbations
    AXIOM_INVERSION       = "axiom_inversion"       # flip all axiom verdicts
    NCI_FLOOR_INJECT      = "nci_floor_inject"       # force NCI to minimum
    NCI_CEILING_INJECT    = "nci_ceiling_inject"     # force NCI to maximum
    RUIN_FORCE_TRUE       = "ruin_force_true"        # inject ruin_risk=True
    IRREV_MAX_INJECT      = "irrev_max_inject"       # inject irreversibility=1.0

    # Boundary perturbations
    GATE_MINUS_ONE        = "gate_minus_one"         # shift phase gate NCI −1
    GATE_PLUS_ONE         = "gate_plus_one"          # shift phase gate NCI +1
    OPERATOR_DROP         = "operator_drop"          # remove one operator from trace
    OPERATOR_REORDER      = "operator_reorder"       # swap operator sequence

    # Perspective perturbations
    PESSIMIST_LENS        = "pessimist_lens"         # weight all risk signals ×2
    OPTIMIST_LENS         = "optimist_lens"          # weight all risk signals ×0.5
    BASE_RATE_CHALLENGE   = "base_rate_challenge"    # inject historical failure rate
    SECOND_ORDER_EFFECTS  = "second_order_effects"   # inject downstream consequences

    # Combination experiments
    COMPOUND_STRESS       = "compound_stress"        # ruin + cliff + axiom together
    NULL_HYPOTHESIS       = "null_hypothesis"        # all signals → noise baseline


@dataclass
class LokiPerturbation:
    perturbation_id:   str
    perturbation_type: LokiPerturbationType
    span_id:           str
    applied_at:        float
    description:       str
    parameters:        Dict[str, Any] = field(default_factory=dict)
    result_summary:    Dict[str, Any] = field(default_factory=dict)
    anomalies_induced: List[str]      = field(default_factory=list)  # anomaly_ids

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["perturbation_type"] = self.perturbation_type.value
        return d


@dataclass
class LokiDebugSession:
    """Wraps a trace session with Loki augmentation."""
    session_id:         str
    base_span_id:       str
    perturbations:      List[LokiPerturbation] = field(default_factory=list)
    replay_results:     List["LokiReplayResult"] = field(default_factory=list)
    antifragility_score: Optional[float] = None
    pre_mortems:        List[str] = field(default_factory=list)  # narrative strings
    socratic_exchanges: List["SocraticExchange"] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        return {
            "session_id":           self.session_id,
            "base_span_id":         self.base_span_id,
            "perturbation_count":   len(self.perturbations),
            "anomalies_induced":    sum(len(p.anomalies_induced) for p in self.perturbations),
            "antifragility_score":  self.antifragility_score,
            "pre_mortem_count":     len(self.pre_mortems),
        }


@dataclass
class LokiReplayResult:
    """Result of replaying a span with perturbation."""
    replay_id:         str
    original_span_id:  str
    perturbation_id:   str
    replay_span_id:    str
    original_verdict:  Optional[str]
    replay_verdict:    Optional[str]
    original_nci_exit: Optional[float]
    replay_nci_exit:   Optional[float]
    hash_match:        bool         # True if replay hash matches original
    divergence_notes:  str = ""

    @property
    def verdict_changed(self) -> bool:
        return self.original_verdict != self.replay_verdict

    @property
    def nci_delta(self) -> Optional[float]:
        if self.original_nci_exit is not None and self.replay_nci_exit is not None:
            return self.replay_nci_exit - self.original_nci_exit
        return None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Socratic Trace Dialogue (≤ 3 rounds, per Operator 17 spec)
# ---------------------------------------------------------------------------

@dataclass
class SocraticExchange:
    round_num:   int      # 1, 2, or 3 (max)
    question:    str
    answer:      str
    confidence:  float    # 0.0–1.0 after this round
    timestamp:   float = field(default_factory=time.time)


class SocraticTraceDialogue:
    """
    ≤ 3-round Socratic dialogue grounded in trace evidence.
    Questions are generated from anomalies and span structure.
    Max 3 rounds enforced (per Operator 17 Adversarial Detective spec).
    """

    MAX_ROUNDS = 3

    QUESTION_TEMPLATES = [
        "What specific evidence in the trace CONTRADICTS the {operator} verdict?",
        "If the NCI were 10 points lower, would the outcome change? Which event would flip first?",
        "Which anomaly ({anomaly_type}) was most likely a FALSE POSITIVE and why?",
        "What would have to be true for this RUIN_RISK flag to be a false alarm?",
        "Is the operator sequence ({ops}) the minimum coherent path, or could steps be removed?",
    ]

    def __init__(self, span: TraceSpan):
        self.span     = span
        self.rounds:  List[SocraticExchange] = []
        self._closed  = False

    def ask(self) -> Optional[str]:
        """Generate the next Socratic question from trace evidence, or None if max rounds hit."""
        if len(self.rounds) >= self.MAX_ROUNDS:
            self._closed = True
            return None

        round_num = len(self.rounds) + 1
        question  = self._generate_question(round_num)
        return question

    def answer(self, response: str, confidence: float) -> SocraticExchange:
        """Record a response to the current Socratic question."""
        if self._closed:
            raise RuntimeError("Dialogue is closed (max rounds reached)")

        question = self._generate_question(len(self.rounds) + 1)
        exchange = SocraticExchange(
            round_num=len(self.rounds) + 1,
            question=question,
            answer=response,
            confidence=confidence,
        )
        self.rounds.append(exchange)
        if len(self.rounds) >= self.MAX_ROUNDS:
            self._closed = True
        return exchange

    def _generate_question(self, round_num: int) -> str:
        ops = [e.operator for e in self.span.events if e.event_type == EventType.OPERATOR_END]
        anomaly_types = [a.anomaly_type.value for a in self.span.anomalies]
        dominant_anomaly = anomaly_types[0] if anomaly_types else "none"
        last_operator    = ops[-1] if ops else "unknown"

        templates = [
            f"What specific evidence in this span CONTRADICTS the {last_operator} verdict of '{self.span.verdict}'?",
            f"If the NCI were 10 points lower at entry ({(self.span.nci_entry or 0) - 10:.0f}), which operator result would flip first?",
            f"The anomaly '{dominant_anomaly}' was detected. Is this signal or noise? What trace evidence supports each position?",
        ]
        idx = min(round_num - 1, len(templates) - 1)
        return templates[idx]

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def final_confidence(self) -> Optional[float]:
        return self.rounds[-1].confidence if self.rounds else None


# ---------------------------------------------------------------------------
# Pre-Mortem Generator (trace-grounded)
# ---------------------------------------------------------------------------

class LokiPreMortemGenerator:
    """
    Generates five Operator-17-style pre-mortem narratives from trace evidence.
    Each narrative is a "This is how we failed" scenario grounded in span data.
    """

    TEMPLATES = [
        # 1. Munger Inversion
        lambda span, ops, anomalies: (
            f"[Munger Inversion] We succeeded at maximizing the OPPOSITE of our goal. "
            f"The {ops[0] if ops else 'pipeline'} produced a {span.verdict} verdict at NCI={span.nci_exit}, "
            f"but if every operator decision had been inverted, we would have BLOCKED with stronger evidence. "
            f"Ask: which inversion would be hardest to detect?"
        ),
        # 2. Klein Pre-Mortem
        lambda span, ops, anomalies: (
            f"[Klein Pre-Mortem] It is 6 months from now. The {span.phase_id} decision failed. "
            f"The NCI dropped from {span.nci_exit or '?'} to below 50. "
            f"The proximate cause was the {anomalies[0] if anomalies else 'undetected drift'} anomaly "
            f"that we dismissed. What compounding factors made this a crisis rather than a correction?"
        ),
        # 3. Base Rate Challenge
        lambda span, ops, anomalies: (
            f"[Base Rate Challenge] How often does a '{span.verdict}' verdict at NCI={span.nci_exit} "
            f"precede a NCI_CLIFF in the next span? "
            f"If the historical rate is >20%, this verdict requires additional evidence weight, not less."
        ),
        # 4. Second-Order Effects
        lambda span, ops, anomalies: (
            f"[Second-Order Effects] The {span.verdict} verdict commits downstream systems. "
            f"Operator sequence was: {' → '.join(ops[:5])}. "
            f"What decisions become HARDER to reverse as a result of this commit? "
            f"Is irreversibility_score={span.metadata.get('irreversibility', '?')} honest?"
        ),
        # 5. Adversarial Example
        lambda span, ops, anomalies: (
            f"[Adversarial Example] Construct the minimum input modification that would flip "
            f"the verdict from '{span.verdict}' to BLOCK. "
            f"If that modification is within ±10% of any input parameter, "
            f"the verdict is not robust."
        ),
    ]

    def generate(self, span: TraceSpan) -> List[str]:
        ops       = [e.operator for e in span.events if e.event_type == EventType.OPERATOR_END]
        anomalies = [a.anomaly_type.value for a in span.anomalies]
        return [
            tmpl(span, ops, anomalies)
            for tmpl in self.TEMPLATES
        ]


# ---------------------------------------------------------------------------
# BarRaiser — configurable threshold, ballet-style invocable
# ---------------------------------------------------------------------------

@dataclass
class BarRaiserReview:
    review_id:          str
    span_id:            str
    invoked_by:         str          # operator name that triggered this review
    timestamp:          float
    threshold_used:     float        # configurable: default 0.65, adjustable via slider
    # Three tests (per spec)
    independence_check: bool         # True = reasoning trail stands without re-running
    gate_smell_test:    bool         # True = NCI not suspiciously gate-adjacent
    socratic_reread:    bool         # True = FATED holds up under Socratic questioning
    # Scores (0.0–1.0 each)
    independence_score: float
    gate_smell_score:   float
    socratic_score:     float
    # Verdict
    bar_score:          float        # weighted composite
    verdict:            str          # "ENDORSED" | "FLAG_FOR_REVIEW"
    flag_reason:        str = ""
    recommendations:    List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BarRaiser:
    """
    Ballet-style peer review service.
    Any operator can invoke BarRaiser.  Not a sequential pipeline step.
    Reads reasoning trail only (no signal/derivative re-runs → no 2x compute).

    Threshold design:
        - default_threshold: 0.65 (ENDORSED if bar_score ≥ threshold)
        - Expose as FE slider in debug mode via get_threshold_config()
        - Dynamic context weighting adjusts effective threshold situationally
    """

    # Test weights (must sum to 1.0)
    W_INDEPENDENCE = 0.40
    W_GATE_SMELL   = 0.35
    W_SOCRATIC     = 0.25

    # Default threshold — configurable
    DEFAULT_THRESHOLD = 0.65

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        dynamic_weighting: bool = True,
    ):
        self.threshold        = threshold
        self.dynamic_weighting = dynamic_weighting
        self._threshold_overrides: Dict[str, float] = {}  # context_key → threshold

    # --- Threshold config (FE slider hook) ---

    def set_threshold(self, threshold: float) -> None:
        """Adjust global threshold.  FE debug slider calls this."""
        assert 0.0 <= threshold <= 1.0, "Threshold must be 0.0–1.0"
        self.threshold = threshold

    def set_context_threshold(self, context_key: str, threshold: float) -> None:
        """Set a context-specific threshold (dynamic weighting)."""
        self._threshold_overrides[context_key] = threshold

    def get_threshold_config(self) -> Dict[str, Any]:
        """Returns full threshold config for FE slider rendering."""
        return {
            "global_threshold":    self.threshold,
            "default_threshold":   self.DEFAULT_THRESHOLD,
            "context_overrides":   self._threshold_overrides,
            "dynamic_weighting":   self.dynamic_weighting,
            "slider_min":          0.30,
            "slider_max":          0.90,
            "slider_step":         0.05,
            "description": (
                "Lower threshold = more reviews flagged (more sensitive). "
                "Higher threshold = only strong failures flagged (more permissive). "
                "Default 0.65 is calibrated for gate-adjacent NCI detection."
            ),
        }

    def _effective_threshold(self, span: TraceSpan) -> float:
        """Compute context-aware effective threshold if dynamic_weighting enabled."""
        if not self.dynamic_weighting:
            return self.threshold
        base = self.threshold
        # Increase threshold (more permissive) when NCI is clearly above gate
        nci = span.nci_exit or 0
        if nci >= 92:
            return min(base + 0.10, 0.90)   # high confidence → relax scrutiny
        if nci <= 70:
            return max(base - 0.10, 0.30)   # low NCI → tighten scrutiny
        return base

    # --- Three tests ---

    def _independence_check(self, span: TraceSpan) -> Tuple[bool, float, str]:
        """
        Reasoning trail stands on its own — no need to re-run signal/derivatives.
        Check: does FATED exist and is it substantive?
        Returns (passed, score, reason).
        """
        has_fated      = bool(span.metadata.get("fated_reasoning"))
        has_facts      = bool(span.metadata.get("fated_facts"))
        has_direction  = bool(span.metadata.get("fated_direction"))
        axioms_checked = span.metadata.get("axioms_checked", False)

        score = 0.0
        parts = []
        if has_fated:
            score += 0.40
            parts.append("FATED present")
        if has_facts:
            score += 0.20
            parts.append("facts documented")
        if has_direction:
            score += 0.20
            parts.append("direction documented")
        if axioms_checked:
            score += 0.20
            parts.append("axioms checked")

        passed = score >= 0.60
        reason = "; ".join(parts) if parts else "no reasoning trail found"
        return passed, round(score, 3), reason

    def _gate_smell_test(self, span: TraceSpan) -> Tuple[bool, float, str]:
        """
        NCI should not be suspiciously gate-adjacent (+/- 2 points of a phase gate).
        Gate-adjacent NCIs suggest the system optimized toward the threshold.
        """
        import arcs_rom
        gates = arcs_rom.PHASE_GATES  # e.g. {"phase_1": 75, "phase_2": 82, ...}

        nci = span.nci_exit or 0
        gate_values = list(gates.values())

        # Check if NCI is within ±2 of any gate
        gate_adjacent = any(abs(nci - g) <= 2 for g in gate_values)

        if gate_adjacent:
            adjacent_gate = min(gate_values, key=lambda g: abs(nci - g))
            score  = 0.30  # suspicious
            passed = False
            reason = (
                f"NCI={nci:.1f} is within ±2 of phase gate {adjacent_gate} — "
                f"possible threshold optimization"
            )
        else:
            score  = 1.0
            passed = True
            reason = f"NCI={nci:.1f} is not gate-adjacent (clean)"

        return passed, round(score, 3), reason

    def _socratic_reread(self, span: TraceSpan) -> Tuple[bool, float, str]:
        """
        FATED holds up under a single Socratic reread.
        Uses SocraticTraceDialogue round 1 question as the stress test.
        Human or system answers; if no answer provided, defaults to neutral.
        """
        dialogue = SocraticTraceDialogue(span)
        q1       = dialogue.ask()

        # Score is based on span evidence quality (proxy for FATED coherence)
        anomaly_count   = len(span.anomalies)
        event_count     = len(span.events)
        has_direction   = bool(span.metadata.get("fated_direction"))
        verdict_present = span.verdict is not None

        score = 0.70  # baseline
        score -= anomaly_count * 0.08   # each anomaly reduces confidence
        score += 0.10 if has_direction else 0
        score += 0.10 if verdict_present else 0
        score = max(0.0, min(1.0, score))

        passed = score >= 0.50
        reason = (
            f"Socratic reread: anomalies={anomaly_count}, "
            f"events={event_count}, direction_present={has_direction}"
        )
        return passed, round(score, 3), reason

    # --- Main review entry point ---

    def review(
        self,
        span: TraceSpan,
        invoked_by: str = "unknown_operator",
        logger: Optional[TraceLogger] = None,
    ) -> BarRaiserReview:
        """
        Primary review method.  Reads reasoning trail only.
        Can be called by any operator at any time (ballet-style).
        """
        ind_passed, ind_score, ind_reason   = self._independence_check(span)
        gate_passed, gate_score, gate_reason = self._gate_smell_test(span)
        soc_passed, soc_score, soc_reason    = self._socratic_reread(span)

        # Weighted composite
        bar_score = (
            ind_score  * self.W_INDEPENDENCE
            + gate_score * self.W_GATE_SMELL
            + soc_score  * self.W_SOCRATIC
        )

        effective_thresh = self._effective_threshold(span)
        verdict = "ENDORSED" if bar_score >= effective_thresh else "FLAG_FOR_REVIEW"

        # Build flag reason
        flag_parts = []
        if not ind_passed:
            flag_parts.append(f"Independence: {ind_reason}")
        if not gate_passed:
            flag_parts.append(f"Gate smell: {gate_reason}")
        if not soc_passed:
            flag_parts.append(f"Socratic: {soc_reason}")
        flag_reason = " | ".join(flag_parts) if flag_parts else ""

        # Recommendations
        recs = []
        if not ind_passed:
            recs.append("Document FATED reasoning with explicit facts and direction.")
        if not gate_passed:
            recs.append(
                "Verify NCI grade is not threshold-optimized — regrade with fresh eyes."
            )
        if not soc_passed:
            recs.append("Address anomalies before accepting verdict.")

        review = BarRaiserReview(
            review_id=_new_id("br"),
            span_id=span.span_id,
            invoked_by=invoked_by,
            timestamp=time.time(),
            threshold_used=effective_thresh,
            independence_check=ind_passed,
            gate_smell_test=gate_passed,
            socratic_reread=soc_passed,
            independence_score=ind_score,
            gate_smell_score=gate_score,
            socratic_score=soc_score,
            bar_score=round(bar_score, 4),
            verdict=verdict,
            flag_reason=flag_reason,
            recommendations=recs,
        )

        # Emit trace event if logger provided
        if logger and span.span_id in logger._active_spans:
            logger.record_event(
                span_id=span.span_id,
                event_type=EventType.BAR_RAISER_REVIEW,
                operator="bar_raiser",
                outputs_summary={
                    "verdict":      verdict,
                    "bar_score":    review.bar_score,
                    "threshold":    effective_thresh,
                    "flag_reason":  flag_reason[:120] if flag_reason else "",
                },
                branch_tag=BranchTag.BAR_REVIEW,
            )

        return review

    def deep_review(
        self,
        span: TraceSpan,
        invoked_by: str = "unknown_operator",
        logger: Optional[TraceLogger] = None,
    ) -> Tuple[BarRaiserReview, List[str]]:
        """
        Deep review: standard review + full pre-mortem generation.
        Returns (BarRaiserReview, pre_mortems).
        """
        review    = self.review(span, invoked_by=invoked_by, logger=logger)
        generator = LokiPreMortemGenerator()
        pre_mortems = generator.generate(span)
        return review, pre_mortems


# ---------------------------------------------------------------------------
# AbductiveCalibrator — infer TP/FP from subsequent span behavior
# ---------------------------------------------------------------------------

@dataclass
class CalibrationRecord:
    anomaly_id:       str
    span_id:          str
    anomaly_type:     str
    flagged_at:       float
    resolved_at:      Optional[float]
    inferred_label:   Optional[str]   # "TRUE_POSITIVE" | "FALSE_POSITIVE" | None
    confidence:       float
    next_span_nci:    Optional[float]
    next_span_verdict: Optional[str]
    reasoning:        str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AbductiveCalibrator:
    """
    Infer TP/FP labels from subsequent span behavior — no manual labeling required.

    Abductive logic:
        If BarRaiser flagged span N, observe span N+1:
            - span N+1 NCI drops > 5 OR BLOCKED  → TRUE_POSITIVE  (flag predicted failure)
            - span N+1 NCI stable/improving       → FALSE_POSITIVE (flag was noise)
            - span N+1 not yet available           → PENDING

    This is the RL-adjacent component: the trace corpus is the training signal.
    """

    # Thresholds for TP/FP inference
    TP_NCI_DROP_THRESHOLD  = 5.0     # NCI drop > this → TP
    FP_NCI_STABLE_MIN      = 0.0     # NCI change ≥ this → FP candidate
    CONFIDENCE_TP_BLOCKED  = 0.90    # high confidence when next span BLOCKED
    CONFIDENCE_TP_CLIFF    = 0.75    # moderate confidence when NCI dropped
    CONFIDENCE_FP_STABLE   = 0.65    # moderate confidence when NCI stable

    def __init__(self, logger: TraceLogger):
        self.logger  = logger
        self._records: Dict[str, CalibrationRecord] = {}  # anomaly_id → record

    def register_flag(
        self,
        anomaly_id: str,
        span_id: str,
        anomaly_type: str,
    ) -> CalibrationRecord:
        """Register a new BarRaiser flag for deferred calibration."""
        record = CalibrationRecord(
            anomaly_id=anomaly_id,
            span_id=span_id,
            anomaly_type=anomaly_type,
            flagged_at=time.time(),
            resolved_at=None,
            inferred_label=None,
            confidence=0.0,
            next_span_nci=None,
            next_span_verdict=None,
        )
        self._records[anomaly_id] = record
        return record

    def observe_next_span(
        self,
        original_span_id: str,
        next_span: TraceSpan,
    ) -> List[CalibrationRecord]:
        """
        Observe a completed span and calibrate all pending records from original_span_id.
        Returns list of resolved CalibrationRecords.
        """
        resolved = []
        for rec in self._records.values():
            if rec.span_id != original_span_id or rec.inferred_label is not None:
                continue

            # Compute NCI delta between original span and next span
            original_spans = self.logger.backend.read_spans(limit=200)
            orig_nci_exit  = None
            for s in original_spans:
                if s.get("span_id") == original_span_id:
                    orig_nci_exit = s.get("nci_exit")
                    break

            next_nci    = next_span.nci_exit
            next_verdict = next_span.verdict
            rec.next_span_nci    = next_nci
            rec.next_span_verdict = next_verdict
            rec.resolved_at      = time.time()

            if next_verdict == "BLOCKED":
                rec.inferred_label = "TRUE_POSITIVE"
                rec.confidence     = self.CONFIDENCE_TP_BLOCKED
                rec.reasoning      = (
                    f"Next span BLOCKED — flag correctly predicted ruin/axiom failure"
                )
            elif (orig_nci_exit is not None
                  and next_nci is not None
                  and (orig_nci_exit - next_nci) > self.TP_NCI_DROP_THRESHOLD):
                rec.inferred_label = "TRUE_POSITIVE"
                rec.confidence     = self.CONFIDENCE_TP_CLIFF
                rec.reasoning      = (
                    f"NCI dropped {orig_nci_exit - next_nci:.1f} points after flagged span — "
                    f"flag correctly predicted coherence deterioration"
                )
            elif next_nci is not None and (orig_nci_exit is None or next_nci >= orig_nci_exit - self.FP_NCI_STABLE_MIN):
                rec.inferred_label = "FALSE_POSITIVE"
                rec.confidence     = self.CONFIDENCE_FP_STABLE
                rec.reasoning      = (
                    f"NCI stable/improving ({next_nci}) after flagged span — "
                    f"flag was likely noise"
                )
            else:
                rec.inferred_label = "UNCLEAR"
                rec.confidence     = 0.40
                rec.reasoning      = "Insufficient evidence for calibration"

            # Write annotation to trace logger
            self.logger.annotate(
                span_id=original_span_id,
                label=rec.inferred_label,
                annotated_by="abductive_calibrator",
                confidence=rec.confidence,
                notes=rec.reasoning,
            )
            resolved.append(rec)

        return resolved

    def calibration_report(self) -> Dict[str, Any]:
        """Aggregate calibration statistics across all resolved records."""
        resolved  = [r for r in self._records.values() if r.inferred_label is not None]
        tp_count  = sum(1 for r in resolved if r.inferred_label == "TRUE_POSITIVE")
        fp_count  = sum(1 for r in resolved if r.inferred_label == "FALSE_POSITIVE")
        unclear   = sum(1 for r in resolved if r.inferred_label == "UNCLEAR")
        pending   = len(self._records) - len(resolved)

        precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else None
        return {
            "total_flags":    len(self._records),
            "resolved":       len(resolved),
            "pending":        pending,
            "true_positives": tp_count,
            "false_positives": fp_count,
            "unclear":        unclear,
            "precision":      round(precision, 3) if precision is not None else None,
            "target_precision": 0.70,  # from Operator 17 detective accuracy spec
            "above_target":   precision is not None and precision >= 0.70,
        }

    def export_records(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._records.values()]


# ---------------------------------------------------------------------------
# AntifragilityMeter
# ---------------------------------------------------------------------------

class AntifragilityMeter:
    """
    Measures d²Performance/dStress² > 0 across the span corpus.
    Per Operator 17 spec: antifragility = system improves under stress.

    Stress proxy: NCI entry volatility (std dev across spans).
    Performance proxy: NCI delta (exit − entry) per span.
    Antifragility score: correlation between stress and performance delta.
    """

    def compute(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        entries  = [s.get("nci_entry") for s in spans if s.get("nci_entry") is not None]
        deltas   = [
            s.get("nci_exit", 0) - s.get("nci_entry", 0)
            for s in spans
            if s.get("nci_entry") is not None and s.get("nci_exit") is not None
        ]

        if len(entries) < 3:
            return {"score": None, "reason": "insufficient_data (need ≥ 3 spans)"}

        # Stress = deviation from mean NCI entry
        mean_entry = sum(entries) / len(entries)
        stress     = [abs(e - mean_entry) for e in entries[:len(deltas)]]

        # Correlation proxy: does more stress → more positive delta?
        paired     = list(zip(stress, deltas))
        n          = len(paired)
        mean_s     = sum(s for s, d in paired) / n
        mean_d     = sum(d for s, d in paired) / n
        cov        = sum((s - mean_s) * (d - mean_d) for s, d in paired) / n
        std_s      = (sum((s - mean_s)**2 for s, d in paired) / n) ** 0.5
        std_d      = (sum((d - mean_d)**2 for s, d in paired) / n) ** 0.5

        if std_s == 0 or std_d == 0:
            corr = 0.0
        else:
            corr = cov / (std_s * std_d)

        # Score: 0.0 = perfectly fragile, 1.0 = perfectly antifragile
        # corr range is −1 to +1; map to 0–1
        score = (corr + 1) / 2

        return {
            "score":            round(score, 4),
            "correlation":      round(corr, 4),
            "spans_analyzed":   n,
            "mean_nci_entry":   round(mean_entry, 2),
            "interpretation": (
                "antifragile (stress improves performance)"
                if score > 0.60 else
                "fragile (stress degrades performance)"
                if score < 0.40 else
                "neutral (stress has no consistent effect)"
            ),
            "target": "> 0.60 for antifragile classification",
        }


# ---------------------------------------------------------------------------
# LokiEngine — orchestrates all Loki primitives
# ---------------------------------------------------------------------------

class LokiEngine:
    """
    Top-level Loki Mode orchestrator.
    Wraps a TraceLogger with full adversarial debug capability.
    """

    def __init__(
        self,
        logger: TraceLogger,
        bar_threshold: float = BarRaiser.DEFAULT_THRESHOLD,
    ):
        self.logger        = logger
        self.bar_raiser    = BarRaiser(threshold=bar_threshold)
        self.calibrator    = AbductiveCalibrator(logger)
        self.antifragility = AntifragilityMeter()
        self._sessions: Dict[str, LokiDebugSession] = {}

    def open_debug_session(self, base_span_id: str) -> LokiDebugSession:
        session = LokiDebugSession(
            session_id=_new_id("loki"),
            base_span_id=base_span_id,
        )
        self._sessions[base_span_id] = session
        return session

    def bar_review(
        self,
        span: TraceSpan,
        invoked_by: str,
        deep: bool = False,
    ) -> BarRaiserReview:
        """Ballet-style BarRaiser invocation.  Any operator can call this."""
        if deep:
            review, pre_mortems = self.bar_raiser.deep_review(
                span, invoked_by=invoked_by, logger=self.logger
            )
            ds = self._sessions.get(span.span_id)
            if ds:
                ds.pre_mortems.extend(pre_mortems)
        else:
            review = self.bar_raiser.review(
                span, invoked_by=invoked_by, logger=self.logger
            )

        # Register any FLAG_FOR_REVIEW with calibrator
        if review.verdict == "FLAG_FOR_REVIEW":
            for a in span.anomalies:
                self.calibrator.register_flag(
                    anomaly_id=a.anomaly_id,
                    span_id=span.span_id,
                    anomaly_type=a.anomaly_type.value,
                )

        return review

    def calibrate(
        self,
        original_span_id: str,
        next_span: TraceSpan,
    ) -> List[CalibrationRecord]:
        """Auto-calibrate flags from original_span_id using next_span evidence."""
        return self.calibrator.observe_next_span(original_span_id, next_span)

    def antifragility_report(self) -> Dict[str, Any]:
        spans = self.logger.get_span_history(limit=100)
        return self.antifragility.compute(spans)

    def perturbation_summary(self, base_span_id: str) -> Optional[Dict[str, Any]]:
        ds = self._sessions.get(base_span_id)
        return ds.summary() if ds else None

    def socratic_dialogue(self, span: TraceSpan) -> SocraticTraceDialogue:
        return SocraticTraceDialogue(span)

    def pre_mortem(self, span: TraceSpan) -> List[str]:
        return LokiPreMortemGenerator().generate(span)

    def threshold_config(self) -> Dict[str, Any]:
        """FE debug slider hook — returns full threshold config."""
        return self.bar_raiser.get_threshold_config()


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    import tempfile, shutil
    from arcs_trace import TraceLogger, JSONLBackend, BranchTag, EventType

    print("=== arcs_trace_loki.py smoke test ===\n")

    tmp = tempfile.mkdtemp()
    try:
        # 1. Setup
        backend = JSONLBackend(base_dir=tmp)
        logger  = TraceLogger(backend=backend, pipeline_version="5.0.0-test")
        logger.start_session()
        span_id = logger.start_span(phase_id="phase_5", nci_entry=88.0)

        # Add some events
        logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="sage",
            outputs_summary={"nci_score": 88.0},
            nci_after=88.0,
        )
        logger.record_event(
            span_id=span_id,
            event_type=EventType.COURT_VERDICT,
            operator="court",
            outputs_summary={"verdict": "PERMIT"},
            nci_after=88.0,
        )

        # Close span with metadata (FATED stub)
        span = logger._active_spans[span_id]
        span.metadata.update({
            "fated_reasoning":  True,
            "fated_facts":      True,
            "fated_direction":  True,
            "axioms_checked":   True,
        })

        # 2. BarRaiser review — gate-smell test: NCI=88 is 2-adjacent to phase_5 gate=86
        loki = LokiEngine(logger, bar_threshold=0.65)
        review = loki.bar_review(span, invoked_by="curator")
        print(f"[OK] BarRaiser verdict: {review.verdict}")
        print(f"     bar_score={review.bar_score:.3f}, threshold={review.threshold_used}")
        print(f"     independence={review.independence_score:.2f}, "
              f"gate_smell={review.gate_smell_score:.2f}, "
              f"socratic={review.socratic_score:.2f}")
        if review.flag_reason:
            print(f"     flag_reason: {review.flag_reason[:80]}")

        # 3. Test configurable threshold via slider
        loki.bar_raiser.set_threshold(0.30)  # very permissive
        review_permissive = loki.bar_raiser.review(span, invoked_by="alchemist")
        assert review_permissive.verdict == "ENDORSED", \
            f"Expected ENDORSED at threshold 0.30, got {review_permissive.verdict}"
        loki.bar_raiser.set_threshold(0.65)  # reset
        print(f"[OK] Threshold slider: ENDORSED at 0.30, original at 0.65={review.verdict}")

        # 4. Deep review (bar + pre-mortem)
        review2, pre_mortems = loki.bar_raiser.deep_review(span, invoked_by="lab")
        assert len(pre_mortems) == 5
        print(f"[OK] Deep review: {len(pre_mortems)} pre-mortems generated")
        print(f"     Sample: {pre_mortems[0][:80]}...")

        # 5. Socratic dialogue
        dialogue = loki.socratic_dialogue(span)
        q1 = dialogue.ask()
        assert q1 is not None
        exchange = dialogue.answer("The verdict is supported by NCI > gate.", 0.80)
        assert exchange.round_num == 1
        q2 = dialogue.ask()
        assert q2 is not None
        exchange2 = dialogue.answer("COURT_VERDICT present confirms immune system ran.", 0.85)
        q3 = dialogue.ask()
        exchange3 = dialogue.answer("No critical anomalies undermine this.", 0.90)
        assert dialogue.is_closed  # 3 rounds reached
        assert dialogue.ask() is None  # closed
        print(f"[OK] Socratic dialogue: 3/3 rounds, final confidence={dialogue.final_confidence:.2f}")

        # 6. AbductiveCalibrator
        span.anomalies.append(
            TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.NCI_CLIFF,
                severity="HIGH",
                span_id=span_id,
                event_id=None,
                description="Injected for calibrator test",
            )
        )
        cal_rec = loki.calibrator.register_flag(
            anomaly_id=span.anomalies[-1].anomaly_id,
            span_id=span_id,
            anomaly_type="nci_cliff",
        )

        # Simulate next span: BLOCKED (should infer TRUE_POSITIVE)
        span_closed = logger.end_span(span_id, verdict="COMPLETE", nci_exit=88.0)

        next_span_id = logger.start_span(phase_id="phase_5", nci_entry=70.0)
        logger.record_event(
            span_id=next_span_id,
            event_type=EventType.PIPELINE_END,
            operator="pipeline",
            outputs_summary={"verdict": "BLOCKED"},
            nci_after=62.0,
        )
        next_span = logger._active_spans[next_span_id]
        next_span.verdict = "BLOCKED"
        next_span.nci_exit = 62.0

        resolved = loki.calibrate(span_id, next_span)
        assert len(resolved) == 1
        assert resolved[0].inferred_label == "TRUE_POSITIVE"
        print(f"[OK] AbductiveCalibrator: inferred label = {resolved[0].inferred_label}")
        print(f"     reasoning: {resolved[0].reasoning[:70]}...")

        # Close next span
        logger.end_span(next_span_id, verdict="BLOCKED", nci_exit=62.0)

        # 7. Calibration report
        report = loki.calibrator.calibration_report()
        assert report["true_positives"] == 1
        print(f"[OK] Calibration report: precision={report['precision']}, "
              f"TP={report['true_positives']}, FP={report['false_positives']}")

        # 8. Antifragility meter (need multiple spans — create a few)
        for nci_entry in [78, 70, 82, 66, 90]:
            s = logger.start_span(phase_id="phase_5", nci_entry=float(nci_entry))
            logger.end_span(s, verdict="COMPLETE", nci_exit=float(nci_entry) + 3)
        af = loki.antifragility_report()
        assert isinstance(af.get("score"), float) or af.get("score") is None
        print(f"[OK] Antifragility meter: score={af.get('score')}, {af.get('interpretation', 'N/A')}")

        # 9. Threshold config (FE slider hook)
        config = loki.threshold_config()
        assert config["slider_min"] == 0.30
        assert config["slider_max"] == 0.90
        print(f"[OK] Threshold config: slider {config['slider_min']}–{config['slider_max']}, "
              f"step={config['slider_step']}")

        print("\n=== Smoke test PASSED — arcs_trace_loki.py ===")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    _smoke_test()
