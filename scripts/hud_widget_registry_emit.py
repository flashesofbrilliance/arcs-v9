#!/usr/bin/env python3
"""
hud_widget_registry_emit.py - generate runtime/specs/hud-widgets.json, the registry of the five
HUD gauges (fidelity, conviction, clarity, coherence, consonance). stdlib-only.

Patterned on scripts/operator_registry_emit.py: the WIDGETS table below is the declaration, the
output is generated, and the emitter REFUSES to write a registry holding a binding it cannot
resolve against the tree. Spec: _PROPOSALS/2026-10-15-hud-widget-lockups-spec.md (widget table);
ruling: _PROPOSALS/2026-10-19-hud-audit-ruling-sheet.md (C0 + D1-D5 as recommended, "widgets 1 to 5"
= the five gauges; D3 merges clarity/coherence at the question level and redefines consonance).

Each widget declares:
  reads     list of {kind, ...}; every read must resolve:
              json    {file, path}      file exists and the dotted path exists in it
              symbol  {file, symbol}    the identifier appears in the file
              prisma  {model, field}    the model block in prisma/schema.prisma has the field
  n         {unit, threshold}  threshold is an int, or null with a "why" (conviction: none until
            receipts are tagged real). Below threshold the widget renders GRAIN and prints n.
  emits     subset of EMIT_EVENTS
  operator  optional int; must be an op in operators/OPERATOR-REGISTRY.json that is not UNBUILT
  tool      optional "kind:name"; must exist in runtime/specs/tool-catalog.json

Tier 0, no model. Usage:
  python3 scripts/hud_widget_registry_emit.py              # regenerate
  python3 scripts/hud_widget_registry_emit.py --check      # exit 1 if stale or any binding fails
  python3 scripts/hud_widget_registry_emit.py --self-test  # known-bad fails, known-good passes
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runtime" / "specs" / "hud-widgets.json"
OP_REG = ROOT / "operators" / "OPERATOR-REGISTRY.json"
TOOLS = ROOT / "runtime" / "specs" / "tool-catalog.json"
PRISMA = ROOT / "prisma" / "schema.prisma"

EMIT_EVENTS = {"close", "move", "snap"}
UNIVERSE = "src/data/universe-field.json"

WIDGETS: list[dict] = [
    {"id": "fidelity", "title": "Fidelity",
     "reads": [{"kind": "symbol", "file": "src/lib/ygate.ts", "symbol": "renderResolution"},
               {"kind": "json", "file": UNIVERSE, "path": "nodes"}],
     "n": {"unit": "evidence (mapped files + commits in 28 days) or receipts", "threshold": 10},
     "emits": ["close", "move", "snap"]},
    {"id": "conviction", "title": "Conviction",
     "reads": [{"kind": "prisma", "model": "Receipt", "field": "nciScore"},
               {"kind": "json", "file": UNIVERSE, "path": "dimensions.conviction.signal"}],
     "n": {"unit": "receipts tagged real", "threshold": None,
           "why": "no reading until receipts are tagged real; prints No signal"},
     "emits": ["close", "move", "snap"]},
    {"id": "clarity", "title": "Clarity",
     "reads": [{"kind": "symbol", "file": "src/app/api/compass/route.ts", "symbol": "nci_by_lens"},
               {"kind": "json", "file": UNIVERSE, "path": "dimensions.clarity.nodes_clear"},
               {"kind": "json", "file": UNIVERSE, "path": "dimensions.clarity.nodes"}],
     "n": {"unit": "questions or lattice nodes", "threshold": 10},
     "emits": ["close", "move", "snap"]},
    {"id": "coherence", "title": "Coherence",
     "reads": [{"kind": "json", "file": UNIVERSE, "path": "dimensions.coherence.diamonds"},
               {"kind": "json", "file": UNIVERSE, "path": "dimensions.coherence.mean_hardness"},
               {"kind": "json", "file": UNIVERSE, "path": "dimensions.clarity.nodes"}],
     "n": {"unit": "lattice nodes", "threshold": 10},
     "emits": ["close", "move", "snap"]},
    {"id": "consonance", "title": "Consonance",
     "reads": [{"kind": "prisma", "model": "Receipt", "field": "nciScore"},
               {"kind": "prisma", "model": "Outcome", "field": "matched"}],
     "n": {"unit": "closed receipts per cohort", "threshold": 30},
     "emits": ["close", "move", "snap"],
     "operator": 19, "tool": "operator:arcs_accountant.py"},
]


def _dig(obj, path: str) -> bool:
    for part in path.split("."):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            return False
    return True


def _read(rel: str) -> str | None:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


def resolve_read(r: dict) -> str | None:
    """Return None if the read resolves, else the reason it does not."""
    kind = r.get("kind")
    if kind == "json":
        txt = _read(r.get("file", ""))
        if txt is None:
            return f"missing file {r.get('file')}"
        try:
            ok = _dig(json.loads(txt), r.get("path", ""))
        except ValueError:
            return f"{r['file']} is not valid JSON"
        return None if ok else f"path {r['path']} not in {r['file']}"
    if kind == "symbol":
        txt = _read(r.get("file", ""))
        if txt is None:
            return f"missing file {r.get('file')}"
        sym = r.get("symbol", "")
        return None if sym and re.search(rf"\b{re.escape(sym)}\b", txt) else f"symbol {sym} not in {r['file']}"
    if kind == "prisma":
        txt = _read("prisma/schema.prisma")
        if txt is None:
            return "missing prisma/schema.prisma"
        m = re.search(rf"^model\s+{re.escape(r.get('model', ''))}\s*\{{(.*?)^\}}", txt, re.M | re.S)
        if not m:
            return f"model {r.get('model')} not in schema"
        return None if re.search(rf"^\s*{re.escape(r.get('field', ''))}\s", m.group(1), re.M) \
            else f"field {r.get('field')} not on model {r['model']}"
    return f"unknown read kind {kind!r}"


def verify(widgets: list[dict], op_ids: dict[int, str], tools: set[str]) -> list[str]:
    """All binding problems for a widget set. Empty list means every binding resolves."""
    errs: list[str] = []
    seen: set[str] = set()
    for w in widgets:
        wid = w.get("id", "?")
        if wid in seen:
            errs.append(f"{wid}: duplicate id")
        seen.add(wid)
        if not w.get("reads"):
            errs.append(f"{wid}: declares no reads")
        for r in w.get("reads", []):
            why = resolve_read(r)
            if why:
                errs.append(f"{wid}: read unresolved: {why}")
        n = w.get("n") or {}
        if "threshold" not in n or not n.get("unit"):
            errs.append(f"{wid}: n needs unit and threshold")
        elif n["threshold"] is None and not n.get("why"):
            errs.append(f"{wid}: null threshold needs a why")
        elif n["threshold"] is not None and not isinstance(n["threshold"], int):
            errs.append(f"{wid}: threshold must be an int or null")
        bad = set(w.get("emits", [])) - EMIT_EVENTS
        if bad or not w.get("emits"):
            errs.append(f"{wid}: emits must be a non-empty subset of {sorted(EMIT_EVENTS)} (got {sorted(bad)})")
        if "operator" in w:
            st = op_ids.get(w["operator"])
            if st is None:
                errs.append(f"{wid}: operator {w['operator']} not in OPERATOR-REGISTRY.json")
            elif st == "UNBUILT":
                errs.append(f"{wid}: operator {w['operator']} is UNBUILT")
        if "tool" in w and w["tool"] not in tools:
            errs.append(f"{wid}: tool {w['tool']} not in tool-catalog.json")
    return errs


def load_ops() -> dict[int, str]:
    d = json.loads(OP_REG.read_text(encoding="utf-8"))
    return {o["op"]: o["status"] for o in d["operators"]}


def load_tools() -> set[str]:
    d = json.loads(TOOLS.read_text(encoding="utf-8"))
    return {f"{t['kind']}:{t['name']}" for t in d["tools"]}


def build(widgets: list[dict] = WIDGETS) -> dict:
    errs = verify(widgets, load_ops(), load_tools())
    if errs:
        sys.stderr.write("REFUSING TO EMIT - bindings that fail the tree:\n  " + "\n  ".join(errs) + "\n")
        raise SystemExit(2)
    return {
        "$schema": "arcs-hud-widget-registry/v1",
        "source_of_truth": "_PROPOSALS/2026-10-15-hud-widget-lockups-spec.md (widget table); ruling _PROPOSALS/2026-10-19-hud-audit-ruling-sheet.md",
        "generator": "scripts/hud_widget_registry_emit.py",
        "verification": "every read, operator and tool link resolved against the tree at emit",
        "widgets": [dict(w, order=i + 1) for i, w in enumerate(widgets)],
    }


def report(reg: dict) -> None:
    ws = reg["widgets"]
    print(f"widgets: {len(ws)} ({', '.join(w['id'] for w in ws)})")
    print("unresolved bindings: 0")
    nothr = [w["id"] for w in ws if w["n"]["threshold"] is None]
    print(f"judgment residue: thresholds are the spec's, not measured; no threshold: {', '.join(nothr) or 'none'}; "
          "views, drag/snap and the admin mount are the next row")


def self_test() -> int:
    ops = {19: "READY", 14: "PARTIAL", 6: "UNBUILT"}
    tools = {"operator:arcs_accountant.py"}
    good = copy.deepcopy(WIDGETS)
    fails = []
    if verify(good, ops, tools):
        fails.append(f"known-good set rejected: {verify(good, ops, tools)}")

    def bad(label, mutate):
        w = copy.deepcopy(WIDGETS)
        mutate(w)
        if not verify(w, ops, tools):
            fails.append(f"known-bad passed: {label}")

    bad("operator not in registry", lambda w: w[4].update(operator=99))
    bad("operator UNBUILT", lambda w: w[4].update(operator=6))
    bad("tool not in catalog", lambda w: w[4].update(tool="script:nope.py"))
    bad("json path missing", lambda w: w[2]["reads"][1].update(path="dimensions.clarity.nope"))
    bad("file missing", lambda w: w[3]["reads"][0].update(file="src/data/nope.json"))
    bad("symbol missing", lambda w: w[0]["reads"][0].update(symbol="noSuchSymbolZz"))
    bad("prisma field missing", lambda w: w[4]["reads"][1].update(field="nope"))
    bad("no n threshold key", lambda w: w[1]["n"].pop("threshold"))
    bad("null threshold without why", lambda w: w[1]["n"].pop("why"))
    bad("unknown emit", lambda w: w[0].update(emits=["explode"]))
    bad("no reads", lambda w: w[0].update(reads=[]))
    bad("duplicate id", lambda w: w[1].update(id="fidelity"))
    for f in fails:
        print("FAIL:", f, file=sys.stderr)
    if fails:
        return 1
    print("self-test OK (known-good passes; 12 known-bad each fail)")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed registry is stale or a binding fails")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    reg = build()
    text = json.dumps(reg, indent=2, ensure_ascii=False) + "\n"
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("hud-widgets.json missing or stale. Regenerate:\n  python3 scripts/hud_widget_registry_emit.py", file=sys.stderr)
            raise SystemExit(1)
        print(f"hud widget registry OK ({len(reg['widgets'])} widgets)")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    report(reg)


if __name__ == "__main__":
    main()
