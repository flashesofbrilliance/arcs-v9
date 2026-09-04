#!/usr/bin/env python3
"""research_render.py — render digest node schema as a 3-altitude research report.

Turns the ARCS "digest node" schema (the shape the Atlas auditors emit) into a
self-contained, air-gap-safe HTML report readable at three altitudes:

    Skim      — takeaway first: one big number, the health bar, what needs attention.
    Scan      — the informatics: status distribution, by-domain grid, filters.
    Trenches  — the full report: every node, grouped, expandable on demand.

This is the delivery-grammar Ahmed asked for (takeaway -> evidence -> depth on
demand), made mechanical: skim never front-loads depth; depth is always one click
down. Point it at any digest-*.json set and get the same tiered surface.

Usage:
    python3 scripts/research_render.py OUT.html DIGEST.json [DIGEST.json ...]
    python3 scripts/research_render.py            # defaults: Atlas digests -> atlas-report.html

Node schema (missing keys are tolerated):
    {id, title, domain, cluster, status, claim, provenance, links[], note}

Stdlib only. The data is embedded inline (works from file://). Internal research:
render LOCAL, never to a public host.
"""
import json, sys, os, html, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_digests(paths):
    nodes = []
    for p in paths:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"  skip {p}: {e}", file=sys.stderr)
            continue
        domain_default = d.get("domain") if isinstance(d, dict) else None
        if not domain_default:
            base = os.path.basename(p)
            domain_default = base.replace("digest-", "").replace(".json", "")
        items = d.get("nodes", d) if isinstance(d, dict) else d
        for n in items:
            nodes.append({
                "id": n.get("id") or "",
                "title": n.get("title") or "(untitled)",
                "domain": n.get("domain") or domain_default,
                "cluster": n.get("cluster") or "(uncategorized)",
                "status": (n.get("status") or "UNVERIFIED").upper(),
                "claim": n.get("claim") or "",
                "provenance": n.get("provenance") or "",
                "links": n.get("links") or [],
                "note": n.get("note") or "",
            })
    return nodes


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="robots" content="noindex, nofollow">
<style>
  :root{
    --bg:#020408; --surface:#0b1017; --elev:#0e141d; --border:#1e2c3a; --border2:#26374a;
    --fg1:#eff4fa; --fg2:#c6d3e1; --fg3:#a3b4c6; --fg4:#7e8fa4; --dim:#64748b;
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --red:#FF4D6D; --slate:#64748b;
    --live:#00FF9D; --prose:#00F0FF; --drift:#FFD700; --stale:#7e8fa4; --unv:#4a5a6d;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --sans:'Inter',system-ui,-apple-system,sans-serif;
    --measure:760px;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html{background:radial-gradient(1100px 600px at 15% -10%,rgba(0,240,255,.06),transparent 60%),var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased;}
  body{max-width:1080px;margin:0 auto;padding:26px 22px 80px;}
  a{color:var(--cyan);text-decoration:none;} a:hover{text-decoration:underline;}
  .mono{font-family:var(--mono);}
  .eyebrow{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);display:flex;align-items:center;gap:8px;}
  .eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 9px var(--green);}
  h1{font-size:clamp(24px,4vw,36px);font-weight:800;letter-spacing:-.02em;margin:12px 0 4px;text-wrap:balance;}
  .sub{color:var(--fg3);font-size:13.5px;font-family:var(--mono);}
  /* altitude toggle */
  .alt{position:sticky;top:0;z-index:20;display:flex;gap:6px;margin:20px 0 8px;padding:10px 0;background:linear-gradient(180deg,var(--bg) 60%,rgba(2,4,8,.0));backdrop-filter:blur(6px);}
  .alt button{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.03em;color:var(--fg3);background:var(--elev);border:1px solid var(--border2);border-radius:9px;padding:9px 15px;cursor:pointer;transition:.14s;display:flex;flex-direction:column;gap:2px;align-items:flex-start;}
  .alt button .k{font-size:9px;color:var(--fg4);letter-spacing:.14em;}
  .alt button:hover{border-color:var(--cyan);color:var(--fg1);}
  .alt button.on{color:#001014;background:linear-gradient(100deg,var(--cyan),#00c8dd);border-color:transparent;}
  .alt button.on .k{color:#013;}
  section[hidden]{display:none;}
  /* skim */
  .bignum{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin:6px 0 18px;}
  .bignum .n{font-size:clamp(48px,9vw,76px);font-weight:800;letter-spacing:-.03em;line-height:.9;color:var(--fg1);}
  .bignum .l{font-family:var(--mono);font-size:12.5px;color:var(--fg3);max-width:320px;line-height:1.5;}
  .hbar{display:flex;height:16px;border-radius:6px;overflow:hidden;border:1px solid var(--border);margin:2px 0 8px;}
  .hbar span{display:block;height:100%;}
  .hleg{display:flex;flex-wrap:wrap;gap:8px 16px;font-family:var(--mono);font-size:11px;color:var(--fg2);margin-bottom:22px;}
  .hleg .it{display:flex;align-items:center;gap:6px;} .hleg .sw{width:10px;height:10px;border-radius:3px;}
  .three{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:8px;}
  .card{border:1px solid var(--border);border-radius:13px;padding:15px 16px;background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.14));}
  .card .ct{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin-bottom:8px;}
  .card .cbig{font-size:30px;font-weight:800;letter-spacing:-.02em;color:var(--fg1);line-height:1;}
  .card p{font-size:13px;line-height:1.55;color:var(--fg2);margin-top:6px;}
  .card ul{list-style:none;margin-top:8px;display:flex;flex-direction:column;gap:6px;}
  .card li{font-size:12.5px;line-height:1.45;color:var(--fg2);display:flex;gap:7px;}
  .card li .sd{flex:0 0 auto;width:7px;height:7px;border-radius:50%;margin-top:5px;}
  .jump{font-family:var(--mono);font-size:11.5px;color:var(--fg3);margin-top:18px;}
  .jump a{cursor:pointer;}
  /* scan */
  .grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:4px 0 20px;}
  .dcard{border:1px solid var(--border);border-radius:13px;padding:14px 15px;background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.14));cursor:pointer;transition:.14s;}
  .dcard:hover{border-color:var(--cyan);}
  .dcard.sel{border-color:var(--cyan);box-shadow:0 0 0 1px var(--cyan) inset;}
  .dcard .dh{display:flex;justify-content:space-between;align-items:baseline;}
  .dcard .dn{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan);}
  .dcard .dc{font-size:26px;font-weight:800;color:var(--fg1);line-height:1;}
  .dcard .mini{display:flex;height:8px;border-radius:4px;overflow:hidden;margin:10px 0 8px;border:1px solid var(--border);}
  .dcard .mini span{display:block;height:100%;}
  .dcard .cl{font-size:11.5px;color:var(--fg3);line-height:1.5;}
  .sech{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);margin:6px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border);}
  .chips{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:20px;}
  .chip{font-family:var(--mono);font-size:11px;color:var(--fg2);background:var(--elev);border:1px solid var(--border2);border-radius:999px;padding:5px 11px;cursor:pointer;transition:.12s;}
  .chip:hover{border-color:var(--cyan);color:var(--fg1);} .chip.sel{color:#001014;background:var(--cyan);border-color:transparent;}
  .chip b{color:inherit;font-weight:700;}
  /* trenches */
  .tbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:4px 0 12px;}
  .tbar input{flex:1 1 240px;font-family:var(--mono);font-size:12.5px;color:var(--fg1);background:var(--elev);border:1px solid var(--border2);border-radius:9px;padding:9px 12px;}
  .tbar input:focus{outline:none;border-color:var(--cyan);}
  .tbar .cnt{font-family:var(--mono);font-size:11px;color:var(--fg4);white-space:nowrap;}
  .tbar .clr{font-family:var(--mono);font-size:11px;color:var(--cyan);cursor:pointer;}
  .grp{margin-bottom:20px;}
  .grp>.gh{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan);margin:14px 0 8px;display:flex;gap:8px;align-items:baseline;}
  .grp>.gh .gc{color:var(--fg4);font-weight:400;letter-spacing:.02em;}
  .node{border:1px solid var(--border);border-radius:10px;margin-bottom:7px;background:var(--surface);overflow:hidden;}
  .node>.nh{display:grid;grid-template-columns:auto 1fr auto;gap:11px;align-items:start;padding:12px 14px;cursor:pointer;}
  .node>.nh:hover{background:var(--elev);}
  .node .sd{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:0 0 auto;}
  .node .nt{min-width:0;}
  .node .ntitle{font-size:14px;font-weight:700;color:var(--fg1);line-height:1.35;}
  .node .nclaim{font-size:13px;color:var(--fg2);line-height:1.5;margin-top:3px;text-wrap:pretty;}
  .node .st{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap;align-self:center;}
  .node .body{padding:0 14px 13px 34px;display:none;}
  .node.open .body{display:block;}
  .node .body .row{font-family:var(--mono);font-size:11px;color:var(--fg3);line-height:1.6;margin-top:4px;}
  .node .body .row b{color:var(--fg4);font-weight:700;text-transform:uppercase;letter-spacing:.06em;font-size:9.5px;margin-right:6px;}
  .node .body .lk{display:inline-block;background:var(--elev);border:1px solid var(--border2);border-radius:6px;padding:2px 7px;margin:2px 4px 0 0;color:var(--fg3);font-size:10.5px;}
  .empty{font-family:var(--mono);font-size:12px;color:var(--fg4);padding:20px;text-align:center;}
  .foot{margin-top:34px;padding-top:16px;border-top:1px solid var(--border);font-family:var(--mono);font-size:10.5px;color:var(--fg4);line-height:1.7;}
  @media(max-width:560px){
    .node>.nh{grid-template-columns:auto 1fr;} .node .st{grid-column:2;justify-self:start;margin-top:6px;}
    .alt button{padding:8px 11px;}
  }
