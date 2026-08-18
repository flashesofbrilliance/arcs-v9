#!/usr/bin/env python3
"""doll_export.py — cut a russian-doll seed bundle from the corpus (User0 side).

Builds the declared-edges closure from a root node and seals it as one portable
JSON doll. Honest by construction:
  - edges DECLARED only; cycles become {"@ref": id} (no invented hierarchy)
  - --bodies bakes full frontmatter+body per shell (true tenant bootstrap)
  - AIR-GAP GATE (fail-closed): a node's frontmatter `audience:` defaults to
    internal when absent. `--audience external` cuts EXCLUDE every non-external
    shell (replaced by {"@gated": id}) and the receipt says how many were held.
  - epoch stamp: repo commit + catalog sha, so every doll names its world-state.

Usage: doll_export.py --root <node-id> [--bodies] [--audience internal|external]
       [--out FILE]
Stdlib-only. Companion: doll_sprout.py (UserN+1 side).
"""
import argparse, hashlib, json, os, re, subprocess, sys, time

MEMDIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(REPO, "_ARTIFACTS", "catalog.json")
AUD_RE = re.compile(r"^\s*audience:\s*(\S+)", re.M)
WIKI_RE = re.compile(r"\[\[([a-z0-9._-]+)\]\]")


def read_file(node):
    f = node.get("file")
    if not f:
        return None
    p = os.path.join(MEMDIR, f)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def audience_of(body):
    if body is None:
        return "internal"           # fail-closed: no file, no export outward
    m = AUD_RE.search(body[:2000])
    return m.group(1).strip() if m else "internal"   # absent = internal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--bodies", action="store_true")
    ap.add_argument("--audience", choices=["internal", "external"], default="internal")
    ap.add_argument("--out")
    a = ap.parse_args()

    cat = json.load(open(CATALOG, encoding="utf-8"))
    nodes = {n["id"]: n for n in cat["nodes"]}
    outs, ins = {}, {}
    for e in cat["edges"]:
        outs.setdefault(e["from"], []).append(e["to"])
        ins.setdefault(e["to"], []).append(e["from"])
    indeg = {k: len(v) for k, v in ins.items()}
    if a.root not in nodes:
        sys.exit(f"root not in catalog: {a.root}")

    gated = []

    def build(nid, seen):
        n = nodes.get(nid)
        if not n:
            return {"ref": nid, "missing": True}
        body = read_file(n)
        if a.audience == "external" and audience_of(body) != "external":
            gated.append(nid)
            return {"@gated": nid}   # held behind the air-gap, named not hidden
        seen.add(nid)
        d = indeg.get(nid, 0)
        shell = {
            "id": nid, "kind": n["kind"], "type": n["type"], "section": n["section"],
            "desc": n.get("desc", ""),
            "field_state": {"echo_weight": d, "staleness_days": n["age_days"],
                            "promoted": bool(n.get("promoted"))},
            "source": n.get("file", "_SEEDS bank row"),
            "declares": [{"@ref": t} if t in seen else build(t, seen)
                         for t in outs.get(nid, [])],
            "echoed_by": ins.get(nid, []),
        }
        if a.bodies and body is not None:
            shell["body"] = body
        return shell

    doll = build(a.root, set())
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    bundle = {
        "format": "arcs-doll/1",
        "root": a.root,
        "audience_cut": a.audience,
        "bodies": a.bodies,
        "epoch": {"repo_commit": commit,
                  "catalog_sha": hashlib.sha256(open(CATALOG, "rb").read()).hexdigest()[:16],
                  "exported": time.strftime("%Y-%m-%dT%H:%M:%S")},
        "gated_count": len(gated),
        "doll": doll,
    }
    out = a.out or os.path.join(REPO, "_ARTIFACTS", f"doll-{a.root}.json")
    json.dump(bundle, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    def count(d):
        return 0 if ("@ref" in d or "@gated" in d or d.get("missing")) \
            else 1 + sum(count(c) for c in d["declares"])
    print(f"doll: root={a.root} · {count(doll)} shells · audience={a.audience} · "
          f"gated={len(gated)} · bodies={a.bodies} · epoch={commit} -> {out}")
    if gated:
        print("held behind the air-gap (named, not hidden): " + " ".join(sorted(set(gated))[:12])
              + (" …" if len(set(gated)) > 12 else ""))


if __name__ == "__main__":
    main()
