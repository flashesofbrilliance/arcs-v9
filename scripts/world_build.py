#!/usr/bin/env python3
"""world_build.py — assemble the ARCS World (the 720° Möbius surface) from repo sources.

Stdlib-only. Harvests, never infers: every room is fed from files that already exist.

  python3 scripts/world_build.py --tier private   # both faces of the strip
  python3 scripts/world_build.py --tier public    # private face stripped (gated, not hidden)
  python3 scripts/world_build.py --tier both      # default: builds both

Outputs (under _ARTIFACTS/world/):
  world.<tier>.json          the harvested data
  arcs-world.<tier>.html     the template with the data injected at /*__WORLD__*/

Public face  = trust contract, privacy/terms covenant, canon (apex spine, field guide), ADR titles
               and statuses, the knowledge lattice, the NFTT stories, the proverbs.
Private face = DEWY receipts, witness stubs, great moments, memory catalog (ziggurat), recoil and
               war-room rosters, the prospecting survey, ADR sharp questions.
The seam is the Tao's one seam, four faces: the bank is open, the spark is metered.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "_ARTIFACTS", "world")
TEMPLATE = os.path.join(OUT_DIR, "world.template.html")

PRIVATE_KEYS = {"dewy", "witness", "moments", "ziggurat", "recoil", "warrooms", "survey"}
COVENANT_ADRS = ["ADR-032", "ADR-037", "ADR-044", "ADR-048", "ADR-049", "ADR-050", "ADR-055", "ADR-072"]


def rd(path: str, limit: int | None = None) -> str:
    try:
        with open(path, "r", errors="ignore") as fh:
            return fh.read(limit) if limit else fh.read()
    except OSError:
        return ""


def rel(p: str) -> str:
    return os.path.relpath(p, REPO)


def clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# ---------------------------------------------------------------- harvesters
def harvest_lattice() -> dict:
    d = json.load(open(os.path.join(REPO, "runtime/specs/knowledge-lattice-v1.json")))
    inv = d.get("invariants", {})
    return {
        "version": d.get("version"), "epoch_source": d.get("epoch_source"),
        "hardness_rule": d.get("hardness_rule"), "last_drift_check": d.get("last_drift_check"),
        "domains": d["domains"], "strata": d["strata"],
        "nodes": [{k: n.get(k) for k in ("id", "label", "st", "dom", "status", "what")} for n in d["nodes"]],
        "edges": d["edges"],
        "invariants": {k: inv.get(k) for k in ("note", "tautology", "constitutional", "empirical")},
        "satoshi": d.get("satoshi"),
    }


def harvest_adrs(private: bool) -> list[dict]:
    idx = json.load(open(os.path.join(REPO, "_DECISIONS/index.json")))
    out = []
    for e in idx:
        f = os.path.join(REPO, "_DECISIONS", e.get("file", ""))
        s = rd(f, 8000)
        m = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", s) or re.search(r"(20\d{2}-\d{2}-\d{2})", s)
        row = {"id": e["id"], "title": re.sub(r"^ADR-\d+\s*[—-]\s*", "", e.get("title", "")),
               "status": e.get("status"), "y": e.get("y_state"), "date": m.group(1) if m else None,
               "file": e.get("file")}
        if private:
            q = re.search(r"\*\*Sharp question:\*\*\s*(.+?)(?:\n\n|\n##)", s, re.S)
            row["sharp"] = clip(q.group(1), 320) if q else None
        out.append(row)
    return out


def harvest_dewy() -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "_STATE/*.dewy.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for r in d.get("receipts", []):
            v = r.get("dewy_vector", {}) or {}
            out.append({"date": d.get("session_ts") or re.search(r"(20\d{2}-\d{2}-\d{2})", f).group(1),
                        "id": r.get("receipt_id"), "surface": clip(r.get("surface", ""), 160),
                        "q": clip(r.get("sharp_question", ""), 300),
                        "D": clip(v.get("D", ""), 420), "E": clip(v.get("E", ""), 260),
                        "W": clip(v.get("W", ""), 260), "Y": clip(v.get("Y", ""), 260), "file": rel(f)})
    return out


def harvest_witness() -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "_STATE/witness/*.jsonl"))):
        for line in open(f, errors="ignore"):
            if not line.strip():
                continue
            try:
                w = json.loads(line)
            except Exception:
                continue
            out.append({"ts": w.get("ts"), "date": (w.get("ts") or "")[:10], "quote": clip(w.get("quote", ""), 600),
                        "context": clip(w.get("context", ""), 300), "gut": clip(w.get("gut", ""), 300),
                        "y": w.get("y"), "promoted": w.get("promoted"), "file": rel(f)})
    return out


def harvest_jsonl(path: str) -> list[dict]:
    out = []
    for line in rd(path).split("\n"):
        if line.strip():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def harvest_proverbs() -> list[dict]:
    rows = harvest_jsonl(os.path.join(REPO, "_CANON/tao-proverbs.jsonl"))
    return [{"id": r.get("id"), "aspect": r.get("aspect"), "verb": r.get("verb"), "text": r.get("text"),
             "date": r.get("minted"), "adr": r.get("source_adr")} for r in rows]


def harvest_moments() -> list[dict]:
    rows = harvest_jsonl(os.path.join(REPO, "_CANON/great-moments.jsonl"))
    return [{"date": (r.get("ts") or "")[:10], "speaker": r.get("speaker"), "quote": clip(r.get("quote", ""), 500),
             "gut": clip(r.get("gut", ""), 400), "situation": r.get("situation")} for r in rows]


def harvest_blog() -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "_ARTIFACTS/blog/stories/*.story.md"))):
        s = rd(f)
        m = re.search(r"---story---\s*(\{.*?\})\s*\n---", s, re.S)
        if not m:
            continue
        try:
            e = json.loads(m.group(1))
        except Exception:
            continue
        body = s[m.end():]
        lede = next((p.strip() for p in re.split(r"\n\s*\n", body) if len(p.strip()) > 80 and not p.strip().startswith("#")), "")
        out.append({"slug": e.get("slug"), "tier": e.get("tier"), "title": e.get("title"),
                    "description": e.get("description"), "eyebrow": e.get("eyebrow"),
                    "threads": e.get("threads", []), "arc": e.get("arc", {}), "lede": clip(lede, 360), "file": rel(f)})
    return out


def harvest_covenant() -> dict:
    tc = rd(os.path.join(REPO, "_CANON/trust-contract.md"))
    ver = re.search(r"\*\*Version:\*\*\s*([\d.]+)", tc)
    date = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", tc)
    sections = []
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", tc, re.S | re.M):
        h, body = m.group(1).strip(), m.group(2).strip()
        if h.lower().startswith("amendment"):
            continue
        sections.append({"h": h, "body": body})

    def page_paras(path):
        s = rd(os.path.join(REPO, path))
        return [clip(t, 420) for t in re.findall(r">([^<>{}]{60,})<", s)][:14]

    return {"trust": {"version": ver.group(1) if ver else None, "date": date.group(1) if date else None, "sections": sections},
            "privacy": page_paras("src/app/privacy/page.tsx"), "terms": page_paras("src/app/terms/page.tsx"),
            "trust_page": page_paras("src/app/trust/page.tsx")}


def harvest_flora() -> dict:
    s = rd(os.path.join(REPO, "_CANON/flora-and-fauna.md"))
    kingdoms, cur = [], None
    for line in s.split("\n"):
        m = re.match(r"^## ([IVX]+)\. (.+?)( —.*)?$", line)
        if m:
            cur = {"n": m.group(1), "name": m.group(2).strip(), "organisms": []}
            kingdoms.append(cur)
            continue
        m = re.match(r"^### \*(.+?)\* — (.+)$", line)
        if m and cur:
            cur["organisms"].append({"binomial": m.group(1), "name": m.group(2).strip()})
    return {"kingdoms": [k for k in kingdoms if k["organisms"]], "file": "_CANON/flora-and-fauna.md"}


def harvest_ziggurat() -> dict:
    p = os.path.join(REPO, "_ARTIFACTS/catalog.json")
    if not os.path.exists(p):
        return {}
    c = json.load(open(p))
    indeg = {}
    for e in c.get("edges", []):
        indeg[e.get("to")] = indeg.get(e.get("to"), 0) + 1
    nodes = {n["id"]: n for n in c.get("nodes", [])}
    hubs = sorted(indeg.items(), key=lambda kv: -kv[1])[:14]
    return {"generated": c.get("generated"), "nodes": len(c.get("nodes", [])), "edges": len(c.get("edges", [])),
            "dangling": c.get("dangling_declared"),
            "hubs": [{"id": k, "in": v, "kind": nodes.get(k, {}).get("kind"), "type": nodes.get(k, {}).get("type"),
                      "desc": clip(nodes.get(k, {}).get("desc", ""), 200)} for k, v in hubs],
            # the memory ring for the explorer: every node, every declared edge (nothing inferred)
            "ring": [{"id": n["id"], "kind": n.get("kind"), "type": n.get("type"), "desc": clip(n.get("desc", ""), 240),
                      "in": indeg.get(n["id"], 0)} for n in c.get("nodes", [])],
            "ring_edges": [[e.get("from"), e.get("to")] for e in c.get("edges", []) if e.get("from") in nodes and e.get("to") in nodes]}


def harvest_recoil() -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "runtime/recoil/generated/*.json"))):
        b = os.path.basename(f)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.json$", b)
        if m:
            out.append({"date": m.group(1), "name": m.group(2).replace("-", " "), "file": rel(f)})
    return out


def harvest_warrooms() -> list[str]:
    return sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(REPO, "runtime/warroom/*.html")))


def harvest_survey() -> dict:
    files = sorted(glob.glob(os.path.join(REPO, "_STATE/*-corpus-index.jsonl")))
    if not files:
        return {}
    lines = rd(files[-1]).split("\n")
    meta = json.loads(lines[0]).get("_meta", {}) if lines and lines[0].startswith('{"_meta"') else {}
    rows = [json.loads(l) for l in lines[1:] if l.strip()]
    graded = [r for r in rows if r.get("grade")]
    grades = {g: sum(1 for r in graded if r["grade"] == g) for g in "ABCD"}
    orph = [r for r in rows if r.get("ref_scanned") and r.get("inbound_refs") == 0]
    return {"generated": meta.get("generated"), "shallow": meta.get("shallow_clone"), "indexed": len(rows),
            "graded": len(graded), "grades": grades, "orphans": len(orph),
            "orphan_bytes": sum(r["bytes"] for r in orph), "file": rel(files[-1])}


def git_meta() -> dict:
    def sh(*a):
        try:
            return subprocess.check_output(list(a), text=True, cwd=REPO).strip()
        except Exception:
            return None
    return {"branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"), "head": sh("git", "rev-parse", "--short", "HEAD"),
            "shallow": os.path.exists(os.path.join(REPO, ".git", "shallow"))}


# ---------------------------------------------------------------- assemble
def build(tier: str) -> dict:
    private = tier == "private"
    world = {
        "meta": {"generated": _dt.date.today().isoformat(), "tier": tier, **git_meta()},
        "lattice": harvest_lattice(),
        "adrs": harvest_adrs(private),
        "proverbs": harvest_proverbs(),
        "blog": harvest_blog(),
        "covenant": harvest_covenant(),
        "covenant_adrs": COVENANT_ADRS,
        "apex": rd(os.path.join(REPO, "_CANON/apex-spine-mobius-induction-circuit.md")),
        "flora": harvest_flora(),
    }
    if private:
        world.update({
            "dewy": harvest_dewy(), "witness": harvest_witness(), "moments": harvest_moments(),
            "ziggurat": harvest_ziggurat(), "recoil": harvest_recoil(), "warrooms": harvest_warrooms(),
            "survey": harvest_survey(),
        })
    # timeline: every dated thing, both faces (private items only when private)
    tl = []
    for a in world["adrs"]:
        if a["date"]:
            tl.append({"date": a["date"], "kind": "adr", "label": f"{a['id']} · {a['title']}", "face": "public"})
    for p in world["proverbs"]:
        if p.get("date"):
            tl.append({"date": p["date"], "kind": "proverb", "label": p["id"], "face": "public"})
    if private:
        for d in world["dewy"]:
            tl.append({"date": d["date"], "kind": "dewy", "label": d["id"], "face": "private"})
        for w in world["witness"]:
            if w["date"]:
                tl.append({"date": w["date"], "kind": "witness", "label": clip(w["quote"], 80), "face": "private"})
        for r in world["recoil"]:
            tl.append({"date": r["date"], "kind": "recoil", "label": r["name"], "face": "private"})
    # lattice epochs from the epoch_source string
    for m in re.finditer(r"e(\d)=(\d{4}-\d{2}-\d{2})", world["lattice"].get("epoch_source") or ""):
        tl.append({"date": m.group(2), "kind": "epoch", "label": f"lattice epoch e{m.group(1)}", "face": "public"})
    tl.sort(key=lambda x: x["date"])
    world["timeline"] = tl
    world["time_range"] = [tl[0]["date"], tl[-1]["date"]] if tl else None
    return world


def render(world: dict, tier: str) -> str:
    tpl = rd(TEMPLATE)
    if "/*__WORLD__*/{}" not in tpl:
        raise SystemExit("template slot /*__WORLD__*/{} not found in " + TEMPLATE)
    data = json.dumps(world, ensure_ascii=False).replace("</script", "<\\/script")
    return tpl.replace("/*__WORLD__*/{}", data).replace("__TIER__", tier)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", choices=["public", "private", "both"], default="both")
    ap.add_argument("--json-only", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(OUT_DIR, exist_ok=True)
    tiers = ["public", "private"] if a.tier == "both" else [a.tier]
    for t in tiers:
        w = build(t)
        jp = os.path.join(OUT_DIR, f"world.{t}.json")
        with open(jp, "w") as fh:
            json.dump(w, fh, ensure_ascii=False, indent=0)
        line = f"{t:<8} json={os.path.getsize(jp)//1024}KB adrs={len(w['adrs'])} lattice={len(w['lattice']['nodes'])}n/{len(w['lattice']['edges'])}e proverbs={len(w['proverbs'])} blog={len(w['blog'])} timeline={len(w['timeline'])}"
        if t == "private":
            line += f" dewy={len(w['dewy'])} witness={len(w['witness'])} recoil={len(w['recoil'])} warrooms={len(w['warrooms'])}"
        if not a.json_only:
            hp = os.path.join(OUT_DIR, f"arcs-world.{t}.html")
            with open(hp, "w") as fh:
                fh.write(render(w, t))
            line += f" html={os.path.getsize(hp)//1024}KB"
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
