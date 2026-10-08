#!/usr/bin/env python3
"""universe_snapshot_emit.py: one self-contained snapshot of the whole ARCS populi.

WHY: the field on the home page drew a procedural ziggurat, not the atlas. The universe view
must read field truth: one dated file, stamped with the commit it was built from, that every
surface (the field, status, surfaces, beliefs, the reading room) can project.

BACKBONE: runtime/specs/knowledge-lattice-v1.json (the atlas). Its strata are altitude rings,
its domains are bearings, `zp` (Zero-Point Knowledge, "om") is the null origin. The federation
keys are the lattice's OWN: domains ONTOLOGY / EPISTEMOLOGY / METAPHYSICS ("the physics") /
ETYMOLOGY / LIBRARY, and invariant grades TAUTOLOGY / CONSTITUTIONAL / EMPIRICAL. This script
coins no ontology; a new axis is a canon change, decided by Zach, not here.

EIGHT DIMENSIONS (each global, and per node where a node has a population):
  corpus     files in _ARTIFACTS, _PATTERNS, _STATE, _SEEDS            (git ls-files)
  canon      _CANON files, tao proverbs, ADRs                            (git ls-files + jsonl rows)
  codebase   src, scripts, operators files                               (git ls-files)
  conviction Y-gate spread across receipts                               NO SIGNAL (prod DB; not read here)
  clarity    1 - open shore questions / nodes, and unmapped-file fog     (lattice + node map)
  coherence  hardness = distinct domains among in-edge sources; diamond >= 4 (the lattice's rule)
  cohesion   cross-domain edges / all edges                              (lattice edges)
  consonance invariants by grade + last drift check                      (lattice invariants)

SOURCES: every catalog, index, registry, manifest and ledger tracked in git, plus each reading
room shelf. Rows are counted, never copied: private sources (counterpart catalogs, job search,
recoil) carry a count and a privacy flag, no contents.

NODE POPULATIONS: runtime/specs/universe-node-map-v0.json maps lattice node ids to path
patterns. Explicit rules only; a file no rule claims is counted as fog, never guessed onto a node.

Usage:
  python3 scripts/universe_snapshot_emit.py           # write runtime/specs/universe-snapshot.json
  python3 scripts/universe_snapshot_emit.py --check   # exit 1 if the committed snapshot is stale
Stdlib only.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATTICE = ROOT / "runtime" / "specs" / "knowledge-lattice-v1.json"
NODEMAP = ROOT / "runtime" / "specs" / "universe-node-map-v0.json"
SHELF = ROOT / "runtime" / "specs" / "reading-room-manifest.json"
OUT = ROOT / "runtime" / "specs" / "universe-snapshot.json"

CORPUS = ("_ARTIFACTS/", "_PATTERNS/", "_STATE/", "_SEEDS/")
CANON = ("_CANON/", "_DECISIONS/")
CODE = ("src/", "scripts/", "operators/")
INDEX_RE = re.compile(r"(catalog|index|registry|inventory|manifest|concordance|ledger)[^/]*\.(json|jsonl)$", re.I)
PRIVATE = ("_STATE/job-search/", "runtime/recoil/", "_QUEUE/linkedin/", "_STATE/handoff-excavation/")
PRIVATE_RE = re.compile(r"_ARTIFACTS/[^/]+-catalog\.json$")  # counterpart catalogs


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT, check=True).stdout


def rows(path: Path) -> int | None:
    try:
        t = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if path.suffix == ".jsonl":
        return sum(1 for l in t.splitlines() if l.strip())
    try:
        d = json.loads(t)
    except Exception:
        return None
    if isinstance(d, list):
        return len(d)
    if isinstance(d, dict):
        lists = [v for v in d.values() if isinstance(v, list)]
        return max((len(v) for v in lists), default=len(d))
    return None


def build(files: list[str]) -> dict:
    lat = json.loads(LATTICE.read_text(encoding="utf-8"))
    nodes = lat["nodes"] if isinstance(lat["nodes"], list) else [dict(v, id=k) for k, v in lat["nodes"].items()]
    dom = {n["id"]: n["dom"] for n in nodes}
    edges = [e for e in lat["edges"] if e[0] in dom and e[1] in dom]

    # coherence: the lattice's own hardness rule
    into: dict[str, set[str]] = {}
    for a, b, *_ in edges:
        into.setdefault(b, set()).add(dom[a])
    grade = {}
    inv = lat.get("invariants", {})
    for g in ("tautology", "constitutional", "empirical"):
        for i in inv.get(g, []):
            grade[i] = g

    # populations: explicit rules only
    nmap = json.loads(NODEMAP.read_text(encoding="utf-8"))["rules"]
    pop: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    claimed = set()
    for f in files:
        lf = f.lower()
        for nid, pats in nmap.items():
            if nid in pop and any(fnmatch.fnmatch(lf, p.lower()) for p in pats):
                pop[nid].append(f)
                claimed.add(f)

    out_nodes = []
    for n in nodes:
        fs = pop[n["id"]]
        out_nodes.append({
            "id": n["id"], "label": n["label"], "stratum": n["st"], "domain": n["dom"], "status": n["status"],
            "shore_open": len(n.get("shore", [])),
            "hardness": len(into.get(n["id"], ())), "diamond": len(into.get(n["id"], ())) >= 4,
            "invariant": grade.get(n["id"]),
            "population": {
                "corpus": sum(f.startswith(CORPUS) for f in fs),
                "canon": sum(f.startswith(CANON) or f in ("WORLD.md",) for f in fs),
                "codebase": sum(f.startswith(CODE) for f in fs),
                "files": len(fs),
            },
        })

    tracked = [f for f in files if f.startswith(CORPUS + CANON + CODE)]
    tao = rows(ROOT / "_CANON" / "tao-proverbs.jsonl") or 0
    shore = sum(n["shore_open"] for n in out_nodes)
    cross = sum(1 for a, b, *_ in edges if dom[a] != dom[b])

    sources = []
    for f in files:
        if not INDEX_RE.search(f.rsplit("/", 1)[-1]) or "node_modules" in f:
            continue
        priv = f.startswith(PRIVATE) or bool(PRIVATE_RE.search(f))
        sources.append({"path": f, "kind": INDEX_RE.search(f).group(1).lower(), "rows": rows(ROOT / f), "private": priv})
    shelf = json.loads(SHELF.read_text(encoding="utf-8"))
    rooms = [{"tenant": s["tenant"], "question": s.get("question"), "built": bool(s.get("built")), "render": s.get("render")}
             for s in shelf.get("shelf", [])]

    return {
        "version": "0.1.0",
        "backbone": "runtime/specs/knowledge-lattice-v1.json",
        "lattice_reviewed": lat.get("last_reviewed"),
        "lattice_drift_check": lat.get("last_drift_check"),
        "null_origin": "zp",
        "federation": {
            "domains": {k: v["label"] for k, v in lat["domains"].items()},
            "strata": {k: v["label"] for k, v in lat["strata"].items()},
            "invariant_grades": ["tautology", "constitutional", "empirical"],
        },
        "dimensions": {
            "corpus": sum(f.startswith(CORPUS) for f in files),
            "canon": {"files": sum(f.startswith(CANON) for f in files), "tao_proverbs": tao,
                      "adrs": sum(fnmatch.fnmatch(f, "_DECISIONS/ADR-*.md") for f in files)},
            "codebase": sum(f.startswith(CODE) for f in files),
            "conviction": {"signal": None, "why": "Y-gate spread lives in the prod Receipt table; not read by this script"},
            "clarity": {"nodes_clear": sum(1 for n in out_nodes if n["shore_open"] == 0), "nodes": len(out_nodes),
                        "shore_open": shore, "files_mapped": len(claimed & set(tracked)), "files_fog": len(set(tracked) - claimed)},
            "coherence": {"diamonds": sum(n["diamond"] for n in out_nodes),
                          "mean_hardness": round(sum(n["hardness"] for n in out_nodes) / len(out_nodes), 2)},
            "cohesion": {"cross_domain_edges": cross, "edges": len(edges), "ratio": round(cross / len(edges), 3) if edges else None},
            "consonance": {g: len(inv.get(g, [])) for g in ("tautology", "constitutional", "empirical")},
        },
        "nodes": out_nodes,
        "edges": [[a, b] for a, b, *_ in edges],
        "sources": sources,
        "reading_room": rooms,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="ARCS universe snapshot: emit or check")
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed snapshot is stale")
    a = ap.parse_args()
    files = [f for f in git("ls-files").splitlines() if f]
    snap = build(files)
    body = json.dumps(snap, indent=1, ensure_ascii=False) + "\n"
    if a.check:
        cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur != body:
            print("✖ universe-snapshot --check: stale; run python3 scripts/universe_snapshot_emit.py")
            return 1
        print("✓ universe-snapshot current")
        return 0
    OUT.write_text(body, encoding="utf-8")
    d = snap["dimensions"]
    print(f"universe: {len(snap['nodes'])} nodes · {len(snap['edges'])} edges · {len(snap['sources'])} sources · "
          f"{len(snap['reading_room'])} rooms · mapped {d['clarity']['files_mapped']} / fog {d['clarity']['files_fog']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
