#!/usr/bin/env python3
"""
forge_counterpart.py -- the parameterized counterpart-forge generator.

Deterministic SSOT -> template -> page. One token source (canonical ARCS
dark-cockpit, == src/ui-kit/recoil-report/_tokens.css == src/document/tokens.ts,
ADR-009/031). No per-page :root drift. Follows the block-renderer spine of
scripts/recoil_brief.py; extends it with the crisp counterpart surfaces
extracted from Robin (the platinum master, blueprint sec 9):

  receipt   THE RECEIPT CLOSE  -- bet-filed-before -> scored-after (crispest proof)

Companion scripts:
  gen_receipt_close.py   score an ex-ante receipt against its recoil -> receipt SSOT
  recoil_brief.py        the recoil ("before & after") surface (already canonical)

Crispness rules are GENERATION CONSTRAINTS, not hand-discipline (blueprint sec 9):
  - real-call story + verbatim quotes over abstract diagrams
  - the receipt-close is first-class: predicted-before vs actual-after, scored
  - single-call counterparts render single-call, no multi-call arc

Verify gate (blueprint sec 4) + honesty gate (blueprint sec 11) run on every
generated page and can be invoked standalone (--verify-only).

Usage:
  python3 scripts/forge_counterpart.py --surface receipt \
      --data runtime/recoil/generated/<id>-receipt.json --out public/<name>-receipt.html
  python3 scripts/forge_counterpart.py --verify-only --file public/<name>-receipt.html
"""
import argparse, html, json, os, re, sys

E = lambda s: html.escape(str(s), quote=True)
# Attribute encoder for authored values that may already carry HTML entities
# (e.g. &rsquo;, &#183;): make them attribute-safe (escape " and <) WITHOUT
# re-escaping the & of an existing entity. Text-content authored fields are
# inserted raw; only machine/plain values go through E().
A = lambda s: str(s).replace("<", "&lt;").replace('"', "&quot;")

# ---------------------------------------------------------------------------
# CANONICAL TOKENS -- the single source. Mirrors src/ui-kit/recoil-report/_tokens.css.
# Any surface the forge emits declares THIS :root and nothing else. Omakase house
# style (#0B0B0C / #C9A227 / Helvetica) stays scoped to the omakase/louisville
# family and never leaks into the counterpart recoil family (blueprint sec 10).
# ---------------------------------------------------------------------------
TOKENS = """:root{
  --bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--elevated:#111827;--border:#1e293b;
  --text:#e2e8f0;--muted:#94a3b8;--dimmed:#64748b;
  --cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;
  --cyan-bg:rgba(0,240,255,.07);--green-bg:rgba(0,255,157,.07);--gold-bg:rgba(255,215,0,.07);--red-bg:rgba(255,77,109,.07);
  --r-sm:4px;--r-md:8px;--r-lg:12px;
  --mono:'GeistMono','JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
  --sans:'InstrumentSans','Work Sans',system-ui,-apple-system,sans-serif;
  --display:'BricolageGrotesque','Work Sans',system-ui,sans-serif;
}"""

# ---------------------------------------------------------------------------
# #tip -- the canonical data-vis hover/tap tooltip component (blueprint sec 10).
# Extracted verbatim from robin.html so every recoil/arc chart gets the same
# working hover + touch-tap behavior instead of being hand-inlined per page.
# CSS + JS + the single <div id="tip"></div> sink. Elements opt in with
# [data-tip] and carry data-c (accent), data-t (label), data-n (note).
# ---------------------------------------------------------------------------
TIP_CSS = (".hit{cursor:pointer}"
    "#tip{position:fixed;z-index:80;max-width:min(280px,88vw);pointer-events:none;opacity:0;"
    "transition:opacity .12s;background:#0b0f16;border:1px solid var(--tc,#1e293b);border-radius:10px;"
    "padding:11px 13px;box-shadow:0 8px 30px rgba(0,0,0,.55)}"
    "#tip.on{opacity:1}"
    "#tip .tt{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
    "color:var(--tc,#94a3b8);margin-bottom:6px}"
    "#tip .tn{font-size:13px;color:var(--text);line-height:1.45}"
    "@media(hover:none){.hit{cursor:default}}")

TIP_JS = ("(function(){var tip=document.getElementById('tip');if(!tip)return;"
    "function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}"
    "function show(el,e){var c=el.getAttribute('data-c')||'#94a3b8';tip.style.setProperty('--tc',c);"
    "tip.innerHTML='<div class=\"tt\">'+esc(el.getAttribute('data-t'))+'</div><div class=\"tn\">'+esc(el.getAttribute('data-n'))+'</div>';"
    "tip.classList.add('on');move(e);}"
    "function move(e){var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+16,y=e.clientY+16;"
    "if(x+w>window.innerWidth-8)x=e.clientX-w-16;if(y+h>window.innerHeight-8)y=e.clientY-h-16;"
    "tip.style.left=x+'px';tip.style.top=y+'px';}"
    "function hide(){tip.classList.remove('on');}"
    "document.querySelectorAll('[data-tip]').forEach(function(el){"
    "el.addEventListener('mouseenter',function(e){show(el,e);});el.addEventListener('mousemove',move);"
    "el.addEventListener('mouseleave',hide);"
    "el.addEventListener('click',function(e){e.stopPropagation();var r=el.getBoundingClientRect();"
    "show(el,{clientX:r.left+r.width/2,clientY:r.top+r.height/2});});});"
    "document.addEventListener('click',hide);})();")

# pw-gate (first-name gate) -- reused from recoil_brief.py, canonical tokens.
GATE_CSS = ("#pw-gate{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;"
    "z-index:100;flex-direction:column;gap:16px;}#pw-gate.hidden{display:none;}"
    ".pw-label{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed);}"
    ".pw-input{background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:16px;"
    "padding:10px 16px;outline:none;width:200px;text-align:center;letter-spacing:.1em;}"
    ".pw-input:focus{border-color:var(--cyan);}.pw-input.shake{animation:shake .3s ease;border-color:var(--red);}"
    "@keyframes shake{0%,100%{transform:translateX(0);}20%,60%{transform:translateX(-6px);}40%,80%{transform:translateX(6px);}}")

VERCEL = '<script defer src="/_vercel/insights/script.js"></script>'

# ---------------------------------------------------------------------------
# Receipt Studio panel (blueprint sec 7) -- the interactive file/score/close
# loop, wired to the registry route /api/receipts/studio/<tenant>. Rendered on a
# receipt surface when its SSOT carries a `studio` block. Same-origin fetch works
# only because the counterpart subdomain rewrite excludes /api (negative
# lookahead, mirroring louisville.arcs.care). The route fail-closes until the
# tenant's DB secret is set, so the panel shows a friendly error until then.
# Portable JSON: the export button downloads the receipt as JSON that round-trips
# to `forge_counterpart.py --surface receipt`.
# ---------------------------------------------------------------------------
STUDIO_CSS = (
    ".studio{border:1px solid rgba(0,240,255,.28);border-radius:12px;background:var(--surface);padding:20px 22px;margin-top:16px}"
    ".studio h3{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);margin-bottom:6px}"
    ".studio .sdesc{font-size:13px;color:var(--muted);line-height:1.55;margin-bottom:16px}"
    ".sfield{display:flex;flex-direction:column;gap:5px;margin-bottom:11px}"
    ".sfield label{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed)}"
    ".sfield input,.sfield textarea,.sfield select{background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:var(--sans);font-size:13.5px;padding:9px 12px;outline:none;width:100%}"
    ".sfield textarea{min-height:56px;resize:vertical}.sfield input:focus,.sfield textarea:focus,.sfield select:focus{border-color:var(--cyan)}"
    ".sbtn{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);background:var(--cyan-bg);border:1px solid rgba(0,240,255,.35);border-radius:8px;padding:10px 15px;cursor:pointer}"
    ".sbtn:hover{background:rgba(0,240,255,.12)}.sbtn.ghost{color:var(--muted);background:none;border-color:var(--border)}"
    ".smsg{font-family:var(--mono);font-size:10px;letter-spacing:.04em;margin-top:10px;min-height:14px}"
    ".smsg.ok{color:var(--green)}.smsg.err{color:var(--red)}"
    ".slist{display:grid;gap:9px;margin-top:16px}"
    ".sr{border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:13px 15px}"
    ".srh{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:6px}"
    ".srb{font-size:13px;color:var(--text);line-height:1.45}"
    ".srst{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;padding:2px 8px;border-radius:100px;border:1px solid var(--sc);color:var(--sc);flex:none}"
    ".srmeta{font-family:var(--mono);font-size:9px;letter-spacing:.04em;color:var(--dimmed);margin-top:6px}"
    ".srclose{margin-top:10px;padding-top:10px;border-top:1px solid var(--border);display:none}.sr.open .srclose{display:block}"
    ".srrow{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}"
)


