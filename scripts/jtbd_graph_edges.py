#!/usr/bin/env python3
"""jtbd_graph_edges: Sprint 2 edges for the JTBD graph (backlog row jtbd-graph-s2-edges).

Imported by scripts/universe_jtbd_adapter.py. Stdlib only. Mechanical rules first (AGENTS.md gotcha 11);
each mechanical edge carries `rule` (which rule made it) and `match` (the text the cited evidence must
contain), so verify_edges() can reopen the evidence and confirm it without trusting the builder.

Mechanical rules
  serves       route.tool    a backlog row's route.tool names a tool (path, /invoke, script basename)
  needs        route-target  a surface file named in route.tool is the job's target: job -> surface
  blocks       blocked-row   blocker:backlog:X -> job:backlog:X ; and -> job:backlog:Y when Y.depends_on has X
  needs        depends-on    job -> job from depends_on
  needs        row-cite      a row's text (route excluded) names a tool path/basename, an env var or a quoted npm package
  design-dep   operator-bind tool:operator:<file> -> tool:op:<n> (registry binding.module, s1)
  design-dep   py-import     `import x` / `from x import` resolving to a cataloged scripts/ or operators/ file
  design-dep   js-import     import/require of an npm package that is a dep:npm atom
  design-dep   cite          a tool file RUNS another tool's full path on that line (python3/bash/node/./ path, or an
                             argv list); bare prose mentions give no edge (round 3). Also (neighbor_scan.py citer rule, full path only;
                             skipped: CITE_NOISE pages, lines with direction words (writes, emits, generated, feeds,
                             checks...), and script/operator -> surface, which is generator or gate, not written against)
  runtime-dep  env-read      process.env.X / os.environ[...] / os.getenv for an env var that is a dep:env atom
  runtime-dep  service       a tool file line matches a service's call signature (SERVICES below), unless the call
                             is guarded. anthropic/database/resend: import signatures. github/vercel/perplexity: only
                             set -e shell lines with no 2>/dev/null or || fallback on the joined logical line
Judgment edges: runtime/specs/jtbd-graph-inferred-edges.json (hand pass on the residue), inferred=true + by.
"""
import json, os, re

BACKLOG = "_QUEUE/induced-backlog.jsonl"
AGENTS = "AGENTS.md"
ENV_TS = "src/lib/env.ts"
ENV_CAT = "AGENTS.md env table and src/lib/env.ts"
SVC_CAT = "AGENTS.md connected systems, hand-declared"
INFERRED = "runtime/specs/jtbd-graph-inferred-edges.json"

