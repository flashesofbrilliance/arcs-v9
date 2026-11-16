#!/usr/bin/env python3
"""universe_jtbd_adapter: emit the JTBD graph's nodes (Sprint 1, backlog row jtbd-graph-s1-nodes).

Atoms conform to runtime/specs/jtbd-graph-schema.json v1 (ADR-089). Every atom cites its source line
(source.catalog, source.key, source.line). Nodes only: the one edge family emitted here is the
operator link the s1 gate requires (tool:operator:<file> -design-dep-> tool:op:<n>, evidence the
registry binding line). All other edges are Sprint 2.

Sources and namespaces:
  runtime/specs/tool-catalog.json   tools[]        -> tool:<kind>:<name>
  operators/OPERATOR-REGISTRY.json  operators[]    -> tool:op:<n>
  runtime/specs/surface-catalog.json rows[]        -> tool:surface:<host><path>
  package.json  dependencies + devDependencies     -> dep:npm:<name>
  _QUEUE/induced-backlog.jsonl  every row          -> job:backlog:<id>; BLOCKED rows also blocker:backlog:<id>
  runtime/specs/mcp-tool-index.json tools[]        -> tool:mcp:<server>.<tool> (amendment 8; cached index, no schemas)
    + serves edges only from runtime/specs/mcp-tool-receipts.jsonl (a receipt naming tool_id and job_id)
  mined (default since s4; the miner gate passed 27/30, runtime/specs/jtbd-label-sample-20261018-labels.json):
  memory front-matter + _PATTERNS stems, by the rule in
  _PATTERNS/2026-10-18-jtbd-s1-mined-job-rule.md     -> job:memory:<name>, job:pattern:<stem>

A duplicate natural key inside one source raises SOURCE-DUP and nothing is written (schema rule).
Output is generated and gitignored (receipts-adapter precedent): _STATE/jtbd-graph/graph.json.

  python3 scripts/universe_jtbd_adapter.py              # build, reconcile, verify lines, schema-check
  python3 scripts/universe_jtbd_adapter.py --no-mined   # skip mined jobs (--mined is accepted and is the default)
  python3 scripts/universe_jtbd_adapter.py --self-test  # good fixture passes, bad fixtures fail
  python3 scripts/universe_jtbd_adapter.py --check      # s3 gate: build in memory, run every s1/s2 check, the schema
                                                        # checker with --root key lookup, and the six rules in
                                                        # scripts/jtbd_graph_gates.py against the baseline; exit 1 on
                                                        # any new finding, stale baseline id or grown baseline
  python3 scripts/universe_jtbd_adapter.py --pulse      # one counts line from the last --check (no rebuild; session start)
Stdlib only.
"""
import collections, json, os, random, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import jtbd_graph_schema_check as gc
import jtbd_graph_edges as ge
import jtbd_graph_gates as gg

TOOLS = "runtime/specs/tool-catalog.json"
REG = "operators/OPERATOR-REGISTRY.json"
SURF = "runtime/specs/surface-catalog.json"
PKG = "package.json"
BACKLOG = "_QUEUE/induced-backlog.jsonl"
MCP_INDEX = "runtime/specs/mcp-tool-index.json"
MEM_CAT = "~/.claude/projects/-Users-zharris-arcs-v9/memory/*.md"
PAT_CAT = "_PATTERNS/*.md"
MEM_DIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
OUT = "_STATE/jtbd-graph"
JOB_RE = re.compile(r"jtbd|jobs? to be done|jobs?-to-be-done", re.I)
# Amendment 4 (_PATTERNS/2026-10-19-jtbd-graph-preregistration-amendment-4.md): exclude by pattern.
PAT_EXCLUDE_RE = re.compile(r"-preregistration|^2026-10-18-jtbd-s1-mined-job-rule$")
SAMPLE_FROZEN = "runtime/specs/jtbd-label-sample-20261018.json"
SEED = 20261018
SURF_HOST_RE = re.compile(r"^[a-z0-9.-]+$")


class SourceDup(Exception):
    pass


def _lines(root, rel):
    return open(os.path.join(root, rel), encoding="utf-8").read().split("\n")


def _seek(lines, start, needle, what):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i
    raise ValueError(f"line not found for {what}: {needle!r}")


def _dups(keys, src):
    d = [k for k, n in collections.Counter(keys).items() if n > 1]
    if d:
        raise SourceDup(f"SOURCE-DUP {src}: {sorted(d)}")


def atom(aid, kind, catalog, key, line, **extra):
    a = {"id": aid, "kind": kind, "source": {"catalog": catalog, "key": key, "line": line}}
    a.update({k: v for k, v in extra.items() if v is not None})
    return a


def tools(root):
    d = json.load(open(os.path.join(root, TOOLS))); L = _lines(root, TOOLS)
    _dups([(t["kind"], t["name"]) for t in d["tools"]], TOOLS)
    cur = _seek(L, 0, '"tools": [', "tools[]"); out = []
    for t in d["tools"]:
        cur = _seek(L, cur + 1, f'"name": {json.dumps(t["name"])}', t["name"])
        out.append(atom(f"tool:{t['kind']}:{t['name']}", "tool", TOOLS, t["name"], cur + 1,
                        title=t.get("jtbd"), path=t.get("path"), state=t.get("state")))
    return out, d


def operators(root):
    d = json.load(open(os.path.join(root, REG))); L = _lines(root, REG)
    _dups([o["op"] for o in d["operators"]], REG)
    cur = _seek(L, 0, '"operators": [', "operators[]"); out, binds = [], []
    for o in d["operators"]:
        cur = _seek(L, cur + 1, f'"op": {o["op"]},', f"op {o['op']}")
        out.append(atom(f"tool:op:{o['op']}", "tool", REG, str(o["op"]), cur + 1,
                        title=f"{o.get('name')} ({o.get('symbol')})", state=o.get("status")))
        mod = (o.get("binding") or {}).get("module")
        if mod:
            ml = _seek(L, cur + 1, f'"module": {json.dumps(mod)}', f"op {o['op']} module")
            binds.append((o["op"], mod, ml + 1))
    return out, binds