def _studio_panel(st):
    tenant = st["tenant"]
    author = st.get("author", "ZACH")
    title = st.get("title", "Receipt Studio")
    desc = st.get("desc", "File a bet before the call, score it after. A receipt is just JSON: the bet, the falsifier, the score-back date. It cannot be closed as a memory, only scored against reality.")
    base = f"/api/receipts/studio/{tenant}"
    # The JS is deliberately vanilla + inline (external JS cannot load on a
    # wildcard-rewrite subdomain). sessionId lives in localStorage = the bearer token.
    js = (
        "(function(){var BASE='" + base + "',AUTHOR='" + author + "';"
        "var KEY='studio-" + tenant + "-session';"
        "var sid=localStorage.getItem(KEY);if(!sid){sid=(self.crypto&&crypto.randomUUID?crypto.randomUUID():'s'+Math.random().toString(36).slice(2)+Date.now());localStorage.setItem(KEY,sid);}"
        "var $=function(id){return document.getElementById(id);};"
        "function esc(s){return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}"
        "function msg(t,cls){var m=$('st-msg');m.textContent=t;m.className='smsg '+(cls||'');}"
        "var SC={OPEN:'#FFD700',SCORED:'#00FF9D',KILLED:'#FF4D6D',SCALED:'#00F0FF'};"
        "function receiptJSON(r){return {receipt_type:'session receipt',tenant:'" + tenant + "',sessionId:r.sessionId,author:r.author,bet:r.bet,falsifier:r.falsifier,assumptions:r.assumptions,atRisk:r.atRisk,scoreBackDate:r.scoreBackDate,status:r.status,outcome:r.outcome,variance:r.variance,lesson:r.lesson,filed:r.createdAt};}"
        "function dl(r){var blob=new Blob([JSON.stringify(receiptJSON(r),null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='receipt-'+(r.id||'draft')+'.json';a.click();}"
        "function render(rows){var L=$('st-list');if(!rows.length){L.innerHTML='';return;}L.innerHTML=rows.map(function(r){var sc=SC[r.status]||'#94a3b8';var open=r.status==='OPEN';"
        "return '<div class=\"sr'+(open?' open':'')+'\" data-id=\"'+esc(r.id)+'\"><div class=\"srh\"><div class=\"srb\">'+esc(r.bet)+'</div><span class=\"srst\" style=\"--sc:'+sc+'\">'+esc(r.status)+'</span></div>'"
        "+'<div class=\"srmeta\">falsifier: '+esc(r.falsifier)+' &middot; score-back '+esc((r.scoreBackDate||'').slice(0,10))+'</div>'"
        "+(r.outcome?'<div class=\"srmeta\" style=\"color:var(--text)\">outcome: '+esc(r.outcome)+(r.lesson?' &middot; lesson: '+esc(r.lesson):'')+'</div>':'')"
        "+'<div class=\"srclose\"><div class=\"sfield\"><label>Observed outcome</label><textarea data-f=\"outcome\"></textarea></div>'"
        "+'<div class=\"sfield\"><label>Variance / lesson</label><input data-f=\"lesson\"></div>'"
        "+'<div class=\"srrow\"><button class=\"sbtn\" data-act=\"score\" data-v=\"SCORED\">Score it</button><button class=\"sbtn ghost\" data-act=\"score\" data-v=\"KILLED\">Kill</button></div></div>'"
        "+'<div class=\"srrow\"><button class=\"sbtn ghost\" data-act=\"export\">Export JSON</button></div></div>';}).join('');bind(rows);}"
        "function bind(rows){var by={};rows.forEach(function(r){by[r.id]=r;});"
        "$('st-list').querySelectorAll('[data-act]').forEach(function(b){b.addEventListener('click',function(){var card=b.closest('.sr'),id=card.getAttribute('data-id'),r=by[id];"
        "if(b.getAttribute('data-act')==='export'){dl(r);return;}"
        "var outcome=(card.querySelector('[data-f=outcome]')||{}).value||'';var lesson=(card.querySelector('[data-f=lesson]')||{}).value||'';"
        "fetch(BASE,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:sid,id:id,status:b.getAttribute('data-v'),outcome:outcome,lesson:lesson})}).then(function(x){return x.json();}).then(function(d){if(d.error){msg(d.error,'err');return;}msg('Scored.','ok');load();}).catch(function(){msg('Network error scoring.','err');});});});}"
        "function load(){fetch(BASE+'?sessionId='+encodeURIComponent(sid)).then(function(x){return x.json();}).then(function(d){if(d.error){msg(d.error,'err');return;}if(d.receipts)render(d.receipts);}).catch(function(){msg('Could not load your receipts. If you just filed one, do not re-file; reload in a moment.','err');});}"
        "$('st-file').addEventListener('click',function(){var bet=$('st-bet').value.trim(),fal=$('st-fal').value.trim(),sb=$('st-sb').value;"
        "if(!bet||!fal||!sb){msg('Bet, falsifier, and score-back date are all required.','err');return;}"
        "fetch(BASE,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId:sid,author:AUTHOR,bet:bet,falsifier:fal,scoreBackDate:sb,assumptions:$('st-ass').value.trim()||null})})"
        ".then(function(x){return x.json();}).then(function(d){if(d.error){msg(d.error,'err');return;}msg('Sealed. The bet is filed and cannot be un-filed.','ok');$('st-bet').value='';$('st-fal').value='';$('st-ass').value='';load();}).catch(function(){msg('Network error filing.','err');});});"
        "load();})();"
    )
    return (
        f'<section class="sec"><div class="studio"><h3>{E(title)}</h3><p class="sdesc">{desc}</p>'
        f'<div class="sfield"><label>The bet (a decision that can be wrong)</label><textarea id="st-bet" placeholder="Lead with one narrow thing in his register, name his own advice back..."></textarea></div>'
        f'<div class="sfield"><label>The falsifier (what would prove it wrong)</label><textarea id="st-fal" placeholder="If it cannot fail, it is not a receipt."></textarea></div>'
        f'<div class="sfield"><label>Assumptions (optional)</label><input id="st-ass"></div>'
        f'<div class="sfield"><label>Score-back date</label><input id="st-sb" type="date"></div>'
        f'<div class="srrow"><button id="st-file" class="sbtn">File the bet</button></div>'
        f'<div id="st-msg" class="smsg"></div><div id="st-list" class="slist"></div></div>'
        f'<script>{js}</script></section>'
    )


