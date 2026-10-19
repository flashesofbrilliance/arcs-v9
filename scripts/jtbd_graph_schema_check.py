#!/usr/bin/env python3
"""Validate a JTBD graph ({atoms, edges}) against runtime/specs/jtbd-graph-schema.json.

Stdlib only. Usage:
  python3 scripts/jtbd_graph_schema_check.py GRAPH.json   # exit 1 on any finding
  python3 scripts/jtbd_graph_schema_check.py --self-test  # good fixture passes, every bad fixture fails
  python3 scripts/jtbd_graph_schema_check.py --root DIR GRAPH.json  # also look each atom's key up in its real source
  python3 scripts/jtbd_graph_schema_check.py --mutation-proof  # SOURCE-DUP and KEY-LOOKUP disabled in turn: self-test must FAIL
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "runtime/specs/jtbd-graph-schema.json")
FIX = os.path.join(ROOT, "runtime/specs/fixtures/jtbd-graph")


DISABLED = set()  # mutation proof only
MEM_DIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")


def check(graph, schema, root=None):
    out = []
    ns_map = schema["id_scheme"]["namespaces"]
    kinds = schema["kinds"]
    seen, byid, srcseen = set(), {}, {}
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
        ln = src.get("line")
        if not isinstance(ln, int) or isinstance(ln, bool) or ln < 1:
            out.append(f"SOURCE-LINE {aid}: {ln!r} is not a positive int")
        # namespace = first two segments; a key may itself contain ':' (route params like /:slug)
        ns = ":".join(aid.split(":", 2)[:2]) if aid.count(":") >= 2 else None
        if ns not in ns_map or not ns.startswith(kind + ":"):
            out.append(f"UNKNOWN-NAMESPACE {aid}: kind {kind}"); continue
        if not re.fullmatch(ns_map[ns]["pattern"], aid):
            out.append(f"ID-PATTERN {aid}")
        # stability: the id is re-derivable from the source's natural key, nothing else
        if aid != f"{ns}:{src.get('key')}":
            out.append(f"UNSTABLE-ID {aid}: not derived from source key {src.get('key')!r}")
        if src.get("catalog") != ns_map[ns]["source"]:
            out.append(f"SOURCE-MISMATCH {aid}: catalog {src.get('catalog')!r}")
        if aid in seen:
            out.append(f"DUPLICATE-ID {aid}")
        seen.add(aid); byid[aid] = kind
        # SOURCE-DUP (s3): one source unit emitted twice in a namespace, by key or by cited (file, line)
        if "SOURCE-DUP" not in DISABLED:
            # by line only for one-unit-per-line catalogs; prose sources (catalog names with spaces) may declare
            # several units on one line (AGENTS.md "Stack: Anthropic SDK, Supabase ...")
            # (skeptic round 1, class K) the file form ignores `path`, which a forger can vary; a prose source
            # may hold several units on a line, so there the unit is (line, title)
            forms = [("key", src.get("key"))]
            if " " not in str(src.get("catalog")):
                forms.append(("line", src.get("catalog"), src.get("line")))
            else:
                forms.append(("line", src.get("catalog"), a.get("path") or "", src.get("line"), a.get("title") or ""))
            for k in forms:
                t = (ns,) + k
                if t in srcseen:
                    out.append(f"SOURCE-DUP {aid}: {k[0]} already emitted by {srcseen[t]}")
                srcseen.setdefault(t, aid)
        if root is not None and "KEY-LOOKUP" not in DISABLED:
            miss = key_lookup(a, ns, root)
            if miss:
                out.append(f"KEY-LOOKUP {aid}: {miss}")
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
                if not any(fmts[f].fullmatch(str(item)) for f in et["evidence"]):
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


def key_lookup(a, ns, root):
    """Open the cited source line; the atom's natural key must be on it (or name the file). '' when it is."""
    src = a["source"]; cat, key, ln = src.get("catalog"), str(src.get("key")), src.get("line")
    path = a.get("path")
    if cat.startswith("~"):
        if not os.path.isdir(MEM_DIR):
            return ""  # memory lives outside the repo; reconciled on Zach's machine only (pre-registration s1)
        f = os.path.join(MEM_DIR, os.path.basename(path or ""))
    elif " " in cat or "*" in cat:
        f = os.path.join(root, path or "")
    else:
        f = os.path.join(root, cat)
    try:
        L = open(f, encoding="utf-8").read().split("\n")
    except OSError:
        return f"source file {os.path.relpath(f, root)} not found"
    if not isinstance(ln, int) or not 1 <= ln <= len(L):
        return f"line {ln} outside {os.path.relpath(f, root)}"
    line = L[ln - 1]
    if ns == "job:pattern":
        return "" if os.path.basename(path or "") == key + ".md" else f"pattern file {path!r} is not {key}.md"
    if ns == "tool:surface":
        host, _, rest = key.partition("/")
        if f'"host": {json.dumps("*" if host == "any" else host)}' not in line:
            return f"host of {key!r} not on line {ln}"
        # the path must be in the same row: the lines after the host line, up to the next row's host (class M)
        for nxt in L[ln:]:
            if '"host": ' in nxt:
                break
            if f'"path": {json.dumps("/" + rest)}' in nxt:
                return ""
        return f"path of {key!r} not in the row at line {ln}"
    if ns == "tool:op":
        return "" if f'"op": {key},' in line else f"op {key} not on line {ln}"
    if ns == "job:backlog" or ns == "blocker:backlog":
        try:
            return "" if json.loads(line).get("id") == key else f"row id {key!r} not on line {ln}"
        except ValueError:
            return f"line {ln} is not a JSON row"
    if ns == "dep:service":
        # the needle is the hand-declared one for this slug, never free text (class M)
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import jtbd_graph_edges as ge
            needle = ge.SERVICES.get(key, (None,))[0]
        except ImportError:
            needle = None
        if not needle:
            return f"service {key!r} is not declared in jtbd_graph_edges.SERVICES"
        return "" if a.get("title") == needle and needle in line else f"service needle {needle!r} for {key!r} not on line {ln}"
    if ns == "job:memory":
        return "" if re.fullmatch(r"name:\s*['\"]?" + re.escape(key) + r"['\"]?\s*", line) else f"name {key!r} not on line {ln}"
    if ns == "dep:npm":
        return "" if json.dumps(key) + ":" in line else f"package {key!r} not on line {ln}"
    if ns == "dep:env":
        return "" if re.search(r"(?<![A-Za-z0-9_])" + re.escape(key) + r"(?![A-Za-z0-9_])", line) else f"env {key!r} not on line {ln}"
    if ns.startswith("tool:"):  # tool-catalog: the exact JSON name, so a prefix key does not pass (class L)
        return "" if f'"name": {json.dumps(key)}' in line else f'"name": {json.dumps(key)} not on line {ln}'
    return "" if json.dumps(key) in line else f"key {key!r} not on line {ln}"


