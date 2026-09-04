#!/usr/bin/env python3
"""research_render.py — render a digest node schema as an ALMANAC read through the READER.

Library taxonomy (ARCS): ADR / DEWY / Wisdom / Memory / Handoff are PRIMARY records.
The **Atlas** is second-order (the relational map). The **Almanac** is second-order too
(the graded, dated STATE of the corpus). The **Reader** is the instrument both are viewed
through — three altitudes:

    Skim      — the librarian's REQUIRED READING: the load-bearing spine (ranked by how
                often the corpus references each node, LIVE only), one big number, one health
                plot. Takeaway first.
    Scan      — the informatics: domain x status charts, status filter, click-to-drill.
    Trenches  — the full report: every node, grouped, searchable, click-to-expand, and each
                row EXPORTABLE as a self-contained bundle.

This is the delivery grammar the clinical-AI counterpart asked for (takeaway -> evidence ->
depth on demand) made mechanical: skim never front-loads depth; depth is always one click down.

Node schema (missing keys tolerated): {id, title, domain, cluster, status, claim, provenance, links[], note}
Status vocabulary: LIVE, LIVE-AS-PROSE, DRIFTED, STALE, (anything else) -> UNVERIFIED.

Usage:  python3 scripts/research_render.py [OUT.html] [DIGEST.json ...]
        (no args -> Atlas digests -> _ARTIFACTS/atlas/atlas-almanac.html)

Stdlib only; data embedded inline (works from file://). Internal research: render LOCAL.
"""
import json, sys, os, html, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_digests(paths):
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
                "id": n.get("id") or "",
                "title": n.get("title") or "(untitled)",
                "domain": n.get("domain") or dom,
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
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --red:#FF4D6D;
    /* aggregate status palette (4 buckets, well-separated) + prose accent for node detail */
    --live:#00FF9D; --drift:#FFD700; --stale:#7e8fa4; --unv:#4a5a6d; --prose:#00F0FF;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --sans:'Inter',system-ui,-apple-system,sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html{background:radial-gradient(1100px 600px at 15% -10%,rgba(0,240,255,.06),transparent 60%),var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased;}
  body{max-width:1080px;margin:0 auto;padding:26px 22px 90px;}
  a{color:var(--cyan);text-decoration:none;cursor:pointer;} a:hover{text-decoration:underline;}
  .eyebrow{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);display:flex;align-items:center;gap:8px;}
  .eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 9px var(--green);}
  h1{font-size:clamp(24px,4vw,36px);font-weight:800;letter-spacing:-.02em;margin:12px 0 4px;text-wrap:balance;}
  .sub{color:var(--fg3);font-size:13px;font-family:var(--mono);}
  .alt{position:sticky;top:0;z-index:20;display:flex;gap:6px;margin:20px 0 10px;padding:10px 0;background:linear-gradient(180deg,var(--bg) 62%,rgba(2,4,8,0));backdrop-filter:blur(6px);}
  .alt button{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.03em;color:var(--fg3);background:var(--elev);border:1px solid var(--border2);border-radius:9px;padding:9px 15px;cursor:pointer;transition:.14s;display:flex;flex-direction:column;gap:2px;align-items:flex-start;}
  .alt button .k{font-size:9px;color:var(--fg4);letter-spacing:.14em;}
  .alt button:hover{border-color:var(--cyan);color:var(--fg1);}
  .alt button.on{color:#001014;background:linear-gradient(100deg,var(--cyan),#00c8dd);border-color:transparent;}
  .alt button.on .k{color:#013;}
  section[hidden]{display:none;}
  /* skim */
  .bignum{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin:4px 0 14px;}
  .bignum .n{font-size:clamp(46px,9vw,72px);font-weight:800;letter-spacing:-.03em;line-height:.9;}
  .bignum .l{font-family:var(--mono);font-size:12.5px;color:var(--fg3);max-width:330px;line-height:1.5;}
  .hbar{display:flex;gap:2px;height:16px;margin:2px 0 8px;}
  .hbar span{display:block;height:100%;border-radius:3px;}
  .hleg{display:flex;flex-wrap:wrap;gap:8px 16px;font-family:var(--mono);font-size:11px;color:var(--fg2);margin-bottom:22px;}
  .hleg .it{display:flex;align-items:center;gap:6px;} .hleg .sw{width:10px;height:10px;border-radius:3px;}
  .rr-h{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--gold);margin:2px 0 4px;display:flex;align-items:baseline;gap:9px;}
  .rr-h small{color:var(--fg4);font-weight:400;letter-spacing:.02em;font-size:10.5px;text-transform:none;}
  .rr{display:flex;flex-direction:column;gap:2px;margin-bottom:14px;}
  .rr .row{display:grid;grid-template-columns:26px 1fr auto;gap:12px;align-items:baseline;padding:9px 10px;border-radius:9px;cursor:pointer;transition:.12s;border:1px solid transparent;}
  .rr .row:hover{background:var(--elev);border-color:var(--border2);}
  .rr .rk{font-family:var(--mono);font-size:15px;font-weight:800;color:var(--fg4);}
  .rr .rt{font-size:14px;font-weight:600;color:var(--fg1);line-height:1.35;} .rr .rt .rd{font-family:var(--mono);font-size:10px;color:var(--fg4);text-transform:uppercase;letter-spacing:.06em;margin-left:8px;}
  .rr .rc{font-size:12.5px;color:var(--fg3);line-height:1.45;margin-top:2px;}
  .rr .rw{font-family:var(--mono);font-size:10.5px;color:var(--gold);white-space:nowrap;align-self:center;}
  .attn{font-family:var(--mono);font-size:12px;color:var(--fg3);line-height:1.6;border-left:2px solid var(--drift);padding-left:12px;margin-bottom:8px;}
  .attn b{color:var(--drift);}
  .jump{font-family:var(--mono);font-size:11.5px;color:var(--fg3);margin-top:16px;}
  /* scan */
  .sech{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);margin:8px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:baseline;}
  .sech .clr{color:var(--cyan);cursor:pointer;font-weight:400;text-transform:none;letter-spacing:0;}
  .dbars{display:flex;flex-direction:column;gap:14px;margin-bottom:8px;}
  .dbar{display:grid;grid-template-columns:120px 1fr 48px;gap:14px;align-items:center;cursor:pointer;}
  .dbar:hover .dname{color:var(--fg1);}
  .dbar.sel .dname{color:var(--cyan);}
  .dbar .dname{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--fg3);transition:.12s;text-align:right;}
  .dbar .track{display:flex;gap:2px;height:22px;}
  .dbar .track span{display:block;height:100%;border-radius:3px;min-width:2px;transition:.12s;}
  .dbar .track span:hover{filter:brightness(1.15);}
  .dbar .dtot{font-family:var(--mono);font-size:15px;font-weight:800;color:var(--fg1);text-align:right;}
  .leg{display:flex;flex-wrap:wrap;gap:9px 18px;font-family:var(--mono);font-size:11px;color:var(--fg2);margin:14px 0 22px;}
  .leg .it{display:flex;align-items:center;gap:6px;cursor:pointer;} .leg .sw{width:11px;height:11px;border-radius:3px;} .leg .it.off{opacity:.4;}
  .chips{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:8px;}
  .chip{font-family:var(--mono);font-size:11px;color:var(--fg2);background:var(--elev);border:1px solid var(--border2);border-radius:999px;padding:5px 11px;cursor:pointer;transition:.12s;}
  .chip:hover{border-color:var(--cyan);color:var(--fg1);} .chip.sel{color:#001014;background:var(--cyan);border-color:transparent;} .chip b{color:inherit;}
  /* trenches */
  .tbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:4px 0 12px;}
  .tbar input{flex:1 1 240px;font-family:var(--mono);font-size:12.5px;color:var(--fg1);background:var(--elev);border:1px solid var(--border2);border-radius:9px;padding:9px 12px;}
  .tbar input:focus{outline:none;border-color:var(--cyan);}
  .tbar .cnt{font-family:var(--mono);font-size:11px;color:var(--fg4);white-space:nowrap;} .tbar .clr{font-family:var(--mono);font-size:11px;color:var(--cyan);cursor:pointer;}
  .grp{margin-bottom:18px;} .grp>.gh{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan);margin:14px 0 8px;display:flex;gap:8px;align-items:baseline;}
  .grp>.gh .gc{color:var(--fg4);font-weight:400;letter-spacing:.02em;}
  .node{border:1px solid var(--border);border-radius:10px;margin-bottom:7px;background:var(--surface);overflow:hidden;}
  .node .nh{display:grid;grid-template-columns:auto 1fr auto auto;gap:11px;align-items:start;padding:12px 14px;}
  .node .nh:hover{background:var(--elev);}
  .node .sd{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:0 0 auto;}
  .node .nt{min-width:0;cursor:pointer;} .node .ntitle{font-size:14px;font-weight:700;color:var(--fg1);line-height:1.35;}
  .node .nclaim{font-size:13px;color:var(--fg2);line-height:1.5;margin-top:3px;text-wrap:pretty;}
  .node .st{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap;align-self:center;}
  .node .exp{align-self:center;font-family:var(--mono);font-size:15px;line-height:1;color:var(--fg4);background:none;border:none;cursor:pointer;padding:2px 4px;border-radius:6px;}
  .node .exp:hover{color:var(--cyan);background:var(--elev);}
  .node .body{padding:0 14px 13px 34px;display:none;} .node.open .body{display:block;}
  .node .body .row{font-family:var(--mono);font-size:11px;color:var(--fg3);line-height:1.6;margin-top:4px;}
  .node .body .row b{color:var(--fg4);font-weight:700;text-transform:uppercase;letter-spacing:.06em;font-size:9.5px;margin-right:6px;}
  .node .body .lk{display:inline-block;background:var(--elev);border:1px solid var(--border2);border-radius:6px;padding:2px 7px;margin:2px 4px 0 0;color:var(--fg3);font-size:10.5px;}
  .empty{font-family:var(--mono);font-size:12px;color:var(--fg4);padding:20px;text-align:center;}
  .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--elev);border:1px solid var(--cyan);color:var(--fg1);font-family:var(--mono);font-size:11.5px;padding:10px 16px;border-radius:9px;opacity:0;transition:.2s;pointer-events:none;z-index:40;}
  .toast.on{opacity:1;}
  .foot{margin-top:34px;padding-top:16px;border-top:1px solid var(--border);font-family:var(--mono);font-size:10.5px;color:var(--fg4);line-height:1.7;}
  @media(max-width:560px){
    .dbar{grid-template-columns:1fr auto;} .dbar .dname{text-align:left;} .dbar .track{grid-column:1/-1;order:3;}
    .node .nh{grid-template-columns:auto 1fr auto;} .rr .row{grid-template-columns:22px 1fr;} .rr .rw{grid-column:2;justify-self:start;}
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
  <div class="toast" id="toast"></div>
<script>
const NODES = __DATA__;
const META = __META__;
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));

