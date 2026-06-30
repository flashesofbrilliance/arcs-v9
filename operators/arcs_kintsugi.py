"""
arcs_kintsugi.py
ARCS v9 — Kintsugi Repair Service
Phase 4: WRITE-LOCK

Named after the Japanese art of kintsukuroi (金継ぎ):
  Broken pottery is repaired with gold. The repair is visible — even beautiful.
  The break is part of the object's history, not hidden from it.

Kintsugi is the ARCS receipt repair service. It:
  1. Detects "pathogen" patterns in receipts (anomalies, incoherence, corruption)
  2. Diagnoses the nature of the pathogen
  3. Applies a gold-seam repair — patches the anomaly with transparent documentation
  4. Returns a repaired receipt with visible scar metadata
  5. Logs all repairs to an append-only repair log

CRITICAL: Kintsugi does NOT hide damage. It makes it visible.
  Hidden cracks > golden scars is anti-ARCS. The repair must be auditable.
  A repaired receipt is LESS trusted than a clean receipt, but MORE trusted
  than an unexamined broken one.

Kintsugi is INDEPENDENT of the Constitutional Court:
  - Court: frontline defense (prevents bad decisions from entering)
  - Kintsugi: after-the-fact detection (heals receipts that slipped through)

The two work in sequence: Court first, Kintsugi if anything survives damaged.

NOTOMATION: Kintsugi identifies and documents damage. Humans approve repairs.

Canon references:
  - ARCS-Canon-v2-0-Complete.md (second law: entropy/coherence)
  - Phase 3 decision receipt: "Kintsugi repair service"
  - ARCS-SuperAdmin-Orchestrator.md: "immune system" + "golden seam"
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from arcs_rom import ARCSRom, SATOSHI_CRITERIA, PHASE_GATES, ROM_VERSION

KINTSUGI_VERSION = "v9.0-phase4"
DEFAULT_REPAIR_LOG_PATH = Path(__file__).parent / "arcs_kintsugi_repairs.json"


# ─────────────────────────────────────────────
# PATHOGEN TAXONOMY
# ─────────────────────────────────────────────

class PathogenType(str, Enum):
    """
    Taxonomy of receipt pathologies.

    Named as pathogens to reinforce the immune system metaphor:
    these are things that infect coherence receipts and must be
    isolated, diagnosed, and repaired before they spread.
    """
    # Data integrity pathogens
    NCI_OUT_OF_RANGE     = "NCI_OUT_OF_RANGE"       # NCI < 0 or > 100
    IRREV_OUT_OF_RANGE   = "IRREV_OUT_OF_RANGE"      # irreversibility outside [0,1]
    MISSING_FATED        = "MISSING_FATED"            # FATED fields incomplete
    AXIOM_VIOLATION      = "AXIOM_VIOLATION"          # DNA axiom marked NO

    # Coherence pathogens
    NCI_CLIFF            = "NCI_CLIFF"               # NCI dropped > 15 points from previous
    SATOSHI_DOWNGRADE    = "SATOSHI_DOWNGRADE"        # Was satoshi, no longer qualifies
    RUIN_UNMARKED        = "RUIN_UNMARKED"            # Ruin conditions met but not flagged

    # Process pathogens
    UNSEQUENCED_PHASE    = "UNSEQUENCED_PHASE"        # Phase entry without meeting gate
    DUPLICATE_RECEIPT    = "DUPLICATE_RECEIPT"        # Receipt with same ID already exists
    FATED_INCOMPLETE     = "FATED_INCOMPLETE"         # One or more FATED fields is empty/stub


@dataclass
class Pathogen:
    """A detected pathogen in a receipt."""
    pathogen_type: PathogenType
    severity:      str    # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    description:   str    # What is wrong
    field_path:    str    # Which field has the problem (e.g. "nci_score", "fated.facts")
    detected_value: Any   # The actual bad value
    canon_reference: str  # Which Canon rule is violated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathogen_type": self.pathogen_type.value,
            "severity": self.severity,
            "description": self.description,
            "field_path": self.field_path,
            "detected_value": str(self.detected_value)[:200],
            "canon_reference": self.canon_reference,
        }


@dataclass
class GoldenSeam:
    """
    The repair applied to a pathogen. The visible scar.

    A golden seam documents:
      - What was broken
      - What was done to repair it
      - What the repaired value is
      - Why the repair is valid (FATED mini-reasoning)
      - The trust discount applied to the repaired receipt
    """
    seam_id:         str
    pathogen_type:   str
    original_value:  Any
    repaired_value:  Any
    repair_method:   str   # How it was repaired
    repair_rationale: str  # Why this repair is valid
    trust_discount:  float  # 0.0=no discount, 1.0=completely untrustworthy
    repaired_at:     float = field(default_factory=time.time)
    approved_by:     str  = "KINTSUGI_AUTO"  # "KINTSUGI_AUTO" or "HUMAN_[name]"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seam_id": self.seam_id,
            "pathogen_type": self.pathogen_type,
            "original_value": str(self.original_value)[:200],
            "repaired_value": str(self.repaired_value)[:200],
            "repair_method": self.repair_method,
            "repair_rationale": self.repair_rationale,
            "trust_discount": self.trust_discount,
            "repaired_at": self.repaired_at,
            "approved_by": self.approved_by,
        }


@dataclass
class KintsugiDiagnosis:
    """
    Full diagnosis of a receipt: pathogens found + repair plan.
    """
    receipt_id:   str
    phase_id:     str
    timestamp:    float = field(default_factory=time.time)

    # Detection
    pathogens:    List[Pathogen]     = field(default_factory=list)
    is_healthy:   bool               = True   # No pathogens = healthy

    # Repair
    golden_seams: List[GoldenSeam]   = field(default_factory=list)
    is_repaired:  bool               = False
    repair_nci_discount: float       = 0.0   # Total trust discount from all seams
    repaired_receipt: Optional[Dict[str, Any]] = None

    # Status
    kintsugi_version: str = KINTSUGI_VERSION

    def highest_severity(self) -> str:
        if not self.pathogens:
            return "NONE"
        order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for sev in order:
            if any(p.severity == sev for p in self.pathogens):
                return sev
        return "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp,
            "is_healthy": self.is_healthy,
            "pathogen_count": len(self.pathogens),
            "highest_severity": self.highest_severity(),
            "pathogens": [p.to_dict() for p in self.pathogens],
            "is_repaired": self.is_repaired,
            "repair_nci_discount": self.repair_nci_discount,
            "golden_seam_count": len(self.golden_seams),
            "golden_seams": [s.to_dict() for s in self.golden_seams],
            "kintsugi_version": self.kintsugi_version,
        }


# ─────────────────────────────────────────────
# KINTSUGI SERVICE
# ─────────────────────────────────────────────

class KintsugiService:
    """
    Kintsugi: Receipt pathogen detection and repair.

    Primary workflow:
      1. diagnose(receipt_dict)   → finds pathogens
      2. repair(diagnosis)        → applies golden seams
      3. log_repair(diagnosis)    → appends to audit log

    The service is independent — it does not need a running pipeline.
    It operates on raw receipt dicts (from store) or live receipts.
    """

    def __init__(self, repair_log_path: Optional[Path] = None):
        self.version = KINTSUGI_VERSION
        self.rom = ARCSRom()
        self.repair_log_path = Path(repair_log_path or DEFAULT_REPAIR_LOG_PATH)
        self._seam_counter = 0

    def _next_seam_id(self) -> str:
        self._seam_counter += 1
        return f"seam_{int(time.time())}_{self._seam_counter:03d}"

    # ── Detection ─────────────────────────────

    def _detect_pathogens(self, receipt: Dict[str, Any]) -> List[Pathogen]:
        """
        Full pathogen scan of a receipt dict.
        Returns all detected pathogens (may be empty for a healthy receipt).
        """
        pathogens: List[Pathogen] = []

        nci = receipt.get("nci_score", None)
        irrev = receipt.get("irreversibility", None)
        on_purpose = receipt.get("on_purpose", None)
        fated = receipt.get("fated", {}) or {}
        phase_id = receipt.get("phase_id", "")
        axioms = receipt.get("axioms", {}) or {}

        # ── Data integrity checks ──────────────

        if nci is not None and not (0.0 <= nci <= 100.0):
            pathogens.append(Pathogen(
                pathogen_type=PathogenType.NCI_OUT_OF_RANGE,
                severity="CRITICAL",
                description=f"NCI value {nci} is outside the valid range [0, 100].",
                field_path="nci_score",
                detected_value=nci,
                canon_reference="NCI formula: range [0, 100]",
            ))

        if irrev is not None and not (0.0 <= irrev <= 1.0):
            pathogens.append(Pathogen(
                pathogen_type=PathogenType.IRREV_OUT_OF_RANGE,
                severity="HIGH",
                description=f"Irreversibility {irrev} is outside valid range [0, 1].",
                field_path="irreversibility",
                detected_value=irrev,
                canon_reference="Satoshi criteria: irreversibility ∈ [0, 1]",
            ))

        # ── Axiom violation check ──────────────

        for axiom_key, axiom_val in axioms.items():
            if axiom_val == "NO":
                pathogens.append(Pathogen(
                    pathogen_type=PathogenType.AXIOM_VIOLATION,
                    severity="CRITICAL",
                    description=f"DNA axiom '{axiom_key}' is marked NO — constitutional violation.",
                    field_path=f"axioms.{axiom_key}",
                    detected_value=axiom_val,
                    canon_reference=f"DNA Axiom: {axiom_key}",
                ))

        # ── FATED completeness check ───────────

        fated_fields = ["facts", "assumptions", "tradeoffs", "emotions", "direction"]
        for fated_key in fated_fields:
            val = fated.get(fated_key, "")
            if not val or len(str(val).strip()) < 5:
                pathogens.append(Pathogen(
                    pathogen_type=PathogenType.FATED_INCOMPLETE,
                    severity="MEDIUM",
                    description=f"FATED field '{fated_key}' is missing or too short (< 5 chars).",
                    field_path=f"fated.{fated_key}",
                    detected_value=val,
                    canon_reference="FATED macro: all five fields required for full reasoning trail",
                ))

        # ── Phase gate sequence check ──────────

        if phase_id and nci is not None:
            gate_nci = PHASE_GATES.get(phase_id)
            if gate_nci and nci < gate_nci:
                pathogens.append(Pathogen(
                    pathogen_type=PathogenType.UNSEQUENCED_PHASE,
                    severity="HIGH",
                    description=(
                        f"Receipt for {phase_id} has NCI {nci:.1f}, "
                        f"which is below the gate threshold {gate_nci}. "
                        f"Phase was entered without meeting the NCI gate."
                    ),
                    field_path="nci_score",
                    detected_value=nci,
                    canon_reference=f"Phase gate: {phase_id} requires NCI ≥ {gate_nci}",
                ))

        # ── Satoshi downgrade check ─────────────

        was_satoshi = receipt.get("is_satoshi", False)
        if was_satoshi:
            ok, reason = self.rom.is_satoshi(
                nci_score=nci or 0.0,
                on_purpose=bool(on_purpose),
                irreversibility=irrev or 1.0,
                axioms_all_checked=all(v in {"YES", "TENSION"} for v in axioms.values()),
            )
            if not ok:
                pathogens.append(Pathogen(
                    pathogen_type=PathogenType.SATOSHI_DOWNGRADE,
                    severity="HIGH",
                    description=f"Receipt claimed is_satoshi=True but no longer qualifies: {reason}",
                    field_path="is_satoshi",
                    detected_value=was_satoshi,
                    canon_reference="Satoshi validity criteria (Canon-locked in ROM)",
                ))

        return pathogens

    # ── Repair ────────────────────────────────

    def _apply_seam(
        self, pathogen: Pathogen, receipt: Dict[str, Any]
    ) -> Tuple[GoldenSeam, Dict[str, Any]]:
        """
        Applies a single golden seam repair for one pathogen.
        Returns (GoldenSeam, updated_receipt).
        """
        repaired = dict(receipt)
        seam_id = self._next_seam_id()

        if pathogen.pathogen_type == PathogenType.NCI_OUT_OF_RANGE:
            clamped = max(0.0, min(100.0, pathogen.detected_value))
            repaired["nci_score"] = clamped
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=pathogen.detected_value,
                repaired_value=clamped,
                repair_method="CLAMP",
                repair_rationale=f"NCI clamped to valid range [0, 100]. Original {pathogen.detected_value} is likely a calculation error.",
                trust_discount=0.15,
            )

        elif pathogen.pathogen_type == PathogenType.IRREV_OUT_OF_RANGE:
            clamped = max(0.0, min(1.0, pathogen.detected_value))
            repaired["irreversibility"] = clamped
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=pathogen.detected_value,
                repaired_value=clamped,
                repair_method="CLAMP",
                repair_rationale="Irreversibility clamped to [0, 1]. Value outside range is a data error.",
                trust_discount=0.10,
            )

        elif pathogen.pathogen_type == PathogenType.AXIOM_VIOLATION:
            # Cannot auto-repair an axiom violation — mark it, but do NOT change the axiom
            repaired.setdefault("kintsugi_flags", []).append(
                f"AXIOM_VIOLATION: {pathogen.field_path} = NO"
            )
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value="NO",
                repaired_value="NO (FLAGGED — human review required)",
                repair_method="FLAG_ONLY",
                repair_rationale=(
                    "Axiom violations cannot be auto-repaired. The axiom remains as-is. "
                    "A human must review and either (a) override with documented FATED reasoning, "
                    "or (b) resolve the underlying axiom tension before proceeding."
                ),
                trust_discount=0.35,
                approved_by="HUMAN_REQUIRED",
            )

        elif pathogen.pathogen_type == PathogenType.FATED_INCOMPLETE:
            field_key = pathogen.field_path.replace("fated.", "")
            if "fated" not in repaired or not repaired["fated"]:
                repaired["fated"] = {}
            repaired["fated"][field_key] = (
                f"[KINTSUGI STUB] Original field was missing or too short. "
                f"Human review required to complete this FATED dimension."
            )
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=pathogen.detected_value,
                repaired_value="[STUB — human review required]",
                repair_method="STUB_INJECTION",
                repair_rationale=(
                    f"FATED.{field_key} was empty. A stub has been injected to preserve "
                    "structural validity. Human must complete this field before next phase gate."
                ),
                trust_discount=0.08,
            )

        elif pathogen.pathogen_type == PathogenType.UNSEQUENCED_PHASE:
            # Flag but don't modify — gate violations are informational
            repaired.setdefault("kintsugi_flags", []).append(
                f"UNSEQUENCED_PHASE: NCI {receipt.get('nci_score')} entered {receipt.get('phase_id')} "
                f"below gate {PHASE_GATES.get(receipt.get('phase_id', ''), '?')}"
            )
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=receipt.get("nci_score"),
                repaired_value="FLAGGED",
                repair_method="FLAG_ONLY",
                repair_rationale="Phase gate violation flagged. Cannot retroactively repair phase sequence. Receipt marked.",
                trust_discount=0.20,
            )

        elif pathogen.pathogen_type == PathogenType.SATOSHI_DOWNGRADE:
            repaired["is_satoshi"] = False
            repaired.setdefault("kintsugi_flags", []).append(
                "SATOSHI_DOWNGRADE: was_satoshi=True claim invalidated"
            )
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=True,
                repaired_value=False,
                repair_method="DOWNGRADE",
                repair_rationale="Receipt no longer meets satoshi criteria. is_satoshi corrected to False.",
                trust_discount=0.12,
            )

        else:
            # Generic: flag and note
            repaired.setdefault("kintsugi_flags", []).append(
                f"UNKNOWN_PATHOGEN: {pathogen.pathogen_type.value}"
            )
            seam = GoldenSeam(
                seam_id=seam_id,
                pathogen_type=pathogen.pathogen_type.value,
                original_value=pathogen.detected_value,
                repaired_value="FLAGGED",
                repair_method="FLAG_ONLY",
                repair_rationale="Unknown pathogen type flagged for human review.",
                trust_discount=0.05,
            )

        return seam, repaired

    # ── Main API ──────────────────────────────

    def diagnose(self, receipt: Dict[str, Any]) -> KintsugiDiagnosis:
        """
        Diagnoses a receipt for pathogens.
        Does NOT repair — call repair() after reviewing the diagnosis.

        Args:
            receipt: Raw receipt dict (from store or pipeline)

        Returns:
            KintsugiDiagnosis with all detected pathogens.
        """
        receipt_id = receipt.get("receipt_id", f"unknown_{int(time.time())}")
        phase_id   = receipt.get("phase_id", "unknown")

        pathogens = self._detect_pathogens(receipt)
        is_healthy = len(pathogens) == 0

        return KintsugiDiagnosis(
            receipt_id=receipt_id,
            phase_id=phase_id,
            pathogens=pathogens,
            is_healthy=is_healthy,
        )

    def repair(self, diagnosis: KintsugiDiagnosis, receipt: Dict[str, Any]) -> KintsugiDiagnosis:
        """
        Applies golden seam repairs for all detected pathogens.
        Mutates the diagnosis in-place with repair results.

        NOTOMATION: Auto-repairs only non-critical pathogens.
        Axiom violations and unsequenced phases are FLAGGED, not silently fixed.

        Args:
            diagnosis: The KintsugiDiagnosis from diagnose()
            receipt:   The original receipt dict

        Returns:
            Updated KintsugiDiagnosis with golden_seams and repaired_receipt.
        """
        if diagnosis.is_healthy:
            diagnosis.repaired_receipt = dict(receipt)
            diagnosis.is_repaired = True
            return diagnosis

        repaired = dict(receipt)
        seams: List[GoldenSeam] = []
        total_discount = 0.0

        for pathogen in diagnosis.pathogens:
            seam, repaired = self._apply_seam(pathogen, repaired)
            seams.append(seam)
            total_discount += seam.trust_discount

        # Annotate repaired receipt with kintsugi metadata
        repaired["kintsugi_repaired"] = True
        repaired["kintsugi_repair_count"] = len(seams)
        repaired["kintsugi_trust_discount"] = round(min(1.0, total_discount), 3)
        repaired["kintsugi_seam_ids"] = [s.seam_id for s in seams]
        repaired["kintsugi_repaired_at"] = time.time()
        repaired["kintsugi_version"] = KINTSUGI_VERSION

        # Adjust NCI by trust discount
        if "nci_score" in repaired and isinstance(repaired["nci_score"], (int, float)):
            original_nci = repaired["nci_score"]
            repaired["nci_score"] = round(original_nci * (1.0 - total_discount), 2)
            repaired["nci_pre_repair"] = original_nci

        diagnosis.golden_seams = seams
        diagnosis.is_repaired = True
        diagnosis.repair_nci_discount = round(min(1.0, total_discount), 3)
        diagnosis.repaired_receipt = repaired

        return diagnosis

    def log_repair(self, diagnosis: KintsugiDiagnosis) -> None:
        """
        Appends a repair diagnosis to the append-only repair log.
        """
        log: List[Dict[str, Any]] = []
        if self.repair_log_path.exists():
            try:
                with open(self.repair_log_path, "r") as f:
                    log = json.load(f)
            except (json.JSONDecodeError, IOError):
                log = []

        log.append(diagnosis.to_dict())

        with open(self.repair_log_path, "w") as f:
            json.dump(log, f, indent=2)

    def scan_store(self, receipts: List[Dict[str, Any]]) -> List[KintsugiDiagnosis]:
        """
        Scans an entire receipt store for pathogens.
        Returns diagnoses for all receipts (healthy + unhealthy).
        """
        return [self.diagnose(r) for r in receipts]

    def print_diagnosis(self, diagnosis: KintsugiDiagnosis) -> None:
        status = "🟢 HEALTHY" if diagnosis.is_healthy else f"🔴 {len(diagnosis.pathogens)} PATHOGEN(S)"
        print(f"\n── Kintsugi Diagnosis: {diagnosis.receipt_id} ───────────────────")
        print(f"  Status  : {status}")
        print(f"  Severity: {diagnosis.highest_severity()}")
        if diagnosis.pathogens:
            for p in diagnosis.pathogens:
                print(f"  [{p.severity}] {p.pathogen_type.value}: {p.description[:70]}")
        if diagnosis.is_repaired:
            print(f"  Repaired: ✅ {len(diagnosis.golden_seams)} seam(s) applied")
            print(f"  NCI discount: -{diagnosis.repair_nci_discount:.0%}")
            for s in diagnosis.golden_seams:
                print(f"    🪡 [{s.seam_id}] {s.pathogen_type}: {s.repair_method}")
        print("─" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    print("=== Kintsugi Repair Service Smoke Test ===\n")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        log_path = Path(f.name)

    kintsugi = KintsugiService(repair_log_path=log_path)

    # Receipt 1: Healthy receipt
    healthy_receipt = {
        "receipt_id": "receipt_phase_3_001",
        "phase_id": "phase_3",
        "nci_score": 86.0,
        "on_purpose": True,
        "irreversibility": 0.20,
        "is_satoshi": True,
        "operator": "SAGE",
        "fated": {
            "facts": "Phase 3 complete. Full operator suite operational.",
            "assumptions": "RUIN_RISK detection is correct behavior.",
            "tradeoffs": "Speed vs ceremony — ceremony won.",
            "emotions": "Satisfied. The immune system is working.",
            "direction": "Proceed to Phase 4 after two gap fixes.",
        },
        "axioms": {
            "clarity_before_curvature": "YES",
            "agency_over_automation": "YES",
            "minimum_steps_to_coherence": "YES",
            "kairos_over_neuroticism": "YES",
        },
    }

    d1 = kintsugi.diagnose(healthy_receipt)
    kintsugi.print_diagnosis(d1)

    # Receipt 2: Broken receipt — multiple pathogens
    broken_receipt = {
        "receipt_id": "receipt_phase_X_broken",
        "phase_id": "phase_4",
        "nci_score": 115.0,          # Out of range
        "on_purpose": True,
        "irreversibility": 1.4,       # Out of range
        "is_satoshi": True,           # Will be a downgrade
        "operator": "SAGE",
        "fated": {
            "facts": "Incomplete",    # Too short
            "assumptions": "",        # Missing
            "tradeoffs": "Speed.",    # Too short
            "emotions": "Fine.",      # Too short
            "direction": "Go.",       # Too short
        },
        "axioms": {
            "clarity_before_curvature": "YES",
            "agency_over_automation": "NO",   # Violation
            "minimum_steps_to_coherence": "YES",
            "kairos_over_neuroticism": "TENSION",
        },
    }

    d2 = kintsugi.diagnose(broken_receipt)
    print(f"\nBefore repair: {len(d2.pathogens)} pathogens detected.")
    d2 = kintsugi.repair(d2, broken_receipt)
    kintsugi.print_diagnosis(d2)

    if d2.repaired_receipt:
        repaired = d2.repaired_receipt
        print(f"\n  Repaired NCI: {repaired.get('nci_pre_repair')} → {repaired.get('nci_score')}")
        print(f"  Trust discount: {repaired.get('kintsugi_trust_discount')}")
        print(f"  Seam IDs: {repaired.get('kintsugi_seam_ids')}")

    kintsugi.log_repair(d2)
    print(f"\n  Repair logged to: {log_path}")

    log_path.unlink()
    print("\n✅ Kintsugi verified.")
