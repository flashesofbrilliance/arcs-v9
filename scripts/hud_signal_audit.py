#!/usr/bin/env python3
"""hud_signal_audit.py: mechanical baseline of what the field HUD actually reads. Read-only, stdlib.

Part A  enumerates every reading site in src/organisms/ScopeHud.tsx (row(), cell(), Dial v=, value readouts,
        state labels) and classifies the expression by the identifiers it uses:
          DATA     reads the universe snapshot or a lattice node (universe., d., r.node, r.galaxy, n.sig)
          MODEL    computed from the drawn terrain's constants (grade, heading, safe bearings): true of the
                   picture, not of ARCS data
          DIAL     echoes a viewer control or camera state (visibility, depth, nest, fathoms, hold counts)
          STATE    navigation state (gps, trail)
          NOSIGNAL the literal "No signal"
          AMBIG    none of the above: listed for a human, never auto-classified
        The classifier is a regex over identifiers, so every expression is printed beside its class.
Part B  re-checks claims the 2026-10-15 moire audit made, so a later gate can enforce them:
        waypoint count, sub-11px canvas and SVG text, whether the ripple loop reads any data identifier,
        and the constant fog default.

usage: hud_signal_audit.py [<repo-root>] [--json]   (default: the repo this script lives in)
"""
import json, re, sys

import os
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = (_args[0] if _args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).rstrip("/")
AS_JSON = "--json" in sys.argv


def read(p):
    return open(ROOT + "/" + p, encoding="utf-8").read().split("\n")


hud, scope, client = read("src/organisms/ScopeHud.tsx"), read("src/organisms/Scope.tsx"), read("src/app/hud/HudClient.tsx")

RULES = [
    ("NOSIGNAL", re.compile(r'^\s*"No signal"\s*$|^\s*"No signal"')),
    ("DATA", re.compile(r"\bd\.|\buniverse\.|\br\.node\b|\br\.galaxy\b|\bn\.sig\b|\bf\?\.|\bmix\b|\bstrata\b")),
    ("MODEL", re.compile(r"\bgrade\b|\bhdg\b|\bsafe\.|\bturn\b|\bnearest\b|\bdeg3\(|\bb\.name\b|\bb\.color\b")),
    ("DIAL", re.compile(r"\bvis\b|\bvisState\b|\br\.fog\b|\br\.depth\b|\br\.nest\b|\bfathoms\b|\bx\.altitude\b|\bx\.resolution\b|\br\.holds\b|\bcount\b")),
    ("STATE", re.compile(r"\br\.gps\b|\br\.trail\b")),
]


def classify(expr):
    for name, rx in RULES:
        if rx.search(expr):
            return name
    return "AMBIG"


SITES = [
    ("row", re.compile(r'\brow\("([^"]+)",\s*(.*?)(?:,\s*(?:text|signal)\.\w+)?\)\}?\s*$')),
    ("cell", re.compile(r'\bcell\("([^"]+)",\s*(.*)\)\}?\s*$')),
    ("dial", re.compile(r"<Dial\b[^>]*\bv=\{([^}]+)\}[^>]*\bunit=\"([^\"]*)\"")),
    ("readout", re.compile(r"\.\.\.value[^>]*>\s*(.*?)\s*</(?:div|span)>")),
    ("state-label", re.compile(r"\.\.\.label[^>]*>\s*(\{[^<]*\}[^<]*)</span>")),
]
readings = []
for i, line in enumerate(hud, 1):
    for kind, rx in SITES:
        m = rx.search(line)
        if not m:
            continue
        if kind in ("row", "cell"):
            key, expr = m.group(1), m.group(2)
        elif kind == "dial":
            key, expr = "Dial " + m.group(2), m.group(1)
        else:
            key, expr = kind, m.group(1)
        if expr.strip() == "{v}":  # helper-definition template, not a reading
            break
        readings.append({"line": i, "kind": kind, "key": key, "expr": expr.strip()[:110], "class": classify(expr)})
        break
counts = {c: sum(1 for r in readings if r["class"] == c) for c in ("DATA", "MODEL", "DIAL", "STATE", "NOSIGNAL", "AMBIG")}
total = len(readings)

# ---- Part B ----
wp_start = next(i for i, l in enumerate(scope) if l.startswith("export const WAYPOINTS"))
wp_end = next(i for i in range(wp_start, len(scope)) if scope[i].startswith("]"))
waypoints = sum(1 for l in scope[wp_start:wp_end] if l.strip().startswith("{ id:"))
small = []
for i, l in enumerate(scope, 1):
    m = re.search(r"ctx\.font\s*=\s*`[^`]*?(\d+(?:\.\d+)?)px", l)
    if m and float(m.group(1)) < 11:
        small.append({"file": "Scope.tsx", "line": i, "px": float(m.group(1))})
for i, l in enumerate(hud, 1):
    m = re.search(r'fontSize="(\d+(?:\.\d+)?)"', l)
    if m and float(m.group(1)) < 11:
        small.append({"file": "ScopeHud.tsx", "line": i, "px": float(m.group(1))})
d0 = next(i for i, l in enumerate(scope) if "Droplets. Each overlaid waypoint" in l)
win = scope[d0:d0 + 60]
src_pushes = sum(1 for l in win if "sources.push(" in l)
data_refs = [{"line": d0 + 1 + k, "text": l.strip()[:120]} for k, l in enumerate(win)
             if re.search(r"\b(universe|receipt|echo|ygate|nci|outcome|dimensions)\b", l)]
fog = [l.strip() for l in client if "useState(0" in l]

report = {
    "root": ROOT,
    "A_scopehud": {"sites": total, "counts": counts, "data_share": round(counts["DATA"] / total, 3) if total else None, "readings": readings,
                   "ambiguous_for_human": [r for r in readings if r["class"] == "AMBIG"]},
    "B_claims": {"waypoints_hardcoded": waypoints, "subeleven_px_text_sites": small, "ripple_source_push_sites": src_pushes, "ripple_loop_data_refs": data_refs,
                 "fog_default": fog},
}
if AS_JSON:
    print(json.dumps(report, indent=1))
    sys.exit(0)
print("A. ScopeHud reading sites: %d | %s | data share %.0f%%" % (total, ", ".join("%s %d" % kv for kv in counts.items()), 100 * counts["DATA"] / total))
for r in readings:
    print("  L%-4d %-8s %-9s %-26s %s" % (r["line"], r["kind"], r["class"], r["key"][:26], r["expr"][:70]))
print("B. waypoints hard-coded: %d | sub-11px text sites: %d %s" % (waypoints, len(small), [(s["file"][:5], s["line"], s["px"]) for s in small]))
print("   ripple sources: %d push sites (waypoint loop + navigator); data refs in the loop: %s | fog default: %s" % (src_pushes, [(r["line"], r["text"][:60]) for r in data_refs] or "none", fog))
