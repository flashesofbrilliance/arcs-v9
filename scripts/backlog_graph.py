#!/usr/bin/env python3
"""backlog_graph.py: the induced backlog as a computational graph. Read-only, stdlib, no model calls.

Answers four questions in one pass over _QUEUE/induced-backlog.jsonl:
  1 What depends on what?          nodes = rows, edges = depends_on plus the inverse of unblocks
  2 In what order?                 waves (longest-path depth) over the open rows; ties by rank, order, priority, id
  3 What can start now?            wave 0, a startable state, no dead or missing dependency, ripeness RIPE
  4 Do we have the tool for it?    route.tool resolved against the repo and runtime/specs/tool-catalog.json

Labels: HAVE (every named tool resolves), PARTIAL (some do), NOT-RESOLVED (names given, none resolve,
including prose such as "when built"), NONE (no route.tool: human work). It never guesses a tool.

Findings it reports instead of hiding: dangling dependency ids, dependencies on COMPOSTED or SUPERSEDED rows
(dead), cycles, and rows where `unblocks` and `depends_on` disagree (the graph holds the union).
It never changes a row. Fates stay human (NOTOMATION).

Debt (2026-11-02): tech debt lives in GitHub Issues (label debt, hidden debt-id marker; ADR of 2026-10-06 in
backlog_issue_sync.py), not in the backlog file, so the graph could not see it. --debt reads the issues live
(read-only GraphQL through backlog_issue_sync.debt_issues) and --debt-file reads a saved copy of the same JSON.
Each issue becomes node `debt:<debt-id>`: status open -> OPEN, in-progress -> RUNNING, decision -> BLOCKED,
closed or done -> DONE; a `Depends on: <id>, <id>` line in the issue body gives its edges, and a backlog row
can name `debt:<id>` in depends_on. Issues stay the SSOT; nothing is copied into the backlog file.

Three lenses over the same nodes, each standing alone (never blended into one score):
  deps      the default: order, ready now, unblockers, tool fit, findings
  risk      ruin (castellum's scale), door, consent, failure modes, debt severity, how far a slip reaches
            downstream, and which rows sit under a one-way door or a high or critical ruin upstream
  tradeoff  cost band (S, M, L from cost_prior prose) against leverage (rows unblocked downstream)
A lens prints how many rows carry the field it reads; an unrated row is listed as unrated, never guessed.

usage:
  backlog_graph.py [--file F] [--today YYYY-MM-DD] [--gh] [--json] [--dot] [--top N]
                   [--debt | --debt-file F] [--lens deps|risk|tradeoff]
  backlog_graph.py --self-test            pre-registered known-bad and known-good fixtures, no network
PR triggers are not checked unless --gh is given (it calls the gh CLI per PR); the ripeness column then says so.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backlog_ripeness as br  # noqa: E402
import readiness_packet as rp  # noqa: E402

DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
CATALOG = ROOT / "runtime" / "specs" / "tool-catalog.json"
SPEC = ROOT / "runtime" / "specs" / "backlog-status.json"
STARTABLE = {"OPEN", "READY", "HOLDING"}
DEAD = {"COMPOSTED", "SUPERSEDED"}
TOKEN_RE = re.compile(r"(?<![\w/.-])(/[a-z][\w-]*|(?:[\w.-]+/)+[\w.-]+\.\w{1,6}|[\w-]+\.(?:py|mjs|sh|md|json|ts|tsx|html))(?![\w/-])")


def terminal_states():
    try:
        s = json.loads(SPEC.read_text())["states"]
        return {k for k, v in s.items() if v.get("terminal")}
    except (OSError, KeyError, ValueError):
        return {"DONE", "COMPOSTED", "SUPERSEDED"}


def known_tools():
    """Names, paths and slash commands from the catalog, as a set of strings."""
    out = set()
    try:
        for t in json.loads(CATALOG.read_text())["tools"]:
            for k in ("name", "path", "invoke"):
                if t.get(k):
                    out.add(str(t[k]).strip())
                    out.add(Path(str(t[k]).split()[-1]).name)
    except (OSError, KeyError, ValueError):
        pass
    return out


# Claude Code built-in slash commands. They live in the app, not in this repo or the tool catalog, so a row
# that names one (for example /mcp) is not naming a missing tool. The list is conservative and not exhaustive:
# extend it when a row names a built-in, and check /help for the current set. A name that is not here is
# still resolved first against the repo commands, the catalog and the URL routes.
BUILTIN_COMMANDS = {"add-dir", "agents", "clear", "compact", "config", "context", "cost", "doctor", "export", "fast",
                    "help", "hooks", "ide", "init", "login", "logout", "mcp", "memory", "model", "permissions",
                    "plugin", "resume", "status"}
PLANNED_RE = re.compile(r"\b(build|builds|create|creates|add|new|write|mint|draft|emit|generate)\b", re.I)


def repo_files():
    """Tracked repo paths, so a short path such as compass/route.ts can be matched by suffix."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [x for x in out.split("\n") if x]
    except (OSError, subprocess.CalledProcessError):
        return []


