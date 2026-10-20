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
  python3 operators/jtbd_query.py --self-test     # fixture: right tool first, budget held, blockers and closure found
Stdlib only. Reads _STATE/jtbd-graph/graph.json; builds it with scripts/universe_jtbd_adapter.py when missing.
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


def load_graph(root):
    p = os.path.join(root, GRAPH)
    if not os.path.exists(p):
        subprocess.run([sys.executable, os.path.join(root, "scripts/universe_jtbd_adapter.py")], cwd=root,
                       stdout=subprocess.DEVNULL, check=False)
    return json.load(open(p, encoding="utf-8"))


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


def rank(job, root=REPO, graph=None, mem_dir=MEM_DIR):
    graph = graph or load_graph(root)
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
    score = {t: ts[t] + JOB_BOOST * sum(js[j] for j in top_jobs if t in adj[j]) for t in tids}
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
    res = {"job": job, "assembly": asm, "scores": [round(score[t], 3) for t in asm],
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
        print("usage: jtbd_query.py \"job text\""); sys.exit(2)
    sys.path.insert(0, HERE)
    from arcs_librarian import Librarian
    print(json.dumps(Librarian(load_corpus=False).jtbd(job), indent=1))
