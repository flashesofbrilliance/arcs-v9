#!/usr/bin/env python3
"""jtbd_graph_gates: the six Sprint 3 integrity rules over the JTBD graph (row jtbd-graph-s3-gates, ADR-089).

Rules (defined in _PATTERNS/2026-10-19-jtbd-graph-preregistration-amendment-5.md; zero tolerance, no threshold):
  ORPHAN-TOOL           a tool whose live component holds no job
  ORPHAN-JOB            a job whose live component holds no tool and no dep
  BLOCKER-NO-RESOLVE-BY a blocker atom without a real YYYY-MM-DD resolve_by
  DEP-CYCLE             a cycle over needs + runtime-dep + design-dep (mixed types, inferred edges and self-loops count)
  DEAD-FILE-REF         an atom path, source catalog file, edge evidence file:line or probe that does not resolve
  RUNTIME-DEP-NO-PROBE  a runtime-dep target with no resolving health probe in runtime/specs/jtbd-graph-probes.json

A "live" edge: known type, legal kind pair, from != to, both endpoints are atoms, evidence a non-empty list whose
every item matches a format allowed for that type. blocks edges never attach anything (being blocked is not use).

Known violations on main sit in runtime/specs/jtbd-graph-gate-baseline.json (a ratchet Zach approves): a held id
passes, a new id fails, and a held id that no longer violates fails as STALE-BASELINE so the list only shrinks.

  python3 scripts/jtbd_graph_gates.py --self-test       # each rule: good fixture passes, bad fixture fails
  python3 scripts/jtbd_graph_gates.py --mutation-proof  # each rule disabled in turn: the self-test must FAIL
The gate itself runs from `python3 scripts/universe_jtbd_adapter.py --check`. Stdlib only.
"""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import jtbd_graph_schema_check as gc

SCHEMA = "runtime/specs/jtbd-graph-schema.json"
PROBES = "runtime/specs/jtbd-graph-probes.json"
BASELINE = "runtime/specs/jtbd-graph-gate-baseline.json"
FIX = "runtime/specs/fixtures/jtbd-graph/gates"
MEM_PREFIX = "memory/"
DEP_TYPES = ("needs", "runtime-dep", "design-dep")
ATTACH_TYPES = ("serves", "needs", "design-dep", "runtime-dep")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
FILE_EV = ("file_line", "import")
BACKLOG = "_QUEUE/induced-backlog.jsonl"
CODE_EXT = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".py", ".sh")  # a probe is code; docs, data and markup are not
FIXTURE_TODAY = datetime.date(2026, 10, 20)  # fixtures carry literal dates; pin their clock so the self-test cannot expire
HORIZON_DAYS = 366  # a resolve_by further out than this is a sentinel, not a date (skeptic round 1, class D)
FLOOR_DATE = datetime.date(2020, 1, 1)
# a service probe line must name the service by one of these words (skeptic round 1, class J)
SERVICE_WORDS = {"anthropic": ("anthropic",), "database": ("prisma", "supabase", "psycopg", "database", "postgres"),
                 "resend": ("resend",), "github": ("github",), "vercel": ("vercel",), "perplexity-mcp": ("perplexity",)}


class Ctx:
    def __init__(self, root=REPO, probes=None, mem_dir=None, fixture_probes=False):
        self.root, self.mem_dir, self.fixture_probes = root, mem_dir, fixture_probes
        self.schema = json.load(open(os.path.join(REPO, SCHEMA)))
        self.fmts = {k: re.compile(v) for k, v in self.schema["evidence_formats"].items()}
        self.probes = probes if probes is not None else _load(os.path.join(root, PROBES), {}).get("probes", {})
        self.today = FIXTURE_TODAY if fixture_probes else datetime.date.today()
        self._rows = None

    def rows(self):
        """backlog row id -> raw line"""
        if self._rows is None:
            self._rows = {}
            try:
                for l in open(os.path.join(self.root, BACKLOG), encoding="utf-8"):
                    if l.strip():
                        try:
                            self._rows[json.loads(l).get("id")] = l
                        except ValueError:
                            pass
            except OSError:
                pass
        return self._rows

    def row_ids(self):
        return set(self.rows())