def resolve_token(tok, catalog, files):
    """-> (kind, detail). kind: FILE, SUFFIX, AMBIGUOUS, ROUTE, COMMAND, BUILTIN or UNRESOLVED."""
    if tok.startswith("/") and "/" not in tok[1:]:
        name = tok[1:]
        if tok in catalog or (".claude/commands/%s.md" % name) in files:
            return "COMMAND", tok
        if name in BUILTIN_COMMANDS:
            return "BUILTIN", tok
        if any(("/%s/" % name) in f or f.startswith("src/app/%s/" % name) for f in files):
            return "ROUTE", tok
        return "UNRESOLVED", tok
    if tok in files or (ROOT / tok.lstrip("/")).exists():
        return "FILE", tok
    suffix = [f for f in files if f.endswith("/" + tok)]
    if len(suffix) == 1:
        return "SUFFIX", suffix[0]
    if len(suffix) > 1:
        return "AMBIGUOUS", ", ".join(suffix[:3])
    if tok in catalog or Path(tok).name in catalog:
        return "FILE", tok
    return "UNRESOLVED", tok


def resolve_tool(row, catalog, files=None):
    """-> (label, resolved, missing, planned). missing = named but not found and not planned.
    planned = named, not found, and the row says it will build or create it (not stale)."""
    files = files if files is not None else repo_files()
    tool = (row.get("route") or {}).get("tool")
    if not tool:
        return "NONE", [], [], []
    toks = sorted(set(TOKEN_RE.findall(str(tool))))
    if not toks:
        return "NOT-RESOLVED", [], [], []
    ok, miss, planned = [], [], []
    says_build = bool(PLANNED_RE.search(str(row.get("jtbd", "")) + " " + str(row.get("next_action", ""))))
    for t in toks:
        kind, _ = resolve_token(t, catalog, set(files) if not isinstance(files, set) else files)
        if kind == "UNRESOLVED":
            (planned if says_build else miss).append(t)
        else:
            ok.append(t)
    if len(ok) == len(toks):
        return "HAVE", ok, [], []
    return ("PARTIAL" if ok else "NOT-RESOLVED"), ok, miss, planned


def deps_of(row):
    d = row.get("depends_on")
    if not d:
        return []
    if isinstance(d, str):
        d = re.split(r"[,\s]+", d)
    return [str(x).strip() for x in d if str(x).strip()]


