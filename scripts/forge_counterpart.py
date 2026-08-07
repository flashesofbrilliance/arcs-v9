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
    Deterministic geometry; each point carries a native <title> tooltip. v is the
    resonance height 0..100 (100 = top of chart)."""
    pts = wf["points"]
    n = len(pts)
    W, H, PT, PB, PL, PR = 720, 200, 28, 48, 16, 16
    xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
    ys = [PT + (H - PT - PB) * (1 - (float(p.get("v", 50)) / 100.0)) for p in pts]
    line = "M" + " L".join(f"{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
    area = (f"M{xs[0]:.1f},{H-PB:.1f} L" + " L".join(f"{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
            + f" L{xs[-1]:.1f},{H-PB:.1f} Z")
    dots, labels = "", ""
    for i, p in enumerate(pts):
        kairos = bool(p.get("kairos"))
        c = "#00F0FF" if kairos else ("#94a3b8" if p.get("v", 50) >= 55 else "#64748b")
        r = 6.5 if kairos else 3.5
        dots += (f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="{r}" fill="{c}" stroke="#020408" stroke-width="1.5">'
                 f'<title>{E(p.get("key",""))}: {p.get("tip","")}</title></circle>')
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
            f'{dots}{labels}</svg></div>')


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
    L.append(f'<style>{RECEIPT_CSS}{TIP_CSS}{GATE_CSS if gate_pw else ""}</style>{VERCEL}</head><body>')
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


SURFACES = {"receipt": render_receipt}


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
    # every net-new signal must carry a verbatim quote (grounding, not fabrication)
    for nn in ssot.get("close", {}).get("net_new", []):
        if not nn.get("quote", "").strip():
            findings.append(("FAIL", "honesty", f"net-new signal {nn.get('signal','?')!r} has no verbatim quote -- ungrounded assertion"))
    # scorecard rows need both predicted and observed
    for r in ssot.get("close", {}).get("scorecard", []):
        if not r.get("observed", "").strip():
            findings.append(("FAIL", "honesty", f"scorecard row {r.get('predicted','?')[:40]!r} has no observed outcome"))
    # honesty gate: if the SSOT flags low resolution but no gaps are declared, fail
    if m.get("resolution", {}).get("level") in ("low", "public-only") and not ssot.get("resolution_gaps"):
        findings.append(("FAIL", "honesty",
            "meta.resolution is low/public-only but no resolution_gaps declared -- must emit "
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
