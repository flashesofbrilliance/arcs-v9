#!/usr/bin/env python3
"""
operator_client.py — ARCS operator invocation wrapper

Takes: operator name + input + output format
Does: invokes the operator (CLI subprocess or direct API), parses output,
      returns a normalized envelope the next pipeline step can consume.

Usage:
    # Direct API mode (operator has a run() method):
    python operator_client.py --operator OPERATOR21 --mode api \
        --input '{"knots": [...]}' --format json

    # CLI text mode (operator reachable via cli_arcs_run.py):
    python operator_client.py --operator CIS --mode text \
        --input "Should I pivot the product?" --format json

    # Pipeline mode:
    python operator_client.py --operator PIPELINE --mode api \
        --input '{"signal": [...], "fated": {...}, ...}' --format json

Envelope contract (stdout, JSON):
    {
        "operator":      "OPERATOR21",          # requested operator id
        "mode":          "api",                  # "api" | "text"
        "status":        "ok",                   # "ok" | "error" | "blocked"
        "exit_code":     0,
        "raw": { ... },                          # verbatim operator output
        "envelope": {                             # normalized, pipeline-consumable
            "operator":      "OPERATOR21",
            "version":       "v0.1.0-phase3",
            "gate_status":   "pass",             # when available
            "nci":           85.0,               # when available
            "verdict":       "...",              # when available
            "findings":      [],                 # structured findings (ADR review)
            "receipt":       {...},              # CoherenceReceipt-shaped dict
            "next_action":   "...",
            "blocked_reason": null,
            "operator_specific": { ... }         # operator's own schema, pass-through
        }
    }
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

from arcs_primitives import (
    LABEL_SEED, LABEL_LAB, LABEL_PLAYGROUND, LABEL_GEMINATE,
    LABEL_EXPERIMENTAL,
)

# ─── Paths ────────────────────────────────────────────────────────────────────

HERE = Path(__file__).parent        # operators/ — all operator files live here
ARCS_DIR = HERE


# ─── Operator registry ────────────────────────────────────────────────────────
# Maps operator id → invocation metadata.
#  mode: "api" (direct Python import + run()) | "text" (cli_arcs_run.py subprocess)
#  api_class: fully-qualified class name or function for direct API mode
#  text_signal: how to phrase the signal for cli_arcs_run.py text mode

OPERATOR_REGISTRY = {
    "OPERATOR21": {
        "mode": "api",
        "label": "Anterior/Posterior Spline Inference Operator",
        "version": "v0.1.0-phase3",
        "api_module": "arcs_operator21",
        "api_class": "SplineInferenceOperator",
        "input_schema": "knots + optional seed_vectors",
        "tier": LABEL_SEED,
    },
    "PIPELINE": {
        "mode": "api",
        "label": "ARCS Pipeline v1 (SAGE → LAB → BAR → CURATOR)",
        "version": "v1.0-phase3",
        "api_module": "arcs_pipeline_v1",
        "api_class": "ARCSPipeline",
        "input_schema": "CoherenceSignal + FATEDReasoning + AxiomCheck + SomaticReading + hci_score + phase_id + next_action",
        "tier": LABEL_EXPERIMENTAL,
    },
    "CIS": {
        "mode": "text",
        "label": "CIS Decision Pipeline (cli_arcs_run.py primary path)",
        "version": "v9",
        "text_prefix": "",  # signal passed as-is
        "input_schema": "natural language signal",
        "tier": LABEL_EXPERIMENTAL,
    },
    "HC": {
        "mode": "text",
        "label": "Hemisphere Check (cli_arcs_run.py hc subcommand)",
        "version": "v9",
        "text_prefix": "hc ",
        "input_schema": "natural language signal",
        "tier": LABEL_EXPERIMENTAL,
    },
    "BAR": {
        "mode": "text",
        "label": "BAR Risk/Ruin Assessment",
        "version": "v9",
        "text_prefix": "",  # routed through CIS pipeline
        "input_schema": "natural language signal",
        "tier": LABEL_EXPERIMENTAL,
    },
    "KINTSUGI": {
        "mode": "text",
        "label": "KINTSUGI Phase Gate Validation",
        "version": "v9",
        "text_prefix": "",  # routed through CIS pipeline
        "input_schema": "natural language signal + phase context",
        "tier": LABEL_EXPERIMENTAL,
    },
    "LAB": {
        "mode": "text",
        "label": "LAB Adversarial Review (Loki/Advisors/Bayesian)",
        "version": "v9",
        "text_prefix": "",  # routed through CIS pipeline
        "input_schema": "natural language signal",
        "tier": LABEL_EXPERIMENTAL,
    },
}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def _json_serial(obj: Any) -> Any:
    """Best-effort JSON serialization for objects that may carry non-serializable fields."""
    if isinstance(obj, dict):
        return {k: _json_serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_serial(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    # Dataclass or object with to_dict
    if hasattr(obj, "to_dict"):
        return _json_serial(obj.to_dict())
    # Dataclass without to_dict — try __dict__
    if hasattr(obj, "__dict__"):
        return _json_serial(obj.__dict__)
    # NumPy scalar
    try:
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
    except ImportError:
        pass
    # Fallback: str
    return str(obj)


def _normalize_value(v: Any) -> Any:
    """Coerce a value to something JSON-serializable."""
    if isinstance(v, (str, int, float, bool, type(None))):
        return v
    if isinstance(v, dict):
        return {k: _normalize_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_normalize_value(val) for val in v]
    return str(v)


# ─── CLI text mode ────────────────────────────────────────────────────────────

def invoke_text(operator_id: str, signal: str, extra_args: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Invoke cli_arcs_run.py as a subprocess with --json.

    operator_id: which operator context to frame the signal in
    signal:      natural-language decision signal
    extra_args:  additional CLI flags (e.g. ["--to", "EXECUTOR", "--alt", "L2"])
    """
    if operator_id not in OPERATOR_REGISTRY:
        _die(f"Unknown operator '{operator_id}'. Known: {list(OPERATOR_REGISTRY.keys())}")

    entry = OPERATOR_REGISTRY[operator_id]
    if entry["mode"] != "text":
        _die(f"Operator '{operator_id}' does not support text mode. Use --mode api.")

    cli_path = HERE / "cli_arcs_run.py"
    if not cli_path.exists():
        _die(f"cli_arcs_run.py not found at {cli_path}")

    # Build argv
    argv: list[str] = []
    prefix = entry.get("text_prefix", "")
    if prefix:
        argv.append(prefix)

    argv.append(signal)

    if extra_args:
        argv.extend(extra_args)

    argv.append("--json")

    try:
        proc = subprocess.run(
            [sys.executable, str(cli_path)] + argv,
            capture_output=True,
            text=True,
            cwd=str(ARCS_DIR),
            timeout=120,
            env={**os.environ, "ARCS_DIR": str(ARCS_DIR)},
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "timeout after 120s",
            "exit_code": -1,
        }

    if proc.returncode != 0:
        stderr = proc.stderr.strip() if proc.stderr else ""
        return {
            "status": "error",
            "error": stderr or f"exit code {proc.returncode}",
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip() if proc.stdout else "",
        }

    stdout = proc.stdout.strip()
    if not stdout:
        return {
            "status": "error",
            "error": "empty stdout from cli_arcs_run.py",
            "exit_code": 0,
        }

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": f"cli_arcs_run.py returned non-JSON stdout: {stdout[:200]}",
            "exit_code": 0,
            "stdout": stdout,
        }

    return {
        "status": "ok",
        "exit_code": 0,
        "raw": parsed,
    }