def _load(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def _ev_kind(ctx, et, item):
    return next((f for f in ctx.schema["edge_types"][et]["evidence"] if ctx.fmts[f].fullmatch(str(item))), None)


def _ev_resolves(ctx, et, item):
    """Evidence counts for attachment only if it points at something real (skeptic round 1, class A).
    commit evidence cannot be resolved offline, so it never attaches; receipt evidence attaches only through the
    committed MCP receipt projection (amendment 8)."""
    k = _ev_kind(ctx, et, item)
    if k in FILE_EV:
        rel, ln = str(item).split(":", 1)[1].rsplit(":", 1) if k == "import" else str(item).rsplit(":", 1)
        return _line_ok(ctx, rel, int(ln))
    if k in ("backlog_row", "route_tool"):
        return str(item).split(":", 1)[1] in ctx.row_ids()
    if k == "receipt" and "RECEIPT-EV" in DISABLED:  # mutation proof only: any well-formed receipt id resolves
        return True
    if k == "receipt":  # amendment 8: resolves only when the id is on a line of the committed MCP receipt projection
        import jtbd_graph_edges as ge
        return ge.receipt_line(ctx.root, str(item).split(":", 1)[1]) is not None
    return False


def _ev_text(ctx, et, item):
    k = _ev_kind(ctx, et, item)
    if k in FILE_EV:
        rel, ln = str(item).split(":", 1)[1].rsplit(":", 1) if k == "import" else str(item).rsplit(":", 1)
        if not _line_ok(ctx, rel, int(ln)):
            return None
        return open(_resolve(ctx, rel), encoding="utf-8", errors="replace").read().split("\n")[int(ln) - 1]
    if k in ("backlog_row", "route_tool"):
        return ctx.rows().get(str(item).split(":", 1)[1])
    return None


def _names(a):
    """The strings that name an atom: its natural key, its path and the path's file name."""
    out = {str((a.get("source") or {}).get("key") or "")}
    if isinstance(a.get("path"), str):
        out |= {a["path"], os.path.basename(a["path"])}
    return {x for x in out if len(x) >= 3}


def _about(ctx, e, by):
    """Round 2 class 1: evidence that merely resolves is not enough. The edge's match text must sit on the first
    evidence item, and the match must name one of the edge's endpoints (key, path or file name)."""
    m = e.get("match")
    if not isinstance(m, str) or len(m.strip()) < 3:
        return False
    t = _ev_text(ctx, e["type"], e["evidence"][0])
    if t is None or (m not in t and json.dumps(m)[1:-1] not in t):
        return False
    ml = m.lower()
    return any(n.lower() in ml or ml.strip('"/`') in n.lower() for x in (e["from"], e["to"]) for n in _names(by[x]))


def _receipts_name_edge(ctx, e):
    """Amendment 9: every receipt:<id> item must sit on a projection line naming this edge's own tool and job."""
    import jtbd_graph_edges as ge
    rids = [str(x)[8:] for x in e["evidence"] if str(x).startswith("receipt:")]
    if str(e.get("from", "")).startswith(MCP_INDEX_PREFIX) and not rids:
        return False  # round 2 skeptic: an MCP edge with no receipt item never attaches (amendment 8 rule (d))
    return all(ge.receipt_line(ctx.root, r, tool=e["from"], job=e["to"]) is not None for r in rids)


def live_edges(graph, ctx):
    by = {a["id"]: a for a in graph.get("atoms", [])}
    kind = {i: a.get("kind") for i, a in by.items()}
    out = []
    for e in graph.get("edges", []):
        et = ctx.schema["edge_types"].get(e.get("type"))
        f, t, ev = e.get("from"), e.get("to"), e.get("evidence")
        if not et or f == t or f not in kind or t not in kind or [kind[f], kind[t]] not in et["pairs"]:
            continue
        if not isinstance(ev, list) or not ev or not all(_ev_resolves(ctx, e["type"], x) for x in ev):
            continue
        if "RECEIPT-EV" not in DISABLED and not _receipts_name_edge(ctx, e):
            continue
        if not _about(ctx, e, by):
            continue
        out.append(e)
    return out


def _components(graph, ctx):
    parent = {a["id"]: a["id"] for a in graph.get("atoms", [])}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    kind = {a["id"]: a.get("kind") for a in graph.get("atoms", [])}
    for e in live_edges(graph, ctx):
        # deps never carry attachment: two tools sharing an env var are not linked by it, and a job that
        # only needs a dep has no tool doing it (skeptic round 1, classes B and C)
        if e["type"] in ATTACH_TYPES and "dep" not in (kind[e["from"]], kind[e["to"]]):
            parent[find(e["from"])] = find(e["to"])
    comp = {}
    for a in graph.get("atoms", []):
        comp.setdefault(find(a["id"]), set()).add(a.get("kind"))
    return {a["id"]: comp[find(a["id"])] for a in graph.get("atoms", [])}


MCP_INDEX_PREFIX = "tool:mcp:"  # amendment 8 rule (d): index entries, not owned tools; exempt from ORPHAN-TOOL only


def orphan_tool(graph, ctx):
    c = _components(graph, ctx)
    return [(a["id"], "no job reachable over serves/needs/design-dep/runtime-dep between tools and jobs")
            for a in graph.get("atoms", []) if a.get("kind") == "tool" and "job" not in c[a["id"]]
            and not ("ORPHAN-TOOL:mcp" not in DISABLED and a["id"].startswith(MCP_INDEX_PREFIX))]


def orphan_job(graph, ctx):
    c = _components(graph, ctx)
    return [(a["id"], "no tool reachable over serves/needs/design-dep/runtime-dep between tools and jobs")
            for a in graph.get("atoms", []) if a.get("kind") == "job" and "tool" not in c[a["id"]]]


def blocker_no_resolve_by(graph, ctx):
    out = []
    for a in graph.get("atoms", []):
        if a.get("kind") != "blocker":
            continue
        rb = a.get("resolve_by")
        ok = isinstance(rb, str) and DATE_RE.fullmatch(rb)
        if ok:
            try:
                d = datetime.date.fromisoformat(rb)
                # round 2 class 2: a date already past is lapsed, not a plan; the blocker needs a new date
                ok = ctx.today <= d <= ctx.today + datetime.timedelta(days=HORIZON_DAYS)
            except ValueError:
                ok = False
        if not ok:
            out.append((a["id"], f"resolve_by {rb!r} is not a YYYY-MM-DD date from today to today + {HORIZON_DAYS} days"))
    return out


def dep_cycle(graph, ctx):
    ids = {a["id"] for a in graph.get("atoms", [])}
    adj, out = {}, []
    for e in graph.get("edges", []):
        if e.get("type") not in DEP_TYPES or e.get("from") not in ids or e.get("to") not in ids:
            continue
        if e["from"] == e["to"]:
            out.append((e["from"], f"self-loop {e['type']}"))
        adj.setdefault(e["from"], set()).add(e["to"])
    idx, low, on, st, n = {}, {}, set(), [], [0]
    for r in sorted(adj):
        if r in idx:
            continue
        work = [(r, iter(sorted(adj.get(r, ()))))]
        idx[r] = low[r] = n[0]; n[0] += 1; st.append(r); on.add(r)
        while work:
            v, it = work[-1]
            w = next(it, None)
            if w is not None:
                if w not in idx:
                    idx[w] = low[w] = n[0]; n[0] += 1; st.append(w); on.add(w)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                elif w in on:
                    low[v] = min(low[v], idx[w])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == idx[v]:
                comp = []
                while True:
                    x = st.pop(); on.discard(x); comp.append(x)
                    if x == v:
                        break
                if len(comp) > 1:
                    out.append((min(comp), "cycle " + " <-> ".join(sorted(comp))))
    return out


def _resolve(ctx, rel):
    """Repo-relative path -> absolute path inside the root, or None if it escapes or is absolute."""
    if not isinstance(rel, str) or not rel or os.path.isabs(rel) or rel.startswith("~"):
        return None
    p = os.path.realpath(os.path.join(ctx.root, rel))
    root = os.path.realpath(ctx.root)
    return p if p == root or p.startswith(root + os.sep) else None


def _line_ok(ctx, rel, ln):
    p = _resolve(ctx, rel)
    if not p or not os.path.isfile(p):
        return False
    try:
        n = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
    except OSError:
        return False
    return isinstance(ln, int) and not isinstance(ln, bool) and 1 <= ln <= n


def dead_file_ref(graph, ctx):
    out = []
    for a in graph.get("atoms", []):
        path = a.get("path")
        if path is not None:
            if isinstance(path, str) and path.startswith(MEM_PREFIX):
                # fail closed: a memory ref with no memory dir to check it against is unresolved (class F)
                rest = path[len(MEM_PREFIX):]
                if not ctx.mem_dir or "/" in rest or not os.path.isfile(os.path.join(ctx.mem_dir, rest)):
                    out.append((a["id"], f"memory file {path} not resolvable here"))
            elif not (_resolve(ctx, path) and os.path.isfile(_resolve(ctx, path))):  # a directory is not a file (class E)
                out.append((a["id"], f"path {path!r} does not resolve"))
        cat = (a.get("source") or {}).get("catalog")
        if isinstance(cat, str) and " " not in cat and "*" not in cat and not cat.startswith("~"):
            if not _line_ok(ctx, cat, (a.get("source") or {}).get("line")):
                out.append((a["id"], f"source {cat}:{(a.get('source') or {}).get('line')} does not resolve"))
    for e in graph.get("edges", []):
        if e.get("type") not in ctx.schema["edge_types"] or not isinstance(e.get("evidence"), list):
            continue
        for item in e["evidence"]:
            k = _ev_kind(ctx, e["type"], item)
            if k in FILE_EV:
                rel, ln = str(item).split(":", 1)[1].rsplit(":", 1) if k == "import" else str(item).rsplit(":", 1)
                if not _line_ok(ctx, rel, int(ln)):
                    out.append((e.get("from"), f"evidence {item} on {e.get('type')} -> {e.get('to')} does not resolve"))
    for dep, p in sorted(ctx.probes.items()):
        if not isinstance(p, dict) or not _line_ok(ctx, p.get("file"), p.get("line")):
            out.append((dep, f"probe {p!r} does not resolve"))
    return out


STR_RE = re.compile(r"""("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)""")
CALL_RE = re.compile(r"\bawait\b|\bcurl\b|[\w$\]\)]\s*\(|\$queryRaw")


def _code_part(line, ext):
    """The line with comments removed (string contents kept). Only full-line and trailing comments."""
    s = re.sub(r"/\*.*?\*/", " ", line)
    if s.lstrip().startswith(("/*", "*", "//", "#")):
        return ""
    out, i = [], 0
    for m in STR_RE.finditer(s):  # cut a trailing comment that starts outside any string
        seg = s[i:m.start()]
        cut = re.search(r"//" if ext not in (".py", ".sh") else r"#", seg)
        if cut:
            return "".join(out) + seg[:cut.start()]
        out.append(seg + m.group(0)); i = m.end()
    seg = s[i:]
    cut = re.search(r"//" if ext not in (".py", ".sh") else r"#", seg)
    return "".join(out) + (seg[:cut.start()] if cut else seg)


def _live_lines(text, ext):
    """Per line: False when the line starts inside a multi-line /* */ comment or a Python triple-quoted string.
    Round 2 class 4: comment state carries across lines."""
    out, inside = [], None
    for line in text.split("\n"):
        out.append(inside is None)
        i = 0
        while i < len(line):
            if inside is None:
                if ext not in (".py", ".sh") and line.startswith("/*", i):
                    inside, i = "*/", i + 2; continue
                if ext == ".py" and line.startswith(('"""', "'''"), i):
                    inside, i = line[i:i + 3], i + 3; continue
                if (ext in (".py", ".sh") and line[i] == "#") or (ext not in (".py", ".sh") and line.startswith("//", i)):
                    break
                i += 1
            else:
                j = line.find(inside, i)
                if j < 0:
                    break
                i, inside = j + len(inside), None
    return out


def _word(w, text):
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])", text, re.I) is not None


