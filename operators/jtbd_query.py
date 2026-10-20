#!/usr/bin/env python3
"""jtbd_query: the s4 retrieval shape jtbd(job) over the JTBD graph (backlog row jtbd-graph-s4-retrieval).

Given a stated job, returns under 1,000 tokens (len/4 of the JSON):
  assembly       1 to 5 tool ids (schema form), best first (amendment 7 rule 2)
  blockers       open blocker atoms touching the matched jobs or the assembly
  closure        dependency closure of the assembly (design-dep, runtime-dep, needs; outgoing)
  receipts       last 3 personal decision receipts that name the best tool (Librarian load_universes)

Ranking, fixed before any s4 run (no weight was tuned on an s4 query; amendment 6 rule 4):
  1. Tool text = catalog jtbd line + name + path (tool:op: registry name, role and function).
     Kinds ranked: skill, command, workflow, script, operator, op. Surfaces, packages and hooks are not
     answers to "which tool" (hooks fire on their own) and stay out of the assembly; they can still appear
     in the closure.
  2. Job text = backlog jtbd line, memory description, pattern title and first paragraph.
  3. BM25 of the query against tools and against jobs, each scaled to its max. A tool's score is its own
     plus 0.5 x the summed scaled score of the top 10 jobs it shares an edge with (either direction).
  4. Assembly = tools scoring at least 0.6 x the top score, at most 5, at least 1.

  python3 operators/jtbd_query.py "job text"      # print the answer JSON
  python3 operators/jtbd_query.py --lookup "job"  # what /catalog and /prior-art call: freshness check, fallback, text
  python3 operators/jtbd_query.py --self-test     # fixture: right tool first, budget held, blockers and closure found
Stdlib only. Reads _STATE/jtbd-graph/graph.json; rebuilds it with scripts/universe_jtbd_adapter.py when missing or
older than any source catalog (SOURCES), and never serves a stale graph: lookup() falls back and says why.
"""
import collections, json, math, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
GRAPH = "_STATE/jtbd-graph/graph.json"
TOOLS = "runtime/specs/tool-catalog.json"
REG = "operators/OPERATOR-REGISTRY.json"
MEM_DIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
RANKED = ("tool:skill:", "tool:command:", "tool:workflow:", "tool:script:", "tool:operator:", "tool:op:")
BUDGET_TOKENS = 1000
JOB_BOOST, TOP_JOBS, KEEP_RATIO, MAX_ITEMS = 0.5, 10, 0.6, 5
STOP = set("the and for with that this from into over what which when then them they their have has are was were "
           "can our out all any how why its not but use see run see also each about across".split())


def tokens(s):
    out = []
    for w in re.findall(r"[a-z0-9]+", str(s).lower()):
        if len(w) < 3 or w in STOP:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[: -len(suf)]; break
        out.append(w)
    return out


class BM25:
    def __init__(self, docs, k1=1.2, b=0.75):
        self.docs = [collections.Counter(d) for d in docs]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = (sum(self.len) / len(self.len)) if self.len else 1.0
        df = collections.Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.k1, self.b = k1, b

    def scores(self, q):
        qs = set(q); out = []
        for d, L in zip(self.docs, self.len):
            s = 0.0
            for t in qs:
                f = d.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * L / (self.avg or 1)))
            out.append(s)
        return out


def _scaled(xs):
    m = max(xs) if xs else 0
    return [x / m if m else 0.0 for x in xs]


def _read(path, n=1200):
    try:
        return open(path, encoding="utf-8").read()[:n]
    except OSError:
        return ""


# Source catalogs the adapter reads (scripts/universe_jtbd_adapter.py docstring + jtbd_graph_edges.py). A graph
# older than the newest of these is stale. Folders count by their newest *.md (memory, _PATTERNS).
SOURCES = (TOOLS, REG, "runtime/specs/surface-catalog.json", "package.json", "_QUEUE/induced-backlog.jsonl",
           "AGENTS.md", "src/lib/env.ts", "runtime/specs/jtbd-graph-inferred-edges.json",
           "runtime/specs/jtbd-graph-schema.json", "runtime/specs/jtbd-label-sample-20261018.json")
# Edges are also mined from each atom's own file (jtbd_graph_edges reads tool sources), so every atom path in the
# graph counts as a source too (graph_status reads them from the graph itself).
SOURCE_DIRS = ("_PATTERNS",)


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0.0


def _atom_paths(root):
    try:
        g = json.load(open(os.path.join(root, GRAPH), encoding="utf-8"))
        return sorted({a["path"] for a in g.get("atoms", []) if a.get("path") and not a["id"].startswith("job:memory:")})
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return []


