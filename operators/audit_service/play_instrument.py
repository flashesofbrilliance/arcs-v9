#!/usr/bin/env python3
"""
play_instrument.py — Play the ARCS v9 operator audit instrument on 9 sample pairs.

9 pairs = 1 real (verify-coverage-001 / SAGE, from benchmark_pairs.jsonl)
        + 8 synthetic (calibration data, populated across SAGE/LAB/BAR/KINTSUGI)

The instrument computes:
  - CSM per pair (alignment×0.40 + (1−ΔABS)×0.30 + (1−coherence_loss)×0.20 + (1−severity)×0.10)
  - Fidelity weight per pair (somatic × hci × axioms, provisional weights)
  - Weighted CSM aggregate (Σ CSM_i × w_i / Σ w_i)
  - Weighted CSM by operator
  - Who-was-right (adjudication) where present
  - Horizon mapping (HORIZON_MAP replicated from audit-translator.ts)

NOT persisted to benchmark_pairs.jsonl. Calibration data only.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent
_BENCH = os.environ.get(
    "AUDIT_BENCH_FILE", str(_HERE / "benchmark_pairs.jsonl")
)

# ── HORIZON_MAP (replicated from src/lib/audit-translator.ts lines 105-116) ──
#
# The Python audit service does NOT apply horizon mapping — that lives in the
# TS translator. We replicate it here so the sound board can show the mapped
# horizon for each pair, consistent with what the TS side would produce.

HORIZON_MAP: dict[str, str] = {
    "TODAY": "TODAY",
    "WEEK": "THIS_WEEK",
    "QUARTER": "THIS_QUARTER",
    "YEAR": "ONE_TO_THREE_YEARS",
    "YEARS": "LONGER",
}

# ── provisional fidelity weights (from CSM-spec.md §4 / persistence._WEIGHTS) ─
_WEIGHTS = {
    "somatic": {"user_self_report": 1.0, "default": 0.3},
    "hci": {"user_self_report": 1.0, "proxy": 0.4},
    "axioms": {"llm_derived": 0.6, "default": 0.3},
}


def _fidelity_weight(fidelity: dict) -> float:
    sw = _WEIGHTS["somatic"].get(fidelity.get("somatic", "default"), 0.3)
    hw = _WEIGHTS["hci"].get(fidelity.get("hci", "proxy"), 0.4)
    aw = _WEIGHTS["axioms"].get(fidelity.get("axioms", "default"), 0.3)
    w = sw * hw * aw
    return max(0.0, min(1.0, w))


def _horizon_map(raw: str | None) -> str:
    """Apply HORIZON_MAP. None / unknown → 'UNKNOWN'."""
    if raw is None:
        return "UNKNOWN"
    return HORIZON_MAP.get(raw.upper(), f"UNMAPPED({raw})")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── synthetic pair factory ─────────────────────────────────────────────────────

def _synthetic_pair(
    trace_id: str,
    operator: str,
    horizon: str | None = None,
    *,
    adjudication: dict | None = None,
    llm_output_override: dict | None = None,
) -> dict:
    """Build one synthetic (traceId, operator) benchmark pair.

    Shape matches the schema of benchmark_pairs.jsonl rows (primitives +
    llmOutput + auditResult), populated with plausible calibration values.
    """
    ts = _now_iso()
    primitives = _synthetic_primitives(horizon)
    llm_output = llm_output_override if llm_output_override else _synthetic_llm_output(operator)
    audit_result = _synthetic_audit_result(operator, llm_output, adjudication)
    return {
        "traceId": trace_id,
        "sessionVersion": 1,
        "operator": operator,
        "timestamp": ts,
        "primitives": primitives,
        "llmOutput": llm_output,
        "auditResult": audit_result,
    }


def _synthetic_primitives(horizon: str | None = None) -> dict:
    return {
        "signal": {
            "signalProxy": [0.8, 0.64, 0.48, 0.6, 0.48, 0.36, 0.9, 0.1, 0.3, 0.5, 0.5, 0.7],
            "domain": "decision",
            "label": "test-decision",
        },
        "fated": {
            "facts": "Decision context test",
            "assumptions": "Assumption text",
            "tradeoffs": "Tradeoff text",
            "emotions": "Emotion text",
            "direction": "Direction text",
        },
        "axioms": {
            "clarity_before_curvature": "YES",
            "agency_over_automation": "YES",
            "minimum_steps_to_coherence": "YES",
            "kairos_over_neuroticism": "YES",
        },
        "somatic": {"witness_score": 0.5, "source": "default"},
        "hci_score": 55,
        "pci_score": 0.45,
        "irreversibility": 0.3,
        "on_purpose": True,
        "phase_id": "phase_1",
        "next_action": "Test the next action",
        "signal_classification": "stable",
        "horizon": horizon,
    }


def _synthetic_llm_output(operator: str) -> dict:
    """Plausible llmOutput per operator — calibration values, not real LLM output."""
    base = {
        "nci_score": 56,
        "coherence_pct": 61,
        "true_north": "Be clearer about the decision criteria",
        "reasoning": {
            "fated": {
                "facts": "Decision context test",
                "assumptions": "Assumption text",
                "tradeoffs": "Tradeoff text",
                "emotions": "Emotion text",
                "direction": "Direction text",
            },
            "court": [
                {"verdict": "PASS", "weight": 0.95, "rationale": "Strength of TCI signal."}
            ],
            "geometry": {
                "macros_on": ["constraints", "equilibrium"],
                "macros_off": ["catastrophe", "forensic"],
            },
        },
        "meta": {"macro_tags": ["constraints", "equilibrium", "boundary"]},
        "axioms": {
            "clarity_before_curvature": "YES",
            "agency_over_automation": "YES",
            "minimum_steps_to_coherence": "YES",
            "kairos_over_neuroticism": "YES",
        },
    }
    # Per-operator enrichments — minimal plausible fields that the CSM
    # subtask maps in persistence.py will try to align against.
    if operator == "LAB":
        base["loki_threat_level"] = "MEDIUM"
        base["bayesian_posterior"] = 0.62
        base["advisor_consensus"] = "REVIEW"
        base["hidden_assumptions"] = ["assumption A", "assumption B"]
        base["worst_case_scenario"] = "Worst case text"
    elif operator == "BAR":
        base["bar_verdict"] = "PASS"
        base["baseline"] = {"floor_nci": 42.0, "recovery_path": "Reframe as pivot opportunity"}
        base["asymmetry"] = {"asymmetry_ratio": 0.4}
        base["ruin_detected"] = False
    elif operator == "KINTSUGI":
        base["is_healthy"] = True
        base["pathogens"] = ["LOW"]
        base["kintsugi_trust_discount"] = 0.15
        base["kintsugi_repair_count"] = 1
        base["golden_seams"] = ["clarity_before_curvature"]
        base["pathogens"] = {"severity": ["LOW"]}
    return base


def _synthetic_audit_result(
    operator: str,
    llm_output: dict,
    adjudication: dict | None = None,
) -> dict:
    """Plausible auditResult per operator — calibration values."""
    fidelity = {
        "somatic": "default",
        "hci": "proxy",
        "axioms": "llm_derived",
    }
    # Minimal output — enough for CSM subtask maps to align against.
    output = {
        "nci_score": llm_output.get("nci_score", 56.0),
        "pci_score": 0.45,
        "hci_score": 55,
        "signal_classification": "stable",
        "axioms": {
            "clarity_before_curvature": "YES",
            "agency_over_automation": "YES",
            "minimum_steps_to_coherence": "YES",
            "kairos_over_neuroticism": "YES",
        },
        "verdict": "PASS",
        "kinematic_summary": "Stable signal detected.",
        "five_derivatives": {
            "velocity": 0.8,
            "acceleration": 0.2,
            "diffusion": 0.4,
            "phase_cancellation": 0.1,
            "deceleration": 0.0,
        },
    }
    if operator == "LAB":
        output.update({
            "loki_threat_level": llm_output.get("loki_threat_level", "MEDIUM"),
            "bayesian_posterior": llm_output.get("bayesian_posterior", 0.62),
            "advisor_consensus": llm_output.get("advisor_consensus", "REVIEW"),
            "loki": {
                "hidden_assumptions": llm_output.get("hidden_assumptions", ["assumption A"]),
                "worst_case_scenario": llm_output.get("worst_case_scenario", "Worst case text"),
            },
        })
    elif operator == "BAR":
        output.update({
            "bar_verdict": llm_output.get("bar_verdict", "PASS"),
            "baseline": {
                "floor_nci": llm_output.get("baseline", {}).get("floor_nci", 42.0),
                "recovery_path": llm_output.get("baseline", {}).get("recovery_path", "Reframe as pivot opportunity"),
            },
            "asymmetry": {"asymmetry_ratio": llm_output.get("asymmetry", {}).get("asymmetry_ratio", 0.4)},
            "ruin_detected": llm_output.get("ruin_detected", False),
        })
    elif operator == "KINTSUGI":
        output.update({
            "is_healthy": llm_output.get("is_healthy", True),
            "pathogens": llm_output.get("pathogens", ["LOW"]),
            "kintsugi_trust_discount": llm_output.get("kintsugi_trust_discount", 0.15),
            "kintsugi_repair_count": llm_output.get("kintsugi_repair_count", 1),
            "golden_seams": llm_output.get("golden_seams", ["clarity_before_curvature"]),
            "pathogens": llm_output.get("pathogens", {"severity": ["LOW"]}),
        })

    result = {
        "ok": True,
        "version": "1.0.0",
        "fidelity": fidelity,
        "output": output,
        "adjudication": adjudication,
    }
    return result


# ── build the 9-pair store ──────────────────────────────────────────────────────

_REAL_FILE = Path(_BENCH)


def _load_real_pairs() -> list[dict]:
    """Load the 1 real pair from benchmark_pairs.jsonl, if it exists."""
    if not _REAL_FILE.exists():
        return []
    rows = []
    with open(_REAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _build_nine_pairs() -> list[dict]:
    """Return 9 pairs: 1 real (if on disk) + 8 synthetic.

    If the real file has more than 1 row, we still only take the first real
    row and synthesize the rest, to keep the total at 9.
    """
    real = _load_real_pairs()
    real_pair = real[0] if real else None

    synthetic = [
        _synthetic_pair("t1", "SAGE", horizon="TODAY"),
        _synthetic_pair("t2", "LAB", horizon="QUARTER", adjudication={
            "who_was_right": "operator",
            "unresolved": False,
        }),
        _synthetic_pair("t3", "BAR", horizon="YEAR", adjudication={
            "who_was_right": "llm",
            "unresolved": False,
        }),
        _synthetic_pair("t4", "KINTSUGI", horizon="WEEK"),
        _synthetic_pair("t5", "SAGE", horizon="TODAY", adjudication={
            "who_was_right": "split",
            "unresolved": True,
        }),
        _synthetic_pair("t6", "LAB", horizon="QUARTER"),
        _synthetic_pair("t7", "BAR", horizon="YEAR", adjudication={
            "who_was_right": "operator",
            "unresolved": False,
        }),
        _synthetic_pair("t8", "KINTSUGI", horizon="WEEK", adjudication={
            "who_was_right": "undecided",
            "unresolved": True,
        }),
    ]

    if real_pair:
        # Tag the real pair so we can distinguish it in output
        real_pair["_real"] = True
        return [real_pair] + synthetic
    else:
        return synthetic


# ── CSM computation (replicated from persistence.py §CSM) ─────────────────────
#
# We replicate the core CSM logic here so play_instrument.py is self-contained
# and doesn't depend on importing persistence (which would pull in the JSONL
# read path). The formulas are identical to persistence.compute_csm().

def _extract_field(obj: dict, path: str):
    """Extract a dotted field path from a nested dict. Returns (value, found)."""
    parts = path.split(".")
    cur = obj
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return (None, False)
        cur = cur[p]
    return (cur, True)


def _aligned(op_val, llm_val, kind: str, rng) -> float:
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
        if oi is None or li is None:
            return 0.0
        span = max(len(rng or []) - 1, 1)
        return max(0.0, min(1.0, 1.0 - abs(oi - li) / span))
    if kind == "binary":
        try:
            return 1.0 if bool(op_val) == bool(llm_val) else 0.0
        except (TypeError, ValueError):
            return 0.0
    if kind in ("count_proxy", "text_proxy"):
        try:
            oi = float(op_val) if op_val is not None else 0.0
            li = float(llm_val) if llm_val is not None else 0.0
        except (TypeError, ValueError):
            return 0.0
        span = max(abs(oi), abs(li), 1.0)
        return max(0.0, min(1.0, 1.0 - abs(oi - li) / span))
    return 0.0


# Per-operator subtask maps — identical to persistence.py
_SAGE_SUBTASKS = {
    "nci_score": ("nci_score", "nci_score", "continuous", [0, 100]),
    "coherence_pct": ("coherence_pct", "coherence_pct", "continuous", [0, 100]),
    "signal_classification": ("signal_classification", "signalClassification", "categorical", None),
    "axiom_alignment": ("axioms.alignment_score", "axioms.alignment_score", "continuous", [0, 1]),
    "court": ("verdict", "reasoning.court", "categorical", None),
}

_LAB_SUBTASKS = {
    "loki_threat_level": ("loki_threat_level", "loki_threat_level", "ordered", ["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    "bayesian_posterior": ("bayesian_posterior", "bayesian_posterior", "continuous", [0, 1]),
    "advisor_consensus": ("advisor_consensus", "advisor_consensus", "ordered", ["ABORT", "PROCEED", "REVIEW"]),
    "hidden_assumptions": ("loki.hidden_assumptions", "hidden_assumptions", "count_proxy", None),
    "worst_case_scenario": ("loki.worst_case_scenario", "worst_case_scenario", "text_proxy", None),
}

_BAR_SUBTASKS = {
    "bar_verdict": ("bar_verdict", "bar_verdict", "ordered", ["PASS", "CAUTION", "RUIN_RISK"]),
    "baseline_floor_nci": ("baseline.floor_nci", "baseline.floor_nci", "continuous", [0, 100]),
    "asymmetry_ratio": ("asymmetry.asymmetry_ratio", "asymmetry.asymmetry_ratio", "continuous", [0, 1]),
    "ruin_detected": ("ruin_detected", "ruin_detected", "binary", None),
    "recovery_path": ("baseline.recovery_path", "recovery_path", "text_proxy", None),
}

_KINTSUGI_SUBTASKS = {
    "is_healthy": ("is_healthy", "is_healthy", "binary", None),
    "pathogen_count": ("pathogens", "pathogens", "count_proxy", None),
    "trust_discount": ("kintsugi_trust_discount", "kintsugi_trust_discount", "continuous", [0, 1]),
    "repair_count": ("kintsugi_repair_count", "kintsugi_repair_count", "count_proxy", None),
    "severity_max": ("pathogens", "pathogens", "ordered", ["LOW", "MEDIUM", "HIGH"]),
}

_SUBTASK_MAP = {
    "SAGE": _SAGE_SUBTASKS,
    "LAB": _LAB_SUBTASKS,
    "BAR": _BAR_SUBTASKS,
    "KINTSUGI": _KINTSUGI_SUBTASKS,
}


def _alignments(pair: dict, operator: str) -> dict[str, float]:
    """Return per-subtask alignment dict for one operator on one pair."""
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    tasks = _SUBTASK_MAP.get(operator, {})
    result = {}
    for name, (op_path, llm_path, kind, rng) in tasks.items():
        ov, _ = _extract_field(ar, op_path)
        lv, _ = _extract_field(ll, llm_path)
        result[name] = _aligned(ov, lv, kind, rng)
    return result


def _delta_abs(pair: dict, operator: str) -> float:
    """ΔABS ∈ {0, 1}. 1 if advisor direction agrees AND continuous delta crosses 0.30."""
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
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


def _coherence_loss(pair: dict, operator: str) -> float:
    """Per-operator coherence loss."""
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    if operator == "SAGE":
        cls_op, _ = _extract_field(ar, "coherence_law_score")
        cls_llm, _ = _extract_field(ll, "coherence_pct")
        if cls_op is not None and cls_llm is not None and float(cls_llm) > 0:
            return abs(1.0 - float(cls_op) / max(float(cls_llm), 1.0))
        return 0.5
    if operator == "LAB":
        bp_op, _ = _extract_field(ar, "bayesian_posterior")
        bp_llm, _ = _extract_field(ll, "bayesian_posterior")
        if bp_op is not None and bp_llm is not None:
            return abs(1.0 - float(bp_op) / max(float(bp_llm), 1e-9))
        return 0.5
    if operator == "BAR":
        return 0.0
    if operator == "KINTSUGI":
        return 0.0
    return 0.5


def _severity(pair: dict, operator: str) -> float:
    """Per-operator severity ∈ [0, 1]."""
    ar = (pair.get("auditResult") or {}).get("output") or {}
    ll = pair.get("llmOutput") or {}
    if operator == "SAGE":
        cls_op, _ = _extract_field(ar, "coherence_law_score")
        cls_llm, _ = _extract_field(ll, "coherence_pct")
        if cls_op is not None and cls_llm is not None and float(cls_llm) > 0:
            alignment = float(cls_op) / max(float(cls_llm), 1.0)
            return min(1.0, abs(1.0 - alignment) * 1.5)
        return 0.75
    if operator == "LAB":
        ltl, _ = _extract_field(ar, "loki_threat_level")
        ltl_w = {"CRITICAL": 1.0, "HIGH": 0.7, "MEDIUM": 0.4, "LOW": 0.1}.get(str(ltl), 0.0) * 0.40
        ha, _ = _extract_field(ar, "loki.hidden_assumptions")
        ha_count = len(ha) if isinstance(ha, (list, tuple)) else (1 if ha else 0)
        ha_w = (ha_count / 5.0) * 0.35
        wc, _ = _extract_field(ar, "loki.worst_case_scenario")
        wc_w: float = 0.25 if wc else 0.0
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
        rc_w = (float(rc) if rc is not None else 0.0) * 0.35
        ps, _ = _extract_field(ar, "pathogens.severity")
        if isinstance(ps, list) and len(ps) > 0:
            sev_map: Dict[str, float] = {"HIGH": 0.25, "MEDIUM": 0.15, "LOW": 0.05}
            ps_w = max(sev_map.get(str(s), 0.0) for s in ps)
        else:
            ps_w = 0.0
        return min(1.0, gh_w + rc_w + ps_w)
    return 0.5


def compute_csm(pair: dict, operator: str | None = None) -> float:
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


# ── main: play the instrument ──────────────────────────────────────────────────

def main() -> None:
    pairs = _build_nine_pairs()
    real_count = sum(1 for p in pairs if p.get("_real"))
    synth_count = len(pairs) - real_count

    print("=" * 72)
    print("  ARCS v9 OPERATOR AUDIT — WEIGHTED CSM SOUND BOARD")
    print("=" * 72)
    print(f"  {len(pairs)} pairs: {real_count} real (from benchmark_pairs.jsonl) + {synth_count} synthetic (calibration)")
    print(f"  Store source: {_BENCH}  ({sum(1 for _ in open(_BENCH) if _.strip())} rows on disk)")
    print()

    # ── Per-pair table ──
    print("  ── Per-pair CSM + fidelity weight + adjudication + horizon ──")
    hdr = f"  {'traceId':<10} {'op':<11} {'horizon':<8} {'CSM':>6} {'w':>6} {'adjudication':<28} {'llm?':>5}"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for pair in pairs:
        op = pair.get("operator") or "?"
        csm = compute_csm(pair, op)
        w = _fidelity_weight((pair.get("auditResult") or {}).get("fidelity") or {})
        h_raw = (pair.get("primitives") or {}).get("horizon")
        h_mapped = _horizon_map(h_raw)
        adj = (pair.get("auditResult") or {}).get("adjudication")
        if adj:
            adj_str = f"{adj.get('who_was_right','-')}/{adj.get('unresolved',False)}"
        else:
            adj_str = "— (no adjudication)"
        ll = pair.get("llmOutput") or {}
        ll_has = "YES" if (
            ll.get("nci_score") is not None
            or ll.get("coherence_pct") is not None
            or ll.get("loki_threat_level") is not None
            or ll.get("bar_verdict") is not None
            or ll.get("is_healthy") is not None
            or ll.get("bayesian_posterior") is not None
        ) else "no"
        real_mark = "*" if pair.get("_real") else " "
        print(f"  {pair.get('traceId','?'):<9} {op:<11} {h_mapped:<8} {csm:>6.3f} {w:>6.3f} {adj_str:<28} {ll_has:>5} {real_mark}")
    print("  (* = real pair from disk, not synthetic)")
    print()

    # ── Per-operator CSM summary ──
    print("  ── Per-operator CSM summary ──")
    by_op: dict[str, list[float]] = {}
    for pair in pairs:
        op = pair.get("operator") or "?"
        c = compute_csm(pair, op)
        by_op.setdefault(op, []).append(c)
    print(f"  {'operator':<11} {'n':>3} {'min':>6} {'mean':>6} {'max':>6} {'≥0.65':>6}")
    print("  " + "─" * 40)
    for op in sorted(by_op):
        vals = by_op[op]
        ge = sum(1 for v in vals if v >= 0.65)
        print(f"  {op:<11} {len(vals):>3} {min(vals):>6.3f} {sum(vals)/len(vals):>6.3f} {max(vals):>6.3f} {ge:>6}")
    print()

    # ── Weighted aggregates ──
    print("  ── Weighted CSM aggregates (provisional weights) ──")
    total_w = 0.0
    total_csm_w = 0.0
    for pair in pairs:
        w = _fidelity_weight((pair.get("auditResult") or {}).get("fidelity") or {})
        c = compute_csm(pair)
        total_w += w
        total_csm_w += c * w
    overall_weighted = (total_csm_w / total_w) if total_w > 0 else 0.0
    print(f"  Overall weighted CSM:     {overall_weighted:.3f}")
    print(f"  Per-operator weighted CSM:")
    by_op_w: dict[str, dict[str, float]] = {}
    for pair in pairs:
        op = pair.get("operator") or "UNKNOWN"
        w = _fidelity_weight((pair.get("auditResult") or {}).get("fidelity") or {})
        c = compute_csm(pair, op)
        if op not in by_op_w:
            by_op_w[op] = {"w": 0.0, "cw": 0.0}
        by_op_w[op]["w"] += w
        by_op_w[op]["cw"] += c * w
    for op in sorted(by_op_w):
        v = by_op_w[op]
        op_weighted = (v["cw"] / v["w"]) if v["w"] > 0 else 0.0
        print(f"    {op:<11} {op_weighted:.3f}")
    print()

    # ── Who-was-right coverage ──
    print("  ── Who-was-right (adjudication) coverage ──")
    adjudicated = [p for p in pairs if (p.get("auditResult") or {}).get("adjudication")]
    print(f"  {len(adjudicated)}/{len(pairs)} pairs have adjudication")
    for p in adjudicated:
        a = p.get("auditResult", {}).get("adjudication", {})
        print(f"    {p.get('traceId','?'):<10} {p.get('operator','?'):<11} {a.get('who_was_right','-'):<12} unresolved={a.get('unresolved', False)}")
    print()

    # ── Horizon mapping ──
    print("  ── Horizon mapping (HORIZON_MAP) ──")
    print("  HORIZON_MAP (from src/lib/audit-translator.ts lines 105-116):")
    for k, v in HORIZON_MAP.items():
        print(f"    {k:<10} → {v}")
    print()
    print("  Per-pair mapped horizon:")
    for pair in pairs:
        h_raw = (pair.get("primitives") or {}).get("horizon")
        h_mapped = _horizon_map(h_raw)
        print(f"    {pair.get('traceId','?'):<10} raw={h_raw!r:<12} → {h_mapped}")
    print()

    # ── Fidelity weight breakdown ──
    print("  ── Fidelity weight breakdown (per pair) ──")
    for pair in pairs:
        f = (pair.get("auditResult") or {}).get("fidelity") or {}
        w = _fidelity_weight(f)
        src = f.get("somatic", "?"), f.get("hci", "?"), f.get("axioms", "?")
        print(f"    {pair.get('traceId','?'):<10} {pair.get('operator','?'):<11} w={w:.3f}  somatic={src[0]}  hci={src[1]}  axioms={src[2]}")
    print()

    # ── Interpretation ──
    print("  ── Interpretation ──")
    print("  This is the instrument's sound on 9 sample pairs (1 real + 8 synthetic).")
    print("  Synthetic pairs are calibration data — not real compass output.")
    print()
    print("  CSM distribution across operators shows whether the 4 operators")
    print("  differentiate on the same trace. Weighted aggregates adjust for")
    print("  fidelity source (somatic/hci/axioms). Who-was-right shows where")
    print("  adjudication exists and whether CSM agrees.")
    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
