"""
arcs_primitives_bridge.py
ARCS v9 — CoherenceReceipt → ReceiptObject migration bridge

Maps the Phase 2–6 `CoherenceReceipt` (arcs_primitives.py dataclass)
to the canonical DEWY v1 `ReceiptObject` (arcs_dewy/schema/receipt.py Pydantic model).

Use this when:
  - Feeding old receipts into arcs-worker/scanner/receipt_scanner.py
  - Running DEWY review on Phase 2–6 receipts
  - Normalizing JSON files with the old phase-receipt shape

Not a full fidelity mapping — some CoherenceReceipt fields have no ReceiptObject
equivalent (kinematic_summary, five_derivatives, somatic, hci_score, pci_score).
These are captured in `notes` as a structured string.

Design rule: lossless for the fields receipt_scanner.py needs:
  receipt_id, phase_id, artifacts, on_purpose, after_nci, sealed, cover_level
"""

from __future__ import annotations

import time
import uuid
from typing import Any

# ── Attempt live imports (may fail if packages not installed) ───────────────

try:
    from arcs_primitives import CoherenceReceipt  # type: ignore[import]
    _HAS_PRIMITIVES = True
except ImportError:
    _HAS_PRIMITIVES = False

try:
    # Resolved ADR-010: arcs_dewy.py (DEWYLog/DEWYEntry) renamed to arcs_dewy_log.py;
    # arcs-dewy/ package renamed to arcs_dewy/. Import now resolves correctly.
    from arcs_dewy.schema.receipt import (  # type: ignore[import]
        ReceiptObject,
        FATEDReasoning as DewyFATED,
        OnPurposeLabel,
        StakesLevel,
        DoorType,
    )
    _HAS_DEWY = True
except ImportError:
    _HAS_DEWY = False


# ── On-purpose label normalization ──────────────────────────────────────────

_ON_PURPOSE_MAP: dict[str, str] = {
    "aligned":               "aligned",
    "good_process_bad_luck": "good_process_bad_luck",
    "dumb":                  "dumb",
    "experimental":          "experimental",
    # legacy boolean → enum
    True:                    "aligned",
    False:                   "experimental",
}


def _normalize_on_purpose(value: Any) -> str:
    """Coerce bool or string on_purpose to OnPurposeLabel string."""
    return _ON_PURPOSE_MAP.get(value, "experimental")


# ── Phase receipt JSON → ReceiptObject dict ─────────────────────────────────
# (handles the old JSON shape from decision_receipt_phase2–7 files)

_OLD_PHASE_FIELD_MAP = {
    # old key          → new key (if different)
    "nci_self_grade":        "after_nci",
    "irreversibility_score": "irreversibility",
    "artifacts_shipped":     "artifacts",
    "on_purpose_label":      "on_purpose",
    "reasoning":             "_fated_block",  # special handling below
}


def phase_receipt_dict_to_receipt_object_dict(data: dict) -> dict:
    """
    Normalize an old-style phase receipt JSON dict to ReceiptObject field shape.

    Handles:
      - decision_receipt_phase2–6.json (before_signal / reasoning / on_purpose_label)
      - decision_receipt_phase7_d1*.json (transitional: phase_jtbd / gates_opened)

    Returns a plain dict that ReceiptObject(**result) will accept.
    """
    out: dict[str, Any] = {}

    # Pass-through fields that share names
    passthrough = {
        "receipt_id", "phase_id", "phase_name", "timestamp", "context",
        "irreversibility", "artifacts", "notes", "lenses_applied",
        "axioms_checked", "horizon", "expected_outcome", "review_by_date",
        "stages", "forces", "cover_level", "sealed", "dewy_stub_only",
    }
    for k in passthrough:
        if k in data:
            out[k] = data[k]

    # receipt_id: generate if missing
    if "receipt_id" not in out:
        out["receipt_id"] = data.get("receipt_id", f"migrated-{uuid.uuid4().hex[:8]}")

    # after_nci: prefer after_nci, fall back to nci_self_grade, then 0
    if "after_nci" in data:
        out["after_nci"] = float(data["after_nci"])
    elif "nci_self_grade" in data:
        out["after_nci"] = float(data["nci_self_grade"])
    else:
        out["after_nci"] = 0.0

    # before_nci: from before_signal.nci_score if present
    if "before_nci" in data:
        out["before_nci"] = float(data["before_nci"])
    elif isinstance(data.get("before_signal"), dict):
        out["before_nci"] = float(data["before_signal"].get("nci_score", 0.0))
    else:
        out["before_nci"] = 0.0

    # irreversibility: old field was irreversibility_score
    if "irreversibility" not in out:
        out["irreversibility"] = float(
            data.get("irreversibility_score", data.get("irreversibility", 0.5))
        )

    # on_purpose: old field was on_purpose_label (str)
    raw_op = data.get("on_purpose", data.get("on_purpose_label", "experimental"))
    out["on_purpose"] = _normalize_on_purpose(raw_op)

    # artifacts: old field was artifacts_shipped
    if "artifacts" not in out:
        out["artifacts"] = data.get("artifacts_shipped", [])

    # fated: old field was "reasoning" dict with facts/assumptions/tradeoffs/emotions/direction
    if "fated" not in out and isinstance(data.get("reasoning"), dict):
        out["fated"] = data["reasoning"]
    elif "fated" in data:
        out["fated"] = data["fated"]

    # phase_jtbd / gates_opened: transitional phase7 fields — fold into notes
    extra_notes: list[str] = []
    if "phase_jtbd" in data:
        extra_notes.append(f"phase_jtbd: {data['phase_jtbd']}")
    if "gates_opened" in data:
        extra_notes.append(f"gates_opened: {data['gates_opened']}")
    if extra_notes:
        existing_notes = out.get("notes", data.get("notes", ""))
        out["notes"] = (existing_notes + "\n" + "\n".join(extra_notes)).strip()

    # defaults
    out.setdefault("receipt_id",    f"migrated-{uuid.uuid4().hex[:8]}")
    out.setdefault("phase_id",      data.get("phase", "unknown"))
    out.setdefault("timestamp",     int(data.get("timestamp", time.time())))
    out.setdefault("sealed",        False)
    out.setdefault("cover_level",   "light")
    out.setdefault("dewy_stub_only", True)

    return out


