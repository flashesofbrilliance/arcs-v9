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
    operator_coverage: Dict[str, Any] | None = None,
) -> None:
    """Append one benchmark fragment. Sampling-gated by AUDIT_SAMPLE_RATE.

    Never raises.
    """
    if not _should_sample(trace_id):
        return
    try:
        _ensure_parent(_BENCH_FILE)
        row: Dict[str, Any] = {
            "traceId": trace_id,
            "sessionVersion": session_version,
            "operator": operator,
            "timestamp": _now_iso(),
            "primitives": primitives,
            "llmOutput": llm_output,
            "auditResult": audit_result,
        }
        if operator_coverage is not None:
            row["operator_coverage"] = operator_coverage
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


# ── CSM computation (Phase 2-3) ───────────────────────────────────────────────
# CSM = ALIGNMENT(operator_output, llm_output) × 0.40
#     + (1 − ΔABS) × 0.30
#     + (1 − COHERENCE_LOSS) × 0.20
#     + (1 − SEVERITY) × 0.10
#
# Per-operator subtask maps define which fields map to which of 5 subtasks.
# Each subtask alignment_i = 1 − normalized_distance(op_i, llm_i).
#
# Alignment normalizes per-subtask kind:
#   continuous[rng]   → 1 − |a−b|/max_range
#   categorical       → 1.0 if exact match, else 0.0
#   ordered[list]     → 1 − |pos_a−pos_b|/(len−1)
#   binary            → 1.0 if both same, else 0.0
#   count_proxy       → 1 − |a−b|/max(|a|,|b|,1)
#   text_proxy        → 1 − |a−b|/max(|a|,|b|,1)  (count proxy for text)
#
# Per-operator variants (from CSM-spec.md §5):
#   SAGE:   ΔABS=0 (not defined), coherence_loss=|1−alignment_score/max(llm_coherence_pct,1)|, severity=coherence_loss scaled
#   LAB:    ΔABS=1 if advisor_direction_and_delta, coherence_loss=|1−bayesian_posterior|, severity=ltl+hidden_assumptions+worst_case
#   BAR:    ΔABS=1 if bar_verdict_and_asymmetry_delta, coherence_loss=0 (by design), severity=bar_verdict+asymmetry+ruin
#   KINTSUGI: ΔABS=0, coherence_loss=0 (by design), severity=golden_seams+repair_count+pathogen_severity
# ──────────────────────────────────────────────────────────────────────────────

_SAGE_SUBTASKS: Dict[str, tuple] = {
    "nci_score":            ("nci_score",                  "nci_score",                  "continuous", [0, 100]),
    "coherence_pct":        ("coherence_pct",              "coherence_pct",              "continuous", [0, 100]),
    "signal_classification": ("signal_classification",      "signalClassification",       "categorical", None),
    "axiom_alignment":      ("axioms.alignment_score",     "axioms.alignment_score",     "continuous", [0, 1]),
    "court":                ("verdict",                    "reasoning.court",            "categorical", None),
}