# slug -> (needle on the AGENTS.md line that declares it, call-signature regex in a tool file)
SERVICES = {
    "anthropic": ("Anthropic SDK", r"from anthropic import|^\s*import anthropic\b|@anthropic-ai/sdk"),
    "database": ("Supabase (prod)", r"""from ["']@/lib/db["']|@prisma/client|^\s*import psycopg|from supabase import|@supabase/supabase-js"""),
    "resend": ("Magic link emails via Resend", r"""from ["']resend["']|next-auth/providers/resend"""),
    "github": ("gh pr merge --merge", r"""\[\s*["']gh["']\s*,|api\.github\.com|^\s*gh (pr|api|run|repo) """),
    "vercel": ("Vercel `get_deployment", r"""\[\s*["']vercel["']\s*,|api\.vercel\.com|^\s*(npx )?vercel """),
    "perplexity-mcp": ("Perplexity MCP |", r"api\.perplexity\.ai"),
}
# round 3 (seed 20261020): prose mentions carry no reliable direction ("produced by", "covers", banners, ALLOW
# lists, wrapped lines). A mechanical cite now needs the cited path to be RUN on that line.
INVOKE = r"""(?:python3?|bash|sh|node|npx\s+tsx|tsx|zsh)\s+(?:-\S+\s+)*|\./|["'](?:python3?|bash|sh|node)["']\s*,\s*["']"""
# round 4 (seed 20261021): in code, a command quoted in a message/remedy/comment is not run by the citer
MSG_RE = re.compile(r"SystemExit|sys\.exit|\bprint\(|\bfix\s*=|remed|\braise\b|\becho\b|console\.(log|error)|f[\"']|hint|finding\(")
SH_START = re.compile(r"^\s*(?:(?:then|do|else|&&|\|\||[A-Z_]+=\$\()\s*)?(?:python3?|bash|sh|node|npx\s+tsx|tsx|zsh|\./)")
# a route.tool clause offering a template, precedent or proposal names no tool doing the job
ROUTE_HEDGE = re.compile(r"\b(pattern|template|precedent|prior art|when built|sibling|e\.g\.|like|modelled|modeled)\b", re.I)
ROUTE_SPLIT = re.compile(r"\s*(?:[;,·+]|\bOR\b|\bor\b|\band\b|->)\s*")
CODE_EXT = (".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".sh")
ENV_RE = re.compile(r"""process\.env\.([A-Z][A-Z0-9_]*)|process\.env\[["']([A-Z][A-Z0-9_]*)["']\]|os\.environ\.get\(\s*["']([A-Z][A-Z0-9_]*)|os\.environ\[\s*["']([A-Z][A-Z0-9_]*)|os\.getenv\(\s*["']([A-Z][A-Z0-9_]*)""")
PY_IMP = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import\b|import\s+([A-Za-z_][\w.]*(?:\s*,\s*[A-Za-z_][\w.]*)*))")
JS_IMP = re.compile(r"""(?:^\s*import\b[^'"]*?from\s*|^\s*import\s*|\brequire\(\s*|\bimport\(\s*)["']([^"'./][^"']*)["']""")
# a call that degrades instead of failing is not a runtime-dep (s2 counter-agent, seed 20261018, refuted edge 10)
SOFT_SH = re.compile(r"2>\s*/dev/null|\|\|\s*(true|echo|:)\b|\|\|\s*:$")
# generated listing pages cite every row of a catalog; they are offspring of the catalog, not written against each row
CITE_NOISE = ("runtime/warroom/surfaces.html",)
# round 2 (seed 20261019): a cite whose line says the citer writes/feeds/generates the cited file, or that the cited
# file reads from the citer, runs the other way; the shell cannot tell the direction, so it emits nothing
CITE_DIRECTION = re.compile(r"\b(writ(e|es|ten|ing)|emit(s|ted|ting)?|generat(e|es|ed|ing)|render(s|ed|ing)?|feed(s|ing)?|"
                            r"output|produc(e|es|ed)|from here|once recovered|reads? from|consumer|scan(s|ned)?|check(s|ed)?|gate(s|d)?)\b", re.I)
STRIP_ROUTE = re.compile(r"(?:pattern|template|resources?|prior art|precedent)\s*:\s*[^;·]+", re.I)


def _read(root, rel, cache):
    if rel not in cache:
        p = os.path.join(root, rel)
        try:
            cache[rel] = open(p, encoding="utf-8", errors="replace").read().split("\n") if os.path.isfile(p) else None
        except OSError:
            cache[rel] = None
    return cache[rel]


def env_and_service_atoms(root, atom, dups):
    """dep:env from the AGENTS.md env table + process.env reads in src/lib/env.ts; dep:service hand table."""
    cache, out, seen = {}, [], {}
    L = _read(root, AGENTS, cache) or []
    start = next((i for i, l in enumerate(L) if l.strip() == "## Environment variables"), None)
    names = []
    if start is not None:
        for i in range(start + 1, len(L)):
            if L[i].startswith("## "):
                break
            m = re.match(r"^\|\s*`([A-Z][A-Z0-9_]*)`\s*\|", L[i])
            if m:
                names.append(m.group(1)); seen.setdefault(m.group(1), (AGENTS, i + 1))
    dups(names, AGENTS + " env table")
    for i, l in enumerate(_read(root, ENV_TS, cache) or []):
        for m in re.finditer(r"process\.env\.([A-Z][A-Z0-9_]*)", l):
            seen.setdefault(m.group(1), (ENV_TS, i + 1))
    for n, (f, ln) in seen.items():
        out.append(atom(f"dep:env:{n}", "dep", ENV_CAT, n, ln, path=f))
    for slug, (needle, _) in SERVICES.items():
        ln = next((i + 1 for i, l in enumerate(L) if needle in l), None)
        if ln is None:
            raise ValueError(f"service {slug}: needle {needle!r} not in {AGENTS}")
        out.append(atom(f"dep:service:{slug}", "dep", SVC_CAT, slug, ln, path=AGENTS, title=needle))
    return out


HARD_SVC = {"anthropic", "database", "resend"}  # import-signature services: an import that fails at load is a hard dep


def _logical(L, i):
    """The shell logical line starting at i (backslash and trailing-pipe continuations joined)."""
    out, j = L[i], i
    while j + 1 < len(L) and (L[j].rstrip().endswith("\\") or L[j].rstrip().endswith("|")):
        j += 1; out += " " + L[j]
    return out