def newest_source(root, mem_dir=MEM_DIR):
    """(mtime, path) of the newest source file (catalogs, folders, every atom's own file), or (0, None)."""
    best = (0.0, None)
    for rel in tuple(SOURCES) + tuple(_atom_paths(root)):
        m = _mtime(os.path.join(root, rel))
        if m > best[0]:
            best = (m, rel)
    for d in [os.path.join(root, x) for x in SOURCE_DIRS] + [mem_dir]:
        try:
            names = [n for n in os.listdir(d) if n.endswith(".md") and n != "MEMORY.md"]
        except OSError:
            continue
        for n in names:
            m = _mtime(os.path.join(d, n))
            if m > best[0]:
                best = (m, os.path.join(d, n))
    return best


def graph_status(root, mem_dir=MEM_DIR):
    """'missing' | 'stale' | 'fresh', with the source that made it stale."""
    g = _mtime(os.path.join(root, GRAPH))
    if not g:
        return "missing", None
    m, src = newest_source(root, mem_dir)
    return ("stale", src) if m > g else ("fresh", None)


def build_graph(root):
    """Run the adapter; True only if it exits 0 and the graph file then exists."""
    try:
        r = subprocess.run([sys.executable, os.path.join(root, "scripts/universe_jtbd_adapter.py")], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and os.path.exists(os.path.join(root, GRAPH))


def load_graph(root, mem_dir=MEM_DIR):
    """Graph JSON, rebuilt first when missing or stale. Raises RuntimeError rather than serving a stale graph."""
    st, src = graph_status(root, mem_dir)
    if st != "fresh" and not build_graph(root):
        raise RuntimeError(f"graph {st}" + (f" (newer source {src})" if src else "") + "; rebuild failed")
    st, src = graph_status(root, mem_dir)
    if st != "fresh":
        raise RuntimeError(f"graph still {st} after rebuild" + (f" (newer source {src})" if src else ""))
    return json.load(open(os.path.join(root, GRAPH), encoding="utf-8"))


def lookup(job, root=REPO, mem_dir=MEM_DIR, receipts=None, rebuild=True):
    """First source for "which tool for this job". Returns {"path": "jtbd-graph"|"fallback", "reason", "answer"}.
    path=fallback means the caller must answer the old way (keyword ranking / reading the catalog), and say so.
    Never raises; never serves a graph older than its sources."""
    st, src = graph_status(root, mem_dir)
    if st != "fresh":
        if not rebuild:
            return {"path": "fallback", "reason": f"graph {st}" + (f" (newer source {src})" if src else "")
                    + "; rebuild disabled", "answer": None}
        if not build_graph(root) or graph_status(root, mem_dir)[0] != "fresh":
            return {"path": "fallback", "reason": f"graph {st}; rebuild failed", "answer": None}
        note = f"graph was {st}, rebuilt"
    else:
        note = "graph fresh"
    try:
        g = json.load(open(os.path.join(root, GRAPH), encoding="utf-8"))
        a = answer(job, root, g, mem_dir, receipts)
    except Exception as e:  # a corrupt graph must not crash the command; it falls back loudly
        return {"path": "fallback", "reason": f"graph unreadable ({type(e).__name__}: {str(e)[:80]})", "answer": None}
    if not a.get("assembly"):
        return {"path": "fallback", "reason": note + "; graph returned nothing for this job", "answer": a}
    return {"path": "jtbd-graph", "reason": note, "answer": a}


def render(res):
    """Short text block for the commands. The JSON answer itself is held under BUDGET_TOKENS by answer()."""
    lines = [f"answered by: {res['path']} ({res['reason']})"]
    a = res.get("answer")
    if res["path"] != "jtbd-graph" or not a:
        lines.append("fallback: use the keyword ranking / catalog read below; the graph did not answer.")
        return "\n".join(lines)
    for i, (t, s) in enumerate(zip(a["assembly"], a["scores"])):
        lines.append(f"  {'best' if i == 0 else '    '} [{s:>5}] {t}")
    if a["blockers"]:
        lines.append("  open blockers: " + ", ".join(b["id"] + (f" (resolve by {b['resolve_by']})" if b.get("resolve_by") else "")
                                             for b in a["blockers"]))
    if a["closure_total"]:
        shown = a["closure"][:8]
        lines.append(f"  needs ({a['closure_total']}): " + ", ".join(shown) + (" ..." if a["closure_total"] > len(shown) else ""))
    r = a["receipts"]
    lines.append("  last receipts: " + (", ".join(f"{x['id']} {x['date'] or ''}".strip() for x in r) if isinstance(r, list) else r))
    lines.append(f"  ({a['tokens']} tokens)")
    return "\n".join(lines)


def tool_texts(root, atoms):
    cat = {}
    try:
        for t in json.load(open(os.path.join(root, TOOLS)))["tools"]:
            cat[f"tool:{t['kind']}:{t['name']}"] = t.get("jtbd") or ""
    except (OSError, ValueError):
        pass
    reg = {}
    try:
        for o in json.load(open(os.path.join(root, REG)))["operators"]:
            reg[f"tool:op:{o['op']}"] = " ".join(str(o.get(k, "")) for k in ("name", "role", "function", "level"))
    except (OSError, ValueError):
        pass
    out = {}
    for a in atoms:
        i = a["id"]
        if not i.startswith(RANKED):
            continue
        name = i.split(":", 2)[2]
        out[i] = " ".join([cat.get(i) or a.get("title") or "", reg.get(i, ""), name.replace("_", " ").replace("-", " "),
                           (a.get("path") or "").replace("/", " ")])
    return out


def job_texts(root, atoms, mem_dir):
    out = {}
    for a in atoms:
        i = a["id"]
        if a["kind"] != "job":
            continue
        if i.startswith("job:memory:"):
            body = _read(os.path.join(mem_dir, os.path.basename(a.get("path", ""))))
            m = re.search(r"^description:\s*(.+)$", body, re.M)
            out[i] = (m.group(1) if m else "") + " " + i.split(":", 2)[2].replace("-", " ")
        elif i.startswith("job:pattern:"):
            out[i] = _read(os.path.join(root, a.get("path", "")), 600) + " " + i.split(":", 2)[2].replace("-", " ")
        else:
            out[i] = (a.get("title") or "") + " " + i.split(":", 2)[2].replace("-", " ")
    return out


def _weights(root):
    """{(job, tool): W} from scripts/jtbd_edge_weights.py; {} on any problem (never breaks retrieval)."""
    try:
        sys.path.insert(0, os.path.join(root, "scripts"))
        import jtbd_edge_weights
        return jtbd_edge_weights.load_weights(root)
    except Exception:  # noqa: BLE001
        return {}


def rank(job, root=REPO, graph=None, mem_dir=MEM_DIR):
    graph = graph or load_graph(root, mem_dir)
    atoms = graph["atoms"]
    tt = tool_texts(root, atoms); jt = job_texts(root, atoms, mem_dir)
    tids, jids = list(tt), list(jt)
    q = tokens(job)
    ts = dict(zip(tids, _scaled(BM25([tokens(tt[i]) for i in tids]).scores(q))))
    js = dict(zip(jids, _scaled(BM25([tokens(jt[i]) for i in jids]).scores(q))))
    top_jobs = [j for j in sorted(js, key=lambda j: -js[j])[:TOP_JOBS] if js[j] > 0]
    adj = collections.defaultdict(set)
    for e in graph["edges"]:
        adj[e["from"]].add(e["to"]); adj[e["to"]].add(e["from"])
    # s5 (row jtbd-graph-s5-feedback): per-edge outcome weight W(j, t), promote-only and 1.0 by default, so an
    # empty or missing weights file leaves this byte-identical to s4. Rules: _PATTERNS/2026-10-20-jtbd-s5-preregistration.md.
    W = _weights(root)
    score = {t: ts[t] + JOB_BOOST * sum(js[j] * W.get((j, t), 1.0) for j in top_jobs if t in adj[j]) for t in tids}
    order = sorted((t for t in tids if score[t] > 0), key=lambda t: (-score[t], t))
    return order, score, top_jobs, graph


def answer(job, root=REPO, graph=None, mem_dir=MEM_DIR, receipts=None):
    order, score, top_jobs, graph = rank(job, root, graph, mem_dir)
    if not order:
        return {"job": job, "assembly": [], "note": "no tool fits; route to the backlog"}
    top = score[order[0]]
    asm = [t for t in order if score[t] >= KEEP_RATIO * top][:MAX_ITEMS] or order[:1]
    byid = {a["id"]: a for a in graph["atoms"]}
    out_e = collections.defaultdict(list)
    for e in graph["edges"]:
        out_e[e["from"]].append(e)
    # blockers: blocker atoms for the matched jobs, plus any blocks edge into a matched job or an assembly tool
    near = set(top_jobs) | set(asm)
    blk = set()
    for j in top_jobs:
        b = "blocker:" + j.split(":", 1)[1]
        if b in byid:
            blk.add(b)
    for e in graph["edges"]:
        if e["type"] == "blocks" and e["to"] in near:
            blk.add(e["from"])
    blockers = [{"id": b, "resolve_by": byid.get(b, {}).get("resolve_by")} for b in sorted(blk)
                if byid.get(b, {}).get("state", "BLOCKED") == "BLOCKED"]
    # closure: outgoing design-dep / runtime-dep / needs, transitive, from the assembly
    seen, stack = set(), list(asm)
    while stack:
        n = stack.pop()
        for e in out_e.get(n, []):
            if e["type"] in ("design-dep", "runtime-dep", "needs") and e["to"] not in seen and e["to"] not in asm:
                seen.add(e["to"]); stack.append(e["to"])
    closure = sorted(seen)
    best = asm[0]; name = best.split(":", 2)[2]; path = byid.get(best, {}).get("path") or ""
    recs = []
    for c in receipts or []:
        hay = c.text + " " + " ".join(c.refs or [])
        if name in hay or (path and path in hay):
            recs.append({"id": c.id, "date": c.date})
    recs = sorted(recs, key=lambda r: r["date"] or "", reverse=True)[:3]
    res = {"job": job if len(job) <= 200 else job[:200] + "...", "assembly": asm, "scores": [round(score[t], 3) for t in asm],
           "matched_jobs": top_jobs[:3], "blockers": blockers, "closure": closure, "closure_total": len(closure),
           "receipts": recs or "none local naming the best tool"}
    while len(json.dumps(res)) / 4 > BUDGET_TOKENS and res["closure"]:
        res["closure"] = res["closure"][: len(res["closure"]) // 2] if len(res["closure"]) > 1 else []
    while len(json.dumps(res)) / 4 > BUDGET_TOKENS and len(res["blockers"]) > 1:
        res["blockers"] = res["blockers"][:-1]
    res["tokens"] = math.ceil(len(json.dumps(res)) / 4)
    return res


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "runtime/specs")); os.makedirs(os.path.join(tmp, "operators"))
        json.dump({"tools": [{"kind": "script", "name": "wt_prune.py", "jtbd": "prune stale git worktrees safely"},
                             {"kind": "skill", "name": "night", "jtbd": "end of day digest of commits"},
                             {"kind": "script", "name": "dep.py", "jtbd": "helper"}]}, open(os.path.join(tmp, TOOLS), "w"))
        json.dump({"operators": [{"op": 21, "name": "Librarian", "role": "CTO", "function": "retrieve decisions"}]},
                  open(os.path.join(tmp, REG), "w"))
        many = [{"id": f"tool:script:x{i}.py", "kind": "tool", "title": "unrelated words " * 5} for i in range(400)]
        g = {"atoms": [{"id": "tool:script:wt_prune.py", "kind": "tool", "path": "scripts/wt_prune.py"},
                       {"id": "tool:skill:night", "kind": "tool"}, {"id": "tool:script:dep.py", "kind": "tool"},
                       {"id": "tool:op:21", "kind": "tool"}, {"id": "tool:surface:a/b", "kind": "tool", "title": "worktrees worktrees"},
                       {"id": "job:backlog:clean-trees", "kind": "job", "title": "clean up worktrees that pile up", "state": "BLOCKED"},
                       {"id": "blocker:backlog:clean-trees", "kind": "blocker", "state": "BLOCKED", "resolve_by": "2026-11-01"}] + many,
             "edges": [{"from": "tool:script:wt_prune.py", "to": "tool:script:dep.py", "type": "design-dep"},
                       {"from": "job:backlog:clean-trees", "to": "tool:script:wt_prune.py", "type": "needs"}]
             + [{"from": "tool:script:wt_prune.py", "to": f"tool:script:x{i}.py", "type": "design-dep"} for i in range(400)]}

        class C:  # Librarian Candidate shape
            def __init__(s, i, t, d): s.id, s.text, s.refs, s.date = i, t, [], d
        recs = [C(f"r{i}", "ran wt_prune.py", f"2026-10-0{i}") for i in range(1, 6)] + [C("rz", "other", "2026-10-09")]
        r = answer("my git worktrees keep piling up, prune them", tmp, g, tmp, recs)
        checks = {
            "right tool first": r["assembly"][:1] == ["tool:script:wt_prune.py"],
            "assembly 1 to 5 ranked kinds only": 1 <= len(r["assembly"]) <= 5 and all(a.startswith(RANKED) for a in r["assembly"]),
            "open blocker found": [b["id"] for b in r["blockers"]] == ["blocker:backlog:clean-trees"],
            "closure includes dep": "tool:script:dep.py" in r["closure"] or r["closure_total"] > len(r["closure"]),
            "closure total counts 401": r["closure_total"] == 401,
            "last 3 receipts newest first": [x["id"] for x in r["receipts"]] == ["r5", "r4", "r3"],
            "budget under 1,000 tokens": r["tokens"] <= BUDGET_TOKENS,
        }
        bad = answer("zzqx", tmp, g, tmp, recs)
        checks["no match says no tool fits"] = bad["assembly"] == []
        # lookup(): the command entry. No adapter in tmp, so every rebuild fails: it must fall back, not crash or serve.
        gp = os.path.join(tmp, GRAPH)
        lk = lambda **kw: lookup("prune git worktrees", tmp, tmp, recs, **kw)
        checks["absent graph falls back"] = lk()["path"] == "fallback" and "missing" in lk()["reason"]
        os.makedirs(os.path.dirname(gp)); json.dump(g, open(gp, "w"))
        os.utime(os.path.join(tmp, TOOLS), (1e9, 1e9)); os.utime(os.path.join(tmp, REG), (1e9, 1e9)); os.utime(gp, (2e9, 2e9))
        fresh = lk()
        checks["fresh graph answers"] = fresh["path"] == "jtbd-graph" and fresh["answer"]["assembly"][0] == "tool:script:wt_prune.py"
        checks["render names the path"] = render(fresh).startswith("answered by: jtbd-graph")
        os.utime(os.path.join(tmp, TOOLS), (3e9, 3e9))
        st = lk()
        checks["stale graph never served"] = st["path"] == "fallback" and "stale" in st["reason"] and st["answer"] is None
        checks["stale names the source"] = "stale" in lk(rebuild=False)["reason"] and TOOLS in lk(rebuild=False)["reason"]
        try:
            load_graph(tmp, tmp); checks["load_graph refuses stale"] = False
        except RuntimeError:
            checks["load_graph refuses stale"] = True
        open(gp, "w").write("{not json"); os.utime(gp, (4e9, 4e9))
        checks["corrupt graph falls back"] = lk()["path"] == "fallback" and "unreadable" in lk()["reason"]
        json.dump(g, open(gp, "w")); os.utime(gp, (4e9, 4e9))
        nothing = lookup("zzqx", tmp, tmp, recs)
        checks["empty answer falls back"] = nothing["path"] == "fallback" and "nothing" in nothing["reason"]
        os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True); open(os.path.join(tmp, "scripts/wt_prune.py"), "w").write("x")
        os.utime(os.path.join(tmp, "scripts/wt_prune.py"), (5e9, 5e9))
        checks["changed tool source makes it stale"] = graph_status(tmp, tmp)[0] == "stale"
        os.utime(gp, (6e9, 6e9))
        long = lookup("prune git worktrees " * 400 + "\u00e9\u4e2d" * 1500, tmp, tmp, recs)
        checks["long job stays under budget"] = long["path"] == "jtbd-graph" and len(json.dumps(long)) / 4 <= BUDGET_TOKENS
        checks["fallback render says fallback"] = "fallback" in render(nothing).split("\n")[1]
        ok = all(checks.values())
        for k, v in checks.items():
            print(f"{k}: {'PASS' if v else 'FAIL'}")
        print("self-test OK" if ok else "self-test FAILED")
        return ok


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    job = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))
    if not job:
        print("usage: jtbd_query.py [--lookup [--json] [--no-rebuild]] \"job text\""); sys.exit(2)
    sys.path.insert(0, HERE)
    if "--lookup" in sys.argv:  # /catalog and /prior-art entry: freshness-checked, falls back, never crashes
        recs = None
        try:
            from arcs_librarian import load_universes
            recs = load_universes(__import__("pathlib").Path(REPO))
        except Exception:
            recs = None
        res = lookup(job, REPO, MEM_DIR, recs, rebuild="--no-rebuild" not in sys.argv)
        print(json.dumps(res, indent=1) if "--json" in sys.argv else render(res))
        sys.exit(0)
    # One-way: this module reads the Librarian's personal-tier receipts; the Librarian never imports this module
    # (its jtbd() wrapper was removed 2026-10-20 to break the DEP-CYCLE the jtbd-graph gate reported).
    from arcs_librarian import load_universes
    print(json.dumps(answer(job, REPO, None, MEM_DIR, load_universes(__import__("pathlib").Path(REPO))), indent=1))