# ===========================================================================
# RECEIPT-CLOSE SURFACE  (blueprint sec 9: robin-receipt = the crispest proof)
# The forensic close: a bet filed BEFORE (in the codex) scored AFTER against
# reality. Reverse-listening + deep recall, Kairos write-locked, status-at-open
# -> status-at-close, priors updated. Canonical tokens (no omakase drift).
# ===========================================================================
RECEIPT_CSS = TOKENS + """
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg)}
.recoil{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5;
  background-image:radial-gradient(1200px 640px at 50% -8%,rgba(0,240,255,.06),transparent 62%);min-height:100%;padding:0 0 90px}
.recoil ::selection{background:rgba(0,240,255,.24);color:#fff}
.wrap{max-width:820px;margin:0 auto;padding:0 26px}
.recoil h1,.recoil h3{text-wrap:balance;font-weight:700;letter-spacing:-.015em;font-family:var(--display)}
.recoil p{text-wrap:pretty}
.cover{padding:56px 0 8px;position:relative}
.glyph{position:absolute;top:44px;right:2px;font-size:76px;color:var(--cyan);opacity:.08;line-height:1;user-select:none}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan);
  border:1px solid rgba(0,240,255,.34);border-radius:100px;padding:5px 11px}
.cover h1{font-size:clamp(28px,3.2vw + 14px,42px);line-height:1.08;}
.cover .sub{margin-top:14px;font-size:16.5px;color:var(--text);opacity:.9;line-height:1.55}
.cover .meta{margin-top:16px;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;color:var(--muted);line-height:1.9}
.sec{margin-top:46px}
.eyebrow{font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);
  display:flex;align-items:center;gap:12px;margin-bottom:18px}
.eyebrow::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--border),transparent)}
.eyebrow b{color:var(--cyan)}
.eyebrow2{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:22px 2px 12px}
.lede{font-size:15px;color:var(--text);opacity:.86;line-height:1.6;margin-bottom:18px}
.betbox{border:1px solid rgba(255,215,0,.30);border-radius:12px;
  background:linear-gradient(180deg,var(--gold-bg),transparent);padding:20px 22px;margin-bottom:16px}
.betk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--gold);font-weight:700;display:block;margin-bottom:8px}
.betbox p{font-size:15px;color:var(--text);line-height:1.55}
.preds{display:grid;gap:10px}
.pred{display:grid;grid-template-columns:168px 1fr;gap:18px;align-items:center;border:1px solid var(--border);
  border-radius:10px;background:var(--surface);padding:14px 18px}
.predgauge{display:flex;align-items:center;gap:11px}
.predbar{flex:1;height:7px;background:#0d0d0f;border:1px solid var(--border);border-radius:100px;overflow:hidden}
.predfill{height:100%;background:linear-gradient(90deg,rgba(255,215,0,.5),var(--gold));border-radius:100px}
.predpct{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--gold);width:34px;text-align:right;font-variant-numeric:tabular-nums;flex:none}
.predclaim{font-size:13.5px;color:var(--text);opacity:.92;line-height:1.48}
.predmeta{font-family:var(--mono);font-size:9px;letter-spacing:.04em;color:var(--dimmed);margin-top:5px;text-transform:uppercase}
.kairoslock{border:1px solid rgba(0,240,255,.3);border-radius:12px;background:linear-gradient(180deg,var(--cyan-bg),transparent 65%);padding:20px 22px;margin-top:16px}
.kairoslock.pre{border-color:rgba(255,215,0,.28);background:linear-gradient(180deg,var(--gold-bg),transparent 65%)}
.klk{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--cyan);font-weight:700;display:block;margin-bottom:10px}
.kairoslock.pre .klk{color:var(--gold)}
.kairoslock blockquote{font-size:clamp(17px,1.2vw+12px,21px);font-weight:600;line-height:1.4;color:var(--text);margin-bottom:12px}
.kairoslock p{font-size:13.5px;color:var(--muted);line-height:1.58}
.manifold{border:1px solid var(--border);border-radius:12px;background:linear-gradient(180deg,var(--surface),var(--surface2));padding:16px 14px 8px}
.mcap{margin-top:12px;font-size:13px;color:var(--muted);line-height:1.6;}
.rlwalk{display:grid;gap:10px}
.beat{border:1px solid var(--dcb,var(--border));border-radius:11px;background:var(--surface);padding:16px 18px}
.beat.compressed{opacity:.72;padding:13px 18px;background:var(--surface2)}
.beat.dilated{background:linear-gradient(180deg,var(--cyan-bg),transparent 60%);box-shadow:0 0 0 1px rgba(0,240,255,.18)}
.beath{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:8px}
.beatt{font-family:var(--mono);font-size:10px;letter-spacing:.12em;font-weight:700;color:var(--dc)}
.beatdil{font-family:var(--mono);font-size:8px;letter-spacing:.12em;color:var(--dimmed)}
.beatlabel{font-size:15px;font-weight:700;color:var(--text);margin-bottom:7px}
.beat.compressed .beatlabel{font-size:13.5px;font-weight:600}
.beatq{font-size:13.5px;font-style:italic;color:var(--text);opacity:.9;line-height:1.5;margin-bottom:8px}
.beat.compressed .beatq{font-size:12.5px;margin-bottom:5px}
.beat.dilated .beatq{font-size:15.5px;opacity:1}
.beatread{font-size:13px;color:var(--muted);line-height:1.58;border-top:1px solid var(--border);padding-top:8px}
.closestatus{border:1px solid rgba(0,255,157,.4);border-radius:12px;background:linear-gradient(180deg,var(--green-bg),transparent);padding:20px 22px;margin-bottom:18px}
.csk{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--green);font-weight:700;margin-right:12px}
.csv{font-family:var(--mono);font-size:12px;letter-spacing:.1em;color:var(--green);font-weight:700}
.closestatus p{font-size:14.5px;color:var(--text);opacity:.9;line-height:1.55;margin-top:10px}
.scard{display:grid;gap:10px}
.scrow{display:grid;grid-template-columns:78px 1fr 120px;gap:16px;align-items:start;border:1px solid var(--border);border-radius:10px;background:var(--surface);padding:14px 16px}
.scv{font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;font-weight:700;color:var(--vc);border:1px solid var(--vc);border-radius:100px;padding:4px 0;text-align:center}
.scl{font-family:var(--mono);font-size:8px;letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed);display:block;margin-bottom:2px}
.scp{font-size:13px;color:var(--muted);line-height:1.45;margin-bottom:8px}
.sco{font-size:13px;color:var(--text);opacity:.9;line-height:1.45}
.scd{font-family:var(--mono);font-size:10px;color:var(--muted);line-height:1.5;letter-spacing:.02em}
.nns-wrap{display:grid;gap:10px}
.nn{border:1px solid rgba(0,240,255,.26);border-radius:11px;background:var(--surface);padding:16px 18px}
.nnk{font-family:var(--mono);font-size:8.5px;letter-spacing:.16em;color:var(--cyan);font-weight:700;margin-bottom:7px}
.nns{font-size:15px;font-weight:700;color:var(--text);margin-bottom:6px}
.nnq{font-size:13px;font-style:italic;color:var(--muted);line-height:1.5;margin-bottom:8px}
.nnu{font-size:13px;color:var(--text);opacity:.86;line-height:1.56}.nnu b{color:var(--text);opacity:1}
.posterior{border:1px solid rgba(0,240,255,.28);border-radius:12px;background:linear-gradient(180deg,var(--cyan-bg),transparent 60%);padding:20px 22px;margin-top:18px}
.pok{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--cyan);font-weight:700;display:block;margin-bottom:12px}
.posterior p{font-size:14px;color:var(--text);opacity:.9;line-height:1.58;margin-bottom:8px}.posterior b{color:var(--text);opacity:1}
.powedge{font-size:15px !important;opacity:1 !important}
.ponote{color:var(--muted) !important;font-size:13px !important;border-top:1px solid var(--border);padding-top:10px;margin-top:4px}
.gapflag{border:1px dashed var(--gold);border-radius:11px;background:var(--gold-bg);padding:16px 18px;margin-top:12px}
.gapflag .gk{font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:8px}
.gapflag p{font-size:13.5px;color:var(--text);opacity:.9;line-height:1.55}
.foot{margin-top:52px;padding-top:18px;border-top:1px solid var(--border);text-align:center;
  font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--dimmed);line-height:2}
.foot b{color:var(--cyan)}
@media(max-width:680px){.pred,.scrow{grid-template-columns:1fr;gap:8px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

# beat/verdict color mapping -- CANONICAL (was omakase in robin-receipt.html).
# Dilation color-codes each beat via the TAG color (--dc) + a compliant full 1px
# accent border (--dcb, all four sides -- not a side-tab, so it passes the
# impeccable craft-floor "no colored border-left >1px on callouts" rule).
BEAT_TAG = {"real": "var(--gold)", "dilated": "var(--cyan)", "compressed": "var(--dimmed)"}
BEAT_BORDER = {"real": "rgba(255,215,0,.30)", "dilated": "rgba(0,240,255,.30)", "compressed": "rgba(100,116,139,.28)"}
VERDICT_COLOR = {"HIT": "#00FF9D", "MISS": "#FF4D6D", "PARTIAL": "#FFD700"}


def _waveform_svg(wf):
    """Compute the resonance waveform SVG from points[{key,label,tip,v(0..100),kairos}].
    Deterministic geometry. Each point drives the CANONICAL #tip component (blueprint
    sec 10): a visible dot + a transparent r=16 hit overlay carrying data-tip so every
    arc chart gets the same working hover + touch-tap tooltip (not a native <title>).
    v is the resonance height 0..100 (100 = top of chart)."""
    pts = wf["points"]
    n = len(pts)
    W, H, PT, PB, PL, PR = 720, 200, 28, 48, 16, 16
    xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
    ys = [PT + (H - PT - PB) * (1 - (float(p.get("v", 50)) / 100.0)) for p in pts]
    line = "M" + " L".join(f"{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
    area = (f"M{xs[0]:.1f},{H-PB:.1f} L" + " L".join(f"{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
            + f" L{xs[-1]:.1f},{H-PB:.1f} Z")
    dots, hits, labels = "", "", ""
    for i, p in enumerate(pts):
        kairos = bool(p.get("kairos"))
        c = "#00F0FF" if kairos else ("#94a3b8" if p.get("v", 50) >= 55 else "#64748b")
        r = 6.5 if kairos else 3.5
        dots += f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="{r}" fill="{c}" stroke="#020408" stroke-width="1.5"/>'
        hits += (f'<circle class="hit" cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="16" fill="transparent" data-tip '
                 f'data-c="{c}" data-t="{A(p.get("key",""))}" data-n="{A(p.get("tip",""))}"/>')
        if kairos:
            labels += (f'<text x="{xs[i]:.1f}" y="{ys[i]-14:.1f}" text-anchor="middle" fill="#00F0FF" '
                       f'font-family="ui-monospace,monospace" font-size="9.5" letter-spacing="0.05em">KAIROS</text>')
        labels += (f'<text x="{xs[i]:.1f}" y="{H-PB+15:.1f}" text-anchor="middle" fill="#64748b" '
                   f'font-family="ui-monospace,monospace" font-size="8">{E(p.get("label", p.get("key","")))}</text>')
    return (f'<div class="manifold"><svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" '
            f'role="img" aria-label="Resonance waveform">'
            f'<defs><linearGradient id="mf" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#00F0FF" stop-opacity="0.16"/><stop offset="1" stop-color="#00F0FF" stop-opacity="0"/></linearGradient></defs>'
            f'<line x1="{PL}" y1="{H-PB:.0f}" x2="{W-PR}" y2="{H-PB:.0f}" stroke="#1e293b" stroke-width="1"/>'
            f'<path d="{area}" fill="url(#mf)"/>'
            f'<path d="{line}" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
            f'{dots}{labels}{hits}</svg></div>')


def render_receipt(d):
    m = d["meta"]
    title = m.get("title") or f'{m["counterpart"]}, Receipt Close' + (f', {m["call_label"]}' if m.get("call_label") else "")
    m = {**m, "title": title}
    badges = "".join(f'<span class="badge">{E(b)}</span>' for b in m.get("badges", []))
    meta_line = "<br>".join(E(x) for x in m.get("meta_lines", []))
    L = []
    L.append('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    L.append(f'<meta name="robots" content="noindex, nofollow"><title>{E(m.get("doc_title", m["counterpart"] + " · Receipt Close"))}</title>')
    gate_pw = (m.get("gate") or {}).get("external") or (m.get("gate") or {}).get("view")
    studio_css = STUDIO_CSS if d.get("studio") else ""
    L.append(f'<style>{RECEIPT_CSS}{TIP_CSS}{studio_css}{GATE_CSS if gate_pw else ""}</style>{VERCEL}</head><body>')
    if gate_pw:
        L.append('<div id="pw-gate"><div class="pw-label">ARCS &#183; Private Receipt</div>'
                 '<input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>')
    L.append('<div class="recoil"><div class="wrap">')
    # cover
    L.append('<header class="cover">')
    if m.get("glyph"):
        L.append(f'<span class="glyph" aria-hidden="true">{m["glyph"]}</span>')
    L.append(f'<div class="badges">{badges}</div>')
    L.append(f'<h1>{E(m["title"])}</h1>')
    L.append(f'<p class="sub">{d["lede_cover"]}</p>')
    L.append(f'<div class="meta">{meta_line}</div></header>')

    # 1. ex-ante receipt
    ea = d["ex_ante"]
    L.append('<section class="sec"><div class="eyebrow"><b>&#9633;</b> The ex-ante receipt &nbsp;&middot;&nbsp; the bet, filed before the call</div>')
    L.append(f'<p class="lede">{ea["lede"]}</p>')
    L.append(f'<div class="betbox"><span class="betk">THE BET</span><p>{ea["bet"]}</p></div>')
    L.append('<div class="preds">')
    for p in ea["predictions"]:
        pct = int(p["pct"])
        L.append(f'<div class="pred"><div class="predgauge"><div class="predbar"><div class="predfill" style="width:{pct}%"></div></div>'
                 f'<span class="predpct">{pct}%</span></div>'
                 f'<div class="predbody"><p class="predclaim">{p["claim"]}</p><p class="predmeta">{p.get("meta","")}</p></div></div>')
    L.append('</div>')
    if ea.get("kairos_pre"):
        L.append(f'<div class="kairoslock pre"><span class="klk">KAIROS, CALLED IN ADVANCE</span><p>{ea["kairos_pre"]}</p></div>')
    L.append('</section>')

    # 2. waveform
    wf = d.get("waveform")
    if wf:
        L.append('<section class="sec"><div class="eyebrow"><b>&#9633;</b> The call, as a waveform &nbsp;&middot;&nbsp; ' + E(wf.get("label", "")) + '</div>')
        L.append(_waveform_svg(wf))
        L.append(f'<p class="mcap">{wf["caption"]}</p></section>')

    # 3. reverse listening
    rl = d.get("reverse_listening")
    if rl:
        L.append('<section class="sec"><div class="eyebrow"><b>&#9633;</b> Reverse listening &nbsp;&middot;&nbsp; read from the close, resolution spent on the signal</div>')
        L.append(f'<p class="lede">{rl["lede"]}</p><div class="rlwalk">')
        for b in rl["beats"]:
            dil = b.get("dilation", "real")
            cls = "beat" + (f" {dil}" if dil in ("compressed", "dilated") else " real")
            tag_c = BEAT_TAG.get(dil, "var(--gold)")
            bdr_c = BEAT_BORDER.get(dil, "var(--border)")
            diltag = b.get("dilation_tag", {"real": "REAL RESOLUTION", "dilated": "DILATED RESOLUTION", "compressed": "COMPRESSED RESOLUTION"}[dil])
            L.append(f'<div class="{cls}" style="--dc:{tag_c};--dcb:{bdr_c}"><div class="beath"><span class="beatt">{E(b["tag"])}</span>'
                     f'<span class="beatdil">{E(diltag)}</span></div>'
                     f'<div class="beatlabel">{E(b["label"])}</div>'
                     f'<p class="beatq">&ldquo;{b["quote"]}&rdquo;</p>'
                     f'<p class="beatread">{b["read"]}</p></div>')
        L.append('</div></section>')

    # 4. kairos write-lock
    kl = d.get("kairos_lock")
    if kl:
        L.append('<section class="sec"><div class="kairoslock"><span class="klk">&#9679; KAIROS, WRITE-LOCKED &nbsp;&middot;&nbsp; ' + E(kl["label"]) + '</span>')
        L.append(f'<blockquote>&ldquo;{kl["quote"]}&rdquo;</blockquote><p>{kl["prose"]}</p></div></section>')

    # 5. auto-close scorecard
    cl = d["close"]
    L.append('<section class="sec"><div class="eyebrow"><b>&#9633;</b> The receipt auto-closes &nbsp;&middot;&nbsp; ex-ante scored against reality</div>')
    L.append(f'<div class="closestatus"><span class="csk">STATUS</span><span class="csv">{E(cl.get("status", "CLOSED"))}</span><p>{cl["status_note"]}</p></div>')
    L.append('<div class="scard">')
    for r in cl["scorecard"]:
        v = r["verdict"].upper()
        vc = VERDICT_COLOR.get(v, "#94a3b8")
        L.append(f'<div class="scrow"><div class="scv" style="--vc:{vc}">{E(v)}</div>'
                 f'<div class="scb"><p class="scp"><span class="scl">Predicted</span>{r["predicted"]}</p>'
                 f'<p class="sco"><span class="scl">Observed</span>{r["observed"]}</p></div>'
                 f'<div class="scd">{E(r.get("delta",""))}</div></div>')
    L.append('</div>')
    if cl.get("net_new"):
        L.append('<div class="eyebrow2">Priors updated by net-new information</div><div class="nns-wrap">')
        for nn in cl["net_new"]:
            L.append(f'<div class="nn"><div class="nnk">NET-NEW SIGNAL</div><p class="nns">{E(nn["signal"])}</p>'
                     f'<p class="nnq">&ldquo;{nn["quote"]}&rdquo;</p><p class="nnu"><b>Prior update:</b> {nn["update"]}</p></div>')
        L.append('</div>')
    po = cl.get("posterior")
    if po:
        L.append('<div class="posterior"><span class="pok">THE POSTERIOR &nbsp;&middot;&nbsp; what the receipt taught me</span>')
        L.append(f'<p class="powedge"><b>Wedge:</b> {po["wedge"]}</p>')
        L.append(f'<p><b>Status:</b> {po["status"]}</p>')
        L.append(f'<p><b>Register:</b> {po["register"]}</p>')
        L.append(f'<p class="ponote">{po["note"]}</p></div>')
    # honesty gate: render any declared resolution gap as a visible flag (never hide low res)
    for g in d.get("resolution_gaps", []):
        L.append(f'<div class="gapflag"><div class="gk">additional enrichment source inputs required</div>'
                 f'<p>{E(g["what"])} &mdash; would sharpen with: {E(g["inputs"])}.</p></div>'.replace("&mdash;", "&#8212;"))
    L.append('</section>')

    if d.get("studio"):
        L.append(_studio_panel(d["studio"]))
    L.append(f'<footer class="foot">{d.get("foot", "ARCS &middot; FIELD OS &middot; RECEIPT CLOSE")}</footer>')
    L.append('</div></div><div id="tip"></div>')
    L.append(f'<script>{TIP_JS}</script>')
    if gate_pw:
        key = f'{m["report_id"]}-view-auth'
        L.append("<script>(function(){var K='" + key + "',P='" + gate_pw + "';"
                 "if(sessionStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}"
                 "var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;"
                 "if(i.value.toLowerCase()===P){sessionStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');}"
                 "else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();</script>")
    L.append("<script>window.addEventListener('load',function(){try{if(window.va)va('event',{name:'receipt_view'});}catch(e){}});</script>")
    L.append('</body></html>')
    return "".join(L)


# ===========================================================================
# PROFILE SURFACE  (blueprint sec 9: robin-profile = THE READ, step 1 of the loop)
# The read of the counterpart -- registers / altitude / resonance / quiet-signals
# / loop, enriched from the public crawl. Canonical tokens. Every section is
# optional: a counterpart with thinner signal renders fewer sections + the
# honesty flag (blueprint sec 11), never a fabricated one.
# ===========================================================================
PROFILE_CSS = TOKENS + """
*{box-sizing:border-box;margin:0;padding:0}h1,h2,h3{text-wrap:balance}p{text-wrap:pretty}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;padding:44px 22px 96px}
.page{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
.uplink{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);text-decoration:none;margin-bottom:2px}.uplink:hover{color:var(--cyan)}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed)}
h1{font-size:27px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.18;font-family:var(--display)}
.sub{font-size:14.5px;color:var(--muted);margin-top:10px;line-height:1.6}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3}
.cav{border:1px solid rgba(255,215,0,.28);border-radius:12px;background:var(--gold-bg);padding:15px 17px;font-size:13.5px;color:var(--text);line-height:1.55}.cav b{color:var(--gold)}
.note{font-size:14px;color:var(--muted);line-height:1.6;margin-top:16px}.note b{color:var(--gold)}
.mv{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:24px}
.mvk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dimmed);margin-bottom:10px}
.mv h2{font-size:20px;font-weight:700;letter-spacing:-.01em;margin-bottom:6px;font-family:var(--display)}
.lede{font-size:14px;color:var(--muted);line-height:1.6;margin-bottom:16px}
.headline{font-size:17px;color:#fff;font-weight:700;margin-bottom:14px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.reg{border:1px solid var(--border);border-top:2px solid var(--ac);border-radius:11px;background:var(--surface2);padding:16px 18px}
.regh{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:9px}
.regn{font-size:15px;font-weight:700;color:#fff}
.regalt{font-family:var(--mono);font-size:9px;letter-spacing:.14em;color:var(--ac)}
.regcues{font-size:12px;color:var(--dimmed);line-height:1.5;margin-bottom:10px}
.regq{font-size:13px;color:#d2d0c8;font-style:italic;line-height:1.5;border-top:1px solid var(--border);padding-top:9px}
.regsrc{display:block;font-style:normal;font-family:var(--mono);font-size:9px;letter-spacing:.06em;color:var(--dimmed);margin-top:6px}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.chip{font-family:var(--mono);font-size:10px;letter-spacing:.03em;color:#c0beb6;background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:4px 9px}
.ladder{display:grid;border:1px solid var(--border);border-radius:12px;overflow:hidden}
.rung{display:grid;grid-template-columns:170px 1fr;gap:14px;padding:14px 16px;border-top:1px solid var(--border);background:var(--surface2)}
.rung:first-child{border-top:0;background:linear-gradient(90deg,rgba(0,255,157,.08),transparent 60%)}
.rung:last-child{background:linear-gradient(90deg,rgba(255,77,109,.08),transparent 60%)}
.rlvl{font-family:var(--mono);font-size:11px;font-weight:700;color:#fff;padding-top:2px}
.rb p{font-size:13px;color:#c4c2ba;line-height:1.5}.rt{color:var(--dimmed) !important;font-size:12px !important;margin-top:5px}.rt b{color:var(--text)}
.rmap{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rcol{border:1px solid var(--border);border-radius:11px;padding:16px 18px;background:var(--surface2)}
.rcol.l{border-top:2px solid var(--green)}.rcol.x{border-top:2px solid var(--red)}
.rmk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;margin-bottom:11px}
.rcol.l .rmk{color:var(--green)}.rcol.x .rmk{color:var(--red)}
.rcol ul{list-style:none;display:grid;gap:8px}.rcol li{font-size:12.5px;color:#c0beb6;line-height:1.5;padding-left:14px;position:relative}
.rcol.l li::before{content:"+";position:absolute;left:0;color:var(--green);font-weight:700}
.rcol.x li::before{content:"\\2212";position:absolute;left:0;color:var(--red);font-weight:700}
.scards{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:6px}
.scard{border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:13px 15px}
.sh{font-size:13.5px;font-weight:700;color:#fff;margin-bottom:5px}.scard p{font-size:12px;color:var(--muted);line-height:1.5}
.csub{font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed);margin:16px 0 8px}
.stg{display:grid;grid-template-columns:34px 1fr;gap:14px;padding:12px 0;border-top:1px solid var(--border)}
.stg:first-of-type{border-top:0}
.stn{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--cyan);opacity:.5;line-height:1}
.sts{font-size:15px;font-weight:700;color:#fff;margin-bottom:3px}
.stb p{font-size:13px;color:var(--muted);line-height:1.5}.stb a{color:var(--cyan);text-decoration:none;font-family:var(--mono);font-size:11px}.stb a:hover{text-decoration:underline}
.close{font-size:15px;color:#e4ded4;line-height:1.6;border:1px solid rgba(255,215,0,.28);border-radius:11px;background:var(--gold-bg);padding:14px 16px}
.gapflag{border:1px dashed var(--gold);border-radius:12px;background:var(--gold-bg);padding:18px 20px}
.gapflag .gk{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:9px}
.gapflag p{font-size:13.5px;color:var(--text);opacity:.9;line-height:1.55;margin-bottom:8px}
.gapflag ul{list-style:none;display:flex;flex-wrap:wrap;gap:7px;margin-top:4px}
.gapflag li{font-family:var(--mono);font-size:10px;color:var(--gold);background:var(--gold-bg);border:1px solid rgba(255,215,0,.3);border-radius:6px;padding:4px 9px}
.foot{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--dimmed);text-align:center;padding-top:8px;line-height:2}
@media(max-width:560px){.two,.rmap,.scards{grid-template-columns:1fr}.rung{grid-template-columns:1fr;gap:4px}}
.qgrid{display:grid;gap:10px}
.qcard{border:1px solid var(--border);border-top:2px solid var(--qc);border-radius:11px;background:var(--surface2);padding:15px 17px}
.qtag{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--qc);margin-bottom:7px}
.qh{font-size:15px;font-weight:700;color:#fff;margin-bottom:7px}
.qcard p{font-size:12.5px;color:var(--muted);line-height:1.55;margin-bottom:7px}
.qcard .qso{color:#d2d0c8;border-top:1px solid var(--border);padding-top:8px;margin-bottom:0}
.qcard .qso b{color:var(--gold);font-family:var(--mono);font-size:9px;letter-spacing:.08em;text-transform:uppercase;margin-right:6px}
"""


def _resolution_flag(res):
    """Honesty gate (blueprint sec 11): render low resolution as a visible flag
    naming the specific enrichment inputs, never hide it."""
    lvl = (res or {}).get("level", "")
    if not lvl or lvl.lower().startswith(("full", "high")):
        return ""
    inputs = "".join(f"<li>{E(i)}</li>" for i in res.get("dial_up_inputs", []))
    caveat = res.get("caveat", "")
    return (f'<section class="gapflag"><div class="gk">additional enrichment source inputs required</div>'
            f'<p><b>Resolution: {E(lvl)}.</b> {caveat}</p>'
            + (f'<p>These sources would raise the resolution, with consent:</p><ul>{inputs}</ul>' if inputs else "")
            + '</section>')


def render_profile(d):
    m = d["meta"]
    hdr = d["header"]
    gate_pw = (m.get("gate") or {}).get("external") or (m.get("gate") or {}).get("view")
    L = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f'<meta name="robots" content="noindex, nofollow"><title>{E(m.get("doc_title", m["counterpart"] + " · the profile read"))}</title>',
         f'<style>{PROFILE_CSS}{GATE_CSS if gate_pw else ""}</style>{VERCEL}</head><body>']
    if gate_pw:
        L.append('<div id="pw-gate"><div class="pw-label">ARCS &#183; Private Read</div>'
                 '<input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>')
    L.append('<div class="page">')
    up = m.get("uplink")
    up_html = f'<a class="uplink" href="{E(up["href"])}">&#8593; {E(up["label"])}</a>' if up else ""
    L.append(f'<div>{up_html}<div class="eyebrow">{hdr["eyebrow"]}</div><h1>{hdr["title"]}</h1><div class="sub">{hdr["sub"]}</div></div>')
    L.append('<div class="rule"></div>')
    if d.get("caveat"):
        L.append(f'<div class="cav">{d["caveat"]}</div>')

    def _note(sec):
        return f'<p class="note">{sec["note"]}</p>' if sec.get("note") else ""

    v = d.get("voice")
    if v:
        regs = ""
        for r in v["registers"]:
            regs += (f'<div class="reg" style="--ac:{r["ac"]}"><div class="regh"><span class="regn">{r["name"]}</span>'
                     f'<span class="regalt">{E(r["alt"])}</span></div><p class="regcues">{r["cues"]}</p>'
                     f'<p class="regq">&ldquo;{r["quote"]}&rdquo;<span class="regsrc">{r.get("source","")}</span></p></div>')
        chips = "".join(f'<span class="chip">{c}</span>' for c in v.get("chips", []))
        L.append(f'<section class="mv"><div class="mvk">{v["k"]}</div><h2>{v["h2"]}</h2>'
                 f'<p class="headline">{v["headline"]}</p><div class="two">{regs}</div>'
                 + (f'<div class="chips">{chips}</div>' if chips else "") + _note(v) + '</section>')

    al = d.get("altitude")
    if al:
        rungs = "".join(f'<div class="rung"><div class="rlvl">{E(r["level"])}</div><div class="rb"><p>{r["body"]}</p>'
                        + (f'<p class="rt"><b>Trigger:</b> {r["trigger"]}</p>' if r.get("trigger") else "")
                        + '</div></div>' for r in al["rungs"])
        L.append(f'<section class="mv"><div class="mvk">{al["k"]}</div><h2>{al["h2"]}</h2>'
                 + (f'<p class="lede">{al["lede"]}</p>' if al.get("lede") else "")
                 + f'<div class="ladder">{rungs}</div>' + _note(al) + '</section>')

    rm = d.get("resonance")
    if rm:
        lands = "".join(f"<li>{x}</li>" for x in rm["lands"])
        loses = "".join(f"<li>{x}</li>" for x in rm["loses"])
        L.append(f'<section class="mv"><div class="mvk">{rm["k"]}</div><h2>{rm["h2"]}</h2><div class="rmap">'
                 f'<div class="rcol l"><div class="rmk">&#9650; LANDS</div><ul>{lands}</ul></div>'
                 f'<div class="rcol x"><div class="rmk">&#9660; LOSES YOU</div><ul>{loses}</ul></div></div></section>')

    ev = d.get("evidence")
    if ev:
        cards = "".join(f'<div class="scard"><div class="sh">{E(s["h"])}</div><p>{s["p"]}</p></div>' for s in ev.get("sources", []))
        groups = ""
        for g in ev.get("groups", []):
            gchips = "".join(f'<span class="chip">{c}</span>' for c in g["chips"])
            groups += f'<div class="csub">{E(g["label"])}</div><div class="chips" style="margin-top:0">{gchips}</div>'
        L.append(f'<section class="mv"><div class="mvk">{ev["k"]}</div><h2>{ev["h2"]}</h2>'
                 + (f'<p class="lede">{ev["lede"]}</p>' if ev.get("lede") else "")
                 + (f'<div class="scards">{cards}</div>' if cards else "") + groups + _note(ev) + '</section>')

    qs = d.get("quiet_signals")
    if qs:
        cards = ""
        for c in qs["cards"]:
            cards += (f'<div class="qcard" style="--qc:{c["qc"]}"><div class="qtag">{E(c["tag"])}</div>'
                      f'<div class="qh">{c["headline"]}</div><p>{c["body"]}</p>'
                      f'<p class="qso"><b>so</b>{c["so"]}</p></div>')
        L.append(f'<section class="mv"><div class="mvk">{qs["k"]}</div><h2>{qs["h2"]}</h2>'
                 + (f'<p class="lede">{qs["lede"]}</p>' if qs.get("lede") else "")
                 + f'<div class="qgrid">{cards}</div></section>')

    lp = d.get("loop")
    if lp:
        steps = ""
        for i, s in enumerate(lp["steps"], 1):
            link = f' &middot; <a href="{E(s["link"])}" target="_blank" rel="noopener">open &#8599;</a>' if s.get("link") else ""
            steps += (f'<div class="stg"><div class="stn">{i}</div><div class="stb"><div class="sts">{s["title"]}</div>'
                      f'<p>{s["body"]}{link}</p></div></div>')
        L.append(f'<section class="mv"><div class="mvk">{lp["k"]}</div><h2>{lp["h2"]}</h2>'
                 + (f'<p class="lede">{lp["lede"]}</p>' if lp.get("lede") else "")
                 + steps + (f'<p class="close" style="margin-top:16px">{lp["close"]}</p>' if lp.get("close") else "") + '</section>')

    # bottom resolution flag only if no top caveat carried it (avoid duplicate)
    if not d.get("caveat"):
        L.append(_resolution_flag(m.get("resolution")))
    if d.get("close"):
        L.append(f'<p class="close">{d["close"]}</p>')
    L.append(f'<div class="foot">{d.get("foot", "ARCS &middot; THE PROFILE READ &middot; STEP ONE OF THE LOOP")}</div>')
    L.append('</div>')
    if gate_pw:
        key = f'{m["report_id"]}-view-auth'
        L.append("<script>(function(){var K='" + key + "',P='" + gate_pw + "';"
                 "if(sessionStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}"
                 "var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;"
                 "if(i.value.toLowerCase()===P){sessionStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');}"
                 "else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();</script>")
    L.append("<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^=\"http\"]');if(a&&window.va){try{va('event',{name:'profile_click',data:{to:a.hostname}});}catch(_){}}});</script>")
    L.append('</body></html>')
    return "".join(L)


# ===========================================================================
# CODEX SURFACE  (blueprint sec 9: robin-codex = THE RECOIL, dual-tab)
# Two views of one thing: The Read (game-day tape -- the line, vibe/veer, the
# offer, on the counterpart's own calls) + The Instrument (how the read is made,
# run on Zach's OWN tape, not theirs). Canonical tokens. Extended #tip (5-field
# stated-vs-revealed payload). N-call adaptive: single-call renders one spark.
# ===========================================================================
# extended tooltip (stated vs revealed) -- the codex spark variant of #tip.
TIP_CSS_EXT = (".hit{cursor:pointer}"
    "#tip{position:fixed;z-index:80;max-width:min(300px,88vw);pointer-events:none;opacity:0;transition:opacity .12s;"
    "background:#0b0f16;border:1px solid var(--tc,#1e293b);border-radius:10px;padding:12px 14px;box-shadow:0 8px 30px rgba(0,0,0,.55)}"
    "#tip.on{opacity:1}"
    "#tip .tt{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--tc,#94a3b8);display:flex;justify-content:space-between;gap:10px;margin-bottom:8px}"
    "#tip .tq{font-size:13px;font-style:italic;color:var(--text);line-height:1.45;margin-bottom:10px}"
    "#tip .tr{display:grid;grid-template-columns:58px 1fr;gap:8px;font-size:11.5px;line-height:1.4;margin-top:5px}"
    "#tip .trk{font-family:var(--mono);font-size:8.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dimmed);padding-top:1px}"
    "#tip .trv{color:var(--muted)}"
    "#tip .gap{margin-top:9px;padding-top:8px;border-top:1px solid #1e293b;font-family:var(--mono);font-size:9px;letter-spacing:.06em;color:var(--tc,#94a3b8)}"
    "@media(hover:none){.hit{cursor:default}}")

TIP_JS_EXT = ("(function(){var tip=document.getElementById('tip');if(!tip)return;"
    "function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}"
    "function show(el,e){var c=el.getAttribute('data-c')||'#94a3b8';tip.style.setProperty('--tc',c);"
    "tip.innerHTML='<div class=\"tt\"><span>'+esc(el.getAttribute('data-t'))+'</span><span style=\"color:'+c+'\">'+esc(el.getAttribute('data-ph'))+'</span></div>'"
    "+'<div class=\"tq\">&ldquo;'+esc(el.getAttribute('data-q'))+'&rdquo;</div>'"
    "+'<div class=\"tr\"><span class=\"trk\">My move</span><span class=\"trv\">'+esc(el.getAttribute('data-s'))+'</span></div>'"
    "+'<div class=\"tr\"><span class=\"trk\">How it landed</span><span class=\"trv\">'+esc(el.getAttribute('data-r'))+'</span></div>'"
    "+'<div class=\"gap\">'+esc(el.getAttribute('data-g'))+'</div>';"
    "tip.classList.add('on');move(e);}"
    "function move(e){var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+16,y=e.clientY+16;if(x+w>window.innerWidth-8)x=e.clientX-w-16;if(y+h>window.innerHeight-8)y=e.clientY-h-16;tip.style.left=x+'px';tip.style.top=y+'px';}"
    "function hide(){tip.classList.remove('on');}"
    "document.querySelectorAll('[data-tip]').forEach(function(el){"
    "el.addEventListener('mouseenter',function(e){show(el,e);});el.addEventListener('mousemove',move);el.addEventListener('mouseleave',hide);"
    "el.addEventListener('click',function(e){e.stopPropagation();var r=el.getBoundingClientRect();show(el,{clientX:r.left+r.width/2,clientY:r.top+r.height/2});});});"
    "document.addEventListener('click',hide);})();")

# phase -> colors. Solid for the tag/label (--pc), alpha for the compliant full
# border (--pcb) -- the codex beat's old border-left:3px side-tab, made craft-floor clean.
PHASE_HEX = {"in_sync": "#FFD700", "human": "#00F0FF", "push": "#00FF9D", "out": "#FF4D6D"}
PHASE_TAG = {"in_sync": "var(--gold)", "human": "var(--cyan)", "push": "var(--green)", "out": "var(--red)"}
PHASE_BORDER = {"in_sync": "rgba(255,215,0,.30)", "human": "rgba(0,240,255,.30)", "push": "rgba(0,255,157,.30)", "out": "rgba(255,77,109,.30)"}

CODEX_CSS = TOKENS + """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);padding:40px 24px 96px;line-height:1.62}
.page{max-width:720px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed)}
h1{font-size:27px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.2;font-family:var(--display)}
.sub{font-size:14.5px;color:var(--muted);margin-top:10px;line-height:1.6}.sub strong{color:var(--text);font-weight:600}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3;margin:2px 0}
.uplink{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);text-decoration:none;margin-bottom:2px}.uplink:hover{color:var(--cyan)}
.tabs{display:flex;gap:6px;margin:4px 0 2px}
.tabs button{flex:1;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed);background:var(--surface2);border:1px solid var(--border);border-radius:9px;padding:12px 10px;cursor:pointer;transition:color .15s,border-color .15s,background .15s;line-height:1.3}
.tabs button .th{display:block;font-size:9px;letter-spacing:.14em;color:var(--dimmed);margin-bottom:3px}
.tabs button.active{color:var(--text);border-color:rgba(0,240,255,.4);background:rgba(0,240,255,.06)}
.tabs button.active .th{color:var(--cyan)}
.tabpane{display:none;flex-direction:column;gap:18px}.tabpane.on{display:flex}
.subnav{display:flex;flex-wrap:wrap;gap:5px;margin:2px 0 0}
.subnav a{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--dimmed);text-decoration:none;padding:6px 10px;border-radius:6px;border:1px solid transparent;cursor:pointer;transition:color .15s,border-color .15s,background .15s}
.subnav a:hover{color:var(--text);border-color:var(--border)}
.subnav a .nt{color:var(--dimmed)}.subnav a.read{border-color:rgba(255,215,0,.18)}.subnav a.hood{border-color:rgba(0,240,255,.16)}
.scroll-margin{scroll-margin-top:14px}
.readnote{font-size:13px;line-height:1.55;color:var(--muted);background:var(--gold-bg);border:1px solid rgba(255,215,0,.22);border-radius:10px;padding:12px 15px}
.readnote strong{color:var(--text);font-weight:600}
.shl{font-size:18px;font-weight:700;letter-spacing:-.01em;color:var(--text);margin:6px 2px 0;line-height:1.25}
.lede{font-size:14.5px;color:var(--muted);margin:6px 2px 0;line-height:1.52}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;margin-top:10px}
.card h3{font-size:12px;font-family:var(--mono);font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);margin-bottom:12px}
.card p{font-size:14.5px;color:var(--text);margin-bottom:10px}.card p:last-child{margin-bottom:0}.card strong{font-weight:600}
.said{margin-top:14px;padding:12px 15px;background:var(--cyan-bg);border:1px solid rgba(0,240,255,.2);border-radius:8px}
.said.you{background:rgba(148,163,184,.06);border-color:rgba(148,163,184,.25)}
.said .qk{font-family:var(--mono);font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--cyan);margin-bottom:5px}
.said.you .qk{color:var(--muted)}
.said .qv{font-size:14px;line-height:1.5;color:var(--text);font-style:italic}
ul.plain{list-style:none;display:flex;flex-direction:column;gap:11px;margin-top:4px}
ul.plain li{display:flex;gap:11px;align-items:flex-start;font-size:14px;line-height:1.55}
.dot{width:6px;height:6px;border-radius:50%;background:var(--cyan);flex-shrink:0;margin-top:7px}
.spark-wrap{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:16px 16px 10px;margin-top:12px}
.spark-h{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:2px}
.spark-h .sn{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.08em;color:var(--text)}
.spark-h .sv{font-family:var(--mono);font-size:9.5px;color:var(--gold)}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin:10px 2px 0}
.lgi{display:flex;align-items:center;gap:6px;font-family:var(--mono);font-size:9.5px;letter-spacing:.05em;color:var(--dimmed)}
.lgd{width:8px;height:8px;border-radius:50%;flex:none}
.beat{border:1px solid var(--pcb,var(--border));background:var(--surface);border-radius:9px;padding:13px 15px;margin-top:9px}
.bph{font-family:var(--mono);font-size:8.5px;letter-spacing:.14em;font-weight:700;color:var(--pc);margin-bottom:8px}
.bqp{display:grid;grid-template-columns:48px 1fr;gap:10px;align-items:baseline;margin-bottom:5px}
.bql{font-family:var(--mono);font-size:8px;letter-spacing:.08em;color:var(--dimmed)}
.bqp p{font-size:13.5px;color:var(--text);line-height:1.48;font-style:italic}
.bread{margin-top:8px;padding-top:8px;border-top:1px solid var(--border);font-size:13px;color:var(--muted);line-height:1.55}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}
@media(max-width:560px){.two{grid-template-columns:1fr}.bqp{grid-template-columns:1fr;gap:2px}}
.mini{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:14px 16px}
.mini h4{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}
.mini p{font-size:13px;line-height:1.55;color:var(--text)}
.fence{border-color:rgba(255,215,0,.3);background:var(--gold-bg)}.fence h3{color:var(--gold)}
.offer{border-color:rgba(0,255,157,.3);background:var(--green-bg)}.offer h3{color:var(--green)}
.ladder{display:flex;flex-direction:column;gap:8px;margin-top:6px}
.lrung{display:grid;grid-template-columns:120px 1fr;gap:12px;align-items:baseline;background:var(--surface2);border:1px solid var(--border);border-radius:9px;padding:11px 14px}
.lrk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;color:var(--green)}
.lrung p{font-size:13px;color:var(--text);line-height:1.5}
@media(max-width:560px){.lrung{grid-template-columns:1fr;gap:3px}}
.foot{font-size:13px;color:var(--muted);text-align:center;padding-top:10px;line-height:1.6}
.stamp{text-align:center;margin-top:6px;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dimmed)}
h1,h2,h3{text-wrap:balance}p{text-wrap:pretty}
.sub,.said .qv,.bqp p,.bread,.card p,.mini p,.beat p,.readnote,.lrung p,.bqp .bql{overflow-wrap:anywhere}
@media(max-width:820px){.page{max-width:100%}}
@media(max-width:680px){.two{grid-template-columns:1fr}}
@media(max-width:560px){body{padding:32px 16px 80px}.tabs{flex-direction:column}.tabs button{padding:12px 14px}.subnav{gap:4px}.said{padding:11px 13px}}
"""


def _spark_svg(sp):
    """Compute a call-arc spark from points[{phase, v(0..100), r?, tip:{t,ph,q,s,r,g}}].
    Deterministic geometry; each point carries the extended stated-vs-revealed #tip payload."""
    pts = sp["points"]
    n = len(pts)
    W, H, base, top = 640, 96, 76, 16
    xs = [14 + (W - 28) * (i / (n - 1)) for i in range(n)]
    ys = [base - (float(p.get("v", 50)) / 100.0) * (base - top) for p in pts]
    path = "M" + " L".join(f"{xs[i]:.0f},{ys[i]:.0f}" for i in range(n))
    dots, hits = "", ""
    for i, p in enumerate(pts):
        c = PHASE_HEX.get(p.get("phase", "human"), "#94a3b8")
        r = p.get("r", 5.5)
        dots += f'<circle cx="{xs[i]:.0f}" cy="{ys[i]:.0f}" r="{r}" fill="{c}" stroke="#020408" stroke-width="1.5"/>'
        t = p.get("tip", {})
        hits += (f'<circle class="hit" cx="{xs[i]:.0f}" cy="{ys[i]:.0f}" r="16" fill="transparent" data-tip data-c="{c}" '
                 f'data-t="{A(t.get("t",""))}" data-ph="{A(t.get("ph",""))}" data-q="{A(t.get("q",""))}" '
                 f'data-s="{A(t.get("s",""))}" data-r="{A(t.get("r",""))}" data-g="{A(t.get("g",""))}"/>')
    return (f'<div class="spark-wrap"><div class="spark-h"><span class="sn">{sp["name"]}</span>'
            f'<span class="sv">{sp.get("note","")}</span></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{A(sp.get("name",""))} arc">'
            f'<line x1="14" y1="{base}" x2="{W-14}" y2="{base}" stroke="#1e293b" stroke-width="1"/>'
            f'<path d="{path}" fill="none" stroke="#33415580" stroke-width="1.5" stroke-linejoin="round"/>'
            f'{dots}{hits}</svg></div>')