_LAB_SUBTASKS: Dict[str, tuple] = {
    "loki_threat":          ("loki_threat_level",           "loki_threat_level",          "ordered", ["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    "bayesian_posterior":   ("bayesian_posterior",         "bayesian_posterior",         "continuous", [0, 1]),
    "advisor_consensus":    ("advisor_consensus",           "advisor_consensus",           "ordered", ["ABORT", "PROCEED", "REVIEW"]),
    "hidden_assumptions":   ("loki.hidden_assumptions",     "hidden_assumptions",          "count_proxy", None),
    "worst_case":           ("loki.worst_case_scenario",    "worst_case_scenario",         "text_proxy", None),
}

_BAR_SUBTASKS: Dict[str, tuple] = {
    "bar_verdict":          ("bar_verdict",                 "bar_verdict",                 "ordered", ["PASS", "CAUTION", "RUIN_RISK"]),
    "floor_nci":            ("baseline.floor_nci",          "baseline.floor_nci",          "continuous", [0, 100]),
    "asymmetry_ratio":      ("asymmetry.asymmetry_ratio",   "asymmetry.asymmetry_ratio",   "continuous", [0, 1]),
    "ruin_detected":        ("ruin_detected",               "ruin_detected",               "binary", None),
    "recovery_path":        ("baseline.recovery_path",      "recovery_path",               "text_proxy", None),
}

_KINTSUGI_SUBTASKS: Dict[str, tuple] = {
    "is_healthy":           ("is_healthy",                  "is_healthy",                  "binary", None),
    "pathogen_count":       ("pathogens",                   "pathogens",                   "count_proxy", None),
    "trust_discount":       ("kintsugi_trust_discount",     "kintsugi_trust_discount",     "continuous", [0, 1]),
    "repair_count":         ("kintsugi_repair_count",       "kintsugi_repair_count",       "count_proxy", None),
    "severity_max":         ("pathogens",                   "pathogens",                   "ordered", ["LOW", "MEDIUM", "HIGH"]),
}

def _extract_field(obj: Dict[str, Any], path: str):
    """Extract a dotted field path from a nested dict. Returns (value, found)."""
    parts = path.split(".")
    cur: Any = obj
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return (None, False)
        cur = cur[p]
    return (cur, True)

def _aligned(op_val: Any, llm_val: Any, kind: str, rng: "list | None") -> float:
    """Single subtask alignment: 1 − normalized_distance(op, llm).
    If either side missing → 0 (no evidence of agreement).
    """
    if llm_val is None or llm_val == {} or llm_val == []:
        return 0.0
    if op_val is None:
        return 0.0
    if kind == "continuous":
        if rng is None:
            return 0.0
        lo, hi = rng
        span = max(hi - lo, 1e-9)
        try:
            return max(0.0, min(1.0, 1.0 - abs(float(op_val) - float(llm_val)) / span))
        except (TypeError, ValueError):
            return 0.0
    if kind == "categorical":
        return 1.0 if str(op_val) == str(llm_val) else 0.0
    if kind == "ordered":
        order = {str(v): i for i, v in enumerate(rng or [])}
        oi = order.get(str(op_val))
        li = order.get(str(llm_val))
        if oi is None or li is None or not rng:
            return 0.0
        span = max(len(rng) - 1, 1)
        return max(0.0, min(1.0, 1.0 - abs(oi - li) / span))
    if kind == "binary":
        return 1.0 if bool(op_val) == bool(llm_val) else 0.0
    if kind in ("count", "count_proxy", "text_proxy"):
        try:
            oi = float(op_val) if op_val is not None else 0.0
            li = float(llm_val) if llm_val is not None else 0.0
        except (TypeError, ValueError):
            return 0.0
        span = max(abs(oi), abs(li), 1.0)
        return max(0.0, min(1.0, 1.0 - abs(oi - li) / span))
    return 0.0

def _alignments(pair: Dict[str, Any], operator: str | None) -> Dict[str, float]:
    """Return per-subtask alignment dict for one operator on one pair."""
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    if operator is None or operator == "UNKNOWN":
        operator = pair.get("operator") or "UNKNOWN"
    if operator == "SAGE":
        tasks = _SAGE_SUBTASKS
    elif operator == "LAB":
        tasks = _LAB_SUBTASKS
    elif operator == "BAR":
        tasks = _BAR_SUBTASKS
    elif operator == "KINTSUGI":
        tasks = _KINTSUGI_SUBTASKS
    else:
        return {}
    result: Dict[str, float] = {}
    for name, (op_path, llm_path, kind, rng) in tasks.items():
        ov, _ = _extract_field(ar, op_path)
        lv, _ = _extract_field(ll, llm_path)
        result[name] = _aligned(ov, lv, kind, rng)
    return result

def _delta_abs(pair: Dict[str, Any], operator: str | None) -> float:
    """Tokenized change magnitude ΔABS ∈ {0, 1}.
    1 if advisor direction agrees AND continuous delta crosses 0.30.
    0 otherwise (no evidence of change).
    SAGE and KINTSUGI have no ΔABS defined → 0.
    """
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    if operator is None or operator == "UNKNOWN":
        operator = pair.get("operator") or "UNKNOWN"
    if operator == "LAB":
        ltl_op, _ = _extract_field(ar, "loki_threat_level")
        ltl_llm, _ = _extract_field(ll, "loki_threat_level")
        bp_op, _ = _extract_field(ar, "bayesian_posterior")
        bp_llm, _ = _extract_field(ll, "bayesian_posterior")
        if ltl_op and ltl_llm and bp_op is not None and bp_llm is not None:
            direction = str(ltl_op) == str(ltl_llm)
            delta = abs(float(bp_op) - float(bp_llm))
            return 1.0 if direction and delta > 0.30 else 0.0
        return 0.0
    if operator == "BAR":
        bv_op, _ = _extract_field(ar, "bar_verdict")
        bv_llm, _ = _extract_field(ll, "bar_verdict")
        ar_op, _ = _extract_field(ar, "asymmetry.asymmetry_ratio")
        ar_llm, _ = _extract_field(ll, "asymmetry.asymmetry_ratio")
        if bv_op and bv_llm and ar_op is not None and ar_llm is not None:
            direction = str(bv_op) == str(bv_llm)
            delta = abs(float(ar_op) - float(ar_llm))
            return 1.0 if direction and delta > 0.30 else 0.0
        return 0.0
    return 0.0

def _coherence_loss(pair: Dict[str, Any], operator: str | None) -> float:
    """Per-operator coherence loss (from CSM-spec.md §5).
    SAGE: |1 − (coherence_law_score / max(llm_coherence_pct, 1))|
    LAB:  |1 − bayesian_posterior|
    BAR:  0 (by design — no coherence-loss concept)
    KINTSUGI: 0 (by design — no coherence-loss concept)
    """
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    if operator is None or operator == "UNKNOWN":
        operator = pair.get("operator") or "UNKNOWN"
    if operator == "SAGE":
        cls_op, _ = _extract_field(ar, "axioms.alignment_score")
        cls_llm, _ = _extract_field(ll, "coherence_pct")
        if cls_op is not None and cls_llm is not None and float(cls_llm) > 0:
            return abs(1.0 - float(cls_op) / max(float(cls_llm), 1.0))
        return 0.5  # no evidence → moderate loss
    if operator == "LAB":
        bp_op, _ = _extract_field(ar, "bayesian_posterior")
        bp_llm, _ = _extract_field(ll, "bayesian_posterior")
        if bp_op is not None and bp_llm is not None:
            return abs(1.0 - float(bp_op) / max(float(bp_llm), 1e-9))
        return 0.5
    return 0.0  # BAR, KINTSUGI: 0 by design

def _severity(pair: Dict[str, Any], operator: str | None) -> float:
    """Per-operator severity ∈ [0, 1] (from CSM-spec.md §5).
    Components: GATE_VIOLATION (0.40) + STRUCTURE_WEIGHT (0.35) + REPAIR_NEEDED_LATE (0.25).
    """
    ar = (pair.get("auditResult") or {}).get("output") or {}
    if operator is None or operator == "UNKNOWN":
        operator = pair.get("operator") or "UNKNOWN"
    if operator == "SAGE":
        cl = _coherence_loss(pair, "SAGE")
        return min(1.0, cl * 1.5)  # scale: 0.5 cl → 0.75 severity
    if operator == "LAB":
        ltl, _ = _extract_field(ar, "loki_threat_level")
        ltl_w = {"CRITICAL": 1.0, "HIGH": 0.7, "MEDIUM": 0.4, "LOW": 0.1}.get(str(ltl), 0.0) * 0.40
        ha, _ = _extract_field(ar, "loki.hidden_assumptions")
        ha_count = len(ha) if isinstance(ha, (list, tuple)) else (1 if ha else 0)
        ha_w = (ha_count / 5.0) * 0.35
        wc, _ = _extract_field(ar, "loki.worst_case_scenario")
        wc_w = 0.25 if wc else 0.0
        return min(1.0, ltl_w + ha_w + wc_w)
    if operator == "BAR":
        bv, _ = _extract_field(ar, "bar_verdict")
        bv_w = {"RUIN_RISK": 1.0, "CAUTION": 0.5, "PASS": 0.0}.get(str(bv), 0.0) * 0.40
        ar_val, _ = _extract_field(ar, "asymmetry.asymmetry_ratio")
        ar_w = (float(ar_val) if ar_val is not None else 0.0) * 0.35
        rd, _ = _extract_field(ar, "ruin_detected")
        rd_w = 0.25 if rd else 0.0
        return min(1.0, bv_w + ar_w + rd_w)
    if operator == "KINTSUGI":
        gh, _ = _extract_field(ar, "golden_seams")
        gh_count = len(gh) if isinstance(gh, (list, tuple)) else (1 if gh else 0)
        gh_w = (gh_count / 3.0) * 0.40
        rc, _ = _extract_field(ar, "kintsugi_repair_count")
        rc_w = (float(rc) / 3.0 if rc is not None else 0.0) * 0.35
        ps, _ = _extract_field(ar, "pathogens.severity")
        if isinstance(ps, list) and len(ps) > 0:
            sev_map: Dict[str, float] = {"HIGH": 0.25, "MEDIUM": 0.15, "LOW": 0.05}
            ps_w = max(sev_map.get(str(s), 0.0) for s in ps)
        else:
            ps_w = {"HIGH": 0.25, "MEDIUM": 0.15, "LOW": 0.05}.get(str(ps), 0.0)
        return min(1.0, gh_w + rc_w + ps_w)
    return 0.5

def compute_csm(pair: Dict[str, Any], operator: str | None = None) -> float:
    """Compute unweighted CSM for one pair on one operator.
    CSM = ALIGNMENT × 0.40 + (1 − ΔABS) × 0.30 + (1 − COHERENCE_LOSS) × 0.20 + (1 − SEVERITY) × 0.10
    If operator is None, use the pair's own operator.
    Returns float in [0, 1].
    """
    if operator is None or operator == "UNKNOWN":
        operator = pair.get("operator") or "UNKNOWN"
    al = _alignments(pair, operator)
    if not al:
        return 0.0
    alignment = sum(al.values()) / len(al)
    delta = _delta_abs(pair, operator)
    coherence_loss = _coherence_loss(pair, operator)
    severity = _severity(pair, operator)
    csm = alignment * 0.40 + (1.0 - delta) * 0.30 + (1.0 - coherence_loss) * 0.20 + (1.0 - severity) * 0.10
    return max(0.0, min(1.0, csm))

def compute_all_csm(pairs: list) -> list:
    """Compute CSM for all pairs, all operators.
    Returns list of dicts: traceId, operator, csm, alignment, delta, coherence_loss, severity, subtask_alignments.
    """
    result: list = []
    for pair in pairs:
        op = pair.get("operator") or "UNKNOWN"
        csm = compute_csm(pair, op)
        al = _alignments(pair, op)
        result.append({
            "traceId": pair.get("traceId"),
            "operator": op,
            "csm": csm,
            "alignment": sum(al.values()) / max(len(al), 1),
            "delta": _delta_abs(pair, op),
            "coherence_loss": _coherence_loss(pair, op),
            "severity": _severity(pair, op),
            "subtask_alignments": al,
        })
    return result

# ── Fidelity weighting (from CSM-spec.md §4 + manifest E5) ────────────────────
# WEIGHTS = {somatic: {user_self_report: 1.0, default: 0.3},
#            hci:     {user_self_report: 1.0, proxy: 0.4},
#            axioms:  {llm_derived: 0.6, default: 0.3}}
# fidelity_weight = WEIGHTS.somatic[src] × WEIGHTS.hci[src] × WEIGHTS.axioms[src]
# Provisional — unvalidated until who-was-right data accumulates.

_WEIGHTS: Dict[str, Dict[str, float]] = {
    "somatic": {"user_self_report": 1.0, "default": 0.3},
    "hci":     {"user_self_report": 1.0, "proxy": 0.4},
    "axioms":  {"llm_derived": 0.6, "default": 0.3},
}

def fidelity_weight(pair: Dict[str, Any]) -> float:
    """Per-pair fidelity weight ∈ [0, 1].
    fidelity_weight = s × h × a where s/h/a are the per-source weights.
    """
    f = ((pair.get("auditResult") or {}).get("fidelity") or {})
    sw = _WEIGHTS["somatic"].get(f.get("somatic", "default"), 0.3)
    hw = _WEIGHTS["hci"].get(f.get("hci", "proxy"), 0.4)
    aw = _WEIGHTS["axioms"].get(f.get("axioms", "default"), 0.3)
    w = sw * hw * aw
    return max(0.0, min(1.0, w))

def weighted_csm(pairs: list) -> float:
    """Weighted CSM aggregate across all pairs.
    weighted_csm = Σ(CSM_i × w_i) / Σ(w_i)   (if Σw > 0, else 0)
    """
    if not pairs:
        return 0.0
    total_w = 0.0
    total_csm_w = 0.0
    for pair in pairs:
        w = fidelity_weight(pair)
        c = compute_csm(pair)
        total_w += w
        total_csm_w += c * w
    if total_w <= 0.0:
        return 0.0
    return total_csm_w / total_w

def weighted_csm_by_operator(pairs: list) -> Dict[str, float]:
    """Per-operator weighted CSM aggregate.
    Returns {operator: weighted_csm} for each operator present.
    """
    acc: Dict[str, Dict[str, float]] = {}
    for pair in pairs:
        op = pair.get("operator") or "UNKNOWN"
        w = fidelity_weight(pair)
        c = compute_csm(pair, op)
        if op not in acc:
            acc[op] = {"w": 0.0, "cw": 0.0}
        acc[op]["w"] += w
        acc[op]["cw"] += c * w
    result: Dict[str, float] = {}
    for op, v in acc.items():
        result[op] = (v["cw"] / v["w"]) if v["w"] > 0 else 0.0
    return result

def print_weighted_store():
    """Print the instrument's weighted sound board to stdout."""
    pairs = loadBenchmarkPairs(limit=1000)
    print("=" * 72)
    print("  ARCS v9 OPERATOR AUDIT — WEIGHTED CSM SOUND BOARD")
    print("=" * 72)
    print(f"  Store: {_BENCH_FILE}  ({len(pairs)} pairs)")
    print()
    # Per-pair table
    print("  ── Per-pair CSM + fidelity weight ──")
    hdr = f"  {'traceId':<6} {'op':<11} {'CSM':>6} {'w':>6} {'adjudication':<28} {'llm?':>5}"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for pair in pairs:
        op = pair.get("operator") or "?"
        csm = compute_csm(pair, op)
        w = fidelity_weight(pair)
        adj = ((pair.get("auditResult") or {}).get("adjudication") or None)
        if adj:
            adj_str = f"{adj.get('who_was_right','-')}/{adj.get('unresolved',False)}"
        else:
            adj_str = "— (no adjudication)"
        ll = pair.get("llmOutput") or {}
        ll_has = "YES" if (ll.get("nci_score") is not None or ll.get("coherence_pct") is not None) else "no"
        print(f"  {pair.get('traceId','?'):<6} {op:<11} {csm:>6.3f} {w:>6.3f} {adj_str:<28} {ll_has:>5}")
    print()
    # Per-operator summary
    print("  ── Per-operator CSM summary ──")
    all_csm = compute_all_csm(pairs)
    by_op: Dict[str, list] = {}
    for r in all_csm:
        by_op.setdefault(r["operator"], []).append(r["csm"])
    print(f"  {'operator':<11} {'n':>3} {'min':>6} {'mean':>6} {'max':>6} {'≥0.65':>6}")
    print("  " + "─" * 40)
    for op in sorted(by_op):
        vals = by_op[op]
        ge = sum(1 for v in vals if v >= 0.65)
        print(f"  {op:<11} {len(vals):>3} {min(vals):>6.3f} {sum(vals)/len(vals):>6.3f} {max(vals):>6.3f} {ge:>6}")
    print()
    # Weighted aggregates
    print("  ── Weighted CSM aggregates (provisional weights) ──")
    wc = weighted_csm(pairs)
    wco = weighted_csm_by_operator(pairs)
    print(f"  Overall weighted CSM:     {wc:.3f}")
    print(f"  Per-operator weighted CSM:")
    for op in sorted(wco):
        print(f"    {op:<11} {wco[op]:.3f}")
    print()
    print("  Note: llmOutput is empty for all pairs — CSM computed against"
          " missing LLM reference (treats missing LHS as 0 alignment)."
          " Enrich with synthetic llmOutput to hear real signal.")
    print("=" * 72)
