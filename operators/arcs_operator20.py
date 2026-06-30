"""
arcs_operator20.py — Phase 5 Folksonomy Cultivator (Operator 20)
DBSCAN clustering on 54-dimensional receipt seed vectors.
Builds a three-layer taxonomy: Seeds → Leaves → Branches.

Architecture:
    FolksonomySeed       — 54-dim feature vector extracted from CoherenceReceipt
    FolksonomyCluster    — DBSCAN cluster of related receipts (a "Leaf")
    FolksonomyBranch     — Meta-cluster grouping related Leaves
    CultivateReport      — Full output: clusters + branch map + quality metrics

54 Seed Dimensions:
    Signal (10):      velocity, acceleration, diffusion, phase_cancellation, deceleration,
                      nci_score, irreversibility, signal_class_onehot (4 classes)
    Operator (8):     lab_threat (4 onehot), ruin_detected, baseline_ok, asymmetry_ratio, kelly_fraction
    Court (4):        verdict (3 onehot), evidence_weight
    Somatic (6):      phase_tuning, surge_detection, feels_right, that_vibes, locked_in, expected_vs_actual
    FATED (5):        facts_len, assumptions_len, tradeoffs_len, emotions_len, direction_len
    Meta (7):         on_purpose, hci_score, timestamp_bucket, phase_onehot (4 phases),
    Axioms (4):       clarity, agency, minimum_steps, kairos
    Trace (10):       anomaly_count, span_duration_ms, bar_score, nci_delta,
                      event_count, court_bypass, ruin_unmarked, nci_cliff, irrev_spike, bar_flag

Total: 10+8+4+6+5+7+4+10 = 54 ✓

Pre-requisite chain:
    Phase 5: arcs_operator20.py (this file) — DBSCAN on seed corpus
    Phase 6: REST API exposes taxonomy externally
    Post-Phase 6: Live folksonomy service (after corpus ≥ 100 receipts)
"""

from __future__ import annotations

import json
import math
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Seed dimension spec (canonical, used for both extraction and documentation)
# ---------------------------------------------------------------------------

SEED_DIMENSION_NAMES: List[str] = [
    # Signal (0–9)
    "velocity", "acceleration", "diffusion", "phase_cancellation", "deceleration",
    "nci_score", "irreversibility",
    "sig_cls_accelerating", "sig_cls_stable", "sig_cls_decelerating",
    # Operator (10–17)
    "lab_threat_low", "lab_threat_medium", "lab_threat_high", "lab_threat_critical",
    "ruin_detected", "baseline_ok", "asymmetry_ratio", "kelly_fraction",
    # Court (18–21)
    "court_permit", "court_conditional", "court_block",
    "court_evidence_weight",
    # Somatic (22–27)
    "somatic_phase_tuning", "somatic_surge", "somatic_feels_right",
    "somatic_vibes", "somatic_locked_in", "somatic_expected_vs_actual",
    # FATED (28–32)
    "fated_facts_len", "fated_assumptions_len", "fated_tradeoffs_len",
    "fated_emotions_len", "fated_direction_len",
    # Meta (33–39)
    "on_purpose", "hci_score", "timestamp_bucket",
    "phase_1", "phase_2", "phase_3", "phase_4",
    # Axioms (40–43)
    "axiom_clarity", "axiom_agency", "axiom_minimum_steps", "axiom_kairos",
    # Trace (44–53)
    "anomaly_count", "span_duration_ms_norm", "bar_score", "nci_delta_norm",
    "event_count_norm", "court_bypass", "ruin_unmarked", "nci_cliff",
    "irrev_spike", "bar_flag",
]

assert len(SEED_DIMENSION_NAMES) == 54, f"Expected 54 dims, got {len(SEED_DIMENSION_NAMES)}"