def run_paths(line, p, run_re):
    """Matches on `line` (in tool file p) where p really runs another path; the cite rule's whole decision."""
    code = p.endswith(CODE_EXT)
    if code and (line.lstrip().startswith(("#", "//", "*")) or MSG_RE.search(line)):
        return []
    out = []
    for m in run_re.finditer(line):
        if code and p.endswith(".sh") and not SH_START.match(line):
            continue
        if code and not p.endswith(".sh") and m.group(0)[0] not in "\"'":
            continue  # .py/.js: only a real argv list runs the path
        out.append(m)
    return out


def _soft(L, i):
    """True when line i is guarded: shell fallback on the line, or a Python try: opening within 3 lines above."""
    if SOFT_SH.search(L[i]):
        return True
    ind = len(L[i]) - len(L[i].lstrip())
    for j in range(max(0, i - 3), i):
        if L[j].strip() == "try:" and len(L[j]) - len(L[j].lstrip()) < ind:
            return True
    return False


def _edge(fr, to, typ, ev, match, rule):
    return {"from": fr, "to": to, "type": typ, "evidence": [ev], "inferred": False, "rule": rule, "match": match}


def build_edges(root, atoms, rows, op_edges):
    ids = {a["id"] for a in atoms}
    tool_atoms = [a for a in atoms if a["kind"] == "tool"]
    by_path = {}  # repo file -> [tool ids]
    for a in tool_atoms:
        if a.get("path"):
            by_path.setdefault(a["path"], []).append(a["id"])
    # names usable in prose: full paths always; script/operator basenames >= 6 chars when unique; /invoke for commands+skills
    base = {}
    for a in tool_atoms:
        if a["id"].startswith(("tool:script:", "tool:operator:")) and a.get("path"):
            b = os.path.basename(a["path"])
            if len(b) >= 6:
                base.setdefault(b, []).append(a["id"])
    base = {b: v[0] for b, v in base.items() if len(v) == 1}
    inv = {}
    for a in tool_atoms:
        if a["id"].startswith(("tool:command:", "tool:skill:")):
            inv.setdefault("/" + a["id"].split(":", 2)[2], []).append(a["id"])
    paths_sorted = sorted(by_path, key=len, reverse=True)
    path_re = re.compile("|".join(re.escape(p) for p in paths_sorted)) if paths_sorted else None
    run_re = re.compile(r"(?:" + INVOKE + r")(" + "|".join(re.escape(p) for p in paths_sorted) + r")(?![\w./-])") if paths_sorted else None
    base_re = re.compile(r"(?<![\w/.-])(" + "|".join(re.escape(b) for b in sorted(base, key=len, reverse=True)) + r")(?![\w-])") if base else None
    inv_re = re.compile(r"(?<![\w/.-])(" + "|".join(re.escape(i) for i in sorted(inv, key=len, reverse=True)) + r")(?![\w/-])") if inv else None

    def name_hits(text):
        hits = []
        consumed = []
        if path_re:
            for m in path_re.finditer(text):
                consumed.append(m.span())
                hits += [(t, m.group(0)) for t in by_path[m.group(0)]]
        for rx, table in ((base_re, base), (inv_re, inv)):
            if not rx:
                continue
            for m in rx.finditer(text):
                if any(s <= m.start() < e for s, e in consumed):
                    continue
                v = table[m.group(1)]
                hits += [(t, m.group(1)) for t in (v if isinstance(v, list) else [v])]
        return hits

    edges = list(op_edges)
    for e in edges:
        e.setdefault("rule", "operator-bind")
    row_by = {r["id"]: (ln, r) for ln, r in rows}
    env_names = {a["id"][8:] for a in atoms if a["id"].startswith("dep:env:")}
    npm_names = {a["id"][8:] for a in atoms if a["id"].startswith("dep:npm:")}
    npm_re = re.compile(r"""(?<=[`'"])(""" + "|".join(re.escape(n) for n in sorted(npm_names, key=len, reverse=True)) + r""")(?=[`'"@])""") if npm_names else None
    env_word = re.compile(r"(?<![A-Z0-9_])(" + "|".join(sorted(env_names, key=len, reverse=True)) + r")(?![A-Z0-9_])") if env_names else None

    for ln, r in rows:
        jid = f"job:backlog:{r['id']}"
        rt = (r.get("route") or {}).get("tool") or ""
        clauses = [c for c in ROUTE_SPLIT.split(STRIP_ROUTE.sub(" ", rt)) if c and not ROUTE_HEDGE.search(c)]
        for tid, m in name_hits(" ; ".join(clauses)):
            if tid.startswith("tool:surface:"):
                # a page named in route.tool is what the job edits, not a tool doing it (round 2, seed 20261019)
                edges.append(_edge(jid, tid, "needs", f"backlog:{r['id']}", m, "route-target"))
            else:
                edges.append(_edge(tid, jid, "serves", f"route.tool:{r['id']}", m, "route.tool"))
        if r.get("state") == "BLOCKED":
            edges.append(_edge(f"blocker:backlog:{r['id']}", jid, "blocks", f"backlog:{r['id']}", '"state": "BLOCKED"', "blocked-row"))
        for d in r.get("depends_on") or []:
            if f"job:backlog:{d}" in ids:
                edges.append(_edge(jid, f"job:backlog:{d}", "needs", f"backlog:{r['id']}", d, "depends-on"))
                if row_by.get(d, (0, {}))[1].get("state") == "BLOCKED":
                    edges.append(_edge(f"blocker:backlog:{d}", jid, "blocks", f"backlog:{r['id']}", d, "blocked-row"))
        rest = {k: v for k, v in r.items() if k not in ("route", "id", "depends_on", "unblocks")}
        text = json.dumps(rest, ensure_ascii=False)
        for tid, m in name_hits(text):
            edges.append(_edge(jid, tid, "needs", f"backlog:{r['id']}", m, "row-cite"))
        if env_word:
            for m in env_word.finditer(text):
                edges.append(_edge(jid, f"dep:env:{m.group(1)}", "needs", f"backlog:{r['id']}", m.group(1), "row-cite"))
        if npm_re:
            for m in npm_re.finditer(text):
                edges.append(_edge(jid, f"dep:npm:{m.group(1)}", "needs", f"backlog:{r['id']}", m.group(1), "row-cite"))

    # file-level rules over every tool file
    cache = {}
    py_mod = {}
    for p, tids in by_path.items():
        if p.endswith(".py") and os.path.dirname(p) in ("scripts", "operators"):
            py_mod.setdefault(os.path.splitext(os.path.basename(p))[0], []).append((os.path.dirname(p), tids))
    svc = {s: re.compile(rx) for s, (_, rx) in SERVICES.items()}
    for p, tids in sorted(by_path.items()):
        L = _read(root, p, cache)
        if L is None:
            continue
        code = p.endswith(CODE_EXT)
        for i, line in enumerate(L):
            ev = f"{p}:{i + 1}"
            if run_re and p not in CITE_NOISE and not CITE_DIRECTION.search(line):
                for m in run_paths(line, p, run_re):
                    if m.group(1) == p:
                        continue
                    for fr in tids:
                        for to in by_path[m.group(1)]:
                            # a script naming a surface is its generator or its gate, never written against it
                            if fr.startswith(("tool:script:", "tool:operator:")) and to.startswith("tool:surface:"):
                                continue
                            if to != fr:
                                edges.append(_edge(fr, to, "design-dep", ev, m.group(1), "cite"))
            if not code:
                continue
            if p.endswith(".py"):
                m = PY_IMP.match(line)
                if m:
                    mods = [m.group(1)] if m.group(1) else [x.strip() for x in m.group(2).split(",")]
                    for mod in mods:
                        leaf = mod.split(".")[-1] if mod.startswith(("scripts.", "operators.")) else mod
                        cands = py_mod.get(leaf, [])
                        same = [c for c in cands if c[0] == os.path.dirname(p)] or (cands if len(cands) == 1 else [])
                        for _, to_ids in same:
                            for fr in tids:
                                for to in to_ids:
                                    if to != fr:
                                        edges.append(_edge(fr, to, "design-dep", f"import:{ev}", leaf, "py-import"))
            else:
                for m in JS_IMP.finditer(line):
                    spec = m.group(1)
                    pkg = "/".join(spec.split("/")[:2]) if spec.startswith("@") else spec.split("/")[0]
                    if pkg in npm_names:
                        for fr in tids:
                            edges.append(_edge(fr, f"dep:npm:{pkg}", "design-dep", f"import:{ev}", spec, "js-import"))
            for m in ENV_RE.finditer(line):
                n = next(g for g in m.groups() if g)
                if n in env_names:
                    for fr in tids:
                        edges.append(_edge(fr, f"dep:env:{n}", "runtime-dep", ev, n, "env-read"))
            for s, rx in svc.items():
                mm = rx.search(line)
                # import-signature services always; CLI/API services (github, vercel, perplexity) only from a set -e shell
                # line with no guard on its logical line. Python subprocess/urlopen calls: failure handling (returncode,
                # try, or-defaults) cannot be settled by the shell, so no mechanical edge (round 2, 7 of 18 failed soft)
                # import signatures only for Python/TS (URL constants are not calls; round 3: slop_eval.py:62)
                hard = s in HARD_SVC and not _soft(L, i)
                if s not in HARD_SVC and p.endswith(".sh"):
                    hard = any(l.strip().startswith("set -e") for l in L[:20]) and not SOFT_SH.search(_logical(L, i))
                if mm and hard:
                    for fr in tids:
                        edges.append(_edge(fr, f"dep:service:{s}", "runtime-dep", ev, mm.group(0).strip(), "service"))
    # judgment residue (hand pass), committed
    ip = os.path.join(root, INFERRED)
    if os.path.isfile(ip):
        for e in json.load(open(ip))["edges"]:
            edges.append(dict(e, inferred=True))
    # one edge per (from, to, type): keep the first evidence
    out, seen = [], set()
    for e in edges:
        t = (e["from"], e["to"], e["type"])
        if t not in seen:
            seen.add(t); out.append(e)
    return out


