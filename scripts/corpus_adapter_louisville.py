#!/usr/bin/env python3
"""corpus_adapter_louisville.py — pilot adapter: Louisville engagement corpus → catalog.

The corpus-atlas engines (atlas/spine/dolls) are corpus-generic; this adapter is the
per-client shim. Declared-edges-only, same honesty floor as the memory adapter:
  - manifest edges  <- louisville-canon-manifest.json (a literal declared manifest)
  - href edges      <- one artifact's HTML referencing another artifact by name/URL
  - roster edges    <- the HANDOFF doc naming an artifact (declared roster)
Version dupes (_1, _2, " (1)") collapse to one node; the dupe count is a DRIFT signal,
not hidden. Staleness = mtime of the canonical (newest) copy. Nothing inferred.

Output: _ARTIFACTS/louisville-catalog.json (same schema as catalog.json) + drift receipt.
Stdlib-only.
"""
import json, os, re, glob, time, sys

DL = os.path.expanduser("~/Downloads")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "_ARTIFACTS", "louisville-catalog.json")

CANON_RE = re.compile(r"(.+?)(?:_\d+|\s\(\d+\))?(\.[a-z]+)$")

def canon_name(fname):
    m = CANON_RE.match(fname)
    return (m.group(1) + m.group(2)) if m else fname

def classify(fname, path):
    if fname.endswith(".pdf"): return ("print", "performer", "Prints & Gifts")
    if fname.endswith(".json"): return ("ssot", "feedback", "SSOTs & Manifests")
    if fname.endswith(".md") or fname.endswith(".skill"): return ("canon", "reference", "Canon & Docs")
    if "/louisville-canon-bundle/" in path: return ("canon-surface", "user", "Canon Bundle Surfaces")
    if path.startswith(os.path.join(REPO, "public")): return ("repo-surface", "repo", "Repo Surfaces (live-path)")
    if "recoil/generated" in path: return ("ssot", "feedback", "SSOTs & Manifests")
    return ("surface", "project", "Pitch Surfaces (Downloads)")

def collect():
    files = {}
    pats = [os.path.join(DL, "louisville*"),
            os.path.join(DL, "louisville-canon-bundle", "*"),
            os.path.join(REPO, "public", "omakase", "louisville*"),
            os.path.join(REPO, "public", "louisville*"),
            os.path.join(REPO, "runtime", "recoil", "generated", "*jeben*")]
    for pat in pats:
        for p in glob.glob(pat):
            if os.path.isdir(p): continue
            base = os.path.basename(p)
            cn = canon_name(base)
            e = files.setdefault(cn, {"copies": []})
            e["copies"].append(p)
    return files

def main():
    now = time.time()
    files = collect()
    nodes, edges, dupes = [], [], 0
    texts = {}
    for cn, e in sorted(files.items()):
        # canonical copy = newest mtime
        copies = sorted(e["copies"], key=os.path.getmtime, reverse=True)
        p = copies[0]
        dupes += len(copies) - 1
        kind, typ, section = classify(cn, p)
        nid = os.path.splitext(cn)[0]
        try:
            body = open(p, encoding="utf-8", errors="ignore").read() if not cn.endswith(".pdf") else ""
        except OSError:
            body = ""
        texts[nid] = body
        nodes.append({"id": nid, "file": p.replace(os.path.expanduser("~"), "~"),
            "kind": kind, "type": typ, "section": section,
            "desc": f"{cn} · {len(copies)} cop{'ies' if len(copies)>1 else 'y'} · canonical={os.path.dirname(p).replace(os.path.expanduser('~'),'~')}",
            "age_days": int((now - os.path.getmtime(p)) / 86400),
            "promoted": p.startswith(os.path.join(REPO, "public")),
            "versions": len(copies)})
    ids = {n["id"] for n in nodes}
    seen = set()
    def add(f, t, rel):
        if f != t and t in ids and (f, t, rel) not in seen:
            seen.add((f, t, rel)); edges.append({"from": f, "to": t, "rel": rel})
    # manifest edges (first-class declared)
    man = texts.get("louisville-canon-manifest")
    if man:
        for t in ids:
            if t != "louisville-canon-manifest" and (t in man or t.replace("louisville-","") in man):
                add("louisville-canon-manifest", t, "declared-manifest")
    # href/name edges between artifacts
    for nid, body in texts.items():
        if not body: continue
        for t in ids:
            if t == nid: continue
            if (t + ".html") in body or (t + ".pdf") in body or f"{t}.arcs.care" in body:
                add(nid, t, "declared-href")
    # roster edges from the HANDOFF
    ho = texts.get("louisville-arcs-care-HANDOFF")
    if ho:
        for t in ids:
            if t != "louisville-arcs-care-HANDOFF" and t in ho:
                add("louisville-arcs-care-HANDOFF", t, "declared-roster")
    cat = {"generated": time.strftime("%Y-%m-%d %H:%M"), "corpus": "louisville",
           "nodes": nodes, "edges": edges, "version_dupes": dupes}
    json.dump(cat, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # drift receipt
    locs = {os.path.dirname(n["file"]) for n in nodes}
    live = [n["id"] for n in nodes if n["promoted"]]
    print(f"louisville catalog: {len(nodes)} nodes · {len(edges)} declared edges "
          f"({sum(1 for e in edges if e['rel']=='declared-manifest')} manifest / "
          f"{sum(1 for e in edges if e['rel']=='declared-href')} href / "
          f"{sum(1 for e in edges if e['rel']=='declared-roster')} roster) -> {OUT}")
    print(f"DRIFT receipt: {dupes} version-dupe copies · {len(locs)} scatter locations · "
          f"on a live repo path: {live or 'NONE'}")

if __name__ == "__main__":
    sys.exit(main())
