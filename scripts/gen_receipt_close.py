#!/usr/bin/env python3
"""Render a forensic Receipt-Close artifact (self-contained standalone HTML).
Ex-ante receipt (confidence-scored) -> kinematic manifold -> reverse listening at
adaptive time dilation -> kairos lock -> auto-close scorecard + net-new priors ->
posterior -> next move -> S-tier menu. Reuses the ARCS recoil design grammar.

Usage: python3 scripts/gen_receipt_close.py <reportId> <out.html>
"""
import json, html, sys

reportId = sys.argv[1] if len(sys.argv) > 1 else "2026-08-05-robin-daniels-receipt-close"
out = sys.argv[2] if len(sys.argv) > 2 else "_ARTIFACTS/robin-receipt-close.html"
d = json.load(open(f"runtime/recoil/generated/{reportId}.json"))
E = lambda s: html.escape(str(s))
KIND = {"kairos": "#00F0FF", "peak": "#C9A227", "park": "#E34F1C", "rising": "#8E8E95", "base": "#6E6E75"}
VERD = {"hit": ("#5C8A4E", "HIT"), "partial": ("#C9A227", "PARTIAL"), "miss": ("#E34F1C", "MISS")}
DIL = {"dilated": "#00F0FF", "real": "#C9A227", "compressed": "#6E6E75"}

cov = d["cover"]
badges = "".join(f'<span class="badge">{E(b)}</span>' for b in cov["badges"])
meta_html = E(cov["meta"]).replace("\n", "<br>")

# --- ex-ante receipt (confidence bars) ---
ea = d["exAnte"]
preds = "".join(f'''
      <div class="pred">
        <div class="predbar"><div class="predfill" style="width:{p['confidence']}%"></div><span class="predpct">{p['confidence']}%</span></div>
        <div class="predbody"><p class="predclaim">{E(p['claim'])}</p><p class="predmeta">{E(p['weight'])} &middot; {E(p['basis'])}</p></div>
      </div>''' for p in ea["predictions"])
exante = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The ex-ante receipt &nbsp;&middot;&nbsp; the bet, filed before the call</div>
      <p class="lede">{E(ea["filedNote"])}</p>
      <div class="betbox"><span class="betk">THE BET</span><p>{E(ea["bet"])}</p></div>
      <div class="preds">{preds}</div>
      <div class="kairoslock pre"><span class="klk">KAIROS, CALLED IN ADVANCE</span><p>{E(ea["kairosLock"])}</p></div>
    </section>'''

# --- kinematic manifold ---
kin = d["kinematics"]
pts = kin["points"]
W, H, PT, PB, PL, PR = 720, 200, 26, 48, 16, 16
n = len(pts)
xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
ys = [PT + (H - PT - PB) * (1 - (p["v"] / 100)) for p in pts]
line = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
area = f"M{xs[0]:.1f},{H-PB} " + " ".join(f"L{xs[i]:.1f},{ys[i]:.1f}" for i in range(n)) + f" L{xs[-1]:.1f},{H-PB} Z"
dots = labels = ""
for i, p in enumerate(pts):
    c = KIND.get(p["kind"], "#8E8E95")
    r = 6.5 if p["kind"] in ("kairos", "peak", "park") else 3.5
    dots += (f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="{r}" fill="{c}" stroke="#0B0B0C" stroke-width="1.5">'
             f'<title>{E(p["t"])}: {E(p.get("note",""))}</title></circle>')
    if p["kind"] in ("kairos", "peak", "park"):
        labels += (f'<text x="{xs[i]:.1f}" y="{ys[i]-13:.1f}" text-anchor="middle" fill="{c}" '
                   f'font-family="ui-monospace,monospace" font-size="9.5" letter-spacing="0.05em">{E(p["kind"].upper())}</text>')
    labels += (f'<text x="{xs[i]:.1f}" y="{H-PB+15:.1f}" text-anchor="middle" fill="#6E6E75" '
               f'font-family="ui-monospace,monospace" font-size="8">{E(p["t"])}</text>')
manifold = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The call, as a waveform &nbsp;&middot;&nbsp; call 3, Aug 5</div>
      <div class="manifold">
        <svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Resonance across call 3">
          <defs><linearGradient id="mf" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#00F0FF" stop-opacity="0.16"/><stop offset="1" stop-color="#00F0FF" stop-opacity="0"/></linearGradient></defs>
          <line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="#232326" stroke-width="1"/>
          <path d="{area}" fill="url(#mf)"/>
          <path d="{line}" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
          {dots}{labels}
        </svg>
      </div>
      <p class="mcap">{E(kin["caption"])}</p>
    </section>'''

