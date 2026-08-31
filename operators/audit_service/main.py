#!/usr/bin/env python3
"""
audit_service/main.py — Path A FastAPI audit layer.

Exposes:
  GET  /api/audit/health
  POST /api/audit/sage
  POST /api/audit/lab
  POST /api/audit/bar
  POST /api/audit/kintsugi
  POST /api/audit/receipt   (batch: all four in one call, optional)

The compass route calls these AFTER LLM inference, persists the audit trace
+ benchmark fragment, and (optionally) injects the advisory block back into
context for a follow-up enrichment pass.

Run:
    cd operators && uvicorn audit_service.main:app --host 127.0.0.1 --port 8766
"""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict

# Make operators/ importable regardless of cwd
_HERE = Path(__file__).resolve().parent
_SYSROOT = _HERE.parent  # operators/
if str(_SYSROOT) not in sys.path:
    sys.path.insert(0, str(_SYSROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    AuditRequest,
    AuditResponse,
    CombinedAuditResponse,
    HealthResponse,
)
from .service import run_sage, run_lab, run_bar, run_kintsugi
from .persistence import (
    store_audit_trace,
    store_benchmark_fragment,
    store_csm_result,
    compute_csm,
    compute_all_csm,
)
from .coverage_hooks import record_coverage

APP_VERSION = "1.0.0"
OPERATORS = ["SAGE", "LAB", "BAR", "KINTSUGI"]

PORT = int(os.environ.get("AUDIT_SERVICE_PORT", "8766"))
ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "AUDIT_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,tauri://localhost",
    ).split(",")
    if o.strip()
]