def _evidence_text(root, item, rows_by, cache):
    """Return the text an evidence item points at, or None if it does not resolve."""
    if item.startswith("route.tool:"):
        r = rows_by.get(item[11:])
        return ((r[1].get("route") or {}).get("tool") or "") if r else None
    if item.startswith("backlog:"):
        r = rows_by.get(item[8:])
        if not r:
            return None
        L = _read(root, BACKLOG, cache)
        return L[r[0] - 1] if L and 0 < r[0] <= len(L) else None
    if item.startswith("import:"):
        item = item[7:]
    m = re.fullmatch(r"(.+):([1-9][0-9]*)", item)
    if not m:
        return None
    L = _read(root, m.group(1), cache)
    n = int(m.group(2))
    return L[n - 1] if L and n <= len(L) else None


def verify_edges(graph, root, rows):
    """Reopen every evidence item: it must resolve, and the first item must contain the edge's match."""
    rows_by = {r["id"]: (ln, r) for ln, r in rows}
    cache, bad = {}, []
    for e in graph["edges"]:
        tag = f"{e['from']} -{e['type']}-> {e['to']}"
        texts = [_evidence_text(root, it, rows_by, cache) for it in e["evidence"]]
        if any(t is None for t in texts):
            bad.append((tag, "evidence does not resolve", e["evidence"])); continue
        m = e.get("match")
        if not m:
            bad.append((tag, "no match text to verify", e["evidence"])); continue
        if m not in texts[0] and json.dumps(m)[1:-1] not in texts[0]:
            bad.append((tag, f"match {m!r} not at evidence", e["evidence"][0]))
            continue
        if e["evidence"][0].startswith("import:") and not re.search(r"\bimport\b|\brequire\(|\bfrom\b", texts[0]):
            bad.append((tag, "import evidence line is not an import", e["evidence"][0]))
    return bad


