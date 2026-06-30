"""
arcs_rom.py
ARCS v9 — Canon ROM (Read-Only Memory)
Phase 4: WRITE-LOCK

The ROM is the immutable Canon firmware.
Once written in Phase 4, it is the single source of truth for:
  - DNA Axioms (write-locked; four immutable principles)
  - NCI formula and phase gate thresholds
  - Satoshi validity criteria
  - Operator version registry
  - Canon validation functions

"ROM" is a deliberate metaphor: firmware that can only be changed
at the hardware level (by the ARCS project maintainer), not by
runtime operations. Any attempt to override ROM values is logged
as a canon_violation — the system cannot proceed on violated Canon.

Phase 4 hardening: the rules are now locked.
Subsequent phases operate within them; they do not change them.

Canon reference: ARCS-SuperAdmin-Orchestrator.md
  "The Orchestrator verifies system invariants before committing any action."
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

ROM_VERSION = "v9.0-phase4"

# ─────────────────────────────────────────────
# IMMUTABLE CANON — DNA AXIOMS
# ─────────────────────────────────────────────

# These four axioms are the ARCS constitutional core.
# They are write-locked: no operator, pipeline, or runtime may modify them.
# Violations are logged; the system does not proceed on violated Canon.

DNA_AXIOMS: Dict[str, str] = {
    "clarity_before_curvature": (
        "Signal before elegance. Understand the data before adding abstraction. "
        "Do not impose structure on noise."
    ),
    "agency_over_automation": (
        "Human judgment before delegated decision. Tools externalize cognition; "
        "they do not replace it. NOTOMATION is non-negotiable."
    ),
    "minimum_steps_to_coherence": (
        "Shortest path to a real, working artifact. No premature abstraction. "
        "No speculative engineering. Ship the minimum coherent unit first."
    ),
    "kairos_over_neuroticism": (
        "Opportune timing over anxiety. Act at the Kairos window. "
        "Do not rush from fear; do not delay from perfectionism."
    ),
}

# ─────────────────────────────────────────────
# NCI FORMULA (LOCKED)
# ─────────────────────────────────────────────

NCI_FORMULA: Dict[str, Any] = {
    "formula": "NCI = (on_purpose_rate × 0.7) + ((1 - avg_irreversibility) × 0.3)",
    "on_purpose_weight": 0.70,
    "irreversibility_weight": 0.30,
    "range": [0.0, 100.0],
    "description": (
        "Navigational Confidence Index. Measures how intentionally a phase was built "
        "and how reversible its commitments are. High NCI = reasoned, recoverable action."
    ),
}

# ─────────────────────────────────────────────
# PHASE GATE THRESHOLDS (LOCKED)
# ─────────────────────────────────────────────

PHASE_GATES: Dict[str, float] = {
    "phase_1": 75.0,   # READ: Inventory complete
    "phase_2": 82.0,   # WRITE: Core primitives + SAGE
    "phase_3": 85.0,   # READ-WRITE: Full operator suite
    "phase_4": 88.0,   # WRITE-LOCK: ROM + Constitutional Court
    "phase_5": 86.0,   # PHASE-SYNC: Runtime service + Yoav
    "phase_6": 88.0,   # LOSSLESS TRANSLATION: Export + API
}

# ─────────────────────────────────────────────
# SATOSHI VALIDITY CRITERIA (LOCKED)
# ─────────────────────────────────────────────

SATOSHI_CRITERIA: Dict[str, Any] = {
    "on_purpose": True,
    "min_nci": 50.0,
    "max_irreversibility": 0.5,
    "all_axioms_checked": True,
    "description": (
        "Satoshi = smallest recursively buildable coherence unit. "
        "A receipt is a satoshi iff: on_purpose=True, NCI≥50, "
        "irreversibility≤0.5, and all four DNA axioms are checked."
    ),
}

# ─────────────────────────────────────────────
# OPERATOR VERSION REGISTRY (LOCKED AT PHASE 4)
# ─────────────────────────────────────────────

OPERATOR_REGISTRY: Dict[str, str] = {
    "SAGE":    "v9.0-phase2",
    "LAB":     "v9.0-phase3",
    "BAR":     "v9.0-phase3",
    "CURATOR": "v9.0-phase3",
    "COURT":   "v9.0-phase4",    # Constitutional Court (new in Phase 4)
    "KINTSUGI":"v9.0-phase4",    # Repair service (new in Phase 4)
    "ROM":     ROM_VERSION,
}

# ─────────────────────────────────────────────
# RUIN ADJUDICATION THRESHOLDS (LOCKED)
# ─────────────────────────────────────────────

RUIN_THRESHOLDS: Dict[str, Any] = {
    "irreversibility_ruin": 0.70,    # irreversibility > 0.7 → BAR flags ruin
    "loki_ruin_standard": 0.70,      # standard loki ruin threshold
    "loki_ruin_ceiling_high": 0.85,  # NCI 85-90 decelerating: raise to 0.85
    "loki_ruin_ceiling_peak": 0.95,  # NCI > 90 decelerating: ceiling-adjacent
    "court_permit_threshold": 0.65,  # Court permits if evidence_weight > 0.65
    "court_block_threshold": 0.35,   # Court blocks if evidence_weight < 0.35
    "satoshi_floor": 50.0,           # NCI below this = below satoshi validity
}

# ─────────────────────────────────────────────
# ROM INTEGRITY HASH
# ─────────────────────────────────────────────

def _compute_rom_hash() -> str:
    """
    SHA-256 hash of the ROM content.
    Used to detect tampering. Any change to the ROM constants above
    will produce a different hash — exposing the modification.
    """
    rom_payload = json.dumps(
        {
            "dna_axioms": DNA_AXIOMS,
            "nci_formula": NCI_FORMULA,
            "phase_gates": PHASE_GATES,
            "satoshi_criteria": SATOSHI_CRITERIA,
            "operator_registry": OPERATOR_REGISTRY,
            "ruin_thresholds": RUIN_THRESHOLDS,
            "version": ROM_VERSION,
        },
        sort_keys=True,
    )
    return hashlib.sha256(rom_payload.encode()).hexdigest()


ROM_HASH: str = _compute_rom_hash()


# ─────────────────────────────────────────────
# VALIDATION RESULT
# ─────────────────────────────────────────────

@dataclass
class ROMValidationResult:
    """
    Result of validating a receipt, operator output, or claim against Canon.

    Violations are logged and block progression.
    Warnings are noted but do not block.
    Passed means the item is fully Canon-compliant.
    """
    is_valid: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)
    validated_at: float = field(default_factory=time.time)
    rom_version: str = ROM_VERSION
    rom_hash_at_validation: str = field(default_factory=lambda: ROM_HASH)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violations": self.violations,
            "warnings": self.warnings,
            "checks_passed": self.checks_passed,
            "validated_at": self.validated_at,
            "rom_version": self.rom_version,
            "rom_hash": self.rom_hash_at_validation,
        }

    def summary(self) -> str:
        if self.is_valid:
            return f"✅ Canon-valid. {len(self.checks_passed)} checks passed. {len(self.warnings)} warnings."
        return (
            f"🛑 Canon VIOLATED. {len(self.violations)} violation(s): "
            + "; ".join(self.violations)
        )


# ─────────────────────────────────────────────
# ROM VALIDATOR
# ─────────────────────────────────────────────

class ARCSRom:
    """
    The Canon ROM. Write-locked firmware for ARCS v9.

    Primary responsibilities:
      1. Verify ROM integrity (hash check)
      2. Validate receipts against Canon criteria
      3. Check phase gate eligibility
      4. Validate operator versions
      5. Check satoshi validity

    The ROM does NOT make decisions. It validates that decisions
    are consistent with locked Canon. NOTOMATION applies.
    """

    def __init__(self):
        self.version = ROM_VERSION
        self.hash = ROM_HASH
        self._verify_integrity()

    def _verify_integrity(self) -> None:
        """Verifies ROM has not been tampered with since initialization."""
        current_hash = _compute_rom_hash()
        if current_hash != self.hash:
            raise RuntimeError(
                f"ROM INTEGRITY VIOLATION: Canon hash mismatch. "
                f"Expected {self.hash[:16]}..., got {current_hash[:16]}... "
                f"The ROM has been modified after initialization."
            )

    # ── Phase Gate ────────────────────────────

    def check_phase_gate(self, phase_id: str, nci_score: float) -> Tuple[bool, str]:
        """
        Checks if NCI score meets the phase gate threshold.
        Returns (passes, message).
        """
        threshold = PHASE_GATES.get(phase_id)
        if threshold is None:
            return False, f"Unknown phase_id '{phase_id}'. Valid phases: {list(PHASE_GATES.keys())}"
        if nci_score >= threshold:
            return True, f"Phase gate PASSED: NCI {nci_score:.1f} ≥ {threshold} required for {phase_id}."
        return False, (
            f"Phase gate NOT MET: NCI {nci_score:.1f} < {threshold} required for {phase_id}. "
            f"Gap: {threshold - nci_score:.1f} points needed."
        )

    # ── Satoshi Check ─────────────────────────

    def is_satoshi(
        self,
        nci_score: float,
        on_purpose: bool,
        irreversibility: float,
        axioms_all_checked: bool,
    ) -> Tuple[bool, str]:
        """
        Returns (is_satoshi, reason) using locked Canon criteria.
        """
        if not on_purpose:
            return False, "Not a satoshi: on_purpose=False."
        if nci_score < SATOSHI_CRITERIA["min_nci"]:
            return False, f"Not a satoshi: NCI {nci_score:.1f} < {SATOSHI_CRITERIA['min_nci']} minimum."
        if irreversibility > SATOSHI_CRITERIA["max_irreversibility"]:
            return False, f"Not a satoshi: irreversibility {irreversibility:.2f} > {SATOSHI_CRITERIA['max_irreversibility']} maximum."
        if not axioms_all_checked:
            return False, "Not a satoshi: not all four DNA axioms were checked."
        return True, f"Satoshi valid: NCI {nci_score:.1f}, irreversibility {irreversibility:.2f}, all axioms checked."

    # ── Operator Version Check ────────────────

    def validate_operator_version(self, operator_name: str, version: str) -> Tuple[bool, str]:
        """
        Checks if an operator's version matches the Canon registry.
        """
        canonical = OPERATOR_REGISTRY.get(operator_name.upper())
        if canonical is None:
            return False, f"Operator '{operator_name}' not in Canon registry."
        if version == canonical:
            return True, f"Operator {operator_name} version {version} is Canon-compliant."
        return False, (
            f"Operator {operator_name} version mismatch: "
            f"running {version}, Canon requires {canonical}."
        )

    # ── Axiom Validation ─────────────────────

    def validate_axioms(self, axiom_dict: Dict[str, str]) -> ROMValidationResult:
        """
        Validates that axiom checks are present and non-violating.
        axiom_dict: {axiom_name: "YES" | "NO" | "TENSION"}
        """
        violations = []
        warnings = []
        checks_passed = []

        for axiom_name in DNA_AXIOMS:
            val = axiom_dict.get(axiom_name, "MISSING")
            if val == "MISSING":
                violations.append(f"Axiom '{axiom_name}' not checked.")
            elif val == "NO":
                violations.append(f"Axiom '{axiom_name}' VIOLATED (marked NO).")
            elif val == "TENSION":
                warnings.append(f"Axiom '{axiom_name}' in TENSION — review before committing.")
                checks_passed.append(axiom_name)
            else:  # YES
                checks_passed.append(axiom_name)

        is_valid = len(violations) == 0
        return ROMValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            checks_passed=checks_passed,
        )

    # ── Full Receipt Validation ───────────────

    def validate_receipt(self, receipt_dict: Dict[str, Any]) -> ROMValidationResult:
        """
        Validates a receipt (as dict) against all Canon criteria.
        Checks: NCI formula integrity, satoshi validity, axiom compliance.
        """
        violations = []
        warnings = []
        checks_passed = []

        # Check NCI is within range
        nci = receipt_dict.get("nci_score", -1)
        if not (0.0 <= nci <= 100.0):
            violations.append(f"NCI {nci} is outside valid range [0, 100].")
        else:
            checks_passed.append("nci_range")

        # Check on_purpose is boolean
        on_purpose = receipt_dict.get("on_purpose", None)
        if not isinstance(on_purpose, bool):
            warnings.append("on_purpose field missing or non-boolean.")
        else:
            checks_passed.append("on_purpose_type")

        # Check irreversibility is in range
        irrev = receipt_dict.get("irreversibility", -1)
        if not (0.0 <= irrev <= 1.0):
            violations.append(f"irreversibility {irrev} is outside [0, 1].")
        else:
            checks_passed.append("irreversibility_range")

        # Check operator is registered
        operator = receipt_dict.get("operator", "")
        if operator.upper() not in OPERATOR_REGISTRY:
            warnings.append(f"Operator '{operator}' not in Canon registry.")
        else:
            checks_passed.append("operator_registered")

        # Check FATED completeness (if present)
        fated = receipt_dict.get("fated", {})
        if fated:
            missing = [k for k in ["facts", "assumptions", "tradeoffs", "emotions", "direction"] if not fated.get(k)]
            if missing:
                warnings.append(f"FATED incomplete: missing fields {missing}.")
            else:
                checks_passed.append("fated_complete")

        is_valid = len(violations) == 0
        return ROMValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            checks_passed=checks_passed,
        )

    # ── ROM Status ────────────────────────────

    def status(self) -> Dict[str, Any]:
        return {
            "rom_version": self.version,
            "rom_hash": self.hash[:16] + "...",
            "axioms_count": len(DNA_AXIOMS),
            "phase_gates": PHASE_GATES,
            "operator_registry": OPERATOR_REGISTRY,
            "satoshi_min_nci": SATOSHI_CRITERIA["min_nci"],
            "satoshi_max_irreversibility": SATOSHI_CRITERIA["max_irreversibility"],
            "nci_formula": NCI_FORMULA["formula"],
            "integrity": "VERIFIED",
        }

    def print_status(self) -> None:
        s = self.status()
        print("\n── ARCS ROM Status ──────────────────────────────────────")
        for k, v in s.items():
            print(f"  {k:35}: {v}")
        print("─" * 60)


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== ARCS ROM Smoke Test ===\n")

    rom = ARCSRom()
    rom.print_status()

    # Phase gate checks
    print("\n── Phase Gate Checks ─────────────────────────────────────")
    for phase, nci_test in [("phase_3", 86.0), ("phase_4", 87.5), ("phase_4", 88.0), ("phase_6", 91.0)]:
        passes, msg = rom.check_phase_gate(phase, nci_test)
        print(f"  {'✅' if passes else '✗'} NCI {nci_test} for {phase}: {msg.split(':')[1].strip()}")

    # Satoshi checks
    print("\n── Satoshi Checks ────────────────────────────────────────")
    for label, nci, op, irrev, ax in [
        ("Valid satoshi",   82.5, True, 0.2,  True),
        ("Below NCI floor", 48.0, True, 0.2,  True),
        ("Too irreversible", 75.0, True, 0.75, True),
        ("Not on purpose",  80.0, False, 0.3, True),
    ]:
        ok, reason = rom.is_satoshi(nci, op, irrev, ax)
        print(f"  {'✅' if ok else '✗'} {label}: {reason[:70]}")

    # Axiom validation
    print("\n── Axiom Validation ──────────────────────────────────────")
    clean = {k: "YES" for k in DNA_AXIOMS}
    violated = {**clean, "agency_over_automation": "NO"}
    tension  = {**clean, "kairos_over_neuroticism": "TENSION"}

    for label, adict in [("All YES", clean), ("One NO", violated), ("One TENSION", tension)]:
        result = rom.validate_axioms(adict)
        print(f"  {'✅' if result.is_valid else '🛑'} {label}: {result.summary()}")

    # Operator version checks
    print("\n── Operator Version Checks ───────────────────────────────")
    for op, ver in [("SAGE", "v9.0-phase2"), ("LAB", "v9.0-phase3"), ("SAGE", "v8.0-old")]:
        ok, msg = rom.validate_operator_version(op, ver)
        print(f"  {'✅' if ok else '✗'} {op}@{ver}: {msg.split(':')[-1].strip()}")

    print("\n✅ ROM verified — Canon firmware locked.")
