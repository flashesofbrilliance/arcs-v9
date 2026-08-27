#!/usr/bin/env python3
"""
adr_audit.py — ADR quality-gate wrapper

Takes an ADR file path + review tier (1–4 per arcs-adr-review skill).
Invokes BAR + KINTSUGI (+ optionally LAB) as structured CLI review lenses.
Returns structured findings in the format defined by the ARCS ADR review protocol.

Usage:
    python adr_audit.py --adr path/to/ADR.md --tier 2 --format json
    python adr_audit.py --adr path/to/ADR.md --tier 3 --include-lab --format json
    python adr_audit.py --adr path/to/ADR.md --tier 1 --format text

Tiers (from arcs-adr-review skill):
    Tier 1 — Risk/ruin gate:   BAR only
    Tier 2 — Phase gate:       BAR + KINTSUGI
    Tier 3 — Full adversarial: BAR + KINTSUGI + LAB
    Tier 4 — Constitutional:   CONTRACT (axiom compliance)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────

HERE = Path(__file__).parent
ARCS_DIR = HERE


# ─── Operator labels (from arcs_primitives) ──────────────────────────────────

LABEL_SEED         = "seed"
LABEL_LAB          = "lab"
LABEL_PLAYGROUND   = "playground"
LABEL_GEMINATE     = "geminate_candidacy"
LABEL_EXPERIMENTAL = "experimental"


# ─── ADR content loading ──────────────────────────────────────────────────────

def _load_adr(path: Path) -> str:
    """Read an ADR file and return its text content."""
    if not path.exists():
        _die(f"ADR file not found: {path}")
    if not path.is_file():
        _die(f"ADR path is not a file: {path}")
    try:
        return path.read_text()
    except Exception as e:
        _die(f"Could not read ADR file {path}: {e}")


# ─── Structured finding format ────────────────────────────────────────────────
# From arcs-adr-review skill § "Structured finding format":

def _make_finding(
    operator: str,
    adr_path: str,
    adr_section: str,
    severity: str,
    finding_type: str,
    finding: str,
    evidence: str,
    recommendation: str,
    action: str,
) -> Dict[str, Any]:
    return {
        "operator": operator,
        "adr": adr_path,
        "adr_section": adr_section,
        "severity": severity,
        "type": finding_type,
        "finding": finding,
        "evidence": evidence,
        "recommendation": recommendation,
        "action": action,
    }


# ─── Review lenses ────────────────────────────────────────────────────────────

def _review_bar(adr_text: str, adr_path: str, model: str | None = None) -> List[Dict[str, Any]]:
    """
    BAR lens: risk/ruin boundary conditions on the ADR decision.

    Feeds the ADR text to cli_arcs_run.py and parses the structured output.
    Extracts boundary conditions, ruin scenarios, severity grading.
    """
    findings: List[Dict[str, Any]] = []

    # Invoke BAR via cli_arcs_run.py text mode.
    # BAR is routed through the CIS pipeline — frame the signal as a risk/ruin review.
    prompt = (
        f"Review this ADR for risk and ruin boundary conditions. "
        f"Identify all boundary conditions, ruin scenarios, and severity grading. "
        f"ADR text:\n\n{adr_text}"
    )

    result = _invoke_cis_text(prompt, model=model)
    if result.get("status") != "ok":
        findings.append(_make_finding(
            operator="BAR",
            adr_path=adr_path,
            adr_section="(full ADR)",
            severity="medium",
            finding_type="review_instrument_error",
            finding=f"BAR review instrument failed: {result.get('error', 'unknown')}",
            evidence=f"cli_arcs_run.py returned: {result}",
            recommendation="Run BAR review manually or fix the instrument before re-running.",
            action="fix_instrument_or_accept_manual_review",
        ))
        return findings

    raw = result.get("raw", {})
    gate = raw.get("gate_status", "unknown")
    css = raw.get("css", 0.0)
    distortions = raw.get("active_distortions", [])
    vector = raw.get("vector_action", "")
    true_north = raw.get("true_north", "")

    # Map CIS gate to BAR-style severity
    severity_map = {
        "halt": "critical",
        "warn": "high",
        "pass": "low",
    }
    severity = severity_map.get(gate, "medium")

    finding_text = (
        f"BAR review via CIS pipeline: gate={gate.upper()}, CSS={css:.3f}. "
        f"True North: {true_north[:200]}. "
        f"Vector: {vector[:200]}."
    )
    if distortions:
        finding_text += f" Active distortions: {', '.join(distortions[:3])}."

    findings.append(_make_finding(
        operator="BAR",
        adr_path=adr_path,
        adr_section="(full ADR — risk/ruin lens)",
        severity=severity,
        finding_type="boundary_condition",
        finding=finding_text,
        evidence=f"ADR text length: {len(adr_text)} chars. cli_arcs_run.py signal: risk/ruin review prompt.",
        recommendation=(
            "For HALT: restore sender coherence before proceeding — the ADR decision "
            "has active distortions blocking transmission."
            if gate == "halt" else
            "For WARN: proceed with awareness of visible seam. Review distortions."
            if gate == "warn" else
            "For PASS: no critical boundary conditions detected by BAR lens. "
            "Proceed to next review tier if applicable."
        ),
        action=(
            "halt_and_restore_coherence"
            if gate == "halt" else
            "proceed_with_awareness"
            if gate == "warn" else
            "proceed_to_next_tier"
        ),
    ))

    return findings


def _review_kintsugi(adr_text: str, adr_path: str, model: str | None = None) -> List[Dict[str, Any]]:
    """
    KINTSUGI lens: phase gate validation on the ADR decision.

    Feeds the ADR text to cli_arcs_run.py and parses for phase-gate status,
    seams, and repair recommendations.

    KINTSUGI looks for: phase-gate status (pass/warn/halt), seams identified,
    repair recommendations.
    """
    findings: List[Dict[str, Any]] = []

    prompt = (
        f"Validate the phase gate for this decision. Identify any seams that need "
        f"repair, and recommend repairs. ADR text:\n\n{adr_text}"
    )

    result = _invoke_cis_text(prompt, model=model)
    if result.get("status") != "ok":
        findings.append(_make_finding(
            operator="KINTSUGI",
            adr_path=adr_path,
            adr_section="(full ADR — phase gate lens)",
            severity="medium",
            finding_type="review_instrument_error",
            finding=f"KINTSUGI review instrument failed: {result.get('error', 'unknown')}",
            evidence=f"cli_arcs_run.py returned: {result}",
            recommendation="Run KINTSUGI review manually or fix the instrument before re-running.",
            action="fix_instrument_or_accept_manual_review",
        ))
        return findings

    raw = result.get("raw", {})
    gate = raw.get("gate_status", "unknown")
    css = raw.get("css", 0.0)
    distortions = raw.get("active_distortions", [])
    vector = raw.get("vector_action", "")
    seam = raw.get("visible_seam", "")

    severity_map = {
        "halt": "critical",
        "warn": "high",
        "pass": "low",
    }
    severity = severity_map.get(gate, "medium")

    finding_text = (
        f"KINTSUGI phase-gate validation via CIS pipeline: gate={gate.upper()}, "
        f"CSS={css:.3f}."
    )
    if seam:
        finding_text += f" Visible seam: {seam[:200]}."
    if distortions:
        finding_text += f" Distortions: {', '.join(distortions[:3])}."
    finding_text += f" Next action: {vector[:200]}."

    recommendations_map = {
        "halt": (
            "Phase gate HALT — transmission blocked. Restore sender coherence first. "
            "Do not mark this ADR canonical until the halt is resolved. "
            "Identify the active distortion, repair it, and re-run the phase gate."
        ),
        "warn": (
            "Phase gate WARN — visible seam applied. Document the seam acceptance "
            "in the ADR before marking canonical. The decision can proceed with awareness."
        ),
        "pass": (
            "Phase gate PASS — no seams blocking transmission. "
            "Decision is phase-gate valid. Continue to next review tier if applicable."
        ),
    }

    findings.append(_make_finding(
        operator="KINTSUGI",
        adr_path=adr_path,
        adr_section="(full ADR — phase gate lens)",
        severity=severity,
        finding_type="phase_gate_status",
        finding=finding_text,
        evidence=f"ADR text length: {len(adr_text)} chars. cli_arcs_run.py signal: phase gate validation prompt.",
        recommendation=recommendations_map.get(gate, "Review KINTSUGI output manually."),
        action=(
            "halt_restore_coherence"
            if gate == "halt" else
            "document_seam_acceptance"
            if gate == "warn" else
            "proceed_to_next_tier"
        ),
    ))

    return findings


def _review_lab(adr_text: str, adr_path: str, model: str | None = None) -> List[Dict[str, Any]]:
    """
    LAB lens: adversarial review from Loki / Advisors / Bayesian perspectives.

    Feeds the ADR text to cli_arcs_run.py and parses for three-lens challenge
    points, Bayesian posterior shift, recommended counter-positions.
    """
    findings: List[Dict[str, Any]] = []

    prompt = (
        f"Adversarial review of this ADR from Loki / Advisors / Bayesian perspectives. "
        f"Identify three-lens challenge points, Bayesian posterior shift, and "
        f"recommended counter-positions. ADR text:\n\n{adr_text}"
    )

    result = _invoke_cis_text(prompt, model=model)
    if result.get("status") != "ok":
        findings.append(_make_finding(
            operator="LAB",
            adr_path=adr_path,
            adr_section="(full ADR — adversarial lens)",
            severity="medium",
            finding_type="review_instrument_error",
            finding=f"LAB review instrument failed: {result.get('error', 'unknown')}",
            evidence=f"cli_arcs_run.py returned: {result}",
            recommendation="Run LAB review manually or fix the instrument before re-running.",
            action="fix_instrument_or_accept_manual_review",
        ))
        return findings

    raw = result.get("raw", {})
    gate = raw.get("gate_status", "unknown")
    distortions = raw.get("active_distortions", [])
    vector = raw.get("vector_action", "")

    severity = "high" if gate == "halt" else ("medium" if gate == "warn" else "low")

    finding_text = (
        f"LAB adversarial review via CIS pipeline: gate={gate.upper()}. "
        f"Three-lens challenge: {vector[:300]}."
    )
    if distortions:
        finding_text += f" Active challenges: {', '.join(distortions[:3])}."

    findings.append(_make_finding(
        operator="LAB",
        adr_path=adr_path,
        adr_section="(full ADR — adversarial lens)",
        severity=severity,
        finding_type="adversarial_challenge",
        finding=finding_text,
        evidence=f"ADR text length: {len(adr_text)} chars. cli_arcs_run.py signal: adversarial review prompt.",
        recommendation=(
            "For HALT: the adversarial lens found blocking challenges. "
            "Address each challenge point before marking the ADR canonical. "
            "LAB challenges are not necessarily resolvable — but none should be ignored."
            if gate == "halt" else
            "For WARN: the adversarial lens found visible challenge points. "
            "Acknowledge them in the ADR. None are ignored — but none are necessarily fatal."
            if gate == "warn" else
            "For PASS: the adversarial lens found no blocking challenges. "
            "LAB challenges acknowledged. Continue to next tier if applicable."
        ),
        action=(
            "address_challenges_before_canonical"
            if gate in ("halt", "warn") else
            "acknowledge_and_proceed"
        ),
    ))

    return findings


def _invoke_cis_text(prompt: str, model: str | None = None) -> Dict[str, Any]:
    """
    Invoke cli_arcs_run.py as a subprocess with --json.

    If `model` is provided, it is passed to the subprocess via the
    ARCS_MODEL environment variable so the Hermes model resolver can
    route to a specific model rather than the default.

    Returns the parsed JSON result, or an error dict.
    """
    cli_path = HERE / "cli_arcs_run.py"
    if not cli_path.exists():
        return {
            "status": "error",
            "error": f"cli_arcs_run.py not found at {cli_path}",
        }

    try:
        import subprocess

        env = {**os.environ, "ARCS_DIR": str(ARCS_DIR)}
        if model:
            env["ARCS_MODEL"] = model

        proc = subprocess.run(
            [sys.executable, str(cli_path), prompt, "--json"],
            capture_output=True,
            text=True,
            cwd=str(ARCS_DIR),
            timeout=120,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout after 120s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

    if proc.returncode != 0:
        stderr = proc.stderr.strip() if proc.stderr else ""
        return {
            "status": "error",
            "error": stderr or f"exit code {proc.returncode}",
            "stdout": proc.stdout.strip() if proc.stdout else "",
        }

    stdout = proc.stdout.strip()
    if not stdout:
        return {"status": "error", "error": "empty stdout from cli_arcs_run.py"}

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": f"cli_arcs_run.py returned non-JSON stdout: {stdout[:200]}",
            "stdout": stdout,
        }

    return {"status": "ok", "raw": parsed}


# ─── Tier router ──────────────────────────────────────────────────────────────

TIER_OPERATORS = {
    1: ["BAR"],
    2: ["BAR", "KINTSUGI"],
    3: ["BAR", "KINTSUGI", "LAB"],
    # Tier 4 (CONTRACT / axiom compliance) is not yet wired as a separate
    # instrument — it runs through the same CIS pipeline with an axiom-compliance
    # framing. For now, Tier 4 = Tier 3 + an explicit axiom-compliance note.
}


def run_adr_audit(
    adr_path: Path,
    tier: int,
    include_lab: bool = False,
    model: str | None = None,
) -> Dict[str, Any]:
    """
    Run the ADR review at the specified tier.

    Returns a review bundle:
        {
            "status": "ok" | "error",
            "adr": str,              # path to ADR file
            "tier": int,
            "operators_run": list[str],
            "findings": list[dict], # structured findings per operator
            "gate_summary": {
                "bar_gate": str,
                "kintsugi_gate": str,
                "lab_gate": str | None,
            },
            "overall": "pass" | "provisional" | "fail",
            "error": str | None,
        }
    """
    if tier not in TIER_OPERATORS:
        return {
            "status": "error",
            "error": f"Unknown tier {tier}. Valid tiers: {list(TIER_OPERATORS.keys())}",
        }

    operators_to_run = TIER_OPERATORS[tier]
    if include_lab and "LAB" not in operators_to_run:
        operators_to_run = operators_to_run + ["LAB"]

    # Load ADR text
    try:
        adr_text = _load_adr(adr_path)
    except SystemExit:
        raise
    except Exception as e:
        return {
            "status": "error",
            "error": f"Could not load ADR: {e}",
        }

    adr_str = str(adr_path)

    # Run each operator lens
    all_findings: List[Dict[str, Any]] = []
    gate_summary: Dict[str, Any] = {
        "bar_gate": "unknown",
        "kintsugi_gate": "unknown",
        "lab_gate": None,
    }

    for op_name in operators_to_run:
        op_name_upper = op_name.upper()
        if op_name_upper == "BAR":
            findings = _review_bar(adr_text, adr_str, model)
        elif op_name_upper == "KINTSUGI":
            findings = _review_kintsugi(adr_text, adr_str, model)
        elif op_name_upper == "LAB":
            findings = _review_lab(adr_text, adr_str, model)
        else:
            findings = [
                _make_finding(
                    operator=op_name,
                    adr_path=adr_str,
                    adr_section="(full ADR)",
                    severity="medium",
                    finding_type="unknown_operator",
                    finding=f"Operator '{op_name}' is not a recognized review lens.",
                    evidence="",
                    recommendation="Remove from operator list or add a review implementation.",
                    action="fix_operator_list",
                )
            ]

        all_findings.extend(findings)

        # Update gate summary from findings
        for f in findings:
            if f["operator"] == "BAR":
                gate_summary["bar_gate"] = f.get("severity", "unknown")
            elif f["operator"] == "KINTSUGI":
                gate_summary["kintsugi_gate"] = f.get("severity", "unknown")
            elif f["operator"] == "LAB":
                gate_summary["lab_gate"] = f.get("severity", "unknown")

    # Determine overall status
    severities = [f["severity"] for f in all_findings]
    if "critical" in severities:
        overall = "fail"
    elif "high" in severities:
        overall = "provisional"
    else:
        overall = "pass"

    return {
        "status": "ok",
        "adr": adr_str,
        "tier": tier,
        "operators_run": operators_to_run,
        "findings": all_findings,
        "gate_summary": gate_summary,
        "overall": overall,
    }


def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def _emit_json(result: Dict[str, Any], pretty: bool = True) -> None:
    indent = 2 if pretty else None
    print(json.dumps(result, indent=indent, default=str))


def _emit_text(result: Dict[str, Any]) -> None:
    """Human-readable ADR audit summary."""
    status = result.get("status", "?")
    if status == "error":
        print(f"\n❌ ADR Audit Error: {result.get('error', 'unknown')}")
        return

    adr = result.get("adr", "?")
    tier = result.get("tier", "?")
    overall = result.get("overall", "?")
    ops = result.get("operators_run", [])
    findings = result.get("findings", [])
    gates = result.get("gate_summary", {})

    print(f"\n⬡  ARCS ADR AUDIT — {adr}")
    print(f"   Tier {tier} | Operators: {', '.join(ops)}")
    print(f"   Overall: {overall.upper()}")
    print(f"   Gates: BAR={gates.get('bar_gate', '?')} | KINTSUGI={gates.get('kintsugi_gate', '?')} | LAB={gates.get('lab_gate', '?')}")
    print()

    if not findings:
        print("   No findings.")
        return

    severity_colors = {
        "critical": "\033[31m",
        "high": "\033[33m",
        "medium": "\033[36m",
        "low": "\033[32m",
        "reset": "\033[0m",
    }
    use_color = sys.stdout.isatty()

    for i, f in enumerate(findings, 1):
        sev = f.get("severity", "medium")
        color = severity_colors.get(sev, "") if use_color else ""
        reset = severity_colors["reset"] if use_color else ""
        op = f.get("operator", "?")
        ftype = f.get("type", "?")
        finding_text = f.get("finding", "")
        recommendation = f.get("recommendation", "")
        action = f.get("action", "")

        print(f"   Finding {i} [{op}] {sev.upper()} — {ftype}")
        print(f"     {color}Finding:{reset} {finding_text[:200]}")
        print(f"     {color}Evidence:{reset} {f.get('evidence', '')[:150]}")
        print(f"     {color}Recommendation:{reset} {recommendation[:200]}")
        print(f"     {color}Action:{reset} {action}")
        print()


def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="ARCS ADR quality-gate audit — structured findings via operator lenses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Tiers (from arcs-adr-review skill):
          1 — BAR only (risk/ruin gate)
          2 — BAR + KINTSUGI (phase gate)
          3 — BAR + KINTSUGI + LAB (full adversarial)
          4 — CONTRACT (axiom compliance) — falls back to Tier 3 + axiom note

        Examples:
          python adr_audit.py --adr ADR-032.md --tier 1 --format json
          python adr_audit.py --adr ADR-032.md --tier 2 --format text
          python adr_audit.py --adr ADR-032.md --tier 3 --include-lab --format json
        """),
    )

    parser.add_argument("--adr", required=True, help="Path to ADR file")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], required=True, help="Review tier (1–4)")
    parser.add_argument("--include-lab", action="store_true", help="Add LAB lens (for Tier 3+ or escalation)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--model", default=None, help="Model override for the CIS subprocess (e.g. poolside/laguna-xs-2.1:free)")

    args = parser.parse_args(argv)

    adr_path = Path(args.adr)
    if not adr_path.exists():
        _die(f"ADR file not found: {adr_path}")

    try:
        result = run_adr_audit(adr_path, args.tier, args.include_lab, args.model)
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