// full node status (detail level) -> label + color
const ST = {
  "LIVE":{label:"Live",c:"var(--live)"}, "LIVE-AS-PROSE":{label:"Live (prose)",c:"var(--prose)"},
  "DRIFTED":{label:"Drifted",c:"var(--drift)"}, "STALE":{label:"Stale",c:"var(--stale)"},
};
const st = raw => ST[raw] || {label:"Unverified", c:"var(--unv)"};
// aggregate bucket (chart/skim level) -> 4 well-separated buckets, prose folds into Live
const AGG = ["LIVE","DRIFTED","STALE","UNVERIFIED"];
const ABI = {LIVE:{label:"Live",c:"var(--live)"},DRIFTED:{label:"Drifted",c:"var(--drift)"},STALE:{label:"Stale",c:"var(--stale)"},UNVERIFIED:{label:"Unverified",c:"var(--unv)"}};
const agg = raw => (raw==="LIVE"||raw==="LIVE-AS-PROSE")?"LIVE":(ABI[raw]?raw:"UNVERIFIED");
const isLive = n => agg(n.status)==="LIVE";
const byId = {}; NODES.forEach(n=>{ if(n.id) byId[n.id]=n; });

// in-degree: how many nodes reference each id in their links[]
const IND = {}; NODES.forEach(n=>(n.links||[]).forEach(l=>{ IND[l]=(IND[l]||0)+1; }));
// Two shelves. Foundational = required BY CANON (constitutional clusters), regardless of
// link-count: in-degree structurally under-weights foundations because everything
// assumes them and nothing links to them. Load-bearing = required BY REFERENCE (in-degree).
const FOUND_RE = /architecture|canon-governance|user cognition|product context|governance|design principles|leadership|rom-primitive/i;
function foundational(k){ return NODES.filter(n=>isLive(n)&&FOUND_RE.test(n.cluster||"")).map(n=>({n,deg:IND[n.id]||0})).sort((a,b)=>b.deg-a.deg||String(a.n.epoch||"z").localeCompare(String(b.n.epoch||"z"))).slice(0,k); }
function required(k, exclude){ return NODES.filter(n=>n.id&&IND[n.id]&&isLive(n)&&!(exclude&&exclude.has(n.id))).map(n=>({n,deg:IND[n.id]})).sort((a,b)=>b.deg-a.deg).slice(0,k); }
function shelfRows(list, why){ return list.map((r,i)=>`<div class="row" onclick="jumpTo('${esc(r.n.id)}')">
      <span class="rk">${i+1}</span>
      <div><div class="rt">${esc(r.n.title)}<span class="rd">${esc(r.n.domain)}</span></div><div class="rc">${esc(r.n.claim)}</div></div>
      <span class="rw">${why(r)}</span></div>`).join(""); }