def _probe_ok(ctx, dep, p):
    if not isinstance(p, dict):
        return False
    f, ln, m = p.get("file"), p.get("line"), p.get("match")
    if not isinstance(m, str) or not m.strip() or not _line_ok(ctx, f, ln):
        return False
    ext = os.path.splitext(f)[1]
    if ext not in CODE_EXT or (f.startswith(FIX) and not ctx.fixture_probes) or f == PROBES:
        return False  # classes I: only code files probe, case-sensitive allowlist
    text = open(_resolve(ctx, f), encoding="utf-8", errors="replace").read()
    if not _live_lines(text, ext)[ln - 1]:
        return False
    code = _code_part(text.split("\n")[ln - 1], ext)
    bare = STR_RE.sub('""', code)  # round 2 class 3: the dep must be named in code, not inside a string literal
    if m not in code:
        return False  # class G: a needle in a comment does not probe
    if not CALL_RE.search(STR_RE.sub('""', code)):
        return False  # class G: a line that only holds a string does nothing; a probe line calls or awaits
    key = dep.split(":", 2)[2] if dep.count(":") >= 2 else ""
    if dep.startswith("dep:env:"):
        return re.search(r"(?<![A-Za-z0-9_])" + re.escape(key) + r"(?![A-Za-z0-9_])", bare) is not None  # class H
    words = SERVICE_WORDS.get(key, (key,))
    return any(_word(w, bare) for w in words)  # class J: the line names the service


