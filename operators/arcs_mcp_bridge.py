#!/usr/bin/env python3
"""
arcs_mcp_bridge.py — stdio MCP server exposing the ARCS operator suite to
Claude Code. Reads operators/OPERATOR-REGISTRY.json (generated, grep-verified)
and dispatches in-process through the same bindings; nothing here hand-writes
an operator map.

Design (decided 2026-09-27, session arcs-production-harness-arch):
  - Substrate: in-process import via the registry's `call` kind, falling back
    to operators/operator_client.py for the CIS/LAB/PIPELINE paths. No FastAPI
    hop, no cli_arcs_run text parsing.
  - Honesty: an operator whose registry status is UNBUILT / PARTIAL / BLOCKED
    still answers, with status=blocked and the reason. The seam stays visible
    (Kintsugi: never silently patch an integrity gap).
  - Persistence: every tool call appends one line to an append-only JSONL
    ledger (operators/ledger/operator-receipts.jsonl by default; override with
    ARCS_LEDGER_PATH). Git is the write lock; Supabase sync is a later,
    idempotent projection keyed on receipt_id.

Run:  operators/mcp-bridge.sh               (Claude Code launches this via .mcp.json)
      operators/.venv/bin/python operators/arcs_mcp_bridge.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "OPERATOR-REGISTRY.json"
DEFAULT_LEDGER = HERE / "ledger" / "operator-receipts.jsonl"
os.chdir(HERE)
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

BRIDGE_VERSION = "0.1.0"


# ── registry ────────────────────────────────────────────────────────────────

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        raise SystemExit("OPERATOR-REGISTRY.json missing: run python3 scripts/operator_registry_emit.py")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


REGISTRY = load_registry()
BY_OP: dict[int, dict] = {r["op"]: r for r in REGISTRY["operators"]}
BY_NAME: dict[str, int] = {}
for _r in REGISTRY["operators"]:
    BY_NAME[_r["name"].lower()] = _r["op"]
    BY_NAME[_r["symbol"].lower()] = _r["op"]


def resolve(op: str | int) -> dict:
    if isinstance(op, int) or str(op).isdigit():
        row = BY_OP.get(int(op))
    else:
        row = BY_OP.get(BY_NAME.get(str(op).lower(), -1))
    if not row:
        raise ValueError(f"unknown operator {op!r}; use list_operators")
    return row


# ── ledger ──────────────────────────────────────────────────────────────────

def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if hasattr(obj, "to_dict"):
        return _jsonable(obj.to_dict())
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return _jsonable(vars(obj))
    return str(obj)


def ledger_path() -> Path:
    return Path(os.environ.get("ARCS_LEDGER_PATH", DEFAULT_LEDGER))


def ledger_append(tool: str, op: Optional[int], inputs: dict, envelope: dict) -> str:
    rid = f"OPR-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    line = {
        "receipt_id": rid,
        "event_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bridge_version": BRIDGE_VERSION,
        "tool": tool,
        "op": op,
        "status": envelope.get("status"),
        "input_sha": _sha(inputs),
        "output_sha": _sha(envelope),
        "input": _jsonable(inputs),
        "envelope": _jsonable(envelope),
        "synced": False,
    }
    p = ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return rid


# ── dispatch ────────────────────────────────────────────────────────────────

def _blocked(row: dict, reason: str) -> dict:
    return {
        "operator": row["op"], "name": row["name"], "status": "blocked",
        "registry_status": row["status"], "blocked_reason": reason,
        "nearest": row.get("nearest"), "note": row.get("binding", {}).get("note"),
    }


def _import_symbol(binding: dict):
    modname = binding["module"][:-3].replace("/", ".")
    mod = importlib.import_module(modname)
    return getattr(mod, binding["symbol"]), mod


def dispatch(op: str | int, series: Optional[list[float]] = None,
             params: Optional[dict] = None, payload: Optional[dict] = None) -> dict:
    """Run one operator by registry binding. Never raises for a known operator;
    returns an envelope whose status is ok | blocked | error."""
    row = resolve(op)
    params = params or {}
    payload = payload or {}
    st = row["status"]
    if st == "UNBUILT":
        return _blocked(row, "operator is not implemented in this repo")
    if st == "BLOCKED":
        return _blocked(row, f"module cannot import: {row.get('blocked_reason')}")
    b = row["binding"]
    kind = b["call"]
    if kind == "none":
        return _blocked(row, f"{b['symbol']} exists but has no standalone entrypoint ({b['input']})")
    try:
        if kind == "apply_series":
            if series is None:
                return _blocked(row, "series: list[float] is required")
            cls, _ = _import_symbol(b)
            out = cls(**params).apply(series)
            result = {"series_out": _jsonable(out), "params": cls(**params).model_dump()}
        elif kind == "series_method":
            if series is None:
                return _blocked(row, "series: list[float] is required")
            import numpy as np
            cls, _ = _import_symbol(b)
            inst = cls(np.asarray(series, dtype=float), **params)
            result = {"series_out": _jsonable(getattr(inst, b["entrypoint"])()), "params": params}
        elif kind == "callable":
            sym, mod = _import_symbol(b)
            target = sym
            if isinstance(sym, type):                       # class: construct then call entrypoint
                inst = sym(**params)
                target = getattr(inst, b["entrypoint"])
            if b.get("adapter") == "receipts_to_seeds":     # Operator20: receipts -> seeds -> cultivate
                receipts = payload.get("receipts")
                if not receipts:
                    return _blocked(row, "payload.receipts: list[dict] is required")
                seeds = inst.extract_seeds(receipts, payload.get("spans"))
                payload = {"seeds": seeds, "phase_id": payload.get("phase_id", "phase_5")}
            result = _jsonable(target(**payload))
        elif kind == "operator_client":
            import operator_client as oc
            cid = b["client_id"]
            entry = oc.OPERATOR_REGISTRY[cid]
            if entry["mode"] == "text":
                signal = payload.get("signal") or payload.get("text")
                if not signal:
                    return _blocked(row, "payload.signal (natural-language) is required")
                result = oc.invoke_text(cid, signal, payload.get("extra_args"))
            else:
                result = oc.invoke_api(cid, dict(payload))
            if result.get("status") == "error":
                return {"operator": row["op"], "name": row["name"], "status": "error",
                        "error": result.get("error"), "client_id": cid}
        else:
            return _blocked(row, f"unknown call kind {kind}")
    except Exception as e:  # operator raised: surface, do not hide
        return {"operator": row["op"], "name": row["name"], "status": "error",
                "error": f"{type(e).__name__}: {e}", "binding": b}
    return {"operator": row["op"], "name": row["name"], "symbol": row["symbol"],
            "status": "ok", "registry_status": st, "binding": b, "result": result}


# ── MCP surface ─────────────────────────────────────────────────────────────

def build_server():
    from mcp.server.mcpserver import MCPServer

    srv = MCPServer(
        name="arcs-operators",
        version=BRIDGE_VERSION,
        instructions=(
            "ARCS v9 operator suite (numbering locked to operators/docs/PERIODIC-TABLE.md). "
            "Call list_operators first; run_operator answers with status=blocked for anything "
            "UNBUILT/PARTIAL/BLOCKED instead of faking a result. Every call is receipted to an "
            "append-only ledger."
        ),
    )

    @srv.tool(description="List the operator registry: op number, name, level, status (READY|PARTIAL|BLOCKED|UNBUILT), binding, nearest real code.")
    def list_operators(status: Optional[str] = None, level: Optional[str] = None) -> dict:
        rows = REGISTRY["operators"]
        if status:
            rows = [r for r in rows if r["status"] == status.upper()]
        if level:
            rows = [r for r in rows if r["level"] == level.lower()]
        slim = [{k: r.get(k) for k in ("op", "symbol", "name", "level", "status", "function")}
                | ({"input": r["binding"]["input"]} if r.get("binding") else {"nearest": r.get("nearest")})
                for r in rows]
        return {"source_of_truth": REGISTRY["source_of_truth"], "counts": REGISTRY["counts"], "operators": slim}

    @srv.tool(description="Full registry row for one operator (by number, name, or symbol), including binding, entrypoint, input contract, notes.")
    def describe_operator(op: str) -> dict:
        return resolve(op)

    @srv.tool(description=(
        "Run one operator by number/name. Atoms (1,2,3,4,5,7) take `series` (list of floats) + optional `params`. "
        "Operators 16 (Orchestrator/PIPELINE) and 17 (Detective/LAB) take `payload.signal` (natural language). "
        "20 Folksonomy takes payload.receipts; 21 Librarian takes payload.n; 22 Conductor takes payload.receipt. "
        "Unbuilt/partial/blocked operators return status=blocked with the reason. Receipted to the ledger."))
    def run_operator(op: str, series: Optional[list[float]] = None,
                     params: Optional[dict] = None, payload: Optional[dict] = None) -> dict:
        env = dispatch(op, series, params, payload)
        env["receipt_id"] = ledger_append("run_operator", env.get("operator"),
                                          {"op": op, "series": series, "params": params, "payload": payload}, env)
        return env

    @srv.tool(description="Run the natural-language CIS decision pipeline (HC -> LTE) on a signal. This is the primary text entrypoint. Receipted.")
    def run_cis(signal: str, to_archetype: Optional[str] = None, altitude: Optional[str] = None) -> dict:
        import operator_client as oc
        extra: list[str] = []
        if to_archetype:
            extra += ["--to", to_archetype]
        if altitude:
            extra += ["--alt", altitude]
        res = oc.invoke_text("CIS", signal, extra or None)
        env = {"status": "ok" if res.get("status") == "ok" else "error", **res}
        env["receipt_id"] = ledger_append("run_cis", None, {"signal": signal, "extra": extra}, env)
        return env

    @srv.tool(description="Golden Inchworm (Red Thread -> Golden Thread -> Needle) + Orthogonal Echo Detector over free text (RC-OPS-001). Receipted.")
    def run_inchworm(text: str, domain_texts: Optional[dict] = None) -> dict:
        from arcs_inchworm_echo import run_arcs_pipeline
        try:
            res = _jsonable(run_arcs_pipeline(text, domain_texts))
            env = {"status": "ok", "result": res}
        except Exception as e:
            env = {"status": "error", "error": f"{type(e).__name__}: {e}"}
        env["receipt_id"] = ledger_append("run_inchworm", None, {"text": text, "domain_texts": domain_texts}, env)
        return env

    @srv.tool(description="Tail the append-only operator receipt ledger (newest last).")
    def ledger_tail(n: int = 10) -> dict:
        p = ledger_path()
        if not p.exists():
            return {"path": str(p), "count": 0, "receipts": []}
        lines = p.read_text(encoding="utf-8").splitlines()
        out = [json.loads(l) for l in lines[-n:] if l.strip()]
        for r in out:                                # keep the tail readable
            r.pop("envelope", None); r.pop("input", None)
        return {"path": str(p), "count": len(lines), "receipts": out}

    return srv


# ── self-test ───────────────────────────────────────────────────────────────

def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "ledger.jsonl"
    os.environ["ARCS_LEDGER_PATH"] = str(tmp)
    fails = 0

    def check(label: str, cond: bool, detail: Any = ""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {str(detail)[:110]}")
        fails += 0 if cond else 1

    print("self-test: arcs_mcp_bridge")
    series = [0, 1, 4, 9, 16, 25, 36, 49]
    e = dispatch(4, series=series, params={"sigma": 1.0})
    check("op4 WaveDiffusion READY runs", e["status"] == "ok" and len(e["result"]["series_out"]) == len(series), e.get("error"))
    e = dispatch("FirstDerivative", series=series)
    check("op1 by name; derivative of n^2 ~ 2n", e["status"] == "ok" and abs(e["result"]["series_out"][3] - 6.0) < 1e-9, e.get("result", {}).get("series_out"))
    e = dispatch(3, series=series)
    check("op3 jerk via KinematicManifold", e["status"] == "ok", e.get("error"))
    e = dispatch(9)
    check("op9 HarmonyIndex UNBUILT -> blocked, with nearest", e["status"] == "blocked" and e.get("nearest"), e.get("blocked_reason"))
    e = dispatch(13)
    check("op13 TemporalSequencer BLOCKED (pandas) -> blocked", e["status"] == "blocked", e.get("blocked_reason"))
    e = dispatch(18)
    check("op18 Immune PARTIAL -> blocked (no standalone entrypoint)", e["status"] == "blocked", e.get("blocked_reason"))
    e = dispatch(21, payload={"q": "operator 21 librarian retrieval policy", "budget": 8000, "stakes": "medium"})
    check("op21 Librarian recommend(q, budget) runs; reserve_ratio + curation_debt + what_unconfirmed present",
          e["status"] == "ok" and all(k in e["result"] for k in ("items", "reserve_ratio", "curation_debt", "what_confirmed", "what_unconfirmed"))
          and e["result"]["budget"]["used_bytes"] <= 8000, e.get("error") or e["result"].get("reserve_ratio"))
    e = dispatch(22, payload={"receipt": {"nci_score": 72, "phase_id": "phase_3"}})
    check("op22 Conductor evaluate_receipt runs", e["status"] == "ok", e.get("error"))
    e = dispatch(19, payload={"receipts": [{"receipt_id": "a", "cohort": "founder", "nci_score": 60, "horizon": "WEEK", "drift_state": "LANDED"},
                                           {"receipt_id": "b", "cohort": "external", "nci_score": 40, "horizon": "WEEK", "drift_state": "ON_TRACK"}],
                              "outcomes": [{"receipt_id": "a", "matched": True, "regret_score": 2}]})
    check("op19 Accountant runs; n=1 -> sufficiency insufficient, no curve", e["status"] == "ok" and e["result"]["sufficiency"] == "insufficient"
          and e["result"]["cohorts"]["founder"]["calibration"]["spearman_nci_vs_regret"] is None, e.get("error") or e["result"]["totals"])
    e = dispatch(20, payload={"receipts": [{"question": "q", "nci_score": 50}]})
    check("op20 Folksonomy under-corpus returns a report (not an error)", e["status"] == "ok" and "n_seeds" in json.dumps(e["result"]) or e["status"] == "ok", e.get("error") or str(e.get("result"))[:80])
    try:
        dispatch(999); check("unknown op raises", False)
    except ValueError as ex:
        check("unknown op raises", True, ex)
    # MCP surface + ledger
    srv = build_server()
    import asyncio
    tools = asyncio.run(srv.list_tools())
    names = sorted(t.name for t in tools)
    check("MCP tools registered", names == sorted(["list_operators", "describe_operator", "run_operator", "run_cis", "run_inchworm", "ledger_tail"]), names)
    res = asyncio.run(srv.call_tool("run_operator", {"op": "4", "series": series}))
    check("call_tool run_operator via MCP", bool(res), type(res).__name__)
    res = asyncio.run(srv.call_tool("run_operator", {"op": "25"}))
    check("call_tool Shavasana -> blocked via MCP", "blocked" in json.dumps(_jsonable(res)), "")
    n = len(tmp.read_text().splitlines()) if tmp.exists() else 0
    check("ledger received 2 receipts", n == 2, n)
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
