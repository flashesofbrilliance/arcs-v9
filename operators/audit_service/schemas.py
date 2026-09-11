"""
schemas.py — Pydantic models for the audit service contract.

Mirrors src/lib/audit-client.ts + audit-translator.ts so the TS client
and the Python service speak the same shape.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ── Primitives (what the TS client sends) ────────────────────────────────────

class SignalPrimitives(BaseModel):
    label: str = Field(..., max_length=300)
    domain: str = Field(default="decision", max_length=64)
    signalProxy: List[float] = Field(..., min_length=3, max_length=64)
    phaseId: str = Field(..., max_length=32)


class FatedPrimitives(BaseModel):
    facts: str = Field(default="", max_length=4000)
    assumptions: str = Field(default="", max_length=4000)
    tradeoffs: str = Field(default="", max_length=4000)
    emotions: str = Field(default="", max_length=4000)
    direction: str = Field(default="", max_length=4000)


class AxiomPrimitives(BaseModel):
    clarity_before_curvature: Literal["YES", "NO", "TENSION"]
    agency_over_automation: Literal["YES", "NO", "TENSION"]
    minimum_steps_to_coherence: Literal["YES", "NO", "TENSION"]
    kairos_over_neuroticism: Literal["YES", "NO", "TENSION"]
    source: Literal["llm_derived", "default"] = "default"


class SomaticPrimitives(BaseModel):
    phase_tuning: float = Field(ge=0.0, le=1.0)
    surge_detection: float = Field(ge=0.0, le=1.0)
    feels_right: float = Field(ge=0.0, le=1.0)
    that_vibes: float = Field(ge=0.0, le=1.0)
    locked_in: float = Field(ge=0.0, le=1.0)
    expected_vs_actual: float = Field(ge=0.0, le=1.0)
    source: Literal["default", "user_self_report"] = "default"


class FidelityMarkers(BaseModel):
    somatic: Literal["default", "user_self_report"]
    hci: Literal["proxy", "user_self_report"]
    axioms: Literal["llm_derived", "default"]


class OperatorPrimitives(BaseModel):
    signal: SignalPrimitives
    fated: FatedPrimitives = Field(default_factory=FatedPrimitives)
    axioms: AxiomPrimitives = Field(default_factory=lambda: AxiomPrimitives(
        clarity_before_curvature="TENSION",
        agency_over_automation="TENSION",
        minimum_steps_to_coherence="TENSION",
        kairos_over_neuroticism="TENSION",
        source="default",
    ))
    somatic: SomaticPrimitives = Field(default_factory=lambda: SomaticPrimitives(
        phase_tuning=0.55, surge_detection=0.50, feels_right=0.50,
        that_vibes=0.50, locked_in=0.55, expected_vs_actual=0.50, source="default",
    ))
    hci_score: float = Field(ge=0.0, le=100.0, default=50.0)
    hci_source: Literal["proxy", "user_self_report"] = "proxy"
    pci_score: float = Field(ge=0.0, le=100.0, default=50.0)
    irreversibility: float = Field(ge=0.0, le=1.0, default=0.3)
    onPurpose: bool = True
    nextAction: str = Field(default="", max_length=400)
    phaseId: str = Field(default="phase_1", max_length=32)
    signalClassification: Literal["strong_signal", "noise", "mixed", "decelerating"] = "mixed"


class AuditRequest(BaseModel):
    primitives: OperatorPrimitives
    llmOutput: Dict[str, Any] = Field(default_factory=dict)
    traceId: str = Field(..., min_length=1, max_length=128)
    sessionVersion: int = Field(default=1, ge=0)


# ── Responses ────────────────────────────────────────────────────────────────

class AuditResponse(BaseModel):
    ok: bool
    operator: str
    output: Dict[str, Any] = Field(default_factory=dict)
    primitivesSent: Dict[str, Any] = Field(default_factory=dict)
    latencyMs: float = 0.0
    fidelity: Dict[str, str] = Field(default_factory=lambda: {
        "somatic": "default", "hci": "proxy", "axioms": "default",
    })
    failureReason: Optional[str] = None


class HealthResponse(BaseModel):
    ok: bool
    operators: List[str]
    version: str


# ── Batch / combined response (nice-to-have, not used by the TS client yet) ─

class CombinedAuditResponse(BaseModel):
    ok: bool
    traceId: str
    sessionVersion: int
    sage: Optional[AuditResponse] = None
    lab: Optional[AuditResponse] = None
    bar: Optional[AuditResponse] = None
    kintsugi: Optional[AuditResponse] = None
    totalLatencyMs: float = 0.0
    anyFailed: bool = False
    failureReasons: Dict[str, str] = Field(default_factory=dict)
