#!/usr/bin/env python3
"""
pipeline_runner.py — ARCS pipeline wrapper

Calls arcs_pipeline_v1.py with context, returns a receipt-shaped result.
This is the multi-step inference entry point: takes a flat input dict,
constructs the primitives, runs SAGE → LAB → BAR → CURATOR, returns
a PipelineResult.to_dict() envelope the next step can consume.

Usage:
    python pipeline_runner.py --input pipeline_input.json --format json
    python pipeline_runner.py --input pipeline_input.json --format text
    echo '{"signal": [65,72,78,...], "fated": {...}, ...}' | python pipeline_runner.py
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


def _load_pipeline() -> Any:
    """Import and instantiate ARCSPipeline."""
    os.chdir(ARCS_DIR)
    from arcs_pipeline_v1 import ARCSPipeline

    return ARCSPipeline()


def _construct_primitives(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct the primitive objects the pipeline.run() signature requires
    from a flat input dict.

    Required keys in input_data:
        signal       list[float]   — raw numerical signal (at least 3 points)
        domain       str           — e.g. "decision", "meta"
        label        str           — human-readable signal description
        fated        dict          — {facts, assumptions, tradeoffs, emotions, direction}
        axioms       dict          — {clarity_before_curvature, agency_over_automation,
                                     minimum_steps_to_coherence, kairos_over_neuroticism}
                                     each value: "YES" | "NO" | "TENSION"
        somatic      dict          — {phase_tuning, surge_detection, feels_right,
                                     that_vibes, locked_in, expected_vs_actual}
                                     each value: 0.0–1.0
        hci_score    float         — Human Coherence Index (0–100)
        phase_id     str           — e.g. "phase_3"
        next_action  str           — what to do after the pipeline completes

    Optional keys:
        on_purpose        bool   — default True
        irreversibility   float  — default 0.3
        artifacts_shipped list   — default []
        notes             str    — default ""
        verbose           bool   — default False
    """
    os.chdir(ARCS_DIR)
    from arcs_primitives import (
        AxiomCheck,
        CoherenceSignal,
        FATEDReasoning,
        SomaticReading,
    )
    import numpy as np

    # ── Signal ──────────────────────────────────────────────────────────────
    raw_signal = input_data.get("signal")
    if raw_signal is None:
        _die("Missing required field: signal (list of floats, ≥ 3 points)")
    if not isinstance(raw_signal, (list, tuple)) or len(raw_signal) < 3:
        _die("signal must be a list of at least 3 floats")
    try:
        signal_arr = np.array(raw_signal, dtype=float)
    except (TypeError, ValueError) as e:
        _die(f"signal contains non-numeric values: {e}")

    domain = input_data.get("domain", "decision")
    label = input_data.get("label", "")
    if not label:
        _die("Missing required field: label (human-readable signal description)")

    signal = CoherenceSignal(
        signal=signal_arr,
        domain=domain,
        label=label,
    )

    # ── FATED ───────────────────────────────────────────────────────────────
    fated_dict = input_data.get("fated")
    if fated_dict is None:
        _die("Missing required field: fated ({facts, assumptions, tradeoffs, emotions, direction})")
    required_fated = ["facts", "assumptions", "tradeoffs", "emotions", "direction"]
    for key in required_fated:
        if key not in fated_dict or not isinstance(fated_dict[key], str):
            _die(f"fated.{key} must be a non-empty string")
    fated = FATEDReasoning(
        facts=fated_dict["facts"],
        assumptions=fated_dict["assumptions"],
        tradeoffs=fated_dict["tradeoffs"],
        emotions=fated_dict["emotions"],
        direction=fated_dict["direction"],
    )

    # ── Axioms ──────────────────────────────────────────────────────────────
    axioms_dict = input_data.get("axioms")
    if axioms_dict is None:
        _die("Missing required field: axioms ({clarity_before_curvature, agency_over_automation, minimum_steps_to_coherence, kairos_over_neuroticism})")
    valid_axiom_values = {"YES", "NO", "TENSION"}
    axiom_fields = [
        "clarity_before_curvature",
        "agency_over_automation",
        "minimum_steps_to_coherence",
        "kairos_over_neuroticism",
    ]
    for field in axiom_fields:
        val = axioms_dict.get(field)
        if val not in valid_axiom_values:
            _die(f"axioms.{field} must be one of {valid_axiom_values}, got '{val}'")
    axioms = AxiomCheck(
        clarity_before_curvature=axioms_dict["clarity_before_curvature"],
        agency_over_automation=axioms_dict["agency_over_automation"],
        minimum_steps_to_coherence=axioms_dict["minimum_steps_to_coherence"],
        kairos_over_neuroticism=axioms_dict["kairos_over_neuroticism"],
    )

    # ── Somatic ─────────────────────────────────────────────────────────────
    somatic_dict = input_data.get("somatic")
    if somatic_dict is None:
        _die("Missing required field: somatic ({phase_tuning, surge_detection, feels_right, that_vibes, locked_in, expected_vs_actual})")
    somatic_fields = [
        "phase_tuning",
        "surge_detection",
        "feels_right",
        "that_vibes",
        "locked_in",
        "expected_vs_actual",
    ]
    somatic_values = {}
    for field in somatic_fields:
        val = somatic_dict.get(field)
        if val is None or not isinstance(val, (int, float)):
            _die(f"somatic.{field} must be a float 0.0–1.0, got '{val}'")
        if not (0.0 <= val <= 1.0):
            _die(f"somatic.{field} must be 0.0–1.0, got {val}")
        somatic_values[field] = float(val)
    somatic = SomaticReading(**somatic_values)

    # ── Pipeline params ──────────────────────────────────────────────────────
    hci_score = input_data.get("hci_score")
    if hci_score is None:
        _die("Missing required field: hci_score (float 0–100)")
    try:
        hci_score = float(hci_score)
    except (TypeError, ValueError):
        _die(f"hci_score must be numeric, got '{hci_score}'")
    if not (0.0 <= hci_score <= 100.0):
        _die(f"hci_score must be 0.0–100.0, got {hci_score}")

    phase_id = input_data.get("phase_id")
    if not phase_id:
        _die("Missing required field: phase_id (e.g. 'phase_3')")

    next_action = input_data.get("next_action")
    if not next_action:
        _die("Missing required field: next_action")

    return {
        "signal": signal,
        "fated": fated,
        "axioms": axioms,
        "somatic": somatic,
        "hci_score": hci_score,
        "phase_id": phase_id,
        "next_action": next_action,
        "on_purpose": input_data.get("on_purpose", True),
        "irreversibility": float(input_data.get("irreversibility", 0.3)),
        "artifacts_shipped": input_data.get("artifacts_shipped", []) or [],
        "notes": input_data.get("notes", ""),
        "verbose": bool(input_data.get("verbose", False)),
    }