def _codex_read_block(b):
    t = b["type"]
    idattr = f' id="{b["id"]}"' if b.get("id") else ""
    scm = " scroll-margin" if b.get("id") else ""
    if t == "readnote":
        return f'<div class="readnote{scm}"{idattr}>{b["html"]}</div>'
    if t == "line":
        s = b["said"]
        cls = "said you" if s.get("speaker") == "you" else "said"
        pb = f'<p>{b["p_before"]}</p>' if b.get("p_before") else ""
        pa = f'<p style="margin-top:12px;">{b["p_after"]}</p>' if b.get("p_after") else ""
        h3c = f' style="color:{b["h3color"]};"' if b.get("h3color") else ""
        return (f'<div class="card{scm}"{idattr}><h3{h3c}>{b["h3"]}</h3>{pb}'
                f'<div class="{cls}"><div class="qk">{s["qk"]}</div><div class="qv">"{s["qv"]}"</div></div>{pa}</div>')
    if t == "legend":
        items = "".join(f'<span class="lgi"><span class="lgd" style="background:{i["color"]};"></span>{i["label"]}</span>' for i in b["items"])
        return f'<div class="legend{scm}"{idattr}>{items}</div>'
    if t == "spark":
        return _spark_svg(b)
    if t == "beat":
        ph = b.get("phase", "human")
        pc, pcb = PHASE_TAG.get(ph, "var(--cyan)"), PHASE_BORDER.get(ph, "var(--border)")
        pairs = "".join(f'<div class="bqp"><span class="bql">{p["who"]}</span><p>{p["text"]}</p></div>' for p in b["pairs"])
        bread = f'<p class="bread">{b["bread"]}</p>' if b.get("bread") else ""
        return f'<div class="beat" style="--pc:{pc};--pcb:{pcb}"><div class="bph">{b["bph"]}</div>{pairs}{bread}</div>'
    if t == "offer":
        s = b.get("said")
        said = ""
        if s:
            cls = "said you" if s.get("speaker") == "you" else "said"
            said = f'<div class="{cls}"><div class="qk">{s["qk"]}</div><div class="qv">"{s["qv"]}"</div></div>'
        pb = f'<p>{b["p_before"]}</p>' if b.get("p_before") else ""
        pa = f'<p style="margin-top:12px;">{b["p_mid"]}</p>' if b.get("p_mid") else ""
        ladder = "".join(f'<div class="lrung"><span class="lrk">{r["k"]}</span><p>{r["p"]}</p></div>' for r in b.get("ladder", []))
        pc = f'<p style="margin-top:14px;">{b["p_close"]}</p>' if b.get("p_close") else ""
        return (f'<div class="card offer{scm}"{idattr}><h3>{b["h3"]}</h3>{pb}{said}{pa}'
                f'<div class="ladder">{ladder}</div>{pc}</div>')
    return ""


