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

usage:
  backlog_graph.py [--file F] [--today YYYY-MM-DD] [--gh] [--json] [--dot] [--top N]
  backlog_graph.py --self-test            pre-registered known-bad and known-good fixtures, no network
PR triggers are not checked unless --gh is given (it calls the gh CLI per PR); the ripeness column then says so.
"""
import argparse
import datetime as dt
import json
import os
import re
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


def resolve_tool(row, catalog):
    tool = (row.get("route") or {}).get("tool")
    if not tool:
        return "NONE", [], []
    toks = sorted(set(TOKEN_RE.findall(str(tool))))
    if not toks:
        return "NOT-RESOLVED", [], []
    ok = [t for t in toks if (ROOT / t.lstrip("/")).exists() or t in catalog or Path(t).name in catalog]
    miss = [t for t in toks if t not in ok]
    if len(ok) == len(toks):
        return "HAVE", ok, []
    return ("PARTIAL" if ok else "NOT-RESOLVED"), ok, miss


def deps_of(row):
    d = row.get("depends_on")
    if not d:
        return []
    if isinstance(d, str):
        d = re.split(r"[,\s]+", d)
    return [str(x).strip() for x in d if str(x).strip()]


def build(rows, today, catalog=None, terminal=None):
    terminal = terminal if terminal is not None else terminal_states()
    catalog = catalog if catalog is not None else known_tools()
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
        tool, resolved, missing = resolve_tool(r, catalog)
        has_dead = any(d in by_id and state[d] in DEAD for d in deps[i]) or any(d not in by_id for d in deps[i])
        startable = (state[i] in STARTABLE and wave.get(i) == 0 and not has_dead)
        nodes.append({"id": i, "state": state[i], "wave": wave.get(i), "ripeness": v[0] if v else "TERMINAL",
                      "tool": tool, "tool_resolved": resolved, "tool_missing": missing, "deps": sorted(deps[i]),
                      "descendants": len(descendants(i)), "cost": r.get("cost_prior"),
                      "consent": r.get("consent"),
                      "tier_cue": 4 if (r.get("consent") == "human" or r.get("door") == "one-way" or rp.ONE_WAY.search(rp._text(r))) else 2,
                      "ready_now": bool(startable and v and v[0] == "RIPE")})
    return {"today": str(today), "rows": len(by_id), "active": len(active), "nodes": nodes,
            "findings": {"dangling": dangling, "dead_dependency": dead, "cycle_members": cycle, "unblocks_mismatch": sorted(mismatch)},
            "critical_path_waves": (max(wave.values()) + 1) if wave else 0}


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
    prose = [x for x in n if x["tool"] == "NOT-RESOLVED" and not x["tool_missing"]]
    out.append("")
    out.append(f"route.tool: {len(stale)} rows name a path or command that does not resolve as written (stale, or a short path), {len(prose)} are prose with no path (cannot be matched)")
    for x in stale[:top]:
        out.append(f"  {x['id']:<44} missing: {', '.join(x['tool_missing'])[:80]}")
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
        ("rendered text has no em-dash", "\u2014" not in render(g) and "\u2014" not in render(gb)),
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
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.gh:
        os.environ.setdefault("BACKLOG_RIPENESS_GH_STUB", "{}")
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    g = build(rp.load(a.file), today)
    if a.json:
        print(json.dumps(g, indent=1, ensure_ascii=False))
    elif a.dot:
        print(to_dot(g))
    else:
        print(render(g, a.top))
        if not a.gh:
            print("\n(PR triggers were not checked; pass --gh to include them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
