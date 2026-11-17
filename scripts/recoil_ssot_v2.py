#!/usr/bin/env python3
"""Recoil SSOT v2: validator, v1 adapter and sweep (stdlib only).

The schema is runtime/specs/recoil-ssot-v2.schema.json; this script interprets it,
so the schema file stays the single source. On top of the structural check it runs
the cross-reference rules a JSON Schema cannot express (every cited atom exists,
every GROUNDED claim quotes its atom verbatim, a cell id is its own coordinate).

  python3 scripts/recoil_ssot_v2.py validate FILE...      # v2 files (or v1: adapted first)
  python3 scripts/recoil_ssot_v2.py adapt FILE [-o OUT]   # v1 -> v2 JSON
  python3 scripts/recoil_ssot_v2.py export FILE [-o OUT]  # v2 -> v1 JSON (drops v2-only keys)
  python3 scripts/recoil_ssot_v2.py sweep [DIR]           # every file in DIR (default runtime/recoil/generated)
  python3 scripts/recoil_ssot_v2.py fidelity GRADE [Y]    # render state set by code
  python3 scripts/recoil_ssot_v2.py --self-test

Shapes the adapter knows:
  six-tab.v1      the war-room SSOT (meta + page.blocks; opportunity, beliefs, ... optional).
                  Every v1 key is kept in place. Unknown top-level keys go to x_v1. The v1 export
                  restores them and the original key order (migration.v1_key_order).
  six-section.v1  the flat RecoilReport props shape (cover + loadBearingQuote, ...). It is a render
                  output, not an SSOT: wrapped whole under legacy.data, nothing lifted into atoms.
Anything else (codex, onedoor, profile, receipt pages, DEWY stubs) is listed as not a call SSOT.

Sweep exit code: 1 if any recognized SSOT fails validation or loses data on the round trip;
files that are not call SSOTs are listed with their reason and do not fail the sweep.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA_PATH = os.path.join(ROOT, "runtime", "specs", "recoil-ssot-v2.schema.json")
DEFAULT_DIR = os.path.join(ROOT, "runtime", "recoil", "generated")
SCHEMA_ID = "arcs.recoil.ssot.v2"
ADAPTER = "scripts/recoil_ssot_v2.py"

SIX_TAB_KEYS = ["meta", "opportunity", "beliefs", "kinematic_series", "insights",
                "next_steps", "redaction_policy", "page"]
V2_ONLY = ["schema", "call", "verbs", "claims", "cells", "atlas", "legacy", "migration", "x_v1"]
PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")


def load_schema(path: str = SCHEMA_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- structural check

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, path: str, msg: str) -> None:
        self.errors.append(f"{path or '$'}: {msg}")

    def warn(self, path: str, msg: str) -> None:
        self.warnings.append(f"{path or '$'}: {msg}")


def _resolve(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local $ref is supported: {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def check(value, schema: dict, root: dict, rep: Report, path: str = "") -> None:
    """Interpret the subset of JSON Schema 2020-12 the v2 schema uses."""
    if "$ref" in schema:
        check(value, _resolve(root, schema["$ref"]), root, rep, path)
        return
    if "const" in schema and value != schema["const"]:
        rep.err(path, f"must be {schema['const']!r}, got {value!r}")
        return
    if "enum" in schema and value not in schema["enum"]:
        rep.err(path, f"{value!r} not in {schema['enum']}")
        return
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](value) for t in types):
            rep.err(path, f"expected {'|'.join(types)}, got {type(value).__name__}")
            return
    if "x-vocab" in schema and value is not None and value not in schema["x-vocab"]:
        if not (isinstance(value, str) and PLACEHOLDER.search(value)):
            rep.warn(path, f"{value!r} is off the usual vocabulary {schema['x-vocab']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            rep.err(path, "empty string")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            rep.err(path, f"{value!r} does not match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            rep.err(path, f"{value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            rep.err(path, f"{value} > maximum {schema['maximum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            rep.err(path, f"needs at least {schema['minItems']} item(s)")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            rep.err(path, f"at most {schema['maxItems']} item(s), got {len(value)}")
        if "items" in schema:
            for i, item in enumerate(value):
                check(item, schema["items"], root, rep, f"{path}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                rep.err(path, f"missing required key {key!r}")
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        addl = schema.get("additionalProperties", True)
        for key, sub in value.items():
            kp = f"{path}.{key}" if path else key
            if key in props:
                check(sub, props[key], root, rep, kp)
                continue
            matched = [p for p in patterns if re.search(p, key)]
            for p in matched:
                check(sub, patterns[p], root, rep, kp)
            if matched:
                continue
            if addl is False:
                rep.err(kp, "key not allowed here")
            elif isinstance(addl, dict):
                check(sub, addl, root, rep, kp)


# --------------------------------------------------------------------------- cross-reference rules

def semantic(doc: dict, rep: Report) -> None:
    atoms = (doc.get("call") or {}).get("atoms") or []
    atom_text: dict[str, str] = {}
    for i, a in enumerate(atoms):
        aid = a.get("id")
        if aid in atom_text:
            rep.err(f"call.atoms[{i}].id", f"duplicate atom id {aid}")
        atom_text[aid] = a.get("text", "")
    for i, a in enumerate(atoms):
        if a.get("parent") and a["parent"] not in atom_text:
            rep.err(f"call.atoms[{i}].parent", f"unknown atom {a['parent']}")
        if a.get("kind") == "number" and "value" not in a:
            rep.warn(f"call.atoms[{i}]", "number atom has no value")

    def cites(path: str, ids) -> None:
        for j, aid in enumerate(ids or []):
            if aid not in atom_text:
                rep.err(f"{path}[{j}]", f"cites unknown atom {aid}")

    claim_ids: set[str] = set()
    for i, c in enumerate(doc.get("claims") or []):
        cid = c.get("id")
        if cid in claim_ids:
            rep.err(f"claims[{i}].id", f"duplicate claim id {cid}")
        claim_ids.add(cid)
    belief_ids = {b.get("id") for b in doc.get("beliefs") or []}

    for i, c in enumerate(doc.get("claims") or []):
        p = f"claims[{i}]"
        cites(f"{p}.cites", c.get("cites"))
        ev = c.get("evidence") or []
        if c.get("ruling") == "GROUNDED" and not ev:
            rep.err(p, "GROUNDED claim has no evidence quote")
        for j, e in enumerate(ev):
            aid, quote = e.get("atom"), e.get("quote", "")
            if aid not in atom_text:
                rep.err(f"{p}.evidence[{j}]", f"quotes unknown atom {aid}")
            elif quote and quote not in atom_text[aid]:
                rep.err(f"{p}.evidence[{j}]", f"quote not found verbatim in {aid}")
        if c.get("belief") and c["belief"] not in belief_ids:
            rep.err(f"{p}.belief", f"unknown belief {c['belief']}")

    for verb, vp in (doc.get("verbs") or {}).items():
        if isinstance(vp, dict):
            cites(f"verbs.{verb}.cites", vp.get("cites"))
            for j, cid in enumerate(vp.get("claims") or []):
                if cid not in claim_ids:
                    rep.err(f"verbs.{verb}.claims[{j}]", f"unknown claim {cid}")

    cell_ids: set[str] = set()
    for i, c in enumerate(doc.get("cells") or []):
        p = f"cells[{i}]"
        coord = ".".join(str(c.get(k)) for k in ("lens", "resolution", "operator", "verb", "l"))
        if c.get("id") != coord:
            rep.err(f"{p}.id", f"id {c.get('id')!r} is not its coordinate {coord!r}")
        if c.get("id") in cell_ids:
            rep.err(f"{p}.id", f"duplicate cell {c.get('id')}")
        cell_ids.add(c.get("id"))
        cites(f"{p}.cites", c.get("cites"))
        for j, cid in enumerate(c.get("claims") or []):
            if cid not in claim_ids:
                rep.err(f"{p}.claims[{j}]", f"unknown claim {cid}")

    for key in ("beliefs", "insights", "next_steps"):
        for i, item in enumerate(doc.get(key) or []):
            if isinstance(item, dict):
                cites(f"{key}[{i}].atoms", item.get("atoms"))

    atlas = doc.get("atlas") or {}
    kairos_ids: set[str] = set()
    for i, k in enumerate(atlas.get("kairos") or []):
        if k.get("atom") not in atom_text:
            rep.err(f"atlas.kairos[{i}].atom", f"unknown atom {k.get('atom')}")
        if k.get("belief") and k["belief"] not in belief_ids:
            rep.err(f"atlas.kairos[{i}].belief", f"unknown belief {k['belief']}")
        kairos_ids.add(k.get("id"))
    pools = {"atom": set(atom_text), "claim": claim_ids, "belief": belief_ids,
             "cell": cell_ids, "kairos": kairos_ids}
    for i, r in enumerate(atlas.get("refs") or []):
        pool = pools.get(r.get("kind"))
        if pool is not None and r.get("ref") not in pool:
            rep.err(f"atlas.refs[{i}].ref", f"unknown {r.get('kind')} {r.get('ref')}")

    placeholders = _count_placeholders(doc)
    if placeholders:
        rep.warn("", f"{placeholders} unfilled {{{{placeholder}}}} string(s) from the template")


def _count_placeholders(v) -> int:
    if isinstance(v, str):
        return 1 if PLACEHOLDER.search(v) else 0
    if isinstance(v, dict):
        return sum(_count_placeholders(x) for k, x in v.items() if not k.startswith("_"))
    if isinstance(v, list):
        return sum(_count_placeholders(x) for x in v)
    return 0


TURN_LINE = re.compile(r"^\[(\d{1,3}:\d{2}(?::\d{2})?)\]\s*[^:\[\]]{1,60}:\s*(.+)$")


def grounding(doc: dict, rep: Report, root: str) -> None:
    """Atoms against their source. Each utterance must sit verbatim in a transcript turn at its own t;
    each child atom (number, promise, ...) must sit verbatim in its parent. Without this a made-up atom
    passes, since the other checks only compare quotes with atom text (seat council 2026-11-16)."""
    call = doc.get("call") or {}
    atoms = call.get("atoms") or []
    by_id = {a.get("id"): a for a in atoms}
    for i, a in enumerate(atoms):
        par = by_id.get(a.get("parent"))
        if par is not None and a.get("text", "") not in par.get("text", ""):
            rep.err(f"call.atoms[{i}].text", f"not verbatim in its parent {a['parent']}")
    tpath = (call.get("source") or {}).get("transcript")
    if not tpath:
        if any(a.get("kind") == "utterance" for a in atoms):
            rep.warn("call.source", "no transcript cited; utterance atoms are not grounded")
        return
    full = os.path.join(root, tpath)
    if not os.path.isfile(full):
        rep.err("call.source.transcript", f"cited transcript not found: {tpath}")
        return
    turns: dict[str, list[str]] = {}
    for ln in open(full, encoding="utf-8", errors="replace").read().splitlines():
        m = TURN_LINE.match(ln.strip())
        if m:
            turns.setdefault(m.group(1), []).append(m.group(2).strip())
    for i, a in enumerate(atoms):
        if a.get("kind") != "utterance":
            continue
        text, at = a.get("text", ""), turns.get(str(a.get("t")), [])
        if not at:
            rep.err(f"call.atoms[{i}].t", f"{a.get('id')}: no transcript turn at {a.get('t')}")
        elif not any(text in turn for turn in at):
            rep.err(f"call.atoms[{i}].text", f"{a.get('id')}: not verbatim in the transcript turn at {a.get('t')}")


def validate(doc: dict, schema: dict | None = None, root: str | None = None) -> Report:
    schema = schema or load_schema()
    rep = Report()
    check(doc, schema, schema, rep)
    if isinstance(doc, dict):
        semantic(doc, rep)
        if root is not None:
            grounding(doc, rep, root)
    return rep


# --------------------------------------------------------------------------- fidelity (set by code)

def fidelity(letter: str | None, y_state: str | None = None, schema: dict | None = None) -> str:
    """Grade letter (A..E, NS, or None for not scored) plus Y state -> render state."""
    rule = (schema or load_schema())["x-fidelity"]
    if y_state and y_state in rule["y_override"]:
        return rule["y_override"][y_state]
    return rule["by_grade"].get(letter or "NS", "GRAIN")


# --------------------------------------------------------------------------- shapes and adapter

OTHER_SHAPES = [
    ("v1 codex page", {"header", "tabs", "subnav", "read"}),
    ("v1 one-door page", {"header", "blocks", "foot"}),
    ("v1 profile page", {"voice", "altitude", "resonance"}),
    ("v1 enriched profile", {"identity", "career_arc_one_thread"}),
    ("v1 receipt page", {"lede_cover", "ex_ante", "waveform"}),
    ("v1 diamond page", {"trajectory", "the_one_number"}),
    ("fork-grade taxonomy", {"taxonomic_claims"}),
    ("DEWY receipt stub", {"dewy", "true_north"}),
    ("ex-ante receipt", {"ex_ante", "close_loop"}),
    ("send receipt", {"_TYPE", "receipt"}),
    ("COURT pilot kit", {"kit", "compass_run"}),
]


def detect(doc) -> str:
    if not isinstance(doc, dict):
        return "not an object"
    if doc.get("schema") == SCHEMA_ID:
        return "v2"
    page = doc.get("page")
    if "meta" in doc and isinstance(page, dict) and "blocks" in page:
        return "six-tab.v1"
    if "cover" in doc and "loadBearingQuote" in doc:
        return "six-section.v1"
    keys = set(doc)
    for name, need in OTHER_SHAPES:
        if need <= keys:
            return name
    return "unknown shape"


def to_v2(doc: dict, stem: str | None = None) -> dict:
    kind = detect(doc)
    if kind == "v2":
        return copy.deepcopy(doc)
    clash = [k for k in V2_ONLY if k in doc]
    if clash:
        raise ValueError(f"v1 doc already uses v2 key(s) {clash}; refusing to adapt")
    order = list(doc.keys())
    if kind == "six-tab.v1":
        out: dict = {"schema": SCHEMA_ID}
        extra: dict = {}
        for k, v in doc.items():
            if k in SIX_TAB_KEYS or k.startswith("_"):
                out[k] = copy.deepcopy(v)
            else:
                extra[k] = copy.deepcopy(v)
        if extra:
            out["x_v1"] = extra
        out["call"] = {"atoms": []}
        out["migration"] = {"from": "six-tab.v1", "adapter": ADAPTER, "v1_key_order": order}
        return out
    if kind == "six-section.v1":
        m = doc.get("meta") or {}
        meta: dict = {"report_id": doc.get("reportId") or stem or ""}
        date = m.get("date") or _date_from(stem)
        if date:
            meta["date"] = date
        who = [p.get("name") for p in m.get("participants") or []
               if isinstance(p, dict) and p.get("name") and p.get("name") != "Zach Harris"]
        if who:
            meta["counterpart"] = who[0]
        return {"schema": SCHEMA_ID, "meta": meta, "call": {"atoms": []},
                "legacy": {"kind": "six-section", "data": copy.deepcopy(doc)},
                "migration": {"from": "six-section.v1", "adapter": ADAPTER, "v1_key_order": order}}
    raise ValueError(f"no adapter for shape: {kind}")


def _date_from(stem: str | None) -> str | None:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", stem or "")
    return m.group(1) if m else None


def to_v1(doc: dict) -> dict:
    mig = doc.get("migration") or {}
    if mig.get("from") == "six-section.v1":
        data = copy.deepcopy((doc.get("legacy") or {}).get("data") or {})
        return _reorder(data, mig.get("v1_key_order"))
    out = {k: copy.deepcopy(v) for k, v in doc.items() if k not in V2_ONLY}
    out.update(copy.deepcopy(doc.get("x_v1") or {}))
    return _reorder(out, mig.get("v1_key_order"))


def _reorder(d: dict, order) -> dict:
    if not order:
        return d
    out = {k: d[k] for k in order if k in d}
    out.update({k: v for k, v in d.items() if k not in out})
    return out


def lossless(v1: dict, stem: str | None = None) -> tuple[bool, str]:
    back = to_v1(to_v2(v1, stem))
    if back != v1:
        return False, "round trip changed content"
    if list(back.keys()) != list(v1.keys()):
        return False, "round trip changed top-level key order"
    a = json.dumps(v1, ensure_ascii=False, indent=2)
    b = json.dumps(back, ensure_ascii=False, indent=2)
    if a != b:
        return False, "round trip changed serialization"
    return True, "lossless"


# --------------------------------------------------------------------------- sweep

def sweep(directory: str, schema: dict) -> tuple[list[dict], bool]:
    rows, ok = [], True
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if not os.path.isfile(path) or name.startswith("."):
            continue
        stem = os.path.splitext(name)[0]
        row = {"file": name, "shape": "", "status": "", "reason": "", "warnings": 0}
        if not name.endswith(".json"):
            row.update(shape="not JSON", status="SKIP", reason="not a JSON file (notes, handoff, CSV or script)")
            rows.append(row)
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            row.update(shape="unparseable", status="FAIL", reason=f"JSON parse error: {e}")
            rows.append(row)
            ok = False
            continue
        kind = detect(doc)
        row["shape"] = kind
        if kind not in ("v2", "six-tab.v1", "six-section.v1"):
            row.update(status="NOT-SSOT", reason=f"{kind}: a page or receipt for another surface, not a call SSOT; no adapter")
            rows.append(row)
            continue
        v2 = to_v2(doc, stem)
        if kind != "v2":
            good, why = lossless(doc, stem)
            if not good:
                row.update(status="FAIL", reason=why)
                rows.append(row)
                ok = False
                continue
        rep = validate(v2, schema)
        row["warnings"] = len(rep.warnings)
        row["warning_list"] = rep.warnings
        if rep.errors:
            row.update(status="FAIL", reason="; ".join(rep.errors[:3]) + (f" (+{len(rep.errors) - 3} more)" if len(rep.errors) > 3 else ""))
            ok = False
        else:
            row.update(status="PASS", reason="round trip lossless; v2 valid" if kind != "v2" else "v2 valid")
        rows.append(row)
    return rows, ok


def print_sweep(rows: list[dict], verbose: bool) -> None:
    w = max(len(r["file"]) for r in rows) if rows else 10
    for r in rows:
        print(f"{r['status']:<8} {r['file']:<{w}}  {r['shape']:<16} warn={r['warnings']:<3} {r['reason']}")
        if verbose:
            for x in r.get("warning_list", []):
                print(f"{'':<8} {'':<{w}}    warn: {x}")
    tally: dict[str, int] = {}
    for r in rows:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print("summary: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) + f" (of {len(rows)} files)")


# --------------------------------------------------------------------------- self-test

def _good_v2() -> dict:
    g = {"letter": "B", "basis": "two atoms agree"}
    return {
        "schema": SCHEMA_ID,
        "meta": {"report_id": "2026-11-11-test", "date": "2026-11-11", "counterpart": "Test Person"},
        "beliefs": [{"id": "P1", "claim": "c", "inference": "OBS", "confidence": [0.4, 0.7],
                     "conviction": "MED", "verdict": "UPGRADE"}],
        "page": {"header": {}, "blocks": [{"type": "prose", "audience": "internal"}]},
        "call": {"source": {"granola_id": "x"}, "atoms": [
            {"id": "a001", "t": "0:12", "speaker": "Test Person", "kind": "utterance", "text": "We ship weekly and hire two PMs."},
            {"id": "a002", "t": "0:12", "speaker": "Test Person", "kind": "number", "text": "two PMs", "parent": "a001", "value": 2},
            {"id": "a003", "t": "1:05", "speaker": "Zach Harris", "kind": "promise", "text": "I will send the sample Friday.", "owner": "Zach Harris"},
        ]},
        "verbs": {v: {"verdict": f"{v} verdict", "cites": ["a001"], "grade": g}
                  for v in ("analyze", "assess", "evaluate", "synthesize", "recapitulate")},
        "claims": [{"id": "c001", "said": "They hire two PMs", "premise": "headcount is approved",
                    "mechanism": "a stated number on the call", "evidence": [{"atom": "a001", "quote": "hire two PMs"}],
                    "ruling": "GROUNDED", "cites": ["a001", "a002"], "belief": "P1", "grade": g}],
        "cells": [{"id": "D.Operational.COURT.assess.L2", "lens": "D", "resolution": "Operational", "operator": "COURT",
                   "verb": "assess", "l": "L2", "note": "the number decides scope", "cites": ["a002"], "claims": ["c001"], "grade": g}],
        "atlas": {"target": "arcs.atlas.v2", "file": "runtime/recoil/generated/2026-11-11-test.atlas.json",
                  "refs": [{"node": "n1", "kind": "claim", "ref": "c001", "grade": g}],
                  "kairos": [{"id": "k01", "atom": "a001", "belief": "P1", "note": "P1 moved", "grade": g}]},
    }


def self_test() -> int:
    schema = load_schema()
    fails = 0

    def expect(name: str, doc: dict, needle: str | None) -> None:
        nonlocal fails
        rep = validate(doc, schema)
        if needle is None:
            good = not rep.errors
        else:
            good = any(needle in e for e in rep.errors)
        print(f"{'ok  ' if good else 'FAIL'} {name}" + ("" if good else f"  errors={rep.errors}"))
        fails += 0 if good else 1

    expect("good v2 passes", _good_v2(), None)

    def mut(fn):
        d = _good_v2()
        fn(d)
        return d

    expect("wrong schema id", mut(lambda d: d.update(schema="v1")), "must be")
    expect("missing meta.date", mut(lambda d: d["meta"].pop("date")), "missing required key 'date'")
    expect("unknown top-level key", mut(lambda d: d.update(stray=1)), "key not allowed")
    expect("atom without speaker", mut(lambda d: d["call"]["atoms"][0].pop("speaker")), "missing required key 'speaker'")
    expect("atom with bad timestamp", mut(lambda d: d["call"]["atoms"][0].update(t="12s")), "does not match")
    expect("atom kind off-enum", mut(lambda d: d["call"]["atoms"][0].update(kind="vibe")), "not in")
    expect("duplicate atom id", mut(lambda d: d["call"]["atoms"][1].update(id="a001")), "duplicate atom id")
    expect("verb cites nothing", mut(lambda d: d["verbs"]["assess"].update(cites=[])), "at least 1")
    expect("verb cites unknown atom", mut(lambda d: d["verbs"]["assess"].update(cites=["a999"])), "unknown atom a999")
    expect("only four verbs", mut(lambda d: d["verbs"].pop("recapitulate")), "recapitulate")
    expect("verb without grade", mut(lambda d: d["verbs"]["analyze"].pop("grade")), "missing required key 'grade'")
    expect("claim without mechanism", mut(lambda d: d["claims"][0].pop("mechanism")), "mechanism")
    expect("ruling off-enum", mut(lambda d: d["claims"][0].update(ruling="TRUE")), "not in")
    expect("GROUNDED with no quote", mut(lambda d: d["claims"][0].update(evidence=[])), "no evidence quote")
    expect("quote not in atom", mut(lambda d: d["claims"][0]["evidence"][0].update(quote="hire ten PMs")), "not found verbatim")
    expect("claim moves unknown belief", mut(lambda d: d["claims"][0].update(belief="P9")), "unknown belief P9")
    expect("cell id is not its coordinate", mut(lambda d: d["cells"][0].update(verb="evaluate")), "is not its coordinate")
    expect("cell lens off-axis", mut(lambda d: d["cells"][0].update(lens="X")), "not in")
    expect("cell cites unknown atom", mut(lambda d: d["cells"][0].update(cites=["a404"])), "unknown atom a404")
    expect("grade letter off-scale", mut(lambda d: d["claims"][0].update(grade={"letter": "F", "basis": "x"})), "not in")
    expect("atlas ref to unknown claim", mut(lambda d: d["atlas"]["refs"][0].update(ref="c404")), "unknown claim c404")
    expect("kairos at unknown atom", mut(lambda d: d["atlas"]["kairos"][0].update(atom="a404")), "unknown atom a404")
    expect("audience off-enum", mut(lambda d: d["page"]["blocks"][0].update(audience="public")), "not in")
    expect("belief confidence out of 0..1", mut(lambda d: d["beliefs"][0].update(confidence=[0.4, 1.7])), "maximum")

    # grounding: atoms against the transcript they cite, children against their parent
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "t.txt"), "w").write(
            "[Granola x]\n\n[0:12] Test Person: We ship weekly and hire two PMs.\n[1:05] Me: I will send the sample Friday.\n")

        def ground(name: str, fn, needle: str | None) -> None:
            nonlocal fails
            d = _good_v2()
            d["call"]["source"]["transcript"] = "t.txt"
            fn(d)
            rep = validate(d, schema, root=td)
            good = not rep.errors if needle is None else any(needle in e for e in rep.errors)
            print(f"{'ok  ' if good else 'FAIL'} {name}" + ("" if good else f"  errors={rep.errors}"))
            fails += 0 if good else 1

        ground("grounded atoms pass", lambda d: None, None)
        ground("made-up utterance fails", lambda d: d["call"]["atoms"][0].update(text="We ship daily."), "not verbatim in the transcript")
        ground("utterance at a time with no turn fails", lambda d: d["call"]["atoms"][0].update(t="0:13"), "no transcript turn at 0:13")
        ground("child not in its parent fails", lambda d: d["call"]["atoms"][1].update(text="ten PMs"), "not verbatim in its parent")
        ground("missing transcript file fails", lambda d: d["call"]["source"].update(transcript="gone.txt"), "not found")

    # fidelity is set by code
    table = [("A", None, "SHARP"), ("B", "YELLOW", "SHARP"), ("C", None, "DEGRADED"), ("D", None, "GRAIN"),
             ("E", None, "GRAIN"), ("NS", None, "GRAIN"), (None, None, "GRAIN"), ("A", "PARADOX", "MOIRE")]
    for letter, y, want in table:
        got = fidelity(letter, y, schema)
        good = got == want
        print(f"{'ok  ' if good else 'FAIL'} fidelity({letter}, {y}) = {got}")
        fails += 0 if good else 1

    # adapter: six-tab round trip, extra key, order, refusal
    v1 = {"_TEMPLATE": "t", "meta": {"report_id": "2026-01-01-x", "date": "2026-01-01", "counterpart": "X"},
          "send_log": [{"to": "x"}], "opportunity": {"y_state": "YELLOW"},
          "page": {"header": {}, "blocks": [{"type": "prose", "audience": "both"}]}}
    v2 = to_v2(v1)
    checks = [
        ("six-tab detected", detect(v1) == "six-tab.v1"),
        ("unknown v1 key parked in x_v1", v2.get("x_v1") == {"send_log": [{"to": "x"}]} and "send_log" not in v2),
        ("adapted six-tab validates", not validate(v2, schema).errors),
        ("six-tab round trip lossless", lossless(v1)[0]),
        ("v2 enrichments drop on v1 export", "call" not in to_v1(dict(v2, verbs={}))),
    ]
    try:
        to_v2(dict(v1, claims=[]))
        checks.append(("refuses a v1 doc that uses a v2 key", False))
    except ValueError:
        checks.append(("refuses a v1 doc that uses a v2 key", True))
    six = {"reportId": "2026-02-02-y", "meta": {"date": "2026-02-02", "participants": [{"name": "Zach Harris"}, {"name": "Y Person"}]},
           "cover": {"title": "t"}, "loadBearingQuote": {"text": "q"}, "signalThreads": [], "protocol": {}}
    s2 = to_v2(six, "2026-02-02-y")
    checks += [
        ("six-section detected", detect(six) == "six-section.v1"),
        ("six-section wrapped whole", s2["legacy"]["data"] == six and s2["meta"]["counterpart"] == "Y Person"),
        ("six-section lifts no atoms", s2["call"]["atoms"] == []),
        ("adapted six-section validates", not validate(s2, schema).errors),
        ("six-section round trip lossless", lossless(six, "2026-02-02-y")[0]),
        ("other page shapes are not SSOTs", detect({"header": {}, "blocks": [], "foot": {}}) == "v1 one-door page"),
    ]
    try:
        to_v2({"header": {}, "blocks": [], "foot": {}})
        checks.append(("refuses an unknown shape", False))
    except ValueError:
        checks.append(("refuses an unknown shape", True))
    for name, good in checks:
        print(f"{'ok  ' if good else 'FAIL'} {name}")
        fails += 0 if good else 1

    print(f"self-test: {'PASS' if not fails else f'FAIL ({fails})'}")
    return 1 if fails else 0


# --------------------------------------------------------------------------- CLI

def _read(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write(doc: dict, out: str | None) -> None:
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="validate v2 files (v1 files are adapted first)")
    v.add_argument("files", nargs="+")
    v.add_argument("-v", "--verbose", action="store_true", help="print warnings too")
    a = sub.add_parser("adapt", help="v1 -> v2")
    a.add_argument("file")
    a.add_argument("-o", "--out")
    e = sub.add_parser("export", help="v2 -> v1 (drops v2-only keys)")
    e.add_argument("file")
    e.add_argument("-o", "--out")
    s = sub.add_parser("sweep", help="adapt, round-trip and validate every file in a directory")
    s.add_argument("dir", nargs="?", default=DEFAULT_DIR)
    s.add_argument("-v", "--verbose", action="store_true")
    s.add_argument("--json", action="store_true", help="machine-readable rows")
    f = sub.add_parser("fidelity", help="grade (+ Y state) -> render state")
    f.add_argument("grade")
    f.add_argument("y", nargs="?")
    args = ap.parse_args(argv)
    schema = load_schema()

    if args.cmd == "validate":
        bad = 0
        for path in args.files:
            doc = _read(path)
            stem = os.path.splitext(os.path.basename(path))[0]
            try:
                doc = to_v2(doc, stem)
            except ValueError as ex:
                print(f"FAIL {path}: {ex}")
                bad += 1
                continue
            rep = validate(doc, schema, root=os.getcwd())
            print(f"{'FAIL' if rep.errors else 'PASS'} {path} ({len(rep.errors)} error(s), {len(rep.warnings)} warning(s))")
            for x in rep.errors:
                print(f"  error: {x}")
            if args.verbose:
                for x in rep.warnings:
                    print(f"  warn: {x}")
            bad += 1 if rep.errors else 0
        return 1 if bad else 0
    if args.cmd == "adapt":
        _write(to_v2(_read(args.file), os.path.splitext(os.path.basename(args.file))[0]), args.out)
        return 0
    if args.cmd == "export":
        _write(to_v1(_read(args.file)), args.out)
        return 0
    if args.cmd == "sweep":
        rows, ok = sweep(args.dir, schema)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print_sweep(rows, args.verbose)
        return 0 if ok else 1
    if args.cmd == "fidelity":
        print(fidelity(None if args.grade.upper() in ("NONE", "NS") else args.grade.upper(), args.y, schema))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