def surfaces(root):
    d = json.load(open(os.path.join(root, SURF))); L = _lines(root, SURF)
    _dups([(r["host"], r["path"]) for r in d["rows"]], SURF)
    cur = _seek(L, 0, '"rows": [', "rows[]"); out, unresolved = [], []
    for r in d["rows"]:
        cur = _seek(L, cur + 1, f'"host": {json.dumps(r["host"])}', r["host"])
        host = "any" if r["host"] == "*" else r["host"]  # wildcard host -> "any" (Zach, 2026-10-18, ADR-089 amendment 1)
        key = host + r["path"]
        if not SURF_HOST_RE.match(host):
            # host '*' (catch-all) fails the write-locked id pattern; held for Zach's id decision, counted not dropped
            unresolved.append({"namespace": "tool:surface", "key": key, "source": {"catalog": SURF, "line": cur + 1},
                               "why": "host fails tool:surface id pattern (write-locked, ADR-089)"})
            continue
        out.append(atom(f"tool:surface:{key}", "tool", SURF, key, cur + 1,
                        title=r.get("purpose") or r.get("title"), path=r.get("file")))
    return out, d, unresolved


def npm(root):
    d = json.load(open(os.path.join(root, PKG))); L = _lines(root, PKG); out = []
    names = list(d.get("dependencies", {})) + list(d.get("devDependencies", {}))
    _dups(names, PKG)
    for block in ("dependencies", "devDependencies"):
        cur = _seek(L, 0, f'"{block}": {{', block)
        for n in d.get(block, {}):
            ln = _seek(L, cur + 1, f'{json.dumps(n)}:', n)
            out.append(atom(f"dep:npm:{n}", "dep", PKG, n, ln + 1, title=f"{block} {d[block][n]}"))
    return out, len(names)


def mcp_tools(root):
    """Amendment 8: one atom per index row. An absent index emits nothing (the namespace is optional)."""
    p = os.path.join(root, MCP_INDEX)
    if not os.path.exists(p):
        return [], 0, None
    d = json.load(open(p, encoding="utf-8")); L = _lines(root, MCP_INDEX)
    _dups([r["name"] for r in d["tools"]], MCP_INDEX)
    cur = _seek(L, 0, '"tools": [', "tools[]"); out = []
    for r in d["tools"]:
        cur = _seek(L, cur + 1, f'"name": {json.dumps(r["name"])}', r["name"])
        out.append(atom(f"tool:mcp:{r['name']}", "tool", MCP_INDEX, r["name"], cur + 1,
                        title=r.get("purpose"), cls=r.get("class"), fn=r.get("fn")))
    return out, len(d["tools"]), d.get("captured_at")


def mcp_edges(root, atoms):
    """Amendment 8 rule (d): a serves edge only where a receipt names both the MCP tool and the backlog job.
    Never from names or purpose text. Evidence: the projection line, then receipt:<id>."""
    ids = {a["id"] for a in atoms}; out = []
    for n, line in enumerate(_lines(root, ge.MCP_RECEIPTS) if os.path.exists(os.path.join(root, ge.MCP_RECEIPTS)) else [], 1):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        t, j = r.get("tool_id"), r.get("job_id")
        if not (isinstance(t, str) and t.startswith("tool:mcp:") and t in ids and isinstance(j, str)
                and j.startswith("job:") and j in ids and r.get("receipt_id")):
            continue
        out.append({"from": t, "to": j, "type": "serves",
                    "evidence": [f"{ge.MCP_RECEIPTS}:{n}", f"receipt:{r['receipt_id']}"], "inferred": False,
                    "rule": "mcp-receipt", "match": t.split(":", 2)[2]})
    return out


def backlog(root):
    rows = [(i + 1, json.loads(l)) for i, l in enumerate(_lines(root, BACKLOG)) if l.strip()]
    _dups([r["id"] for _, r in rows], BACKLOG)
    jobs, blockers = [], []
    for ln, r in rows:
        jobs.append(atom(f"job:backlog:{r['id']}", "job", BACKLOG, r["id"], ln, title=r.get("jtbd"), state=r.get("state")))
        if r.get("state") == "BLOCKED":
            blockers.append(atom(f"blocker:backlog:{r['id']}", "blocker", BACKLOG, r["id"], ln,
                                 title=r.get("status_note"), state="BLOCKED", resolve_by=r.get("resolve_by")))
    return jobs, blockers, rows


def _frontmatter_name(lines):
    if not lines or lines[0].strip() != "---":
        return None, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return None, None
        m = re.match(r"^name:\s*(.+?)\s*$", lines[i])
        if m:
            return m.group(1).strip("'\""), i + 1
    return None, None


def mined(root, mem_dir):
    jobs, skipped = [], []
    if mem_dir and os.path.isdir(mem_dir):
        names = []
        for f in sorted(os.listdir(mem_dir)):
            if not f.endswith(".md") or f == "MEMORY.md":
                continue
            L = open(os.path.join(mem_dir, f), encoding="utf-8").read().split("\n")
            if not JOB_RE.search("\n".join(L)):
                continue
            name, ln = _frontmatter_name(L)
            if not name:
                skipped.append(f); continue
            names.append(name)
            jobs.append(atom(f"job:memory:{name}", "job", MEM_CAT, name, ln, path=f"memory/{f}"))
        _dups(names, MEM_CAT)
    pdir = os.path.join(root, "_PATTERNS")
    for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        stem = f[:-3]
        if not f.endswith(".md") or PAT_EXCLUDE_RE.search(stem):
            continue
        L = _lines(root, f"_PATTERNS/{f}")
        hit = next((i for i, l in enumerate(L) if JOB_RE.search(l)), None)
        if hit is not None:
            jobs.append(atom(f"job:pattern:{stem}", "job", PAT_CAT, stem, hit + 1, path=f"_PATTERNS/{f}"))
    return jobs, skipped