def build(rows, today, catalog=None, terminal=None, files=None):
    terminal = terminal if terminal is not None else terminal_states()
    catalog = catalog if catalog is not None else known_tools()
    files = set(files if files is not None else repo_files())
    by_id = {r["id"]: r for r in rows if r.get("id")}
    deps = {i: set(deps_of(r)) for i, r in by_id.items()}
    mismatch = []
    for i, r in by_id.items():
        for u in (r.get("unblocks") or []):
            if u in by_id:
                if i not in deps[u]:
                    mismatch.append(f"{i} unblocks {u} but {u} does not list {i} in depends_on")
                deps[u].add(i)
    state = {i: str(r.get("state") or "OPEN") for i, r in by_id.items()}
    active = {i for i in by_id if state[i] not in terminal}
    dangling = sorted(f"{i} -> {d}" for i in active for d in deps[i] if d not in by_id)
    dead = sorted(f"{i} -> {d} ({state[d]})" for i in active for d in deps[i] if d in by_id and state[d] in DEAD)
    live_deps = {i: {d for d in deps[i] if d in active} for i in active}
    indeg = {i: len(live_deps[i]) for i in active}
    kids = defaultdict(set)
    for i in active:
        for d in live_deps[i]:
            kids[d].add(i)
    wave, q = {}, deque(sorted(i for i in active if indeg[i] == 0))
    for i in q:
        wave[i] = 0
    seen = 0
    while q:
        n = q.popleft()
        seen += 1
        for k in sorted(kids[n]):
            wave[k] = max(wave.get(k, 0), wave[n] + 1)
            indeg[k] -= 1
            if indeg[k] == 0:
                q.append(k)
    cycle = sorted(i for i in active if i not in wave)

    def key(i):
        r = by_id[i]
        return (r.get("rank") if isinstance(r.get("rank"), int) else 99,
                r.get("order") if isinstance(r.get("order"), int) else 99,
                str(r.get("priority") or "P9"), i)

    def descendants(i, memo={}):
        out, stack = set(), [i]
        while stack:
            for k in kids[stack.pop()]:
                if k not in out:
                    out.add(k)
                    stack.append(k)
        return out

    nodes = []
    for i in sorted(active, key=lambda x: (wave.get(x, 999),) + key(x)):
        r = by_id[i]
        v = br.assess(r, by_id, today)
        tool, resolved, missing, planned = resolve_tool(r, catalog, files)
        has_dead = any(d in by_id and state[d] in DEAD for d in deps[i]) or any(d not in by_id for d in deps[i])
        startable = (state[i] in STARTABLE and wave.get(i) == 0 and not has_dead)
        nodes.append({"id": i, "state": state[i], "wave": wave.get(i), "ripeness": v[0] if v else "TERMINAL",
                      "tool": tool, "tool_resolved": resolved, "tool_missing": missing, "tool_planned": planned, "deps": sorted(deps[i]),
                      "descendants": len(descendants(i)), "cost": r.get("cost_prior"),
                      "consent": r.get("consent"),
                      "tier_cue": 4 if (r.get("consent") == "human" or r.get("door") == "one-way" or rp.ONE_WAY.search(rp._text(r))) else 2,
                      "ready_now": bool(startable and v and v[0] == "RIPE")})
    return {"today": str(today), "rows": len(by_id), "active": len(active), "nodes": nodes,
            "findings": {"dangling": dangling, "dead_dependency": dead, "cycle_members": cycle, "unblocks_mismatch": sorted(mismatch)},
            "critical_path_waves": (max(wave.values()) + 1) if wave else 0}


DEBT_STATE = {"open": "OPEN", "in-progress": "RUNNING", "decision": "BLOCKED", "done": "DONE"}
DEBT_MARK_RE = re.compile(r"<!-- debt-id: ([A-Za-z0-9_.\-]+) -->")
DEP_LINE_RE = re.compile(r"^[*_\s]*depends[ _]on[*_.:\s]+(.+)$", re.I | re.M)
REF_RE = re.compile(r"\*\*Ref\.\*\*\s*(.+)")


def debt_to_row(issue):
    """One GitHub debt issue as a read-only graph row, id debt:<debt-id>. None when it has no debt-id marker."""
    body = issue.get("body") or ""
    m = DEBT_MARK_RE.search(body)
    if not m:
        return None
    names = [l.get("name", "") if isinstance(l, dict) else str(l) for l in issue.get("labels") or []]
    sev = next((n[4:] for n in names if n.startswith("sev:")), None)
    st = next((n[7:] for n in names if n.startswith("status:")), "open")
    if issue.get("state") == "CLOSED":
        st = "done"
    deps = []
    for line in DEP_LINE_RE.findall(body):
        deps += [d.strip("`.*_ ") for d in re.split(r"[,;\s]+", line) if d.strip("`.*_ ")]
    row = {"id": "debt:" + m.group(1), "source": "debt", "issue": issue.get("number"), "jtbd": issue.get("title", ""),
           "state": DEBT_STATE.get(st, "OPEN"), "severity": sev, "depends_on": deps}
    ref = REF_RE.search(body)
    if ref:
        row["route"] = {"tool": ref.group(1).strip()}
    if row["state"] == "RUNNING":
        row["claimed_by"] = "issue #%s" % issue.get("number")
    return row


def load_debt(path=None):
    """Debt issues as rows. path: a saved JSON list of issues; None: read them live with gh (read-only)."""
    if path:
        issues = json.loads(Path(path).read_text())
    else:
        import backlog_issue_sync as bis
        issues = bis.debt_issues()
    return [r for r in (debt_to_row(i) for i in issues) if r]


