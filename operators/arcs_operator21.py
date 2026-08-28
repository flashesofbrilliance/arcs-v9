"""
arcs_operator21.py
ARCS v9 — Anterior/Posterior Spline Inference Operator
Phase 3: READ-WRITE

Interpolative inference across the reticulated knowledge lattice.
Takes the anterior (pre-experiential prior) and posterior (evidence-updated)
belief states at two knot points in the spline, and infers the shape of the
curve between them — the "splines" of the knowledge web as it reticulates.

Canonical reference:
  ARCS-YellowPaper-v1-1.md — anterior/posterior Gaussian dimension
  ADR-020 — Tribune intelligence layer (anterior/proactive/posterior phases)
  ADR-023 — observability goal lattice (reticulated lattice of abductive inference)

The "spline" is the knowledge web's shape between two resolved knot points.
Each cut/twist/turn sharpens the resolution between them — progressive
de-fuzzing of the interpolative inference as the lattice tightens.

Operator 21 sits between Operator 20 (folksonomy cultivation / seed clustering)
and Phase 4 ROM lock — it is the inference layer that turns clustered seeds
into a continuous belief surface with anterior/posterior interpolation.
"""

from __future__ import annotations
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from arcs_primitives import (
    AXIOM_YES, AXIOM_NO, AXIOM_TENSION,
    LABEL_SEED, LABEL_LAB, LABEL_PLAYGROUND, LABEL_GEMINATE,
    AxiomCheck, CoherenceReceipt, CoherenceSignal,
    SomaticReading,
)
from arcs_rom import ROM_VERSION, DNA_AXIOMS, NCI_FORMULA

OPERATOR_VERSION = "v0.1.0-phase3"
OPERATOR_ID = "OP-21"


# ─────────────────────────────────────────────
# KNOT — a resolved point on the knowledge spline
# ─────────────────────────────────────────────

@dataclass
class Knot:
    """
    A resolved belief state at a point in the knowledge spline.

    A knot is what you get AFTER a cut/twist/turn has resolved —
    the anterior belief (prior) and posterior belief (evidence-updated)
    at that point, plus the metadata of how it got there.

    The spline interpolates between knots. The more knots you have,
    and the sharper each one is, the less fuzzy the interpolation.
    """
    knot_id: str
    anterior: Dict[str, Any]       # pre-experiential prior belief state
    posterior: Dict[str, Any]      # evidence-updated belief state
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.5        # 0..1, how sharply resolved this knot is
    source: str = ""               # which session/worktree/commit produced this
    tags: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)  # declared neighbors in lattice


# ─────────────────────────────────────────────
# SPLINE SEGMENT — interpolative inference between two knots
# ─────────────────────────────────────────────

@dataclass
class SplineSegment:
    """
    The inferred shape of the knowledge web between two resolved knots.

    Anterior/posterior interpolation: given knot A (anterior + posterior)
    and knot B (anterior + posterior), infer what the belief state looks
    like at t∈[0,1] between them.

    The "fuzziness" of the inference is inversely proportional to:
      - confidence of both endpoint knots
      - density of intermediate knots (more knots = less interpolation needed)
      - coherence of the directional vector between them
    """
    from_knot: str
    to_knot: str
    t_samples: List[float] = field(default_factory=list)  # [0.0, 0.25, 0.5, 0.75, 1.0]
    interpolated_states: List[Dict[str, Any]] = field(default_factory=list)
    anterior_trajectory: List[Dict[str, Any]] = field(default_factory=list)
    posterior_trajectory: List[Dict[str, Any]] = field(default_factory=list)
    coherence_score: float = 0.0       # 0..1, how clean the interpolation is
    fuzziness: float = 1.0             # 0..1, 1=maximum fuzz, 0=sharp
    directional_vector: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────
# OPERATOR 21 — Anterior/Posterior Spline Inference
# ─────────────────────────────────────────────