def build(root, with_mined=False, mem_dir=MEM_DIR):
    t, tcat = tools(root); o, binds = operators(root); s, scat, unres = surfaces(root)
    n, npm_n = npm(root); j, b, rows = backlog(root)
    ev = ge.env_and_service_atoms(root, atom, _dups)
    mc, mcp_n, _ = mcp_tools(root)
    atoms = t + o + s + n + j + b + ev + mc
    file_of = {a["path"]: a["id"] for a in t if a["id"].startswith("tool:operator:")}
    edges = []
    for op, mod, ln in binds:
        fid = file_of.get(f"operators/{mod}")
        if fid:
            edges.append({"from": fid, "to": f"tool:op:{op}", "type": "design-dep",
                          "evidence": [f"{REG}:{ln}"], "inferred": False,
                          "rule": "operator-bind", "match": json.dumps(mod)})
    expected = {f"tool:{k}": v for k, v in tcat["counts"].items()}
    expected.update({"dep:env": sum(1 for a in ev if a["id"].startswith("dep:env:")),
                     "dep:service": len(ge.SERVICES)})
    expected.update({"tool:op": len(json.load(open(os.path.join(root, REG)))["operators"]),
                     "tool:surface": scat["counts"]["rows"], "dep:npm": npm_n, "job:backlog": len(rows),
                     "blocker:backlog": sum(1 for _, r in rows if r.get("state") == "BLOCKED")})
    if mcp_n:
        expected["tool:mcp"] = mcp_n
    skipped = []
    if with_mined:
        m, skipped = mined(root, mem_dir); atoms += m
    edges = ge.build_edges(root, atoms, rows, edges)
    edges += mcp_edges(root, atoms)
    unres += [{"namespace": "job:memory", "key": f, "source": {"catalog": MEM_CAT, "line": None},
               "why": "matches the mined-job rule but has no top-of-file front-matter name"} for f in skipped]
    return {"atoms": atoms, "edges": edges, "unresolved": unres}, expected, binds, skipped


def reconcile(graph, expected):
    got = collections.Counter(":".join(a["id"].split(":", 2)[:2]) for a in graph["atoms"])
    got.update(u["namespace"] for u in graph.get("unresolved", []) if u["namespace"] in expected)
    rows = [(ns, expected.get(ns), got.get(ns, 0)) for ns in sorted(set(expected) | set(got))]
    bad = [r for r in rows if r[1] is not None and r[1] != r[2]]
    return rows, bad


def verify_lines(graph, root, mem_dir=MEM_DIR):
    """Open every cited line; the natural key (or its JSON form) must appear on it."""
    bad, cache = [], {}
    for a in graph["atoms"]:
        src = a["source"]; cat = src["catalog"]
        path = os.path.join(mem_dir, os.path.basename(a["path"])) if cat == MEM_CAT else \
            os.path.join(root, a["path"]) if cat in (PAT_CAT, ge.ENV_CAT, ge.SVC_CAT) else os.path.join(root, cat)
        if path not in cache:
            cache[path] = open(path, encoding="utf-8").read().split("\n")
        L = cache[path]; ln = src["line"]
        line = L[ln - 1] if 0 < ln <= len(L) else ""
        key = src["key"]
        if a["id"].startswith("tool:surface:"):
            h = json.loads(line.split('"host": ', 1)[1].rstrip(',')) if '"host": ' in line else None
            ok = h is not None and key.startswith("any" if h == "*" else h)
        elif cat == PAT_CAT:
            ok = bool(JOB_RE.search(line))
        elif cat == BACKLOG:
            try:
                ok = json.loads(line).get("id") == key
            except ValueError:
                ok = False
        elif cat == ge.ENV_CAT:
            ok = f"`{key}`" in line or f"process.env.{key}" in line
        elif cat == ge.SVC_CAT:
            ok = a.get("title", "\0") in line
        elif cat == REG:
            ok = f'"op": {key},' in line
        else:
            ok = json.dumps(key) in line or f"name: {key}" in line
        if not ok:
            bad.append((a["id"], f"{cat}:{ln}", line.strip()[:80]))
    return bad


def operator_links(graph, binds):
    """s1 gate: each (bound file atom, op) pair has exactly one design-dep edge."""
    files = {a["path"]: a["id"] for a in graph["atoms"] if a["id"].startswith("tool:operator:")}
    cnt = collections.Counter((e["from"], e["to"]) for e in graph["edges"] if e["type"] == "design-dep")
    bad = []
    for op, mod, _ in binds:
        fid = files.get(f"operators/{mod}")
        if fid and cnt[(fid, f"tool:op:{op}")] != 1:
            bad.append((fid, op, cnt[(fid, f"tool:op:{op}")]))
    return bad


def label_sample(graph, root=REPO):
    fz = os.path.join(root, SAMPLE_FROZEN)
    if os.path.exists(fz):  # frozen as drawn (amendment 4); independent of later miner changes
        return json.load(open(fz))["ids"]
    ids = sorted(a["id"] for a in graph["atoms"] if a["id"].startswith(("job:memory:", "job:pattern:")))
    return random.Random(SEED).sample(ids, min(30, len(ids)))


