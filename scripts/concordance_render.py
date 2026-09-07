#!/usr/bin/env python3
"""concordance_render.py — the Concordance: where does concept X appear across the corpus.

A reference work that answers "where does concept X appear, everywhere?" It is a PURE
DETERMINISTIC RENDER over the digest link-graph (the same `links[]` in-degree that ranks the
Almanac's Required Reading). No LLM, no agents.

It doubles as a DELEGATION PRE-GATE demonstration: it computes and PRINTS its own judgment
residue. For the Concordance that residue is 0 (the link graph IS the deliverable), so nothing
is ever delegated. The rule this proves: precompute exhausts the mechanical, a residue gate
measures what judgment is left, and delegation triggers ONLY on the residue, at the cheapest
tier that can do it. Zero residue -> zero agents (mechanical-pass-first / cheap-tripwire made
literal, sibling to the Phase 0 integrity gate).

Usage:  python3 scripts/concordance_render.py [OUT.html] [DIGEST.json ...]
        (no args -> Atlas digests -> _ARTIFACTS/atlas/concordance.html)

Stdlib only; data embedded inline (works from file://). Internal research: render LOCAL.
"""
import json, sys, os, html, glob, datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_nodes(paths):
    nodes = []
    for p in paths:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"  skip {p}: {e}", file=sys.stderr); continue
        dom = (d.get("domain") if isinstance(d, dict) else None) or \
            os.path.basename(p).replace("digest-", "").replace(".json", "")
        for n in (d.get("nodes", d) if isinstance(d, dict) else d):
            nodes.append({
                "id": (n.get("id") or "").strip(),
                "title": n.get("title") or "(untitled)",
                "domain": n.get("domain") or dom,
                "cluster": n.get("cluster") or "(uncategorized)",
                "status": (n.get("status") or "UNVERIFIED").upper(),
                "claim": n.get("claim") or "",
                "links": [str(l).strip() for l in (n.get("links") or []) if str(l).strip()],
            })
    return nodes


def build_concordance(nodes):
    """target-slug -> referencing nodes. Pure mechanical; this is the whole product."""
    byid = {n["id"]: n for n in nodes if n["id"]}
    refs = defaultdict(list)
    for n in nodes:
        for t in n["links"]:
            refs[t].append(n)
    entries = []
    for slug, refset in refs.items():
        entries.append({
            "slug": slug,
            "count": len(refset),
            "resolved": slug in byid,                       # is the concept itself a graded node?
            "target": byid.get(slug),                       # the node it resolves to, if any
            "refs": sorted(refset, key=lambda x: (x["domain"], x["title"])),
        })
    entries.sort(key=lambda e: (-e["count"], e["slug"]))
    return byid, entries