function aggcounts(nodes){ const c={}; AGG.forEach(b=>c[b]=0); nodes.forEach(n=>c[agg(n.status)]++); return c; }
function domains(){ const d={}; NODES.forEach(n=>{(d[n.domain]=d[n.domain]||[]).push(n);}); return d; }
function track(c,total){ return AGG.filter(b=>c[b]).map(b=>`<span style="flex:${c[b]};background:${ABI[b].c}" title="${ABI[b].label}: ${c[b]}"></span>`).join(""); }

// shared filter state (scan <-> trenches)
let F = {domain:null, bucket:null, q:""};
const applyF = () => NODES.filter(n =>
  (!F.domain || n.domain===F.domain) && (!F.bucket || agg(n.status)===F.bucket) &&
  (!F.q || (n.title+" "+n.claim+" "+n.cluster+" "+n.provenance).toLowerCase().includes(F.q)));

// ---------- SKIM = required reading ----------
function renderSkim(){
  const total = NODES.length, c = aggcounts(NODES);
  const dm = domains(), health = Math.round(100*c.LIVE/total);
  const found = foundational(6);
  const foundIds = new Set(found.map(r=>r.n.id));
  const req = required(8, foundIds);
  const drift = NODES.filter(n=>agg(n.status)==="DRIFTED");
  const leg = AGG.filter(b=>c[b]).map(b=>`<span class="it"><span class="sw" style="background:${ABI[b].c}"></span>${ABI[b].label} ${c[b]}</span>`).join("");
  const foundRows = shelfRows(found, r=>esc(r.n.cluster)) || `<div class="rc" style="padding:8px 10px">No constitutional nodes graded live.</div>`;
  const rows = shelfRows(req, r=>`referenced ${r.deg}&times;`) || `<div class="rc" style="padding:8px 10px">No cross-referenced live nodes yet.</div>`;
  document.getElementById("skim").innerHTML = `
    <div class="bignum"><span class="n">${health}<span style="font-size:.5em">%</span></span><span class="l">of ${total} load-bearing nodes are <b style="color:var(--live)">live</b> and hold against the repo. ${c.DRIFTED} drifted &middot; ${c.STALE} stale.</span></div>
    <div class="hbar">${track(c,total)}</div><div class="hleg">${leg}</div>
    <div class="rr-h">Required reading &middot; foundational <small>read to understand the world &mdash; required by canon, not by link-count</small></div>
    <div class="rr">${foundRows}</div>
    <div class="rr-h">Required reading &middot; load-bearing <small>read to do the work &mdash; ranked by how often the corpus leans on it, live only</small></div>
    <div class="rr">${rows}</div>
    ${drift.length?`<div class="attn"><b>Needs attention:</b> ${drift.length} claim${drift.length!=1?"s have":" has"} drifted from the record. ${esc((drift[0]||{}).title||"")}${drift.length>1?`, +${drift.length-1} more`:""}.</div>`:""}
    <div class="jump">Go deeper: <a onclick="setAlt('scan')">the informatics &rarr;</a> &middot; <a onclick="setAlt('trenches')">every node &rarr;</a></div>`;
}