def runtime_dep_no_probe(graph, ctx):
    """One finding per runtime-dep edge (not per target), so holding a target in the baseline cannot hide a new
    caller of it (skeptic round 1, class N)."""
    ids = {a["id"] for a in graph.get("atoms", [])}
    pairs = sorted({(e["to"], e["from"]) for e in graph.get("edges", []) if e.get("type") == "runtime-dep"
                    and e.get("to") in ids and e.get("from") in ids and e.get("from") != e.get("to")})
    ok = {}
    return [(f"{t} <- {f}", "no resolving health probe") for t, f in pairs
            if not ok.setdefault(t, _probe_ok(ctx, t, ctx.probes.get(t)))]


RULES = {
    "ORPHAN-TOOL": orphan_tool,
    "ORPHAN-JOB": orphan_job,
    "BLOCKER-NO-RESOLVE-BY": blocker_no_resolve_by,
    "DEP-CYCLE": dep_cycle,
    "DEAD-FILE-REF": dead_file_ref,
    "RUNTIME-DEP-NO-PROBE": runtime_dep_no_probe,
}
DISABLED = set()  # mutation proof only


def run_rules(graph, ctx):
    return {r: ([] if r in DISABLED else sorted(set(fn(graph, ctx)))) for r, fn in RULES.items()}