RUIN = {"low": 1, "medium": 2, "high": 4, "critical": 8}  # castellum.py's scale, so the two never disagree
LOUD = {"high", "critical"}


def cost_band(text):
    """S, M or L from cost_prior prose, or None when it gives no size. The cut points are stated, not tuned:
    up to 4 h or 1 session is S, up to 16 h, 2 days or 3 sessions is M, anything larger is L."""
    t = str(text or "").lower()
    if not t or "tbd" in t or "container" in t:
        return None
    for w, b in (("small", "S"), ("medium", "M"), ("large", "L")):
        if re.search(r"\b%s\b" % w, t):
            return b
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", t)]
    if not nums:
        return None
    n = max(nums)
    if re.search(r"\bmin", t):
        return "S" if n <= 240 else "M"
    if re.search(r"\bsessions?\b", t):
        return "S" if n <= 1 else "M" if n <= 3 else "L"
    if re.search(r"\b(w|wk|weeks?)\b", t):
        return "L"
    if re.search(r"\b(d|days?)\b", t):
        return "M" if n <= 2 else "L"
    if re.search(r"\b(h|hrs?|hours?)\b", t):
        return "S" if n <= 4 else "M" if n <= 16 else "L"
    return None


def _ancestors(g):
    parents = {x["id"]: [d for d in x["deps"]] for x in g["nodes"]}
    memo = {}

    def up(i):
        if i in memo:
            return memo[i]
        memo[i] = set()
        out = set()
        for p in parents.get(i, []):
            if p in parents:
                out.add(p)
                out |= up(p)
        memo[i] = out
        return out
    return {i: up(i) for i in parents}


def risk_lens(g, rows):
    """Per active node: its own risk fields, how far a slip reaches, and the risky rows upstream of it."""
    by_id = {r["id"]: r for r in rows if r.get("id")}
    anc = _ancestors(g)
    own, loud = {}, set()
    for x in g["nodes"]:
        r = by_id.get(x["id"], {})
        ruin = str(r.get("ruin") or "").lower() or None
        fm = r.get("failure_modes")
        own[x["id"]] = {"id": x["id"], "ruin": ruin if ruin in RUIN else None, "door": r.get("door"),
                        "consent": r.get("consent"), "severity": r.get("severity"),
                        "failure_modes": len(fm) if isinstance(fm, list) else (1 if fm else 0),
                        "exposure": x["descendants"], "wave": x["wave"], "state": x["state"]}
        if ruin in LOUD or r.get("door") == "one-way" or r.get("severity") == "P1":
            loud.add(x["id"])
    out = []
    for i, v in own.items():
        v["under_risk"] = sorted(anc.get(i, set()) & loud)
        tier = 0 if i in loud else 1 if (v["ruin"] == "medium" or v["severity"] == "P2") else 2 if (v["ruin"] or v["severity"]) else 3
        v["tier"] = ["loud", "medium", "low", "unrated"][tier]
        out.append(v)
    out.sort(key=lambda v: (["loud", "medium", "low", "unrated"].index(v["tier"]), -v["exposure"], v["id"]))
    rated = sum(1 for v in out if v["ruin"] or v["severity"])
    return {"rows": out, "coverage": {"rated": rated, "of": len(out),
            "one_way": sum(1 for v in out if v["door"] == "one-way"), "loud": len(loud),
            "under_risk": sum(1 for v in out if v["under_risk"])}}


def tradeoff_lens(g, rows):
    """Cost band against leverage, four plain quadrants plus cost unknown. It describes; it does not rank a winner."""
    by_id = {r["id"]: r for r in rows if r.get("id")}
    out, quad = [], defaultdict(list)
    for x in g["nodes"]:
        r = by_id.get(x["id"], {})
        band = cost_band(r.get("cost_prior"))
        lev = x["descendants"]
        q = ("cost unknown" if band is None else
             ("small cost, unblocks others" if lev else "small cost, unblocks none") if band == "S" else
             ("larger cost, unblocks others" if lev else "larger cost, unblocks none"))
        v = {"id": x["id"], "cost": band, "cost_prior": r.get("cost_prior"), "leverage": lev,
             "ruin": str(r.get("ruin") or "").lower() or None, "ready_now": x["ready_now"], "quadrant": q}
        out.append(v)
        quad[q].append(v)
    for q in quad:
        quad[q].sort(key=lambda v: (-v["leverage"], not v["ready_now"], v["id"]))
    banded = sum(1 for v in out if v["cost"])
    return {"rows": out, "quadrants": {k: [v["id"] for v in quad[k]] for k in quad},
            "coverage": {"cost_banded": banded, "of": len(out)}}


