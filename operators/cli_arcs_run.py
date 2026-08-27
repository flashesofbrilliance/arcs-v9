#!/usr/bin/env python3
"""
cli_arcs_run.py — ARCS v9 Decision CLI
=======================================
Primary usage (Sprint 8):
    python cli_arcs_run.py "Should I pivot the product?"
    python cli_arcs_run.py "Should I pivot the product?" --json
    python cli_arcs_run.py "Should I pivot the product?" --to EXECUTOR --jtbd "Q3 strategy"

Reads from stdin if no signal argument is given:
    echo "Should I pivot?" | python cli_arcs_run.py

Advanced subcommands:
    python cli_arcs_run.py hc      "text"       [--jtbd "..."]
    python cli_arcs_run.py receipt [phase]       [--all]
    python cli_arcs_run.py nci
    python cli_arcs_run.py audit

Output (default, human-readable):
    ⬡  ARCS SIGNAL ANALYSIS
    ✅ Gate: PASS  CSS 0.87 · IPS 0.97 · NCI 88/100 · Receiver: CONNECTOR @ L2

    True North
      The signal indicates...

    Signal
      • Retention cohorts show 94% NRR...
      • Pipeline coverage at 1.4× floor...

    Vector
      Transmit to CONNECTOR at L2 (IPS 0.97)

    Kairos Horizon
      This week

Output (--json):
    {"gate_status": "pass", "css": 0.87, "ips": 0.97, "nci": 88, ...}

Gate states:
    PASS  — Healthy signal, full translation, ship it
    WARN  — Translation completed with visible seam; review distortions
    HALT  — Transmission blocked; restore sender coherence first

ARCS-Canon-v9 § Kairos over Neuroticism:
    Opportune timing over anxiety. Act in the window.
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any

# ─── Paths ────────────────────────────────────────────────────────────────────

ARCS_DIR   = Path(__file__).parent
RECEIPT_DIR = ARCS_DIR

# ─── Subcommands that route to advanced handlers ─────────────────────────────

_SUBCOMMANDS = frozenset({"hc", "receipt", "nci", "audit"})

# ─── Colour helpers (graceful fallback: no tty, or NO_COLOR env) ─────────────

def _c(code: str, text: str) -> str:
    if sys.stdout.isatty() and not os.environ.get("NO_COLOR"):
        return f"\033[{code}m{text}\033[0m"
    return text

def bold(t: str)    -> str: return _c("1", t)
def green(t: str)   -> str: return _c("32", t)
def yellow(t: str)  -> str: return _c("33", t)
def red(t: str)     -> str: return _c("31", t)
def cyan(t: str)    -> str: return _c("36", t)
def dim(t: str)     -> str: return _c("2", t)

def _gate_color(gate: str) -> str:
    return {"pass": green, "warn": yellow, "halt": red}.get(gate, str)(gate.upper())

def _nci_color(nci: int) -> str:
    if nci >= 88: return green(str(nci))
    if nci >= 75: return yellow(str(nci))
    return red(str(nci))

def _score_bar(score: float, width: int = 20) -> str:
    filled = int(score * width)
    bar    = "█" * filled + "░" * (width - filled)
    color  = red if score >= 0.65 else yellow if score >= 0.35 else green
    return f"{color(bar)} {score:.3f}"

# ─── Signal extraction helpers ────────────────────────────────────────────────

def _extract_true_north(text: str) -> str:
    """First complete sentence of the translated signal = True North."""
    if not text:
        return "Signal too weak to extract True North."
    # Normalise line breaks so sentence detection works across wrapped paragraphs
    flat = text.replace("\n", " ").strip()
    for sep in (". ", "! ", "? "):
        idx = flat.find(sep)
        if idx > 15:
            return flat[:idx + 1].strip()
    # Fallback: first 120 chars
    return (flat[:120] + ("…" if len(flat) > 120 else "")).strip()

def _extract_bullets(translated: str, true_north: str) -> list[str]:
    """Extract up to 3 key signal bullets from the remainder of the translation."""
    # Strip True North from the front
    remainder = translated.replace("\n", " ").strip()
    tn_clean  = true_north.rstrip(".!?").strip()
    if remainder.startswith(tn_clean):
        remainder = remainder[len(tn_clean):].lstrip(". \t")

    if not remainder:
        return []

    # Split on sentence boundaries
    for sep in (". ", "! ", "? "):
        remainder = remainder.replace(sep, "|||")
    parts = [p.strip().rstrip(".!? ") for p in remainder.split("|||")]
    parts = [p for p in parts if len(p) > 20]
    return parts[:3]

def _kairos_horizon(resp: Any) -> str:
    """
    Derive Kairos timing window from altitude + urgency modifier.

    Logic:
        urgency_modifier > 0.85 OR altitude L0–L1 → Today
        urgency_modifier > 0.65 OR altitude L2     → This week
        altitude L3                                 → This quarter
        altitude L4–L5                              → Long arc (90+ days)
    """
    urgency = getattr(getattr(resp, "css_injected", None), "urgency_modifier", 0.7)
    alt     = getattr(resp, "target_altitude", 2)  # default L2
    if urgency >= 0.85 or alt <= 1:
        return "Today"
    if urgency >= 0.65 or alt == 2:
        return "This week"
    if alt == 3:
        return "This quarter"
    return "Long arc (90+ days)"

def _vector_action(resp: Any) -> str:
    """One clear next action sentence derived from gate state + distortions."""
    gate = getattr(resp, "gate_status", "pass")
    dists = getattr(resp, "active_distortions", [])
    if gate == "halt":
        block = dists[0] if dists else "active distortion pattern"
        return f"Restore sender coherence. Active block: {block}"
    if gate == "warn":
        seam_note = (f" | Distortions: {', '.join(dists[:2])}" if dists else "")
        return f"Proceed with awareness{seam_note}"
    archetype = getattr(resp, "target_archetype", "CONNECTOR")
    alt       = getattr(resp, "target_altitude", 2)
    ips       = getattr(resp, "ips", 0.0)
    return f"Transmit signal to {archetype} at altitude L{alt} (IPS {ips:.2f})"


# ─── CIS pipeline runner ──────────────────────────────────────────────────────

def _run_cis(signal: str, to_arch: str | None, alt_str: str | None, jtbd: str | None) -> dict:
    """
    Run the full CIS pipeline: HC → LTE (→ optional Field OS framing).
    Returns a plain dict suitable for JSON serialisation or human printing.
    """
    os.chdir(ARCS_DIR)   # ensure local imports resolve

    # ── Model override via ARCS_MODEL env var ───────────────────────────
    # When adr_audit.py (or any caller) sets ARCS_MODEL, forward it to the
    # Hermès model resolver so the subprocess uses a specific model rather
    # than the profile default. The resolver honours ARCS_MODEL when present.
    model_override = os.environ.get("ARCS_MODEL")
    if model_override:
        # Propagate to child processes (e.g. downstream CIS invocations)
        os.environ["ARCS_MODEL"] = model_override

    from arcs_cis import (
        CognitiveInterfaceSystem,
        CISRequest,
        AltitudeLevel,
        ARCHETYPE_REGISTRY,
    )

    # Resolve altitude
    target_alt = None
    if alt_str:
        alt_map = {
            "L0": AltitudeLevel.L0_VISCERAL,
            "L1": AltitudeLevel.L1_OPERATIONAL,
            "L2": AltitudeLevel.L2_TACTICAL,
            "L3": AltitudeLevel.L3_STRATEGIC,
            "L4": AltitudeLevel.L4_CONCEPTUAL,
            "L5": AltitudeLevel.L5_EPISTEMIC,
        }
        target_alt = alt_map.get(alt_str.upper())
        if target_alt is None:
            _die(f"Unknown altitude '{alt_str}'. Use L0–L5.")

    # Validate archetype
    if to_arch and to_arch.upper() not in ARCHETYPE_REGISTRY:
        _die(f"Unknown archetype '{to_arch}'. Valid: {', '.join(ARCHETYPE_REGISTRY)}")

    jtbd_anchor = jtbd or signal[:80]

    cis  = CognitiveInterfaceSystem(jtbd=jtbd_anchor)
    resp = cis.translate(CISRequest(
        raw_signal       = signal,
        target_archetype = to_arch.upper() if to_arch else None,
        target_altitude  = target_alt,
        jtbd_anchor      = jtbd_anchor,
    ))

    true_north = _extract_true_north(resp.translated_signal)
    bullets    = _extract_bullets(resp.translated_signal, true_north)
    kairos     = _kairos_horizon(resp)
    vector     = _vector_action(resp)

    return {
        # Gate & health
        "gate_status":        resp.gate_status,
        "css":                round(resp.css, 4),
        "ips":                round(resp.ips, 4),
        "nci":                resp.nci_grade,
        "channel_stable":     resp.channel_stable,
        # Structured output
        "true_north":         true_north,
        "signal_bullets":     bullets,
        "vector_action":      vector,
        "kairos_horizon":     kairos,
        # Receiver context
        "target_archetype":   resp.target_archetype,
        "target_altitude":    f"L{resp.target_altitude}",
        "source_altitude":    f"L{resp.source_altitude}",
        # Distortions
        "active_distortions": resp.active_distortions,
        # Trust / ROM state
        "trust_calibration":  round(resp.trust_calibration, 4),
        "rom_promotion_ready": resp.rom_promotion_ready,
        "turn_count":         resp.turn_count,
        # Provenance
        "visible_seam":       resp.visible_seam,
        "translated_signal":  resp.translated_signal,
    }


# ─── Human-readable printer ───────────────────────────────────────────────────

_GATE_SYM = {"pass": "✅", "warn": "⚠️ ", "halt": "🛑"}
_GATE_DESC = {
    "pass": "Sender healthy — signal transmitted with full fidelity",
    "warn": "Elevated distortion — signal transmitted with visible seam",
    "halt": "Transmission halted — restore sender coherence first",
}

def _print_result(r: dict) -> None:
    gate = r["gate_status"]
    sym  = _GATE_SYM.get(gate, "?")

    print()
    print(bold("⬡  ARCS SIGNAL ANALYSIS"))
    print()

    # ── Gate status line ─────────────────────────────────────────────────────
    gate_color = green if gate == "pass" else yellow if gate == "warn" else red
    print(f"  {sym} {gate_color(_GATE_DESC.get(gate, gate.upper()))}")
    print(
        f"     CSS {r['css']:.2f}  ·  IPS {r['ips']:.2f}  ·  "
        f"NCI {_nci_color(r['nci'])}/100  ·  "
        f"Receiver: {cyan(r['target_archetype'])} @ {r['target_altitude']}"
    )
    print()

    # ── HALT path ────────────────────────────────────────────────────────────
    if gate == "halt":
        print(bold("  ⛔  Translation halted"))
        for d in r["active_distortions"]:
            print(f"     • {red(d)}")
        print()
        print(f"  {bold('Next action:')}")
        print(f"     {r['vector_action']}")
        print()
        _print_trust_line(r)
        return

    # ── True North ───────────────────────────────────────────────────────────
    print(bold("  True North"))
    wrapped = textwrap.fill(
        r["true_north"], width=72,
        initial_indent="    ", subsequent_indent="    ",
    )
    print(wrapped)
    print()

    # ── Signal bullets ───────────────────────────────────────────────────────
    if r["signal_bullets"]:
        print(bold("  Signal"))
        for b in r["signal_bullets"]:
            wrapped = textwrap.fill(
                b, width=70,
                initial_indent="    • ", subsequent_indent="      ",
            )
            print(wrapped)
        print()

    # ── WARN distortion notice ───────────────────────────────────────────────
    if gate == "warn" and r["active_distortions"]:
        print(bold("  Distortions  ") + yellow("(seam applied)"))
        for d in r["active_distortions"]:
            print(f"    ⚠  {yellow(d)}")
        print()

    # ── Vector / next action ─────────────────────────────────────────────────
    print(bold("  Vector"))
    print(f"    {r['vector_action']}")
    print()

    # ── Kairos horizon ───────────────────────────────────────────────────────
    k = r["kairos_horizon"]
    k_color = red if k == "Today" else yellow if "week" in k else dim
    print(bold("  Kairos Horizon"))
    print(f"    {k_color(k)}")
    print()

    # ── Trust / NCI footer ───────────────────────────────────────────────────
    _print_trust_line(r)

    # ── Seam note ────────────────────────────────────────────────────────────
    if r.get("visible_seam"):
        print(dim(f"  ─ Seam: {r['visible_seam'][:100]}"))
    print()


def _print_trust_line(r: dict) -> None:
    nci   = r["nci"]
    trust = r["trust_calibration"]
    turns = r["turn_count"]
    width = 20
    bar   = "█" * int(trust * width) + "░" * (width - int(trust * width))
    t_col = green if trust >= 0.80 else yellow if trust >= 0.60 else red
    rom   = green("  ROM-ready ✓") if r["rom_promotion_ready"] else ""
    print(dim(
        f"  NCI {_nci_color(nci)}/100  ·  "
        f"Trust {t_col(bar)} {trust:.2f}{rom}  ·  "
        f"{turns} turn{'s' if turns != 1 else ''}"
    ))


# ─── Advanced subcommands ─────────────────────────────────────────────────────

def _cmd_hc(argv: list[str]) -> None:
    """Hemisphere check: sender cognitive health diagnostic."""
    import argparse
    p = argparse.ArgumentParser(prog="cli_arcs_run hc")
    p.add_argument("text")
    p.add_argument("--jtbd", metavar="ANCHOR", default=None)
    p.add_argument("--json", dest="json_out", action="store_true")
    args = p.parse_args(argv)

    os.chdir(ARCS_DIR)
    from arcs_hc import run_hc_scan
    csr = run_hc_scan(args.text, jtbd_anchor=args.jtbd)

    if args.json_out:
        print(json.dumps({
            "css": csr.css,
            "gate_status": csr.gate_status,
            "myth_engine_score": csr.myth_engine_score,
            "pattern_engine_score": csr.pattern_engine_score,
            "temporal_drift_score": csr.temporal_drift_score,
            "active_distortions": csr.active_distortions,
            "recommended_action": csr.recommended_action,
        }, indent=2))
        return

    sym = {"pass": "✅", "warn": "⚠️ ", "halt": "🛑"}.get(csr.gate_status, "?")
    print(bold("\n⬡  HEMISPHERE CHECK"))
    print()
    print(f"  {sym} CSS:             {csr.css:.3f}  {_gate_color(csr.gate_status)}")
    print()
    print(bold("  Engine Scores"))
    print(f"    Myth Engine:     {_score_bar(csr.myth_engine_score)}")
    print(f"    Pattern Engine:  {_score_bar(csr.pattern_engine_score)}")
    print(f"    Temporal Drift:  {_score_bar(csr.temporal_drift_score)}")
    print()
    print(bold("  Raw Axes"))
    print(f"    ER  (Epistemic Register):    {csr.epistemic_register:.3f}")
    print(f"    EAS (Evidence Anchoring):    {csr.evidence_anchoring:.3f}")
    print(f"    PEI (Pattern Extrapolation): {csr.pattern_extrapolation:.3f}")
    print(f"    JSD (JTBD Distance):         {csr.jtbd_distance:.3f}")
    print(f"    NCS (Narrative Coherence):   {csr.narrative_coherence:.3f}")
    print(f"    UI  (Urgency Index):         {csr.urgency_index:.3f}")
    print()
    if csr.active_distortions:
        print(bold("  Active Distortions"))
        for d in csr.active_distortions:
            print(f"    • {yellow(d)}")
        print()
    rec_color = red if csr.gate_status == "halt" else yellow if csr.gate_status == "warn" else green
    print(f"  {rec_color('Recommendation:')} {csr.recommended_action}")
    print()


def _cmd_receipt(argv: list[str]) -> None:
    """View decision receipts."""
    import argparse
    p = argparse.ArgumentParser(prog="cli_arcs_run receipt")
    p.add_argument("phase", nargs="?", default=None)
    p.add_argument("--all", action="store_true")
    p.add_argument("--json", dest="json_out", action="store_true")
    args = p.parse_args(argv)

    receipts = sorted(RECEIPT_DIR.glob("decision_receipt_phase*.json"))
    if not receipts:
        print(red("  No decision receipts found."))
        return

    if args.phase:
        receipts = [r for r in receipts if args.phase.lower().replace(" ", "_") in r.name.lower()]
        if not receipts:
            print(red(f"  No receipt found for phase '{args.phase}'."))
            return

    if not args.all and not args.phase:
        receipts = receipts[-1:]

    if args.json_out:
        out = []
        for path in receipts:
            try:
                with open(path) as f:
                    out.append(json.load(f))
            except Exception:
                pass
        print(json.dumps(out, indent=2))
        return

    print(bold(f"\n⬡  DECISION RECEIPTS ({len(receipts)} shown)\n"))
    for path in receipts:
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception:
            continue

        nci   = d.get("nci_self_grade", "?")
        label = d.get("on_purpose_label", "?")
        name  = d.get("phase_name", path.stem)
        irrev = d.get("irreversibility_score", "?")
        seam  = d.get("kintsugi_note")

        label_color = green if label == "aligned" else yellow if "good" in str(label) else red
        print(f"  {bold(name)}")
        print(f"    File:          {dim(path.name)}")
        print(f"    NCI:           {_nci_color(int(nci)) if isinstance(nci, (int, float)) else nci}/100")
        print(f"    On-purpose:    {label_color(label)}")
        print(f"    Irreversible:  {irrev}")
        if seam:
            print(f"    {yellow('⚑ Kintsugi:')}   {dim(seam[:80])}{'...' if len(seam) > 80 else ''}")
        direction = d.get("reasoning", {}).get("direction", "")
        if direction:
            wrapped = textwrap.fill(
                direction, width=68,
                initial_indent="    ", subsequent_indent="    ",
            )
            print(f"  {bold('  Direction:')}")
            print(wrapped)
        artifacts = d.get("artifacts_shipped", [])
        if artifacts:
            print(f"    Shipped:       {', '.join(str(a) for a in artifacts[:4])}{'…' if len(artifacts) > 4 else ''}")
        print()


def _cmd_nci(argv: list[str]) -> None:
    """Current NCI from stored receipts."""
    import argparse
    p = argparse.ArgumentParser(prog="cli_arcs_run nci")
    p.add_argument("--json", dest="json_out", action="store_true")
    args = p.parse_args(argv)

    receipts = sorted(RECEIPT_DIR.glob("decision_receipt_phase*.json"))
    scores, labels = [], []
    for path in receipts:
        try:
            with open(path) as f:
                d = json.load(f)
            s = d.get("nci_self_grade")
            if s is not None:
                scores.append(int(s))
                labels.append(d.get("on_purpose_label", ""))
        except Exception:
            continue

    if not scores:
        print(red("  No receipts found."))
        return

    avg             = sum(scores) / len(scores)
    latest          = scores[-1]
    aligned         = sum(1 for l in labels if l == "aligned")
    on_purpose_rate = aligned / len(labels) if labels else 0.0
    nci_computed    = int((on_purpose_rate * 0.7 + 0.6 * 0.3) * 100)

    # phase_id → best NCI
    phase_scores: dict[str, int] = {}
    for path in RECEIPT_DIR.glob("decision_receipt_phase*.json"):
        try:
            with open(path) as f:
                d = json.load(f)
            pid = d.get("phase_id", "").lower().replace(" ", "_")
            v   = d.get("nci_self_grade")
            if pid and v is not None:
                phase_scores[pid] = max(phase_scores.get(pid, 0), int(v))
        except Exception:
            continue

    gates = [
        ("phase_1", "Phase 1", 75),
        ("phase_2", "Phase 2", 82),
        ("phase_3", "Phase 3", 85),
        ("phase_4", "Phase 4", 88),
        ("phase_5", "Phase 5", 86),
        ("phase_6", "Phase 6", 88),
    ]

    if args.json_out:
        gate_data = []
        for pid, label, threshold in gates:
            s = phase_scores.get(pid)
            gate_data.append({
                "phase": label, "threshold": threshold,
                "nci": s, "passed": (s is not None and s >= threshold),
            })
        print(json.dumps({
            "latest": latest, "average": round(avg, 1),
            "on_purpose_rate": round(on_purpose_rate, 3),
            "nci_computed": nci_computed, "phases": gate_data,
        }, indent=2))
        return

    print(bold("\n⬡  NAVIGATIONAL CONFIDENCE INDEX\n"))
    print(f"  Latest NCI:          {_nci_color(latest)}/100")
    print(f"  Average ({len(scores)} phases):   {_nci_color(int(avg))}/100")
    print(f"  On-purpose rate:     {green(f'{on_purpose_rate:.0%}')}")
    print(f"  Computed NCI:        {_nci_color(nci_computed)}/100")
    print()
    print(bold("  Phase Gates"))
    for pid, label, threshold in gates:
        s = phase_scores.get(pid)
        if s is None:
            status = dim("  pending")
        elif s >= threshold:
            status = green(f"  ✓ {s}/100 (gate: {threshold})")
        else:
            status = red(f"  ✗ {s}/100 (gate: {threshold})")
        print(f"    {label}: {status}")
    print()


def _cmd_audit(argv: list[str]) -> None:
    """Meta-audit summary."""
    import argparse
    p = argparse.ArgumentParser(prog="cli_arcs_run audit")
    p.parse_args(argv)

    audit_path = ARCS_DIR / "ARCS_Meta_Audit_v9.md"
    print(bold("\n⬡  ARCS META-AUDIT\n"))
    if not audit_path.exists():
        print(red("  ARCS_Meta_Audit_v9.md not found. Run from the ARCS directory."))
        return

    with open(audit_path) as f:
        lines = f.readlines()

    in_section, printed = False, 0
    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("## Executive Finding"):
            in_section = True
        if in_section:
            if stripped.startswith("## ") and printed > 3:
                break
            print("  " + stripped)
            printed += 1

    print()
    print(bold("  Sprint Status (CIS plan, Sprints 0–9)"))
    sprint_status = [
        ("0", "Data models wired",                  True),
        ("1", "Altitude Detector live, unit tested", True),
        ("2", "Codex archetype registry populated",  True),
        ("3", "CSR cold-start + Bayesian update",    True),
        ("4", "LTE stubs end-to-end",                True),
        ("5", "HC → LTE integration (IPS ≥ 0.95)",  True),
        ("6", "HC wired upstream, CSS locked",       True),
        ("7", "CSS injection in all 7 LTE stages",   True),
        ("8", "cli_arcs_run.py primary interface",   True),
        ("9", "ROM_CHANGELOG.md + operator contract", True),
    ]
    for num, label, done in sprint_status:
        sym = green("✓") if done else dim("○")
        print(f"    Sprint {num}: {sym}  {label if done else dim(label)}")
    print()


# ─── Help ─────────────────────────────────────────────────────────────────────

def _print_help() -> None:
    print(textwrap.dedent(f"""
    {bold('ARCS v9 Decision CLI')}

    {bold('Primary usage:')}
      python cli_arcs_run.py "Should I pivot the product?"
      python cli_arcs_run.py "Should I pivot?" --json
      python cli_arcs_run.py "Should I pivot?" --to EXECUTOR --alt L1 --jtbd "Q3 strategy"
      echo "Should I pivot?" | python cli_arcs_run.py

    {bold('Advanced subcommands:')}
      python cli_arcs_run.py hc      "text"     [--jtbd "anchor"]
      python cli_arcs_run.py receipt [phase]    [--all] [--json]
      python cli_arcs_run.py nci               [--json]
      python cli_arcs_run.py audit

    {bold('Flags (primary mode):')}
      --json            Machine-readable JSON output (Next.js API bridge)
      --to ARCHETYPE    Target receiver archetype
      --alt LEVEL       Target altitude (L0–L5)
      --jtbd ANCHOR     Job-to-be-done anchor for HC temporal drift scoring

    {bold('Archetypes:')}
      QUANT  CONNECTOR  ARCHITECT  INSTITUTIONALIST  EXECUTOR  PHILOSOPHER  CAVEMAN

    {bold('Altitudes:')}
      L0 Visceral   L1 Operational  L2 Tactical (default)
      L3 Strategic  L4 Conceptual   L5 Epistemic

    {bold('Gate states:')}
      PASS  Sender healthy — signal transmitted with full fidelity
      WARN  Elevated distortion — transmitted with visible Kintsugi seam
      HALT  Transmission blocked — restore sender coherence first

    {bold('Environment:')}
      ARCS_DEBUG=1   Print full traceback on error
      NO_COLOR=1     Disable ANSI colours
    """))


# ─── Error helper ─────────────────────────────────────────────────────────────

def _die(msg: str) -> None:
    print(red(f"  Error: {msg}"), file=sys.stderr)
    sys.exit(1)


# ─── Entry point ─────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    # ── No arguments: show help or read stdin ──────────────────────────────
    if not argv:
        if not sys.stdin.isatty():
            signal = sys.stdin.read().strip()
            if signal:
                argv = [signal]
            else:
                _print_help()
                return
        else:
            _print_help()
            return

    first = argv[0]

    # ── Route advanced subcommands ─────────────────────────────────────────
    if first in _SUBCOMMANDS:
        handler = {
            "hc":      _cmd_hc,
            "receipt": _cmd_receipt,
            "nci":     _cmd_nci,
            "audit":   _cmd_audit,
        }[first]
        try:
            handler(argv[1:])
        except KeyboardInterrupt:
            print("\n  Interrupted.")
            sys.exit(0)
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n{red('Error:')} {e}", file=sys.stderr)
            if os.environ.get("ARCS_DEBUG"):
                import traceback; traceback.print_exc()
            sys.exit(1)
        return

    if first in ("--help", "-h", "help"):
        _print_help()
        return

    # ── Primary path: signal → CIS pipeline → structured output ───────────
    # Parse primary-mode flags; treat bare words as part of the signal
    import argparse
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--json",   dest="json_out",  action="store_true")
    p.add_argument("--to",     metavar="ARCHETYPE", default=None)
    p.add_argument("--alt",    metavar="LEVEL",    default=None)
    p.add_argument("--jtbd",   metavar="ANCHOR",   default=None)
    p.add_argument("--help",   "-h",              action="store_true")
    parsed, remaining = p.parse_known_args(argv)

    if parsed.help:
        _print_help()
        return

    # Everything that isn't a flag is the signal
    signal_parts = [w for w in remaining if not w.startswith("-")]
    signal       = " ".join(signal_parts).strip()

    if not signal:
        _die("No signal provided. Run with --help for usage.")

    try:
        result = _run_cis(signal, parsed.to, parsed.alt, parsed.jtbd)
    except KeyboardInterrupt:
        print("\n  Interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{red('Error:')} {e}", file=sys.stderr)
        if os.environ.get("ARCS_DEBUG"):
            import traceback; traceback.print_exc()
        sys.exit(1)

    if parsed.json_out:
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_result(result)


if __name__ == "__main__":
    main()