def _codex_hood_block(b):
    t = b["type"]
    idattr = f' id="{b["id"]}"' if b.get("id") else ""
    scm = " scroll-margin" if b.get("id") else ""
    fence = " fence" if b.get("fence") else ""
    h3c = f' style="color:{b["h3color"]};"' if b.get("h3color") else ""
    if t == "card":
        ps = "".join(f'<p>{p}</p>' for p in b["ps"])
        return f'<div class="card{fence}{scm}"{idattr}><h3{h3c}>{b["h3"]}</h3>{ps}</div>'
    if t == "states":
        minis = "".join(f'<div class="mini"><h4 style="color:{mm["color"]};">{mm["h4"]}</h4><p>{mm["p"]}</p></div>' for mm in b["minis"])
        pa = f'<p style="margin-top:14px;">{b["p_after"]}</p>' if b.get("p_after") else ""
        return f'<div class="card"><h3{h3c}>{b["h3"]}</h3><div class="two">{minis}</div>{pa}</div>'
    if t == "checks":
        items = "".join(f'<li><span class="dot"></span><div><strong>{i["strong"]}</strong> {i["rest"]}</div></li>' for i in b["items"])
        intro = f'<p>{b["p_intro"]}</p>' if b.get("p_intro") else ""
        return f'<div class="card{scm}"{idattr}><h3{h3c}>{b["h3"]}</h3>{intro}<ul class="plain">{items}</ul></div>'
    return ""