def render_risk(lens, top=8):
    c = lens["coverage"]
    out = [f"risk lens: {c['rated']} of {c['of']} active rows carry a ruin or severity rating; {c['of'] - c['rated']} are unrated",
           f"loud (ruin high or critical, a one-way door, or debt P1): {c['loud']} · one-way doors: {c['one_way']} · "
           f"rows downstream of a loud row: {c['under_risk']}", ""]
    for tier in ("loud", "medium"):
        rs = [v for v in lens["rows"] if v["tier"] == tier]
        out.append(f"{tier} ({len(rs)}), most downstream exposure first:")
        for v in rs[:top]:
            bits = [f"ruin {v['ruin']}" if v["ruin"] else "", f"door {v['door']}" if v["door"] else "",
                    f"sev {v['severity']}" if v["severity"] else "", "consent human" if v["consent"] == "human" else "",
                    f"{v['failure_modes']} failure modes" if v["failure_modes"] else ""]
            out.append(f"  {v['id']:<44} {v['state']:<8} exposes {v['exposure']:<3} {' · '.join(b for b in bits if b)}")
        out.append("")
    under = sorted((v for v in lens["rows"] if v["under_risk"]), key=lambda v: (-len(v["under_risk"]), v["id"]))
    out.append(f"inherited risk ({len(under)} rows sit downstream of a loud row):")
    for v in under[:top]:
        out.append(f"  {v['id']:<44} under {', '.join(v['under_risk'][:3])}")
    return "\n".join(out)


def render_tradeoff(lens, top=8):
    c = lens["coverage"]
    out = [f"tradeoff lens: {c['cost_banded']} of {c['of']} active rows give a cost the script can band (S up to 4 h or 1 session, "
           "M up to 16 h, 2 days or 3 sessions, L above); leverage = rows unblocked downstream", ""]
    for q in ("small cost, unblocks others", "larger cost, unblocks others", "small cost, unblocks none",
              "larger cost, unblocks none", "cost unknown"):
        ids = lens["quadrants"].get(q, [])
        rows = {v["id"]: v for v in lens["rows"]}
        out.append(f"{q} ({len(ids)}):")
        for i in ids[:top]:
            v = rows[i]
            out.append(f"  {i:<44} cost {v['cost'] or '?'}  unblocks {v['leverage']:<3}{'  ready now' if v['ready_now'] else ''}"
                       f"{'  ruin ' + v['ruin'] if v['ruin'] else ''}")
        out.append("")
    return "\n".join(out).rstrip()


def render(g, top=8):
    n = g["nodes"]
    by_tool = defaultdict(int)
    for x in n:
        by_tool[x["tool"]] += 1
    f = g["findings"]
    out = [f"backlog graph {g['today']}: {g['rows']} rows, {g['active']} active, {g['critical_path_waves']} waves deep",
           "tools: " + " · ".join(f"{k} {v}" for k, v in sorted(by_tool.items())),
           "findings: " + " · ".join(f"{k} {len(v)}" for k, v in f.items()), ""]
    ready = [x for x in n if x["ready_now"]]
    out.append(f"ready now ({len(ready)}): wave 0, startable state, trigger RIPE, no dead or missing dependency")
    for x in ready[:top]:
        out.append(f"  {x['id']:<44} tool {x['tool']:<12} tier cue {x['tier_cue']}  unblocks {x['descendants']}")
    out.append("")
    out.append(f"biggest unblockers (descendants), top {top}:")
    for x in sorted(n, key=lambda x: (-x["descendants"], x["id"]))[:top]:
        if x["descendants"]:
            out.append(f"  {x['id']:<44} {x['descendants']} downstream  wave {x['wave']}  {x['state']}")
    stale = [x for x in n if x["tool_missing"]]
    planned = [x for x in n if x["tool_planned"]]
    prose = [x for x in n if x["tool"] == "NOT-RESOLVED" and not x["tool_missing"] and not x["tool_planned"]]
    out.append("")
    out.append(f"route.tool: {len(stale)} rows name a path or command that is not found and not planned (stale), "
               f"{len(planned)} name something the row says it will build, {len(prose)} are prose with no path (cannot be matched)")
    for x in stale[:top]:
        out.append(f"  {x['id']:<44} stale: {', '.join(x['tool_missing'])[:80]}")
    for name, items in f.items():
        if items:
            out.append("")
            out.append(f"{name} ({len(items)}):")
            out += [f"  {i}" for i in items[:top]]
            if len(items) > top:
                out.append(f"  ... {len(items) - top} more (--json for all)")
    return "\n".join(out)


