# DEWY — Decision Evidence Weight Yield
# Crystallization log schema for ARCS v9
#
# RENAME NOTICE (ADR-010, 2026-05-27):
# This file was originally arcs_dewy.py. It was renamed to arcs_dewy_log.py to
# resolve a sys.path collision with the arcs_dewy/ package (formerly arcs-dewy/).
# DEWYLog / DEWYEntry live here. ReceiptObject lives in arcs_dewy/schema/receipt.py.

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class DEWYEntry:
    """One entry per CIS run — the crystallized evidence unit."""
    session_id:              str
    timestamp:               str               # ISO 8601
    question:                str
    nci:                     float
    gate_pass:               bool
    true_north:              str
    bullets:                 list[str]
    css_overall:             float             # CognitiveSafetyScore.overall
    trust_calibration_score: float
    on_purpose_label:        str               # DRIFT | RESONANCE | LOCK
    phase:                   int
    raw_receipt:             dict


@dataclass
class DEWYLog:
    """Full session crystallization log."""
    log_id:     str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    entries:    list[DEWYEntry] = field(default_factory=list)

    def append(self, entry: DEWYEntry) -> None:
        self.entries.append(entry)

    def to_json(self) -> str:
        d = {
            "log_id":     self.log_id,
            "created_at": self.created_at,
            "entries":    [asdict(e) for e in self.entries],
        }
        return json.dumps(d, indent=2)

    @classmethod
    def from_json(cls, s: str) -> DEWYLog:
        d = json.loads(s)
        entries = [DEWYEntry(**e) for e in d.get("entries", [])]
        return cls(
            log_id=d["log_id"],
            created_at=d["created_at"],
            entries=entries,
        )

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        if total == 0:
            return {
                "total_runs":           0,
                "avg_nci":              0.0,
                "gate_pass_rate":       0.0,
                "last_on_purpose_label": None,
            }
        return {
            "total_runs":            total,
            "avg_nci":               round(sum(e.nci for e in self.entries) / total, 2),
            "gate_pass_rate":        round(sum(1 for e in self.entries if e.gate_pass) / total, 2),
            "last_on_purpose_label": self.entries[-1].on_purpose_label,
        }


def create_dewy_log() -> DEWYLog:
    """Factory: create an empty DEWYLog."""
    return DEWYLog()


def entry_from_cis_result(result: dict) -> DEWYEntry:
    """
    Map the JSON output of `cli_arcs_run.py --json` to a DEWYEntry.

    Expected keys (from CISResponse.to_dict() piped through the CLI):
        session_id, question, nci_grade, gate_status, translated_signal,
        trust_calibration, css, phase (optional), raw_receipt (full dict).
    """
    gate_status = result.get("gate_status", "halt")
    nci = float(result.get("nci_grade", 0))
    css = float(result.get("css", 0.0))
    trust = float(result.get("trust_calibration", result.get("trust_calibration_score", 1.0)))

    # Derive on_purpose_label from signal strength
    if gate_status == "halt" or nci < 40:
        on_purpose_label = "DRIFT"
    elif nci >= 75 and gate_status == "pass":
        on_purpose_label = "LOCK"
    else:
        on_purpose_label = "RESONANCE"

    # Extract bullets from translated_signal if structured, else wrap as single item
    translated = result.get("translated_signal", "")
    raw_bullets = result.get("bullets", [])
    if not raw_bullets and translated:
        raw_bullets = [translated[:200]]

    return DEWYEntry(
        session_id=result.get("session_id", str(uuid.uuid4())),
        timestamp=datetime.now(timezone.utc).isoformat(),
        question=result.get("question", result.get("raw_signal", "")),
        nci=nci,
        gate_pass=(gate_status in ("pass", "warn")),
        true_north=result.get("true_north", result.get("jtbd", "")),
        bullets=raw_bullets,
        css_overall=css,
        trust_calibration_score=trust,
        on_purpose_label=on_purpose_label,
        phase=int(result.get("phase", 6)),
        raw_receipt=result,
    )