app = FastAPI(
    title="ARCS v9 Audit Service",
    version=APP_VERSION,
    description="Path A operator audit layer for the Question Compass route.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/audit/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, operators=OPERATORS, version=APP_VERSION)


# ── Per-operator endpoints ────────────────────────────────────────────────────

def _fidelity_markers(req: AuditRequest) -> Dict[str, str]:
    return {
        "somatic": req.primitives.somatic.source,
        "hci": req.primitives.hci_source,
        "axioms": req.primitives.axioms.source,
    }


# ── Once-per-receipt coverage cache (Approach D wiring) ───────────────────────

_coverage_cache: Dict[str, Dict[str, Any]] = {}
_coverage_lock = threading.Lock()


def _coverage_key(req: AuditRequest) -> str:
    return f"{req.traceId}|{req.sessionVersion}"


def _get_coverage(req: AuditRequest) -> Dict[str, Any] | None:
    """Return operator_coverage for this receipt, computing it once per receipt.

    Thread-safe: first caller computes, subsequent callers in any thread read the
    cached result. Coverage hooks run once per receipt, not per operator.
    """
    key = _coverage_key(req)
    with _coverage_lock:
        if key in _coverage_cache:
            return _coverage_cache[key]
        try:
            coverage = record_coverage(
                req.primitives.model_dump(),
                req.llmOutput,
                {},  # auditResult not yet available; hooks read primitives + llmOutput
                req.traceId,
                req.sessionVersion,
            )
            _coverage_cache[key] = coverage
            return coverage
        except Exception:
            return None


def _clear_coverage_cache() -> None:
    """Clear the coverage cache. Useful for testing."""
    with _coverage_lock:
        _coverage_cache.clear()


def _persist(
    req: AuditRequest,
    operator: str,
    result: Dict[str, Any],
) -> None:
    try:
        store_audit_trace(req.traceId, req.sessionVersion, operator, result)
        coverage = _get_coverage(req)
        store_benchmark_fragment(
            req.traceId,
            req.sessionVersion,
            operator,
            req.primitives.model_dump(),
            req.llmOutput,
            result,
            operator_coverage=coverage,
        )
        # Task 19: persist CSM computation result (Seam 2 / JTBD-20).
        pair = {
            "traceId": req.traceId,
            "sessionVersion": req.sessionVersion,
            "operator": operator,
            "primitives": req.primitives.model_dump(),
            "llmOutput": req.llmOutput,
            "auditResult": result,
        }
        all_csm = compute_all_csm([pair])
        if all_csm:
            csm_row = all_csm[0]
            store_csm_result(
                trace_id=req.traceId,
                session_version=req.sessionVersion,
                operator=operator,
                csm=csm_row.get("csm", 0.0),
                alignment=csm_row.get("alignment", 0.0),
                delta_abs=csm_row.get("delta", 0.0),
                coherence_loss=csm_row.get("coherence_loss", 0.0),
                severity=csm_row.get("severity", 0.0),
                subtask_alignments=csm_row.get("subtask_alignments", {}),
                llm_output=req.llmOutput,
            )
    except Exception:
        pass  # persistence is best-effort; never break the endpoint


@app.post("/api/audit/sage", response_model=AuditResponse, response_model_exclude_none=True)
def sage_endpoint(req: AuditRequest) -> AuditResponse:
    fidelity = _fidelity_markers(req)
    result = run_sage(req.primitives.model_dump(), req.llmOutput, fidelity)
    _persist(req, "SAGE", result)
    return AuditResponse(**result)


@app.post("/api/audit/lab", response_model=AuditResponse, response_model_exclude_none=True)
def lab_endpoint(req: AuditRequest) -> AuditResponse:
    fidelity = _fidelity_markers(req)
    result = run_lab(req.primitives.model_dump(), req.llmOutput, fidelity)
    _persist(req, "LAB", result)
    return AuditResponse(**result)


@app.post("/api/audit/bar", response_model=AuditResponse, response_model_exclude_none=True)
def bar_endpoint(req: AuditRequest) -> AuditResponse:
    fidelity = _fidelity_markers(req)
    result = run_bar(req.primitives.model_dump(), req.llmOutput, fidelity)
    _persist(req, "BAR", result)
    return AuditResponse(**result)


@app.post("/api/audit/kintsugi", response_model=AuditResponse, response_model_exclude_none=True)
def kintsugi_endpoint(req: AuditRequest) -> AuditResponse:
    fidelity = _fidelity_markers(req)
    result = run_kintsugi(req.primitives.model_dump(), req.llmOutput, fidelity)
    _persist(req, "KINTSUGI", result)
    return AuditResponse(**result)


# ── Batch receipt endpoint (convenience — not yet used by the TS client) ─────

@app.post("/api/audit/receipt", response_model=CombinedAuditResponse, response_model_exclude_none=True)
def receipt_endpoint(req: AuditRequest) -> CombinedAuditResponse:
    t0 = time.time()
    fidelity = _fidelity_markers(req)
    primitives = req.primitives.model_dump()
    llm = req.llmOutput

    sage_result = run_sage(primitives, llm, fidelity)
    lab_result = run_lab(primitives, llm, fidelity)
    bar_result = run_bar(primitives, llm, fidelity)
    kintsugi_result = run_kintsugi(primitives, llm, fidelity)

    for op, res in [
        ("SAGE", sage_result),
        ("LAB", lab_result),
        ("BAR", bar_result),
        ("KINTSUGI", kintsugi_result),
    ]:
        _persist(req, op, res)

    any_failed = not (sage_result["ok"] and lab_result["ok"] and bar_result["ok"] and kintsugi_result["ok"])
    return CombinedAuditResponse(
        ok=any_failed is False,
        traceId=req.traceId,
        sessionVersion=req.sessionVersion,
        sage=AuditResponse(**sage_result) if sage_result else None,
        lab=AuditResponse(**lab_result) if lab_result else None,
        bar=AuditResponse(**bar_result) if bar_result else None,
        kintsugi=AuditResponse(**kintsugi_result) if kintsugi_result else None,
        totalLatencyMs=round((time.time() - t0) * 1000, 1),
        anyFailed=any_failed,
        failureReasons={
            op: str(res.get("failureReason") or "")
            for op, res in [
                ("SAGE", sage_result),
                ("LAB", lab_result),
                ("BAR", bar_result),
                ("KINTSUGI", kintsugi_result),
            ]
            if not res.get("ok") and res.get("failureReason")
        },
    )


# ── Startup log ──────────────────────────────────────────────────────────────

@app.on_event("startup")
def _startup() -> None:
    print(f"[audit_service] starting v{APP_VERSION} on port {PORT} — origins={ORIGINS}")
