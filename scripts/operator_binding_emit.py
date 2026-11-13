#!/usr/bin/env python3
"""operator_binding_emit.py: the seat binding map. Every operator, Python operator file and agent ("seat"),
bound to the jobs, tools, surfaces and ROM primitives it is grep-verified to touch. Stdlib only, no model calls.

Why (Zach, 2026-11-13): "hire all our current python advisors operators and staff of chiefs and wire them to the
right mechanical process and primitives ... to the current known surfaces and jobs to be done and backlogs".
Before anything is wired, this says what each seat is already wired to, by evidence, and marks the rest UNBOUND.
Never hand-write a binding (gotcha 16): every edge carries the file and line where its needle was found.

Roster (enumerated, never typed):
  operators/OPERATOR-REGISTRY.json operators[]       -> tool:op:<n>            (numbering = PERIODIC-TABLE.md)
  runtime/specs/tool-catalog.json  kind == operator   -> tool:operator:<file>   (Python operators under operators/)
  runtime/specs/tool-catalog.json  kind == agent      -> tool:agent:<name>      (chiefs, I.D.E.A. seats, reviewers)
Targets (ids match the JTBD graph namespaces, ADR-089, so the map joins _STATE/jtbd-graph/graph.json):
  _QUEUE/induced-backlog.jsonl     row text names the seat          -> job:backlog:<id>      (mentioned_by_row)
  runtime/specs/tool-catalog.json  a tool's file names the seat     -> tool:<kind>:<name>    (cited_by_tool)
                                   the seat's file names a tool path -> tool:<kind>:<name>   (cites_tool)
  runtime/specs/surface-catalog.json a routed file names the seat   -> tool:surface:<host><path> (serves_surface)
  ROM primitives (CLAUDE.md)       the seat's own file names one    -> rom:<primitive>       (invokes_primitive)
Seat status: BOUND when it has at least one job, tool or surface edge; else UNBOUND with the reason.
`reads_backlog` is true only when the seat's own file opens the backlog file: a mention is not a row adapter.

Also checks runtime/specs/design-review-seats.json: every seat named per design-loop stage is on the roster.

usage:
  operator_binding_emit.py            write runtime/specs/operator-binding-map.json
  operator_binding_emit.py --check    verify every committed edge's evidence still holds, every roster seat is in
                                      the map, and the design-review seats exist; exit 1 on any failure
  operator_binding_emit.py --self-test  a planted fake binding must fail --check; the real map must pass
"""
import json, os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "runtime/specs/operator-binding-map.json"
DESIGN = "runtime/specs/design-review-seats.json"
BACKLOG = "_QUEUE/induced-backlog.jsonl"
ROM = {
    "notomation": r"\bnotomation\b",
    "hypersphere-context-manifold": r"\bhypersphere\b",
    "hyperstition-pipeline": r"\bhyperstition\b",
    "golden-inchworm": r"\binchworm\b",
    "orthogonal-echo-detector": r"\borthogonal[ _-]echo\b",
    "kintsugi-immune-system": r"\bkintsugi\b",
    "write-lock": r"\bwrite[ _-]lock\b",
}
STOP_AGENT_NAMES = {"claude"}  # the catch-all agent's bare name matches everything


