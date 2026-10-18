#!/usr/bin/env python3
"""line_triage.py: assign each startable backlog row a resolution level (R-1, R0..R4) for the assembly line.

Read-only, stdlib, no model calls. Reads scripts/backlog_graph.py --json plus the backlog rows
(for door/ruin). Design: _PATTERNS/2026-10-18-assembly-line-choreography.md. It never changes a row;
fates stay human (NOTOMATION). First matching rule wins, and the rule that fired is printed.

usage: line_triage.py [--all] [--json] [--self-test]
  default lists wave-0 startable rows (ready_now); --all lists every active row.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUMAN_TRACK_PREFIXES = ("filing-",)  # Zach 2026-10-18: patent filing stays a human track, outside the line
DECISION_SUFFIXES = ("-redecide", "-ruling")  # Zach 2026-10-18: ADR rulings always R3, whatever the tier cue
ACTIVE = {"OPEN", "READY", "HOLDING", "BLOCKED"}


def level(node, row):
    """Return (level, rule). node: backlog_graph node; row: raw backlog row ({} if absent)."""
    nid = node["id"]
    if nid.startswith(HUMAN_TRACK_PREFIXES):
        return "R4", "human-track prefix"
    if node.get("state") == "BLOCKED" or node.get("consent") or row.get("ruin"):
        return "R4", "blocked, consent or ruin"
    if node.get("tool") == "NONE":
        return "R4", "no route.tool: human work"
    if nid.endswith(DECISION_SUFFIXES):
        return "R3", "decision row (-redecide/-ruling): Zach rules, parent drafts the card"
    if row.get("door") == "one-way" or node.get("tier_cue", 2) >= 4:
        return "R3", "one-way door or tier cue 4: parent drafts a decision card"
    if node.get("tool") == "NOT-RESOLVED":
        return "R-1", "route.tool does not resolve: fill it first"
    if node.get("tool") == "PARTIAL":
        return "R2", "tool partly resolves"
    if node.get("tool") == "HAVE":
        return "R1", "tool resolves, two-way, tier cue 2"
    return "R4", "unrecognised tool label, default to human"


def triage(nodes, rows, everything=False):
    out = []
    for n in nodes:
        if n.get("state") not in ACTIVE:
            continue
        if not everything and not n.get("ready_now"):
            continue
        lv, rule = level(n, rows.get(n["id"], {}))
        out.append({"id": n["id"], "level": lv, "rule": rule, "downstream": n.get("descendants", 0)})
    return sorted(out, key=lambda r: (-r["downstream"], r["id"]))


def load():
    g = json.loads(subprocess.check_output([sys.executable, str(ROOT / "scripts/backlog_graph.py"), "--json"]))
    rows = {}
    for line in (ROOT / "_QUEUE/induced-backlog.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["id"]] = r
    return g["nodes"], rows


def self_test():
    base = {"state": "READY", "tool": "HAVE", "tier_cue": 2, "consent": None, "ready_now": True, "descendants": 0}
    cases = [
        ({**base, "id": "x"}, {}, "R1"),
        ({**base, "id": "x"}, {"door": "one-way"}, "R3"),          # fail-on-bad: one-way door must never be R1
        ({**base, "id": "x", "tier_cue": 4}, {}, "R3"),
        ({**base, "id": "x", "tool": "NOT-RESOLVED"}, {}, "R-1"),
        ({**base, "id": "x", "tool": "PARTIAL"}, {}, "R2"),
        ({**base, "id": "x", "tool": "NONE"}, {}, "R4"),
        ({**base, "id": "x", "consent": "human"}, {}, "R4"),
        ({**base, "id": "x"}, {"ruin": "yes"}, "R4"),
        ({**base, "id": "filing-draft"}, {}, "R4"),                 # filing hub stays human even with a resolved tool
        ({**base, "id": "x", "state": "BLOCKED"}, {}, "R4"),
        ({**base, "id": "adr-9-acceptance-redecide", "tool": "NOT-RESOLVED"}, {}, "R3"),  # decision beats R-1
        ({**base, "id": "foo-graduation-ruling"}, {}, "R3"),
    ]
    bad = [(n["id"], want, level(n, r)[0]) for n, r, want in cases if level(n, r)[0] != want]
    if bad:
        print("self-test FAILED:", bad)
        return 1
    print(f"self-test: OK ({len(cases)} cases)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    nodes, rows = load()
    res = triage(nodes, rows, a.all)
    if a.json:
        print(json.dumps(res, indent=1))
        return 0
    counts = {}
    for r in res:
        counts[r["level"]] = counts.get(r["level"], 0) + 1
    print(f"{len(res)} rows ({'all active' if a.all else 'startable now'}): " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for r in res:
        print(f"  {r['level']:<4} {r['id']:<48} down={r['downstream']:<3} {r['rule']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