def apply_baseline(found, baseline):
    """-> (new, held, stale). held ids pass; a held id that no longer violates is stale and fails."""
    new, held, stale = {}, {}, {}
    for r, items in found.items():
        allow = set(baseline.get(r, []))
        hit = {i for i, _ in items}
        new[r] = [(i, d) for i, d in items if i not in allow]
        held[r] = sorted(hit & allow)
        stale[r] = sorted(allow - hit)
    for r in baseline:
        if r not in found:
            stale[r] = sorted(baseline[r])
    return new, held, stale


TRIAGE = "runtime/specs/jtbd-graph-triage.json"
TRIAGE_MAX_DAYS = 14


def apply_triage(new, triage, today, rows=None):
    """Time-boxed holds for NEW findings (the baseline only holds old debt and may only shrink).
    An entry {rule, id, reason, row, added, resolve_by} passes its finding until resolve_by, then fails TRIAGE-EXPIRED.
    It must name a backlog row (when rows is given), carry a reason, and resolve within TRIAGE_MAX_DAYS of added;
    an entry whose finding is gone fails TRIAGE-STALE so the file is cleaned up. -> (new, triaged, problems)"""
    import datetime as _dt
    out = {r: list(v) for r, v in new.items()}
    triaged, problems = [], []
    for e in triage:
        r, i = e.get("rule"), e.get("id")
        try:
            added = _dt.date.fromisoformat(e.get("added", "")); due = _dt.date.fromisoformat(e.get("resolve_by", ""))
        except ValueError:
            problems.append(f"TRIAGE-INVALID {r} {i}: added and resolve_by must be YYYY-MM-DD"); continue
        if not e.get("reason") or not e.get("row"):
            problems.append(f"TRIAGE-INVALID {r} {i}: needs a reason and a backlog row"); continue
        if rows is not None and e["row"] not in rows:
            problems.append(f"TRIAGE-INVALID {r} {i}: row {e['row']!r} is not in the backlog"); continue
        if (due - added).days > TRIAGE_MAX_DAYS:
            problems.append(f"TRIAGE-INVALID {r} {i}: resolve_by is more than {TRIAGE_MAX_DAYS} days after added"); continue
        hit = [x for x in out.get(r, []) if x[0] == i]
        if not hit:
            problems.append(f"TRIAGE-STALE {r} {i}: no longer a new finding; remove it from {TRIAGE}"); continue
        if today > due:
            problems.append(f"TRIAGE-EXPIRED {r} {i}: resolve_by {due} has passed (row {e['row']})"); continue
        out[r] = [x for x in out[r] if x[0] != i]
        triaged.append((r, i, str(due)))
    return out, triaged, problems


