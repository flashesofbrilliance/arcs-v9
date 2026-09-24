"""
arcs_api.py — ARCS v9 FastAPI Backend
Exposes the ARCSRuntimeService over HTTP for the Question Compass / Zoetrope UI.

Design:
  - Single POST /api/run   → full pipeline result (SAGE + LAB + BAR + Court + Kintsugi)
  - GET  /api/health       → liveness check
  - GET  /api/latest       → last run receipt (session-scoped)
  - CORS: open in dev, configurable via ARCS_ALLOWED_ORIGINS env var
  - Port: ARCS_PORT env var (default 8765)

Tauri notes:
  - Port and allowed origins are env-configurable — Tauri sidecar sets ARCS_PORT
  - No hard-coded localhost references
  - Stateless per-request (except session reuse within process lifetime)
"""

from __future__ import annotations

import os
import time
import numpy as np
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# ARCS runtime
from arcs_primitives   import CoherenceSignal
from arcs_runtime_service import ARCSRuntimeService, BarRaiserTrigger
from arcs_operator20  import Operator20

# ARCS substrate (GIGI-backed template library + gap log)
try:
    from arcs_substrate import query_template, slot_fill, FiberCoords
    _SUBSTRATE_AVAILABLE = True
except ImportError:
    _SUBSTRATE_AVAILABLE = False

# ARCS backup (iCloud encrypted snapshot, triggered on receipt write)
try:
    from arcs_backup import trigger_backup as _trigger_backup
    _BACKUP_AVAILABLE = True
except ImportError:
    _BACKUP_AVAILABLE = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ARCS_PORT    = int(os.environ.get("ARCS_PORT", "8765"))
ARCS_ORIGINS = os.environ.get(
    "ARCS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,tauri://localhost"
).split(",")

TRACE_DIR = os.environ.get("ARCS_TRACE_DIR", "arcs_trace_logs")

# ---------------------------------------------------------------------------
# Singleton runtime (shared within process, restarted per cold start)
# ---------------------------------------------------------------------------

_service: Optional[ARCSRuntimeService] = None


def get_service() -> ARCSRuntimeService:
    global _service
    if _service is None:
        _service = ARCSRuntimeService(
            trace_dir=TRACE_DIR,
            bar_trigger=BarRaiserTrigger.GATE_ADJACENT,
        )
        _service.start_session({"started_by": "arcs_api", "version": "9.0"})
    return _service


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    """
    Minimal signal descriptor the UI sends.
    signal_values: raw coherence values (1-10 floats, e.g. NCI readings over time)
    domain:        semantic label for the signal domain (e.g. "product_coherence")
    label:         human-readable label for the specific decision signal
    phase_id:      which ARCS phase this run is graded against (default phase_5)
    irreversibility: 0.0–1.0 (how hard is this to undo?)
    on_purpose:    was this decision made with explicit reasoning?
    hci_score:     human coherence index (0.0–1.0), optional
    """
    signal_values:   List[float] = Field(
        ..., min_length=3, max_length=100,
        description="Coherence signal series (min 3 values)"
    )
    domain:          str = Field(default="decision_coherence", max_length=64)
    label:           str = Field(default="compass_run", max_length=128)
    phase_id:        str = Field(default="phase_5")
    irreversibility: float = Field(default=0.25, ge=0.0, le=1.0)
    on_purpose:      bool  = Field(default=True)
    hci_score:       float = Field(default=0.72, ge=0.0, le=1.0)
    fated_facts:     str   = Field(default="", max_length=2000)
    fated_assumptions: str = Field(default="", max_length=2000)
    fated_tradeoffs: str   = Field(default="", max_length=2000)
    fated_emotions:  str   = Field(default="", max_length=2000)
    fated_direction: str   = Field(default="", max_length=2000)

    @field_validator("signal_values")
    @classmethod
    def validate_signal_range(cls, v):
        for val in v:
            if not (0.0 <= val <= 100.0):
                raise ValueError(f"Signal values must be in [0, 100]. Got: {val}")
        return v

    @field_validator("phase_id")
    @classmethod
    def validate_phase(cls, v):
        valid = {"phase_1", "phase_2", "phase_3", "phase_4", "phase_5", "phase_6"}
        if v not in valid:
            raise ValueError(f"phase_id must be one of {valid}")
        return v


class DerivativesPayload(BaseModel):
    velocity:           float
    acceleration:       float
    diffusion:          float
    phase_cancellation: float
    deceleration:       float


class RunResponse(BaseModel):
    """Serializable pipeline result for the frontend."""
    ok:                   bool
    nci_score:            float
    verdict:              str
    signal_classification: str
    on_purpose_label:     str
    is_satoshi:           bool
    coherence_pct:        int        # 0–100 for ring display
    court_verdict:        Optional[str]
    kintsugi_applied:     bool
    bar_review_id:        Optional[str]
    span_id:              str
    session_id:           str
    duration_ms:          float
    anomaly_count:        int
    error:                Optional[str]
    # SAGE receipt fields surfaced for Zoetrope mapping
    five_derivatives:     Dict[str, float]
    axioms:               Dict[str, str]
    somatic:              Dict[str, Any]
    phase_id:             str
    timestamp:            float


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ARCS v9 Runtime API",
    version="9.0.0",
    description="Decision intelligence backend for Question Compass and Zoetrope UI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ARCS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_last_run: Optional[RunResponse] = None

