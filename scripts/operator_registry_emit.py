#!/usr/bin/env python3
"""
operator_registry_emit.py — generate operators/OPERATOR-REGISTRY.json from the
canonical periodic table + a verified binding map. stdlib-only.

WHY THIS EXISTS (2026-09-27): an external "audit" of the operator suite mapped
its own invented 1..19 numbering onto files that do not implement those
operators (kryptonite_scorer.py as "Accountant", audit_service/ as "Librarian",
governance.py as "Immune"). A hand-written map lies silently; a generated one
that greps for every claimed symbol cannot. Numbering is LOCKED to
operators/docs/PERIODIC-TABLE.md (Zach, 2026-09-27).

Truth model per operator row:
  status = READY     binding declared AND file exists AND symbol found in source
           PARTIAL   symbol exists but there is no standalone runnable entrypoint
           BLOCKED   file + symbol exist but the module cannot import (missing deps)
                     (only assigned by --probe, which imports with the venv)
           UNBUILT   no binding declared; `nearest` names the closest real code
  Any mismatch between a declared binding and the tree is a HARD ERROR: the
  generator refuses to emit a registry that claims a symbol it cannot find.

Usage:
  python3 scripts/operator_registry_emit.py            # regenerate (static verify)
  python3 scripts/operator_registry_emit.py --probe    # + import-probe via operators/.venv
  python3 scripts/operator_registry_emit.py --check    # exit 1 if committed file is stale
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "operators"
TABLE = OPS / "docs" / "PERIODIC-TABLE.md"
OUT = OPS / "OPERATOR-REGISTRY.json"
VENV_PY = OPS / ".venv" / "bin" / "python"

# ---------------------------------------------------------------------------
# Binding map: periodic-table number -> real code. Every entry is grep-verified
# at emit time. `call` tells the bridge how to invoke:
#   apply_series      cls(**params).apply(list[float])
#   series_method     cls(np.asarray(data), **params).<entrypoint>()
#   callable          module.<entrypoint>(**input)
#   operator_client   operators/operator_client.py registry id (text or api mode)
#   none              runnable only via composition; PARTIAL
# ---------------------------------------------------------------------------
BINDINGS: dict[int, dict] = {
    1:  {"module": "core/atoms.py", "symbol": "FirstDerivative", "entrypoint": "apply",
         "call": "apply_series", "input": "series: list[float]; params: {spacing, order}"},
    2:  {"module": "core/atoms.py", "symbol": "SecondDerivative", "entrypoint": "apply",
         "call": "apply_series", "input": "series: list[float]; params: {spacing, order}"},
    3:  {"module": "arcs_kinematics.py", "symbol": "KinematicManifold", "entrypoint": "jerk",
         "call": "series_method", "input": "series: list[float]; params: {dt}",
         "note": "third derivative is the jerk() method of the 12-D manifold; no standalone atom"},
    4:  {"module": "core/atoms.py", "symbol": "WaveDiffusion", "entrypoint": "apply",
         "call": "apply_series", "input": "series: list[float]; params: {sigma, mode}"},
    5:  {"module": "core/atoms.py", "symbol": "PhaseCancel", "entrypoint": "apply",
         "call": "apply_series",
         "input": "series: list[float]; params: {sample_rate, targets[], bandwidth, attenuation}"},
    7:  {"module": "core/atoms.py", "symbol": "Decelerator", "entrypoint": "apply",
         "call": "apply_series", "input": "series: list[float]; params: {alpha, warm_start}"},
    12: {"module": "arcs_operators_lab.py", "symbol": "BayesianUpdate", "entrypoint": None,
         "call": "none", "input": "n/a",
         "note": "the Bayesian lens runs inside LABOperator.run(); no standalone updater"},
    13: {"module": "core/operators.py", "symbol": "Conductor", "entrypoint": "sequence",
         "call": "none", "input": "tasks: [{id, deps[], priority}]",
         "note": "module imports pandas + loguru (neither declared in pyproject); expect BLOCKED on probe"},
    14: {"module": "arcs_primitives.py", "symbol": "CoherenceReceipt", "entrypoint": "coherence_law_score",
         "call": "none", "input": "n/a",
         "note": "ARCS Law C = aA - b(S-S_min)^2 + gW is a method on the receipt, not a free atom"},
    16: {"module": "arcs_pipeline_v1.py", "symbol": "ARCSPipeline", "entrypoint": "run",
         "call": "operator_client", "client_id": "PIPELINE",
         "input": "structured: CoherenceSignal + FATEDReasoning + AxiomCheck + SomaticReading + hci_score + phase_id + next_action"},
    17: {"module": "arcs_operators_lab.py", "symbol": "LABOperator", "entrypoint": "run",
         "call": "operator_client", "client_id": "LAB",
         "input": "text signal (routed through the CIS pipeline)",
         "note": "Loki / Advisors / Bayesian three-lens adversarial review = the Detective role"},
    18: {"module": "arcs_constitutional_court.py", "symbol": "ConstitutionalCourt", "entrypoint": "adjudicate",
         "call": "none", "input": "sage_receipt + lab_assessment + bar_assessment + phase_id",
         "note": "only invoked on a BAR RUIN_RISK verdict; not a default pipeline step"},
    20: {"module": "arcs_operator20.py", "symbol": "Operator20", "entrypoint": "cultivate",
         "call": "callable", "adapter": "receipts_to_seeds",
         "input": "payload.receipts: list[dict] (>= MIN_CORPUS_SIZE for clusters); payload.phase_id",
         "note": "gated at 100 receipts; auto-sweep lives in arcs_api.cultivate_auto_sweep"},
    21: {"module": "arcs_store.py", "symbol": "ARCSStore", "entrypoint": "latest",
         "call": "callable", "input": "store_path; n (latest) | phase_id | status | nci range",
         "note": "append-only JSON receipt store; Librarian = store + retrieve"},
    22: {"module": "receipt_evaluator.py", "symbol": "evaluate_receipt", "entrypoint": "evaluate_receipt",
         "call": "callable", "input": "receipt: dict (nci_score, phase_id); repair: bool",
         "note": "Kintsugi phase gate over a DEWY receipt = the meta-review"},
    23: {"module": "arcs_trace_loki.py", "symbol": "LokiEngine", "entrypoint": "bar_review",
         "call": "none", "input": "TraceLogger-bound; open_debug_session(span_id) first"},
    26: {"module": "arcs_runtime_service.py", "symbol": "ARCSRuntimeService", "entrypoint": "run_pipeline",
         "call": "none", "input": "session-scoped; start_session() then run_pipeline(...)"},
}

# Closest real code for rows with no binding (so UNBUILT never reads as "nothing").
NEAREST: dict[int, str] = {
    6:  "no phase-lock primitive; PhaseCancel (5) is the only wave-domain atom",
    8:  "no resonance atom; Operator21 spline knots carry alignment implicitly",
    9:  "no composite HarmonyIndex; ~30 lines of weighted sum over atom outputs",
    10: "no noise filter atom; WaveDiffusion (4) smooths but does not separate signal/noise",
    11: "arcs_trace_loki.AbductiveCalibrator records calibration but is not a ConfidenceIndex",
    15: "no energy catalyst atom",
    19: "receipt_evaluator + prisma Outcome model measure outcomes; no Accountant operator (n=2 closed loops)",
    24: "arcs_operators_lab.LokiChallenge is generated inside LAB; no standalone steel-man",
    25: "no Shavasana pause anywhere in code (0 grep hits 2026-09-27)",
    27: "scripts/arcs_core.py Folksonomist builds taxonomies from scans; not wired as an operator",
    28: "operators/audit_service/ is an informativeness gate, not a transaction auditor",
}

ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*\*\*(\w+)\*\*\s*\|\s*([A-Za-z]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


def parse_table() -> list[dict]:
    rows = []
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        n = int(m.group(1))
        if n > 99:          # molecules (101..108) are compositions, not operators
            continue
        rows.append({"op": n, "symbol": m.group(2), "name": m.group(3),
                     "role": m.group(4).strip(), "function": m.group(5).strip()})
    rows.sort(key=lambda r: r["op"])
    return rows


def level_for(n: int) -> str:
    if n <= 15:
        return "atom"
    if n <= 21:
        return "boardroom"
    if n <= 25:
        return "chorus"
    return "superadmin"


def static_verify(b: dict) -> tuple[bool, str]:
    path = OPS / b["module"]
    if not path.exists():
        return False, f"missing file {b['module']}"
    src = path.read_text(encoding="utf-8", errors="replace")
    sym = b["symbol"]
    if not re.search(rf"^(class|def)\s+{re.escape(sym)}\b", src, re.M):
        return False, f"symbol {sym} not defined in {b['module']}"
    ep = b.get("entrypoint")
    if ep and ep != sym and not re.search(rf"^\s+def\s+{re.escape(ep)}\b", src, re.M):
        return False, f"entrypoint {ep} not found on {sym} in {b['module']}"
    return True, "ok"


def probe_imports(rows: list[dict]) -> None:
    """Import each bound module with the venv interpreter; record failures as BLOCKED."""
    if not VENV_PY.exists():
        for r in rows:
            r["probe"] = "skipped: operators/.venv absent (run operators/mcp-bridge.sh once)"
        return
    code = r'''
import importlib, json, os, sys
os.chdir(sys.argv[1]); sys.path.insert(0, sys.argv[1])
out = {}
for mod in json.loads(sys.argv[2]):
    name = mod[:-3].replace("/", ".")
    try:
        importlib.import_module(name); out[mod] = "ok"
    except Exception as e:
        out[mod] = f"{type(e).__name__}: {e}"
print(json.dumps(out))
'''
    mods = sorted({r["binding"]["module"] for r in rows if r.get("binding")})
    proc = subprocess.run([str(VENV_PY), "-c", code, str(OPS), json.dumps(mods)],
                          capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise SystemExit(f"probe failed: {proc.stderr}")
    res = json.loads(proc.stdout.strip().splitlines()[-1])
    for r in rows:
        b = r.get("binding")
        if not b:
            continue
        verdict = res.get(b["module"], "unknown")
        r["probe"] = verdict
        if verdict != "ok":
            r["status"] = "BLOCKED"
            r["blocked_reason"] = verdict


def build(probe: bool) -> dict:
    rows = parse_table()
    errors = []
    for r in rows:
        n = r["op"]
        r["level"] = level_for(n)
        b = BINDINGS.get(n)
        if b:
            ok, why = static_verify(b)
            if not ok:
                errors.append(f"op {n} ({r['name']}): {why}")
                continue
            r["binding"] = b
            r["status"] = "PARTIAL" if b["call"] == "none" else "READY"
        else:
            r["status"] = "UNBUILT"
            r["nearest"] = NEAREST.get(n, "none identified")
    if errors:
        sys.stderr.write("REFUSING TO EMIT — binding claims that fail the tree:\n  " + "\n  ".join(errors) + "\n")
        raise SystemExit(2)
    if probe:
        probe_imports(rows)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {
        "$schema": "arcs-operator-registry/v1",
        "source_of_truth": "operators/docs/PERIODIC-TABLE.md (numbering LOCKED 2026-09-27)",
        "generator": "scripts/operator_registry_emit.py",
        "verification": "every binding grep-verified at emit; --probe adds an import test via operators/.venv",
        "counts": counts,
        "operators": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="import-probe bound modules with operators/.venv")
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed registry is stale")
    a = ap.parse_args()
    reg = build(probe=a.probe)
    text = json.dumps(reg, indent=2, ensure_ascii=False) + "\n"
    if a.check:
        if not OUT.exists():
            print("registry missing", file=sys.stderr); raise SystemExit(1)
        cur = json.loads(OUT.read_text(encoding="utf-8"))
        # compare the static view only (probe fields are environment-dependent)
        strip = lambda d: [{k: v for k, v in r.items() if k not in ("probe", "blocked_reason")}
                           | ({"status": "READY"} if r.get("status") == "BLOCKED" and r.get("binding", {}).get("call") != "none" else {})
                           | ({"status": "PARTIAL"} if r.get("status") == "BLOCKED" and r.get("binding", {}).get("call") == "none" else {})
                           for r in d["operators"]]
        if strip(cur) != strip(reg):
            print("OPERATOR-REGISTRY.json is stale vs the periodic table / bindings. Regenerate:", file=sys.stderr)
            print("  python3 scripts/operator_registry_emit.py", file=sys.stderr)
            raise SystemExit(1)
        print(f"registry OK ({len(reg['operators'])} rows, {reg['counts']})")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  counts={reg['counts']}")


if __name__ == "__main__":
    main()
