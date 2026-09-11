#!/usr/bin/env python3
"""
receipt_evaluator.py — KINTSUGI phase-gate wrapper

Takes a DEWY receipt (dict or JSON envelope) + optional outcome context.
Runs KINTSUGI phase gate: diagnose → optional repair → pass/warn/halt +
seam repair recommendations.

Usage:
    python receipt_evaluator.py --receipt receipt.json --format json
    python receipt_evaluator.py --receipt receipt.json --format text
    echo '{"receipt_id": "...", "nci_score": 85, ...}' | python receipt_evaluator.py
    python receipt_evaluator.py --receipt receipt.json --repair --format json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────

HERE = Path(__file__).parent
ARCS_DIR = HERE


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def _json_serial(obj: Any) -> Any:
    """Best-effort JSON serialization for operator output objects."""
    if isinstance(obj, dict):
        return {k: _json_serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_serial(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if hasattr(obj, "to_dict"):
        return _json_serial(obj.to_dict())
    if hasattr(obj, "__dict__"):
        return _json_serial(obj.__dict__)
    try:
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
    except ImportError:
        pass
    return str(obj)


def _load_receipt(path: Path) -> Dict[str, Any]:
    """Load a receipt JSON file and return the dict."""
    if not path.exists():
        _die(f"Receipt file not found: {path}")
    if not path.is_file():
        _die(f"Receipt path is not a file: {path}")
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        _die(f"Receipt file is not valid JSON: {e}")
    if not isinstance(data, dict):
        _die(f"Receipt file must contain a JSON object (dict), got {type(data).__name__}")
    return data


def _load_receipt_from_stdin() -> Dict[str, Any]:
    """Read JSON receipt from stdin."""
    raw = sys.stdin.read().strip()
    if not raw:
        _die("No receipt provided on stdin")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        _die(f"stdin receipt is not valid JSON: {e}")
    if not isinstance(data, dict):
        _die(f"stdin receipt must be a JSON object (dict), got {type(data).__name__}")
    return data


def _load_kintsugi() -> Any:
    """Import and instantiate KintsugiService."""
    os.chdir(ARCS_DIR)
    from arcs_kintsugi import KintsugiService

    return KintsugiService()


def evaluate_receipt(
    receipt: Dict[str, Any],
    repair: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run KINTSUGI phase gate on a DEWY receipt.

    Args:
        receipt:  DEWY receipt dict (must have at minimum nci_score, phase_id)
        repair:  If True, apply golden seam repairs after diagnosis.
        verbose: If True, print diagnostic details to stderr.

    Returns:
        {
            "status":           "ok" | "error",
            "receipt_id":       str,
            "phase_id":         str,
            "is_healthy":       bool,
            "pathogen_count":   int,
            "highest_severity": str,      # NONE | LOW | MEDIUM | HIGH | CRITICAL
            "gate":             "pass" | "warn" | "halt",
            "gate_reason":      str,
            "nci_before":       float | None,
            "nci_after":        float | None,
            "trust_discount":   float,
            "pathogens":        list[dict],
            "golden_seams":     list[dict] | None,   # only if repair=True
            "repaired_receipt": dict | None,         # only if repair=True
            "recommendations":  list[str],
            "error":            str | None,
        }
    """
    try:
        ks = _load_kintsugi()
    except Exception as e:
        return {
            "status": "error",
            "error": f"failed to load KintsugiService: {e}",
        }

    # Detect pathogens
    try:
        diagnosis = ks.diagnose(receipt)
    except Exception as e:
        import traceback

        return {
            "status": "error",
            "error": f"KINTSUGI diagnose() failed: {e}",
            "traceback": traceback.format_exc(),
        }

    if verbose:
        print(f"[receipt_evaluator] Diagnosis: {diagnosis.to_dict()}", file=sys.stderr)

    # Determine gate from diagnosis
    highest = diagnosis.highest_severity()
    pathogen_count = len(diagnosis.pathogens)
    is_healthy = diagnosis.is_healthy

    # Gate logic:
    #   no pathogens → PASS
    #   LOW/MEDIUM pathogens → WARN (seams available, proceed with awareness)
    #   HIGH/CRITICAL pathogens → HALT (do not proceed until resolved)
    if is_healthy or highest == "NONE":
        gate = "pass"
        gate_reason = "No pathogens detected. Receipt is phase-gate valid."
    elif highest in ("LOW", "MEDIUM"):
        gate = "warn"
        gate_reason = (
            f"{pathogen_count} pathogen(s) detected at {highest} severity. "
            f"Receipt can proceed with awareness — review seams before next phase gate."
        )
    else:
        gate = "halt"
        gate_reason = (
            f"{pathogen_count} pathogen(s) detected at {highest} severity. "
            f"Receipt phase gate blocked. Resolve pathogens before proceeding."
        )

    # Determine NCI before repair
    nci_before = receipt.get("nci_score")

    # Apply repair if requested
    nci_after: Optional[float] = None
    trust_discount = 0.0
    golden_seams: Optional[list] = None
    repaired_receipt: Optional[dict] = None
    recommendations: list = []

    if repair:
        try:
            repaired_diag = ks.repair(diagnosis, receipt)
        except Exception as e:
            import traceback

            return {
                "status": "error",
                "error": f"KINTSUGI repair() failed: {e}",
                "traceback": traceback.format_exc(),
            }

        nci_after = repaired_diag.repaired_receipt.get("nci_score") if repaired_diag.repaired_receipt else None
        trust_discount = repaired_diag.repair_nci_discount
        golden_seams = [s.to_dict() for s in repaired_diag.golden_seams] if repaired_diag.golden_seams else []
        repaired_receipt = repaired_diag.repaired_receipt

        if verbose:
            print(f"[receipt_evaluator] Repaired: {repaired_diag.to_dict()}", file=sys.stderr)

        # Build repair recommendations
        for seam in (repaired_diag.golden_seams or []):
            recommendations.append(
                f"{seam.repair_method} repair for {seam.pathogen_type}: "
                f"original={str(seam.original_value)[:80]}, "
                f"repaired={str(seam.repaired_value)[:80]}, "
                f"trust_discount={seam.trust_discount:.2f}, "
                f"approved_by={seam.approved_by}"
            )
    else:
        # Build non-repair recommendations from pathogens
        for p in diagnosis.pathogens:
            recommendations.append(
                f"{p.severity} {p.pathogen_type.value}: {p.description[:150]} "
                f"(field: {p.field_path}, canon: {p.canon_reference})"
            )

    return {
        "status": "ok",
        "receipt_id": diagnosis.receipt_id,
        "phase_id": diagnosis.phase_id,
        "is_healthy": is_healthy,
        "pathogen_count": pathogen_count,
        "highest_severity": highest,
        "gate": gate,
        "gate_reason": gate_reason,
        "nci_before": nci_before,
        "nci_after": nci_after,
        "trust_discount": trust_discount,
        "pathogens": [p.to_dict() for p in diagnosis.pathogens],
        "golden_seams": golden_seams,
        "repaired_receipt": repaired_receipt,
        "recommendations": recommendations,
    }