// ---------- SCAN = informatics ----------
function renderScan(){
  const dm = domains(), total = NODES.length, c = aggcounts(NODES);
  const bars = Object.keys(dm).sort((a,b)=>dm[b].length-dm[a].length).map(d=>{
    const nodes=dm[d], cc=aggcounts(nodes);
    return `<div class="dbar ${F.domain===d?'sel':''}" onclick="toggleDomain('${esc(d)}')">
      <span class="dname">${esc(d)}</span><div class="track">${track(cc,nodes.length)}</div><span class="dtot">${nodes.length}</span></div>`;
  }).join("");
  const leg = AGG.filter(b=>c[b]).map(b=>`<span class="it ${F.bucket&&F.bucket!==b?'off':''}" onclick="toggleBucket('${b}')"><span class="sw" style="background:${ABI[b].c}"></span>${ABI[b].label} <b>${c[b]}</b></span>`).join("");
  const active = F.domain||F.bucket;
  document.getElementById("scan").innerHTML = `
    <div class="sech"><span>Nodes by domain &times; status &middot; click a bar to filter</span>${active?`<span class="clr" onclick="clearF()">clear filter</span>`:""}</div>
    <div class="dbars">${bars}</div>
    <div class="leg">${leg}</div>
    <div class="jump"><a onclick="setAlt('trenches')">Open the Trenches${active?" (filtered)":""} &rarr;</a></div>`;
}