def render_codex(d):
    m = d["meta"]
    hdr = d["header"]
    gate_pw = (m.get("gate") or {}).get("external") or (m.get("gate") or {}).get("view")
    subs = "".join(f'<p class="sub">{s}</p>' for s in hdr.get("subs", []))
    L = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         f'<meta name="robots" content="noindex, nofollow"><title>{E(m.get("doc_title", m["counterpart"] + " · the codex"))}</title>',
         f'<style>{CODEX_CSS}{TIP_CSS_EXT}{GATE_CSS if gate_pw else ""}</style>{VERCEL}</head><body>']
    if gate_pw:
        L.append('<div id="pw-gate"><div class="pw-label">ARCS &#183; Private Codex</div>'
                 '<input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>')
    L.append('<div class="page"><div>')
    up = m.get("uplink")
    if up:
        L.append(f'<a class="uplink" href="{E(up["href"])}">&#8593; {E(up["label"])}</a>')
    L.append(f'<div class="eyebrow">{hdr["eyebrow"]}</div><h1>{hdr["title"]}</h1>{subs}</div><div class="rule"></div>')
    tb = d["tabs"]
    L.append(f'<div class="tabs"><button id="tab-read" class="active" onclick="showTab(\'read\')">'
             f'<span class="th">{tb["read_th"]}</span>{tb["read_label"]}</button>'
             f'<button id="tab-hood" onclick="showTab(\'hood\')">'
             f'<span class="th">{tb["hood_th"]}</span>{tb["hood_label"]}</button></div>')
    if d.get("subnav"):
        links = "".join(f'<a class="{l["side"]}" data-tab="{"read" if l["side"]=="read" else "hood"}" data-to="{A(l["to"])}">'
                        f'<span class="nt">{l["nt"]}</span> {l["label"]}</a>' for l in d["subnav"])
        L.append(f'<nav class="subnav">{links}</nav>')
    L.append('<div id="pane-read" class="tabpane on">')
    for b in d["read"]:
        L.append(_codex_read_block(b))
    L.append('</div><div id="pane-hood" class="tabpane">')
    for b in d["hood"]:
        L.append(_codex_hood_block(b))
    L.append('</div>')
    L.append(f'<div class="foot">{d.get("foot","")}</div>')
    if d.get("stamp"):
        L.append(f'<div class="stamp">{d["stamp"]}</div>')
    L.append('</div><div id="tip"></div><script>')
    L.append("function showTab(t){document.getElementById('pane-read').classList.toggle('on',t==='read');"
             "document.getElementById('pane-hood').classList.toggle('on',t==='hood');"
             "document.getElementById('tab-read').classList.toggle('active',t==='read');"
             "document.getElementById('tab-hood').classList.toggle('active',t==='hood');"
             "try{history.replaceState(null,'',t==='read'?'#read':'#instrument');}catch(e){}"
             "try{if(window.va)va('event',{name:'codex_tab',data:{tab:t}});}catch(e){}"
             "window.scrollTo({top:0,behavior:'smooth'});}"
             "(function(){var h=(location.hash||'').toLowerCase();showTab(h==='#instrument'?'hood':'read');})();")
    if gate_pw:
        key = f'{m["report_id"]}-view-auth'
        L.append("(function(){var K='" + key + "',P='" + gate_pw + "';"
                 "if(localStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}"
                 "var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;"
                 "if(i.value.toLowerCase()===P){localStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');}"
                 "else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();")
    L.append(TIP_JS_EXT)
    L.append("(function(){document.querySelectorAll('.subnav a').forEach(function(a){a.addEventListener('click',function(){"
             "if(typeof showTab==='function')showTab(a.getAttribute('data-tab'));"
             "var t=document.getElementById(a.getAttribute('data-to'));if(t)setTimeout(function(){t.scrollIntoView({behavior:'smooth',block:'start'});},60);});});})();")
    L.append('</script></body></html>')
    return "".join(L)


