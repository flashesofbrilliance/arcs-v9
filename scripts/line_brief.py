#!/usr/bin/env python3
"""line_brief.py: render the child-session brief for assembly-line rows, with the orientation pre-paid.

Read-only, stdlib. Design: _PATTERNS/2026-10-18-assembly-line-choreography.md. The measured drag
(median 296k new tokens, 5 to 60 tool calls before the first edit) tracks tool calls, so each brief carries
what a child would otherwise spend calls to find: as-of git heads, resolved paths with sizes, the row's
gates, the one done-check, and the write scope (OWNS). It refuses: R3/R4 rows (no child), a row with no
resolvable write scope at R1/R2, and any two briefs in one wave whose OWNS overlap. Children never write
_QUEUE/; they return row deltas (parent is the only writer there).

usage: line_brief.py ROW_ID [ROW_ID ...] [--json] | --self-test
"""
import argparse, json, subprocess, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import line_triage  # noqa: E402

ROOT = line_triage.ROOT
SPAWNABLE = {"R1", "R2", "R-1"}
FORBIDDEN_WRITE = ("_QUEUE/", "CLAUDE.md", "_SEEDS/_oracle.json")  # hot files: parent or lease holder only


def git(*a):
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *a], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNCONFIRMED"


def owns_for(level, node):
    """Write scope. R-1 children write no file: they return the route.tool value as a row delta."""
    if level == "R-1":
        return []
    paths = [p for p in node.get("tool_resolved", []) if (ROOT / p).is_file() and not p.startswith(FORBIDDEN_WRITE)]
    return sorted(set(paths))


def build(node, row, level, rule):
    owns = owns_for(level, node)
    if level in ("R1", "R2") and not owns:
        return None, "no writable resolved file in route.tool; triage R-1 first"
    sizes = {p: len((ROOT / p).read_text(errors="ignore").splitlines()) for p in owns}
    done = row.get("done_check") or (row.get("gates") or ["UNCONFIRMED: row names no gate; ask the parent before acting"])[0]
    brief = {
        "title": f"Resolve {node['id']}" if level == "R-1" else f"Close {node['id']}",
        "level": level,
        "tier": {"R-1": "cheapest", "R1": "cheapest", "R2": "mid"}[level],
        "as_of": {"date": date.today().isoformat(),
                  "head": git("rev-parse", "--short", "HEAD"), "origin_main": git("rev-parse", "--short", "origin/main")},
        "row": {k: row.get(k) for k in ("id", "jtbd", "gates", "door", "abort", "rollback", "depends_on") if row.get(k) is not None},
        "triage_rule": rule,
        "owns": owns,
        "owns_lines": sizes,
        "ssot": [p for p in node.get("tool_resolved", []) if p not in owns],
        "done_check": done,
        "do_not": ["merge", "edit _QUEUE/ (return row_deltas instead)", "start sessions", "touch files outside OWNS"],
        "return_contract": ["status", "pr", "touched", "evidence", "row_deltas", "new_rows(with evidence)", "unblocks_observed"],
    }
    return brief, None


def render(b):
    L = [f"TITLE: {b['title']}", f"LEVEL: {b['level']} (run at {b['tier']} tier); triage rule: {b['triage_rule']}",
         f"AS-OF {b['as_of']['date']}: HEAD {b['as_of']['head']}, origin/main {b['as_of']['origin_main']}. Do not re-derive; start from these.",
         "ROW: " + json.dumps(b["row"], ensure_ascii=False),
         "OWNS (write): " + (", ".join(f"{p} ({b['owns_lines'][p]} lines)" for p in b["owns"]) or "none; return the route.tool value as a row_delta"),
         "SSOT (read-only): " + (", ".join(b["ssot"]) or "none"),
         f"DONE LOOKS LIKE: {b['done_check']}", "DO NOT: " + "; ".join(b["do_not"]),
         "RETURN CONTRACT: " + ", ".join(b["return_contract"]),
         "FIRST MOVE: act on OWNS directly; the orientation above is current. Read only what OWNS names."]
    return "\n".join(L)


def make_wave(ids, nodes, rows):
    by = {n["id"]: n for n in nodes}
    briefs, refused = [], []
    seen = {}
    for i in ids:
        n = by.get(i)
        if not n:
            refused.append((i, "not in graph")); continue
        lv, rule = line_triage.level(n, rows.get(i, {}))
        if lv not in SPAWNABLE:
            refused.append((i, f"{lv}: {rule}; no child")); continue
        b, err = build(n, rows.get(i, {}), lv, rule)
        if err:
            refused.append((i, err)); continue
        clash = [(p, seen[p]) for p in b["owns"] if p in seen]
        if clash:
            refused.append((i, f"OWNS overlap with {clash[0][1]} on {clash[0][0]}")); continue
        for p in b["owns"]:
            seen[p] = i
        briefs.append(b)
    return briefs, refused


def self_test():
    N = lambda i, tool="HAVE", paths=(), **k: {"id": i, "state": "READY", "tool": tool, "tier_cue": 2, "consent": None, "ready_now": True, "descendants": 0, "tool_resolved": list(paths), **k}
    real = "scripts/line_triage.py"
    nodes = [N("a", paths=[real]), N("b", paths=[real]), N("c", tool="NOT-RESOLVED"), N("d", tier_cue=4, paths=[real]),
             N("e", paths=["_QUEUE/induced-backlog.jsonl"]), N("filing-x", paths=[real])]
    nodes[3]["tier_cue"] = 4
    briefs, refused = make_wave(["a", "b", "c", "d", "e", "filing-x"], nodes, {})
    got = {b["row"].get("id", b["title"]): b for b in briefs}
    ok = [
        ("a gets a brief", any(b["title"] == "Close a" for b in briefs)),
        ("b refused on OWNS overlap with a", any(i == "b" and "overlap" in w for i, w in refused)),
        ("c (R-1) gets a brief with empty OWNS", any(b["title"] == "Resolve c" and b["owns"] == [] for b in briefs)),
        ("d (R3) refused, no child", any(i == "d" and w.startswith("R3") for i, w in refused)),
        ("e refused: only hot file resolves", any(i == "e" for i, _ in refused)),
        ("filing-x refused as human track", any(i == "filing-x" and w.startswith("R4") for i, w in refused)),
        ("no brief ever owns a hot file", all(not p.startswith(FORBIDDEN_WRITE) for b in briefs for p in b["owns"])),
        ("rendered brief carries all template sections", all(s in render(briefs[0]) for s in ("TITLE:", "AS-OF", "ROW:", "OWNS", "SSOT", "DONE LOOKS LIKE:", "DO NOT:", "RETURN CONTRACT:", "FIRST MOVE:"))),
    ]
    bad = [n for n, v in ok if not v]
    if bad:
        print("self-test FAILED:", bad); return 1
    print(f"self-test: OK ({len(ok)} checks)"); return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*"); ap.add_argument("--json", action="store_true"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.ids:
        ap.error("give at least one row id")
    nodes, rows = line_triage.load()
    briefs, refused = make_wave(a.ids, nodes, rows)
    if a.json:
        print(json.dumps({"briefs": briefs, "refused": refused}, indent=1)); return 0
    for b in briefs:
        print(render(b)); print("-" * 60)
    for i, why in refused:
        print(f"REFUSED {i}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