def to_dot(g):
    lines = ["digraph backlog {", "  rankdir=LR;"]
    for x in g["nodes"]:
        lines.append(f'  "{x["id"]}" [label="{x["id"]}\\n{x["state"]}"];')
        for d in x["deps"]:
            lines.append(f'  "{d}" -> "{x["id"]}";')
    lines.append("}")
    return "\n".join(lines)


def self_test():
    os.environ["BACKLOG_RIPENESS_GH_STUB"] = "{}"
    today = dt.date(2026, 10, 18)
    T = {"DONE", "COMPOSTED", "SUPERSEDED"}
    cat = {"readiness_packet.py", "/readiness"}
    FX = {"src/app/api/compass/route.ts", "src/app/api/account/delete/route.ts", "src/app/brief/[receiptId]/page.tsx", ".claude/commands/readiness.md"}
    chain = [{"id": "a", "state": "OPEN", "trigger": "after 2026-10-01", "route": {"tool": "scripts/readiness_packet.py"}},
             {"id": "b", "state": "HOLDING", "depends_on": ["a"], "trigger": "after 2026-10-01"},
             {"id": "c", "state": "HOLDING", "depends_on": "b", "trigger": "after 2026-10-01"}]
    g = build(chain, today, cat, T)
    order = [x["id"] for x in g["nodes"]]
    done = [dict(chain[0], state="DONE")] + chain[1:]
    g2 = build(done, today, cat, T)
    bad = [{"id": "x", "state": "OPEN", "depends_on": ["y", "ghost"], "trigger": "after 2026-10-01", "route": {"tool": "when built"}},
           {"id": "y", "state": "OPEN", "depends_on": ["x"], "trigger": "after 2026-10-01"},
           {"id": "z", "state": "OPEN", "depends_on": ["dead"], "trigger": "after 2026-10-01"},
           {"id": "dead", "state": "COMPOSTED"},
           {"id": "u", "state": "OPEN", "unblocks": ["v"], "trigger": "after 2026-10-01"},
           {"id": "v", "state": "OPEN", "trigger": "after 2026-10-01"}]
    gb = build(bad, today, cat, T)
    byid = {x["id"]: x for x in gb["nodes"]}
    checks = [
        ("known-good chain orders a, b, c", order == ["a", "b", "c"]),
        ("waves are 0, 1, 2", [x["wave"] for x in g["nodes"]] == [0, 1, 2]),
        ("a bare-string depends_on is read as one id, not characters", g["nodes"][2]["deps"] == ["b"]),
        ("only the root is ready now", [x["id"] for x in g["nodes"] if x["ready_now"]] == ["a"]),
        ("a known tool path resolves to HAVE", g["nodes"][0]["tool"] == "HAVE"),
        ("when a is DONE, b becomes ready", [x["id"] for x in g2["nodes"] if x["ready_now"]] == ["b"]),
        ("known-bad: prose tool is NOT-RESOLVED", byid["x"]["tool"] == "NOT-RESOLVED"),
        ("known-bad: a cycle is reported, not crashed on", set(gb["findings"]["cycle_members"]) >= {"x", "y"}),
        ("known-bad: a dangling id is reported", any("ghost" in d for d in gb["findings"]["dangling"])),
        ("known-bad: a dependency on a COMPOSTED row is dead and blocks readiness", any("dead" in d for d in gb["findings"]["dead_dependency"]) and not byid["z"]["ready_now"]),
        ("known-bad: cycle members are never ready now", not byid["x"]["ready_now"] and not byid["y"]["ready_now"]),
        ("unblocks without depends_on is reported and still adds the edge", any(m.startswith("u unblocks v") for m in gb["findings"]["unblocks_mismatch"]) and byid["v"]["deps"] == ["u"]),
        ("a path that does not exist is reported as missing, not as prose", build([{"id": "m", "state": "OPEN", "trigger": "after 2026-10-01", "route": {"tool": "scripts/no_such_tool.py"}}], today, cat, T)["nodes"][0]["tool_missing"] == ["scripts/no_such_tool.py"]),
        ("prose has no missing path", byid["x"]["tool_missing"] == []),
        ("a one-way door cues tier 4", build([{"id": "d", "state": "OPEN", "trigger": "after 2026-10-01", "door": "one-way"}], today, cat, T)["nodes"][0]["tier_cue"] == 4),
        ("a Claude Code built-in command (/mcp) resolves as BUILTIN, not as a missing tool", resolve_token("/mcp", cat, FX)[0] == "BUILTIN"),
        ("a row naming only a built-in has its tool found", resolve_tool({"jtbd": "x", "route": {"tool": "connect via /mcp"}}, cat, FX)[0] == "HAVE"),
        ("a repo command still wins over a built-in name", resolve_token("/readiness", cat, FX)[0] == "COMMAND"),
        ("a name that is no built-in, command or route is still UNRESOLVED", resolve_token("/design-sync", cat, FX)[0] == "UNRESOLVED" and "design-sync" not in BUILTIN_COMMANDS),
        ("a short path resolves by suffix to the right file, not to another route.ts", resolve_token("compass/route.ts", cat, FX) == ("SUFFIX", "src/app/api/compass/route.ts")),
        ("a bare generic basename with several matches is AMBIGUOUS", resolve_token("route.ts", cat, FX)[0] == "AMBIGUOUS"),
        ("a URL route resolves as ROUTE", resolve_token("/brief", cat, FX)[0] == "ROUTE"),
        ("a slash command resolves as COMMAND", resolve_token("/readiness", cat, FX)[0] == "COMMAND"),
        ("an unknown command or URL is UNRESOLVED", resolve_token("/design-sync", cat, FX)[0] == "UNRESOLVED"),
        ("a missing path the row says it will build is planned, not stale", resolve_tool({"jtbd": "Build the helper", "route": {"tool": "scripts/not_yet.py"}}, cat, FX)[2:] == ([], ["scripts/not_yet.py"])),
        ("the same missing path with no build intent is stale", resolve_tool({"jtbd": "Check the helper", "route": {"tool": "scripts/not_yet.py"}}, cat, FX)[2:] == (["scripts/not_yet.py"], [])),
        ("a resolved short path is HAVE with nothing missing", resolve_tool({"jtbd": "x", "route": {"tool": "compass/route.ts"}}, cat, FX)[:1] + resolve_tool({"jtbd": "x", "route": {"tool": "compass/route.ts"}}, cat, FX)[2:3] == ("HAVE", [])),
        ("rendered text has no em-dash", "\u2014" not in render(g) and "\u2014" not in render(gb)),
    ]
    # Debt issues as nodes, and the two lenses. Pre-registered 2026-11-02 before the first live run.
    iss = [{"number": 1, "title": "fix a", "state": "OPEN", "body": "x\n\n**Ref.** scripts/readiness_packet.py\n\n<!-- debt-id: da -->",
            "labels": [{"name": "debt"}, {"name": "sev:P1"}, {"name": "status:in-progress"}]},
           {"number": 2, "title": "fix b", "state": "OPEN", "body": "**Depends on.** debt:da, a\n\n<!-- debt-id: db -->",
            "labels": [{"name": "debt"}, {"name": "status:decision"}]},
           {"number": 3, "title": "old", "state": "CLOSED", "body": "<!-- debt-id: dc -->", "labels": [{"name": "status:open"}]},
           {"number": 4, "title": "no marker", "state": "OPEN", "body": "plain issue", "labels": []}]
    drows = [r for r in (debt_to_row(i) for i in iss) if r]
    dmap = {r["id"]: r for r in drows}
    gd = build(chain + drows, today, cat, T)
    dnode = {x["id"]: x for x in gd["nodes"]}
    lr = [{"id": "p", "state": "OPEN", "ruin": "high", "door": "one-way", "trigger": "after 2026-10-01", "cost_prior": "author estimate: 2 h"},
          {"id": "q", "state": "OPEN", "depends_on": ["p"], "trigger": "after 2026-10-01", "cost_prior": "3 d (author estimate)"},
          {"id": "s", "state": "OPEN", "trigger": "after 2026-10-01", "cost_prior": "tbd"}]
    gl = build(lr, today, cat, T)
    rk = {v["id"]: v for v in risk_lens(gl, lr)["rows"]}
    tl = tradeoff_lens(gl, lr)
    tq = {v["id"]: v["quadrant"] for v in tl["rows"]}
    checks += [
        ("debt: an issue without a debt-id marker is skipped", len(drows) == 3),
        ("debt: ids are namespaced debt:<id>", set(dmap) == {"debt:da", "debt:db", "debt:dc"}),
        ("debt: status labels map in-progress RUNNING, decision BLOCKED, closed DONE",
         (dmap["debt:da"]["state"], dmap["debt:db"]["state"], dmap["debt:dc"]["state"]) == ("RUNNING", "BLOCKED", "DONE")),
        ("debt: a Depends on line gives edges to debt and backlog ids", dmap["debt:db"]["depends_on"] == ["debt:da", "a"]),
        ("debt: the Ref line becomes route.tool and resolves", dnode["debt:da"]["tool"] == "HAVE"),
        ("debt: a closed issue leaves the graph", "debt:dc" not in dnode),
        ("debt: a debt node waits on its backlog dependency", dnode["debt:db"]["wave"] == 1),
        ("cost band: hours, days, sessions, words and tbd",
         [cost_band(x) for x in ("author estimate: 2 h", "3 d (author estimate)", "1 session", "~8 sessions across 3 waves", "small", "tbd", "author estimate: container, no own cost")]
         == ["S", "L", "S", "L", "S", None, None]),
        ("risk: a one-way high-ruin row is loud", rk["p"]["tier"] == "loud"),
        ("risk: a row downstream inherits the loud row", rk["q"]["under_risk"] == ["p"]),
        ("risk: a row with no rating is unrated, not low", rk["s"]["tier"] == "unrated"),
        ("risk: the loud row's exposure counts what it blocks", rk["p"]["exposure"] == 1),
        ("tradeoff: small cost that unblocks others", tq["p"] == "small cost, unblocks others"),
        ("tradeoff: tbd cost is unknown, not small", tq["s"] == "cost unknown"),
        ("lens text has no em-dash", "\u2014" not in render_risk(risk_lens(gl, lr)) + render_tradeoff(tl)),
    ]
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(DEFAULT_FILE))
    ap.add_argument("--today", default=None)
    ap.add_argument("--gh", action="store_true", help="check PR triggers with the gh CLI (slow)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dot", action="store_true")
    ap.add_argument("--top", type=int, default=8)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--debt", action="store_true", help="add open debt issues as nodes (gh, read-only)")
    src.add_argument("--debt-file", help="add debt issues from a saved JSON list (offline)")
    ap.add_argument("--lens", choices=["deps", "risk", "tradeoff"], default="deps")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.gh:
        os.environ.setdefault("BACKLOG_RIPENESS_GH_STUB", "{}")
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    rows = rp.load(a.file)
    debt = load_debt(a.debt_file) if (a.debt or a.debt_file) else []
    rows = rows + debt
    g = build(rows, today)
    if debt:
        g["debt"] = {"issues": len(debt), "active": sum(1 for x in g["nodes"] if x["id"].startswith("debt:")),
                     "with_edges": sum(1 for r in debt if r["depends_on"]) +
                     sum(1 for r in rows if not r["id"].startswith("debt:") and any(str(d).startswith("debt:") for d in deps_of(r)))}
    if a.json:
        g["lenses"] = {"risk": risk_lens(g, rows), "tradeoff": tradeoff_lens(g, rows)}
        print(json.dumps(g, indent=1, ensure_ascii=False))
    elif a.dot:
        print(to_dot(g))
    else:
        if a.lens == "risk":
            print(render_risk(risk_lens(g, rows), a.top))
        elif a.lens == "tradeoff":
            print(render_tradeoff(tradeoff_lens(g, rows), a.top))
        else:
            print(render(g, a.top))
        if debt:
            d = g["debt"]
            print(f"\ndebt: {d['issues']} issues read, {d['active']} active as debt:<id> nodes, {d['with_edges']} carry or receive an edge")
        if not a.gh:
            print("\n(PR triggers were not checked; pass --gh to include them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
