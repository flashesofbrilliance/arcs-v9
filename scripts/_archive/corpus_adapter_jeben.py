#!/usr/bin/env python3
"""corpus_adapter_jeben.py — adapter #2: Jeben engagement corpus → catalog.

Second instance of the adapter-per-client pattern (class: corpus_adapter_louisville.py,
the pilot). Engines stay generic; this shim only knows where the Jeben corpus lives and
which honesty rules apply. Declared-edges-only, nothing inferred.

Jeben-specific additions over the pilot:
  - AUDIENCE GATE (mandatory, per corpus-atlas-pilot memory): every node carries
    audience: internal | counterpart-facing. Anything not on a live public path or
    explicitly built FOR Jeben is internal. The catalog itself is internal-only —
    it must never be projected to a counterpart surface without a manual gate pass.
  - transcript nodes are flagged kind=transcript (raw ground truth; the fact-check
    substrate — quotes cited anywhere must trace back to one of these).
Version dupes collapse to one node; dupe count is a DRIFT signal, not hidden.
Output: _ARTIFACTS/jeben-catalog.json + drift receipt. Stdlib-only.
"""
import json, os, re, glob, time, sys

DL = os.path.expanduser("~/Downloads")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "_ARTIFACTS", "jeben-catalog.json")

CANON_RE = re.compile(r"(.+?)(?:_\d+|\s\(\d+\))?(\.[a-z]+)$")

def canon_name(fname):
    m = CANON_RE.match(fname)
    return (m.group(1) + m.group(2)) if m else fname

def classify(fname, path):
    low = fname.lower()
    if low == "jebenharrybriefing.txt": return ("transcript", "reference", "Raw Transcripts")
    if "/For Jeben/" in path: return ("gift", "user", "Sent to Jeben (For Jeben bundle)")
    if fname.endswith(".pdf"): return ("print", "performer", "Prints & Decks")
    if fname.endswith(".json") and "recoil/generated" in path: return ("ssot", "feedback", "SSOTs")
    if fname.endswith(".jsonl"): return ("canon", "reference", "Canon Registers")
    if path.startswith(os.path.join(REPO, "public")): return ("repo-surface", "repo", "Repo Surfaces (live-path)")
    if "runtime/warroom" in path: return ("repo-surface", "repo", "Repo Surfaces (gated warroom)")
    if fname.endswith(".md"): return ("analysis", "project", "Perplexity-era Analyses (Downloads)")
    return ("surface", "project", "Other (Downloads)")

def audience(kind, path):
    # counterpart-facing = things Jeben was actually given or can reach.
    if kind == "gift": return "counterpart-facing"
    if kind == "repo-surface": return "counterpart-facing"  # jeben.arcs.care live path
    if "Limitless-Minds-x-ARCS-Jeben-Intro" in path: return "counterpart-facing"
    return "internal"

def collect():
    files = {}
    pats = [os.path.join(DL, "*[Jj]eben*"),
            os.path.join(DL, "For Jeben", "*"),
            os.path.join(REPO, "public", "jeben*"),
            os.path.join(REPO, "runtime", "warroom", "jeben*"),
            os.path.join(REPO, "runtime", "recoil", "generated", "*jeben*"),
            os.path.join(REPO, "runtime", "recoil", "transcripts", "*jeben*"),
            os.path.join(REPO, "_CANON", "great-moments.jsonl")]
    for pat in pats:
        for p in glob.glob(pat):
            if os.path.isdir(p) or p.endswith(".zip"): continue
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
            "audience": audience(kind, p),
            "desc": f"{cn} · {len(copies)} cop{'ies' if len(copies)>1 else 'y'} · canonical={os.path.dirname(p).replace(os.path.expanduser('~'),'~')}",
            "age_days": int((now - os.path.getmtime(p)) / 86400),
            "promoted": p.startswith(os.path.join(REPO, "public")),
            "versions": len(copies)})
    ids = {n["id"] for n in nodes}
    seen = set()
    def add(f, t, rel):
        if f != t and t in ids and (f, t, rel) not in seen:
            seen.add((f, t, rel)); edges.append({"from": f, "to": t, "rel": rel})
    # href/name edges between artifacts (declared references only)
    for nid, body in texts.items():
        if not body: continue
        for t in ids:
            if t == nid: continue
            if (t + ".html") in body or (t + ".pdf") in body or (t + ".txt") in body or f"{t}.arcs.care" in body:
                add(nid, t, "declared-href")
    # citation edges: canon register entries citing a transcript by filename
    gm = texts.get("great-moments", "")
    if gm and "JebenHarryBriefing" in gm:
        add("great-moments", "JebenHarryBriefing", "declared-citation")
    cat = {"generated": time.strftime("%Y-%m-%d %H:%M"), "corpus": "jeben",
           "audience_gate": "MANDATORY — this catalog is internal-only; project nothing to a counterpart surface without a manual gate pass",
           "nodes": nodes, "edges": edges, "version_dupes": dupes}
    json.dump(cat, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    locs = {os.path.dirname(n["file"]) for n in nodes}
    live = [n["id"] for n in nodes if n["promoted"]]
    cf = [n["id"] for n in nodes if n["audience"] == "counterpart-facing"]
    print(f"jeben catalog: {len(nodes)} nodes · {len(edges)} declared edges -> {OUT}")
    print(f"DRIFT receipt: {dupes} version-dupe copies · {len(locs)} scatter locations · "
          f"live repo path: {live or 'NONE'}")
    print(f"AUDIENCE GATE: {len(cf)} counterpart-facing nodes: {cf}")

if __name__ == "__main__":
    sys.exit(main())