def coherence_receipt_to_receipt_object_dict(cr: Any) -> dict:
    """
    Map a live CoherenceReceipt dataclass instance to a ReceiptObject-compatible dict.

    `cr` is typed as Any to avoid hard import dependency on arcs_primitives.
    All field access is via getattr with safe defaults.
    """
    def _g(field: str, default: Any = None) -> Any:
        return getattr(cr, field, default)

    # Capture lossy fields in notes so nothing is silently dropped
    lossy = {
        "operator":             _g("operator"),
        "signal_label":         _g("signal_label"),
        "kinematic_summary":    _g("kinematic_summary"),
        "five_derivatives":     _g("five_derivatives"),
        "hci_score":            _g("hci_score"),
        "pci_score":            _g("pci_score"),
        "signal_classification": _g("signal_classification"),
    }
    lossy_str = "; ".join(f"{k}={v}" for k, v in lossy.items() if v is not None)

    # FATED: CoherenceReceipt.fated is same shape (facts/assumptions/tradeoffs/emotions/direction)
    fated_obj = _g("fated")
    fated_dict: dict = {}
    if fated_obj is not None:
        fated_dict = {
            "facts":       getattr(fated_obj, "facts", ""),
            "assumptions": getattr(fated_obj, "assumptions", ""),
            "tradeoffs":   getattr(fated_obj, "tradeoffs", ""),
            "emotions":    getattr(fated_obj, "emotions", ""),
            "direction":   getattr(fated_obj, "direction", ""),
        }

    # axioms: CoherenceReceipt.axioms is AxiomCheck; fold to list[str]
    axioms_obj = _g("axioms")
    axioms_list: list[str] = []
    if axioms_obj is not None:
        for attr in ("clarity_before_curvature", "agency_over_automation",
                     "minimum_steps_to_coherence", "kairos_over_neuroticism"):
            val = getattr(axioms_obj, attr, None)
            if val is not None:
                axioms_list.append(f"{attr}: {val}")

    nci = float(_g("nci_score", 0.0))

    return {
        "receipt_id":      f"migrated-cr-{uuid.uuid4().hex[:8]}",
        "phase_id":        _g("phase_id", "unknown"),
        "phase_name":      "",
        "timestamp":       int(_g("timestamp", time.time())),
        "context":         _g("signal_label", ""),
        "before_nci":      nci,         # CoherenceReceipt has one NCI; mirror to both
        "after_nci":       nci,
        "on_purpose":      _normalize_on_purpose(_g("on_purpose_label", "experimental")),
        "irreversibility": float(_g("irreversibility", 0.5)),
        "fated":           fated_dict,
        "axioms_checked":  axioms_list,
        "artifacts":       list(_g("artifacts_shipped", []) or []),
        "notes":           (_g("notes", "") or "") + (f"\n[migrated from CoherenceReceipt: {lossy_str}]" if lossy_str else ""),
        "cover_level":     "light",
        "sealed":          False,
        "dewy_stub_only":  True,
        "lenses_applied":  [],
    }


# ── Convenience: try to build a live ReceiptObject if dewy is available ─────

def coherence_receipt_to_receipt_object(cr: Any) -> Any:
    """
    Return a ReceiptObject if arcs-dewy is installed, otherwise return the dict.
    Safe to call regardless of whether packages are installed.
    """
    d = coherence_receipt_to_receipt_object_dict(cr)
    if _HAS_DEWY:
        from arcs_dewy.schema.receipt import ReceiptObject  # type: ignore[import]
        return ReceiptObject(**d)
    return d


# ── Batch: normalize a JSON file from any known phase-receipt shape ──────────

def normalize_receipt_file(path: str) -> dict:
    """
    Read a JSON file and return a ReceiptObject-compatible dict.
    Handles old phase2–6 shape, transitional phase7 shape, and ReceiptObject shape.
    """
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict at root of {path}")

    # Already ReceiptObject shape: has both after_nci and receipt_id with no legacy fields
    is_new_shape = (
        "after_nci" in data
        and "receipt_id" in data
        and "before_signal" not in data
        and "nci_self_grade" not in data
    )
    if is_new_shape:
        return data

    return phase_receipt_dict_to_receipt_object_dict(data)