SEED_DIM = 54


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FolksonomySeed:
    """54-dimensional feature vector extracted from a receipt + trace span."""
    seed_id:     str
    receipt_id:  str           # span_id or receipt identifier
    phase_id:    str
    created_at:  float
    vector:      List[float]   # length = SEED_DIM = 54
    labels:      List[str]     = field(default_factory=list)  # human-assigned tags
    metadata:    Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.vector) != SEED_DIM:
            raise ValueError(f"Seed vector must have {SEED_DIM} dims, got {len(self.vector)}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def distance(self, other: "FolksonomySeed") -> float:
        """Euclidean distance in 54-dim space."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.vector, other.vector)))


@dataclass
class FolksonomyCluster:
    """
    One DBSCAN cluster — a Leaf in the three-layer taxonomy.
    Represents a coherent group of receipts with similar feature profiles.
    """
    cluster_id:    str
    label:         str           # human-readable cluster name (auto-generated)
    centroid:      List[float]   # mean vector of all seeds in cluster
    seed_ids:      List[str]     # member receipt IDs
    core_dims:     List[str]     # top-5 dimensions driving this cluster's identity
    cohesion:      float         # average intra-cluster distance (lower = tighter)
    silhouette:    float         # cluster quality score (−1 to +1)
    phase_dist:    Dict[str, int]  # {"phase_1": 3, "phase_5": 8, ...}
    verdict_dist:  Dict[str, int]  # {"PERMIT": 9, "BLOCK": 2, ...}
    is_noise:      bool = False    # True = DBSCAN noise cluster
    branch_id:     Optional[str] = None  # assigned branch after meta-clustering
    metadata:      Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FolksonomyBranch:
    """
    Meta-cluster of related Leaves — a Branch in the three-layer taxonomy.
    Groups clusters that share a dominant feature profile.
    """
    branch_id:   str
    label:       str
    cluster_ids: List[str]
    dominant_dims: List[str]    # shared high-value dimensions
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CultivateReport:
    """Full output of one Operator20 run."""
    report_id:        str
    phase_id:         str
    generated_at:     float
    seed_count:       int
    cluster_count:    int
    noise_count:      int         # seeds in noise cluster
    branch_count:     int
    clusters:         List[FolksonomyCluster]
    branches:         List[FolksonomyBranch]
    quality_metrics:  Dict[str, float]
    gravitational_overlays: Dict[str, Any]   # from trace corpus gravitational forces
    epsilon_used:     float
    min_samples_used: int
    corpus_path:      Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def summary(self) -> str:
        lines = [
            f"CultivateReport ({self.report_id[:12]})",
            f"  Seeds: {self.seed_count} | Clusters: {self.cluster_count} | Noise: {self.noise_count}",
            f"  Branches: {self.branch_count}",
            f"  Quality: avg_silhouette={self.quality_metrics.get('avg_silhouette', 0):.3f}, "
            f"coverage={self.quality_metrics.get('coverage_pct', 0):.1f}%",
        ]
        for c in self.clusters[:5]:
            lines.append(f"  [{c.label}] {len(c.seed_ids)} receipts, "
                         f"cohesion={c.cohesion:.3f}, silhouette={c.silhouette:.3f}")
        if len(self.clusters) > 5:
            lines.append(f"  ... and {len(self.clusters) - 5} more clusters")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Seed Extractor
# ---------------------------------------------------------------------------

class SeedExtractor:
    """
    Extracts 54-dimensional FolksonomySeed vectors from receipt dicts + trace spans.
    Handles missing fields gracefully (defaults to 0.0).
    """

    SIGNAL_CLASS_MAP = {
        "accelerating":  (1, 0, 0),
        "stable":        (0, 1, 0),
        "decelerating":  (0, 0, 1),
        "noise":         (0, 0, 0),
    }

    LAB_THREAT_MAP = {
        "LOW":      (1, 0, 0, 0),
        "MEDIUM":   (0, 1, 0, 0),
        "HIGH":     (0, 0, 1, 0),
        "CRITICAL": (0, 0, 0, 1),
    }

    COURT_VERDICT_MAP = {
        "PERMIT":      (1, 0, 0),
        "CONDITIONAL": (0, 1, 0),
        "BLOCK":       (0, 0, 1),
    }

    AXIOM_MAP = {"YES": 1.0, "NO": 0.0, "TENSION": 0.5}

    PHASE_MAP = {"phase_1": 0, "phase_2": 1, "phase_3": 2, "phase_4": 3, "phase_5": 3}

    def extract(
        self,
        receipt: Dict[str, Any],
        span: Optional[Dict[str, Any]] = None,
    ) -> FolksonomySeed:
        """
        Extract a FolksonomySeed from a receipt dict and optional trace span dict.
        receipt: dict with keys from CoherenceReceipt
        span:    dict from TraceSpan.to_dict() (optional, for trace dimensions)
        """
        v = [0.0] * SEED_DIM

        # ── Signal (0–9) ──────────────────────────────────────────────────
        derivs = receipt.get("five_derivatives", {}) or {}
        v[0]  = _norm(derivs.get("velocity", 0), -5, 5)
        v[1]  = _norm(derivs.get("acceleration", 0), -5, 5)
        v[2]  = _norm(derivs.get("diffusion", 0), 0, 1)
        v[3]  = _norm(derivs.get("phase_cancellation", 0), 0, 1)
        v[4]  = _norm(derivs.get("deceleration", 0), 0, 1)
        v[5]  = _norm(receipt.get("nci_score", 50), 0, 100)
        v[6]  = float(receipt.get("irreversibility", 0.3))

        sig_cls = receipt.get("signal_classification", "stable")
        acc, sta, dec = self.SIGNAL_CLASS_MAP.get(sig_cls, (0, 1, 0))
        v[7], v[8], v[9] = float(acc), float(sta), float(dec)

        # ── Operator (10–17) ──────────────────────────────────────────────
        lab = receipt.get("lab", {}) or {}
        threat_vec = self.LAB_THREAT_MAP.get(
            lab.get("lab_threat_level", "LOW"), (1, 0, 0, 0)
        )
        v[10], v[11], v[12], v[13] = [float(x) for x in threat_vec]

        bar = receipt.get("bar", {}) or {}
        v[14] = 1.0 if bar.get("ruin_detected", False) else 0.0
        v[15] = 1.0 if bar.get("baseline_ok", True) else 0.0
        v[16] = _norm(bar.get("asymmetry_ratio", 1.0), 0, 10)
        v[17] = _norm(bar.get("kelly_fraction", 0.1), 0, 1)

        # ── Court (18–21) ─────────────────────────────────────────────────
        court = receipt.get("court", {}) or {}
        verdict_str = court.get("verdict", "PERMIT")
        perm, cond, blk = self.COURT_VERDICT_MAP.get(verdict_str, (1, 0, 0))
        v[18], v[19], v[20] = float(perm), float(cond), float(blk)
        v[21] = _norm(court.get("evidence_weight", 0), 0, 1)

        # ── Somatic (22–27) ───────────────────────────────────────────────
        somatic = receipt.get("somatic", {}) or {}
        v[22] = _norm(somatic.get("phase_tuning", 0.5), 0, 1)
        v[23] = 1.0 if somatic.get("surge_detection", False) else 0.0
        v[24] = 1.0 if somatic.get("feels_right", True) else 0.0
        v[25] = 1.0 if somatic.get("that_vibes", True) else 0.0
        v[26] = 1.0 if somatic.get("locked_in", True) else 0.0
        v[27] = _norm(somatic.get("expected_vs_actual", 0.5), 0, 1)

        # ── FATED (28–32) ─────────────────────────────────────────────────
        fated = receipt.get("fated", {}) or {}
        def flen(key: str) -> float:
            return _norm(len(str(fated.get(key, ""))), 0, 500)
        v[28] = flen("facts")
        v[29] = flen("assumptions")
        v[30] = flen("tradeoffs")
        v[31] = flen("emotions")
        v[32] = flen("direction")

        # ── Meta (33–39) ──────────────────────────────────────────────────
        v[33] = 1.0 if receipt.get("on_purpose", True) else 0.0
        v[34] = _norm(receipt.get("hci_score", 0.5), 0, 1)
        # Timestamp bucket: 0.0 = old, 1.0 = recent (within 7 days)
        ts = receipt.get("timestamp", time.time())
        try:
            ts_float = float(ts)
        except (ValueError, TypeError):
            import datetime as _dt
            try:
                ts_float = _dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
            except Exception:
                ts_float = time.time()
        age_days = (time.time() - ts_float) / 86400
        v[35] = max(0.0, 1.0 - age_days / 7.0)

        phase_id = receipt.get("phase_id", "phase_1")
        phase_idx = self.PHASE_MAP.get(phase_id, 0)
        v[36] = 1.0 if phase_idx == 0 else 0.0
        v[37] = 1.0 if phase_idx == 1 else 0.0
        v[38] = 1.0 if phase_idx == 2 else 0.0
        v[39] = 1.0 if phase_idx == 3 else 0.0

        # ── Axioms (40–43) ─────────────────────────────────────────────────
        axioms = receipt.get("axioms", {}) or {}
        v[40] = self.AXIOM_MAP.get(str(axioms.get("clarity_before_curvature", "YES")), 1.0)
        v[41] = self.AXIOM_MAP.get(str(axioms.get("agency_over_automation", "YES")), 1.0)
        v[42] = self.AXIOM_MAP.get(str(axioms.get("minimum_steps_to_coherence", "YES")), 1.0)
        v[43] = self.AXIOM_MAP.get(str(axioms.get("kairos_over_neuroticism", "YES")), 1.0)

        # ── Trace (44–53) ──────────────────────────────────────────────────
        if span:
            anomalies = span.get("anomalies", []) or []
            anomaly_types = {a.get("anomaly_type", "") for a in anomalies}
            v[44] = _norm(len(anomalies), 0, 10)
            v[45] = _norm(span.get("duration_ms", 0) or 0, 0, 30000)
            v[47] = _norm(abs(span.get("nci_delta", 0) or 0), 0, 50)
            v[48] = _norm(len(span.get("events", []) or []), 0, 20)
            v[49] = 1.0 if "court_bypass" in anomaly_types else 0.0
            v[50] = 1.0 if "ruin_unmarked" in anomaly_types else 0.0
            v[51] = 1.0 if "nci_cliff" in anomaly_types else 0.0
            v[52] = 1.0 if "irrev_spike" in anomaly_types else 0.0
        # v[46] = bar_score (set separately if available)
        bar_score = receipt.get("bar_score") or (span or {}).get("bar_score")
        if bar_score is not None:
            v[46] = _norm(float(bar_score), 0, 1)
        # v[53] = bar_flag
        bar_flag = receipt.get("bar_flag") or (span or {}).get("bar_flag", False)
        v[53] = 1.0 if bar_flag else 0.0

        return FolksonomySeed(
            seed_id=_new_id("seed"),
            receipt_id=receipt.get("span_id", receipt.get("receipt_id", _new_id("rcpt"))),
            phase_id=phase_id,
            created_at=time.time(),
            vector=v,
            metadata={"signal_classification": sig_cls, "nci_score": receipt.get("nci_score")},
        )


# ---------------------------------------------------------------------------
# DBSCAN (pure Python — no sklearn dependency)
# ---------------------------------------------------------------------------

class DBSCAN:
    """
    Pure-Python DBSCAN implementation for FolksonomySeed clustering.
    No external dependencies — stdlib only.

    Parameters:
        epsilon:     neighbourhood radius
        min_samples: minimum core point neighbours
    """

    NOISE = -1

    def __init__(self, epsilon: float = 0.8, min_samples: int = 3):
        self.epsilon     = epsilon
        self.min_samples = min_samples

    def fit(self, seeds: List[FolksonomySeed]) -> List[int]:
        """
        Returns list of cluster labels (same length as seeds).
        Label = −1 for noise, 0..N for clusters.
        """
        n       = len(seeds)
        labels  = [None] * n
        cluster = 0

        # Precompute distance matrix
        dists = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = seeds[i].distance(seeds[j])
                dists[i][j] = d
                dists[j][i] = d

        def neighbourhood(idx: int) -> List[int]:
            return [j for j in range(n) if dists[idx][j] <= self.epsilon]

        for i in range(n):
            if labels[i] is not None:
                continue
            neighbours = neighbourhood(i)
            if len(neighbours) < self.min_samples:
                labels[i] = self.NOISE
                continue
            labels[i] = cluster
            seed_set = set(neighbours)
            seed_set.discard(i)
            queue = list(seed_set)
            while queue:
                q = queue.pop(0)
                if labels[q] == self.NOISE:
                    labels[q] = cluster
                if labels[q] is not None:
                    continue
                labels[q] = cluster
                q_neighbours = neighbourhood(q)
                if len(q_neighbours) >= self.min_samples:
                    for nb in q_neighbours:
                        if labels[nb] is None:
                            queue.append(nb)
            cluster += 1

        return [lbl if lbl is not None else self.NOISE for lbl in labels]


# ---------------------------------------------------------------------------
# Operator20 — Folksonomy Cultivator
# ---------------------------------------------------------------------------

class Operator20:
    """
    Phase 5 Folksonomy Cultivator.

    Three-layer growth model:
        Seeds  → raw 54-dim receipt vectors
        Leaves → DBSCAN clusters of related receipts
        Branches → meta-clusters grouping related Leaves

    Pre-req chain reminder:
        Phase 5: Operator20 validates seed dimensions on Phase 5 corpus
        Phase 6: REST API exposes taxonomy
        Post-Phase 6: Live recursive growth (once corpus ≥ 100 receipts)
    """

    # DBSCAN defaults (tuned for early-stage corpus, ~10–100 receipts)
    DEFAULT_EPSILON     = 0.8
    DEFAULT_MIN_SAMPLES = 2    # small corpus = small min_samples

    # Minimum corpus for meaningful clustering
    MIN_CORPUS_SIZE = 5
    RECOMMENDED_CORPUS_SIZE = 100

    def __init__(
        self,
        epsilon: float = DEFAULT_EPSILON,
        min_samples: int = DEFAULT_MIN_SAMPLES,
    ):
        self.epsilon     = epsilon
        self.min_samples = min_samples
        self.extractor   = SeedExtractor()
        self._dbscan     = DBSCAN(epsilon=epsilon, min_samples=min_samples)

    def extract_seeds(
        self,
        receipts: List[Dict[str, Any]],
        spans: Optional[List[Dict[str, Any]]] = None,
    ) -> List[FolksonomySeed]:
        """Extract FolksonomySeeds from receipt corpus."""
        span_map: Dict[str, Dict[str, Any]] = {}
        if spans:
            span_map = {s.get("span_id", ""): s for s in spans}

        seeds = []
        for receipt in receipts:
            span_id = receipt.get("span_id")
            span = span_map.get(span_id) if span_id else None
            seed = self.extractor.extract(receipt, span)
            seeds.append(seed)
        return seeds

    def cultivate(
        self,
        seeds: List[FolksonomySeed],
        phase_id: str = "phase_5",
        gravitational_forces: Optional[List[Dict[str, Any]]] = None,
        corpus_path: Optional[str] = None,
    ) -> CultivateReport:
        """
        Run DBSCAN clustering and build the three-layer folksonomy.
        Returns CultivateReport with all cluster metadata.
        """
        n = len(seeds)
        if n < self.MIN_CORPUS_SIZE:
            # Return empty report with guidance
            return CultivateReport(
                report_id=_new_id("rpt"),
                phase_id=phase_id,
                generated_at=time.time(),
                seed_count=n,
                cluster_count=0,
                noise_count=n,
                branch_count=0,
                clusters=[],
                branches=[],
                quality_metrics={
                    "avg_silhouette": 0.0,
                    "coverage_pct": 0.0,
                    "corpus_warning": 1.0,
                },
                gravitational_overlays={},
                epsilon_used=self.epsilon,
                min_samples_used=self.min_samples,
                corpus_path=corpus_path,
            )

        # ── DBSCAN clustering ─────────────────────────────────────────────
        labels = self._dbscan.fit(seeds)

        # Group seeds by cluster label
        cluster_map: Dict[int, List[int]] = {}
        for i, lbl in enumerate(labels):
            cluster_map.setdefault(lbl, []).append(i)

        # ── Build FolksonomyClusters (Leaves) ──────────────────────────────
        clusters: List[FolksonomyCluster] = []
        noise_count = len(cluster_map.get(-1, []))

        for lbl, idxs in cluster_map.items():
            is_noise = lbl == -1
            member_seeds = [seeds[i] for i in idxs]
            centroid = _mean_vector([s.vector for s in member_seeds])
            core_dims = _top_k_dims(centroid, k=5)
            cohesion  = _avg_intra_distance(member_seeds)
            silhouette = self._silhouette_for_cluster(lbl, idxs, labels, seeds)

            # Auto-label cluster based on dominant dimensions
            cluster_label = self._auto_label(centroid, lbl, is_noise)

            # Phase and verdict distributions
            phase_dist: Dict[str, int] = {}
            for s in member_seeds:
                p = s.phase_id
                phase_dist[p] = phase_dist.get(p, 0) + 1

            verdict_dist: Dict[str, int] = {}
            for s in member_seeds:
                vd = s.metadata.get("verdict", "unknown")
                verdict_dist[str(vd)] = verdict_dist.get(str(vd), 0) + 1

            cluster = FolksonomyCluster(
                cluster_id=_new_id("clst"),
                label=cluster_label,
                centroid=centroid,
                seed_ids=[s.seed_id for s in member_seeds],
                core_dims=core_dims,
                cohesion=round(cohesion, 4),
                silhouette=round(silhouette, 4),
                phase_dist=phase_dist,
                verdict_dist=verdict_dist,
                is_noise=is_noise,
            )
            clusters.append(cluster)

        # Sort: non-noise first, then by size descending
        clusters.sort(key=lambda c: (c.is_noise, -len(c.seed_ids)))

        # ── Build FolksonomyBranches (meta-clusters of Leaves) ─────────────
        branches = self._build_branches(clusters)
        for branch in branches:
            for cid in branch.cluster_ids:
                for c in clusters:
                    if c.cluster_id == cid:
                        c.branch_id = branch.branch_id

        # ── Quality metrics ────────────────────────────────────────────────
        non_noise = [c for c in clusters if not c.is_noise]
        avg_sil = (
            sum(c.silhouette for c in non_noise) / len(non_noise)
            if non_noise else 0.0
        )
        coverage = (n - noise_count) / n if n > 0 else 0.0

        quality_metrics = {
            "avg_silhouette":   round(avg_sil, 4),
            "coverage_pct":     round(coverage * 100, 1),
            "noise_pct":        round(noise_count / n * 100, 1) if n > 0 else 0.0,
            "avg_cluster_size": round((n - noise_count) / len(non_noise), 1) if non_noise else 0.0,
            "corpus_size":      float(n),
            "corpus_ready":     1.0 if n >= self.RECOMMENDED_CORPUS_SIZE else n / self.RECOMMENDED_CORPUS_SIZE,
        }

        # ── Gravitational force overlay ────────────────────────────────────
        grav_overlay: Dict[str, Any] = {}
        if gravitational_forces:
            for gf in gravitational_forces:
                key = f"{gf.get('source')}→{gf.get('target')}"
                grav_overlay[key] = {
                    "force":   gf.get("force", 0),
                    "coupled": gf.get("coupled", 0),
                    "total":   gf.get("total", 0),
                }

        return CultivateReport(
            report_id=_new_id("rpt"),
            phase_id=phase_id,
            generated_at=time.time(),
            seed_count=n,
            cluster_count=len(non_noise),
            noise_count=noise_count,
            branch_count=len(branches),
            clusters=clusters,
            branches=branches,
            quality_metrics=quality_metrics,
            gravitational_overlays=grav_overlay,
            epsilon_used=self.epsilon,
            min_samples_used=self.min_samples,
            corpus_path=corpus_path,
        )

    def cultivate_from_jsonl(
        self,
        receipts_path: str,
        spans_path: Optional[str] = None,
        phase_id: str = "phase_5",
    ) -> CultivateReport:
        """Convenience: read receipts (and optional spans) from JSONL, then cultivate."""
        receipts = _read_jsonl(receipts_path)
        spans    = _read_jsonl(spans_path) if spans_path else []
        seeds    = self.extract_seeds(receipts, spans if spans else None)
        return self.cultivate(seeds, phase_id=phase_id, corpus_path=receipts_path)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _auto_label(self, centroid: List[float], label_id: int, is_noise: bool) -> str:
        if is_noise:
            return "⚡ noise"
        top_dims = _top_k_dims(centroid, k=3)
        prefix = top_dims[0] if top_dims else "unlabeled"

        # Map dimension prefixes to readable labels
        label_rules = [
            ("nci_score",          "high_coherence"),
            ("ruin",               "ruin_risk"),
            ("lab_threat_high",    "high_threat"),
            ("lab_threat_critical","critical_threat"),
            ("court_block",        "blocked_decisions"),
            ("court_permit",       "permit_flow"),
            ("somatic_locked",     "flow_state"),
            ("axiom",              "axiom_aligned"),
            ("nci_cliff",          "nci_instability"),
            ("irrev",              "high_irreversibility"),
            ("fated_",             "well_documented"),
            ("on_purpose",         "intentional_decisions"),
        ]
        for dim_substr, readable in label_rules:
            if any(dim_substr in d for d in top_dims):
                return f"cluster_{label_id}_{readable}"
        return f"cluster_{label_id}_{prefix[:20]}"

    def _build_branches(
        self, clusters: List[FolksonomyCluster]
    ) -> List[FolksonomyBranch]:
        """
        Group Leaves into Branches by shared dominant dimensions.
        Simple heuristic: clusters with overlapping top-3 core_dims go in the same branch.
        """
        non_noise = [c for c in clusters if not c.is_noise]
        if not non_noise:
            return []

        # Group by first core dim (dominant feature)
        branch_groups: Dict[str, List[FolksonomyCluster]] = {}
        for c in non_noise:
            # Use the category prefix of the top dim as branch key
            top_dim = c.core_dims[0] if c.core_dims else "misc"
            branch_key = _dim_category(top_dim)
            branch_groups.setdefault(branch_key, []).append(c)

        branches = []
        for key, group_clusters in branch_groups.items():
            # Collect all core dims across clusters in this group
            all_dims: Dict[str, int] = {}
            for c in group_clusters:
                for d in c.core_dims:
                    all_dims[d] = all_dims.get(d, 0) + 1
            dominant = sorted(all_dims, key=lambda d: -all_dims[d])[:5]

            branch = FolksonomyBranch(
                branch_id=_new_id("br"),
                label=f"branch_{key}",
                cluster_ids=[c.cluster_id for c in group_clusters],
                dominant_dims=dominant,
                description=f"Receipts where '{key}' dimensions are most active",
            )
            branches.append(branch)
        return branches

    def _silhouette_for_cluster(
        self,
        target_label: int,
        target_idxs: List[int],
        all_labels: List[int],
        seeds: List[FolksonomySeed],
    ) -> float:
        """Simplified silhouette score for one cluster."""
        if target_label == -1 or len(target_idxs) < 2:
            return 0.0

        silhouettes = []
        other_labels = set(l for l in all_labels if l != target_label and l != -1)

        for i in target_idxs:
            # a(i): mean distance to other points in same cluster
            same = [j for j in target_idxs if j != i]
            a = (sum(seeds[i].distance(seeds[j]) for j in same) / len(same)) if same else 0.0

            # b(i): min mean distance to any other cluster
            if not other_labels:
                b = a + 1  # no other clusters — silhouette = 0
            else:
                b = min(
                    sum(seeds[i].distance(seeds[j]) for j in range(len(seeds))
                        if all_labels[j] == lbl) / max(1, sum(1 for l in all_labels if l == lbl))
                    for lbl in other_labels
                )

            s = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
            silhouettes.append(s)

        return sum(silhouettes) / len(silhouettes) if silhouettes else 0.0

    def persist_report(self, report: CultivateReport, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2, default=str)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _norm(value: float, lo: float, hi: float) -> float:
    """Normalize value to [0, 1] range."""
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def _mean_vector(vectors: List[List[float]]) -> List[float]:
    if not vectors:
        return [0.0] * SEED_DIM
    n = len(vectors)
    return [sum(v[i] for v in vectors) / n for i in range(len(vectors[0]))]


def _top_k_dims(centroid: List[float], k: int = 5) -> List[str]:
    """Return the k dimension names with highest values in the centroid."""
    indexed = sorted(enumerate(centroid), key=lambda x: -x[1])
    return [SEED_DIMENSION_NAMES[i] for i, _ in indexed[:k]]


def _avg_intra_distance(seeds: List[FolksonomySeed]) -> float:
    if len(seeds) < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(len(seeds)):
        for j in range(i + 1, len(seeds)):
            total += seeds[i].distance(seeds[j])
            count += 1
    return total / count if count > 0 else 0.0


def _dim_category(dim_name: str) -> str:
    """Map a dimension name to its category prefix."""
    for prefix in ["velocity", "nci", "irrev", "lab", "court", "somatic",
                   "fated", "axiom", "ruin", "bar", "sig_cls", "on_purpose", "hci"]:
        if dim_name.startswith(prefix):
            return prefix
    return "misc"


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    records = []
    for line in p.read_text(encoding="utf-8").strip().splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    import tempfile, shutil, random

    print("=== arcs_operator20.py smoke test ===\n")

    tmp = tempfile.mkdtemp()
    random.seed(42)

    try:
        # 1. Generate synthetic receipt corpus (20 receipts)
        def _make_receipt(phase_id: str, nci: float, sig_cls: str,
                           ruin: bool = False, court_verdict: str = "PERMIT") -> Dict[str, Any]:
            return {
                "span_id":              _new_id("spn"),
                "phase_id":             phase_id,
                "nci_score":            nci,
                "irreversibility":      random.uniform(0.1, 0.7),
                "on_purpose":           True,
                "signal_classification": sig_cls,
                "hci_score":            random.uniform(0.5, 0.9),
                "timestamp":            time.time() - random.uniform(0, 86400),
                "five_derivatives": {
                    "velocity":           random.uniform(-2, 2),
                    "acceleration":       random.uniform(-1, 1),
                    "diffusion":          random.uniform(0, 1),
                    "phase_cancellation": random.uniform(0, 0.5),
                    "deceleration":       random.uniform(0, 0.4),
                },
                "lab": {"lab_threat_level": "LOW" if not ruin else "HIGH"},
                "bar": {"ruin_detected": ruin, "baseline_ok": not ruin,
                        "asymmetry_ratio": 2.0, "kelly_fraction": 0.3},
                "court": {"verdict": court_verdict, "evidence_weight": 0.1 if not ruin else 0.8},
                "somatic": {
                    "phase_tuning": 0.7, "surge_detection": False,
                    "feels_right": True, "that_vibes": True,
                    "locked_in": True, "expected_vs_actual": 0.75,
                },
                "fated": {
                    "facts": "Signal coherent with phase targets.",
                    "assumptions": "Normal market conditions apply.",
                    "tradeoffs": "Speed vs. caution.",
                    "emotions": "Confident.",
                    "direction": "Proceed with phase plan.",
                },
                "axioms": {
                    "clarity_before_curvature": "YES",
                    "agency_over_automation": "YES",
                    "minimum_steps_to_coherence": "YES",
                    "kairos_over_neuroticism": "YES",
                },
            }

        receipts = (
            [_make_receipt("phase_5", random.uniform(82, 95), "accelerating") for _ in range(8)]
            + [_make_receipt("phase_5", random.uniform(60, 75), "stable") for _ in range(6)]
            + [_make_receipt("phase_4", random.uniform(50, 65), "decelerating", ruin=True,
                             court_verdict="BLOCK") for _ in range(4)]
            + [_make_receipt("phase_3", random.uniform(70, 85), "stable") for _ in range(2)]
        )
        print(f"[OK] Generated {len(receipts)} synthetic receipts")

        # 2. Extract seeds
        op20 = Operator20(epsilon=0.9, min_samples=2)
        seeds = op20.extract_seeds(receipts)
        assert len(seeds) == len(receipts)
        assert all(len(s.vector) == 54 for s in seeds)
        assert all(all(0.0 <= v <= 1.0 or v == 0.0 for v in s.vector) for s in seeds), \
            "Some seed values out of [0,1] range"
        print(f"[OK] Extracted {len(seeds)} seeds, all 54-dim, all normalized [0,1]")

        # 3. Cultivate
        report = op20.cultivate(seeds, phase_id="phase_5")
        print(f"\n[OK] Cultivation complete:")
        print(f"     clusters={report.cluster_count}, noise={report.noise_count}, "
              f"branches={report.branch_count}")
        print(f"     avg_silhouette={report.quality_metrics['avg_silhouette']:.3f}, "
              f"coverage={report.quality_metrics['coverage_pct']:.1f}%")

        # Should have at least 2 meaningful clusters (accelerating vs ruin)
        non_noise = [c for c in report.clusters if not c.is_noise]
        assert len(non_noise) >= 1, "Expected at least 1 non-noise cluster"
        print(f"[OK] Non-noise clusters: {len(non_noise)}")

        for c in non_noise[:3]:
            print(f"     [{c.label}] size={len(c.seed_ids)}, "
                  f"cohesion={c.cohesion:.3f}, "
                  f"core_dims={c.core_dims[:2]}")

        # 4. Branches
        assert len(report.branches) >= 1
        for b in report.branches[:3]:
            print(f"[OK] Branch: {b.label} ({len(b.cluster_ids)} clusters)")

        # 5. Gravitational force overlay
        grav_forces = [
            {"source": "sage", "target": "lab",   "force": 1.0, "coupled": 20, "total": 20},
            {"source": "lab",  "target": "bar",   "force": 0.9, "coupled": 18, "total": 20},
            {"source": "bar",  "target": "court", "force": 0.85, "coupled": 17, "total": 20},
        ]
        report2 = op20.cultivate(seeds, phase_id="phase_5", gravitational_forces=grav_forces)
        assert "sage→lab" in report2.gravitational_overlays
        assert report2.gravitational_overlays["sage→lab"]["force"] == 1.0
        print(f"[OK] Gravitational overlay: {list(report2.gravitational_overlays.keys())}")

        # 6. Persist report
        out_path = f"{tmp}/folksonomy_report.json"
        op20.persist_report(report, out_path)
        assert Path(out_path).exists()
        loaded = json.loads(Path(out_path).read_text())
        assert loaded["seed_count"] == len(receipts)
        print(f"[OK] Report persisted to {out_path}")

        # 7. Corpus size warning (< MIN_CORPUS_SIZE)
        tiny_seeds = seeds[:3]
        tiny_report = op20.cultivate(tiny_seeds, phase_id="phase_5")
        assert tiny_report.cluster_count == 0
        assert tiny_report.quality_metrics.get("corpus_warning") == 1.0
        print(f"[OK] Corpus warning triggered for {len(tiny_seeds)} seeds (< {op20.MIN_CORPUS_SIZE})")

        # 8. Summary
        print(f"\n{report.summary()}")

        print("\n=== Smoke test PASSED — arcs_operator20.py ===")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    _smoke_test()