class SplineInferenceOperator:
    """
    Interpolative inference across the reticulated knowledge lattice.

    Inputs:
      - A set of resolved Knots (anterior + posterior belief states at points)
      - Optional: seed vectors from Operator 20 (folksonomy clusters as anchor points)

    Outputs:
      - SplineSegments connecting knots with interpolated belief trajectories
      - Fuzziness gradient: which regions of the spline are sharp vs. fuzzy
      - Directional vectors: the "forward projected" shape of the lattice

    The operator's job is to make the fuzzy logic LESS fuzzy with each cut.
    Each knot resolution sharpens the interpolation. Each cut/twist/turn
    that lands cleanly adds a knot and tightens the spline.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.knots: Dict[str, Knot] = {}
        self.segments: List[SplineSegment] = []
        self.version = OPERATOR_VERSION
        # __canonicality — farm league canonicality tier.
        # Operators that opt into the farm league protocol carry this attribute.
        # Default SEED: provisional, on-disk, not committed to main.
        # Ascends: SEED → LAB → PLAYGROUND → GEMINATE_CANDIDACY → (canonical, implicit).
        # Promotion is opt-in, never automatic.
        self.__canonicality: str = LABEL_SEED
        # _pollination — instance-state pollination surface.
        # Mutated in place by pollinate(); returned by _pollination_state().
        self._pollination: Dict[str, Any] = {
            "exports": [],
            "imports": [],
            "compatible_tiers": self._compatible_tiers(),
            "last_pollinated_at": None,
        }

    # ── knot management ──────────────────────

    def add_knot(self, knot: Knot) -> None:
        """Register a resolved belief state as a knot on the spline."""
        self.knots[knot.knot_id] = knot

    TIER_ORDER = [LABEL_SEED, LABEL_LAB, LABEL_PLAYGROUND, LABEL_GEMINATE]

    def _compatible_tiers(self) -> List[str]:
        """Return tiers this operator can exchange pollination with (same tier ± 1)."""
        idx = self.TIER_ORDER.index(self.__canonicality)
        return [
            self.TIER_ORDER[i]
            for i in range(max(0, idx - 1), min(len(self.TIER_ORDER), idx + 2))
            if self.TIER_ORDER[i] != self.__canonicality
        ]

    def pollinate(self, export: Dict[str, Any], tier_hint: Optional[str] = None) -> None:
        """Register a pollination export on the surface; mutates self._pollination in place."""
        self._pollination["exports"].append(export)
        self._pollination["last_pollinated_at"] = time.time()

    def resolve_knot(
        self,
        knot_id: str,
        anterior: Dict[str, Any],
        posterior: Dict[str, Any],
        confidence: float = 0.5,
        source: str = "",
        tags: Optional[List[str]] = None,
        edges: Optional[List[str]] = None,
    ) -> Knot:
        """
        Create and register a resolved knot.

        This is the atomic cut event: the moment a belief state resolves
        from anterior (prior) to posterior (evidence-updated). The sharper
        the resolution (higher confidence), the more this knot tightens
        the surrounding spline.
        """
        knot = Knot(
            knot_id=knot_id,
            anterior=anterior,
            posterior=posterior,
            confidence=confidence,
            source=source,
            tags=tags or [],
            edges=edges or [],
        )
        self.add_knot(knot)
        return knot

    # ── pollination surface ──────────────────────────────────────────────────

    def _pollination_state(self) -> Dict[str, Any]:
        """Return the current pollination surface (stored on the instance)."""
        return self._pollination

    # ── spline construction ──────────────────

    def build_segments(self) -> List[SplineSegment]:
        """
        Build spline segments between all adjacent knots in the lattice.

        Adjacency is determined by declared edges (from the folksonomy graph).
        If no edges are declared, fall back to topological proximity in the
        belief-space embedding.
        """
        self.segments = []
        knot_ids = list(self.knots.keys())

        if len(knot_ids) < 2:
            return self.segments

        # Build adjacency from declared edges
        adjacency: Dict[str, List[str]] = {kid: [] for kid in knot_ids}
        for kid in knot_ids:
            knot = self.knots[kid]
            for edge_target in knot.edges:
                if edge_target in self.knots:
                    adjacency[kid].append(edge_target)

        # Create segments along declared edges
        seen_pairs = set()
        for from_id, targets in adjacency.items():
            for to_id in targets:
                pair_key = tuple(sorted([from_id, to_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                segment = self._interpolate(from_id, to_id)
                self.segments.append(segment)

        # If no declared edges, connect in topological order
        if not self.segments and len(knot_ids) >= 2:
            for i in range(len(knot_ids) - 1):
                segment = self._interpolate(knot_ids[i], knot_ids[i + 1])
                self.segments.append(segment)

        return self.segments

    def _interpolate(self, from_id: str, to_id: str) -> SplineSegment:
        """
        Interpolate the belief trajectory between two knots.

        Anterior/posterior reasoning:
          - Anterior trajectory: how the PRIOR belief evolves from knot A to knot B
          - Posterior trajectory: how the EVIDENCE-UPDATED belief evolves
          - The difference between them at each t-sample is the "learning delta"
        """
        from_knot = self.knots[from_id]
        to_knot = self.knots[to_id]

        t_samples = [0.0, 0.25, 0.5, 0.75, 1.0]
        interpolated = []
        anterior_traj = []
        posterior_traj = []

        for t in t_samples:
            anterior_blend = self._blend_beliefs(
                from_knot.anterior, to_knot.anterior, t
            )
            posterior_blend = self._blend_beliefs(
                from_knot.posterior, to_knot.posterior, t
            )

            anterior_traj.append(anterior_blend)
            posterior_traj.append(posterior_blend)
            interpolated.append({
                "t": t,
                "anterior": anterior_blend,
                "posterior": posterior_blend,
                "learning_delta": self._compute_delta(anterior_blend, posterior_blend),
            })

        # Coherence: how clean is the interpolation?
        # High confidence endpoints + small learning delta across the spline
        # = high coherence (less fuzzy)
        endpoint_confidence = (from_knot.confidence + to_knot.confidence) / 2
        avg_delta_mag = sum(
            self._delta_magnitude(s["learning_delta"]) for s in interpolated
        ) / len(interpolated)

        coherence = endpoint_confidence * (1 - avg_delta_mag)
        fuzziness = 1 - coherence

        # Directional vector: the net direction of belief change across the segment
        directional_vector = self._compute_directional_vector(
            from_knot.posterior, to_knot.posterior
        )

        return SplineSegment(
            from_knot=from_id,
            to_knot=to_id,
            t_samples=t_samples,
            interpolated_states=interpolated,
            anterior_trajectory=anterior_traj,
            posterior_trajectory=posterior_traj,
            coherence_score=coherence,
            fuzziness=fuzziness,
            directional_vector=directional_vector,
        )

    def _blend_beliefs(
        self, belief_a: Dict[str, Any], belief_b: Dict[str, Any], t: float
    ) -> Dict[str, Any]:
        """Linear interpolation between two belief dicts (simplified)."""
        result = {}
        all_keys = set(belief_a.keys()) | set(belief_b.keys())
        for key in all_keys:
            val_a = belief_a.get(key)
            val_b = belief_b.get(key)
            if val_a is None:
                result[key] = val_b
            elif val_b is None:
                result[key] = val_a
            elif isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                result[key] = val_a * (1 - t) + val_b * t
            else:
                result[key] = val_a if t < 0.5 else val_b
        return result

    def _compute_delta(
        self, anterior: Dict[str, Any], posterior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute the delta between anterior and posterior belief states."""
        delta = {}
        all_keys = set(anterior.keys()) | set(posterior.keys())
        for key in all_keys:
            val_a = anterior.get(key)
            val_b = posterior.get(key)
            if val_a is None or val_b is None:
                delta[key] = {
                    "from": val_a,
                    "to": val_b,
                    "type": "emerged" if val_b is not None else "vanished",
                }
            elif isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                delta[key] = {
                    "from": val_a,
                    "to": val_b,
                    "delta": val_b - val_a,
                    "type": "shifted",
                }
            else:
                delta[key] = {
                    "from": val_a,
                    "to": val_b,
                    "type": "transformed" if val_a != val_b else "stable",
                }
        return delta

    def _delta_magnitude(self, delta: Dict[str, Any]) -> float:
        """Compute a scalar magnitude of belief change."""
        magnitudes = []
        for key, info in delta.items():
            if info.get("type") == "shifted":
                magnitudes.append(abs(info.get("delta", 0)))
            elif info.get("type") == "transformed":
                magnitudes.append(1.0)
            elif info.get("type") in ("emerged", "vanished"):
                magnitudes.append(0.5)
        return sum(magnitudes) / max(len(magnitudes), 1)

    def _compute_directional_vector(
        self, posterior_a: Dict[str, Any], posterior_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute the net directional vector of belief change.

        This is the "forward projected" shape — what direction the lattice
        is trending as it reticulates between these two knots.
        """
        vector = {}
        all_keys = set(posterior_a.keys()) | set(posterior_b.keys())
        for key in all_keys:
            val_a = posterior_a.get(key)
            val_b = posterior_b.get(key)
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                direction = (
                    "increases" if val_b > val_a
                    else ("decreases" if val_b < val_a else "stable")
                )
                vector[key] = {
                    "from": val_a,
                    "to": val_b,
                    "direction": direction,
                    "magnitude": abs(val_b - val_a),
                }
            elif val_a != val_b:
                vector[key] = {
                    "from": val_a,
                    "to": val_b,
                    "direction": "transformed",
                    "magnitude": 1.0,
                }
        return vector

    # ── fuzzy reduction analysis ─────────────

    def fuzziness_gradient(self) -> Dict[str, Any]:
        """
        Return the fuzziness profile across the entire spline.

        Where the lattice is fuzzy (high interpolation uncertainty), that's
        where the next cut/twist/turn should land. Where it's sharp, the
        knots are well-resolved and the inference is reliable.
        """
        if not self.segments:
            return {
                "segments": [],
                "overall_fuzziness": 1.0,
                "sharp_regions": [],
                "fuzzy_regions": [],
            }

        segments_by_fuzz = sorted(
            self.segments, key=lambda s: s.fuzziness, reverse=True
        )

        sharp_regions = [
            {
                "segment": f"{s.from_knot}->{s.to_knot}",
                "fuzziness": s.fuzziness,
                "coherence": s.coherence_score,
            }
            for s in segments_by_fuzz if s.fuzziness < 0.5
        ]
        fuzzy_regions = [
            {
                "segment": f"{s.from_knot}->{s.to_knot}",
                "fuzziness": s.fuzziness,
                "coherence": s.coherence_score,
            }
            for s in segments_by_fuzz if s.fuzziness >= 0.5
        ]

        overall = sum(s.fuzziness for s in self.segments) / len(self.segments)

        return {
            "segments": [
                {
                    "from": s.from_knot,
                    "to": s.to_knot,
                    "fuzziness": s.fuzziness,
                    "coherence": s.coherence_score,
                    "directional_vector": s.directional_vector,
                }
                for s in segments_by_fuzz
            ],
            "overall_fuzziness": overall,
            "sharp_regions": sharp_regions,
            "fuzzy_regions": fuzzy_regions,
            "next_cut_recommendation": (
                fuzzy_regions[0]["segment"] if fuzzy_regions
                else "lattice is sharp — no cut needed"
            ),
        }

    def progressive_defuzzing(self) -> Dict[str, Any]:
        """
        Analyze how the lattice has de-fuzzed over time.

        As knots are added and resolution sharpens, the overall fuzziness
        should decrease. This tracks the "each cut makes the fuzzy logic
        less fuzzy" property.
        """
        if len(self.knots) < 2:
            return {"knot_count": len(self.knots), "trend": "insufficient_data"}

        sorted_knots = sorted(self.knots.values(), key=lambda k: k.timestamp)
        rolling_fuzz = []
        for i in range(1, len(sorted_knots)):
            temp_op = SplineInferenceOperator()
            for k in sorted_knots[:i + 1]:
                temp_op.add_knot(k)
            temp_op.build_segments()
            gradient = temp_op.fuzziness_gradient()
            rolling_fuzz.append({
                "knot_count": i + 1,
                "overall_fuzziness": gradient["overall_fuzziness"],
                "timestamp": sorted_knots[i].timestamp,
            })

        if len(rolling_fuzz) >= 2:
            first = rolling_fuzz[0]["overall_fuzziness"]
            last = rolling_fuzz[-1]["overall_fuzziness"]
            trend = (
                "defuzzing" if last < first
                else ("stable" if abs(last - first) < 0.05 else "fuzzing")
            )
        else:
            trend = "insufficient_data"

        return {
            "knot_count": len(self.knots),
            "rolling_fuzziness": rolling_fuzz,
            "trend": trend,
            "defuzzing_rate": (
                (rolling_fuzz[0]["overall_fuzziness"] - rolling_fuzz[-1]["overall_fuzziness"])
                / max(len(rolling_fuzz), 1)
                if len(rolling_fuzz) >= 2 else 0
            ),
        }

    # ── public interface ─────────────────────

    def run(
        self,
        knots: Optional[List[Dict[str, Any]]] = None,
        seed_vectors: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Run the spline inference operator.

        Args:
          knots: list of knot dicts (anterior/posterior belief states)
          seed_vectors: optional Operator 20 seed clusters for anchor points

        Returns:
          { knots, segments, fuzziness_gradient, progressive_defuzzing }
        """
        if knots:
            for k in knots:
                self.resolve_knot(
                    knot_id=k.get("knot_id", ""),
                    anterior=k.get("anterior", {}),
                    posterior=k.get("posterior", {}),
                    confidence=k.get("confidence", 0.5),
                    source=k.get("source", ""),
                    tags=k.get("tags", []),
                    edges=k.get("edges", []),
                )

        if seed_vectors:
            for i, seed in enumerate(seed_vectors):
                self.resolve_knot(
                    knot_id=f"seed_cluster_{i}",
                    anterior=seed.get("centroid", {}),
                    posterior=seed.get("centroid", {}),
                    confidence=0.3,
                    source="operator20_seed",
                    tags=["seed_cluster"],
                )

        self.build_segments()

        return {
            "operator": OPERATOR_ID,
            "version": self.version,
            "knot_count": len(self.knots),
            "segment_count": len(self.segments),
            "fuzziness_gradient": self.fuzziness_gradient(),
            "progressive_defuzzing": self.progressive_defuzzing(),
            "knots": {
                kid: {
                    "knot_id": k.knot_id,
                    "confidence": k.confidence,
                    "source": k.source,
                    "tags": k.tags,
                    "edges": k.edges,
                }
                for kid, k in self.knots.items()
            },
            "segments": [
                {
                    "from": s.from_knot,
                    "to": s.to_knot,
                    "fuzziness": s.fuzziness,
                    "coherence": s.coherence_score,
                    "directional_vector": s.directional_vector,
                }
                for s in self.segments
            ],
            "canonicality": self.__canonicality,
            "pollination": self._pollination_state(),
        }


# ─────────────────────────────────────────────
# STANDALONE CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    op = SplineInferenceOperator()

    op.resolve_knot(
        knot_id="knot_alpha",
        anterior={"confidence": 0.3, "stance": "skeptical", "temperature": 0.8},
        posterior={"confidence": 0.85, "stance": "convicted", "temperature": 0.3},
        confidence=0.8,
        source="session_001",
        tags=["resolved", "high_confidence"],
        edges=["knot_beta"],
    )

    op.resolve_knot(
        knot_id="knot_beta",
        anterior={"confidence": 0.4, "stance": "undecided", "temperature": 0.6},
        posterior={"confidence": 0.7, "stance": "leaning", "temperature": 0.4},
        confidence=0.6,
        source="session_002",
        tags=["resolved", "medium_confidence"],
        edges=["knot_alpha"],
    )

    op.resolve_knot(
        knot_id="knot_gamma",
        anterior={"confidence": 0.2, "stance": "unknown", "temperature": 0.9},
        posterior={"confidence": 0.5, "stance": "emerging", "temperature": 0.5},
        confidence=0.4,
        source="session_003",
        tags=["partial", "fuzzy"],
        edges=["knot_beta"],
    )

    result = op.run()
    print(json.dumps(result, indent=2, default=str))
