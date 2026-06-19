from __future__ import annotations

"""
Greek/Stoic Virtue Atoms for ARCS hiring coherence

Implements four higher-level primitives that operate on (candidate, role, org)
feature bundles and emit scalar scores in [0,1] with immutable receipts:
- MetisAtom (cunning fit)
- ParrhesiaAtom (candor & truth)
- KairosAlignmentAtom (timing fit)
- AtaraxiaAtom (stoic stability)
"""

from dataclasses import dataclass
from typing import Dict, Mapping, Optional

import numpy as np
from loguru import logger

from .governance import decision_receipt
from .operators import chrono_kairos


def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


@dataclass
class VirtueScores:
    metis: float
    parrhesia: float
    kairos: float
    ataraxia: float
    receipts: Dict[str, Mapping]


class MetisAtom:
    """Measures non-obvious adjacency and ethical rule-bending potential.

    Heuristics (bounded in [0,1]):
    - Unusual moves: signal from candidate receipts/history (0..1)
    - Role need for constraint-bending (0..1)
    - Org risk tolerance / governance maturity (0..1)
    Score blends these with diminishing returns to favor balanced cunning.
    """

    def score(self, candidate: Mapping, role: Mapping, org: Mapping) -> Mapping[str, float | Mapping]:
        unusual = float(candidate.get("unusual_moves", 0.0))
        need = float(role.get("constraint_bending_need", 0.0))
        tolerance = float(org.get("risk_tolerance", 0.5)) * float(org.get("governance_maturity", 0.5))
        s = 0.5 * _clip01(unusual) + 0.3 * _clip01(need) + 0.2 * _clip01(tolerance)
        s = _clip01(s)
        r = decision_receipt("virtue.metis", {"unusual": unusual, "need": need, "tolerance": tolerance, "score": s})
        return {"score": s, "receipt": r}


class ParrhesiaAtom:
    """Estimates mutual fearless truth-telling capacity (candidate ↔ org).

    Inputs expected if available:
    - candidate.candor_index (0..1), whistle_history (0..1)
    - org.psych_safety (0..1), no_retaliation_policy (0/1), receipts_completeness (0..1)
    Score penalizes high candidate candor with low org safety (silencing risk).
    """

    def score(self, candidate: Mapping, role: Mapping, org: Mapping) -> Mapping[str, float | Mapping]:
        candor = float(candidate.get("candor_index", 0.5))
        whistle = float(candidate.get("whistle_history", 0.0))
        safety = float(org.get("psych_safety", 0.5))
        policy = 1.0 if org.get("no_retaliation_policy", False) else 0.0
        receipts = float(org.get("receipts_completeness", 0.5))
        base = 0.5 * candor + 0.2 * whistle + 0.2 * safety + 0.1 * policy
        # If safety is low and candor high, reduce effective score (risk of silencing)
        penalty = max(0.0, candor - safety) * 0.3
        s = _clip01(base - penalty)
        r = decision_receipt("virtue.parrhesia", {
            "candor": candor, "whistle": whistle, "safety": safety,
            "policy": policy, "receipts_completeness": receipts, "score": s
        })
        return {"score": s, "receipt": r}


class KairosAlignmentAtom:
    """Computes timing fit between candidate readiness and org temporal state.

    Consumes simple readiness/urgency traces (aligned-length lists in [0,1])
    and measures overlap via Chrono-Kairos composite.
    """

    def score(self, candidate: Mapping, role: Mapping, org: Mapping) -> Mapping[str, float | Mapping]:
        readiness = candidate.get("readiness_trace") or role.get("readiness_trace") or [0.5]
        urgency = org.get("urgency_trace") or role.get("urgency_trace") or [0.5]
        length = min(len(readiness), len(urgency))
        readiness = readiness[:length]
        urgency = urgency[:length]
        ck = chrono_kairos(scheduled_windows=[], signals={"readiness": readiness, "urgency": urgency}, threshold=0.6)
        comp = np.asarray(ck.get("composite"))
        # Overlap score as mean of pointwise min(readiness, urgency)
        overlap = float(np.mean(np.minimum(readiness, urgency))) if length else 0.0
        s = _clip01(0.6 * overlap + 0.4 * float(comp.mean() if comp.size else 0.0))
        r = decision_receipt("virtue.kairos", {"overlap": overlap, "composite_mean": float(comp.mean() if comp.size else 0.0), "score": s})
        return {"score": s, "receipt": r}


class AtaraxiaAtom:
    """Estimates productive calm fit given role entropy and candidate resilience.

    Inputs:
    - role.entropy (0..1), org.entropy (0..1)
    - candidate.resilience (0..1), pacing_pref (0..1; higher = faster-paced ok)
    Score high when resilience and pacing suffice for entropy without overload.
    """

    def score(self, candidate: Mapping, role: Mapping, org: Mapping) -> Mapping[str, float | Mapping]:
        entropy = 0.6 * float(role.get("entropy", 0.5)) + 0.4 * float(org.get("entropy", 0.5))
        resilience = float(candidate.get("resilience", 0.5))
        pacing = float(candidate.get("pacing_pref", 0.5))
        # Mismatch penalty when entropy exceeds coping capacity
        capacity = 0.7 * resilience + 0.3 * pacing
        penalty = max(0.0, entropy - capacity)
        s = _clip01(1.0 - penalty)
        r = decision_receipt("virtue.ataraxia", {"entropy": entropy, "capacity": capacity, "score": s})
        return {"score": s, "receipt": r}