// ---------- TRENCHES = full + per-row export ----------
function renderTrenches(){
  const rows = applyF(), g = {};
  rows.forEach(n=>{ (g[n.domain]=g[n.domain]||{}); (g[n.domain][n.cluster]=g[n.domain][n.cluster]||[]).push(n); });
  let out = "";
  Object.keys(g).sort().forEach(d=>Object.keys(g[d]).sort().forEach(cl=>{
    const list = g[d][cl];
    out += `<div class="grp"><div class="gh">${esc(d)} <span class="gc">/ ${esc(cl)} &middot; ${list.length}</span></div>`;
    list.forEach((n,i)=>{
      const s = st(n.status), nid = (n.id||n.title).replace(/[^a-z0-9]/gi,"_")+"_"+i;
      const links = (n.links||[]).map(l=>`<span class="lk">${esc(l)}</span>`).join("");
      out += `<div class="node" data-nid="${esc(n.id)}" id="N_${nid}">
        <div class="nh">
          <span class="sd" style="background:${s.c}"></span>
          <div class="nt" onclick="this.closest('.node').classList.toggle('open')"><div class="ntitle">${esc(n.title)}</div><div class="nclaim">${esc(n.claim)}</div></div>
          <span class="st" style="color:${s.c};border:1px solid ${s.c}">${esc(s.label)}</span>
          <button class="exp" title="Export this node as a self-contained bundle" onclick="exportNode('${esc(n.id)}','${nid}')">&#8595;</button>
        </div>
        <div class="body">
          ${n.note?`<div class="row"><b>Note</b>${esc(n.note)}</div>`:""}
          ${n.provenance?`<div class="row"><b>Source</b>${esc(n.provenance)}</div>`:""}
          ${links?`<div class="row"><b>Links</b>${links}</div>`:""}
        </div></div>`;
    });
    out += `</div>`;
  }));
  const active = F.domain||F.bucket||F.q;
  document.getElementById("trenches").innerHTML = `
    <div class="tbar"><input id="q" placeholder="search claims, titles, provenance..." value="${esc(F.q)}">
      <span class="cnt">${rows.length} / ${NODES.length} nodes</span>${active?`<span class="clr" onclick="clearF()">clear</span>`:""}</div>
    ${out || '<div class="empty">No nodes match this filter.</div>'}`;
  const q = document.getElementById("q");
  q.addEventListener("input", e=>{ F.q=e.target.value.toLowerCase(); const p=q.selectionStart; renderTrenches(); const nq=document.getElementById("q"); nq.focus(); nq.setSelectionRange(p,p); });
}

