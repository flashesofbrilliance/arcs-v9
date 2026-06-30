"""
arcs_operator_kairos.py
ARCS v9 — Kairos Operator (Gyroscopic Time Mode Detector)
Phase 7: TARGET — currently LAB/experimental

KAIROS: The Temporal Mode Gyroscope.
  Detects which time mode a signal is operating in and annotates
  the receipt before reasoning runs. Auto-modulates — no manual switching.

  Modes:
    CHRONOS    — linear execution; throughput, deadlines, sprint fidelity
    KAIROS     — high-coherence depth; belief updates, insight, identity synthesis
    DRIFT      — permissioned exploration; serendipity, pattern collision
    SANCTUARY  — restorative; not subject to throughput measurement
    WRITE_LOCK — commitment window; global serializability enforced (Yoav)

Role in pipeline:
  - Runs BEFORE SAGE (first lens after signal ingestion)
  - Annotates CoherenceSignal with detected time_mode + confidence
  - SAGE and downstream operators condition their reasoning on time_mode
  - Does NOT override human-set mode if one is present (Agency over Automation)

ROM candidacy gate:
  - Must produce NCI improvement over baseline (manual switching) across ≥50 receipts
  - Gyroscope vs. conductor A/B logged via feature flag KAIROS_GYROSCOPE_ENABLED
  - Promote to ROM only after FATED receipt with empirical evidence

NOTOMATION: Gyroscope proposes the mode. Human can override. System never silently coerces.

Status: STUB — interfaces locked, implementation pending Phase 7.
Decision receipt: decision_receipt_time_quality_attribution.json (2026-04-08)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from arcs_primitives import CoherenceSignal, CoherenceReceipt

KAIROS_VERSION = "v9.0-phase7-stub"

# ─────────────────────────────────────────────
# TIME MODES
# ─────────────────────────────────────────────

class TimeMode(str, Enum):
    CHRONOS    = "chronos"     # linear execution — throughput, deadlines
    KAIROS     = "kairos"      # high-coherence depth — insight, synthesis
    DRIFT      = "drift"       # permissioned exploration — serendipity
    SANCTUARY  = "sanctuary"   # restorative — not subject to clock metrics
    WRITE_LOCK = "write_lock"  # commitment window — Yoav serializability

# Jurisdiction: who owns the evaluation criteria for this block
class TimeJurisdiction(str, Enum):
    CLOCK     = "clock"      # throughput metrics apply
    COURT     = "court"      # human sign-off required before judgment
    HUMAN     = "human"      # human self-assessment only
    SANCTUARY = "sanctuary"  # no external evaluation permitted

# Gate type for this time block
class TimeGate(str, Enum):
    OPEN       = "open"        # proceed freely
    SOFT_PAUSE = "soft_pause"  # NCI check recommended
    HARD_STOP  = "hard_stop"   # must clear before proceeding

# ─────────────────────────────────────────────
# OUTPUT SCHEMA
# ─────────────────────────────────────────────

@dataclass
class KairosAnnotation:
    """
    Output of the Kairos operator. Attached to a CoherenceSignal before
    SAGE and downstream operators run.
    """
    detected_mode:    TimeMode
    confidence:       float                  # 0.0–1.0
    jurisdiction:     TimeJurisdiction
    gate:             TimeGate
    human_override:   Optional[TimeMode]     # None if human has not set a mode
    effective_mode:   TimeMode               # human_override if set, else detected_mode
    signals_used:     List[str]              # which signal features drove detection
    mode_rationale:   str                    # one-sentence explanation
    timestamp:        float = field(default_factory=time.time)
    operator_version: str   = KAIROS_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected_mode":  self.detected_mode.value,
            "confidence":     round(self.confidence, 3),
            "jurisdiction":   self.jurisdiction.value,
            "gate":           self.gate.value,
            "human_override": self.human_override.value if self.human_override else None,
            "effective_mode": self.effective_mode.value,
            "signals_used":   self.signals_used,
            "mode_rationale": self.mode_rationale,
            "timestamp":      self.timestamp,
            "operator_version": self.operator_version,
        }

# Feature flag lives here in Phase 7 once gyroscopic detection is implemented.
# Do not add it before the implementation exists — a flag with no behavior
# is a broken contract. See: decision_receipt_time_quality_attribution.json

# ─────────────────────────────────────────────
# KAIROS OPERATOR (STUB)
# ─────────────────────────────────────────────

class KairosOperator:
    """
    Gyroscopic time mode detector.

    Phase 7 implementation will infer TimeMode from:
      - Signal velocity + acceleration (from KinematicManifold)
      - NCI trajectory (rising = Kairos candidate; cliff = potential Write-Lock)
      - Irreversibility score (high irrev + low NCI → Write-Lock)
      - Receipt density in current session (many recent receipts → Chronos)
      - Time-since-last-action (long gap → Drift or Sanctuary)
      - Explicit Yoav commit in progress → Write-Lock

    Until Phase 7: returns CHRONOS as safe default with confidence 0.0
    so downstream operators are unaffected.
    """

    def __init__(self, human_mode: Optional[TimeMode] = None):
        """
        Args:
            human_mode: If set, bypasses gyroscope and uses human-specified mode.
                        Respects Agency over Automation at all times.
        """
        self.human_mode = human_mode

    def detect(
        self,
        signal: CoherenceSignal,
        receipt: Optional[CoherenceReceipt] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> KairosAnnotation:
        """
        Detect the time mode for this signal.

        If human_mode is set: annotate with override, skip detection.
        If gyroscope_enabled(): run detection logic (Phase 7).
        Otherwise: return CHRONOS default (safe, no pipeline impact).
        """
        # Agency over Automation — human override always wins
        if self.human_mode is not None:
            return KairosAnnotation(
                detected_mode  = self.human_mode,
                confidence     = 1.0,
                jurisdiction   = self._jurisdiction_for(self.human_mode),
                gate           = self._gate_for(self.human_mode, receipt),
                human_override = self.human_mode,
                effective_mode = self.human_mode,
                signals_used   = ["human_override"],
                mode_rationale = f"Human-specified mode: {self.human_mode.value}.",
            )

        # ── Phase 7: gyroscopic detection ──────────────────────────────────
        # Implement here. Inputs available:
        #   signal.signal, receipt.nci_score, receipt.irreversibility,
        #   session_context["receipts_this_session"],
        #   session_context["seconds_since_last_action"]
        # Until then: stub returns CHRONOS with confidence=0.0 (no pipeline impact).
        return KairosAnnotation(
            detected_mode  = TimeMode.CHRONOS,
            confidence     = 0.0,
            jurisdiction   = TimeJurisdiction.CLOCK,
            gate           = TimeGate.OPEN,
            human_override = None,
            effective_mode = TimeMode.CHRONOS,
            signals_used   = [],
            mode_rationale = "Gyroscopic detection not yet implemented (Phase 7 target).",
        )

    def _jurisdiction_for(self, mode: TimeMode) -> TimeJurisdiction:
        return {
            TimeMode.CHRONOS:    TimeJurisdiction.CLOCK,
            TimeMode.KAIROS:     TimeJurisdiction.HUMAN,
            TimeMode.DRIFT:      TimeJurisdiction.HUMAN,
            TimeMode.SANCTUARY:  TimeJurisdiction.SANCTUARY,
            TimeMode.WRITE_LOCK: TimeJurisdiction.COURT,
        }[mode]

    def _gate_for(self, mode: TimeMode, receipt: Optional[CoherenceReceipt]) -> TimeGate:
        if mode == TimeMode.WRITE_LOCK:
            return TimeGate.HARD_STOP
        if mode == TimeMode.SANCTUARY:
            return TimeGate.HARD_STOP  # no Clock metrics permitted
        if receipt and receipt.nci_score < 60:
            return TimeGate.SOFT_PAUSE
        return TimeGate.OPEN


# ─────────────────────────────────────────────
# CONVENIENCE
# ─────────────────────────────────────────────

def annotate_signal(
    signal: CoherenceSignal,
    human_mode: Optional[TimeMode] = None,
    receipt: Optional[CoherenceReceipt] = None,
    session_context: Optional[Dict[str, Any]] = None,
) -> KairosAnnotation:
    """Single-call convenience wrapper."""
    return KairosOperator(human_mode=human_mode).detect(signal, receipt, session_context)