</style>
</head>
<body>
  <div class="eyebrow"><span class="dot"></span>__EYEBROW__</div>
  <h1>__H1__</h1>
  <div class="sub">__SUB__</div>

  <div class="alt" id="alt">
    <button data-alt="skim" class="on"><span class="k">5 SEC</span>Skim</button>
    <button data-alt="scan"><span class="k">30 SEC</span>Scan</button>
    <button data-alt="trenches"><span class="k">FULL</span>The Trenches</button>
  </div>

  <section id="skim"></section>
  <section id="scan" hidden></section>
  <section id="trenches" hidden></section>

  <div class="foot">__FOOT__</div>

<script>
const NODES = __DATA__;
const META = __META__;

// status vocabulary -> bucket, label, color, order
const ST = {
  "LIVE":            {b:"LIVE",     label:"Live",           c:"var(--live)",  o:0},
  "LIVE-AS-PROSE":   {b:"PROSE",    label:"Live (prose)",   c:"var(--prose)", o:1},
  "DRIFTED":         {b:"DRIFTED",  label:"Drifted",        c:"var(--drift)", o:2},
  "STALE":           {b:"STALE",    label:"Stale",          c:"var(--stale)", o:3},
};
function st(raw){ return ST[raw] || {b:"UNVERIFIED", label:"Unverified", c:"var(--unv)", o:4}; }
const BUCKETS = ["LIVE","PROSE","DRIFTED","STALE","UNVERIFIED"];
const BINFO = {LIVE:{label:"Live",c:"var(--live)"},PROSE:{label:"Live (prose)",c:"var(--prose)"},DRIFTED:{label:"Drifted",c:"var(--drift)"},STALE:{label:"Stale",c:"var(--stale)"},UNVERIFIED:{label:"Unverified",c:"var(--unv)"}};
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));

