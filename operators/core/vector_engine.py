from __future__ import annotations

"""
ARCS Vector Decision Engine (5D FATED Hypercube)

Implements geometric constraint checks, virtue mapping, and path analysis with
immutable decision receipts (Loguru + SHA-256).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping

import numpy as np

from .governance import decision_receipt


class Axis(Enum):
    """The 5D Hypercube Dimensions (FATED)."""

    FIDELITY = 0
    ALTITUDE = 1
    TIME = 2
    ENERGY = 3
    DECISION = 4


class Virtue(Enum):
    """The Pentagram of Coherence (Virtue Manifold)."""

    METIS = 0
    PARRHESIA = 1
    KAIROS = 2
    ATARAXIA = 3
    SYMPATHEIA = 4


@dataclass(frozen=True)
class Constraint:
    """A geometric boundary in 5D space.

    boundary is the minimum acceptable projection along the unit normal.
    """

    axis: Axis
    normal: np.ndarray
    boundary: float
    description: str
    is_hard_stop: bool = True

    def unit(self) -> np.ndarray:
        n = self.normal.astype(float)
        norm = float(np.linalg.norm(n) or 1.0)
        return n / norm


@dataclass
class DecisionState:
    """A single point (pixel) in the 5D Hypercube."""

    vector: np.ndarray = field(default_factory=lambda: np.zeros(5))
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.vector.shape != (5,):
            raise ValueError("State must be a 5D vector.")


class ARCSVectorEngine:
    """Decision Engine using 5D Hypercube geometric constructions.

    Provides:
    - calculate_coherence: magnitude-based coherence in [0,1]
    - detect_collisions: boundary violations using dot(v, n_unit)
    - map_to_virtues: projection from FATED to Virtue manifold
    - analyze_critical_path: survivability, golden seams, collisions
    """

    def __init__(self, constraints: List[Constraint]):
        self.constraints = constraints
        decision_receipt("vector_engine.init", {"constraints": len(constraints)})

    @staticmethod
    def _clip01(v: np.ndarray) -> np.ndarray:
        return np.clip(v, 0.0, 1.0)

    def calculate_coherence(self, state: DecisionState) -> float:
        v = self._clip01(state.vector.astype(float))
        coh = float(np.clip(np.linalg.norm(v) / np.sqrt(5.0), 0.0, 1.0))
        decision_receipt("vector_engine.coherence", {"coherence": coh})
        return coh

    def detect_collisions(self, path: List[DecisionState]) -> List[Dict]:
        collisions: List[Dict] = []
        if not path or not self.constraints:
            decision_receipt("vector_engine.collisions", {"count": 0})
            return collisions
        for i, state in enumerate(path):
            v = self._clip01(state.vector.astype(float))
            for c in self.constraints:
                proj = float(np.dot(v, c.unit()))
                if proj < c.boundary:  # boundary as minimum acceptable projection
                    collisions.append(
                        {
                            "step": i,
                            "axis": c.axis.name,
                            "severity": float(c.boundary - proj),
                            "description": c.description,
                            "is_pathogen": c.is_hard_stop,
                        }
                    )
        decision_receipt("vector_engine.collisions", {"count": len(collisions)})
        return collisions

    def map_to_virtues(self, state: DecisionState) -> Dict[Virtue, float]:
        v = self._clip01(state.vector.astype(float))
        mapping: Dict[Virtue, float] = {
            Virtue.METIS: float(v[0]),
            Virtue.PARRHESIA: float(v[1]),
            Virtue.KAIROS: float(v[2]),
            Virtue.ATARAXIA: float(v[3]),
            Virtue.SYMPATHEIA: float(v[4]),
        }
        decision_receipt("vector_engine.virtues", {"virtues": {k.name: mapping[k] for k in mapping}})
        return mapping

    def analyze_critical_path(self, path: List[DecisionState]) -> Dict:
        if not path:
            out = {
                "survivability": 1.0,
                "avg_coherence": 0.0,
                "collisions": [],
                "golden_seams": [],
                "status": "EMPTY",
            }
            decision_receipt("vector_engine.path", out)
            return out
        collisions = self.detect_collisions(path)
        coherence_scores = [self.calculate_coherence(s) for s in path]
        golden_seams = [i for i in range(1, len(coherence_scores)) if coherence_scores[i] > coherence_scores[i - 1]]
        denom = max(1, len(path) * max(1, len(self.constraints)))
        survivability = float(1.0 - (len(collisions) / denom))
        status = "STABLE" if not any(c["is_pathogen"] for c in collisions) else "PATHOGENIC"
        out = {
            "survivability": survivability,
            "avg_coherence": float(np.mean(coherence_scores)),
            "collisions": collisions,
            "golden_seams": golden_seams,
            "status": status,
        }
        decision_receipt(
            "vector_engine.path",
            {"survivability": survivability, "status": status, "collisions": len(collisions)},
        )
        return out