def self_test(verbose=True, missed=None):
    ok = True
    fixdir = os.path.join(REPO, FIX)
    for rule in RULES:
        stem = rule.lower()
        for side in ("good", "bad"):
            g = json.load(open(os.path.join(fixdir, f"{stem}.{side}.json")))
            ctx = Ctx(REPO, probes=g.get("probes", {}), fixture_probes=True)
            found = run_rules(g, ctx)
            if side == "good":
                hit = {r: v for r, v in found.items() if v}
                good = not hit
                if verbose:
                    print(f"{stem}.good.json: {'PASS' if good else 'FAIL'}" + ("" if good else f" {hit}"))
                ok &= good
            else:
                want = set(g["_expect_ids"])
                got = {i for i, _ in found[rule]}
                caught = want <= got
                if verbose:
                    print(f"{stem}.bad.json: {'caught' if caught else 'MISSED'} {rule} ({len(want & got)}/{len(want)} expected ids"
                          + ("" if caught else f"; missed {sorted(want - got)}") + ")")
                ok &= caught
                if missed is not None and not caught:
                    missed.add(rule)
    # the baseline ratchet: a held id passes, a new id fails, a fixed held id is stale
    g = json.load(open(os.path.join(fixdir, "orphan-tool.bad.json")))
    found = run_rules(g, Ctx(REPO, probes=g.get("probes", {}), fixture_probes=True))
    ids = [i for i, _ in found["ORPHAN-TOOL"]]
    n1, _, s1 = apply_baseline(found, {"ORPHAN-TOOL": ids})
    n2, _, _ = apply_baseline(found, {"ORPHAN-TOOL": ids[1:]})
    _, _, s3 = apply_baseline(found, {"ORPHAN-TOOL": ids + ["tool:script:fixed-long-ago.py"]})
    rat = (not n1["ORPHAN-TOOL"] and not s1["ORPHAN-TOOL"] and bool(n2["ORPHAN-TOOL"]) and s3["ORPHAN-TOOL"] == ["tool:script:fixed-long-ago.py"])
    if verbose:
        print(f"baseline ratchet (held passes, new fails, stale fails): {'ok' if rat else 'WRONG'}")
    ok &= rat
    # the triage file: a dated hold passes until resolve_by, then fails; no row, too long, or stale all fail
    import datetime as _dt
    d0 = _dt.date(2026, 10, 20); tid = "tool:script:triage-fixture.py"  # fixed id: independent of any rule's output
    e = {"rule": "ORPHAN-TOOL", "id": tid, "reason": "fixture", "row": "row-a", "added": "2026-10-20", "resolve_by": "2026-10-27"}
    n_ok, t_ok, p_ok = apply_triage({"ORPHAN-TOOL": [(tid, "x")]}, [e], d0, {"row-a"})
    held_ok = not p_ok and not any(x[0] == tid for x in n_ok["ORPHAN-TOOL"])
    _, _, p_exp = apply_triage({"ORPHAN-TOOL": [(tid, "x")]}, [e], d0 + _dt.timedelta(days=8), {"row-a"})
    _, _, p_row = apply_triage({"ORPHAN-TOOL": [(tid, "x")]}, [dict(e, row="no-such-row")], d0, {"row-a"})
    _, _, p_long = apply_triage({"ORPHAN-TOOL": [(tid, "x")]}, [dict(e, resolve_by="2026-12-31")], d0, {"row-a"})
    _, _, p_stale = apply_triage({"ORPHAN-TOOL": []}, [e], d0, {"row-a"})
    tri = (held_ok and any(x.startswith("TRIAGE-EXPIRED") for x in p_exp) and any(x.startswith("TRIAGE-INVALID") for x in p_row)
           and any(x.startswith("TRIAGE-INVALID") for x in p_long) and any(x.startswith("TRIAGE-STALE") for x in p_stale))
    if verbose:
        print(f"triage holds (dated hold passes; expired, rowless, too long and stale all fail): {'ok' if tri else 'WRONG'}")
    ok &= tri
    m = mcp_self_test()
    if verbose:
        print(f"mcp index (unused index tool not orphan; receipt on file attaches; forged receipt does not): {'ok' if m else 'WRONG'}")
    ok &= m
    if verbose:
        print("gates self-test OK" if ok else "gates self-test FAILED")
    return ok