function counts(nodes){ const c={}; BUCKETS.forEach(b=>c[b]=0); nodes.forEach(n=>c[st(n.status).b]++); return c; }
function domains(){ const d={}; NODES.forEach(n=>{(d[n.domain]=d[n.domain]||[]).push(n);}); return d; }

// ---- filter state (shared by Scan + Trenches) ----
let F = {domain:null, bucket:null, q:""};
function applyF(){ return NODES.filter(n =>
  (!F.domain || n.domain===F.domain) &&
  (!F.bucket || st(n.status).b===F.bucket) &&
  (!F.q || (n.title+" "+n.claim+" "+n.cluster+" "+n.provenance).toLowerCase().includes(F.q)) ); }

function bar(c, total, h){ // stacked bar html from a counts object
  return BUCKETS.filter(b=>c[b]).map(b=>`<span style="width:${(100*c[b]/total).toFixed(2)}%;background:${BINFO[b].c}" title="${BINFO[b].label}: ${c[b]}"></span>`).join("");
}

// ---------- SKIM ----------
function renderSkim(){
  const c = counts(NODES), total = NODES.length;
  const drift = NODES.filter(n=>st(n.status).b==="DRIFTED");
  const stale = NODES.filter(n=>st(n.status).b==="STALE");
  const dm = domains();
  const domCount = Object.keys(dm).length;
  const health = Math.round(100*(c.LIVE)/total);
  const attn = drift.slice(0,4).map(n=>`<li><span class="sd" style="background:var(--drift)"></span>${esc(n.title)}</li>`).join("") || "<li>None — nothing has drifted from the record.</li>";
  const leg = BUCKETS.filter(b=>c[b]).map(b=>`<span class="it"><span class="sw" style="background:${BINFO[b].c}"></span>${BINFO[b].label} ${c[b]}</span>`).join("");
  document.getElementById("skim").innerHTML = `
    <div class="bignum"><span class="n">${total}</span><span class="l">load-bearing nodes graded against the live repo, across ${domCount} domains.</span></div>
    <div class="hbar">${bar(c,total)}</div>
    <div class="hleg">${leg}</div>
    <div class="three">
      <div class="card"><div class="ct">Health</div><div class="cbig">${health}%</div><p>of graded claims are live and hold against the repo right now.</p></div>
      <div class="card"><div class="ct">Needs attention · ${drift.length}</div><ul>${attn}</ul></div>
      <div class="card"><div class="ct">Aging · ${stale.length}</div><p>${stale.length?`claims are stale (time-bound and now past). ${esc((stale[0]||{}).title||"")}${stale.length>1?", +"+(stale.length-1)+" more":""}.`:"nothing stale."}</p></div>
    </div>
    <div class="jump">Go deeper: <a onclick="setAlt('scan')">the informatics &rarr;</a> &middot; <a onclick="setAlt('trenches')">every node &rarr;</a></div>`;
}