# --- reverse listening at adaptive time dilation ---
rl = d["reverseListening"]
walk = ""
for b in rl["walk"]:
    dc = DIL.get(b["dilation"], "#6E6E75")
    cls = "beat " + b["dilation"]
    walk += f'''
      <div class="{cls}" style="--dc:{dc}">
        <div class="beath"><span class="beatt">{E(b['t'])}</span><span class="beatdil">{E(b['dilation'].upper())} RESOLUTION</span></div>
        <div class="beatlabel">{E(b['label'])}</div>
        <p class="beatq">&ldquo;{E(b['quote'])}&rdquo;</p>
        <p class="beatread">{E(b['read'])}</p>
      </div>'''
reverse = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Reverse listening &nbsp;&middot;&nbsp; read from the close, resolution spent on the signal</div>
      <p class="lede">{E(rl["method"])}</p>
      <div class="rlwalk">{walk}</div>
    </section>'''

# --- kairos lock ---
k = d["kairos"]
kairos = f'''
    <section class="sec">
      <div class="kairoslock"><span class="klk">&#9679; KAIROS, WRITE-LOCKED &nbsp;&middot;&nbsp; {E(k['at'])}</span>
        <blockquote>&ldquo;{E(k['quote'])}&rdquo;</blockquote>
        <p>{E(k['why'])}</p>
      </div>
    </section>'''

# --- auto-close scorecard ---
ac = d["autoClose"]
rows = ""
for s in ac["scored"]:
    vc, vl = VERD.get(s["verdict"], ("#8E8E95", s["verdict"].upper()))
    rows += f'''
      <div class="scrow">
        <div class="scv" style="--vc:{vc}">{vl}</div>
        <div class="scb"><p class="scp"><span class="scl">Predicted</span>{E(s['predicted'])}</p>
          <p class="sco"><span class="scl">Observed</span>{E(s['observed'])}</p></div>
        <div class="scd">{E(s['delta'])}</div>
      </div>'''
netnew = "".join(f'''
      <div class="nn">
        <div class="nnk">NET-NEW SIGNAL</div>
        <p class="nns">{E(x['signal'])}</p>
        <p class="nnq">&ldquo;{E(x['quote'])}&rdquo;</p>
        <p class="nnu"><b>Prior update:</b> {E(x['priorUpdate'])}</p>
      </div>''' for x in ac["netNew"])
po = ac["posterior"]
autoclose = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The receipt auto-closes &nbsp;&middot;&nbsp; ex-ante scored against reality</div>
      <div class="closestatus"><span class="csk">STATUS</span><span class="csv">{E(ac['status'])}</span><p>{E(ac['headline'])}</p></div>
      <div class="scard">{rows}</div>
      <div class="eyebrow2">Priors updated by net-new information</div>
      <div class="nns-wrap">{netnew}</div>
      <div class="posterior">
        <span class="pok">THE POSTERIOR &nbsp;&middot;&nbsp; what the receipt taught me</span>
        <p class="powedge"><b>Wedge:</b> {E(po['wedge'])}</p>
        <p><b>Status:</b> {E(po['status'])}</p>
        <p><b>Register:</b> {E(po['register'])}</p>
        <p class="ponote">{E(po['note'])}</p>
      </div>
    </section>'''

