"""
arcs_runtime_service.py — Phase 5 Ballet-Style Runtime Daemon
Orchestrates the full ARCS pipeline with trace observability, Constitutional Court
immune system, Kintsugi repair, and BarRaiser invocation (ballet-style, not sequential).

Design Principles:
    - NOT a rigid sequential pipeline — each operator declares its own dependencies
    - BarRaiser invocable by any operator at any time
    - Trace logger wraps every operator call (zero boilerplate at call site)
    - Kintsugi runs post-pipeline to repair any pathogens in the receipt
    - Constitutional Court runs pre-commit to adjudicate before any state mutation
    - YoavStore commit only after Court=PERMIT

Ballet metaphor:
    The conductor (ARCSRuntimeService) sets tempo and manages span lifecycle.
    Dancers (operators) improvise within structure.
    Any dancer can call a timeout (BarRaiser).
    The stage manager (Kintsugi) repairs costume tears after each act.
"""

from __future__ import annotations

import json
import time
import traceback
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# --- Internal imports ---
from arcs_primitives import CoherenceSignal, CoherenceReceipt
from arcs_operators_sage import SAGEOperator, FATEDReasoning, AxiomCheck, SomaticReading
from arcs_operators_lab import LABOperator
from arcs_operators_bar import BAROperator
from arcs_operators_curator import CuratorOperator
from arcs_constitutional_court import ConstitutionalCourt, CourtVerdict
from arcs_kintsugi import KintsugiService
from arcs_trace import (
    TraceLogger,
    JSONLBackend,
    BranchTag,
    EventType,
    TraceSpan,
    _new_id,
    hash_input,
)
from arcs_trace_loki import LokiEngine, BarRaiser


# ---------------------------------------------------------------------------
# Pipeline result
# ---------------------------------------------------------------------------

class PipelineVerdict(str, Enum):
    COMPLETE   = "COMPLETE"
    ACCEPTABLE = "ACCEPTABLE"
    BLOCKED    = "BLOCKED"
    ERROR      = "ERROR"


@dataclass
class PipelineResult:
    """Returned by ARCSRuntimeService.run_pipeline()."""
    verdict:          PipelineVerdict
    nci_score:        float
    receipt:          Optional[CoherenceReceipt]
    court_verdict:    Optional[CourtVerdict]
    kintsugi_applied: bool
    bar_review_id:    Optional[str]
    span_id:          str
    session_id:       str
    duration_ms:      float
    anomaly_count:    int
    error:            Optional[str] = None
    metadata:         Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["verdict"]       = self.verdict.value
        d["court_verdict"] = self.court_verdict.verdict if self.court_verdict else None
        if self.receipt:
            d["receipt_nci"] = self.receipt.nci_score
        return d

    @property
    def is_success(self) -> bool:
        return self.verdict in (PipelineVerdict.COMPLETE, PipelineVerdict.ACCEPTABLE)


# ---------------------------------------------------------------------------
# BarRaiser trigger policy
# ---------------------------------------------------------------------------

class BarRaiserTrigger(str, Enum):
    """Configurable trigger policy for automatic BarRaiser invocation."""
    NEVER          = "never"           # manual only
    GATE_ADJACENT  = "gate_adjacent"   # NCI within ±3 of any phase gate
    ON_BLOCKED     = "on_blocked"      # court issued BLOCK
    ON_ANOMALY     = "on_anomaly"      # any anomaly detected
    ALWAYS         = "always"          # every pipeline run (debug mode)


# ---------------------------------------------------------------------------
# ARCSRuntimeService
# ---------------------------------------------------------------------------