// ---------- SCAN ----------
function renderScan(){
  const dm = domains();
  const total = NODES.length;
  const cards = Object.keys(dm).sort((a,b)=>dm[b].length-dm[a].length).map(d=>{
    const nodes=dm[d], c=counts(nodes);
    const cl = [...new Set(nodes.map(n=>n.cluster))];
    const sel = F.domain===d ? "sel":"";
    return `<div class="dcard ${sel}" onclick="toggleDomain('${esc(d)}')">
      <div class="dh"><span class="dn">${esc(d)}</span><span class="dc">${nodes.length}</span></div>
      <div class="mini">${bar(c,nodes.length)}</div>
      <div class="cl">${cl.length} cluster${cl.length!=1?"s":""} &middot; ${c.DRIFTED||0} drifted &middot; ${c.STALE||0} stale</div></div>`;
  }).join("");
  // status chips
  const c = counts(NODES);
  const chips = BUCKETS.filter(b=>c[b]).map(b=>`<span class="chip ${F.bucket===b?'sel':''}" onclick="toggleBucket('${b}')"><span style="color:${BINFO[b].c}">&#9679;</span> ${BINFO[b].label} <b>${c[b]}</b></span>`).join("");
  document.getElementById("scan").innerHTML = `
    <div class="sech">By domain (click to filter)</div>
    <div class="grid4">${cards}</div>
    <div class="sech">By status</div>
    <div class="chips">${chips}</div>
    <div class="jump">${(F.domain||F.bucket)?'Filtered. ':''}<a onclick="setAlt('trenches')">Open the Trenches &rarr;</a>${(F.domain||F.bucket)?' <a onclick="clearF()">clear filter</a>':''}</div>`;
}

// ---------- TRENCHES ----------
function renderTrenches(){
  const rows = applyF();
  // group by domain -> cluster
  const g = {};
  rows.forEach(n=>{ (g[n.domain]=g[n.domain]||{}); (g[n.domain][n.cluster]=g[n.domain][n.cluster]||[]).push(n); });
  let out = "";
  Object.keys(g).sort().forEach(d=>{
    Object.keys(g[d]).sort().forEach(cl=>{
      const list = g[d][cl].sort((a,b)=>st(a.status).o-st(b.status).o);
      out += `<div class="grp"><div class="gh">${esc(d)} <span class="gc">/ ${esc(cl)} &middot; ${list.length}</span></div>`;
      list.forEach((n,i)=>{
        const s = st(n.status);
        const links = (n.links||[]).map(l=>`<span class="lk">${esc(l)}</span>`).join("");
        out += `<div class="node" id="n_${esc(n.domain)}_${esc(n.id||n.title.slice(0,8))}_${i}">
          <div class="nh" onclick="this.parentNode.classList.toggle('open')">
            <span class="sd" style="background:${s.c}"></span>
            <div class="nt"><div class="ntitle">${esc(n.title)}</div><div class="nclaim">${esc(n.claim)}</div></div>
            <span class="st" style="color:${s.c};border:1px solid ${s.c}">${esc(s.label)}</span>
          </div>
          <div class="body">
            ${n.note?`<div class="row"><b>Note</b>${esc(n.note)}</div>`:""}
            ${n.provenance?`<div class="row"><b>Source</b>${esc(n.provenance)}</div>`:""}
            ${links?`<div class="row"><b>Links</b>${links}</div>`:""}
          </div></div>`;
      });
      out += `</div>`;
    });
  });
  const active = F.domain||F.bucket||F.q;
  document.getElementById("trenches").innerHTML = `
    <div class="tbar">
      <input id="q" placeholder="search claims, titles, provenance..." value="${esc(F.q)}">
      <span class="cnt">${rows.length} / ${NODES.length} nodes</span>
      ${active?'<span class="clr" onclick="clearF()">clear</span>':''}
    </div>
    ${out || '<div class="empty">No nodes match this filter.</div>'}`;
  const q = document.getElementById("q");
  q.addEventListener("input", e=>{ F.q=e.target.value.toLowerCase(); const p=q.selectionStart; renderTrenches(); const nq=document.getElementById("q"); nq.focus(); nq.setSelectionRange(p,p); });
}