# ===========================================================================
# ONE-DOOR SURFACE  (blueprint sec 9: robin.html = THE ONE-DOOR, the entry)
# facesnav (N reads that feed each other) + one-line seed + the concrete
# real-call STORY + how-it-works + where-it-goes + how-to-start + for-the-room.
# Crispness rule: LEAD WITH THE STORY, not a diagram. Single-call counterparts
# lead with the belief-flip narrative (no multi-call loop diagram). Canonical
# tokens; base #tip; side-tabs converted to compliant full borders.
# ===========================================================================
ONEDOOR_CSS = TOKENS + """
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;padding:48px 22px 96px}
.page{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
h1,h2,h3{text-wrap:balance}p{text-wrap:pretty}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed)}
h1{font-size:28px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.18;font-family:var(--display)}
.sub{font-size:15px;color:var(--muted);margin-top:10px}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3}
.mv{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:26px 26px 28px;position:relative}
.mv.seed{border-color:rgba(255,215,0,.25)}.mv.well{border-color:rgba(0,240,255,.28)}.mv.corpus{border-color:rgba(0,255,157,.22)}
.mv.horizon{border-color:rgba(255,215,0,.22)}.mv.start{border-color:rgba(0,255,157,.3)}.mv.trust{border-color:rgba(148,163,184,.25)}
.mvk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dimmed);margin-bottom:10px}
.mv.seed .mvk{color:var(--gold)}.mv.well .mvk{color:var(--cyan)}.mv.corpus .mvk{color:var(--green)}
.mv.horizon .mvk{color:var(--gold)}.mv.start .mvk{color:var(--green)}.mv.trust .mvk{color:var(--muted)}
.mv h2{font-size:21px;font-weight:700;letter-spacing:-.01em;margin-bottom:12px}
.mvintro{font-size:14.5px;color:var(--muted);line-height:1.6;margin-bottom:18px}
.lbq{border:1px solid rgba(255,215,0,.30);border-radius:11px;background:var(--gold-bg);padding:16px 18px;margin:4px 0 16px}
.lbq blockquote{font-size:19px;font-weight:600;line-height:1.4;color:#fff}
.lbq .attr{font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dimmed);margin-top:10px;line-height:1.6}
.cta{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(255,215,0,.4);border-radius:8px;padding:11px 18px;text-decoration:none;transition:background .15s}
.cta:hover{background:var(--gold-bg)}
.manifold{border:1px solid var(--border);border-radius:12px;background:var(--surface2);padding:14px 14px 8px;margin-bottom:14px}
.mcap{font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:20px}
.flip{display:grid;gap:10px}
.flipcard{border:1px solid var(--fcb,var(--border));border-radius:11px;background:var(--surface2);padding:15px 17px}
.flipk{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--fc,var(--dimmed));margin-bottom:8px}
.flipb{font-size:13px;color:var(--muted);line-height:1.5;margin-bottom:8px}.flipb b{color:var(--text)}
.flipq{font-size:13.5px;font-style:italic;color:var(--text);line-height:1.5;border-top:1px solid var(--border);padding-top:9px;margin-bottom:8px}
.flipa{font-size:13px;color:var(--text);line-height:1.55}.flipa b{color:var(--green)}
.cc{border-top:1px solid var(--border);padding:16px 0}.cc:first-of-type{border-top:0;padding-top:2px}
.cc h3{font-size:16px;margin-bottom:6px}.cc p{font-size:14px;color:var(--muted);line-height:1.6}
.cclink{display:inline-block;margin-top:9px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);text-decoration:none}
.cclink:hover{text-decoration:underline}
.seeds{display:grid;gap:11px}
.seedc{border:1px solid rgba(255,215,0,.24);border-radius:10px;background:var(--surface2);padding:15px 17px}
.seedc h3{font-size:15px;margin-bottom:6px;color:#fff}.seedc p{font-size:13px;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
.needs{display:grid;gap:10px;margin-bottom:14px}
.need{display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:baseline;border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:14px 16px}
.need h3{font-size:14px;color:#fff;white-space:nowrap}.need p{font-size:13px;color:var(--muted);line-height:1.5}
.needclose{font-size:14px;color:var(--text);line-height:1.6}
.prows{display:grid;gap:9px}
.prow{display:grid;grid-template-columns:130px 1fr;gap:14px;border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:14px 16px}
.pwho{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan);padding-top:2px}
.pobj{font-size:13.5px;font-style:italic;color:var(--text);margin-bottom:6px}.pans{font-size:13px;color:var(--muted);line-height:1.55}
.facesnav{border:1px solid rgba(0,240,255,.22);border-radius:12px;background:var(--surface2);padding:14px 16px;display:grid;gap:2px}
.facesl{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);margin-bottom:6px}
.face{display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:baseline;padding:9px 8px;border-radius:8px;text-decoration:none;color:var(--text);cursor:pointer;transition:background .15s}
.face::after{content:"\\2197";font-family:var(--mono);font-size:13px;font-weight:700;color:var(--dimmed);align-self:center;transition:color .15s,transform .15s}
.face:hover::after{color:var(--cyan);transform:translate(2px,-2px)}
a.face:hover{background:var(--surface)}.face.here{opacity:.65}
.facen.led{display:inline-block;width:8px;height:8px;border-radius:50%;align-self:start;margin-top:5px;background:rgb(var(--rgb));animation:ledpulse 1.8s ease-in-out infinite}
.led.g{--rgb:0,255,157}.led.o{--rgb:255,159,28}.led.r{--rgb:255,77,109}.led.c{--rgb:0,240,255}
@keyframes ledpulse{0%,100%{opacity:.5}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.facen.led{animation:none;opacity:1}.face::after{transition:none}}
.faceb{display:flex;flex-direction:column;gap:2px}
.facet{font-size:14.5px;font-weight:700;color:#fff}.facet b{color:var(--gold);font-family:var(--mono);font-size:10px;letter-spacing:.06em;font-weight:700}
.faced{font-size:12px;color:var(--muted)}
.foot{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--dimmed);text-align:center;padding-top:8px;line-height:2}
@media(max-width:560px){.need{grid-template-columns:1fr;gap:4px}.prow{grid-template-columns:1fr;gap:5px}}
"""

# belief-flip card accent by verdict/direction
FLIP_ACC = {"up": ("var(--green)", "rgba(0,255,157,.30)"), "flip": ("var(--gold)", "rgba(255,215,0,.30)"),
            "down": ("var(--red)", "rgba(255,77,109,.30)"), "hold": ("var(--cyan)", "rgba(0,240,255,.28)")}