# --- next move ---
nm = d["nextMove"]
steps = "".join(f'''
      <div class="nmstep">
        <div class="nmk">{E(s['label'])}</div>
        <div class="nmb"><h3>{E(s['title'])}</h3><p>{E(s['body'])}</p></div>
      </div>''' for s in nm["steps"])
nextmove = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The next move &nbsp;&middot;&nbsp; {E(nm['headline'])}</div>
      {steps}
    </section>'''

# --- s-tier menu ---
menu = "".join(f'''
      <div class="menu">
        <div class="menuh">{E(m['name'])}</div>
        <p class="menuw">{E(m['what'])}</p>
        <p class="menupull"><b>Why it pulls him in:</b> {E(m['whyItPulls'])}</p>
      </div>''' for m in d["sTierMenu"])
smenu = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> S-tier artifacts to pull him further</div>
      <div class="menus">{menu}</div>
    </section>'''

CSS = '''<style>
  :root{--case:#0B0B0C;--panel:#131315;--line:#232326;--dial:#E8E4DA;--graphite:#8E8E95;--faint:#6E6E75;
    --gold:#C9A227;--gold-lift:#E0BE4A;--verm:#E34F1C;--ok:#5C8A4E;--cyan:#00F0FF;
    --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,monospace;--sans:"Helvetica Neue",Helvetica,Arial,sans-serif;}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--case)}
  .recoil{background:var(--case);color:var(--dial);font-family:var(--sans);line-height:1.5;
    background-image:radial-gradient(1200px 640px at 50% -8%,rgba(0,240,255,.06),transparent 62%);min-height:100%;padding:0 0 90px}
  .recoil ::selection{background:rgba(0,240,255,.24);color:#fff}
  .wrap{max-width:820px;margin:0 auto;padding:0 26px}
  .recoil h1,.recoil h3{text-wrap:balance;font-weight:700;letter-spacing:-.015em}
  .recoil p{text-wrap:pretty}
  .cover{padding:56px 0 8px;position:relative}
  .glyph{position:absolute;top:44px;right:2px;font-size:76px;color:var(--cyan);opacity:.08;line-height:1;user-select:none}
  .badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
  .badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan);
    border:1px solid rgba(0,240,255,.34);border-radius:100px;padding:5px 11px}
  .cover h1{font-size:clamp(28px,3.2vw + 14px,42px);line-height:1.08;max-width:22ch}
  .cover .sub{margin-top:14px;font-size:16.5px;color:var(--dial);opacity:.9;max-width:70ch;line-height:1.55}
  .cover .meta{margin-top:16px;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;color:var(--graphite);line-height:1.9}
  .sec{margin-top:46px}
  .eyebrow{font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--graphite);
    display:flex;align-items:center;gap:12px;margin-bottom:18px}
  .eyebrow::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
  .eyebrow b{color:var(--cyan)}
  .eyebrow2{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--graphite);margin:22px 2px 12px}
  .lede{font-size:15px;color:#cdcbc3;line-height:1.6;max-width:74ch;margin-bottom:18px}
  /* ex-ante */
  .betbox{border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:12px;background:linear-gradient(180deg,rgba(201,162,39,.06),transparent);padding:18px 20px;margin-bottom:16px}
  .betk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--gold);font-weight:700;display:block;margin-bottom:8px}
  .betbox p{font-size:15px;color:#e6e0d6;line-height:1.55}
  .preds{display:grid;gap:9px}
  .pred{display:grid;grid-template-columns:150px 1fr;gap:16px;align-items:center;border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:12px 15px}
  .predbar{position:relative;height:22px;background:#0d0d0f;border:1px solid var(--line);border-radius:5px;overflow:hidden}
  .predfill{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,rgba(201,162,39,.5),rgba(201,162,39,.85));border-right:1px solid var(--gold-lift)}
  .predpct{position:absolute;right:6px;top:50%;transform:translateY(-50%);font-family:var(--mono);font-size:10px;font-weight:700;color:#0B0B0C;mix-blend-mode:screen;filter:invert(1)}
  .predclaim{font-size:13.5px;color:#d4d2ca;line-height:1.45}
  .predmeta{font-family:var(--mono);font-size:9px;letter-spacing:.04em;color:var(--faint);margin-top:4px;text-transform:uppercase}
  .kairoslock{border:1px solid rgba(0,240,255,.3);border-radius:12px;background:linear-gradient(180deg,rgba(0,240,255,.06),transparent 65%);padding:20px 22px;margin-top:16px}
  .kairoslock.pre{border-color:rgba(201,162,39,.28);background:linear-gradient(180deg,rgba(201,162,39,.05),transparent 65%)}
  .klk{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--cyan);font-weight:700;display:block;margin-bottom:10px}
  .kairoslock.pre .klk{color:var(--gold)}
  .kairoslock blockquote{font-size:clamp(17px,1.2vw+12px,21px);font-weight:600;line-height:1.4;color:#F1EEE6;margin-bottom:12px}
  .kairoslock p{font-size:13.5px;color:#c4c2ba;line-height:1.58}
  /* manifold */
  .manifold{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:16px 14px 8px}
  .mcap{margin-top:12px;font-size:13px;color:var(--graphite);line-height:1.6;max-width:74ch}
  /* reverse listening / time dilation */
  .rlwalk{display:grid;gap:11px}
  .beat{border:1px solid var(--line);border-left:3px solid var(--dc);border-radius:11px;background:var(--panel);padding:15px 18px}
  .beat.compressed{opacity:.72;padding:11px 16px;background:#0e0e10}
  .beat.dilated{border-width:1px;border-left-width:4px;background:linear-gradient(180deg,rgba(0,240,255,.05),transparent 60%);box-shadow:0 0 0 1px rgba(0,240,255,.08)}
  .beath{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:8px}
  .beatt{font-family:var(--mono);font-size:10px;letter-spacing:.12em;font-weight:700;color:var(--dc)}
  .beatdil{font-family:var(--mono);font-size:8px;letter-spacing:.12em;color:var(--faint)}
  .beatlabel{font-size:15px;font-weight:700;color:#F1EEE6;margin-bottom:7px}
  .beat.compressed .beatlabel{font-size:13.5px;font-weight:600}
  .beatq{font-size:13.5px;font-style:italic;color:#d0cec6;line-height:1.5;margin-bottom:8px}
  .beat.compressed .beatq{font-size:12.5px;margin-bottom:5px}
  .beat.dilated .beatq{font-size:15.5px;color:#F1EEE6}
  .beatread{font-size:13px;color:var(--graphite);line-height:1.58;border-top:1px solid var(--line);padding-top:8px}
  .beat.dilated .beatread{color:#c0beb6}
  /* auto-close */
  .closestatus{border:1px solid rgba(92,138,78,.4);border-radius:12px;background:linear-gradient(180deg,rgba(92,138,78,.07),transparent);padding:18px 20px;margin-bottom:18px}
  .csk{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--ok);font-weight:700;margin-right:12px}
  .csv{font-family:var(--mono);font-size:12px;letter-spacing:.1em;color:#8fbf7e;font-weight:700}
  .closestatus p{font-size:14.5px;color:#e0ded6;line-height:1.55;margin-top:10px}
  .scard{display:grid;gap:8px}
  .scrow{display:grid;grid-template-columns:78px 1fr 120px;gap:14px;align-items:start;border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:13px 15px}
  .scv{font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;font-weight:700;color:var(--vc);border:1px solid var(--vc);border-radius:100px;padding:4px 0;text-align:center}
  .scl{font-family:var(--mono);font-size:8px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:2px}
  .scp{font-size:13px;color:#cbc9c1;line-height:1.45;margin-bottom:8px}
  .sco{font-size:13px;color:#d6d4cc;line-height:1.45}
  .scd{font-family:var(--mono);font-size:10px;color:var(--graphite);line-height:1.5;letter-spacing:.02em}
  .nns-wrap{display:grid;gap:10px}
  .nn{border:1px solid var(--line);border-left:3px solid var(--cyan);border-radius:11px;background:#101012;padding:14px 16px}
  .nnk{font-family:var(--mono);font-size:8.5px;letter-spacing:.16em;color:var(--cyan);font-weight:700;margin-bottom:7px}
  .nns{font-size:15px;font-weight:700;color:#F1EEE6;margin-bottom:6px}
  .nnq{font-size:13px;font-style:italic;color:var(--graphite);line-height:1.5;margin-bottom:8px}
  .nnu{font-size:13px;color:#c0beb6;line-height:1.56}.nnu b{color:var(--dial)}
  .posterior{border:1px solid rgba(0,240,255,.28);border-radius:12px;background:linear-gradient(180deg,rgba(0,240,255,.05),transparent 60%);padding:20px 22px;margin-top:18px}
  .pok{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--cyan);font-weight:700;display:block;margin-bottom:12px}
  .posterior p{font-size:14px;color:#d4d2ca;line-height:1.58;margin-bottom:8px}.posterior b{color:#F1EEE6}
  .powedge{font-size:15px !important;color:#e6e0d6 !important}
  .ponote{color:var(--graphite) !important;font-size:13px !important;border-top:1px solid var(--line);padding-top:10px;margin-top:4px}
  /* next move */
  .nmstep{display:grid;grid-template-columns:110px 1fr;gap:14px;padding:14px 0;border-top:1px solid var(--line)}
  .nmstep:first-of-type{border-top:0}
  .nmk{font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--cyan);font-weight:700;padding-top:3px}
  .nmb h3{font-size:15.5px;margin-bottom:5px}
  .nmb p{font-size:13.5px;color:#c0beb6;line-height:1.58}
  /* s-tier menu */
  .menus{display:grid;grid-template-columns:1fr 1fr;gap:11px}
  .menu{border:1px solid var(--line);border-radius:11px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:15px 17px}
  .menuh{font-size:15px;font-weight:700;color:#F1EEE6;margin-bottom:6px}
  .menuh::before{content:"\\25C8 ";color:var(--cyan);font-size:12px}
  .menuw{font-size:13px;color:#c4c2ba;line-height:1.5;margin-bottom:8px}
  .menupull{font-size:12.5px;color:var(--graphite);line-height:1.55}.menupull b{color:var(--dial)}
  .foot{margin-top:52px;padding-top:18px;border-top:1px solid var(--line);text-align:center;
    font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--faint);line-height:2}
  .foot b{color:var(--cyan)}
  @media(max-width:680px){
    .pred,.scrow,.nmstep,.menus{grid-template-columns:1fr;gap:8px}
  }
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>'''

body = f'''
<div class="recoil"><div class="wrap">
  <header class="cover">
    <span class="glyph" aria-hidden="true">&#20214;</span>
    <div class="badges">{badges}</div>
    <h1>{E(cov['title'])}</h1>
    <p class="sub">{E(cov['subtitle'])}</p>
    <div class="meta">{meta_html}</div>
  </header>
  {exante}
  {manifold}
  {reverse}
  {kairos}
  {autoclose}
  {nextmove}
  {smenu}
  <footer class="foot">ARCS &middot; FIELD OS &middot; FORENSIC RECEIPT CLOSE &middot; ROBIN DANIELS, CALL 3<br><b>FILE THE BET &middot; SCORE AGAINST REALITY &middot; LET THE RECEIPT TEACH YOU THE WEDGE</b></footer>
</div></div>'''

DOC = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robin Daniels &middot; Receipt Close &middot; Call 3</title>{CSS}</head><body>{body}</body></html>'''

open(out, "w").write(DOC)
print("wrote", out, len(DOC), "bytes | em-dashes:", DOC.count("—"))