// ---- interactions ----
function setAlt(a){
  ["skim","scan","trenches"].forEach(s=>document.getElementById(s).hidden = (s!==a));
  document.querySelectorAll("#alt button").forEach(b=>b.classList.toggle("on", b.dataset.alt===a));
  if(a==="skim") renderSkim(); if(a==="scan") renderScan(); if(a==="trenches") renderTrenches();
  window.scrollTo({top:0,behavior:"instant"});
}
function toggleDomain(d){ F.domain = F.domain===d?null:d; renderScan(); }
function toggleBucket(b){ F.bucket = F.bucket===b?null:b; renderScan(); }
function clearF(){ F={domain:null,bucket:null,q:""}; renderScan(); if(!document.getElementById("trenches").hidden) renderTrenches(); }
document.querySelectorAll("#alt button").forEach(b=>b.addEventListener("click",()=>setAlt(b.dataset.alt)));
renderSkim();
</script>
</body>
</html>
"""


def render(nodes, meta):
    from collections import Counter
    c = Counter()
    for n in nodes:
        s = n["status"]
        b = {"LIVE": "LIVE", "LIVE-AS-PROSE": "PROSE", "DRIFTED": "DRIFTED", "STALE": "STALE"}.get(s, "UNVERIFIED")
        c[b] += 1
    doms = sorted({n["domain"] for n in nodes})
    sub = f"{len(nodes)} nodes &middot; {len(doms)} domains &middot; {c['LIVE']} live &middot; {c['DRIFTED']} drifted &middot; {c['STALE']} stale &middot; graded {meta['generated']}"
    foot = ("Internal research surface &mdash; render local, never a public host. "
            "Statuses graded against the live repo at render time; a snapshot, not live. "
            "Generated by scripts/research_render.py from the digest node schema.")
    out = (TEMPLATE
           .replace("__TITLE__", html.escape(meta["title"]))
           .replace("__EYEBROW__", html.escape(meta["eyebrow"]))
           .replace("__H1__", html.escape(meta["h1"]))
           .replace("__SUB__", sub)
           .replace("__FOOT__", foot)
           .replace("__DATA__", json.dumps(nodes, ensure_ascii=False))
           .replace("__META__", json.dumps(meta, ensure_ascii=False)))
    return out


def main():
    args = sys.argv[1:]
    if args:
        out_path, digests = args[0], args[1:]
    else:
        out_path = os.path.join(ROOT, "_ARTIFACTS/atlas/atlas-report.html")
        digests = sorted(glob.glob(os.path.join(ROOT, "_ARTIFACTS/atlas/digest-*.json")))
    if not digests:
        print("no digests found", file=sys.stderr); sys.exit(1)
    nodes = load_digests(digests)
    meta = {
        "title": "ARCS Research Atlas · Skim / Scan / Trenches",
        "eyebrow": "ARCS Research · The Atlas",
        "h1": "What ARCS knows, at three altitudes",
        "generated": datetime.date.today().isoformat(),
        "sources": [os.path.basename(d) for d in digests],
    }
    open(out_path, "w", encoding="utf-8").write(render(nodes, meta))
    print(f"rendered {len(nodes)} nodes -> {out_path}")


if __name__ == "__main__":
    main()
