"""persistence.py — append-only audit trail + benchmark fragments.

Two JSONL files:
  - audit_traces.jsonl  — one row per (traceId, operator) audit result
  - benchmark_pairs.jsonl — one row per (traceId, operator) fragment:
      primitives + llmOutput + that operator's auditResult
These are the source for the with/without-audit efficacy study and the
Path A → Path B evidence review.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent
_LOCK = threading.Lock()

_BENCH_FILE = Path(os.environ.get("AUDIT_BENCH_FILE", str(_HERE / "benchmark_pairs.jsonl")))
_TRACE_FILE = Path(os.environ.get("AUDIT_TRACE_FILE", str(_HERE / "audit_traces.jsonl")))

# Sampling: if AUDIT_SAMPLE_RATE is set to a float in (0, 1], only that fraction
# of traces are persisted. "all" or unset → persist everything.
_SAMPLE_RATE: float | None = None


def _parse_sample_rate() -> float | None:
    val = os.environ.get("AUDIT_SAMPLE_RATE", "").strip().lower()
    if val in ("", "all"):
        return None  # persist everything
    try:
        rate = float(val)
        if rate <= 0.0 or rate > 1.0:
            raise ValueError
        return rate
    except (ValueError, TypeError):
        # malformed → treat as "all" rather than silent-dropping everything
        return None


def _should_sample(trace_id: str) -> bool:
    """Return True if this trace should be sampled in (persist it).

    Deterministic per trace_id via hash, so the same trace always gets the
    same decision regardless of when it's written.
    """
    global _SAMPLE_RATE
    if _SAMPLE_RATE is None:
        _SAMPLE_RATE = _parse_sample_rate()
    if _SAMPLE_RATE is None:
        return True
    # hash the trace_id to a 0..1 float
    h = int(hashlib.sha256(trace_id.encode()).hexdigest(), 16)
    return (h % 1_000_000) / 1_000_000.0 < _SAMPLE_RATE


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def store_audit_trace(
    trace_id: str,
    session_version: int,
    operator: str,
    result: Dict[str, Any],
) -> None:
    """Append one audit result row. Sampling-gated by AUDIT_SAMPLE_RATE.

    Never raises — persistence is best-effort.
    """
    if not _should_sample(trace_id):
        return
    try:
        _ensure_parent(_TRACE_FILE)
        row = {
            "traceId": trace_id,
            "sessionVersion": session_version,
            "operator": operator,
            "timestamp": _now_iso(),
            "result": result,
        }
        with _LOCK, open(_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception:
        pass


def store_benchmark_fragment(
    trace_id: str,
    session_version: int,
    operator: str,
    primitives: Dict[str, Any],
    llm_output: Dict[str, Any],
    audit_result: Dict[str, Any],
) -> None:
    """Append one benchmark fragment. Sampling-gated by AUDIT_SAMPLE_RATE.

    Never raises.
    """
    if not _should_sample(trace_id):
        return
    try:
        _ensure_parent(_BENCH_FILE)
        row = {
            "traceId": trace_id,
            "sessionVersion": session_version,
            "operator": operator,
            "timestamp": _now_iso(),
            "primitives": primitives,
            "llmOutput": llm_output,
            "auditResult": audit_result,
        }
        with _LOCK, open(_BENCH_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception:
        pass


def clear_store() -> None:
    """Delete both JSONL files. Useful for local reset between test runs."""
    for path in (_BENCH_FILE, _TRACE_FILE):
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass


# ── Read APIs (Phase 1) ──────────────────────────────────────────────────────


def _read_jsonl(path: Path, limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
    """Read up to `limit` rows from a JSONL file, skipping `offset` rows.
    Never raises — returns empty list on any failure."""
    try:
        if not path.exists():
            return []
        rows: list[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for _ in range(offset):
                line = f.readline()
                if not line:
                    break
            for line in f:
                if len(rows) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows
    except Exception:
        return []


def loadBenchmarkPairs(
    trace_id: str | None = None,
    operator: str | None = None,
    fidelity_somatic: str | None = None,
    fidelity_hci: str | None = None,
    fidelity_axioms: str | None = None,
    before: str | None = None,
    after: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Dict[str, Any]]:
    """Load benchmark pairs filtered by optional criteria.

    Returns list of benchmark pair dicts (traceId, sessionVersion, operator,
    timestamp, primitives, llmOutput, auditResult).

    Filter semantics:
      - trace_id / operator: exact match (None = don't filter)
      - fidelity_*: matches the corresponding fidelity.source value
      - before / after: ISO timestamp bounds on the row timestamp (inclusive)
      - limit / offset: pagination (default 100, offset 0)
    """
    rows = _read_jsonl(_BENCH_FILE, limit=1000, offset=offset)
    filtered: list[Dict[str, Any]] = []
    for row in rows:
        if trace_id is not None and row.get("traceId") != trace_id:
            continue
        if operator is not None and row.get("operator") != operator:
            continue
        result = row.get("auditResult") or {}
        fidelity = result.get("fidelity") or {}
        if fidelity_somatic is not None and fidelity.get("somatic") != fidelity_somatic:
            continue
        if fidelity_hci is not None and fidelity.get("hci") != fidelity_hci:
            continue
        if fidelity_axioms is not None and fidelity.get("axioms") != fidelity_axioms:
            continue
        ts = row.get("timestamp") or ""
        if before is not None and ts > before:
            continue
        if after is not None and ts < after:
            continue
        filtered.append(row)
    return filtered[:limit]


def loadAuditTracesPage(
    trace_id: str | None = None,
    operator: str | None = None,
    before: str | None = None,
    after: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Dict[str, Any]]:
    """Load audit traces page filtered by optional criteria.

    Returns list of audit trace dicts (traceId, sessionVersion, operator,
    timestamp, result).

    Filter semantics:
      - trace_id / operator: exact match (None = don't filter)
      - before / after: ISO timestamp bounds on the row timestamp (inclusive)
      - limit / offset: pagination (default 100, offset 0)
    """
    rows = _read_jsonl(_TRACE_FILE, limit=1000, offset=offset)
    filtered: list[Dict[str, Any]] = []
    for row in rows:
        if trace_id is not None and row.get("traceId") != trace_id:
            continue
        if operator is not None and row.get("operator") != operator:
            continue
        ts = row.get("timestamp") or ""
        if before is not None and ts > before:
            continue
        if after is not None and ts < after:
            continue
        filtered.append(row)
    return filtered[:limit]


def audit_store_stats() -> Dict[str, Any]:
    """Quick stats on both stores — useful for monitoring and the review cadence."""
    bench = _read_jsonl(_BENCH_FILE, limit=10000)
    trace = _read_jsonl(_TRACE_FILE, limit=10000)
    bench_by_operator: Dict[str, int] = {}
    trace_by_operator: Dict[str, int] = {}
    bench_by_fidelity: Dict[str, int] = {}
    for row in bench:
        op = row.get("operator") or "unknown"
        bench_by_operator[op] = bench_by_operator.get(op, 0) + 1
        fidelity = (row.get("auditResult") or {}).get("fidelity") or {}
        key = f"{fidelity.get('somatic','?')}/{fidelity.get('hci','?')}/{fidelity.get('axioms','?')}"
        bench_by_fidelity[key] = bench_by_fidelity.get(key, 0) + 1
    for row in trace:
        op = row.get("operator") or "unknown"
        trace_by_operator[op] = trace_by_operator.get(op, 0) + 1
    sample_rate = _parse_sample_rate()
    return {
        "bench_rows": len(bench),
        "trace_rows": len(trace),
        "bench_by_operator": bench_by_operator,
        "trace_by_operator": trace_by_operator,
        "bench_by_fidelity": bench_by_fidelity,
        "sample_rate": sample_rate,
    }