def rd(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def roster():
    reg = json.loads(rd("operators/OPERATOR-REGISTRY.json"))
    cat = json.loads(rd("runtime/specs/tool-catalog.json"))["tools"]
    seats = []
    for o in reg["operators"]:
        mod = (o.get("binding") or {}).get("module")
        path = "operators/" + mod if mod else None
        needles = [r"\b[Oo]p(?:erator)?[ -]?%d\b" % o["op"], r"\b%s\b" % re.escape(o["name"])]
        if mod:
            needles.append(re.escape(os.path.basename(mod)))
        seats.append({"id": "tool:op:%d" % o["op"], "kind": "registry-operator", "name": o["name"],
                      "registry_status": o["status"], "path": path, "needles": needles})
    for t in cat:
        if t["kind"] == "operator":
            seats.append({"id": "tool:operator:" + t["name"], "kind": "python-operator", "name": t["name"],
                          "path": t["path"], "needles": [re.escape(t["name"])]})
        elif t["kind"] == "agent":
            n = t["name"]
            needles = [r"subagent_type=%s\b" % re.escape(n), re.escape("agents/%s.md" % n)]
            if n not in STOP_AGENT_NAMES:
                needles.append(r"(?<![\w/-])%s(?![\w-])" % re.escape(n))
            seats.append({"id": "tool:agent:" + n, "kind": "agent", "name": n, "path": t["path"],
                          "needles": needles})
    return sorted(seats, key=lambda s: s["id"]), cat


def first_hit(text, pats):
    for p in pats:
        m = re.search(p, text)
        if m:
            return p, text.count("\n", 0, m.start()) + 1
    return None, None


def build():
    seats, cat = roster()
    rows = []
    for i, line in enumerate((rd(BACKLOG) or "").splitlines(), 1):
        if line.strip():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            rows.append((i, r.get("id"), r.get("state"), line))
    tools = [(t, rd(t["path"]) or "") for t in cat]
    surf = json.loads(rd("runtime/specs/surface-catalog.json"))["rows"]
    files = {}
    surf_rows = []
    for s in surf:
        f = s.get("file")
        if f and f not in files:
            files[f] = rd(f) or ""
        surf_rows.append(("tool:surface:%s%s" % (s["host"], s["path"]), f))
    tool_paths = [(t["path"], "tool:%s:%s" % (t["kind"], t["name"])) for t in cat]
    out = []
    for s in seats:
        edges = []
        own = rd(s["path"]) if s["path"] else None
        own_rel = s["path"]
        for ln, rid, state, text in rows:
            p, _ = first_hit(text, s["needles"])
            if p:
                edges.append({"target": "job:backlog:" + rid, "kind": "mentioned_by_row", "row_state": state,
                              "evidence": {"file": BACKLOG, "line": ln, "row_id": rid, "needle": p}})
        for t, text in tools:
            if t["path"] == own_rel:
                continue
            p, ln = first_hit(text, s["needles"])
            if p:
                edges.append({"target": "tool:%s:%s" % (t["kind"], t["name"]), "kind": "cited_by_tool",
                              "evidence": {"file": t["path"], "line": ln, "needle": p}})
        for sid, f in surf_rows:
            if f and f != own_rel:
                p, ln = first_hit(files.get(f, ""), s["needles"])
                if p:
                    edges.append({"target": sid, "kind": "serves_surface",
                                  "evidence": {"file": f, "line": ln, "needle": p}})
        if own:
            for path, tid in tool_paths:
                if path != own_rel and path in own:
                    pat = re.escape(path)
                    _, ln = first_hit(own, [pat])
                    edges.append({"target": tid, "kind": "cites_tool",
                                  "evidence": {"file": own_rel, "line": ln, "needle": pat}})
            for prim, pat in sorted(ROM.items()):
                m = re.search(pat, own, re.I)
                if m:
                    edges.append({"target": "rom:" + prim, "kind": "invokes_primitive",
                                  "evidence": {"file": own_rel, "line": own.count("\n", 0, m.start()) + 1,
                                               "needle": "(?i)" + pat}})
        # one edge per (target, kind); deterministic order
        seen, uniq = set(), []
        for e in sorted(edges, key=lambda e: (e["kind"], e["target"])):
            k = (e["kind"], e["target"])
            if k not in seen:
                seen.add(k)
                uniq.append(e)
        working = [e for e in uniq if e["kind"] != "invokes_primitive"]
        if s["kind"] == "registry-operator" and not s["path"]:
            status, why = "UNBOUND", "registry status %s: no module to bind" % s["registry_status"]
        elif not working:
            status, why = "UNBOUND", "no backlog row, tool or surface names it"
        else:
            status, why = "BOUND", None
        active = sum(1 for e in uniq if e["kind"] == "mentioned_by_row"
                     and e["row_state"] not in ("DONE", "COMPOSTED", "SUPERSEDED"))
        rec = {"id": s["id"], "kind": s["kind"], "name": s["name"], "path": s["path"], "status": status,
               "reads_backlog": bool(own and "induced-backlog" in own and "open(" in own),
               "counts": {k: sum(1 for e in uniq if e["kind"] == k) for k in
                          ("mentioned_by_row", "cited_by_tool", "cites_tool", "serves_surface", "invokes_primitive")},
               "active_rows": active, "edges": uniq}
        if s["kind"] == "registry-operator":
            rec["registry_status"] = s["registry_status"]
        if why:
            rec["unbound_reason"] = why
        out.append(rec)
    by = lambda st: sum(1 for r in out if r["status"] == st)
    return {"$schema": "operator-binding-map v1", "generator": "scripts/operator_binding_emit.py",
            "rule": "grep-verified edges only; every edge cites file, line and needle; UNBOUND when none",
            "roster_sources": ["operators/OPERATOR-REGISTRY.json", "runtime/specs/tool-catalog.json"],
            "counts": {"seats": len(out), "BOUND": by("BOUND"), "UNBOUND": by("UNBOUND"),
                       "reads_backlog": sum(1 for r in out if r["reads_backlog"]),
                       "edges": sum(len(r["edges"]) for r in out)},
            "seats": out}


def check(m, root_seats=None):
    errs = []
    rows = {}
    for line in (rd(BACKLOG) or "").splitlines():
        try:
            r = json.loads(line)
            rows[r.get("id")] = line
        except ValueError:
            pass
    cache = {}
    for s in m["seats"]:
        for e in s["edges"]:
            ev = e["evidence"]
            if ev["file"] == BACKLOG:
                text = rows.get(ev.get("row_id"))
                where = "row %s" % ev.get("row_id")
            else:
                if ev["file"] not in cache:
                    cache[ev["file"]] = rd(ev["file"])
                text, where = cache[ev["file"]], ev["file"]
            if text is None:
                errs.append("%s -> %s: evidence %s is gone" % (s["id"], e["target"], where))
            elif not re.search(ev["needle"], text):
                errs.append("%s -> %s: needle %r not found in %s" % (s["id"], e["target"], ev["needle"], where))
    seats = root_seats if root_seats is not None else [x["id"] for x in roster()[0]]
    have = {s["id"] for s in m["seats"]}
    for sid in seats:
        if sid not in have:
            errs.append("roster seat %s missing from the map: regenerate" % sid)
    d = rd(DESIGN)
    if d:
        for st in json.loads(d)["stages"]:
            for seat in st["seats"]:
                if seat not in have:
                    errs.append("design stage %s names seat %s, not on the roster" % (st["stage"], seat))
    return errs


def self_test():
    m = build()
    bad = json.loads(json.dumps(m))
    loki = next(s for s in bad["seats"] if s["id"] == "tool:agent:chief-loki")
    some_row = next(r for r in (json.loads(l) for l in rd(BACKLOG).splitlines() if l.strip())
                    if "chief-loki" not in json.dumps(r))
    loki["edges"].append({"target": "job:backlog:" + some_row["id"], "kind": "mentioned_by_row",
                          "evidence": {"file": BACKLOG, "line": 1, "row_id": some_row["id"],
                                       "needle": loki["edges"][0]["evidence"]["needle"] if loki["edges"] else "chief-loki"}})
    missing = json.loads(json.dumps(m))
    missing["seats"] = missing["seats"][1:]
    ok = not check(m)
    fake_caught = bool(check(bad))
    missing_caught = bool(check(missing))
    print("good map passes:", ok, "| planted fake binding caught:", fake_caught,
          "| dropped seat caught:", missing_caught)
    return 0 if ok and fake_caught and missing_caught else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        text = rd(OUT)
        if text is None:
            print("✖ %s missing: run python3 scripts/operator_binding_emit.py" % OUT)
            return 1
        errs = check(json.loads(text))
        for e in errs[:40]:
            print("✖", e)
        if errs:
            print("✖ %d binding-map failure(s); regenerate with python3 scripts/operator_binding_emit.py" % len(errs))
            return 1
        print("✓ binding map: every edge's evidence holds, every roster seat present, design seats exist")
        return 0
    m = build()
    body = json.dumps(m, indent=1, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=os.path.join(ROOT, "runtime/specs"))
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, os.path.join(ROOT, OUT))
    c = m["counts"]
    print("wrote %s: %d seats, %d BOUND, %d UNBOUND, %d read the backlog, %d edges"
          % (OUT, c["seats"], c["BOUND"], c["UNBOUND"], c["reads_backlog"], c["edges"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
