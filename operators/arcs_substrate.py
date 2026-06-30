"""
ARCS substrate client — thin REST wrapper around GIGI.
ARCS owns the judgment semantics; GIGI is the persistence + retrieval engine.

Interface: query_template(macro, fiber_coords) → SubstrateResult
DB: ~/gigi/arcs.db  (managed by gigi-stream, port 3142)
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional
import urllib.request
import urllib.error
import json

from arcs_battery import get_battery_mode

GIGI_BASE = os.environ.get("GIGI_URL", "http://localhost:3142")
GIGI_API_KEY = os.environ.get("GIGI_API_KEY", "")

GapSignalType = Literal[
    "TRUE_UNDEFINED",
    "FUZZY_TRUTH",
    "INCOHERENT_RATIONALE",
    "UNDER_INSTRUMENTED",
]

RoutingPath = Literal["L1_match", "L2_partial", "L5_floor"]


@dataclass
class SubstrateResult:
    routing_path: RoutingPath
    template_id: Optional[str] = None
    skeleton: Optional[str] = None
    macro_family: Optional[str] = None
    holonomy_distance: float = 1.0
    confidence: float = 0.0
    provenance: Optional[str] = None
    gap_log_id: Optional[str] = None


@dataclass
class FiberCoords:
    stakes: str          # low | medium | high | existential
    horizon: str         # today | this-week | this-quarter | multi-year
    mode: str = "decide" # decide | explore | sense-check


def _gigi_post(path: str, body: dict) -> dict:
    url = f"{GIGI_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            **({"X-API-Key": GIGI_API_KEY} if GIGI_API_KEY else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError:
        return {"error": "gigi_unavailable"}


def _gigi_available() -> bool:
    try:
        req = urllib.request.Request(f"{GIGI_BASE}/v1/health", method="GET")
        with urllib.request.urlopen(req, timeout=2):
            return True
    except Exception:
        return False


def _fiber_distance(coords: FiberCoords, row: dict) -> float:
    """Compute normalized distance between query coords and a template row."""
    stakes_order = {"low": 0, "medium": 1, "high": 2, "existential": 3}
    horizon_order = {"today": 0, "this-week": 1, "this-quarter": 2, "multi-year": 3}

    s_q = stakes_order.get(coords.stakes, 1)
    s_r = stakes_order.get(row.get("stakes", "medium"), 1)
    h_q = horizon_order.get(coords.horizon, 1)
    h_r = horizon_order.get(row.get("horizon", "this-week"), 1)
    m_match = 0.0 if coords.mode == row.get("mode", "decide") else 0.5

    # L2 norm over 3 dimensions, max possible = sqrt(3^2 + 3^2 + 0.5^2) ≈ 4.3
    raw = ((s_q - s_r) ** 2 + (h_q - h_r) ** 2 + m_match**2) ** 0.5
    return min(raw / 4.3, 1.0)


def query_template(macro: str, coords: FiberCoords) -> SubstrateResult:
    """
    Query the ARCS template library (persisted via GIGI) for the best matching
    skeleton given macro family + fiber coordinates.

    Returns SubstrateResult with routing_path, holonomy_distance, confidence.
    On GIGI unavailability, LOW_POWER_SAFE, or L5 miss, returns L5_floor.
    """
    if get_battery_mode() == "LOW_POWER_SAFE":
        return SubstrateResult(routing_path="L5_floor")

    if not _gigi_available():
        return SubstrateResult(routing_path="L5_floor")

    resp = _gigi_post(
        "/v1/bundles/arcs_templates/query",
        {
            "conditions": [{"field": "macro_family", "op": "eq", "value": macro}],
            "limit": 50,
        },
    )

    rows = resp.get("data", [])
    if not rows:
        _write_gap_log(macro, coords, None, 1.0, "L5_floor", "TRUE_UNDEFINED")
        return SubstrateResult(routing_path="L5_floor")

    # Find nearest template by fiber distance
    best_row = min(rows, key=lambda r: _fiber_distance(coords, r))
    dist = _fiber_distance(coords, best_row)

    if dist < 0.2:
        routing_path: RoutingPath = "L1_match"
        confidence = 1.0 - dist
    elif dist < 0.5:
        routing_path = "L2_partial"
        confidence = 1.0 - dist
    else:
        _write_gap_log(macro, coords, best_row.get("template_id"), dist, "L5_floor", "TRUE_UNDEFINED")
        return SubstrateResult(routing_path="L5_floor", holonomy_distance=dist)

    return SubstrateResult(
        routing_path=routing_path,
        template_id=best_row.get("template_id"),
        skeleton=best_row.get("skeleton"),
        macro_family=best_row.get("macro_family"),
        holonomy_distance=dist,
        confidence=round(confidence, 3),
        provenance=best_row.get("source", "canonical"),
    )


def slot_fill(skeleton: str, slots: dict) -> str:
    """Fill {slot} placeholders in a skeleton string."""
    result = skeleton
    for key, value in slots.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def _write_gap_log(
    macro: str,
    coords: FiberCoords,
    nearest_template_id: Optional[str],
    holonomy_distance: float,
    fallback_used: str,
    gap_signal_type: GapSignalType,
    outcome: str = "pending",
    delta: str = "",
) -> str:
    """Append a row to the ARCS gap log (persisted via GIGI). Returns gap_log_id."""
    gap_id = str(uuid.uuid4())
    ts = int(datetime.now(timezone.utc).timestamp() * 1000)

    record = {
        "gap_id": gap_id,
        "macro_family_attempted": macro,
        "stakes": coords.stakes,
        "horizon": coords.horizon,
        "mode": coords.mode,
        "nearest_template_id": nearest_template_id or "",
        "holonomy_distance": holonomy_distance,
        "fallback_used": fallback_used,
        "gap_signal_type": gap_signal_type,
        "instrumentation_needed": int(gap_signal_type == "UNDER_INSTRUMENTED"),
        "incoherence_flag": int(gap_signal_type == "INCOHERENT_RATIONALE"),
        "outcome": outcome,
        "delta": delta,
        "ts": ts,
    }

    _gigi_post("/v1/bundles/arcs_gap_log/insert", {"records": [record]})
    return gap_id


def log_gap(
    macro: str,
    coords: FiberCoords,
    nearest_template_id: Optional[str],
    holonomy_distance: float,
    gap_signal_type: GapSignalType = "TRUE_UNDEFINED",
) -> str:
    """Public API for explicit gap logging from P3 seam swap."""
    return _write_gap_log(
        macro, coords, nearest_template_id, holonomy_distance, "L5_floor", gap_signal_type
    )
