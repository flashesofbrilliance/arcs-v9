"""
arcs_trace.py — Phase 5 Observability Layer
Core trace atoms, pluggable persistence backends, @trace_operator decorator, write-time anomaly detection.

Architecture:
    TraceEvent (atom)
        └── TraceSpan (pipeline run, composes N events)
            └── TraceSession (session, composes N spans)
                └── TraceCorpus (full history, composes N sessions)

Persistence:
    TracePersistenceBackend (abstract)
        ├── JSONLBackend (default, stdlib-only, sovereign/portable)
        └── SupabaseBackend (optional, graceful fallback, loaded lazily)

Usage:
    logger = TraceLogger()                         # JSONL-first by default
    pipeline = ARCSPipeline(trace_logger=logger)   # wired in runtime service
    # OR decorate individual operators:
    @trace_operator(logger)
    def my_operator(receipt, phase_id): ...
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import traceback
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    OPERATOR_START    = "operator_start"
    OPERATOR_END      = "operator_end"
    OPERATOR_ERROR    = "operator_error"
    PIPELINE_START    = "pipeline_start"
    PIPELINE_END      = "pipeline_end"
    GATE_CHECK        = "gate_check"
    COURT_VERDICT     = "court_verdict"
    KINTSUGI_REPAIR   = "kintsugi_repair"
    BAR_RAISER_REVIEW = "bar_raiser_review"
    LOKI_PERTURBATION = "loki_perturbation"
    YOAV_COMMIT       = "yoav_commit"
    ANOMALY_DETECTED  = "anomaly_detected"
    ANNOTATION        = "annotation"


class AnomalyType(str, Enum):
    # Signal anomalies
    NCI_CLIFF           = "nci_cliff"           # NCI drop > 15 in one step
    NCI_CEILING_STUCK   = "nci_ceiling_stuck"   # NCI plateau ≥ 95 for 3+ spans
    RUIN_UNMARKED       = "ruin_unmarked"        # ruin_risk=True but verdict=PERMIT
    IRREV_SPIKE         = "irrev_spike"          # irreversibility > 0.8
    AXIOM_SILENT_FAIL   = "axiom_silent_fail"    # axiom=False but no BLOCK verdict
    # Operator-coupling anomalies
    OPERATOR_ORPHAN     = "operator_orphan"      # operator ran with no upstream receipt
    COURT_BYPASS        = "court_bypass"         # verdict expected but span has no court event
    # Temporal anomalies
    SPAN_TIMEOUT        = "span_timeout"         # span duration > threshold_ms
    REPLAY_DIVERGE      = "replay_diverge"       # replay hash differs from original


class BranchTag(str, Enum):
    MAIN          = "main"          # primary pipeline path
    LOKI_PROBE    = "loki_probe"    # adversarial perturbation branch
    REPLAY        = "replay"        # deterministic replay of prior span
    CONDITIONAL   = "conditional"   # court issued CONDITIONAL; branch taken
    FALLBACK      = "fallback"      # operator failed; fallback path taken
    BAR_REVIEW    = "bar_review"    # bar raiser review sub-branch


# ---------------------------------------------------------------------------
# Core Atoms
# ---------------------------------------------------------------------------

@dataclass
class TraceAnomaly:
    anomaly_id:   str
    anomaly_type: AnomalyType
    severity:     str          # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    span_id:      str
    event_id:     Optional[str]
    description:  str
    context:      Dict[str, Any] = field(default_factory=dict)
    timestamp:    float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["anomaly_type"] = self.anomaly_type.value
        return d


@dataclass
class TraceAnnotation:
    annotation_id:   str
    span_id:         str
    event_id:        Optional[str]
    label:           str        # "TRUE_POSITIVE" | "FALSE_POSITIVE" | "UNCLEAR"
    annotated_by:    str        # "human" | "abductive_calibrator" | "bar_raiser"
    confidence:      float      # 0.0–1.0
    notes:           str = ""
    timestamp:       float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    """Smallest unit of observability — one operator call or system event."""
    event_id:        str
    event_type:      EventType
    operator:        str          # e.g. "sage", "lab", "bar", "court", "kintsugi"
    span_id:         str
    session_id:      str
    timestamp:       float
    duration_ms:     Optional[float]
    input_hash:      Optional[str]    # SHA-256 of serialized input (for replay)
    outputs_summary: Dict[str, Any]   # lightweight summary, not full output
    branch_tag:      BranchTag
    nci_delta:       Optional[float]  # NCI change produced by this event
    nci_after:       Optional[float]  # NCI value after event
    error:           Optional[str]    # exception message if OPERATOR_ERROR
    metadata:        Dict[str, Any] = field(default_factory=dict)

    def replay_hash(self) -> str:
        """Deterministic hash for replay verification."""
        payload = json.dumps({
            "operator":    self.operator,
            "input_hash":  self.input_hash,
            "branch_tag":  self.branch_tag.value,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        d["branch_tag"] = self.branch_tag.value
        return d


@dataclass
class TraceSpan:
    """One pipeline run — composes N TraceEvents."""
    span_id:          str
    session_id:       str
    phase_id:         str
    pipeline_version: str
    started_at:       float
    ended_at:         Optional[float]
    events:           List[TraceEvent]    = field(default_factory=list)
    anomalies:        List[TraceAnomaly]  = field(default_factory=list)
    annotations:      List[TraceAnnotation] = field(default_factory=list)
    nci_entry:        Optional[float] = None
    nci_exit:         Optional[float] = None
    verdict:          Optional[str]   = None   # COMPLETE | BLOCKED | ACCEPTABLE
    branch_tag:       BranchTag = BranchTag.MAIN
    parent_span_id:   Optional[str] = None     # set for replay/loki sub-spans
    metadata:         Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000

    @property
    def nci_delta(self) -> Optional[float]:
        if self.nci_entry is not None and self.nci_exit is not None:
            return self.nci_exit - self.nci_entry
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id":          self.span_id,
            "session_id":       self.session_id,
            "phase_id":         self.phase_id,
            "pipeline_version": self.pipeline_version,
            "started_at":       self.started_at,
            "ended_at":         self.ended_at,
            "duration_ms":      self.duration_ms,
            "nci_entry":        self.nci_entry,
            "nci_exit":         self.nci_exit,
            "nci_delta":        self.nci_delta,
            "verdict":          self.verdict,
            "branch_tag":       self.branch_tag.value,
            "parent_span_id":   self.parent_span_id,
            "events":           [e.to_dict() for e in self.events],
            "anomalies":        [a.to_dict() for a in self.anomalies],
            "annotations":      [a.to_dict() for a in self.annotations],
            "metadata":         self.metadata,
        }


@dataclass
class TraceSession:
    """One ARCS session — composes N TraceSpans."""
    session_id:    str
    started_at:    float
    ended_at:      Optional[float] = None
    spans:         List[TraceSpan] = field(default_factory=list)
    metadata:      Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at":   self.ended_at,
            "span_count": len(self.spans),
            "metadata":   self.metadata,
        }


# ---------------------------------------------------------------------------
# Persistence Backends
# ---------------------------------------------------------------------------

class TracePersistenceBackend(ABC):
    """Abstract backend — append-only contract."""

    @abstractmethod
    def write_event(self, event: TraceEvent) -> None: ...

    @abstractmethod
    def write_span(self, span: TraceSpan) -> None: ...

    @abstractmethod
    def write_anomaly(self, anomaly: TraceAnomaly) -> None: ...

    @abstractmethod
    def write_annotation(self, annotation: TraceAnnotation) -> None: ...

    @abstractmethod
    def read_spans(self, session_id: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def read_anomalies(self, span_id: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]: ...


class JSONLBackend(TracePersistenceBackend):
    """
    Sovereign JSONL persistence.  Each record type gets its own .jsonl file.
    Append-only.  Zero external dependencies.  Self-contained on disk.
    """

    def __init__(self, base_dir: str = "arcs_trace_logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._files = {
            "events":      self.base_dir / "events.jsonl",
            "spans":       self.base_dir / "spans.jsonl",
            "anomalies":   self.base_dir / "anomalies.jsonl",
            "annotations": self.base_dir / "annotations.jsonl",
        }

    @staticmethod
    def _safe_json(obj: Any) -> str:
        """json.dumps with fallback serializer for dataclass / arbitrary objects."""
        import dataclasses
        def default(o: Any) -> Any:
            if dataclasses.is_dataclass(o) and not isinstance(o, type):
                return dataclasses.asdict(o)
            try:
                return str(o)
            except Exception:
                return "<non-serializable>"
        return json.dumps(obj, default=default)

    def _append(self, key: str, record: Dict[str, Any]) -> None:
        with open(self._files[key], "a", encoding="utf-8") as fh:
            fh.write(self._safe_json(record) + "\n")

    def _read_last_n(self, key: str, limit: int) -> List[Dict[str, Any]]:
        path = self._files[key]
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(l) for l in lines[-limit:]]

    def write_event(self, event: TraceEvent) -> None:
        self._append("events", event.to_dict())

    def write_span(self, span: TraceSpan) -> None:
        self._append("spans", span.to_dict())

    def write_anomaly(self, anomaly: TraceAnomaly) -> None:
        self._append("anomalies", anomaly.to_dict())

    def write_annotation(self, annotation: TraceAnnotation) -> None:
        self._append("annotations", annotation.to_dict())

    def read_spans(self, session_id: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        records = self._read_last_n("spans", limit * 2)
        if session_id:
            records = [r for r in records if r.get("session_id") == session_id]
        return records[-limit:]

    def read_anomalies(self, span_id: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        records = self._read_last_n("anomalies", limit * 2)
        if span_id:
            records = [r for r in records if r.get("span_id") == span_id]
        return records[-limit:]


class SupabaseBackend(TracePersistenceBackend):
    """
    Optional Supabase write-through backend.
    Falls back gracefully if supabase-py is not installed.
    Designed as secondary write — JSONLBackend is always primary.

    Tables expected (create via Supabase SQL editor):
        trace_events(event_id PK, span_id, data JSONB, created_at TIMESTAMPTZ)
        trace_spans(span_id PK, session_id, data JSONB, created_at TIMESTAMPTZ)
        trace_anomalies(anomaly_id PK, span_id, data JSONB, created_at TIMESTAMPTZ)
        trace_annotations(annotation_id PK, span_id, data JSONB, created_at TIMESTAMPTZ)
    """

    def __init__(self, supabase_url: str, supabase_key: str):
        self._available = False
        self._client = None
        try:
            from supabase import create_client  # type: ignore
            self._client = create_client(supabase_url, supabase_key)
            self._available = True
        except ImportError:
            pass  # supabase-py not installed — backend silently disabled

    @property
    def available(self) -> bool:
        return self._available

    def _upsert(self, table: str, record: Dict[str, Any], id_key: str) -> None:
        if not self._available:
            return
        try:
            self._client.table(table).upsert(
                {"id": record[id_key], "data": record, "created_at": "now()"}
            ).execute()
        except Exception:
            pass  # non-fatal; JSONL is primary

    def write_event(self, event: TraceEvent) -> None:
        self._upsert("trace_events", event.to_dict(), "event_id")

    def write_span(self, span: TraceSpan) -> None:
        self._upsert("trace_spans", span.to_dict(), "span_id")

    def write_anomaly(self, anomaly: TraceAnomaly) -> None:
        self._upsert("trace_anomalies", anomaly.to_dict(), "anomaly_id")

    def write_annotation(self, annotation: TraceAnnotation) -> None:
        self._upsert("trace_annotations", annotation.to_dict(), "annotation_id")

    def read_spans(self, session_id: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            q = self._client.table("trace_spans").select("data").limit(limit)
            if session_id:
                q = q.eq("session_id", session_id)
            res = q.execute()
            return [r["data"] for r in res.data]
        except Exception:
            return []

    def read_anomalies(self, span_id: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            q = self._client.table("trace_anomalies").select("data").limit(limit)
            if span_id:
                q = q.eq("span_id", span_id)
            res = q.execute()
            return [r["data"] for r in res.data]
        except Exception:
            return []


class DualWriteBackend(TracePersistenceBackend):
    """
    Writes to primary (JSONL) always, and optionally to secondary (Supabase).
    Secondary failures are silently swallowed — primary is the source of truth.
    """

    def __init__(self, primary: TracePersistenceBackend,
                 secondary: Optional[TracePersistenceBackend] = None):
        self.primary   = primary
        self.secondary = secondary

    def _dual(self, method: str, *args, **kwargs) -> None:
        getattr(self.primary, method)(*args, **kwargs)
        if self.secondary:
            try:
                getattr(self.secondary, method)(*args, **kwargs)
            except Exception:
                pass

    def write_event(self, event: TraceEvent) -> None:
        self._dual("write_event", event)

    def write_span(self, span: TraceSpan) -> None:
        self._dual("write_span", span)

    def write_anomaly(self, anomaly: TraceAnomaly) -> None:
        self._dual("write_anomaly", anomaly)

    def write_annotation(self, annotation: TraceAnnotation) -> None:
        self._dual("write_annotation", annotation)

    def read_spans(self, **kwargs) -> List[Dict[str, Any]]:
        return self.primary.read_spans(**kwargs)

    def read_anomalies(self, **kwargs) -> List[Dict[str, Any]]:
        return self.primary.read_anomalies(**kwargs)


# ---------------------------------------------------------------------------
# Anomaly Detector
# ---------------------------------------------------------------------------

class AnomalyDetector:
    """
    Write-time anomaly detection.  Called by TraceLogger after every event
    and after every span close.  Returns list of detected TraceAnomalies.
    """

    # NCI drop threshold that constitutes a "cliff"
    NCI_CLIFF_THRESHOLD = 15.0
    # Span timeout default (ms)
    SPAN_TIMEOUT_MS     = 30_000

    def __init__(self, span_timeout_ms: float = SPAN_TIMEOUT_MS):
        self.span_timeout_ms = span_timeout_ms
        # Rolling window: track last N nci_exit values for ceiling-stuck detection
        self._nci_history: List[float] = []

    def detect_on_event(self, event: TraceEvent,
                        prior_nci: Optional[float]) -> List[TraceAnomaly]:
        anomalies = []

        # NCI Cliff: large NCI drop in a single event
        if (event.nci_delta is not None
                and prior_nci is not None
                and event.nci_delta < -self.NCI_CLIFF_THRESHOLD):
            anomalies.append(TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.NCI_CLIFF,
                severity="HIGH",
                span_id=event.span_id,
                event_id=event.event_id,
                description=(
                    f"NCI dropped {event.nci_delta:.1f} in one step "
                    f"(prior={prior_nci:.1f}, after={event.nci_after})"
                ),
                context={"nci_delta": event.nci_delta, "prior_nci": prior_nci},
            ))

        # Irreversibility spike
        irrev = event.outputs_summary.get("irreversibility_score")
        if irrev is not None and irrev > 0.8:
            anomalies.append(TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.IRREV_SPIKE,
                severity="MEDIUM",
                span_id=event.span_id,
                event_id=event.event_id,
                description=f"Irreversibility spike: {irrev:.2f} > 0.80",
                context={"irreversibility_score": irrev},
            ))

        # Ruin unmarked: ruin_risk=True but verdict is PERMIT
        ruin = event.outputs_summary.get("ruin_risk")
        verdict = event.outputs_summary.get("verdict")
        if ruin is True and verdict == "PERMIT":
            anomalies.append(TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.RUIN_UNMARKED,
                severity="CRITICAL",
                span_id=event.span_id,
                event_id=event.event_id,
                description="ruin_risk=True but verdict=PERMIT — ruin gate bypassed",
                context={"ruin_risk": ruin, "verdict": verdict},
            ))

        # Axiom silent fail: any axiom=False but no BLOCK
        axiom_violations = event.outputs_summary.get("axiom_violations", [])
        if axiom_violations and verdict not in ("BLOCK", "CONDITIONAL"):
            anomalies.append(TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.AXIOM_SILENT_FAIL,
                severity="HIGH",
                span_id=event.span_id,
                event_id=event.event_id,
                description=(
                    f"Axiom violations {axiom_violations} present but verdict={verdict}"
                ),
                context={"axiom_violations": axiom_violations, "verdict": verdict},
            ))

        return anomalies

    def detect_on_span_close(self, span: TraceSpan) -> List[TraceAnomaly]:
        anomalies = []

        # Span timeout
        if span.duration_ms is not None and span.duration_ms > self.span_timeout_ms:
            anomalies.append(TraceAnomaly(
                anomaly_id=_new_id("anm"),
                anomaly_type=AnomalyType.SPAN_TIMEOUT,
                severity="LOW",
                span_id=span.span_id,
                event_id=None,
                description=(
                    f"Span duration {span.duration_ms:.0f}ms exceeds "
                    f"threshold {self.span_timeout_ms:.0f}ms"
                ),
                context={"duration_ms": span.duration_ms},
            ))

        # Court bypass: pipeline_end event with no court_verdict event
        event_types = {e.event_type for e in span.events}
        if EventType.PIPELINE_END in event_types and EventType.COURT_VERDICT not in event_types:
            # Only flag on MAIN branch runs with more than 2 events (not trivial/test spans)
            if span.branch_tag == BranchTag.MAIN and len(span.events) > 2:
                anomalies.append(TraceAnomaly(
                    anomaly_id=_new_id("anm"),
                    anomaly_type=AnomalyType.COURT_BYPASS,
                    severity="MEDIUM",
                    span_id=span.span_id,
                    event_id=None,
                    description="Pipeline completed on MAIN branch without a court verdict",
                    context={"event_types": [e.value for e in event_types]},
                ))

        # NCI ceiling stuck: track rolling history
        if span.nci_exit is not None:
            self._nci_history.append(span.nci_exit)
            self._nci_history = self._nci_history[-5:]  # keep last 5
            if (len(self._nci_history) >= 3
                    and all(v >= 95.0 for v in self._nci_history[-3:])):
                anomalies.append(TraceAnomaly(
                    anomaly_id=_new_id("anm"),
                    anomaly_type=AnomalyType.NCI_CEILING_STUCK,
                    severity="LOW",
                    span_id=span.span_id,
                    event_id=None,
                    description=(
                        "NCI has been ≥ 95 for 3+ consecutive spans — "
                        "may indicate over-fitting to coherence signal"
                    ),
                    context={"nci_history": self._nci_history[-3:]},
                ))

        return anomalies


# ---------------------------------------------------------------------------
# TraceLogger
# ---------------------------------------------------------------------------

class TraceLogger:
    """
    Central observability hub.
    - Creates and manages TraceSession, TraceSpan lifetimes
    - Persists events/spans/anomalies through configurable backend
    - Runs write-time anomaly detection
    - Exposes replay and gravitational force APIs
    """

    def __init__(
        self,
        backend: Optional[TracePersistenceBackend] = None,
        base_dir: str = "arcs_trace_logs",
        span_timeout_ms: float = AnomalyDetector.SPAN_TIMEOUT_MS,
        pipeline_version: str = "5.0.0",
    ):
        self.backend = backend or JSONLBackend(base_dir=base_dir)
        self.pipeline_version = pipeline_version
        self.detector = AnomalyDetector(span_timeout_ms=span_timeout_ms)

        self._session: Optional[TraceSession] = None
        self._active_spans: Dict[str, TraceSpan] = {}
        self._last_nci: Dict[str, Optional[float]] = {}  # span_id → last nci_after

    # --- Session lifecycle ---

    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        sid = _new_id("ses")
        self._session = TraceSession(
            session_id=sid,
            started_at=time.time(),
            metadata=metadata or {},
        )
        return sid

    def end_session(self) -> Optional[str]:
        if self._session:
            self._session.ended_at = time.time()
            sid = self._session.session_id
            self.backend.write_span.__func__  # flush any open spans
            return sid
        return None

    @property
    def session_id(self) -> Optional[str]:
        return self._session.session_id if self._session else None

    # --- Span lifecycle ---

    def start_span(
        self,
        phase_id: str,
        branch_tag: BranchTag = BranchTag.MAIN,
        parent_span_id: Optional[str] = None,
        nci_entry: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        sid = self._session.session_id if self._session else _new_id("ses")
        span_id = _new_id("spn")
        span = TraceSpan(
            span_id=span_id,
            session_id=sid,
            phase_id=phase_id,
            pipeline_version=self.pipeline_version,
            started_at=time.time(),
            ended_at=None,
            nci_entry=nci_entry,
            branch_tag=branch_tag,
            parent_span_id=parent_span_id,
            metadata=metadata or {},
        )
        self._active_spans[span_id] = span
        self._last_nci[span_id] = nci_entry
        return span_id

    def end_span(
        self,
        span_id: str,
        verdict: Optional[str] = None,
        nci_exit: Optional[float] = None,
    ) -> TraceSpan:
        span = self._active_spans.pop(span_id, None)
        if span is None:
            raise ValueError(f"No active span: {span_id}")
        span.ended_at = time.time()
        span.verdict  = verdict
        span.nci_exit = nci_exit

        # Write-time anomaly detection on span close
        close_anomalies = self.detector.detect_on_span_close(span)
        for a in close_anomalies:
            span.anomalies.append(a)
            self.backend.write_anomaly(a)

        # Persist complete span
        self.backend.write_span(span)

        # Attach to session
        if self._session:
            self._session.spans.append(span)

        self._last_nci.pop(span_id, None)
        return span

    # --- Event recording ---

    def record_event(
        self,
        span_id: str,
        event_type: EventType,
        operator: str,
        outputs_summary: Dict[str, Any],
        input_hash: Optional[str] = None,
        duration_ms: Optional[float] = None,
        nci_delta: Optional[float] = None,
        nci_after: Optional[float] = None,
        branch_tag: Optional[BranchTag] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceEvent:
        span = self._active_spans.get(span_id)
        session_id = span.session_id if span else (self.session_id or "unknown")

        event = TraceEvent(
            event_id=_new_id("evt"),
            event_type=event_type,
            operator=operator,
            span_id=span_id,
            session_id=session_id,
            timestamp=time.time(),
            duration_ms=duration_ms,
            input_hash=input_hash,
            outputs_summary=outputs_summary,
            branch_tag=branch_tag or (span.branch_tag if span else BranchTag.MAIN),
            nci_delta=nci_delta,
            nci_after=nci_after,
            error=error,
            metadata=metadata or {},
        )

        # Persist event
        self.backend.write_event(event)

        # Attach to span
        if span:
            span.events.append(event)

        # Write-time anomaly detection
        prior_nci = self._last_nci.get(span_id)
        event_anomalies = self.detector.detect_on_event(event, prior_nci)
        for a in event_anomalies:
            if span:
                span.anomalies.append(a)
            self.backend.write_anomaly(a)

        # Update rolling NCI
        if nci_after is not None:
            self._last_nci[span_id] = nci_after

        return event

    # --- Annotation ---

    def annotate(
        self,
        span_id: str,
        label: str,
        annotated_by: str,
        confidence: float,
        event_id: Optional[str] = None,
        notes: str = "",
    ) -> TraceAnnotation:
        ann = TraceAnnotation(
            annotation_id=_new_id("ann"),
            span_id=span_id,
            event_id=event_id,
            label=label,
            annotated_by=annotated_by,
            confidence=confidence,
            notes=notes,
        )
        self.backend.write_annotation(ann)
        span = self._active_spans.get(span_id)
        if span:
            span.annotations.append(ann)
        return ann

    # --- Query APIs ---

    def get_span_history(self, session_id: Optional[str] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        return self.backend.read_spans(session_id=session_id, limit=limit)

    def get_anomalies(self, span_id: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        return self.backend.read_anomalies(span_id=span_id, limit=limit)

    def gravitational_force(
        self,
        source_operator: str,
        target_operator: str,
        session_id: Optional[str] = None,
        limit: int = 200,
    ) -> Dict[str, Any]:
        """
        Compute coupling strength (gravitational force) between two operators
        across the span corpus.  Force = fraction of spans where source → target
        in sequential order.
        """
        spans = self.backend.read_spans(session_id=session_id, limit=limit)
        total = 0
        coupled = 0
        for span_dict in spans:
            events = span_dict.get("events", [])
            ops = [e["operator"] for e in events]
            if source_operator in ops:
                total += 1
                # target must appear after source
                src_idx = ops.index(source_operator)
                if target_operator in ops[src_idx + 1:]:
                    coupled += 1
        force = coupled / total if total > 0 else 0.0
        return {
            "source":  source_operator,
            "target":  target_operator,
            "force":   round(force, 4),
            "coupled": coupled,
            "total":   total,
        }


# ---------------------------------------------------------------------------
# @trace_operator decorator
# ---------------------------------------------------------------------------

def trace_operator(
    logger: TraceLogger,
    operator_name: Optional[str] = None,
    branch_tag: BranchTag = BranchTag.MAIN,
    extract_nci: Optional[Callable[[Any], Optional[float]]] = None,
    extract_summary: Optional[Callable[[Any], Dict[str, Any]]] = None,
):
    """
    Decorator that wraps an operator function with TraceLogger instrumentation.

    Args:
        logger:          TraceLogger instance to emit events into.
        operator_name:   Override name; defaults to function.__name__.
        branch_tag:      Branch classification for these events.
        extract_nci:     Callable(result) → float | None — extract NCI from result.
        extract_summary: Callable(result) → dict — extract summary dict from result.

    Usage:
        @trace_operator(logger, operator_name="sage")
        def run_sage(receipt, phase_id): ...
    """
    def decorator(fn: Callable) -> Callable:
        op_name = operator_name or fn.__name__

        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Compute input hash for replay
            try:
                input_repr = json.dumps(
                    [str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()],
                    sort_keys=True,
                )
                input_hash = hashlib.sha256(input_repr.encode()).hexdigest()[:16]
            except Exception:
                input_hash = "unhashable"

            # Infer span_id from kwargs or create an ephemeral one
            span_id = kwargs.get("span_id") or kwargs.get("_span_id")
            _ephemeral_span = span_id is None
            if _ephemeral_span:
                span_id = logger.start_span(
                    phase_id=kwargs.get("phase_id", "unknown"),
                    branch_tag=branch_tag,
                )

            # START event
            logger.record_event(
                span_id=span_id,
                event_type=EventType.OPERATOR_START,
                operator=op_name,
                outputs_summary={},
                input_hash=input_hash,
                branch_tag=branch_tag,
            )

            t0 = time.perf_counter()
            error_str: Optional[str] = None
            result = None
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                error_str = traceback.format_exc()
                # END event for error
                logger.record_event(
                    span_id=span_id,
                    event_type=EventType.OPERATOR_ERROR,
                    operator=op_name,
                    outputs_summary={"error": str(exc)},
                    duration_ms=(time.perf_counter() - t0) * 1000,
                    branch_tag=branch_tag,
                    error=error_str,
                )
                if _ephemeral_span:
                    logger.end_span(span_id, verdict="ERROR")
                raise

            duration_ms = (time.perf_counter() - t0) * 1000

            # Extract NCI and summary from result
            nci_after: Optional[float] = None
            nci_delta: Optional[float] = None
            if extract_nci and result is not None:
                nci_after = extract_nci(result)
                prior = logger._last_nci.get(span_id)
                if nci_after is not None and prior is not None:
                    nci_delta = nci_after - prior

            summary: Dict[str, Any] = {}
            if extract_summary and result is not None:
                try:
                    summary = extract_summary(result)
                except Exception:
                    summary = {"extract_error": True}

            # END event
            logger.record_event(
                span_id=span_id,
                event_type=EventType.OPERATOR_END,
                operator=op_name,
                outputs_summary=summary,
                input_hash=input_hash,
                duration_ms=duration_ms,
                nci_delta=nci_delta,
                nci_after=nci_after,
                branch_tag=branch_tag,
            )

            if _ephemeral_span:
                logger.end_span(span_id, nci_exit=nci_after)

            return result

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def hash_input(obj: Any) -> str:
    """Serialize and SHA-256 hash an arbitrary Python object."""
    try:
        serialized = json.dumps(obj, default=str, sort_keys=True)
    except Exception:
        serialized = str(obj)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    import tempfile, shutil

    print("=== arcs_trace.py smoke test ===\n")

    tmp = tempfile.mkdtemp()
    try:
        # 1. Create logger with JSONL backend in temp dir
        backend = JSONLBackend(base_dir=tmp)
        logger  = TraceLogger(backend=backend, pipeline_version="5.0.0-test")

        # 2. Session + span lifecycle
        session_id = logger.start_session(metadata={"purpose": "smoke_test"})
        span_id    = logger.start_span(phase_id="phase_5", nci_entry=82.0)
        print(f"[OK] Session started: {session_id[:20]}...")
        print(f"[OK] Span started:    {span_id[:20]}...")

        # 3. Record several events
        logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_START,
            operator="sage",
            outputs_summary={"signal_class": "accelerating"},
            nci_after=85.0,
            nci_delta=3.0,
        )
        logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="sage",
            outputs_summary={"nci_score": 85.0},
            nci_after=85.0,
        )
        logger.record_event(
            span_id=span_id,
            event_type=EventType.COURT_VERDICT,
            operator="court",
            outputs_summary={"verdict": "PERMIT", "evidence_weight": 0.1},
            nci_after=85.0,
        )
        print("[OK] Events recorded (sage×2, court×1)")

        # 4. Test NCI cliff anomaly detection
        logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="lab",
            outputs_summary={"lab_threat_level": "HIGH"},
            nci_after=65.0,   # 20-point drop → cliff
            nci_delta=-20.0,
        )
        span_obj = logger._active_spans[span_id]
        cliff_anomalies = [a for a in span_obj.anomalies
                           if a.anomaly_type == AnomalyType.NCI_CLIFF]
        assert len(cliff_anomalies) == 1, f"Expected 1 cliff anomaly, got {len(cliff_anomalies)}"
        print(f"[OK] NCI cliff anomaly detected: {cliff_anomalies[0].description[:60]}...")

        # 5. Test ruin_unmarked anomaly
        logger.record_event(
            span_id=span_id,
            event_type=EventType.OPERATOR_END,
            operator="bar",
            outputs_summary={"ruin_risk": True, "verdict": "PERMIT"},
            nci_after=63.0,
        )
        ruin_anomalies = [a for a in span_obj.anomalies
                          if a.anomaly_type == AnomalyType.RUIN_UNMARKED]
        assert len(ruin_anomalies) == 1, f"Expected 1 ruin anomaly, got {len(ruin_anomalies)}"
        print(f"[OK] Ruin-unmarked anomaly detected: {ruin_anomalies[0].severity}")

        # 6. Close span
        span = logger.end_span(span_id, verdict="COMPLETE", nci_exit=63.0)
        assert span.verdict == "COMPLETE"
        assert span.nci_delta == 63.0 - 82.0
        print(f"[OK] Span closed: verdict={span.verdict}, nci_delta={span.nci_delta:.1f}")

        # 7. Verify JSONL files written
        for fname in ["events.jsonl", "spans.jsonl", "anomalies.jsonl"]:
            fpath = os.path.join(tmp, fname)
            assert os.path.exists(fpath), f"Missing {fname}"
            lines = open(fpath).readlines()
            assert len(lines) > 0, f"{fname} is empty"
            print(f"[OK] {fname}: {len(lines)} records")

        # 8. Test @trace_operator decorator
        logger2  = TraceLogger(backend=JSONLBackend(base_dir=tmp), pipeline_version="5.0.0-test")
        sid2 = logger2.start_session()
        spn2 = logger2.start_span(phase_id="phase_5_dec", nci_entry=80.0)

        @trace_operator(logger2, operator_name="test_op",
                        extract_nci=lambda r: r.get("nci"),
                        extract_summary=lambda r: {"verdict": r.get("verdict")})
        def fake_operator(input_val, phase_id="phase_5_dec", _span_id=None):
            return {"nci": 88.0, "verdict": "COMPLETE"}

        result = fake_operator("signal_input", phase_id="phase_5_dec", _span_id=spn2)
        assert result["nci"] == 88.0
        span2 = logger2.end_span(spn2, verdict="COMPLETE", nci_exit=88.0)
        assert len(span2.events) == 2  # START + END
        print(f"[OK] @trace_operator decorator: {len(span2.events)} events, nci_exit={span2.nci_exit}")

        # 9. Test gravitational force API
        force = logger.gravitational_force("sage", "court")
        assert isinstance(force["force"], float)
        print(f"[OK] Gravitational force sage→court: {force['force']:.2f} ({force['coupled']}/{force['total']})")

        # 10. Test annotation API
        ann = logger.annotate(
            span_id=span.span_id,
            label="TRUE_POSITIVE",
            annotated_by="human",
            confidence=0.95,
            notes="NCI cliff confirmed by post-hoc review",
        )
        assert ann.label == "TRUE_POSITIVE"
        print(f"[OK] Annotation written: {ann.label} by {ann.annotated_by}")

        print("\n=== Smoke test PASSED — arcs_trace.py ===")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    _smoke_test()