def _onedoor_block(b):
    t = b["type"]
    if t == "facesnav":
        faces = ""
        for f in b["faces"]:
            tag = f' &middot; <b>{f["tag"]}</b>' if f.get("tag") else ""
            here = " here" if f.get("here") else ""
            faces += (f'<a class="face{here}" href="{A(f["href"])}" target="_blank" rel="noopener">'
                      f'<span class="facen led {f.get("led","c")}" aria-hidden="true"></span>'
                      f'<span class="faceb"><span class="facet">{f["title"]}{tag}</span>'
                      f'<span class="faced">{f["desc"]}</span></span></a>')
        return f'<div class="facesnav"><div class="facesl">{b.get("label","")}</div>{faces}</div>'
    if t == "seed":
        cta = f'<a class="cta" href="{A(b["cta"]["href"])}" target="_blank" rel="noopener">{b["cta"]["label"]}</a>' if b.get("cta") else ""
        return (f'<section class="mv seed"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>'
                f'<div class="lbq"><blockquote>&ldquo;{b["quote"]}&rdquo;</blockquote><div class="attr">{b["attr"]}</div></div>{cta}</section>')
    if t == "story":
        cards = ""
        for c in b["beats"]:
            fc, fcb = FLIP_ACC.get(c.get("dir", "flip"), FLIP_ACC["flip"])
            q = f'<p class="flipq">&ldquo;{c["quote"]}&rdquo;</p>' if c.get("quote") else ""
            before = f'<p class="flipb"><b>Before:</b> {c["before"]}</p>' if c.get("before") else ""
            after = f'<p class="flipa"><b>After:</b> {c["after"]}</p>' if c.get("after") else ""
            cards += (f'<div class="flipcard" style="--fc:{fc};--fcb:{fcb}"><div class="flipk">{E(c["k"])}</div>'
                      f'{before}{q}{after}</div>')
        return (f'<section class="mv well"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>'
                f'<p class="mvintro">{b["intro"]}</p><div class="flip">{cards}</div>'
                + (f'<p class="mcap" style="margin-top:16px">{b["caption"]}</p>' if b.get("caption") else "") + '</section>')
    if t == "howitworks":
        cards = ""
        for c in b["cards"]:
            link = f'<a class="cclink" href="{A(c["link"]["href"])}" target="_blank" rel="noopener">{c["link"]["label"]} &rarr;</a>' if c.get("link") else ""
            cards += f'<div class="cc"><h3>{c["h3"]}</h3><p>{c["p"]}</p>{link}</div>'
        return f'<section class="mv corpus"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>{cards}</section>'
    if t == "horizon":
        seeds = "".join(f'<div class="seedc"><h3>{s["h3"]}</h3><p>{s["p"]}</p></div>' for s in b["seeds"])
        return (f'<section class="mv horizon"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>'
                + (f'<p class="mvintro">{b["intro"]}</p>' if b.get("intro") else "")
                + f'<div class="seeds">{seeds}</div></section>')
    if t == "start":
        needs = "".join(f'<div class="need"><h3>{n["h3"]}</h3><p>{n["p"]}</p></div>' for n in b["needs"])
        close = f'<p class="needclose">{b["close"]}</p>' if b.get("close") else ""
        return (f'<section class="mv start"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>'
                + (f'<p class="mvintro">{b["intro"]}</p>' if b.get("intro") else "")
                + f'<div class="needs">{needs}</div>{close}</section>')
    if t == "trust":
        prows = "".join(f'<div class="prow"><div class="pwho">{E(p["who"])}</div><div class="pbody">'
                        f'<p class="pobj">&ldquo;{p["obj"]}&rdquo;</p><p class="pans">{p["ans"]}</p></div></div>' for p in b["prows"])
        return (f'<section class="mv trust"><div class="mvk">{b["k"]}</div><h2>{b["h2"]}</h2>'
                + (f'<p class="mvintro">{b["intro"]}</p>' if b.get("intro") else "")
                + f'<div class="prows">{prows}</div></section>')
    return ""


def render_onedoor(d):
    m = d["meta"]
    hdr = d["header"]
    gate_pw = (m.get("gate") or {}).get("external") or (m.get("gate") or {}).get("view")
    L = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f'<meta name="robots" content="noindex, nofollow"><title>{E(m.get("doc_title", m["counterpart"] + " · one door"))}</title>',
         f'<style>{ONEDOOR_CSS}{TIP_CSS}{GATE_CSS if gate_pw else ""}</style>{VERCEL}</head><body>']
    if gate_pw:
        L.append('<div id="pw-gate"><div class="pw-label">ARCS &#183; Private &#183; for ' + E(m["counterpart"].split()[0]) + '</div>'
                 '<input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>')
    L.append('<div class="page">')
    L.append(f'<div><div class="eyebrow">{hdr["eyebrow"]}</div><h1>{hdr["title"]}</h1><p class="sub">{hdr["sub"]}</p></div><div class="rule"></div>')
    for b in d["blocks"]:
        L.append(_onedoor_block(b))
    L.append(f'<div class="foot">{d.get("foot","ARCS &middot; ONE DOOR")}</div>')
    L.append('</div><div id="tip"></div>')
    L.append(f'<script>{TIP_JS}</script>')
    if gate_pw:
        key = f'{m["report_id"]}-view-auth'
        L.append("<script>(function(){var K='" + key + "',P='" + gate_pw + "';"
                 "if(localStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}"
                 "var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;"
                 "if(i.value.toLowerCase()===P){localStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');}"
                 "else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();</script>")
    L.append('</body></html>')
    return "".join(L)


SURFACES = {"receipt": render_receipt, "profile": render_profile, "codex": render_codex, "onedoor": render_onedoor}


# ===========================================================================
# VERIFY GATE (blueprint sec 4) + HONESTY GATE (blueprint sec 11)
# Mechanical quality floor for the assembly line. Runs on the rendered HTML
# string and on the source SSOT. Returns (ok, findings[]).
# ===========================================================================
# Impeccable-detector heuristics: patterns that read as machine-authored or
# violate the ARCS voice/brand rules.
BANNED_SUBSTRINGS = [
    "—",   # em-dash (writing-avoid-emdashes-plain-language) -- use "--" or ", "
    "delve", "in today's fast-paced", "it's worth noting that",
    "leverage synerg", "unlock the power", "game-chang", "seamless integration",
]
# border-left thicker than 1px on a quote is a detector flag (sec 2) -- but our
# .beat/.betbox use 3px intentionally as structural rails, so we only flag
# border-left on an inline style of a quote-callout class.


def verify_html(htmltext, ssot=None):
    findings = []
    # 1. em-dash / banned substrings (skip inside the <script> tip payload which
    #    is code, not prose; em-dash there would still be a bug, so keep it strict)
    for bad in BANNED_SUBSTRINGS:
        if bad in htmltext:
            idx = htmltext.find(bad)
            ctx = htmltext[max(0, idx - 40):idx + 40].replace("\n", " ")
            findings.append(("FAIL", "impeccable", f"banned pattern {bad!r} near: ...{ctx}..."))
    # 2. must carry noindex + canonical bg, must NOT carry omakase tokens
    if "noindex" not in htmltext:
        findings.append(("FAIL", "brand", "missing <meta robots noindex>"))
    for omk in ["#0B0B0C", "#C9A227", "#5C8A4E", "#E34F1C", "Helvetica Neue"]:
        if omk in htmltext:
            findings.append(("FAIL", "token-drift", f"omakase token {omk} present -- counterpart family must be canonical (blueprint sec 10)"))
    if "#020408" not in htmltext:
        findings.append(("WARN", "token-drift", "canonical --bg #020408 not found; verify :root"))
    # 3. impeccable craft-floor: no colored border-left/right > 1px on a card/callout
    #    (detect.mjs 'side-tab' -- "the most recognizable tell of AI-generated UIs").
    for mm in re.finditer(r'border-(?:left|right)(?:-width)?\s*:\s*([2-9]|\d\d)px', htmltext):
        seg = mm.group(0)
        # a neutral hairline rule on a table/divider is fine; flag only colored side rails
        ctx = htmltext[max(0, mm.start() - 60):mm.start() + 40]
        if "var(--dc" in ctx or "solid var(--" in seg or re.search(r'#[0-9A-Fa-f]{3,6}', seg):
            findings.append(("FAIL", "craft-floor", f"side-tab: colored {seg} on a callout -- AI tell (impeccable craft-floor)"))
    return findings


def honesty_and_attribution(ssot):
    """Honesty gate (sec 11) + attribution discipline (sec 0/D1).
    - insufficient signal must be declared as resolution_gaps, never silently filled.
    - Me = Zach, Them = counterpart. Flag any quote attributed to the counterpart
      that is actually Zach's framing (best-effort: a heuristic sweep is impossible
      here, so we require every close scorecard row to carry an 'observed' string
      that is grounded, and every net_new to carry a verbatim 'quote')."""
    findings = []
    m = ssot.get("meta", {})
    cp = m.get("counterpart", "")
    # receipt-shaped checks only apply when close is the receipt close-block.
    close = ssot.get("close")
    if isinstance(close, dict):
        # every net-new signal must carry a verbatim quote (grounding, not fabrication)
        for nn in close.get("net_new", []):
            if not nn.get("quote", "").strip():
                findings.append(("FAIL", "honesty", f"net-new signal {nn.get('signal','?')!r} has no verbatim quote -- ungrounded assertion"))
        # scorecard rows need both predicted and observed
        for r in close.get("scorecard", []):
            if not r.get("observed", "").strip():
                findings.append(("FAIL", "honesty", f"scorecard row {r.get('predicted','?')[:40]!r} has no observed outcome"))
    # honesty gate: if the SSOT flags low resolution it must name the enrichment
    # inputs -- either a top-level resolution_gaps (receipt) or
    # meta.resolution.dial_up_inputs (profile). A bare low-res claim with no
    # inputs named is a hidden gap, which fails (blueprint sec 11).
    lvl = (m.get("resolution", {}).get("level") or "").lower()
    is_low = bool(lvl) and not lvl.startswith(("full", "high"))
    has_inputs = bool(ssot.get("resolution_gaps")) or bool(m.get("resolution", {}).get("dial_up_inputs"))
    if is_low and not has_inputs:
        findings.append(("FAIL", "honesty",
            f"meta.resolution is '{lvl}' but no enrichment inputs named -- must emit "
            "'additional enrichment source inputs required' with the specific inputs (blueprint sec 11)"))
    # attribution: counterpart name must be present (a receipt with no subject is a smell)
    if not cp:
        findings.append(("WARN", "attribution", "meta.counterpart empty -- cannot enforce Me=Zach/Them=counterpart"))
    return findings


def run_gates(htmltext, ssot):
    findings = verify_html(htmltext, ssot) + honesty_and_attribution(ssot)
    fails = [f for f in findings if f[0] == "FAIL"]
    return findings, len(fails) == 0


def _print_findings(findings):
    if not findings:
        print("  gate: clean (no findings)")
        return
    for level, cat, msg in findings:
        mark = "✗" if level == "FAIL" else "!"
        print(f"  [{mark} {level} {cat}] {msg}")


def main():
    ap = argparse.ArgumentParser(description="Parameterized counterpart-forge generator (canonical tokens).")
    ap.add_argument("--surface", choices=sorted(SURFACES), help="which surface to render")
    ap.add_argument("--data", help="path to the surface SSOT json")
    ap.add_argument("--out", help="output html path (default: stdout)")
    ap.add_argument("--verify-only", action="store_true", help="run the verify+honesty gates on --file, no render")
    ap.add_argument("--file", help="existing html file to verify (with --verify-only)")
    ap.add_argument("--no-gate", action="store_true", help="skip the gates (not recommended)")
    a = ap.parse_args()

    if a.verify_only:
        if not a.file:
            ap.error("--verify-only requires --file")
        htmltext = open(a.file).read()
        findings = verify_html(htmltext)
        print(f"VERIFY {a.file}")
        _print_findings(findings)
        sys.exit(0 if not [f for f in findings if f[0] == "FAIL"] else 1)

    if not (a.surface and a.data):
        ap.error("--surface and --data are required to render")
    ssot = json.load(open(a.data))
    htmltext = SURFACES[a.surface](ssot)

    if not a.no_gate:
        findings, ok = run_gates(htmltext, ssot)
        print(f"GATE {a.surface} <- {a.data}", file=sys.stderr)
        for level, cat, msg in findings:
            mark = "✗" if level == "FAIL" else "!"
            print(f"  [{mark} {level} {cat}] {msg}", file=sys.stderr)
        if not ok:
            print("GATE FAILED -- not writing output. Fix findings or pass --no-gate to override.", file=sys.stderr)
            sys.exit(1)
        if not findings:
            print("  gate: clean", file=sys.stderr)

    if a.out:
        with open(a.out, "w") as f:
            f.write(htmltext)
        print(f"wrote {a.out} ({len(htmltext)} bytes)", file=sys.stderr)
    else:
        print(htmltext)


if __name__ == "__main__":
    main()