// ---- per-row export: a self-contained bundle for one node ----
function exportNode(id, domFallback){
  const n = byId[id] || NODES.find(x=>((x.id||x.title).replace(/[^a-z0-9]/gi,"_"))===domFallback.replace(/_\d+$/,"")) ;
  if(!n){ showToast("node not found"); return; }
  const s = st(n.status);
  const links = (n.links||[]).map(l=>`<span class="lk">${esc(l)}</span>`).join("");
  const doc = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(n.title)} &middot; ARCS Almanac</title><meta name="robots" content="noindex">
<style>:root{--bg:#020408;--fg1:#eff4fa;--fg2:#c6d3e1;--fg3:#a3b4c6;--fg4:#7e8fa4;--border:#1e2c3a;--elev:#0e141d;--cyan:#00F0FF;--mono:'JetBrains Mono',ui-monospace,monospace;--sans:'Inter',system-ui,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}html{background:var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased}
body{max-width:640px;margin:0 auto;padding:42px 24px}.eb{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan)}
.meta{font-family:var(--mono);font-size:10.5px;color:var(--fg4);letter-spacing:.05em;text-transform:uppercase;margin:20px 0 6px}
h1{font-size:24px;font-weight:800;letter-spacing:-.02em;line-height:1.2;margin-bottom:4px;text-wrap:balance}
.pill{display:inline-flex;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:4px 10px;border-radius:999px;margin-top:8px;color:${s.c};border:1px solid ${s.c}}
.claim{font-size:16px;line-height:1.6;color:var(--fg2);margin:18px 0;text-wrap:pretty}
.card{border:1px solid var(--border);border-radius:11px;padding:15px 16px;background:var(--elev);margin-top:12px}
.card b{display:block;font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg4);margin-bottom:6px}
.card .v{font-family:var(--mono);font-size:12px;color:var(--fg3);line-height:1.6}
.lk{display:inline-block;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:3px 9px;margin:2px 5px 0 0;color:var(--fg3);font-size:11px;font-family:var(--mono)}
.foot{margin-top:30px;padding-top:16px;border-top:1px solid var(--border);font-family:var(--mono);font-size:10px;color:var(--fg4);line-height:1.7}</style></head>
<body><div class="eb">&#9670; ARCS Almanac &middot; one node</div>
<div class="meta">${esc(n.domain)} / ${esc(n.cluster)}</div><h1>${esc(n.title)}</h1><span class="pill">${esc(s.label)}</span>
<p class="claim">${esc(n.claim)}</p>
${n.note?`<div class="card"><b>Note</b><div class="v">${esc(n.note)}</div></div>`:""}
${n.provenance?`<div class="card"><b>Source</b><div class="v">${esc(n.provenance)}</div></div>`:""}
${links?`<div class="card"><b>Links</b><div class="v">${links}</div></div>`:""}
<div class="foot">Exported from the ARCS Almanac (${esc(META.generated)}). A graded snapshot, not live. Internal &mdash; keep local.</div></body></html>`;
  try{
    const blob = new Blob([doc], {type:"text/html"});
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = "almanac-" + (n.id||n.title.slice(0,32)).replace(/[^a-z0-9]/gi,"-").toLowerCase() + ".html";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
    showToast("exported " + a.download);
  }catch(e){ showToast("export blocked here — open the file in a browser"); }
}
let toastT; function showToast(m){ const t=document.getElementById("toast"); t.textContent=m; t.classList.add("on"); clearTimeout(toastT); toastT=setTimeout(()=>t.classList.remove("on"),2600); }

// ---- interactions ----
function setAlt(a){
  ["skim","scan","trenches"].forEach(s=>document.getElementById(s).hidden=(s!==a));
  document.querySelectorAll("#alt button").forEach(b=>b.classList.toggle("on", b.dataset.alt===a));
  ({skim:renderSkim,scan:renderScan,trenches:renderTrenches})[a]();
  window.scrollTo({top:0,behavior:"instant"});
}
function jumpTo(id){ setAlt("trenches"); const el=document.querySelector(`.node[data-nid="${CSS.escape(id)}"]`); if(el){ el.classList.add("open"); el.scrollIntoView({block:"center"}); el.style.transition="box-shadow .2s"; el.style.boxShadow="0 0 0 1px var(--cyan)"; setTimeout(()=>el.style.boxShadow="",1400);} }
function toggleDomain(d){ F.domain=F.domain===d?null:d; renderScan(); }
function toggleBucket(b){ F.bucket=F.bucket===b?null:b; renderScan(); }
function clearF(){ F={domain:null,bucket:null,q:""}; renderScan(); if(!document.getElementById("trenches").hidden) renderTrenches(); }
document.querySelectorAll("#alt button").forEach(b=>b.addEventListener("click",()=>setAlt(b.dataset.alt)));
renderSkim();
</script>
</body>
</html>
"""


def render(nodes, meta):
    live = sum(1 for n in nodes if n["status"] in ("LIVE", "LIVE-AS-PROSE"))
    drift = sum(1 for n in nodes if n["status"] == "DRIFTED")
    stale = sum(1 for n in nodes if n["status"] == "STALE")
    doms = sorted({n["domain"] for n in nodes})
    sub = (f"{len(nodes)} nodes &middot; {len(doms)} domains &middot; {live} live &middot; "
           f"{drift} drifted &middot; {stale} stale &middot; graded {meta['generated']}")
    foot = ("The Almanac &mdash; the graded, dated state of the corpus, read through the Reader at three "
            "altitudes. A snapshot, not live: statuses graded against the repo at render time; re-run the "
            "auditors to refresh. Required reading is ranked by reference-density (in-degree), live only. "
            "Internal research &mdash; render local, never a public host. scripts/research_render.py.")
    return (TEMPLATE
            .replace("__TITLE__", html.escape(meta["title"]))
            .replace("__EYEBROW__", html.escape(meta["eyebrow"]))
            .replace("__H1__", html.escape(meta["h1"]))
            .replace("__SUB__", sub).replace("__FOOT__", foot)
            .replace("__DATA__", json.dumps(nodes, ensure_ascii=False))
            .replace("__META__", json.dumps(meta, ensure_ascii=False)))


def main():
    args = sys.argv[1:]
    if args and args[0].endswith((".html", ".htm")):
        out_path, digests = args[0], args[1:]
    else:
        out_path = os.path.join(ROOT, "_ARTIFACTS/atlas/atlas-almanac.html")
        digests = args or sorted(glob.glob(os.path.join(ROOT, "_ARTIFACTS/atlas/digest-*.json")))
    if not digests:
        print("no digests found", file=sys.stderr); sys.exit(1)
    nodes = load_digests(digests)
    meta = {
        "title": "ARCS Almanac · read through the Reader",
        "eyebrow": "ARCS · the Almanac",
        "h1": "The state of what ARCS knows",
        "generated": datetime.date.today().isoformat(),
        "sources": [os.path.basename(d) for d in digests],
    }
    open(out_path, "w", encoding="utf-8").write(render(nodes, meta))
    print(f"rendered {len(nodes)} nodes -> {out_path}")


if __name__ == "__main__":
    main()
