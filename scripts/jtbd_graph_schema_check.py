#!/usr/bin/env python3
"""Validate a JTBD graph ({atoms, edges}) against runtime/specs/jtbd-graph-schema.json.

Stdlib only. Usage:
  python3 scripts/jtbd_graph_schema_check.py GRAPH.json   # exit 1 on any finding
  python3 scripts/jtbd_graph_schema_check.py --self-test  # good fixture passes, every bad fixture fails
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "runtime/specs/jtbd-graph-schema.json")
FIX = os.path.join(ROOT, "runtime/specs/fixtures/jtbd-graph")


def check(graph, schema):
    out = []
    ns_map = schema["id_scheme"]["namespaces"]
    kinds = schema["kinds"]
    seen, byid = set(), {}
    for a in graph.get("atoms", []):
        miss = [k for k in schema["atom_required"] if k not in a]
        if miss:
            out.append(f"ATOM-FIELDS {a.get('id')}: missing {miss}"); continue
        aid, kind, src = a["id"], a["kind"], a["source"]
        if kind not in kinds:
            out.append(f"UNKNOWN-KIND {aid}: {kind}"); continue
        smiss = [k for k in schema["atom_source_required"] if k not in src]
        if smiss:
            out.append(f"SOURCE-FIELDS {aid}: missing {smiss}")
        # namespace = first two segments; a key may itself contain ':' (route params like /:slug)
        ns = ":".join(aid.split(":", 2)[:2]) if aid.count(":") >= 2 else None
        if ns not in ns_map or not ns.startswith(kind + ":"):
            out.append(f"UNKNOWN-NAMESPACE {aid}: kind {kind}"); continue
        if not re.match(ns_map[ns]["pattern"], aid):
            out.append(f"ID-PATTERN {aid}")
        # stability: the id is re-derivable from the source's natural key, nothing else
        if aid != f"{ns}:{src.get('key')}":
            out.append(f"UNSTABLE-ID {aid}: not derived from source key {src.get('key')!r}")
        if src.get("catalog") != ns_map[ns]["source"]:
            out.append(f"SOURCE-MISMATCH {aid}: catalog {src.get('catalog')!r}")
        if aid in seen:
            out.append(f"DUPLICATE-ID {aid}")
        seen.add(aid); byid[aid] = kind
    fmts = {k: re.compile(v) for k, v in schema["evidence_formats"].items()}
    triples = set()
    for e in graph.get("edges", []):
        tag = f"{e.get('from')} -{e.get('type')}-> {e.get('to')}"
        miss = [k for k in schema["edge_required"] if k not in e]
        if miss:
            out.append(f"EDGE-FIELDS {tag}: missing {miss}"); continue
        et = schema["edge_types"].get(e["type"])
        if not et:
            out.append(f"UNKNOWN-EDGE-TYPE {tag}"); continue
        fk, tk = byid.get(e["from"]), byid.get(e["to"])
        if fk is None or tk is None:
            out.append(f"DANGLING-EDGE {tag}"); continue
        if [fk, tk] not in et["pairs"]:
            out.append(f"ILLEGAL-PAIR {tag}: ({fk}, {tk})")
        if e["from"] == e["to"]:
            out.append(f"SELF-EDGE {tag}")
        ev = e["evidence"]
        if not isinstance(ev, list) or not ev:
            out.append(f"NO-EVIDENCE {tag}")
        else:
            for item in ev:
                if not any(fmts[f].match(str(item)) for f in et["evidence"]):
                    out.append(f"BAD-EVIDENCE {tag}: {item!r} (allowed {et['evidence']})")
        if not isinstance(e["inferred"], bool):
            out.append(f"INFERRED-FLAG {tag}")
        elif e["inferred"] and not e.get("by"):
            out.append(f"INFERRED-NO-BY {tag}")
        t = (e["from"], e["to"], e["type"])
        if t in triples:
            out.append(f"DUPLICATE-EDGE {tag}")
        triples.add(t)
    return out


def self_test(schema):
    ok = True
    good = json.load(open(os.path.join(FIX, "good.json")))
    f = check(good, schema)
    print(f"good.json: {'PASS' if not f else 'FAIL'} ({len(f)} findings)")
    for x in f: print("   ", x)
    ok &= not f
    for name in sorted(os.listdir(FIX)):
        if not name.startswith("bad-"): continue
        bad = json.load(open(os.path.join(FIX, name)))
        expect = bad.pop("_expect")
        f = check(bad, schema)
        hit = any(x.startswith(expect) for x in f)
        print(f"{name}: {'caught' if hit else 'MISSED'} {expect} ({len(f)} findings)")
        ok &= hit
    print("self-test OK" if ok else "self-test FAILED")
    return ok


def main(argv):
    schema = json.load(open(SCHEMA))
    if argv[1:] == ["--self-test"]:
        return 0 if self_test(schema) else 1
    if len(argv) != 2:
        print(__doc__); return 2
    f = check(json.load(open(argv[1])), schema)
    for x in f: print(x)
    print(f"{len(f)} findings")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
