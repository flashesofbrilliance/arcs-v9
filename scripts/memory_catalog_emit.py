#!/usr/bin/env python3
"""memory_catalog_emit.py — the ½ punch: mechanical, declared-edges-only backfill.

Walks the memory corpus (+ _SEEDS bank) and emits catalog.json for the Terrain
Atlas explorer. Every field is harvested, never inferred:
  - node identity/type/desc  <- frontmatter (the same SSOT the index inchworm uses)
  - section (district)       <- the node's placement under a MEMORY.md heading
  - edges                    <- ONLY declared [[wiki-links]] in file bodies
  - staleness (fog)          <- file mtime (mechanical clock, not judgment)
  - promoted flag            <- literal PROMOTED stamp in the body
No edge is guessed; absent ancestry stays absent (anti-propaganda rule).
Stdlib-only.
"""
import json, os, re, sys, time

MEMDIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
INDEX = os.path.join(MEMDIR, "MEMORY.md")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = os.path.join(REPO, "_SEEDS", "index.jsonl")

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
WIKI_RE = re.compile(r"\[\[([a-z0-9._-]+)\]\]")
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)
TYPE_RE = re.compile(r"^\s*type:\s*(\S+)", re.M)


def sections_map():
    """file -> section heading, from placement in MEMORY.md (mechanical)."""
    out, cur = {}, "Unfiled"
    for line in open(INDEX, encoding="utf-8"):
        if line.startswith("## "):
            cur = line[3:].strip()
        for m in re.finditer(r"\]\(([A-Za-z0-9._-]+\.md)\)", line):
            out[m.group(1)] = cur
    return out


def main():
    now = time.time()
    secs = sections_map()
    nodes, edges = [], []
    names = set()
    for f in sorted(os.listdir(MEMDIR)):
        if not f.endswith(".md") or f == "MEMORY.md":
            continue
        p = os.path.join(MEMDIR, f)
        body = open(p, encoding="utf-8").read()
        name = os.path.splitext(f)[0]
        names.add(name)
        desc = (DESC_RE.search(body) or [None, ""])[1] if DESC_RE.search(body) else ""
        mtype = TYPE_RE.search(body).group(1) if TYPE_RE.search(body) else "unknown"
        age_d = int((now - os.path.getmtime(p)) / 86400)
        nodes.append({
            "id": name, "file": f, "kind": "memory", "type": mtype,
            "desc": desc.strip().strip('"'), "section": secs.get(f, "Unfiled"),
            "age_days": age_d, "promoted": "PROMOTED" in body,
        })
        for tgt in WIKI_RE.findall(body):
            if tgt != name:
                edges.append({"from": name, "to": tgt, "rel": "declared-link"})
    # seeds (bank rows are themselves declarations)
    if os.path.exists(SEEDS):
        for line in open(SEEDS, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = s.get("name") or s.get("repo") or s.get("id") or "seed"
            nodes.append({
                "id": f"seed:{sid}", "kind": "seed",
                "type": s.get("seed_type", s.get("type", "repo")),
                "desc": (s.get("description") or s.get("desc") or "")[:180],
                "section": "Seed Bank", "age_days": 0, "promoted": bool(s.get("live")),
            })
    # scars: falsification-ledger entries become PRICED nodes (tuition banking) —
    # their own `refs` are declared edges, so a scar accrues echo like any holding
    fl = os.path.join(REPO, "_STATE", "falsification-ledger.jsonl")
    if os.path.exists(fl):
        for line in open(fl, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = s.get("id", "F?")
            nodes.append({
                "id": f"scar:{sid}", "kind": "scar", "type": "problem-shape",
                "desc": (s.get("claim", "") + " → " + s.get("verdict", ""))[:180],
                "section": "Falsification Ledger (tuition)",
                "age_days": 0, "promoted": bool(s.get("canon")),
                "tuition": s.get("cost") or s.get("tokens") or None,  # honest: mostly absent today
            })
            names.add(f"scar:{sid}")
            for r in s.get("refs", []):
                # scar cites its ADRs/tao/receipts — declared, from the ledger itself
                edges.append({"from": f"scar:{sid}", "to": str(r), "rel": "scar-ref"})
    # keep only edges whose endpoints exist (dangling declared links stay out of the render, counted honestly)
    dangling = [e for e in edges if e["to"] not in names]
    edges = [e for e in edges if e["to"] in names]
    cat = {"generated": time.strftime("%Y-%m-%d %H:%M"), "nodes": nodes, "edges": edges,
           "dangling_declared": len(dangling)}
    out = os.path.join(REPO, "_ARTIFACTS", "catalog.json")
    json.dump(cat, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"catalog: {len(nodes)} nodes ({sum(1 for n in nodes if n['kind']=='seed')} seeds) · "
          f"{len(edges)} declared edges · {len(dangling)} dangling (declared but target not yet written) -> {out}")


if __name__ == "__main__":
    sys.exit(main())
