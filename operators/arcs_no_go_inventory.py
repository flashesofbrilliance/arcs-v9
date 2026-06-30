"""
ARCS v9 — No-Go Inventory (NGI) v1.0
Kintsugi ROM artifact. Append-only catalog of failure-class events.
Every NGI entry is tagged to a receipt_id for correlation.

Four failure classes (per arcs-no-go-inventory-v1.0.md):
  BSS_WALL         — Blind Spot Structural Wall (architectural assumption trap)
  TRIUNE_REMAINDER — Triune Logic imbalance (chrono/kairo/yoav misfire)
  KINTSUGI_SCAR   — Kintsugi repair pattern (previously broken, re-emerged)
  STRUCTURAL_BLIND — Structural Blind Spot (phase-level assumption failure)

Usage:
    from arcs_no_go_inventory import NoGoInventory, NGIClass
    ngi = NoGoInventory()
    entry_id = ngi.log(
        ngi_class=NGIClass.BSS_WALL,
        trigger="Court detected ruin risk on irreversibility > 0.7",
        receipt_id="dr-2026-04-20-ABC12",
        notes="VCE v2.0 import snuck into Phase 7 PR",
    )
"""

from __future__ import annotations
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class NGIClass(str, Enum):
    BSS_WALL = "BSS_WALL"
    TRIUNE_REMAINDER = "TRIUNE_REMAINDER"
    KINTSUGI_SCAR = "KINTSUGI_SCAR"
    STRUCTURAL_BLIND = "STRUCTURAL_BLIND"


@dataclass
class NGIEntry:
    id: str
    ngi_class: NGIClass
    trigger: str
    logged_at: str
    receipt_id: Optional[str] = None
    notes: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ngi_class": self.ngi_class.value,
            "trigger": self.trigger,
            "logged_at": self.logged_at,
            "receipt_id": self.receipt_id,
            "notes": self.notes,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
            "resolution_notes": self.resolution_notes,
        }


class NoGoInventory:
    """
    Append-only No-Go Inventory. Defaults to ARCS_NGI_PATH env var or
    ~/.arcs/no_go_inventory.jsonl.
    """

    DEFAULT_PATH = Path.home() / ".arcs" / "no_go_inventory.jsonl"

    def __init__(self, path: Optional[str | Path] = None) -> None:
        self.path = Path(path or os.getenv("ARCS_NGI_PATH", self.DEFAULT_PATH))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        ngi_class: NGIClass,
        trigger: str,
        receipt_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        entry = NGIEntry(
            id=f"ngi-{uuid.uuid4().hex[:8].upper()}",
            ngi_class=ngi_class,
            trigger=trigger,
            logged_at=datetime.now(timezone.utc).isoformat(),
            receipt_id=receipt_id,
            notes=notes,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")
        return entry.id

    def resolve(self, entry_id: str, resolution_notes: Optional[str] = None) -> None:
        """Mark an NGI entry as resolved (tombstone append)."""
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": entry_id,
                "resolved": True,
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolution_notes": resolution_notes,
                "_tombstone": True,
            }) + "\n")

    def list(
        self,
        ngi_class: Optional[NGIClass] = None,
        receipt_id: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
    ) -> list[NGIEntry]:
        if not self.path.exists():
            return []
        # Build map, applying tombstones
        entries: dict[str, dict] = {}
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                raw = json.loads(line)
                eid = raw["id"]
                if raw.get("_tombstone"):
                    if eid in entries:
                        entries[eid].update({
                            "resolved": raw.get("resolved", True),
                            "resolved_at": raw.get("resolved_at"),
                            "resolution_notes": raw.get("resolution_notes"),
                        })
                else:
                    entries[eid] = raw

        results = []
        for raw in entries.values():
            if ngi_class and raw.get("ngi_class") != ngi_class.value:
                continue
            if receipt_id and raw.get("receipt_id") != receipt_id:
                continue
            if resolved is not None and raw.get("resolved", False) != resolved:
                continue
            results.append(NGIEntry(
                id=raw["id"],
                ngi_class=NGIClass(raw["ngi_class"]),
                trigger=raw["trigger"],
                logged_at=raw["logged_at"],
                receipt_id=raw.get("receipt_id"),
                notes=raw.get("notes"),
                resolved=raw.get("resolved", False),
                resolved_at=raw.get("resolved_at"),
                resolution_notes=raw.get("resolution_notes"),
            ))
            if len(results) >= limit:
                break
        return results

    def for_receipt(self, receipt_id: str) -> list[NGIEntry]:
        return self.list(receipt_id=receipt_id)


# ── Module-level default instance ────────────────────────────────────────────

_default_ngi: Optional[NoGoInventory] = None

def get_ngi() -> NoGoInventory:
    global _default_ngi
    if _default_ngi is None:
        _default_ngi = NoGoInventory()
    return _default_ngi