def residue_verdict(nodes, entries):
    """The delegation PRE-GATE: how much of this needs judgment (an LLM/agent)?
    Concordance is a pure projection of existing links -> 0 judgment residue -> delegate nothing."""
    resolved = sum(1 for e in entries if e["resolved"])
    concept_only = len(entries) - resolved
    return {
        "concepts": len(entries),
        "resolved_to_a_node": resolved,
        "concept_only": concept_only,       # referenced but not themselves graded (DATA, not residue)
        "judgment_residue": 0,              # nothing here needs an LLM: it is a projection of links
        "delegate": False,
    }


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title><meta name="robots" content="noindex, nofollow">
<style>
  :root{--bg:#020408;--surface:#0b1017;--elev:#0e141d;--border:#1e2c3a;--border2:#26374a;
    --fg1:#eff4fa;--fg2:#c6d3e1;--fg3:#a3b4c6;--fg4:#7e8fa4;--cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--dim:#4a5a6d;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;--sans:'Inter',system-ui,-apple-system,sans-serif;}
  *{box-sizing:border-box;margin:0;padding:0;}
  html{background:radial-gradient(1100px 600px at 15% -10%,rgba(0,240,255,.06),transparent 60%),var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased;}
  body{max-width:1000px;margin:0 auto;padding:26px 22px 90px;}
  .eyebrow{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);display:flex;align-items:center;gap:8px;}
  .eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 9px var(--green);}
  h1{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em;margin:12px 0 4px;text-wrap:balance;}
  .sub{color:var(--fg3);font-size:13px;font-family:var(--mono);}
  .gate{font-family:var(--mono);font-size:11px;color:var(--fg4);border-left:2px solid var(--green);padding:6px 0 6px 12px;margin:14px 0 4px;line-height:1.6;}
  .gate b{color:var(--green);}
  .tbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:16px 0 12px;position:sticky;top:0;background:linear-gradient(180deg,var(--bg) 70%,transparent);padding:8px 0;z-index:5;}
  .tbar input{flex:1 1 260px;font-family:var(--mono);font-size:12.5px;color:var(--fg1);background:var(--elev);border:1px solid var(--border2);border-radius:9px;padding:10px 13px;}
  .tbar input:focus{outline:none;border-color:var(--cyan);}
  .tbar .cnt{font-family:var(--mono);font-size:11px;color:var(--fg4);white-space:nowrap;}
  .c{border:1px solid var(--border);border-radius:10px;margin-bottom:7px;background:var(--surface);overflow:hidden;}
  .ch{display:grid;grid-template-columns:1fr auto auto;gap:11px;align-items:center;padding:12px 14px;cursor:pointer;}
  .ch:hover{background:var(--elev);}
  .ct{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--fg1);min-width:0;word-break:break-word;}
  .ct .res{color:var(--cyan);} .ct .un{color:var(--fg4);}
  .badge{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap;}
  .badge.node{color:var(--cyan);border:1px solid var(--cyan);} .badge.concept{color:var(--fg4);border:1px solid var(--border2);}
  .deg{font-family:var(--mono);font-size:12px;font-weight:800;color:var(--gold);white-space:nowrap;}
  .body{display:none;padding:0 14px 12px 14px;} .c.open .body{display:block;}
  .body .self{font-size:12.5px;color:var(--fg2);line-height:1.5;border-bottom:1px solid var(--border);padding:2px 0 10px;margin-bottom:8px;}
  .ref{display:grid;grid-template-columns:auto 1fr;gap:9px;align-items:baseline;padding:5px 0;font-size:12.5px;line-height:1.45;}
  .ref .d{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--fg4);white-space:nowrap;padding-top:2px;}
  .ref .t{color:var(--fg1);font-weight:600;} .ref .cl{color:var(--fg3);}
  .empty{font-family:var(--mono);font-size:12px;color:var(--fg4);padding:20px;text-align:center;}
  .foot{margin-top:30px;padding-top:16px;border-top:1px solid var(--border);font-family:var(--mono);font-size:10.5px;color:var(--fg4);line-height:1.7;}
</style></head>
<body>
  <div class="eyebrow"><span class="dot"></span>__EYEBROW__</div>
  <h1>Where does a concept appear</h1>
  <div class="sub">__SUB__</div>
  <div class="gate">__GATE__</div>
  <div class="tbar"><input id="q" placeholder="filter concepts and the nodes that reference them..."><span class="cnt" id="cnt"></span></div>
  <div id="list"></div>
  <div class="foot">__FOOT__</div>