def run(root, with_mined, mem_dir, out_dir, quiet=False):
    graph, expected, binds, skipped = build(root, with_mined, mem_dir)
    rows, bad_counts = reconcile(graph, expected)
    bad_lines = verify_lines(graph, root, mem_dir)
    bad_links = operator_links(graph, binds)
    rows_ = backlog(root)[2]
    bad_edges = ge.verify_edges(graph, root, rows_)
    E = graph["edges"]; mech = sum(1 for e in E if not e["inferred"])
    share = mech / len(E) if E else 1.0
    cyc = ge.cycles(graph); graph["cycles"] = cyc
    findings = gc.check(graph, json.load(open(os.path.join(REPO, "runtime/specs/jtbd-graph-schema.json"))))
    if not quiet:
        print("namespace            expected  emitted")
        for ns, e, g in rows:
            print(f"  {ns:18} {str(e if e is not None else '(mined)'):>8} {g:>8}")
        for u in graph["unresolved"]:
            print(f"  UNRESOLVED {u['namespace']} {u['key']} ({u['why']})")
        print(f"emitted counts include {len(graph['unresolved'])} unresolved (held, not atoms)")
        print(f"atoms {len(graph['atoms'])} · edges {len(E)}")
        for (t, r), c in sorted(collections.Counter((e["type"], e.get("rule")) for e in E).items()):
            print(f"  {t:12} {r:18} {c:>5}")
        print(f"mechanical share: {mech}/{len(E)} = {share:.4f} (gate >= 0.90) {'PASS' if share >= 0.90 else 'FAIL'}")
        print(f"inferred edges: {len(E) - mech}, all flagged with by: {all(e.get('by') for e in E if e['inferred'])}")
        print(f"edge evidence: {len(E) - len(bad_edges)}/{len(E)} resolve" + (f" BAD {bad_edges[:5]}" if bad_edges else ""))
        for t, cs in cyc.items():
            print(f"cycles {t}: {len(cs)}" + "".join(f"\n    {' <-> '.join(c)}" for c in cs))
        print(f"reconcile: {'EXACT' if not bad_counts else bad_counts}")
        print(f"cited lines: {len(graph['atoms']) - len(bad_lines)}/{len(graph['atoms'])} resolve" + (f" BAD {bad_lines[:5]}" if bad_lines else ""))
        print(f"operator links: {'OK' if not bad_links else bad_links}")
        print(f"schema check: {len(findings)} findings" + (f" {findings[:5]}" if findings else ""))
        if skipped:
            print(f"memory files matching the rule but lacking front-matter name (not emitted): {skipped}")
    ok = not (bad_counts or bad_lines or bad_links or findings or bad_edges or share < 0.90)
    if out_dir and ok:
        os.makedirs(out_dir, exist_ok=True)
        json.dump(graph, open(os.path.join(out_dir, "graph.json"), "w"), indent=1, ensure_ascii=False)
        if with_mined:
            json.dump({"seed": SEED, "rule": "_PATTERNS/2026-10-18-jtbd-s1-mined-job-rule.md",
                       "sample": [{"id": i, "label": None} for i in label_sample(graph, root)]},
                      open(os.path.join(out_dir, "label-sample.json"), "w"), indent=1)
        if not quiet:
            print(f"wrote {out_dir}/graph.json")
    return ok, graph


def _fixture(tmp, dup=False):
    os.makedirs(os.path.join(tmp, "runtime/specs")); os.makedirs(os.path.join(tmp, "operators"))
    os.makedirs(os.path.join(tmp, "_QUEUE")); os.makedirs(os.path.join(tmp, "_PATTERNS"))
    tl = [{"kind": "script", "name": "a.py", "path": "scripts/a.py"},
          {"kind": "operator", "name": "op_x.py", "path": "operators/op_x.py"}]
    if dup:
        tl.append({"kind": "script", "name": "a.py", "path": "scripts/a.py"})
    json.dump({"counts": {"script": 1, "operator": 1}, "tools": tl}, open(os.path.join(tmp, TOOLS), "w"), indent=2)
    json.dump({"operators": [{"op": 1, "name": "X", "symbol": "X", "binding": {"module": "op_x.py"}}]},
              open(os.path.join(tmp, REG), "w"), indent=2)
    json.dump({"counts": {"rows": 2}, "rows": [{"host": "a.arcs.care", "path": "/"}, {"host": "*", "path": "/x"}]},
              open(os.path.join(tmp, SURF), "w"), indent=2)
    json.dump({"dependencies": {"next": "1"}, "devDependencies": {"@types/node": "1"}}, open(os.path.join(tmp, PKG), "w"), indent=2)
    open(os.path.join(tmp, BACKLOG), "w").write(json.dumps({"id": "row-a", "state": "OPEN", "route": {"tool": "scripts/a.py"}, "depends_on": ["row-b"], "jtbd": "needs ANTHROPIC_API_KEY"}) + "\n" +
                                                 json.dumps({"id": "row-b", "state": "BLOCKED"}) + "\n")
    os.makedirs(os.path.join(tmp, "scripts")); os.makedirs(os.path.join(tmp, "src/lib"))
    open(os.path.join(tmp, "scripts/a.py"), "w").write('# emits operators/op_x.py\nimport anthropic\nimport op_x\nimport os\nU = os.environ["DATABASE_URL"]\nsubprocess.run(["gh", "pr", "list"])\ntry:\n    subprocess.run(["vercel", "ls"])\nexcept OSError:\n    pass\n')
    open(os.path.join(tmp, "operators/op_x.py"), "w").write('# see scripts/a.py\nsubprocess.run(["python3", "scripts/a.py"])\nraise SystemExit("run: python3 scripts/a.py")\nprint("fix:", ["python3", "scripts/a.py"])\n')
    open(os.path.join(tmp, "AGENTS.md"), "w").write("Stack: Anthropic SDK, Supabase (prod), Magic link emails via Resend, Vercel `get_deployment`\n"
        "gh pr merge --merge\n| Perplexity MCP | x |\n## Environment variables\n| `ANTHROPIC_API_KEY` | k |\n| `DATABASE_URL` | d |\n## Next\n")
    open(os.path.join(tmp, "src/lib/env.ts"), "w").write("export const e = process.env.EMAIL_FROM\n")
    open(os.path.join(tmp, "_PATTERNS/p1.md"), "w").write("# P1\nthe JTBD here\n")
    open(os.path.join(tmp, "_PATTERNS/p2.md"), "w").write("# P2\nno job stated\n")
    open(os.path.join(tmp, "_PATTERNS/x-preregistration-amendment-9.md"), "w").write("# A\nthe JTBD here\n")
    mem = os.path.join(tmp, "mem"); os.makedirs(mem)
    open(os.path.join(mem, "m1.md"), "w").write("---\nname: m-one\n---\njob to be done: x\n")
    open(os.path.join(mem, "m2.md"), "w").write("---\nname: m-two\n---\nnothing\n")
    # m3 cites the same line number as m1 in another file: must not read as SOURCE-DUP (s4 glob-catalog fix)
    open(os.path.join(mem, "m3.md"), "w").write("---\nname: m-three\n---\njtbd: y\n")
    return mem