def run_pipeline(input_data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Run the ARCS pipeline and return a receipt-shaped result dict.

    Returns:
        {
            "status":     "ok" | "error",
            "pipeline_version": str,
            "phase_id":   str,
            "signal_label": str,
            "status_pipeline": "COMPLETE" | "BLOCKED" | "PARTIAL",
            "block_reason": str | None,
            "pipeline_nci": float,
            "pipeline_verdict": str,
            "next_action": str,
            "operator_outputs": {
                "sage":  dict | None,
                "lab":   dict | None,
                "bar":   dict | None,
                "curator": dict | None,
            },
            "operator20_seeds": dict,
            "error": str | None,
        }
    """
    try:
        primitives = _construct_primitives(input_data)
    except SystemExit:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error": f"failed to construct primitives: {e}",
        }

    try:
        pipeline = _load_pipeline()
    except Exception as e:
        return {
            "status": "error",
            "error": f"failed to load pipeline: {e}",
        }

    try:
        result = pipeline.run(
            signal=primitives["signal"],
            fated=primitives["fated"],
            axioms=primitives["axioms"],
            somatic=primitives["somatic"],
            hci_score=primitives["hci_score"],
            phase_id=primitives["phase_id"],
            next_action=primitives["next_action"],
            on_purpose=primitives["on_purpose"],
            irreversibility=primitives["irreversibility"],
            artifacts_shipped=primitives["artifacts_shipped"],
            notes=primitives["notes"],
            verbose=verbose or primitives["verbose"],
        )
    except Exception as e:
        import traceback

        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # Build receipt-shaped output
    operator_outputs = {
        "sage": result.sage_receipt.to_dict() if result.sage_receipt else None,
        "lab": result.lab_assessment.to_dict() if result.lab_assessment else None,
        "bar": result.bar_assessment.to_dict() if result.bar_assessment else None,
        "curator": result.curator_assessment.to_dict() if result.curator_assessment else None,
    }

    return {
        "status": "ok",
        "pipeline_version": result.pipeline_version,
        "phase_id": result.phase_id,
        "signal_label": result.signal_label,
        "pipeline_status": result.status,
        "block_reason": result.block_reason or None,
        "pipeline_nci": result.pipeline_nci,
        "pipeline_verdict": result.pipeline_verdict,
        "next_action": result.next_action,
        "operator_outputs": operator_outputs,
        "operator20_seeds": result.operator20_seeds,
    }


# ─── Output helpers ────────────────────────────────────────────────────────────

def _emit_json(result: Dict[str, Any], pretty: bool = True) -> None:
    indent = 2 if pretty else None
    print(json.dumps(result, indent=indent, default=_json_serial))


def _emit_text(result: Dict[str, Any]) -> None:
    """Human-readable summary of the pipeline result."""
    status = result.get("status", "?")
    if status == "error":
        print(f"\n❌ Pipeline Error: {result.get('error', 'unknown')}")
        tb = result.get("traceback")
        if tb:
            print(f"\n{tb}")
        return

    pstatus = result.get("pipeline_status", "?")
    sym = {"COMPLETE": "✅", "BLOCKED": "🛑", "PARTIAL": "⚠"}.get(pstatus, "?")
    verdict = result.get("pipeline_verdict", "?")
    nci = result.get("pipeline_nci", 0.0)

    print(f"\n⬡  ARCS PIPELINE RUNNER")
    print(f"   {sym} Status: {pstatus}")
    print(f"   Pipeline: {result.get('pipeline_version', '?')} | Phase: {result.get('phase_id', '?')}")
    print(f"   Signal: {result.get('signal_label', '?')}")
    print(f"   Verdict: {verdict}")
    print(f"   NCI: {nci:.1f}/100")
    if result.get("block_reason"):
        print(f"   Blocked: {result['block_reason']}")

    print(f"\n   Operator outputs:")
    for op_name, op_data in result.get("operator_outputs", {}).items():
        if op_data:
            if isinstance(op_data, dict):
                summary = op_data.get("summary_line", op_data.get("label", "?"))
                print(f"     • {op_name}: {summary}")
        else:
            print(f"     • {op_name}: (not run)")

    seeds = result.get("operator20_seeds", {})
    if seeds:
        print(f"\n   Operator20 seeds: {len(seeds)} dimensions")
    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="ARCS pipeline runner — multi-step inference entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python pipeline_runner.py --input pipeline_input.json --format json
          python pipeline_runner.py --input pipeline_input.json --format text
          echo '{"signal": [65,72,78,81,83,84,86,87,88,90], ...}' | python pipeline_runner.py

        Required input fields:
          signal, domain, label, fated, axioms, somatic,
          hci_score, phase_id, next_action

        Optional input fields:
          on_purpose, irreversibility, artifacts_shipped, notes, verbose
        """),
    )

    parser.add_argument("--input", default=None, help="JSON string input")
    parser.add_argument("--input-file", default=None, help="Path to JSON input file")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--verbose", action="store_true", help="Print pipeline verbose logs to stderr")

    args = parser.parse_args(argv)

    if args.input and args.input_file:
        _die("--input and --input-file are mutually exclusive")

    input_data: Optional[Dict[str, Any]] = None

    if args.input:
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError as e:
            _die(f"--input is not valid JSON: {e}")
    elif args.input_file:
        path = Path(args.input_file)
        if not path.exists():
            _die(f"--input-file not found: {path}")
        try:
            with open(path) as f:
                input_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            _die(f"--input-file: {e}")
    else:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                try:
                    input_data = json.loads(raw)
                except json.JSONDecodeError as e:
                    _die(f"stdin input is not valid JSON: {e}")
        if input_data is None:
            _die("No input provided. Use --input, --input-file, or pipe JSON to stdin.")

    if not isinstance(input_data, dict):
        _die("--input / --input-file must contain a JSON object (dict)")

    try:
        result = run_pipeline(input_data, verbose=args.verbose)
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