def cycles(graph, types=("needs", "runtime-dep", "design-dep")):
    """Tarjan SCC per edge type; every strongly connected component of size > 1 is a cycle. Reported, never broken."""
    found = {}
    for t in types:
        adj = {}
        for e in graph["edges"]:
            if e["type"] == t:
                adj.setdefault(e["from"], []).append(e["to"])
        idx, low, on, st, comps, n = {}, {}, set(), [], [], [0]
        for root_v in sorted(adj):
            if root_v in idx:
                continue
            work = [(root_v, 0)]
            while work:
                v, i = work.pop()
                if i == 0:
                    idx[v] = low[v] = n[0]; n[0] += 1; st.append(v); on.add(v)
                nb = adj.get(v, [])
                if i < len(nb):
                    work.append((v, i + 1))
                    w = nb[i]
                    if w not in idx:
                        work.append((w, 0))
                    elif w in on:
                        low[v] = min(low[v], idx[w])
                    continue
                if low[v] == idx[v]:
                    c = []
                    while True:
                        w = st.pop(); on.discard(w); c.append(w)
                        if w == v:
                            break
                    if len(c) > 1:
                        comps.append(sorted(c))
                if work:
                    p = work[-1][0]
                    low[p] = min(low[p], low[v])
        found[t] = sorted(comps)
    return found