# ─── Output helpers ────────────────────────────────────────────────────────────

def _emit_json(result: Dict[str, Any], pretty: bool = True) -> None:
    indent = 2 if pretty else None
    print(json.dumps(result, indent=indent, default=_json_serial))


def _emit_text(result: Dict[str, Any]) -> None:
    """Human-readable receipt evaluation summary."""
    status = result.get("status", "?")
    if status == "error":
        print(f"\n❌ Receipt Evaluator Error: {result.get('error', 'unknown')}")
        tb = result.get("traceback")
        if tb:
            print(f"\n{tb}")
        return

    rid = result.get("receipt_id", "?")
    pid = result.get("phase_id", "?")
    gate = result.get("gate", "?")
    is_healthy = result.get("is_healthy", False)
    pathogen_count = result.get("pathogen_count", 0)
    highest = result.get("highest_severity", "NONE")
    nci_before = result.get("nci_before")
    nci_after = result.get("nci_after")
    trust_discount = result.get("trust_discount", 0.0)
    pathogens = result.get("pathogens", [])
    recommendations = result.get("recommendations", [])

    sym = {"pass": "✅", "warn": "⚠️ ", "halt": "🛑"}.get(gate, "?")
    print(f"\n⬡  KINTSUGI PHASE GATE — Receipt {rid}")
    print(f"   Phase: {pid} | Gate: {sym} {gate.upper()}")
    print(f"   Healthy: {is_healthy} | Pathogens: {pathogen_count} | Highest: {highest}")
    if nci_before is not None:
        print(f"   NCI before: {nci_before:.1f}/100")
    if nci_after is not None:
        print(f"   NCI after repair: {nci_after:.1f}/100 (trust discount: {trust_discount:.2f})")
    print(f"\n   Gate reason: {result.get('gate_reason', '')}")
    if pathogens:
        print(f"\n   Pathogens:")
        for i, p in enumerate(pathogens, 1):
            sev = p.get("severity", "?")
            ptype = p.get("pathogen_type", "?")
            desc = p.get("description", "?")
            print(f"     {i}. [{sev}] {ptype}: {desc[:120]}")
    if recommendations:
        print(f"\n   Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"     {i}. {rec[:150]}")
    if gate == "halt" and not is_healthy:
        print(f"\n   ⛔ HALT — do not proceed to next phase until pathogens are resolved.")
    elif gate == "warn":
        print(f"\n   ⚠️  WARN — proceed with awareness. Review seams before next phase gate.")
    else:
        print(f"\n   ✅ PASS — receipt is phase-gate valid.")
    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="ARCS KINTSUGI phase-gate evaluator — receipt pathogen detection + optional repair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python receipt_evaluator.py --receipt receipt.json --format json
          python receipt_evaluator.py --receipt receipt.json --repair --format json
          python receipt_evaluator.py --receipt receipt.json --format text
          echo '{"receipt_id":"r1","nci_score":85,"phase_id":"phase_1",...}' | python receipt_evaluator.py
        """),
    )

    parser.add_argument("--receipt", default=None, help="Path to receipt JSON file")
    parser.add_argument("--repair", action="store_true", help="Apply golden seam repairs after diagnosis")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostic details to stderr")

    args = parser.parse_args(argv)

    receipt: Optional[Dict[str, Any]] = None

    if args.receipt:
        receipt = _load_receipt(Path(args.receipt))
    elif not sys.stdin.isatty():
        receipt = _load_receipt_from_stdin()

    if receipt is None:
        _die("No receipt provided. Use --receipt, pipe JSON to stdin, or run with no args to see help.")

    try:
        result = evaluate_receipt(receipt, repair=args.repair, verbose=args.verbose)
    except SystemExit:
        raise
    except Exception as e:
        import traceback

        result = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    if args.format == "json":
        _emit_json(result)
    else:
        _emit_text(result)


if __name__ == "__main__":
    main()