def mcp_self_test():
    """Amendment 8: tool:mcp atoms are exempt from ORPHAN-TOOL; a job attaches to one only over a serves edge whose
    receipt id is on a line of the committed projection. A name-only or forged-receipt edge leaves the job an orphan."""
    import tempfile, jtbd_graph_edges as ge
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "runtime/specs"))
        line = json.dumps({"receipt_id": "r-ok--ZH", "job_id": "job:backlog:j1", "tool_id": "tool:mcp:s.apply"})
        open(os.path.join(tmp, ge.MCP_RECEIPTS), "w").write(line + "\n")
        A = lambda i, k, key: {"id": i, "kind": k, "source": {"catalog": "x", "key": key, "line": 1}}
        ev = lambda rid: [f"{ge.MCP_RECEIPTS}:1", f"receipt:{rid}"]
        g = {"atoms": [A("tool:mcp:s.apply", "tool", "s.apply"), A("tool:mcp:s.unused", "tool", "s.unused"),
                       A("job:backlog:j1", "job", "j1"), A("job:backlog:j2", "job", "j2"), A("job:backlog:j3", "job", "j3"), A("job:backlog:j4", "job", "j4"), A("job:backlog:j5", "job", "j5")],
             "edges": [{"from": "tool:mcp:s.apply", "to": "job:backlog:j1", "type": "serves", "evidence": ev("r-ok--ZH"),
                        "inferred": False, "match": "s.apply"},
                       {"from": "tool:mcp:s.apply", "to": "job:backlog:j2", "type": "serves", "evidence": ev("r-forged--ZH"),
                        "inferred": False, "match": "s.apply"},
                       {"from": "tool:mcp:s.apply", "to": "job:backlog:j3", "type": "serves", "evidence": ["receipt:r-ok--ZH"],
                        "inferred": False, "match": "j3"},
                       {"from": "tool:mcp:s.apply", "to": "job:backlog:j4", "type": "serves", "evidence": ev("r-ok--ZH"),
                        "inferred": False, "match": "s.apply"},  # round 1 skeptic: a real receipt for j1 reused for j4
                       {"from": "tool:mcp:s.apply", "to": "job:backlog:j5", "type": "serves", "evidence": [f"{ge.MCP_RECEIPTS}:1"],
                        "inferred": False, "match": "s.apply"}]}  # round 2 skeptic: no receipt item at all
        found = run_rules(g, Ctx(tmp, probes={}))
    ot = {i for i, _ in found["ORPHAN-TOOL"]}; oj = {i for i, _ in found["ORPHAN-JOB"]}
    return ot == set() and oj == {"job:backlog:j2", "job:backlog:j3", "job:backlog:j4", "job:backlog:j5"}


def mutation_proof():
    ok = self_test(verbose=False)  # the unmutated self-test must pass first, or every mutation 'fails' vacuously
    print(f"unmutated self-test: {'PASS' if ok else 'FAIL'}")
    for rule in list(RULES):
        DISABLED.clear(); DISABLED.add(rule)
        missed = set()
        survived = self_test(verbose=False, missed=missed)
        # the proof holds only if the self-test fails AND it fails on this rule's own bad fixture
        good = not survived and missed == {rule}
        print(f"mutation: {rule} disabled -> self-test {'PASSED' if survived else 'FAILED'}, missed {sorted(missed)}: {'proof ok' if good else 'PROOF FAILS'}")
        ok &= good
    DISABLED.clear()
    for mut in ("ORPHAN-TOOL:mcp", "RECEIPT-EV"):  # amendment 8 mutations: the mcp self-test must catch each
        DISABLED.add(mut)
        caught = not mcp_self_test()
        DISABLED.discard(mut)
        print(f"mutation: {mut} disabled -> mcp self-test {'FAILED' if caught else 'PASSED'}: {'proof ok' if caught else 'PROOF FAILS'}")
        ok &= caught
    print("gates mutation proof OK" if ok else "gates mutation proof FAILED")
    return ok


def main(argv):
    if "--self-test" in argv:
        return 0 if self_test() else 1
    if "--mutation-proof" in argv:
        return 0 if mutation_proof() else 1
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
