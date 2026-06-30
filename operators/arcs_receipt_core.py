"""
ARCS v9 — receipt-core (Python)
Mirrors src/receipt/schema.ts. Single contract surface between Python orchestration
and TypeScript frontend: all cross-layer communication is representable as receipts.

ReceiptStore: append-only JSON log (SQLite adapter in Phase 8).
"""

from __future__ import annotations
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

# ── Types ─────────────────────────────────────────────────────────────────────

RoleEffect = Literal["force_multiplier", "randomizer", "mixed"]
TrustPosture = Literal["neutral", "trusted", "caution", "restricted"]
DriftType = Literal["none", "spin_cycle", "useful_tangent", "derailment"]
ListenerAction = Literal["signal_lock", "reframe", "escalate", "hold"]
DecisionMode = Literal["QUICKMOVE", "PLAN", "COURT"]
ClarityMode = Literal["SIMPLE", "RICH", "DEEP"]
DecisionType = Literal["quickmove", "phase_close", "cultivate", "court_escalation"]
Horizon = Literal["today", "this_week", "this_quarter", "one_to_three_years"]
Stakes = Literal["low", "medium", "high", "auto"]
Altitude = Literal["L0", "L1", "L2", "L3"]

# ── Sub-schemas ───────────────────────────────────────────────────────────────

@dataclass
class ClueResult:
    role_effect: RoleEffect
    trust_posture: TrustPosture
    signal_lock: bool
    drift_type: DriftType
    listener_action: ListenerAction
    confidence: float = 0.0      # 0–1

@dataclass
class RiskFactor:
    factor: str
    probability: float
    impact: Literal["low", "medium", "high"]
    mitigation: str

@dataclass
class Alternative:
    description: str
    ev_delta: float
    decision: Literal["selected", "rejected"]
    rejection_reason: Optional[str] = None

@dataclass
class Outcome:
    observed_at: Optional[str] = None
    result_summary: Optional[str] = None
    nci_delta: Optional[float] = None
    regret_score: Optional[float] = None
    prediction_accuracy: Optional[float] = None

# ── Core receipt ──────────────────────────────────────────────────────────────

@dataclass
class DecisionReceipt:
    # Identity
    receipt_id: str
    timestamp: str
    decision_maker_id: str

    # Context
    question: str
    horizon: Horizon
    stakes: Stakes
    altitude: Altitude
    domain: str
    energy_state: str
    tags: list[str]
    constraints: list[str]
    source_surface: str

    # Engine-derived
    mode: DecisionMode
    clarity_mode: ClarityMode
    decision_type: DecisionType
    irreversibility: float
    macros_used: list[str]

    # Prediction
    true_north: str
    why: list[str]               # ≤3 bullets
    confidence: float

    # Optional rich fields
    phase: Optional[str] = None
    session_id: Optional[str] = None
    alternatives_considered: list[Alternative] = field(default_factory=list)
    risk_factors: list[RiskFactor] = field(default_factory=list)
    clue_result: Optional[ClueResult] = None
    rationale: Optional[str] = None
    outcome: Optional[Outcome] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


def generate_receipt_id(prefix: str = "dr") -> str:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rand = uuid.uuid4().hex[:5].upper()
    return f"{prefix}-{date}-{rand}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ── ReceiptStore (append-only JSON log) ───────────────────────────────────────

class ReceiptStore:
    """
    Append-only receipt log. Defaults to ARCS_RECEIPT_PATH env var or
    ~/.arcs/receipts.jsonl. SQLite adapter in Phase 8.
    """

    DEFAULT_PATH = Path.home() / ".arcs" / "receipts.jsonl"

    def __init__(self, path: Optional[str | Path] = None) -> None:
        self.path = Path(path or os.getenv("ARCS_RECEIPT_PATH", self.DEFAULT_PATH))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, receipt: DecisionReceipt) -> str:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(receipt.to_dict(), default=str) + "\n")
        return receipt.receipt_id

    def read(self, receipt_id: str) -> Optional[DecisionReceipt]:
        if not self.path.exists():
            return None
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                raw = json.loads(line)
                if raw.get("receipt_id") == receipt_id:
                    return self._from_dict(raw)
        return None

    def list(
        self,
        phase: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 100,
    ) -> list[DecisionReceipt]:
        if not self.path.exists():
            return []
        results = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                raw = json.loads(line)
                if phase and raw.get("phase") != phase:
                    continue
                if domain and raw.get("domain") != domain:
                    continue
                results.append(self._from_dict(raw))
                if len(results) >= limit:
                    break
        return results

    def update(self, receipt_id: str, patch: dict[str, Any]) -> None:
        """Rewrite log with the patched receipt (append-only semantics preserved via tombstone)."""
        existing = self.read(receipt_id)
        if existing is None:
            raise KeyError(f"Receipt {receipt_id} not found")
        updated = {**existing.to_dict(), **patch, "receipt_id": receipt_id}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(updated, default=str) + "\n")

    @staticmethod
    def _from_dict(raw: dict[str, Any]) -> DecisionReceipt:
        clue_raw = raw.pop("clue_result", None)
        clue = None
        if clue_raw:
            al = clue_raw.get("active_listening", {})
            clue = ClueResult(
                role_effect=clue_raw["role_effect"],
                trust_posture=clue_raw["trust_posture"],
                signal_lock=al.get("signal_lock", False),
                drift_type=al.get("drift_type", "none"),
                listener_action=al.get("listener_action", "hold"),
                confidence=clue_raw.get("confidence", 0.0),
            )
        alts = [Alternative(**a) for a in raw.pop("alternatives_considered", [])]
        risks = [RiskFactor(**r) for r in raw.pop("risk_factors", [])]
        outcome_raw = raw.pop("outcome", None)
        outcome = Outcome(**outcome_raw) if outcome_raw else None

        return DecisionReceipt(
            **{k: v for k, v in raw.items() if k not in ("clue_result",)},
            clue_result=clue,
            alternatives_considered=alts,
            risk_factors=risks,
            outcome=outcome,
        )


# ── Module-level default store ────────────────────────────────────────────────

_default_store: Optional[ReceiptStore] = None

def get_store() -> ReceiptStore:
    global _default_store
    if _default_store is None:
        _default_store = ReceiptStore()
    return _default_store
