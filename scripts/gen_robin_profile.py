#!/usr/bin/env python3
"""Robin enriched-profile read (step 1 of the loop). Cockpit grammar, gated 'robin'.
Usage: python3 scripts/gen_robin_profile.py <reportId> <out.html>"""
import json, html, sys
reportId = sys.argv[1] if len(sys.argv) > 1 else "2026-08-05-robin-profile"
out = sys.argv[2] if len(sys.argv) > 2 else "_ARTIFACTS/robin-profile.html"
d = json.load(open(f"runtime/recoil/generated/{reportId}.json"))
E = lambda s: html.escape(str(s))
hk = d["hook"]

regs = "".join(f'''
  <div class="reg" style="--ac:{'#FFD700' if r['altitude']!='GROUND' else '#00FF9D'}">
    <div class="regh"><span class="regn">{E(r['name'])}</span><span class="regalt">{E(r['altitude'])}</span></div>
    <p class="regcues">{E(" · ".join(r['cues']))}</p>
    <p class="regq">&ldquo;{E(r['quote'])}&rdquo;<span class="regsrc">{E(r['source'])}</span></p>
  </div>''' for r in d["registers"])
vocab = "".join(f'<span class="chip">{E(v)}</span>' for v in d["vocab"])
rungs = "".join(f'''
  <div class="rung"><div class="rlvl">{E(r['alt'])}</div><div class="rb"><p>{E(r['whatHeDoes'])}</p><p class="rt"><b>Trigger:</b> {E(r['trigger'])}</p></div></div>''' for r in d["altitude"]["ladder"])
lands = "".join(f"<li>{E(x)}</li>" for x in d["resonance"]["lands"])
loses = "".join(f"<li>{E(x)}</li>" for x in d["resonance"]["loses"])
site = "".join(f'<div class="scard"><div class="sh">{E(s["h"])}</div><p>{E(s["d"])}</p></div>' for s in d["corpus"]["site"])
pods = "".join(f'<span class="chip">{E(x)}</span>' for x in d["corpus"]["podcasts"])
talks = "".join(f'<span class="chip">{E(x)}</span>' for x in d["corpus"]["talks"])
stages = "".join(f'''
  <div class="stg">
    <div class="stn">{E(s['n'])}</div>
    <div class="stb"><div class="sts">{E(s['s'])}</div><p>{E(s['w'])}{f' &middot; <a href="{E(s["href"])}" target="_blank" rel="noopener">open &#8599;</a>' if s.get('href') else ''}</p></div>
  </div>''' for s in d["loop"]["stages"])

CSS = '''<style>
:root{--bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--border:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--dimmed:#64748b;--cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;--mono:ui-monospace,'SF Mono','Fira Code',monospace;--sans:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;}
*{box-sizing:border-box;margin:0;padding:0}h1,h2,h3{text-wrap:balance}p{text-wrap:pretty}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;padding:44px 22px 96px}
.page{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
.uplink{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);text-decoration:none;margin-bottom:2px}.uplink:hover{color:var(--cyan)}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed)}
h1{font-size:27px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.18}
.sub{font-size:14.5px;color:var(--muted);margin-top:10px;max-width:66ch;line-height:1.6}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3}
.mv{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:24px}
.mvk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dimmed);margin-bottom:10px}
.mv h2{font-size:20px;font-weight:700;letter-spacing:-.01em;margin-bottom:6px}
.lede{font-size:14px;color:var(--muted);line-height:1.6;margin-bottom:16px;max-width:68ch}
.headline{font-size:17px;color:#fff;font-weight:700;margin-bottom:14px;max-width:44ch}
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
.close{font-size:15px;color:#e4ded4;line-height:1.6;border-left:3px solid var(--gold);padding:4px 0 4px 16px}
.foot{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--dimmed);text-align:center;padding-top:8px;line-height:2}
#pw-gate{position:fixed;inset:0;background:#020408;display:flex;align-items:center;justify-content:center;z-index:100;flex-direction:column;gap:16px}#pw-gate.hidden{display:none}
.pw-label{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#475569}
.pw-input{background:#0d1117;border:1px solid #1e293b;border-radius:8px;color:#e2e8f0;font-size:16px;padding:10px 16px;outline:none;width:200px;text-align:center;letter-spacing:.1em}
.pw-input:focus{border-color:#00F0FF}.pw-input.shake{animation:shk .3s ease;border-color:#FF4D6D}
@keyframes shk{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
@media(max-width:560px){.two,.rmap,.scards{grid-template-columns:1fr}.rung{grid-template-columns:1fr;gap:4px}}
</style><script defer src="/_vercel/insights/script.js"></script>'''

body = f'''<div class="page">
  <div><a class="uplink" href="https://robin.arcs.care">&#8593; the studio</a><div class="eyebrow">{E(hk['eyebrow'])}</div><h1>{E(hk['title'])}</h1><p class="sub">{E(hk['sub'])}</p></div>
  <div class="rule"></div>
  <section class="mv"><div class="mvk">01 &middot; your voice</div><h2>Two registers, one person.</h2>
    <p class="headline">{E(d['headline'])}</p><div class="two">{regs}</div><div class="chips">{vocab}</div></section>
  <section class="mv"><div class="mvk">02 &middot; adaptive altitude</div><h2>Meet you at the ground, let you climb.</h2>
    <p class="lede">{E(d['altitude']['summary'])}</p><div class="ladder">{rungs}</div></section>
  <section class="mv"><div class="mvk">03 &middot; what lands, what loses you</div><h2>The resonance map.</h2>
    <div class="rmap"><div class="rcol l"><div class="rmk">&#9650; LANDS</div><ul>{lands}</ul></div><div class="rcol x"><div class="rmk">&#9660; LOSES YOU</div><ul>{loses}</ul></div></div></section>
  <section class="mv"><div class="mvk">04 &middot; the evidence</div><h2>Tuned on your own words.</h2>
    <p class="lede">{E(d['corpus']['intro'])}</p><div class="scards">{site}</div>
    <div class="csub">Podcasts</div><div class="chips" style="margin-top:0">{pods}</div>
    <div class="csub">Talks</div><div class="chips" style="margin-top:0">{talks}</div></section>
  <section class="mv"><div class="mvk">05 &middot; the whole loop</div><h2>{E(d['loop']['title'])}</h2>
    <p class="lede">{E(d['loop']['intro'])}</p>{stages}<p class="close" style="margin-top:16px">{E(d['loop']['note'])}</p></section>
  <p class="close">{E(d['close'])}</p>
  <div class="foot">ARCS &middot; THE PROFILE READ &middot; STEP ONE OF THE LOOP &middot; BUILT FROM YOUR PUBLIC VOICE</div>
</div>'''

GATE = '''<div id="pw-gate"><div class="pw-label">ARCS &middot; Private &middot; for Robin</div><input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>'''
JS = '''<script>(function(){var K='robin-profile-auth',P='robin';if(sessionStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;if(i.value.toLowerCase()===P){sessionStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');try{if(window.va)va('event',{name:'unlock',data:{page:'robin-profile'}});}catch(e){}}else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();</script>'''
DOC = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow"><title>Robin &middot; the profile read</title>{CSS}</head><body>{body}</body></html>'''
open(out, "w").write(DOC)
print("wrote", out, len(DOC), "bytes | em-dashes:", DOC.count("—"))