<script>
const C = __DATA__;
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));
function row(e){
  const name = e.resolved ? `<span class="res">${esc(e.slug)}</span>` : `<span class="un">${esc(e.slug)}</span>`;
  const badge = e.resolved ? `<span class="badge node">node</span>` : `<span class="badge concept">concept-only</span>`;
  const self = e.target ? `<div class="self"><b>${esc(e.target.title)}</b> &middot; ${esc(e.target.domain)} &middot; ${esc(e.target.claim)}</div>` : "";
  const refs = e.refs.map(r=>`<div class="ref"><span class="d">${esc(r.domain)}</span><span><span class="t">${esc(r.title)}</span> <span class="cl">&middot; ${esc(r.claim)}</span></span></div>`).join("");
  return `<div class="c" data-blob="${esc((e.slug+' '+(e.target?e.target.title+' '+e.target.claim:'')+' '+e.refs.map(r=>r.title+' '+r.claim).join(' ')).toLowerCase())}">
    <div class="ch" onclick="this.closest('.c').classList.toggle('open')"><div class="ct">${name}</div>${badge}<span class="deg">${e.count}&times;</span></div>
    <div class="body">${self}${refs}</div></div>`;
}
function render(f){
  f=(f||"").toLowerCase();
  const shown = C.filter(e=>!f || e.slug.toLowerCase().includes(f) || e.blob.includes(f));
  document.getElementById("list").innerHTML = shown.map(row).join("") || '<div class="empty">No concept matches that filter.</div>';
  document.getElementById("cnt").textContent = `${shown.length} / ${C.length} concepts`;
}
// precompute the search blob once (deterministic)
C.forEach(e=>{ e.blob = (e.slug+" "+(e.target?e.target.title+" "+e.target.claim:"")+" "+e.refs.map(r=>r.title+" "+r.claim).join(" ")).toLowerCase(); });
const q=document.getElementById("q");
q.addEventListener("input",e=>render(e.target.value));
render("");
</script></body></html>
"""


def render(byid, entries, verdict, meta):
    data = [{
        "slug": e["slug"], "count": e["count"], "resolved": e["resolved"],
        "target": ({"title": e["target"]["title"], "domain": e["target"]["domain"], "claim": e["target"]["claim"]} if e["target"] else None),
        "refs": [{"domain": r["domain"], "title": r["title"], "claim": r["claim"]} for r in e["refs"]],
    } for e in entries]
    sub = (f"{verdict['concepts']} concepts &middot; {verdict['resolved_to_a_node']} resolve to a graded node &middot; "
           f"{verdict['concept_only']} concept-only &middot; built {meta['generated']}")
    gate = ("<b>Delegation pre-gate:</b> judgment residue = 0. This is a pure projection of the corpus "
            "link-graph, so it renders deterministically and delegates nothing (no LLM, no agents). "
            "The mechanical pass IS the deliverable.")
    foot = ("The Concordance &mdash; where each concept is referenced across the graded corpus, a "
            "deterministic render over the same links[] in-degree that ranks the Almanac's Required "
            "Reading. Local-only. scripts/concordance_render.py.")
    return (TEMPLATE.replace("__TITLE__", html.escape(meta["title"]))
            .replace("__EYEBROW__", html.escape(meta["eyebrow"]))
            .replace("__SUB__", sub).replace("__GATE__", gate).replace("__FOOT__", foot)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))


def main():
    args = sys.argv[1:]
    if args and args[0].endswith((".html", ".htm")):
        out_path, digests = args[0], args[1:]
    else:
        out_path = os.path.join(ROOT, "_ARTIFACTS/atlas/concordance.html")
        digests = args or sorted(glob.glob(os.path.join(ROOT, "_ARTIFACTS/atlas/digest-*.json")))
    if not digests:
        print("no digests found", file=sys.stderr); sys.exit(1)
    nodes = load_nodes(digests)
    byid, entries = build_concordance(nodes)
    verdict = residue_verdict(nodes, entries)
    meta = {"title": "ARCS Concordance", "eyebrow": "ARCS · the Concordance",
            "generated": datetime.date.today().isoformat()}
    open(out_path, "w", encoding="utf-8").write(render(byid, entries, verdict, meta))
    print(f"rendered {verdict['concepts']} concepts over {len(nodes)} nodes -> {out_path}")
    print(f"PRE-GATE: judgment_residue={verdict['judgment_residue']} -> delegate={verdict['delegate']} "
          f"(pure deterministic render; no agents spawned). "
          f"{verdict['resolved_to_a_node']} resolve to a node, {verdict['concept_only']} concept-only.")


if __name__ == "__main__":
    main()