# ─── Direct API mode ──────────────────────────────────────────────────────────

def _load_api_class(module_name: str, class_name: str):
    """Import a class from an operator module by name."""
    os.chdir(ARCS_DIR)
    mod = __import__(module_name, fromlist=[class_name])
    cls = getattr(mod, class_name)
    return cls


def invoke_api(operator_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke an operator directly via its Python API.

    operator_id:   e.g. "OPERATOR21", "PIPELINE"
    input_data:    dict of constructor/run kwargs
    """
    if operator_id not in OPERATOR_REGISTRY:
        _die(f"Unknown operator '{operator_id}'. Known: {list(OPERATOR_REGISTRY.keys())}")

    entry = OPERATOR_REGISTRY[operator_id]
    if entry["mode"] != "api":
        _die(f"Operator '{operator_id}' does not support api mode. Use --mode text.")

    module_name = entry["api_module"]
    class_name = entry["api_class"]

    try:
        cls = _load_api_class(module_name, class_name)
    except (ImportError, AttributeError) as e:
        return {
            "status": "error",
            "error": f"could not load {module_name}.{class_name}: {e}",
            "exit_code": -1,
        }

    # Separate constructor kwargs from run() kwargs
    # By convention: if input_data has a "run_kwargs" key, use it;
    # otherwise pass everything to run() and construct with no args.
    run_kwargs = input_data.pop("run_kwargs", input_data)

    try:
        instance = cls()
    except TypeError:
        # Some operators may need constructor args — pass input_data as **kwargs
        try:
            instance = cls(**input_data)
            run_kwargs = {}
        except Exception as e:
            return {
                "status": "error",
                "error": f"could not construct {class_name}: {e}",
                "exit_code": -1,
            }

    try:
        result = instance.run(**run_kwargs) if run_kwargs else instance.run()
    except TypeError:
        # run() may take no args
        try:
            result = instance.run()
        except Exception as e:
            return {
                "status": "error",
                "error": f"could not run {class_name}.run(): {e}",
                "exit_code": -1,
            }
    except Exception as e:
        import traceback

        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "exit_code": -1,
        }

    # Serialize
    serialized: Any
    if hasattr(result, "to_dict"):
        serialized = result.to_dict()
    elif isinstance(result, dict):
        serialized = result
    else:
        serialized = {"result": str(result)}

    serialized = _json_serial(serialized)

    # Build envelope
    envelope: Dict[str, Any] = {
        "operator": operator_id,
        "version": entry.get("version", "unknown"),
        "canonicality_tier": entry.get("tier", "unknown"),
        "operator_specific": serialized,
    }

    # Normalize common fields if present
    if isinstance(serialized, dict):
        if "gate_status" in serialized:
            envelope["gate_status"] = serialized["gate_status"]
        if "nci" in serialized:
            envelope["nci"] = serialized["nci"]
        elif "nci_score" in serialized:
            envelope["nci"] = serialized["nci_score"]
        if "verdict" in serialized:
            envelope["verdict"] = serialized["verdict"]
        if "pipeline_verdict" in serialized:
            envelope["verdict"] = serialized["pipeline_verdict"]
        if "next_action" in serialized:
            envelope["next_action"] = serialized["next_action"]
        if "status" in serialized and serialized["status"] in ("BLOCKED", "blocked"):
            envelope["status"] = "blocked"
            envelope["blocked_reason"] = serialized.get("block_reason", "")
        elif "status" in serialized:
            envelope["status"] = serialized["status"].lower()
        if "signal_label" in serialized:
            envelope["signal_label"] = serialized["signal_label"]

    # Wire operator-specific tier + pollination into envelope if present
    if "operator_specific" in envelope:
        spec = envelope["operator_specific"]
        if isinstance(spec, dict):
            if "tier" in spec:
                envelope["canonicality_tier"] = spec["tier"]
            if "pollination" in spec:
                envelope["pollination"] = spec["pollination"]

    return {
        "status": "ok",
        "exit_code": 0,
        "raw": serialized,
        "envelope": envelope,
    }


# ─── Output helpers ────────────────────────────────────────────────────────────

def _emit_json(result: Dict[str, Any], pretty: bool = True) -> None:
    indent = 2 if pretty else None
    print(json.dumps(result, indent=indent, default=str))


def _emit_text(result: Dict[str, Any]) -> None:
    """Human-readable summary of the envelope."""
    status = result.get("status", "?")
    op = result.get("operator", "?")
    version = result.get("envelope", {}).get("version", result.get("raw", {}).get("version", "?"))

    sym = {"ok": "✅", "error": "❌", "blocked": "🛑"}.get(status, "?")
    print(f"\n⬡  ARCS OPERATOR CLIENT — {op} {version}")
    print(f"   {sym} status: {status}")
    print()

    env = result.get("envelope", {})
    if env.get("gate_status"):
        print(f"   Gate: {env['gate_status'].upper()}")
    if env.get("nci") is not None:
        print(f"   NCI:  {env['nci']}/100")
    if env.get("verdict"):
        print(f"   Verdict: {env['verdict']}")
    if env.get("next_action"):
        print(f"   Next: {env['next_action']}")
    if env.get("blocked_reason"):
        print(f"   Blocked: {env['blocked_reason']}")

    raw = result.get("raw", {})
    if isinstance(raw, dict):
        extra = {k: v for k, v in raw.items() if k not in ("operator", "version", "gate_status", "nci", "verdict", "next_action", "status", "block_reason", "signal_label")}
        if extra:
            print(f"\n   Raw fields: {', '.join(f'{k}={v}' for k, v in list(extra.items())[:6])}")
    if result.get("error"):
        print(f"\n   Error: {result['error']}")
    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="ARCS operator invocation wrapper — normalized envelope output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Operator21 via direct API (JSON input file)
          python operator_client.py --operator OPERATOR21 --mode api \\
              --input-file knots.json --format json

          # CIS pipeline via text CLI (passthrough flags forwarded to cli_arcs_run.py)
          python operator_client.py --operator CIS --mode text \\
              --input-raw "Should I pivot the product?" --format json \\
              --to EXECUTOR --alt L2 --jtbd "Q3 strategy"

          # Pipeline via direct API (construct CoherenceSignal etc.)
          python operator_client.py --operator PIPELINE --mode api \\
              --input-file pipeline_input.json --format json

        Input formats:
          --input      JSON string (e.g. '{"knots": [...]}')
          --input-file path to JSON file
          --input-raw  natural-language signal (text mode only)

        Text-mode passthrough:
          Any flag not recognized by operator_client.py (e.g. --to, --alt, --jtbd)
          is forwarded verbatim to cli_arcs_run.py. No --extra needed.
        """),
    )

    parser.add_argument("--operator", required=True, help="Operator id (see registry below)")
    parser.add_argument("--mode", choices=["api", "text"], required=True, help="Invocation mode")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--input", default=None, help="JSON string input")
    parser.add_argument("--input-file", default=None, help="Path to JSON input file")
    parser.add_argument("--input-raw", default=None, help="Natural-language signal (text mode)")
    parser.add_argument("--quiet", action="store_true", help="Suppress human-readable preamble in text mode")

    # Parse known args; everything else (e.g. --to, --alt, --jtbd) is left for
    # text-mode passthrough to cli_arcs_run.py.
    args, unknown_args = parser.parse_known_args(argv)

    # Validate operator
    if args.operator not in OPERATOR_REGISTRY:
        _die(f"Unknown operator '{args.operator}'. Known: {list(OPERATOR_REGISTRY.keys())}")

    entry = OPERATOR_REGISTRY[args.operator]
    if args.mode != entry["mode"]:
        _die(f"Operator '{args.operator}' uses mode '{entry['mode']}', not '{args.mode}'. Use --mode {entry['mode']}.")

    # Resolve input
    input_data: Optional[Dict[str, Any]] = None
    signal: Optional[str] = None

    if args.input and args.input_file:
        _die("--input and --input-file are mutually exclusive")

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
        except json.JSONDecodeError as e:
            _die(f"--input-file is not valid JSON: {e}")
    elif args.input_raw:
        signal = args.input_raw
    elif args.mode == "text":
        _die("Text mode requires --input-raw (natural-language signal)")

    # Invoke
    if args.mode == "text":
        if not signal:
            _die("Text mode requires --input-raw")
        extra = unknown_args if unknown_args else None
        raw_result = invoke_text(args.operator, signal, extra)
        raw_result["operator"] = args.operator
        raw_result["mode"] = "text"

        # Build envelope from CIS output
        if raw_result["status"] == "ok" and isinstance(raw_result.get("raw"), dict):
            raw_result["envelope"] = {
                "operator": args.operator,
                "version": entry.get("version", "v9"),
                "gate_status": raw_result["raw"].get("gate_status", "pass"),
                "nci": raw_result["raw"].get("nci"),
                "css": raw_result["raw"].get("css"),
                "ips": raw_result["raw"].get("ips"),
                "true_north": raw_result["raw"].get("true_north"),
                "signal_bullets": raw_result["raw"].get("signal_bullets"),
                "vector_action": raw_result["raw"].get("vector_action"),
                "kairos_horizon": raw_result["raw"].get("kairos_horizon"),
                "target_archetype": raw_result["raw"].get("target_archetype"),
                "target_altitude": raw_result["raw"].get("target_altitude"),
                "active_distortions": raw_result["raw"].get("active_distortions"),
                "next_action": raw_result["raw"].get("vector_action"),
                "operator_specific": raw_result["raw"],
            }

        if args.format == "json":
            _emit_json(raw_result)
        else:
            _emit_text(raw_result)

    elif args.mode == "api":
        if input_data is None:
            _die("API mode requires --input or --input-file")
        raw_result = invoke_api(args.operator, input_data)
        raw_result["operator"] = args.operator
        raw_result["mode"] = "api"

        if args.format == "json":
            _emit_json(raw_result)
        else:
            _emit_text(raw_result)


if __name__ == "__main__":
    main()