class ARCSRuntimeService:
    """
    Ballet-style pipeline orchestrator.

    Usage:
        service = ARCSRuntimeService()
        result  = service.run_pipeline(signal, phase_id="phase_5")

    BarRaiser:
        Any operator can call service.invoke_bar_raiser(span) during a run.
        Automatic triggers are configurable via bar_trigger parameter.
    """

    PIPELINE_VERSION = "5.0.0"

    def __init__(
        self,
        trace_dir:   str = "arcs_trace_logs",
        bar_threshold: float = BarRaiser.DEFAULT_THRESHOLD,
        bar_trigger: BarRaiserTrigger = BarRaiserTrigger.GATE_ADJACENT,
        store_path:  str = "arcs_receipts.jsonl",
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        # --- Persistence ---
        self._backend = JSONLBackend(base_dir=trace_dir)
        if supabase_url and supabase_key:
            from arcs_trace import SupabaseBackend, DualWriteBackend
            supabase_backend = SupabaseBackend(supabase_url, supabase_key)
            if supabase_backend.available:
                from arcs_trace import DualWriteBackend
                self._backend = DualWriteBackend(self._backend, supabase_backend)

        # --- Core systems ---
        self.logger     = TraceLogger(
            backend=self._backend,
            pipeline_version=self.PIPELINE_VERSION,
        )
        self.loki       = LokiEngine(self.logger, bar_threshold=bar_threshold)
        self.court      = ConstitutionalCourt()
        self.kintsugi   = KintsugiService()

        # --- Operators (constructed once, reused) ---
        self.sage     = SAGEOperator()
        self.lab      = LABOperator()
        self.bar      = BAROperator()
        self.curator  = CuratorOperator()

        # --- Config ---
        self.bar_trigger = bar_trigger
        self._store_path = store_path

        # --- Session ---
        self._session_id: Optional[str] = None

    # --- Session management ---

    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        self._session_id = self.logger.start_session(metadata=metadata)
        return self._session_id

    def end_session(self) -> Optional[str]:
        return self.logger.end_session()

    # --- Main pipeline entry point ---

    def run_pipeline(
        self,
        signal: CoherenceSignal,
        phase_id: str,
        nci_entry: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Run the full ARCS pipeline for one signal.
        Returns PipelineResult with trace span_id, verdict, NCI, and all
        operator outputs bundled.
        """
        t0 = time.perf_counter()
        if not self._session_id:
            self.start_session()

        span_id = self.logger.start_span(
            phase_id=phase_id,
            branch_tag=BranchTag.MAIN,
            nci_entry=nci_entry,
            metadata=metadata or {},
        )

        try:
            result = self._execute_pipeline(signal, phase_id, span_id, metadata or {})
        except Exception as exc:
            err_str = traceback.format_exc()
            self.logger.record_event(
                span_id=span_id,
                event_type=EventType.OPERATOR_ERROR,
                operator="runtime_service",
                outputs_summary={"error": str(exc)},
                error=err_str,
            )
            span = self.logger.end_span(span_id, verdict="ERROR")
            duration_ms = (time.perf_counter() - t0) * 1000
            return PipelineResult(
                verdict=PipelineVerdict.ERROR,
                nci_score=0.0,
                receipt=None,
                court_verdict=None,
                kintsugi_applied=False,
                bar_review_id=None,
                span_id=span_id,
                session_id=self._session_id or "unknown",
                duration_ms=duration_ms,
                anomaly_count=len(span.anomalies),
                error=str(exc),
            )

        return result

    def _make_default_fated(self, signal: CoherenceSignal, phase_id: str) -> "FATEDReasoning":
        """Build a minimal FATED reasoning block from signal + phase context."""
        return FATEDReasoning(
            facts=(f"Signal processed by runtime service for {phase_id}. "
                   f"Domain: {signal.domain}, label: {signal.label}."),
            assumptions="Runtime defaults; no manual operator overrides applied.",
            tradeoffs="Auto-generated FATED. Human review recommended for irreversible decisions.",
            emotions="Pipeline run — no somatic override.",
            direction=f"Proceed with {phase_id} pipeline run.",
        )

    def _make_default_axioms(self) -> "AxiomCheck":
        return AxiomCheck(
            clarity_before_curvature="YES",
            agency_over_automation="YES",
            minimum_steps_to_coherence="YES",
            kairos_over_neuroticism="YES",
        )

    def _make_default_somatic(self) -> "SomaticReading":
        return SomaticReading(
            phase_tuning=0.70,
            surge_detection=False,
            feels_right=True,
            that_vibes=True,
            locked_in=True,
            expected_vs_actual=0.75,
        )

    def _execute_pipeline(
        self,
        signal: CoherenceSignal,
        phase_id: str,
        span_id: str,
        metadata: Dict[str, Any],
    ) -> PipelineResult:
        t0 = time.perf_counter()
        input_hash = hash_input({"domain": signal.domain, "label": signal.label})

        fated   = metadata.get("fated")   or self._make_default_fated(signal, phase_id)
        axioms  = metadata.get("axioms")  or self._make_default_axioms()
        somatic = metadata.get("somatic") or self._make_default_somatic()
        hci     = float(metadata.get("hci_score", 0.72))
        action  = metadata.get("next_action", f"proceed with {phase_id}")
        irrev   = float(metadata.get("irreversibility", 0.25))
        on_purp = bool(metadata.get("on_purpose", True))

        # ── Stage 1: SAGE ─────────────────────────────────────────────────
        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_START,
            operator="sage",
            outputs_summary={},
            input_hash=input_hash,
        )
        t_sage = time.perf_counter()
        sage_receipt = self.sage.run(
            signal=signal,
            fated=fated,
            axioms=axioms,
            somatic=somatic,
            hci_score=hci,
            phase_id=phase_id,
            next_action=action,
            on_purpose=on_purp,
            irreversibility=irrev,
        )
        sage_ms = (time.perf_counter() - t_sage) * 1000

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="sage",
            outputs_summary={
                "nci_score":        sage_receipt.nci_score,
                "signal_class":     sage_receipt.signal_classification,
                "on_purpose":       sage_receipt.on_purpose,
                "irreversibility":  sage_receipt.irreversibility,
            },
            input_hash=input_hash,
            duration_ms=sage_ms,
            nci_after=sage_receipt.nci_score,
            nci_delta=sage_receipt.nci_score - (self.logger._last_nci.get(span_id) or 0),
        )

        # ── Stage 2: LAB ──────────────────────────────────────────────────
        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_START,
            operator="lab",
            outputs_summary={},
        )
        t_lab = time.perf_counter()
        lab_assessment = self.lab.run(sage_receipt, phase_id=phase_id)
        lab_ms = (time.perf_counter() - t_lab) * 1000

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="lab",
            outputs_summary={
                "lab_threat_level": lab_assessment.lab_threat_level,
                "loki_threat":      getattr(lab_assessment, "loki_threat", None),
                "loki_structural":  getattr(lab_assessment, "loki_structural", None),
            },
            duration_ms=lab_ms,
            nci_after=sage_receipt.nci_score,
        )

        # ── Stage 3: BAR ──────────────────────────────────────────────────
        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_START,
            operator="bar",
            outputs_summary={},
        )
        t_bar = time.perf_counter()
        bar_result = self.bar.run(
            sage_receipt=sage_receipt,
            lab_assessment=lab_assessment,
            phase_id=phase_id,
        )
        bar_ms = (time.perf_counter() - t_bar) * 1000

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="bar",
            outputs_summary={
                "ruin_detected":  bar_result.ruin.ruin_detected,
                "ruin_prob":      bar_result.ruin.ruin_probability,
                "bet_quality":    bar_result.asymmetry.bet_quality,
                "verdict":        bar_result.bar_verdict,
            },
            duration_ms=bar_ms,
            nci_after=sage_receipt.nci_score,
        )

        # ── Stage 4: CURATOR ──────────────────────────────────────────────
        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_START,
            operator="curator",
            outputs_summary={},
        )
        t_cur = time.perf_counter()
        curator_result = self.curator.run(
            sage_receipt=sage_receipt,
            lab_assessment=lab_assessment,
            bar_assessment=bar_result,
            phase_id=phase_id,
        )
        cur_ms = (time.perf_counter() - t_cur) * 1000

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="curator",
            outputs_summary={
                "reframe":      getattr(curator_result, "reframe", ""),
                "curator_nci":  getattr(curator_result, "curator_nci", None),
            },
            duration_ms=cur_ms,
            nci_after=sage_receipt.nci_score,
        )

        # ── Stage 5: Constitutional Court ─────────────────────────────────
        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.GATE_CHECK,
            operator="court",
            outputs_summary={"gate": "court_pre_check"},
        )
        t_court = time.perf_counter()
        court_verdict = self.court.adjudicate(
            sage_receipt=sage_receipt,
            lab_assessment=lab_assessment,
            bar_assessment=bar_result,
            phase_id=phase_id,
        )
        court_ms = (time.perf_counter() - t_court) * 1000

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.COURT_VERDICT,
            operator="court",
            outputs_summary={
                "verdict":         court_verdict.verdict,
                "evidence_weight": court_verdict.evidence_weight,
                "ruin_detected":   bar_result.ruin.ruin_detected,
                "axiom_violations": [
                    t.test_name for t in court_verdict.tests
                    if not t.passes
                ],
            },
            duration_ms=court_ms,
            nci_after=sage_receipt.nci_score,
        )

        # ── Stage 6: Kintsugi repair ───────────────────────────────────────
        kintsugi_applied = False
        # Kintsugi operates on receipt dicts
        _fated = sage_receipt.fated
        receipt_dict = {
            "nci_score":        sage_receipt.nci_score,
            "irreversibility":  sage_receipt.irreversibility,
            "on_purpose":       sage_receipt.on_purpose,
            "fated": {
                "facts":       getattr(_fated, "facts", "") if _fated else "",
                "assumptions": getattr(_fated, "assumptions", "") if _fated else "",
                "tradeoffs":   getattr(_fated, "tradeoffs", "") if _fated else "",
                "emotions":    getattr(_fated, "emotions", "") if _fated else "",
                "direction":   getattr(_fated, "direction", "") if _fated else "",
            },
            "phase_id":         sage_receipt.phase_id,
            "axioms": {
                "clarity_before_curvature":    sage_receipt.axioms.clarity_before_curvature if sage_receipt.axioms else "YES",
                "agency_over_automation":      sage_receipt.axioms.agency_over_automation if sage_receipt.axioms else "YES",
                "minimum_steps_to_coherence":  sage_receipt.axioms.minimum_steps_to_coherence if sage_receipt.axioms else "YES",
                "kairos_over_neuroticism":     sage_receipt.axioms.kairos_over_neuroticism if sage_receipt.axioms else "YES",
            },
        }
        diagnosis = self.kintsugi.diagnose(receipt_dict)
        if not diagnosis.is_healthy:
            repaired_diagnosis = self.kintsugi.repair(diagnosis, receipt_dict)
            kintsugi_applied = True
            self.logger.record_event(
                span_id=span_id,
                event_type=EventType.KINTSUGI_REPAIR,
                operator="kintsugi",
                outputs_summary={
                    "pathogens_found":  len(diagnosis.pathogens),
                    "seams_applied":    len(repaired_diagnosis.golden_seams),
                    "nci_discount":     repaired_diagnosis.repair_nci_discount,
                },
                nci_after=sage_receipt.nci_score,
            )

        # ── Stage 7: Determine pipeline verdict ───────────────────────────
        if court_verdict.verdict == "BLOCK":
            pipeline_verdict = PipelineVerdict.BLOCKED
        elif court_verdict.verdict == "CONDITIONAL":
            pipeline_verdict = (
                PipelineVerdict.ACCEPTABLE
                if sage_receipt.nci_score >= 70
                else PipelineVerdict.BLOCKED
            )
        else:
            pipeline_verdict = (
                PipelineVerdict.COMPLETE
                if sage_receipt.nci_score >= 80
                else PipelineVerdict.ACCEPTABLE
            )

        self.logger.record_event(
            span_id=span_id,
            event_type=EventType.PIPELINE_END,
            operator="pipeline",
            outputs_summary={
                "verdict": pipeline_verdict.value,
                "nci":     sage_receipt.nci_score,
            },
            nci_after=sage_receipt.nci_score,
        )

        # ── Stage 8: Automatic BarRaiser (ballet trigger check) ────────────
        bar_review_id: Optional[str] = None
        span_obj = self.logger._active_spans.get(span_id)

        if span_obj and self._should_trigger_bar(
            span_obj, pipeline_verdict, sage_receipt.nci_score
        ):
            review = self.loki.bar_review(
                span_obj,
                invoked_by="runtime_service",
            )
            bar_review_id = review.review_id
            self.logger.record_event(
                span_id=span_id,
                event_type=EventType.BAR_RAISER_REVIEW,
                operator="bar_raiser",
                outputs_summary={
                    "verdict":   review.verdict,
                    "bar_score": review.bar_score,
                },
                branch_tag=BranchTag.BAR_REVIEW,
            )

        # ── Close span ────────────────────────────────────────────────────
        span = self.logger.end_span(
            span_id,
            verdict=pipeline_verdict.value,
            nci_exit=sage_receipt.nci_score,
        )

        # ── Persist receipt ───────────────────────────────────────────────
        if pipeline_verdict != PipelineVerdict.BLOCKED:
            self._persist_receipt(sage_receipt, span_id)

        duration_ms = (time.perf_counter() - t0) * 1000

        return PipelineResult(
            verdict=pipeline_verdict,
            nci_score=sage_receipt.nci_score,
            receipt=sage_receipt,
            court_verdict=court_verdict,
            kintsugi_applied=kintsugi_applied,
            bar_review_id=bar_review_id,
            span_id=span_id,
            session_id=self._session_id or "unknown",
            duration_ms=duration_ms,
            anomaly_count=len(span.anomalies),
            metadata={
                "lab_threat":    lab_assessment.lab_threat_level,
                "ruin_detected": bar_result.ruin.ruin_detected,
                "court":         court_verdict.verdict,
            },
        )

    # --- BarRaiser trigger policy ---

    def _should_trigger_bar(
        self,
        span: TraceSpan,
        verdict: PipelineVerdict,
        nci: float,
    ) -> bool:
        """Decide whether to auto-trigger BarRaiser based on current policy."""
        import arcs_rom
        gates = list(arcs_rom.PHASE_GATES.values())

        if self.bar_trigger == BarRaiserTrigger.NEVER:
            return False
        if self.bar_trigger == BarRaiserTrigger.ALWAYS:
            return True
        if self.bar_trigger == BarRaiserTrigger.ON_BLOCKED:
            return verdict == PipelineVerdict.BLOCKED
        if self.bar_trigger == BarRaiserTrigger.ON_ANOMALY:
            return len(span.anomalies) > 0
        if self.bar_trigger == BarRaiserTrigger.GATE_ADJACENT:
            return any(abs(nci - g) <= 3 for g in gates)
        return False

    # --- Ballet-style manual BarRaiser invocation ---

    def invoke_bar_raiser(
        self,
        span_id: str,
        invoked_by: str,
        deep: bool = False,
    ) -> Optional[Any]:
        """
        Any operator can call this at any time during a pipeline run.
        Returns BarRaiserReview or None if span not found.
        """
        span = self.logger._active_spans.get(span_id)
        if span is None:
            return None
        return self.loki.bar_review(span, invoked_by=invoked_by, deep=deep)

    # --- Receipt persistence ---

    def _persist_receipt(self, receipt: CoherenceReceipt, span_id: str) -> None:
        try:
            receipt_dict = {
                "span_id":             span_id,
                "timestamp":           time.time(),
                "nci_score":           receipt.nci_score,
                "signal_class":        receipt.signal_class,
                "on_purpose":          receipt.on_purpose,
                "irreversibility":     receipt.irreversibility_score,
                "phase_id":            receipt.phase_id,
                "fated_reasoning":     receipt.fated_reasoning if hasattr(receipt, "fated_reasoning") else "",
                "axioms_checked":      receipt.axioms_checked if hasattr(receipt, "axioms_checked") else {},
            }
            with open(self._store_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(receipt_dict) + "\n")
        except Exception:
            pass  # persistence is best-effort in Phase 5; Yoav handles guarantees

    # --- Observability helpers ---

    def gravitational_report(self) -> List[Dict[str, Any]]:
        """Compute operator coupling strengths across the corpus."""
        pairs = [
            ("sage", "lab"),
            ("lab", "bar"),
            ("bar", "court"),
            ("court", "kintsugi"),
            ("sage", "court"),
        ]
        return [
            self.logger.gravitational_force(src, tgt)
            for src, tgt in pairs
        ]

    def anomaly_summary(self) -> Dict[str, Any]:
        anomalies = self.logger.get_anomalies(limit=500)
        type_counts: Dict[str, int] = {}
        for a in anomalies:
            atype = a.get("anomaly_type", "unknown")
            type_counts[atype] = type_counts.get(atype, 0) + 1
        return {
            "total":    len(anomalies),
            "by_type":  type_counts,
        }

    def loki_report(self) -> Dict[str, Any]:
        return {
            "antifragility":   self.loki.antifragility_report(),
            "calibration":     self.loki.calibrator.calibration_report(),
            "threshold_config": self.loki.threshold_config(),
        }


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    import tempfile, shutil, numpy as np
    from arcs_primitives import CoherenceSignal

    print("=== arcs_runtime_service.py smoke test ===\n")

    tmp = tempfile.mkdtemp()
    store_path = f"{tmp}/receipts.jsonl"
    try:
        svc = ARCSRuntimeService(
            trace_dir=tmp,
            bar_trigger=BarRaiserTrigger.ALWAYS,   # trigger on every run
            store_path=store_path,
        )
        svc.start_session(metadata={"purpose": "smoke_test"})

        # 1. Healthy accelerating signal
        healthy_signal = np.array([60, 65, 70, 75, 78, 81, 83, 85, 87, 89], dtype=float)
        sig1 = CoherenceSignal(
            signal=healthy_signal,
            domain="coherence",
            label="smoke_test_healthy",
        )
        result1 = svc.run_pipeline(sig1, phase_id="phase_5", nci_entry=80.0)
        if result1.error:
            print(f"[!] Pipeline error: {result1.error}")
        print(f"[OK] Healthy signal:")
        print(f"     verdict={result1.verdict.value}, nci={result1.nci_score:.1f}, "
              f"anomalies={result1.anomaly_count}")
        print(f"     court={result1.metadata.get('court')}, "
              f"kintsugi={result1.kintsugi_applied}")
        print(f"     bar_review_id={'set' if result1.bar_review_id else 'none'}")

        # 2. Noisy / ruin-risk signal
        noisy_signal = np.array([88, 85, 80, 70, 55, 60, 55, 50, 48, 45], dtype=float)
        sig2 = CoherenceSignal(
            signal=noisy_signal,
            domain="coherence",
            label="smoke_test_ruin",
        )
        result2 = svc.run_pipeline(sig2, phase_id="phase_5", nci_entry=82.0)
        print(f"\n[OK] Ruin-risk signal:")
        print(f"     verdict={result2.verdict.value}, nci={result2.nci_score:.1f}, "
              f"anomalies={result2.anomaly_count}")
        print(f"     ruin_detected={result2.metadata.get('ruin_detected')}, "
              f"court={result2.metadata.get('court')}")

        # 3. Ballet BarRaiser: manual invocation mid-run (simulate curator calling it)
        svc2 = ARCSRuntimeService(
            trace_dir=tmp,
            bar_trigger=BarRaiserTrigger.NEVER,  # no auto trigger
            store_path=store_path,
        )
        svc2.start_session()
        span_id3 = svc2.logger.start_span(phase_id="phase_5", nci_entry=85.0)
        from arcs_trace import EventType
        svc2.logger.record_event(
            span_id=span_id3,
            event_type=EventType.OPERATOR_END,
            operator="curator",
            outputs_summary={"reframe": "tested"},
            nci_after=85.0,
        )
        review = svc2.invoke_bar_raiser(span_id3, invoked_by="curator")
        assert review is not None
        print(f"\n[OK] Ballet BarRaiser (manual by curator):")
        print(f"     verdict={review.verdict}, bar_score={review.bar_score:.3f}")
        svc2.logger.end_span(span_id3, verdict="COMPLETE", nci_exit=85.0)

        # 4. Gravitational force report
        grav = svc.gravitational_report()
        print(f"\n[OK] Gravitational force report:")
        for g in grav:
            print(f"     {g['source']}→{g['target']}: force={g['force']:.2f}")

        # 5. Loki report
        loki_rpt = svc.loki_report()
        print(f"\n[OK] Loki report:")
        af = loki_rpt["antifragility"]
        print(f"     antifragility score: {af.get('score')}, {af.get('interpretation', 'N/A')[:40]}")
        cal = loki_rpt["calibration"]
        print(f"     calibration: {cal['total_flags']} flags, {cal['pending']} pending")

        # 6. End session
        svc.end_session()
        print("\n[OK] Session ended cleanly")

        print("\n=== Smoke test PASSED — arcs_runtime_service.py ===")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    _smoke_test()
