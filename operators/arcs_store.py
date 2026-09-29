"""
arcs_store.py
ARCS v9 — Receipt Store + Query API
Phase 3: READ-WRITE

The store is the ARCS memory layer. It:
  1. Archives all PipelineResults (append-only, immutable)
  2. Provides query API (by phase, NCI range, verdict, satoshi status)
  3. Prepares Operator20 seed vectors for Phase 5 DBSCAN clustering
  4. Exports receipts to JSON for Zoetrope BriefingDock

Canon principle: "Receipts are immutable. Decision logs are append-only."
Phase 5 will extend this with Yoav Protocol serializability.
Phase 5 will also implement the DBSCAN clustering on stored seeds.
"""

from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from arcs_primitives import AXIOM_YES, AXIOM_NO, AXIOM_TENSION
from arcs_pipeline_v1 import PipelineResult

STORE_VERSION = "v1.0-phase3"
DEFAULT_STORE_PATH = Path(__file__).parent / "arcs_receipts_store.json"


# ─────────────────────────────────────────────
# STORE
# ─────────────────────────────────────────────

class ARCSStore:
    """
    Append-only receipt store with query API.

    Storage format: JSON file (single source of truth for Phase 3).
    Phase 5 will migrate to a proper database with Yoav Protocol guarantees.

    Key properties:
      - Append-only: receipts are never modified or deleted
      - Indexed: by phase, NCI, satoshi status, verdict
      - Seed-ready: Operator20 seeds extracted and queryable
    """

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = Path(store_path or DEFAULT_STORE_PATH)
        self._receipts: List[Dict[str, Any]] = []
        self._load()

    # ── Persistence ──────────────────────────

    def _load(self) -> None:
        if self.store_path.exists():
            try:
                with open(self.store_path, "r") as f:
                    data = json.load(f)
                    self._receipts = data.get("receipts", [])
            except (json.JSONDecodeError, KeyError):
                self._receipts = []

    def _save(self) -> None:
        payload = {
            "store_version": STORE_VERSION,
            "last_updated": time.time(),
            "total_receipts": len(self._receipts),
            "receipts": self._receipts,
        }
        with open(self.store_path, "w") as f:
            json.dump(payload, f, indent=2)

    # ── Write ─────────────────────────────────

    def append(self, result: PipelineResult) -> str:
        """
        Appends a PipelineResult to the store.
        Returns the receipt ID (timestamp-based).
        Immutable: once appended, a receipt cannot be modified.
        """
        receipt_id = f"receipt_{result.phase_id}_{int(result.timestamp)}"
        record = {
            "receipt_id": receipt_id,
            "stored_at": time.time(),
            **result.to_dict(),
        }
        self._receipts.append(record)
        self._save()
        return receipt_id

    # ── Query API ─────────────────────────────

    def all(self) -> List[Dict[str, Any]]:
        """Returns all receipts (read-only view)."""
        return list(self._receipts)

    def count(self) -> int:
        return len(self._receipts)

    def by_phase(self, phase_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._receipts if r.get("phase_id") == phase_id]

    def by_status(self, status: str) -> List[Dict[str, Any]]:
        return [r for r in self._receipts if r.get("status") == status]

    def by_nci_range(self, min_nci: float, max_nci: float) -> List[Dict[str, Any]]:
        return [
            r for r in self._receipts
            if min_nci <= r.get("pipeline_nci", 0.0) <= max_nci
        ]

    def satoshis(self) -> List[Dict[str, Any]]:
        """Returns all receipts where SAGE's is_satoshi = True."""
        return [
            r for r in self._receipts
            if r.get("sage", {}) and r["sage"].get("is_satoshi", False)
        ]

    def by_verdict(self, verdict_substring: str) -> List[Dict[str, Any]]:
        return [
            r for r in self._receipts
            if verdict_substring.upper() in r.get("pipeline_verdict", "").upper()
        ]

    def latest(self, n: int = 5) -> List[Dict[str, Any]]:
        return self._receipts[-n:]

    def highest_nci(self, n: int = 5) -> List[Dict[str, Any]]:
        return sorted(self._receipts, key=lambda r: r.get("pipeline_nci", 0.0), reverse=True)[:n]

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        """Generic filter with a predicate function."""
        return [r for r in self._receipts if predicate(r)]

    # ── Librarian (Operator 21) ───────────────

    def recommend(self, q: str, budget: int = 16000, stakes: str = "medium", n_max: int = 12,
                  classes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Operator 21 entrypoint: retrieve by EXPECTED VALUE under a context budget
        (policy: _SEEDS/index.jsonl#seed-service-librarian-retrieval-policy).
        The store's own receipts join the corpus (ADRs, seeds, tao, LEGEND/LORE,
        ledgers, memory, prior picks) as `store-receipt` candidates. The ranking
        lives in operators/arcs_librarian.py; this method only adds the store.
        Output contract: items[{id, value, cost, read_friction, backing|null,
        freshness, why_load_bearing, quadrant}] + what_confirmed / what_unconfirmed
        + reserve_ratio + curation_debt + ouroboros. Surfaced, never acted on.
        """
        from arcs_librarian import Candidate, Librarian
        extra = [Candidate.from_store_receipt(r) for r in self._receipts]
        return Librarian(extra_candidates=extra).recommend(q, budget=budget, stakes=stakes, n_max=n_max, classes=classes)

    # ── Operator20 Seed Export ────────────────

    def seed_matrix(self) -> List[Dict[str, Any]]:
        """
        Returns all Operator20 seed vectors as a list of dicts.
        Each dict is one receipt's seed vector.
        Phase 5: feed this into DBSCAN for folksonomy clustering.
        """
        return [r.get("operator20_seeds", {}) for r in self._receipts if r.get("operator20_seeds")]

    def seed_dimension_count(self) -> int:
        """Returns the number of seed dimensions (from the first receipt)."""
        matrix = self.seed_matrix()
        return len(matrix[0]) if matrix else 0

    # ── Stats ─────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        if not self._receipts:
            return {"total": 0}

        ncis = [r.get("pipeline_nci", 0.0) for r in self._receipts]
        satoshi_count = len(self.satoshis())
        complete = len(self.by_status("COMPLETE"))
        blocked  = len(self.by_status("BLOCKED"))

        phase_dist: Dict[str, int] = {}
        for r in self._receipts:
            p = r.get("phase_id", "unknown")
            phase_dist[p] = phase_dist.get(p, 0) + 1

        return {
            "total": len(self._receipts),
            "complete": complete,
            "blocked": blocked,
            "satoshis": satoshi_count,
            "satoshi_rate": round(satoshi_count / len(self._receipts), 3),
            "nci_mean": round(sum(ncis) / len(ncis), 1),
            "nci_max": max(ncis),
            "nci_min": min(ncis),
            "phase_distribution": phase_dist,
            "seed_dimensions": self.seed_dimension_count(),
            "store_version": STORE_VERSION,
        }

    def print_stats(self) -> None:
        s = self.stats()
        print("\n── ARCS Store Stats ─────────────────────────────────────")
        for k, v in s.items():
            print(f"  {k:25}: {v}")
        print("─" * 60)

    # ── Zoetrope Export ───────────────────────

    def to_zoetrope_payload(self, n: int = 10) -> Dict[str, Any]:
        """
        Exports the latest N receipts in a format ready for
        Zoetrope's BriefingDock (via sage_bridge.js).
        """
        latest = self.latest(n)
        return {
            "receipts": latest,
            "stats": self.stats(),
            "exported_at": time.time(),
        }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import numpy as np
    import tempfile
    from arcs_primitives import FATEDReasoning, SomaticReading, AxiomCheck, CoherenceSignal
    from arcs_pipeline_v1 import ARCSPipeline

    print("=== ARCS Store Smoke Test ===\n")

    # Use a temp file so we don't pollute the real store
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

    store = ARCSStore(store_path=temp_path)

    pipeline = ARCSPipeline()

    # Run two pipeline iterations to populate the store
    for i, (nci_base, label) in enumerate([
        (65, "Early phase signal (low NCI baseline)"),
        (87, "Phase 3 complete signal (high NCI baseline)"),
    ]):
        signal = CoherenceSignal(
            signal=np.linspace(nci_base, nci_base + 25, 10),
            domain="meta",
            label=label,
        )
        fated = FATEDReasoning(
            facts=f"Test run {i+1}. NCI base: {nci_base}.",
            assumptions="Store test. Verify append + query.",
            tradeoffs="Test overhead vs. validation confidence.",
            emotions="Neutral. This is automated.",
            direction="Archive result. Verify query API.",
        )
        axioms = AxiomCheck(AXIOM_YES, AXIOM_YES, AXIOM_YES, AXIOM_YES)
        somatic = SomaticReading(0.7, 0.8, 0.75, 0.7, 0.85, 0.7)

        result = pipeline.run(
            signal=signal, fated=fated, axioms=axioms, somatic=somatic,
            hci_score=float(nci_base), phase_id="phase_3",
            next_action="Continue Phase 3.", irreversibility=0.2,
        )
        receipt_id = store.append(result)
        print(f"  Stored: {receipt_id} | NCI: {result.pipeline_nci:.1f} | Status: {result.status}")

    store.print_stats()

    print(f"\nSatoshi receipts: {len(store.satoshis())}")
    print(f"High NCI (>80):   {len(store.by_nci_range(80, 100))}")
    print(f"Seed dimensions:  {store.seed_dimension_count()}")
    print(f"\nZoetrope payload keys: {list(store.to_zoetrope_payload().keys())}")

    # Cleanup
    temp_path.unlink()
    print("\n✅ Store verified.")