# ── Supabase persistence (F-002) ──────────────────────────────────────────────
# Receipts are written to Supabase and read back from it.
# In-memory dict kept as a fallback if SUPABASE_URL is absent (local dev w/o creds).

_SUPABASE_URL  = os.environ.get("SUPABASE_URL", "")
_SUPABASE_KEY  = os.environ.get("SUPABASE_ANON_KEY", "")
_sb_client = None

if _SUPABASE_URL and _SUPABASE_KEY:
    try:
        from supabase import create_client
        _sb_client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
        print(f"[arcs_api] Supabase client initialised → {_SUPABASE_URL}")
    except Exception as _sb_err:
        print(f"[arcs_api] Supabase init failed: {_sb_err} — falling back to in-memory store")

# In-memory fallback (used when Supabase is unavailable)
_receipt_store: Dict[str, List[Dict[str, Any]]] = {}
_RECEIPT_STORE_MAX = 500


def _store_receipt(user_id: str, snapshot: Dict[str, Any]) -> None:
    """Write receipt to Supabase (primary) and in-memory dict (fallback)."""
    if _sb_client is not None:
        try:
            _sb_client.table("arcs_receipts").upsert({
                "receipt_id":    snapshot["receipt_id"],
                "user_id":       user_id,
                "question":      snapshot["question"],
                "true_north":    snapshot["true_north"],
                "why":           snapshot.get("why", []),
                "decision_mode": snapshot["decision_mode"],
                "nci_score":     snapshot.get("nci_score"),
                "is_satoshi":    snapshot.get("is_satoshi", False),
                "door_class":    snapshot.get("door_class"),
                "horizon":       snapshot.get("horizon"),
                "stakes":        snapshot.get("stakes"),
                "status":        snapshot.get("status", "OPEN"),
                "payload":       snapshot,
            }).execute()
            return  # Supabase write succeeded — skip in-memory mirror
        except Exception as e:
            print(f"[arcs_api] Supabase write failed: {e} — falling back to memory")

    # In-memory fallback
    bucket = _receipt_store.setdefault(user_id, [])
    bucket.append(snapshot)
    if len(bucket) > _RECEIPT_STORE_MAX:
        bucket.pop(0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_sage_fields(receipt) -> Dict[str, Any]:
    """Pull SAGE-specific fields from a CoherenceReceipt for Zoetrope mapping."""
    if receipt is None:
        return {
            "five_derivatives": {},
            "axioms": {},
            "somatic": {},
            "signal_classification": "noise",
            "on_purpose_label": "unknown",
            "is_satoshi": False,
        }
    return {
        "five_derivatives": getattr(receipt, "five_derivatives", {}) or {},
        "axioms": {
            "clarity_before_curvature":   getattr(receipt.axioms, "clarity_before_curvature",   "NO"),
            "agency_over_automation":     getattr(receipt.axioms, "agency_over_automation",     "NO"),
            "minimum_steps_to_coherence": getattr(receipt.axioms, "minimum_steps_to_coherence", "NO"),
            "kairos_over_neuroticism":    getattr(receipt.axioms, "kairos_over_neuroticism",    "NO"),
        } if receipt.axioms else {},
        "somatic": {
            "phase_tuning":        getattr(receipt.somatic, "phase_tuning",        0.5),
            "surge_detection":     getattr(receipt.somatic, "surge_detection",     False),
            "feels_right":         getattr(receipt.somatic, "feels_right",         False),
            "that_vibes":          getattr(receipt.somatic, "that_vibes",          False),
            "locked_in":           getattr(receipt.somatic, "locked_in",           False),
            "expected_vs_actual":  getattr(receipt.somatic, "expected_vs_actual",  0.5),
            # Derived witness score: mean of boolean somatic signals (0 or 1)
            "witness_score": sum([
                float(getattr(receipt.somatic, "feels_right",  False) or 0),
                float(getattr(receipt.somatic, "that_vibes",   False) or 0),
                float(getattr(receipt.somatic, "locked_in",    False) or 0),
            ]) / 3.0,
        } if receipt.somatic else {},
        "signal_classification": getattr(receipt, "signal_classification", "noise"),
        "on_purpose_label":      getattr(receipt, "on_purpose_label", "unknown"),
        # is_satoshi is a method, not a property — call it
        "is_satoshi": receipt.is_satoshi() if callable(getattr(receipt, "is_satoshi", None)) else bool(getattr(receipt, "is_satoshi", False)),
    }


def _build_fated(req: RunRequest):
    from arcs_operators_sage import FATEDReasoning
    facts       = req.fated_facts       or f"Signal analysis for domain '{req.domain}', label '{req.label}'."
    assumptions = req.fated_assumptions or "Signal reflects current decision context. Values are representative."
    tradeoffs   = req.fated_tradeoffs   or f"Irreversibility {req.irreversibility:.0%}. Review before committing."
    emotions    = req.fated_emotions    or "Compass run initiated via UI. Operator review recommended."
    direction   = req.fated_direction   or f"Proceed with {req.phase_id} pipeline analysis."
    return FATEDReasoning(
        facts=facts, assumptions=assumptions, tradeoffs=tradeoffs,
        emotions=emotions, direction=direction,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Liveness probe. Returns service status and session info."""
    svc = get_service()
    return {
        "status":     "ok",
        "version":    "9.0.0",
        "session_id": svc._session_id,
        "timestamp":  time.time(),
    }


@app.post("/api/run", response_model=RunResponse)
def run_pipeline(req: RunRequest):
    """
    Run the full ARCS pipeline (SAGE → LAB → BAR → Court → Kintsugi).
    Returns NCI score, signal classification, Zoetrope ring mapping data,
    court verdict, and satoshi status.
    """
    global _last_run

    svc = get_service()

    try:
        signal = CoherenceSignal(
            signal=np.array(req.signal_values, dtype=float),
            domain=req.domain,
            label=req.label,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid signal: {e}")

    fated   = _build_fated(req)
    from arcs_operators_sage import AxiomCheck, SomaticReading
    axioms  = AxiomCheck(
        clarity_before_curvature="YES",
        agency_over_automation="YES",
        minimum_steps_to_coherence="YES",
        kairos_over_neuroticism="YES",
    )
    somatic = SomaticReading(
        phase_tuning=req.hci_score,
        surge_detection=False,
        feels_right=req.on_purpose,
        that_vibes=True,
        locked_in=True,
        expected_vs_actual=req.hci_score,
    )

    # The trace JSONL backend serializes span.metadata to JSON.
    # Pass dataclass objects directly (the runtime extracts them by type);
    # put only JSON-serializable scalars in the metadata dict itself.
    metadata = {
        "fated":          fated,    # runtime pops this before span logging
        "axioms":         axioms,   # same
        "somatic":        somatic,  # same
        "hci_score":      req.hci_score,
        "irreversibility": req.irreversibility,
        "on_purpose":     req.on_purpose,
        "next_action":    f"proceed with {req.phase_id}",
        "source":         "arcs_api",
        # JSON-safe summary (for trace logging)
        "_fated_summary": f"F:{req.fated_facts[:40] if req.fated_facts else 'auto'}",
    }

    result = svc.run_pipeline(
        signal=signal,
        phase_id=req.phase_id,
        nci_entry=None,
        metadata=metadata,
    )

    sage_fields = _extract_sage_fields(result.receipt)
    court_str   = result.court_verdict.verdict if result.court_verdict else None

    resp = RunResponse(
        ok=result.is_success,
        nci_score=round(result.nci_score, 2),
        verdict=result.verdict.value,
        signal_classification=sage_fields["signal_classification"],
        on_purpose_label=sage_fields["on_purpose_label"],
        is_satoshi=sage_fields["is_satoshi"],
        coherence_pct=min(100, max(0, int(result.nci_score))),
        court_verdict=court_str,
        kintsugi_applied=result.kintsugi_applied,
        bar_review_id=result.bar_review_id,
        span_id=result.span_id,
        session_id=result.session_id,
        duration_ms=round(result.duration_ms, 2),
        anomaly_count=result.anomaly_count,
        error=result.error,
        five_derivatives=sage_fields["five_derivatives"],
        axioms=sage_fields["axioms"],
        somatic=sage_fields["somatic"],
        phase_id=req.phase_id,
        timestamp=time.time(),
    )
    _last_run = resp
    return resp


# ---------------------------------------------------------------------------
# SAGE score — advisory pre-screen for the Next.js compass route
# ---------------------------------------------------------------------------
# NOTOMATION boundary: this endpoint enriches Claude's context with operator
# signal (NCI, court verdict, axioms). It never persists — the Prisma Receipt
# model in arcs-v9 is the single source of truth. Do not add a _store_receipt
# call here; that would create a second, divergent receipt store.

class SageScoreRequest(BaseModel):
    """Human-language input from the Next.js compass route."""
    question:  str   = Field(..., min_length=4, max_length=2000)
    # Accept the arcs-v9 canonical horizon enum (TODAY|THIS_WEEK|THIS_QUARTER|
    # ONE_TO_THREE_YEARS — what the compass route actually sends) alongside the
    # legacy THIS_YEAR|LONG_ARC values the service defined but the app never emits.
    horizon:   str   = Field(default="THIS_WEEK",
                              pattern=r"^(TODAY|THIS_WEEK|THIS_QUARTER|ONE_TO_THREE_YEARS|THIS_YEAR|LONG_ARC)$")
    stakes:    str   = Field(default="MEDIUM", pattern=r"^(LOW|MEDIUM|HIGH)$")
    hci_score: float = Field(default=0.72, ge=0.0, le=1.0)


@app.post("/api/sage-score", response_model=RunResponse)
def sage_score(req: SageScoreRequest):
    """
    Runs SAGE → LAB → BAR → Court → Kintsugi on a synthetic signal derived
    from stakes/horizon/hci_score, and returns the raw pipeline result.
    No persistence — see NOTOMATION note above.
    """
    irreversibility = _HORIZON_IRREVERSIBILITY.get(req.horizon, 0.25)
    base    = _STAKES_SIGNALS[req.stakes]
    hci_mod = 0.85 + (req.hci_score * 0.30)
    irr_mod = 1.0  - (irreversibility * 0.10)
    signal_values = [round(v * hci_mod * irr_mod, 3) for v in base]

    run_req = RunRequest(
        signal_values=signal_values,
        domain="question_compass",
        label=req.question[:128],
        phase_id="phase_5",
        irreversibility=irreversibility,
        on_purpose=True,
        hci_score=req.hci_score,
        fated_facts=req.question,
    )
    return run_pipeline(run_req)


# ---------------------------------------------------------------------------
# Question Compass — front-door endpoint
# ---------------------------------------------------------------------------

class QuestionCompassRequest(BaseModel):
    """Native front-door contract. Accepts human language, not signal floats."""
    question:       str   = Field(..., min_length=4, max_length=2000)
    horizon:        str   = Field(default="THIS_WEEK",
                                  pattern=r"^(TODAY|THIS_WEEK|THIS_QUARTER|ONE_TO_THREE_YEARS|THIS_YEAR|LONG_ARC)$")
    stakes:         str   = Field(default="MEDIUM", pattern=r"^(LOW|MEDIUM|HIGH)$")
    clarity_mode:   str   = Field(default="SIMPLE", pattern=r"^(SIMPLE|RICH|DEEP)$")
    jtbd:           str   = Field(default="", max_length=500)
    user_id:        str   = Field(default="anonymous", max_length=64)
    hci_score:      float = Field(default=0.72, ge=0.0, le=1.0)
    irreversibility: float = Field(default=0.25, ge=0.0, le=1.0)


class QuestionCompassResponse(BaseModel):
    """Spec-compliant front-door response."""
    true_north:                  str
    why:                         List[str]
    decision_mode:               str          # QUICKMOVE | PLAN | COURT
    clarity_mode:                str
    receipt_id:                  str
    show_full_reasoning_available: bool
    drift_state:                 str          # ONTRACK | USEFUL_TANGENT | DERAILMENT
    meta: Dict[str, Any]
    # Pipeline internals (for UI ring display)
    nci_score:    float
    coherence_pct: int
    is_satoshi:   bool
    door_class:   str          # TWO_WAY | ONE_WAY
    error:        Optional[str]


_STAKES_SIGNALS: Dict[str, List[float]] = {
    "LOW":    [3.0, 3.5, 4.0, 4.2, 4.5],
    "MEDIUM": [5.0, 5.5, 6.0, 6.3, 6.7],
    "HIGH":   [7.5, 8.0, 8.3, 8.6, 9.0],
}

_HORIZON_IRREVERSIBILITY: Dict[str, float] = {
    "TODAY":              0.10,
    "THIS_WEEK":          0.20,
    "THIS_QUARTER":       0.40,
    "ONE_TO_THREE_YEARS": 0.70,  # arcs-v9 canonical long horizon (multi-year → high irreversibility)
    "THIS_YEAR":          0.60,
    "LONG_ARC":           0.85,
}


def _compute_kairos(mode: str, nci_score: int, horizon: str) -> dict:
    horizon_map = {
        "today":        "TODAY",
        "this_week":    "THIS_WEEK",
        "this week":    "THIS_WEEK",
        "this_quarter": "QUARTER",
        "this quarter": "QUARTER",
        "this_year":    "QUARTER",
        "one_to_three_years": "QUARTER",
        "1-3 years":    "QUARTER",
        "long_arc":     "QUARTER",
    }
    kairos_horizon = horizon_map.get(horizon.lower(), "TODAY")
    if mode == "QUICKMOVE":
        state, confidence, signal = "LOCK", 88, "Window is narrow — move now"
    elif mode == "COURT":
        state, confidence, signal = "SYNC", 82, "Aligned — deliberate action indicated"
    elif nci_score < 65:
        state, confidence, signal = "DRIFT", 55, "Signal unclear — clarify before committing"
    elif mode == "PLAN":
        state, confidence, signal = "SYNC", 75, "Conditions favorable — plan with intention"
    else:
        state, confidence, signal = "OPEN", 70, "No strong timing pressure detected"
    return {"state": state, "confidence": confidence, "signal": signal, "horizon": kairos_horizon}


def _select_decision_mode(stakes: str, horizon: str) -> str:
    if stakes == "HIGH" or horizon in ("ONE_TO_THREE_YEARS", "THIS_YEAR", "LONG_ARC"):
        return "COURT"
    if stakes == "LOW" and horizon in ("TODAY", "THIS_WEEK"):
        return "QUICKMOVE"
    return "PLAN"


def _select_door_class(stakes: str, horizon: str) -> str:
    if stakes == "HIGH" or horizon in ("ONE_TO_THREE_YEARS", "THIS_YEAR", "LONG_ARC"):
        return "ONE_WAY"
    return "TWO_WAY"


_STAKES_TO_FIBER = {"LOW": "low", "MEDIUM": "medium", "HIGH": "high"}
_HORIZON_TO_FIBER = {
    "TODAY": "today", "THIS_WEEK": "this-week",
    "THIS_QUARTER": "this-quarter", "ONE_TO_THREE_YEARS": "multi-year",
    "THIS_YEAR": "multi-year", "LONG_ARC": "multi-year",
}


def _extract_true_north_and_why(
    question: str, result, decision_mode: str, jtbd: str = "",
    stakes: str = "", horizon: str = ""
) -> tuple[str, List[str], dict]:
    """Derive true north using ARCS template library (GIGI) with L5 raw fallback."""
    nci = result.nci_score
    verdict = result.verdict.value if hasattr(result.verdict, "value") else str(result.verdict)

    q_short = question.strip().rstrip("?").strip()

    jtbd_lines: List[str] = []
    if jtbd and jtbd.strip():
        for part in jtbd.replace(". ", "\n").splitlines():
            part = part.strip().rstrip(".")
            if len(part) > 10:
                jtbd_lines.append(part)

    # ── Substrate gate: query ARCS template library (persisted via GIGI) ──────
    substrate_meta: dict = {"routing_path": "L5_floor", "holonomy_distance": 1.0, "confidence": 0.0}
    if _SUBSTRATE_AVAILABLE and stakes and horizon:
        coords = FiberCoords(
            stakes=_STAKES_TO_FIBER.get(stakes, "medium"),
            horizon=_HORIZON_TO_FIBER.get(horizon, "this-week"),
        )
        sr = query_template("BAR", coords)
        substrate_meta = {
            "routing_path": sr.routing_path,
            "holonomy_distance": round(sr.holonomy_distance, 3),
            "confidence": round(sr.confidence, 3),
            "template_id": sr.template_id or "",
            "provenance": sr.provenance or "",
        }
        if sr.routing_path in ("L1_match", "L2_partial") and sr.skeleton:
            filled = slot_fill(sr.skeleton, {"question": q_short, "jtbd": jtbd or decision_mode})
            if sr.routing_path == "L1_match":
                match_label = f"matched (confidence {sr.confidence:.2f})"
            else:
                match_label = f"matched at distance {sr.holonomy_distance:.2f} — verify before committing"
            why = [
                f"ARCS template {match_label}.",
                jtbd_lines[0] if jtbd_lines else f"Decision mode: {decision_mode}.",
                jtbd_lines[1] if len(jtbd_lines) > 1 else f"Template: {sr.template_id}.",
            ]
            return filled, why, substrate_meta
    # ── L5 floor: existing template-string logic (unchanged) ─────────────────

    if verdict in ("COMPLETE", "ACCEPTABLE"):
        mode_verb = {
            "QUICKMOVE": "execute with confidence",
            "PLAN":      "map terrain then commit",
            "COURT":     "convene and deliberate",
        }.get(decision_mode, "proceed with reasoning logged")

        if jtbd_lines:
            true_north = f"{q_short} — {mode_verb}. NCI {nci:.0f}/100, signal is coherent."
            why = [
                f"NCI {nci:.0f}/100 — above coherence threshold.",
                jtbd_lines[0],
                jtbd_lines[1] if len(jtbd_lines) > 1 else f"Reversibility profile matches {decision_mode} track.",
            ]
        else:
            true_north = f"{q_short} — {mode_verb}. NCI {nci:.0f}/100."
            why = [
                f"NCI {nci:.0f}/100 — above coherence threshold.",
                "All four DNA axioms check out.",
                f"Reversibility profile matches {decision_mode} track.",
            ]

    elif verdict == "BLOCKED":
        true_north = f"{q_short} — restore coherence before committing. Active blocks detected."
        why = [
            "Pipeline returned BLOCKED — ruin risk or axiom violation detected.",
            "Review the signal for urgency inflation or thin evidence.",
            "Resubmit with explicit FATED reasoning.",
        ]

    else:
        true_north = f"{q_short} — proceed with caution. Signal quality is uncertain."
        why = [
            f"NCI {nci:.0f}/100 — below optimal threshold.",
            "Consider adding more context before deciding.",
        ]

    return true_north, why, substrate_meta


@app.post("/question-compass", response_model=QuestionCompassResponse)
def question_compass(req: QuestionCompassRequest):
    """
    Front-door endpoint. Accepts a human-language question and returns
    one coherent next move (True North) with minimal explanation.
    Spec: question-compass-service.md
    """
    import uuid

    # Prefer explicit irreversibility from frontend; fall back to horizon-derived value
    irreversibility = req.irreversibility if req.irreversibility != 0.25 else _HORIZON_IRREVERSIBILITY[req.horizon]

    # Derive signal values from stakes baseline, modulated by hci_score and irreversibility.
    # Without this, every HIGH question produces identical NCI (deterministic lookup).
    base   = _STAKES_SIGNALS[req.stakes]
    # hci_score 0→1 shifts signals ±15%; irreversibility 0→1 reduces them up to 10%
    hci_mod = 0.85 + (req.hci_score * 0.30)   # range: 0.85–1.15
    irr_mod = 1.0  - (irreversibility * 0.10)  # range: 0.90–1.00
    signal_values = [round(v * hci_mod * irr_mod, 3) for v in base]
    decision_mode   = _select_decision_mode(req.stakes, req.horizon)
    door_class      = _select_door_class(req.stakes, req.horizon)
    receipt_id      = f"dr_{uuid.uuid4().hex[:12]}"

    # Build a RunRequest and reuse the pipeline
    run_req = RunRequest(
        signal_values=signal_values,
        domain="question_compass",
        label=req.question[:128],
        phase_id="phase_5",
        irreversibility=irreversibility,
        on_purpose=True,
        hci_score=req.hci_score,
        fated_facts=req.question,
        fated_assumptions=req.jtbd or "User submitted via Question Compass front door.",
        fated_direction=f"Route to {decision_mode} at {req.horizon} horizon.",
    )
    run_resp = run_pipeline(run_req)

    true_north, why, substrate_meta = _extract_true_north_and_why(
        req.question,
        type("R", (), {
            "nci_score": run_resp.nci_score,
            "verdict": type("V", (), {"value": run_resp.verdict})(),
        })(),
        decision_mode,
        jtbd=req.jtbd,
        stakes=req.stakes,
        horizon=req.horizon,
    )

    macro_tags: List[str] = []
    if irreversibility >= 0.5:
        macro_tags.append("BAR_ASYMMETRIC")
    if req.horizon in ("TODAY", "THIS_WEEK"):
        macro_tags.append("KKL_OPEN_WINDOW")
    if decision_mode == "COURT":
        macro_tags.append("COURT_REQUIRED")

    import datetime as _dt
    response = QuestionCompassResponse(
        true_north=true_north,
        why=why,
        decision_mode=decision_mode,
        clarity_mode=req.clarity_mode,
        receipt_id=receipt_id,
        show_full_reasoning_available=(req.clarity_mode == "SIMPLE"),
        drift_state="ONTRACK",
        meta={"door_class": door_class, "macro_tags": macro_tags, "substrate": substrate_meta},
        nci_score=run_resp.nci_score,
        coherence_pct=run_resp.coherence_pct,
        is_satoshi=run_resp.is_satoshi,
        door_class=door_class,
        error=run_resp.error,
    )
    _store_receipt(req.user_id, {
        "receipt_id":    receipt_id,
        "timestamp":     _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "question":      req.question,
        "true_north":    true_north,
        "why":           why,
        "decision_mode": decision_mode,
        "nci_score":     run_resp.nci_score,
        "is_satoshi":    run_resp.is_satoshi,
        "door_class":    door_class,
        "horizon":       req.horizon,
        "stakes":        req.stakes,
        "status":        "OPEN",
        "user_id":       req.user_id,
        "kairos":        _compute_kairos(decision_mode, int(run_resp.nci_score), req.horizon),
        "substrate":     substrate_meta,
    })
    if _BACKUP_AVAILABLE:
        _trigger_backup("receipt_written")
    return response


@app.get("/api/latest", response_model=Optional[RunResponse])
def latest_run():
    """Returns the most recent pipeline run result (session-scoped)."""
    return _last_run


@app.get("/api/receipts")
def list_receipts(user_id: str = "anonymous", limit: int = 50, offset: int = 0):
    """Returns receipts for a user, newest first. Reads from Supabase when available."""
    if _sb_client is not None:
        try:
            resp = (
                _sb_client.table("arcs_receipts")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            rows = resp.data or []
            # total count
            count_resp = (
                _sb_client.table("arcs_receipts")
                .select("receipt_id", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            total = count_resp.count or len(rows)
            # Flatten payload into row for backwards-compat with UI shape
            receipts = [r.get("payload", r) for r in rows]
            return {"receipts": receipts, "total": total, "offset": offset, "limit": limit}
        except Exception as e:
            print(f"[arcs_api] Supabase list failed: {e} — falling back to memory")

    # In-memory fallback
    bucket = _receipt_store.get(user_id, [])
    ordered = list(reversed(bucket))
    page = ordered[offset: offset + limit]
    return {"receipts": page, "total": len(bucket), "offset": offset, "limit": limit}


@app.get("/api/receipts/{receipt_id}")
def get_receipt(receipt_id: str, user_id: str = "anonymous"):
    """Returns a single receipt by ID. Reads from Supabase when available."""
    if _sb_client is not None:
        try:
            resp = (
                _sb_client.table("arcs_receipts")
                .select("*")
                .eq("receipt_id", receipt_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            if rows:
                return rows[0].get("payload", rows[0])
        except Exception as e:
            print(f"[arcs_api] Supabase get failed: {e} — falling back to memory")

    # In-memory fallback
    bucket = _receipt_store.get(user_id, [])
    match = next((r for r in bucket if r["receipt_id"] == receipt_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Receipt {receipt_id} not found for user {user_id}")
    return match


@app.patch("/api/receipts/{receipt_id}")
def update_receipt_status(receipt_id: str, user_id: str = "anonymous", status: str = "IMPLEMENTED"):
    """Update receipt status (OPEN → IMPLEMENTED | ARCHIVED)."""
    allowed = {"OPEN", "IMPLEMENTED", "ARCHIVED"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {allowed}")

    if _sb_client is not None:
        try:
            resp = (
                _sb_client.table("arcs_receipts")
                .update({"status": status})
                .eq("receipt_id", receipt_id)
                .eq("user_id", user_id)
                .execute()
            )
            rows = resp.data or []
            if not rows:
                raise HTTPException(status_code=404, detail=f"Receipt {receipt_id} not found for user {user_id}")
            return rows[0].get("payload", rows[0])
        except HTTPException:
            raise
        except Exception as e:
            print(f"[arcs_api] Supabase patch failed: {e} — falling back to memory")

    # In-memory fallback
    bucket = _receipt_store.get(user_id, [])
    match = next((r for r in bucket if r["receipt_id"] == receipt_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Receipt {receipt_id} not found for user {user_id}")
    match["status"] = status
    return match


@app.get("/api/loki")
def loki_report():
    """Returns BarRaiser threshold config for FE slider."""
    svc = get_service()
    return svc.loki_report()


# ---------------------------------------------------------------------------
# Cultivate — Operator20 folksonomy endpoint
# ---------------------------------------------------------------------------

_op20: Optional[Operator20] = None


def get_op20() -> Operator20:
    global _op20
    if _op20 is None:
        _op20 = Operator20()
    return _op20


# ── Operator 20 / Cultivate ────────────────────────────────────────────────────

MIN_CULTIVATE_MANUAL = 5
MIN_CULTIVATE_AUTO   = 12
AUTO_CULTIVATE_DELTA = 12

# In-memory archive state fallback (mirrors _receipt_store pattern)
_archive_state_store: Dict[str, Dict[str, Any]] = {}


class CultivateRequest(BaseModel):
    receipts:  List[Dict[str, Any]] = Field(..., min_length=1)
    phase_id:  str = "phase_6"
    user_id:   str = "anonymous"
    spans:     Optional[List[Dict[str, Any]]] = None


def _derive_archive_id(user_id: Optional[str], phase_id: Optional[str]) -> str:
    uid = user_id or "anonymous"
    pid = phase_id or "phase_7"
    return f"{uid}:{pid}"


def _load_archive_state(archive_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    if _sb_client is not None:
        try:
            resp = _sb_client.table("archive_state").select("*").eq("archive_id", archive_id).execute()
            if resp.data:
                return resp.data[0]
        except Exception as e:
            print(f"[arcs_api] archive_state load failed: {e} — using memory")
    return _archive_state_store.get(archive_id, {
        "archive_id": archive_id,
        "user_id": user_id or "anonymous",
        "total_receipts": 0,
        "last_cultivate_corpus_size": 0,
        "last_cultivate_receipt_id": None,
        "last_cultivate_report_id": None,
        "last_cultivate_at": None,
    })


def _save_archive_state(state: Dict[str, Any]) -> None:
    import datetime as _dt
    state["updated_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    if _sb_client is not None:
        try:
            _sb_client.table("archive_state").upsert(state).execute()
            return
        except Exception as e:
            print(f"[arcs_api] archive_state save failed: {e} — using memory")
    _archive_state_store[state["archive_id"]] = state


def _refresh_archive_state(archive_id: str, user_id: Optional[str] = None, current_count: Optional[int] = None) -> Dict[str, Any]:
    state = _load_archive_state(archive_id, user_id)
    if current_count is not None:
        state["total_receipts"] = current_count
    return state


def should_auto_cultivate(state: Dict[str, Any]) -> bool:
    total = state.get("total_receipts", 0)
    last  = state.get("last_cultivate_corpus_size", 0)
    return total >= MIN_CULTIVATE_AUTO and (total - last) >= AUTO_CULTIVATE_DELTA


def operator20_cultivate(receipts: List[Dict[str, Any]], phase_id: str = "phase_7", spans: Optional[List] = None) -> Dict[str, Any]:
    """Pure clustering function — extracted from route handler."""
    op20  = get_op20()
    seeds = op20.extract_seeds(receipts, spans=spans)
    report = op20.cultivate(seeds, phase_id=phase_id)
    return report.to_dict()


def _build_cultivate_receipt(
    archive_id: str,
    user_id: str,
    report: Dict[str, Any],
    trigger: str,
    corpus_size_at_run: int,
    previous_cultivate_corpus_size: int,
) -> Dict[str, Any]:
    import uuid
    import datetime as _dt
    receipt_id = f"cv_{uuid.uuid4().hex[:12]}"
    return {
        "receipt_id":    receipt_id,
        "receipt_type":  "cultivate",
        "archive_id":    archive_id,
        "user_id":       user_id,
        "question":      f"Auto-cultivate corpus snapshot ({archive_id})",
        "true_north":    f"Corpus cultivated — {report.get('cluster_count', 0)} clusters, {report.get('branch_count', 0)} branches.",
        "why":           [
            f"Corpus size at run: {corpus_size_at_run}",
            f"Trigger: {trigger}",
            f"Previous cultivate corpus size: {previous_cultivate_corpus_size}",
        ],
        "decision_mode": "PLAN",
        "nci_score":     report.get("quality_metrics", {}).get("coherence_score", 0) * 100 if report.get("quality_metrics") else 0,
        "is_satoshi":    False,
        "status":        "OPEN",
        "tags":          ["operator:20", "action:cultivate", f"trigger:{trigger}"],
        "timestamp":     _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "payload": {
            "cultivate_report":               report,
            "corpus_size_at_run":             corpus_size_at_run,
            "trigger":                        trigger,
            "previous_cultivate_corpus_size": previous_cultivate_corpus_size,
        },
    }


def run_cultivate(
    receipts: List[Dict[str, Any]],
    archive_id: str,
    user_id: str,
    trigger: str,
    phase_id: str = "phase_7",
    spans: Optional[List] = None,
) -> Dict[str, Any]:
    """Shared runner for manual and auto cultivate. Returns the cultivate receipt."""
    state   = _load_archive_state(archive_id, user_id)
    total   = len(receipts)
    prev    = state.get("last_cultivate_corpus_size", 0)
    report  = operator20_cultivate(receipts, phase_id=phase_id, spans=spans)
    receipt = _build_cultivate_receipt(
        archive_id=archive_id,
        user_id=user_id,
        report=report,
        trigger=trigger,
        corpus_size_at_run=total,
        previous_cultivate_corpus_size=prev,
    )
    _store_receipt(user_id, receipt)
    if _BACKUP_AVAILABLE:
        _trigger_backup("receipt_written")
    state.update({
        "archive_id":                  archive_id,
        "user_id":                     user_id,
        "total_receipts":              total,
        "last_cultivate_corpus_size":  total,
        "last_cultivate_receipt_id":   receipt["receipt_id"],
        "last_cultivate_report_id":    report.get("report_id"),
        "last_cultivate_at":           receipt["timestamp"],
    })
    _save_archive_state(state)
    return receipt


@app.post("/api/cultivate")
def cultivate(req: CultivateRequest):
    """
    Run Operator20 folksonomy clustering over a receipt corpus.
    Returns a CultivateReport with cluster metadata, branches, and quality metrics.
    Requires at least MIN_CULTIVATE_MANUAL receipts; returns corpus_warning=1.0 below threshold.
    Every call writes an immutable CultivateReceipt and updates archive state.
    """
    archive_id = _derive_archive_id(req.user_id, req.phase_id)
    receipt    = run_cultivate(
        receipts=req.receipts,
        archive_id=archive_id,
        user_id=req.user_id,
        trigger="manual",
        phase_id=req.phase_id,
        spans=req.spans,
    )
    return receipt["payload"]["cultivate_report"]


@app.post("/api/cultivate/auto-sweep")
def cultivate_auto_sweep(user_id: Optional[str] = None):
    """
    Scan all known archive states and auto-cultivate any that meet the delta threshold.
    Safe to call from cron; each qualifying archive gets a new immutable CultivateReceipt.
    """
    results = []
    # Build candidate archive IDs from archive_state store + receipt store (discovery)
    candidate_ids: set = set(_archive_state_store.keys())
    if _sb_client is not None:
        try:
            resp = _sb_client.table("archive_state").select("archive_id,user_id").execute()
            for row in (resp.data or []):
                candidate_ids.add(row["archive_id"])
        except Exception as e:
            print(f"[arcs_api] auto-sweep state fetch failed: {e}")
    # Discover archives from known users in receipt store (covers in-memory / first-run)
    for uid in list(_receipt_store.keys()):
        candidate_ids.add(_derive_archive_id(uid, "phase_7"))

    for aid in candidate_ids:
        # Extract user_id from archive_id (format: "user_id:phase_id")
        uid_from_aid = aid.split(":")[0] if ":" in aid else "anonymous"
        state = _load_archive_state(aid, uid_from_aid)
        uid   = state.get("user_id") or uid_from_aid
        # Refresh total_receipts from live store before evaluating predicate
        if _sb_client is not None:
            try:
                count_resp = _sb_client.table("arcs_receipts").select("receipt_id", count="exact").eq("user_id", uid).execute()
                state["total_receipts"] = count_resp.count or state["total_receipts"]
            except Exception:
                pass
        else:
            state["total_receipts"] = len(_receipt_store.get(uid, []))
        if not should_auto_cultivate(state):
            results.append({"archive_id": aid, "action": "skip", "reason": "below threshold"})
            continue
        # Fetch receipts for this archive
        uid = state.get("user_id", "anonymous")
        try:
            if _sb_client is not None:
                resp = _sb_client.table("arcs_receipts").select("payload").eq("user_id", uid).execute()
                receipts = [r.get("payload", r) for r in (resp.data or [])]
            else:
                receipts = _receipt_store.get(uid, [])
            receipt = run_cultivate(receipts=receipts, archive_id=aid, user_id=uid, trigger="auto")
            results.append({"archive_id": aid, "action": "cultivated", "receipt_id": receipt["receipt_id"]})
        except Exception as e:
            results.append({"archive_id": aid, "action": "error", "reason": str(e)})

    return {"swept": len(candidate_ids), "results": results}


# ---------------------------------------------------------------------------
# Embeddings — local, offline, air-gap-capable (ADR-065: pgvector projection)
# ---------------------------------------------------------------------------
# Lazy-loaded sentence-transformers model. No network call at request time
# once the model is cached locally (first run downloads it once from the
# model hub; every call after that is fully offline). This is the embedding
# pipeline ADR-065 flagged as "not built yet, an ask-first migration" —
# populates ScanSignal.signalEmbedding / ScanFeedback.feedbackEmbedding
# (Prisma TEXT field on the arcs-v9 side), with the pgvector companion
# column on Supabase doing the actual cosine-similarity search.

EMBED_MODEL_NAME = os.environ.get("ARCS_EMBED_MODEL", "all-MiniLM-L6-v2")
_embed_model = None


def get_embed_model():
    """Lazy-load the local embedding model on first use, not at import time."""
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


class EmbedRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=256,
                              description="One or more strings to embed.")


class EmbedResponse(BaseModel):
    model: str
    dims: int
    vectors: List[List[float]]


@app.post("/api/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    """
    Local, offline embedding endpoint. Generates sentence embeddings with a
    cached sentence-transformers model — no external API call, no per-request
    cost, runs fully air-gapped once the model is cached locally.
    """
    try:
        model = get_embed_model()
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="sentence-transformers not installed. Run: pip install -e '.[embeddings]'",
        ) from e
    vectors = model.encode(req.texts, convert_to_numpy=True).tolist()
    return EmbedResponse(
        model=EMBED_MODEL_NAME,
        dims=len(vectors[0]) if vectors else 0,
        vectors=vectors,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print(f"ARCS API starting on port {ARCS_PORT}")
    print(f"Allowed origins: {ARCS_ORIGINS}")
    uvicorn.run("arcs_api:app", host="0.0.0.0", port=ARCS_PORT, reload=True)