def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        mem = _fixture(tmp)
        good, g = run(tmp, True, mem, None, quiet=True)
        ids = sorted(a["id"] for a in g["atoms"])
        want = ["blocker:backlog:row-b", "dep:env:ANTHROPIC_API_KEY", "dep:env:DATABASE_URL", "dep:env:EMAIL_FROM",
                "dep:npm:@types/node", "dep:npm:next"] + [f"dep:service:{x}" for x in sorted(ge.SERVICES)] + [ "job:backlog:row-a", "job:backlog:row-b",
                "job:memory:m-one", "job:memory:m-three", "job:pattern:p1", "tool:op:1", "tool:operator:op_x.py", "tool:script:a.py",
                "tool:surface:a.arcs.care/", "tool:surface:any/x"]
        good = good and ids == sorted(want) and sum(e["rule"] == "operator-bind" for e in g["edges"]) == 1 and [u["key"] for u in g["unresolved"]] == []
        print(f"good fixture: {'PASS' if good else 'FAIL'} ({len(ids)} atoms, {len(g['edges'])} edges)")
        ok &= good
        leak = [i for i in ids if "preregistration" in i]
        print(f"amendment exclusion (x-preregistration-amendment-9 not mined): {'PASS' if not leak else 'FAIL ' + str(leak)}")
        ok &= not leak
        g["atoms"][0]["source"]["line"] += 1
        caught = bool(verify_lines(g, tmp, mem))
        print(f"bad fixture (shifted cite line): {'caught' if caught else 'MISSED'}")
        ok &= caught
        g["edges"].append(dict(g["edges"][0]))
        binds = [(1, "op_x.py", 1)]
        caught = bool(operator_links(g, binds))
        print(f"bad fixture (second operator link): {'caught' if caught else 'MISSED'}")
        ok &= caught
    with tempfile.TemporaryDirectory() as tmp:
        mem = _fixture(tmp, dup=True)
        try:
            run(tmp, False, mem, None, quiet=True); caught = False
        except SourceDup:
            caught = True
        print(f"bad fixture (duplicate tool key): {'caught SOURCE-DUP' if caught else 'MISSED'}")
        ok &= caught
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        d = json.load(open(os.path.join(tmp, TOOLS))); d["counts"]["script"] = 2
        json.dump(d, open(os.path.join(tmp, TOOLS), "w"), indent=2)
        bad_ok, _ = run(tmp, False, None, None, quiet=True)
        print(f"bad fixture (count drift vs catalog): {'caught' if not bad_ok else 'MISSED'}")
        ok &= not bad_ok
    d_on, d_off, d_old = _with_mined([]), _with_mined(["--no-mined"]), _with_mined(["--mined"])
    flip = d_on and not d_off and d_old
    print(f"default emits mined jobs (s4 flip; --no-mined opts out): {'PASS' if flip else 'FAIL'}")
    ok &= flip
    ok &= edge_self_test()
    ok &= mcp_self_test()
    print("self-test OK" if ok else "self-test FAILED")
    return ok