def self_test(schema, missed=None):
    ok = True
    good = json.load(open(os.path.join(FIX, "good.json")))
    f = check(good, schema)
    print(f"good.json: {'PASS' if not f else 'FAIL'} ({len(f)} findings)")
    for x in f: print("   ", x)
    ok &= not f
    gk = json.load(open(os.path.join(FIX, "good-keylookup.json")))
    f = check(gk, schema, ROOT)
    print(f"good-keylookup.json (with --root): {'PASS' if not f else 'FAIL'} ({len(f)} findings)")
    for x in f: print("   ", x)
    ok &= not f
    for name in sorted(os.listdir(FIX)):
        if not name.startswith("bad-"): continue
        bad = json.load(open(os.path.join(FIX, name)))
        expect = bad.pop("_expect")
        f = check(bad, schema, ROOT if bad.pop("_root", False) else None)
        hit = any(x.startswith(expect) for x in f)
        if missed is not None and not hit:
            missed.add(expect)
        print(f"{name}: {'caught' if hit else 'MISSED'} {expect} ({len(f)} findings)")
        ok &= hit
    print("self-test OK" if ok else "self-test FAILED")
    return ok


def mutation_proof(schema):
    ok = self_test(schema)
    for rule in ("SOURCE-DUP", "KEY-LOOKUP"):
        DISABLED.clear(); DISABLED.add(rule); missed = set()
        survived = self_test(schema, missed)
        good = not survived and rule in missed
        print(f"mutation: {rule} disabled -> self-test {'PASSED' if survived else 'FAILED'}: {'proof ok' if good else 'PROOF FAILS'}")
        ok &= good
    DISABLED.clear()
    print("schema mutation proof OK" if ok else "schema mutation proof FAILED")
    return ok


def main(argv):
    schema = json.load(open(SCHEMA))
    if argv[1:] == ["--self-test"]:
        return 0 if self_test(schema) else 1
    if argv[1:] == ["--mutation-proof"]:
        return 0 if mutation_proof(schema) else 1
    root = None
    if len(argv) == 4 and argv[1] == "--root":
        root, argv = argv[2], [argv[0], argv[3]]
    if len(argv) != 2:
        print(__doc__); return 2
    f = check(json.load(open(argv[1])), schema, root)
    for x in f: print(x)
    print(f"{len(f)} findings")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