def mcp_self_test():
    """Amendment 8: index rows become tool:mcp atoms citing their line; serves edges come only from receipt lines
    naming both ends, never from a tool name that resembles a job."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "runtime/specs"))
        rows = [{"kind": "mcp", "name": "srv.apply_migration", "server": "srv", "tool": "apply_migration",
                 "fn": "mcp__srv__apply_migration", "purpose": "apply migration (from name)", "class": "write"},
                {"kind": "mcp", "name": "srv.row-a", "server": "srv", "tool": "row-a", "fn": "mcp__srv__row-a",
                 "purpose": "row a (from name)", "class": "write"}]
        json.dump({"captured_at": "2026-10-20", "tools": rows}, open(os.path.join(tmp, MCP_INDEX), "w"), indent=1)
        R = [{"receipt_id": "r1--ZH", "job_id": "job:backlog:row-a", "tool_id": "tool:mcp:srv.apply_migration"},
             {"receipt_id": "r2--ZH", "job_id": "job:backlog:no-such", "tool_id": "tool:mcp:srv.apply_migration"},
             {"receipt_id": "r3--ZH", "job_id": "job:backlog:row-a", "tool_id": "tool:mcp:srv.absent"},
             {"receipt_id": "", "job_id": "job:backlog:row-a", "tool_id": "tool:mcp:srv.row-a"}]
        open(os.path.join(tmp, ge.MCP_RECEIPTS), "w").write("\n".join(json.dumps(r) for r in R) + "\n")
        at, n, _ = mcp_tools(tmp)
        atoms = at + [{"id": "job:backlog:row-a", "kind": "job"}]
        E = mcp_edges(tmp, atoms)
        L = _lines(tmp, MCP_INDEX)
        good = (n == 2 and [a["id"] for a in at] == ["tool:mcp:srv.apply_migration", "tool:mcp:srv.row-a"]
                and all('"name": ' + json.dumps(a["source"]["key"]) in L[a["source"]["line"] - 1] for a in at)
                and [(e["from"], e["to"], e["evidence"]) for e in E]
                == [("tool:mcp:srv.apply_migration", "job:backlog:row-a", [f"{ge.MCP_RECEIPTS}:1", "receipt:r1--ZH"])])
    print(f"mcp index atoms + receipt-only edges (no edge from a name match, dangling end or blank id): {'PASS' if good else 'FAIL'}")
    return good


def edge_self_test():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        mem = _fixture(tmp)
        good, g = run(tmp, False, mem, None, quiet=True)
        trip = {(e["from"], e["type"], e["to"], e["rule"]) for e in g["edges"]}
        want = {("tool:script:a.py", "serves", "job:backlog:row-a", "route.tool"),
                ("blocker:backlog:row-b", "blocks", "job:backlog:row-b", "blocked-row"),
                ("blocker:backlog:row-b", "blocks", "job:backlog:row-a", "blocked-row"),
                ("job:backlog:row-a", "needs", "job:backlog:row-b", "depends-on"),
                ("tool:script:a.py", "design-dep", "tool:operator:op_x.py", "py-import"),
                ("tool:script:a.py", "runtime-dep", "dep:env:DATABASE_URL", "env-read"),
                ("tool:script:a.py", "runtime-dep", "dep:service:anthropic", "service"),
                ("tool:operator:op_x.py", "design-dep", "tool:script:a.py", "cite"),
                ("job:backlog:row-a", "needs", "dep:env:ANTHROPIC_API_KEY", "row-cite"),
                ("tool:operator:op_x.py", "design-dep", "tool:op:1", "operator-bind")}
        missing = want - trip
        wrong_dir = [t for t in trip if t[:3] == ("tool:script:a.py", "design-dep", "tool:operator:op_x.py") and t[3] == "cite"]
        print(f"bad edge fixture (cite line says 'emits' gives no cite edge): {'caught' if not wrong_dir else 'MISSED'}")
        ok &= not wrong_dir
        prose = [t for t in trip if t[0] == "tool:operator:op_x.py" and t[3] == "cite"]
        print(f"bad edge fixture (prose mention alone gives no cite; the run line does): {'caught' if len(prose) == 1 else 'MISSED'}")
        ok &= len(prose) == 1 and all(e["evidence"][0].endswith(":2") for e in g["edges"] if e["rule"] == "cite")
        defl = '    "resend": ("x", r"""from ["\']resend["\']|next-auth/providers/resend"""),'
        mm = re.compile(ge.SERVICES["resend"][1]).search(defl)
        self_match = bool(mm) and not ge.SVC_REGEX_DEF.search(defl[:mm.start()])
        print(f"bad edge fixture (a detector's own regex literal gives no service edge): {'caught' if not self_match else 'MISSED'}")
        ok &= not self_match
        real = 'import Resend from "next-auth/providers/' + 'resend"'  # split so this file is not itself a resend import
        mr = re.compile(ge.SERVICES["resend"][1]).search(real)
        print(f"good edge fixture (a real resend import still matches): {'ok' if mr and not ge.SVC_REGEX_DEF.search(real[:mr.start()]) else 'WRONG'}")
        ok &= bool(mr) and not ge.SVC_REGEX_DEF.search(real[:mr.start()])
        rr = re.compile(ge.RUN_PREFIX + r"(scripts/a\.py)(?![\w./-])")
        cases = [("operators/o.py", 'subprocess.run(["python3", "scripts/a.py"])', 1),
                 ("operators/o.py", 'print("fix:", ["python3", "scripts/a.py"])', 0),
                 ("operators/o.py", 'raise SystemExit("run: python3 scripts/a.py")', 0),
                 ("operators/o.py", '# python3 scripts/a.py', 0),
                 ("scripts/r.sh", 'python3 scripts/a.py --check', 1),
                 ("scripts/r.sh", 'echo "run python3 scripts/a.py"', 0),
                 ("scripts/r.sh", 'if ! python3 scripts/a.py --check; then', 1),
                 ("scripts/git-hooks/pre-commit", 'if ! python3 scripts/a.py --check; then', 1),
                 ("scripts/git-hooks/pre-commit", '# Fix: python3 scripts/a.py, re-stage.', 0),
                 ("scripts/git-hooks/pre-commit", '  echo "  run python3 scripts/a.py" >&2', 0),
                 ("scripts/git-hooks/pre-commit", 'if [ -f scripts/a.py ]; then', 0),
                 ("scripts/git-hooks/pre-commit", 'if ! echo "$f" | xargs -0 python3 scripts/a.py; then', 1),
                 ("scripts/git-hooks/pre-commit", 'echo "$f" | tr x y; echo "run python3 scripts/a.py"', 0),
                 (".claude/hooks/s.sh", '[ -x "$_d/scripts/a.py" ] && "$_d/scripts/a.py" "$_d" || true', 1),
                 (".claude/hooks/s.sh", 'python3 "$CLAUDE_PROJECT_DIR/scripts/a.py" check 2>/dev/null || true', 1),
                 (".claude/hooks/s.sh", '[ -f "$_d/scripts/a.py" ] || exit 0', 0),
                 ("scripts/g.sh", 'python3 scripts/a.py "$F" || fail "regression (raise the token)"', 1),
                 ("scripts/g.sh", 'python3 scripts/b.py || echo "then run python3 scripts/a.py"', 0),
                 ("operators/o.py", 'subprocess.run(["sh", "-c", "$HOME/scripts/a.py"])', 0),
                 (".claude/commands/c.md", 'Run `python3 scripts/a.py` first.', 1),
                 (".claude/commands/c.md", 'Queue produced by scripts/a.py nightly.', 0)]
        rt = lambda x: [c for c in ge.ROUTE_LIST.split(x) if not ge.ROUTE_HEDGE.search(c)
                        and not ge.ROUTE_TARGET.search(ge.ROUTE_NEGATED.sub(" ", c))]
        for clause, want_n in (("scripts/a.py", 1), ("NEW scripts/a.py", 0), ("extend scripts/a.py", 0),
                               ("scripts/a.py format", 0), ("pattern scripts/a.py", 0), ("np.polyfit (a.py:136)", 0),
                               ("NEW scripts/a.py + .claude/commands/b.md", 1), ("scripts/a.py (tao ns) + new scripts/b.py", 1), ("b.md (step 3 stale)", 0),
                               ("scripts/a.py BINDINGS[21]", 0), ("scripts/a.py; no new channel", 2),
                               ("the weekday 8:00 note / scripts/a.py", 1)):
            n = len(rt(clause))
            print(f"route.tool clause {clause!r}: {'ok' if n == want_n else 'WRONG'}")
            ok &= n == want_n
        jt_hit = bool(re.search(ge.JTBD_EDIT + r"(?<![\w-])/?tao-mint", "point /tao-mint and x at canon", re.I))
        jt_miss = bool(re.search(ge.JTBD_EDIT + r"(?<![\w-])/?tao-mint", "run /tao-mint on the batch", re.I))
        print(f"jtbd edit verb near a route.tool name makes a target: {'ok' if jt_hit and not jt_miss else 'WRONG'}")
        ok &= jt_hit and not jt_miss
        rdir = os.path.join(tmp, "runtime/specs"); json.dump({"note": "t", "edges": [], "retype": [{"mechanical":
            ["tool:script:a.py", "serves", "job:backlog:row-a"], "edge": {"from": "job:backlog:row-a", "to": "tool:script:a.py",
            "type": "needs", "evidence": ["backlog:row-a"], "match": "scripts/a.py", "by": "t", "rule": "residue-retype"}}]},
            open(os.path.join(rdir, "jtbd-graph-inferred-edges.json"), "w"))
        _, g2 = run(tmp, False, mem, None, quiet=True)
        t2 = {(e["from"], e["type"], e["to"], e["inferred"]) for e in g2["edges"]}
        rt_ok = ("tool:script:a.py", "serves", "job:backlog:row-a", False) not in t2 and ("job:backlog:row-a", "needs", "tool:script:a.py", True) in t2
        print(f"retype replaces the mechanical edge with a flagged inferred one: {'ok' if rt_ok else 'WRONG'}")
        ok &= rt_ok
        os.remove(os.path.join(rdir, "jtbd-graph-inferred-edges.json"))
        for src, want in (('k = os.environ["ANTHROPIC_API_KEY"]', True),
                          ('if judge and os.environ.get("ANTHROPIC_API_KEY"):\n    run()\nelse:\n    skip()', False),
                          ('key = os.environ.get("ANTHROPIC_API_KEY")\nif not key:\n    return None', False),
                          ('key = os.environ.get("ANTHROPIC_API_KEY")\nif not key:\n    sys.exit("set it")', True),
                          ('u = os.environ.get("DATABASE_URL") or sys.exit("no db")', True)):
            Ls = src.split("\n"); m = ge.ENV_RE.search(Ls[0])
            got = ge.env_hard(Ls, 0, "index" if m.group(4) or m.group(2) else "get")
            print(f"env-read case {Ls[0][:44]!r}: {'ok' if got == want else 'WRONG'}")
            ok &= got == want
        for src, want in (('U = os.environ["DATABASE_URL"]', False), ("w.write('U = os.environ[\"DATABASE_URL\"]')", True),
                          ('x = f"{os.environ[\'DATABASE_URL\']}"', False)):
            got = ge._in_string(src, ge.ENV_RE.search(src).start())
            print(f"env read inside a string literal {src[:40]!r}: {'ok' if got == want else 'WRONG'}")
            ok &= got == want
        for txt, want in (("Run scripts/a.py --check first.", 1), ("Same lesson as the /rca capture step.", 0),
                          ("x was superseded by scripts/a.py.", 0), ("Removed: 11 cites whose target now exists (a.py).", 0),
                          ("/prior-art and /catalog call it.", 0), ("Uses a.py. Same shape as b.py.", 1),
                          ("scripts/a.py fills x instead of leaving it empty", 1),
                          ('{"jtbd": "edit scripts/a.py", "note": "superseded old flow"}', 1)):
            got = len([x for x in ge.SENTENCE.split(ge.row_sentences(txt)) if "a.py" in x or "rca" in x or "catalog" in x])
            print(f"row-cite sentence {txt[:40]!r}: {'ok' if got == want else 'WRONG'}")
            ok &= got == want
        for f, line, want_n in cases:
            n = len(ge.run_paths(line, f, rr))
            good_case = n == want_n
            print(f"cite line case {f} {line[:40]!r}: {'ok' if good_case else 'WRONG'} ({n} vs {want_n})")
            ok &= good_case
        msg_ok = all(e["evidence"][0].endswith(":2") for e in g["edges"] if e["rule"] == "cite")
        print(f"bad edge fixture (command quoted in a SystemExit/print message gives no cite): {'caught' if msg_ok else 'MISSED'}")
        ok &= msg_ok
        gh = [t for t in trip if t[2] == "dep:service:github"]
        print(f"bad edge fixture (python gh subprocess is not a mechanical runtime-dep): {'caught' if not gh else 'MISSED'}")
        ok &= not gh
        soft = [t for t in trip if t[2] == "dep:service:vercel"]
        print(f"bad edge fixture (guarded vercel call emits no runtime-dep): {'caught' if not soft else 'MISSED'}")
        ok &= not soft
        good = good and not missing
        print(f"edge good fixture: {'PASS' if good else 'FAIL'} ({len(g['edges'])} edges; missing {sorted(missing)})")
        ok &= good
        cyc = g["cycles"]["design-dep"]
        print(f"cycle detector (a.py <-> op_x.py): {'caught' if cyc == [['tool:operator:op_x.py', 'tool:script:a.py']] else 'MISSED'}")
        ok &= cyc == [["tool:operator:op_x.py", "tool:script:a.py"]]
        rows = backlog(tmp)[2]
        for name, mut in (("shifted evidence line", lambda e: e.update(evidence=[e["evidence"][0].rsplit(":", 1)[0] + ":5"])),
                          ("evidence to a missing row", lambda e: e.update(evidence=["backlog:no-such-row"])),
                          ("match text absent at evidence", lambda e: e.update(match="zzz-not-there"))):
            h = json.loads(json.dumps(g))
            tgt = next(e for e in h["edges"] if e["rule"] == ("py-import" if "line" in name else "depends-on"))
            mut(tgt)
            caught = bool(ge.verify_edges(h, tmp, rows))
            print(f"bad edge fixture ({name}): {'caught' if caught else 'MISSED'}")
            ok &= caught
        h = json.loads(json.dumps(g)); h["edges"].append(dict(h["edges"][0], inferred=True))
        h["edges"][-1].pop("by", None); h["edges"][-1]["to"] = "job:backlog:row-b"
        f = gc.check(h, json.load(open(os.path.join(REPO, "runtime/specs/jtbd-graph-schema.json"))))
        caught = any(x.startswith("INFERRED-NO-BY") for x in f)
        print(f"bad edge fixture (inferred without by): {'caught' if caught else 'MISSED'}")
        ok &= caught
        h = json.loads(json.dumps(g))
        for e in h["edges"]:
            e["inferred"] = True; e["by"] = "x"
        E = h["edges"]; share = sum(1 for e in E if not e["inferred"]) / len(E)
        print(f"bad edge fixture (mechanical share {share:.2f} < 0.90): {'caught' if share < 0.90 else 'MISSED'}")
        ok &= share < 0.90
    return ok


def _git(root, *args):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _baseline_head(root):
    """The reference the baseline must stay a subset of: its first version on main's first-parent history.
    Round 2 class 10: a branch's own first version can be amended away before merge, so it never counts.
    Returns {} when the file is not on main yet (nothing to grow from), and None when git cannot answer, which
    the caller treats as a failure (round 2 class 11: fail closed)."""
    ref = "origin/main" if _git(root, "rev-parse", "--verify", "-q", "origin/main") else None
    if _git(root, "rev-parse", "--git-dir") is None:
        return None
    hist = _git(root, "log", "--first-parent", "--reverse", "--format=%H", ref or "HEAD", "--", gg.BASELINE)
    if hist is None:
        return None
    first = hist.split("\n")[0]
    if not first:
        return {}
    raw = _git(root, "show", f"{first}:{gg.BASELINE}")
    try:
        return json.loads(raw).get("rules", {}) if raw is not None else None
    except ValueError:
        return None


def check(root=REPO, mem_dir=MEM_DIR):
    try:
        ok, graph = run(root, False, mem_dir, None, quiet=True)
    except SourceDup as e:
        print(e); return 1
    schema = json.load(open(os.path.join(REPO, "runtime/specs/jtbd-graph-schema.json")))
    lookup = gc.check(graph, schema, root)
    found = gg.run_rules(graph, gg.Ctx(root, mem_dir=mem_dir if os.path.isdir(mem_dir) else None))
    base = gg._load(os.path.join(root, gg.BASELINE), {}).get("rules", {})
    new, held, stale = gg.apply_baseline(found, base)
    tri = gg._load(os.path.join(root, gg.TRIAGE), {}).get("holds", [])
    rows = {json.loads(l)["id"] for l in open(os.path.join(root, BACKLOG)) if l.strip()}
    new, triaged, tri_problems = gg.apply_triage(new, tri, __import__("datetime").date.today(), rows)
    head = _baseline_head(root)
    if head is None:
        grew = {"BASELINE-UNCHECKED": ["git history unavailable; cannot check that the baseline only shrinks"]}
    elif not head:
        grew = {}
        print(f"jtbd-graph --check: {gg.BASELINE} is not on main yet; growth is checked against its first main version from the merge on")
    else:
        grew = {r: sorted(set(ids) - set(head.get(r, []))) for r, ids in base.items()}
    grew = {r: v for r, v in grew.items() if v}
    if not ok:
        print("jtbd-graph --check: the s1/s2 build checks failed; run `python3 scripts/universe_jtbd_adapter.py` for the report")
    for x in lookup:
        print(x)
    for r in gg.RULES:
        for i, d in new[r]:
            print(f"{r} {i}: {d}")
        for i in stale.get(r, []):
            print(f"STALE-BASELINE {r} {i}: no longer violates; remove it from {gg.BASELINE}")
    for x in tri_problems:
        print(x)
    for r, i, due in triaged:
        print(f"TRIAGED {r} {i}: held until {due}")
    for x in gg.triage_due_soon(triaged, __import__("datetime").date.today()):
        print(x)  # warning only: never changes the verdict
    for r, ids in grew.items():
        for i in ids:
            print(f"BASELINE-GREW {r} {i}: the baseline may only shrink (add a dated amendment and get Zach's ok to grow it)")
    try:  # amendment 8 rule (a): a stale MCP index warns here and never fails the pre-commit gate
        import mcp_tool_index_emit as mie
        idx = mie.load_index(root)
        for w in (mie.staleness(idx) if idx else []):
            print(f"WARN mcp-index {w} (re-capture: python3 scripts/mcp_tool_index_emit.py --capture ...)")
    except Exception as e:  # noqa: BLE001
        print(f"WARN mcp-index: staleness not checked ({type(e).__name__})")
    line = " · ".join(f"{r.lower()} {len(new[r])} new/{len(held[r])} held" for r in gg.RULES)
    print(f"jtbd-graph --check: atoms {len(graph['atoms'])} edges {len(graph['edges'])} · {line}")
    bad = (not ok) or lookup or any(new.values()) or any(stale.values()) or grew or tri_problems
    summary = {"ok": not bad, "atoms": len(graph["atoms"]), "edges": len(graph["edges"]),
               "rules": {r: {"new": len(new[r]), "held": len(held[r]), "stale": len(stale.get(r, []))} for r in gg.RULES},
               "key_lookup": len(lookup), "baseline_grew": sum(len(v) for v in grew.values()),
               "head": _git(root, "rev-parse", "HEAD"),
               "at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")}
    try:
        os.makedirs(os.path.join(root, OUT), exist_ok=True)
        json.dump(summary, open(os.path.join(root, OUT, "check.json"), "w"), indent=1)
    except OSError:
        pass
    print("jtbd-graph --check: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


def pulse(root=REPO):
    s = gg._load(os.path.join(root, OUT, "check.json"), None)
    if not s:
        return "jtbd-graph: no --check run yet (python3 scripts/universe_jtbd_adapter.py --check)"
    r = s["rules"]
    held = sum(v["held"] for v in r.values()); new = sum(v["new"] + v["stale"] for v in r.values())
    short = {"ORPHAN-TOOL": "orphan-tool", "ORPHAN-JOB": "orphan-job", "BLOCKER-NO-RESOLVE-BY": "blocker",
             "DEP-CYCLE": "cycle", "DEAD-FILE-REF": "dead-ref", "RUNTIME-DEP-NO-PROBE": "no-probe"}
    parts = " ".join(f"{short.get(k, k)} {v['new']}/{v['held']}" for k, v in r.items())
    head = _git(root, "rev-parse", "HEAD")
    stale = "" if head and s.get("head") == head else " · STALE (HEAD moved since; rerun --check)"
    return (f"jtbd-graph: {'PASS' if s['ok'] else 'FAIL'}{stale} · atoms {s['atoms']} edges {s['edges']} · new {new} held {held} · "
            f"{parts} (new/held) · checked {s['at'][:16]}")


def _with_mined(argv):
    return "--no-mined" not in argv


def main(argv):
    if "--pulse" in argv:
        print(pulse()); return 0
    if "--check" in argv:
        return check()
    if "--self-test" in argv:
        return 0 if self_test() else 1
    try:
        ok, _ = run(REPO, _with_mined(argv), MEM_DIR, os.path.join(REPO, OUT))
    except SourceDup as e:
        print(e); return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
