#!/usr/bin/env python3
"""Render an ARCS-canon Recoil Report HTML artifact from a generated report JSON.
Usage: python3 scripts/gen_recoil_artifact.py <reportId> <out.html>
Self-contained page CONTENT (no doctype/head/body) for publishing as a Claude Artifact."""
import json, html, sys, math

reportId = sys.argv[1] if len(sys.argv) > 1 else "2026-07-31-delaney"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/recoil-artifact.html"
d = json.load(open(f"runtime/recoil/generated/{reportId}.json"))
E = lambda s: html.escape(str(s))
sev = {"warning": ("#E34F1C", "WARNING"), "caution": ("#C9A227", "CAUTION"),
       "info": ("#00F0FF", "NOTE"), "success": ("#5C8A4E", "GOOD")}
KIND = {"peak": "#C9A227", "kairos": "#00F0FF", "park": "#E34F1C", "rising": "#8E8E95", "base": "#6E6E75"}

cov, q = d["cover"], d["loadBearingQuote"]
badges = "".join(f'<span class="badge">{E(b)}</span>' for b in cov["badges"])

# --- kinematic manifold (SVG sparkline) ---
kin = d.get("kinematics")
manifold = ""
if kin:
    pts = kin["points"]
    W, H, PT, PB, PL, PR = 720, 190, 22, 40, 14, 14
    n = len(pts)
    xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
    ys = [PT + (H - PT - PB) * (1 - (p["v"] / 100)) for p in pts]
    line = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
    area = f"M{xs[0]:.1f},{H-PB} " + " ".join(f"L{xs[i]:.1f},{ys[i]:.1f}" for i in range(n)) + f" L{xs[-1]:.1f},{H-PB} Z"
    dots, labels = "", ""
    for i, p in enumerate(pts):
        c = KIND.get(p["kind"], "#8E8E95")
        r = 6 if p["kind"] in ("peak", "kairos", "park") else 3.5
        dots += (f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="{r}" fill="{c}" '
                 f'stroke="#0B0B0C" stroke-width="1.5"><title>{E(p["t"])}: {E(p.get("note",""))}</title></circle>')
        if p["kind"] in ("peak", "kairos", "park"):
            dy = ys[i] - 13 if p["kind"] != "park" else ys[i] + 20
            labels += (f'<text x="{xs[i]:.1f}" y="{dy:.1f}" text-anchor="middle" '
                       f'fill="{c}" font-family="ui-monospace,monospace" font-size="9.5" '
                       f'letter-spacing="0.05em">{E(p["kind"].upper())}</text>')
        labels += (f'<text x="{xs[i]:.1f}" y="{H-PB+15:.1f}" text-anchor="middle" '
                   f'fill="#6E6E75" font-family="ui-monospace,monospace" font-size="8.5">{E(p["t"])}</text>')
    manifold = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The kinematic manifold &nbsp;·&nbsp; where it peaked, where it parked</div>
      <div class="manifold">
        <svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img"
             aria-label="Resonance gradient across the call">
          <defs>
            <linearGradient id="mfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#C9A227" stop-opacity="0.18"/>
              <stop offset="1" stop-color="#C9A227" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="#232326" stroke-width="1"/>
          <path d="{area}" fill="url(#mfill)"/>
          <path d="{line}" fill="none" stroke="#C9A227" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
          {dots}{labels}
        </svg>
      </div>
      <p class="mcap">{E(kin["caption"])}</p>
    </section>'''

# --- bookmarks (ADR-038 primitive): where to re-enter ---
BK = {"peak": "#C9A227", "park": "#E34F1C", "probe": "#00F0FF"}
bookmarks = d.get("bookmarks")
bm = ""
if bookmarks:
    cards = "".join(f'''
      <div class="bm" style="--bc:{BK.get(b['kind'],'#8E8E95')}">
        <div class="bmh"><span class="bmk">{E(b['kind'].upper())}</span><span class="bmat">{E(b['at'])}</span></div>
        <div class="bml">{E(b['label'])}</div>
        <p class="bmw">{E(b['why'])}</p>
        {f'<p class="bmq">&ldquo;{E(b["quote"])}&rdquo;</p>' if b.get('quote') else ''}
      </div>''' for b in bookmarks)
    bm = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Bookmarks &nbsp;·&nbsp; where to re-enter, where to hold, what to probe</div>
      <div class="bms">{cards}</div>
    </section>'''

cw = "".join(f'''
    <div class="step{' peak' if s.get('peak') else ''}">
      <div class="srail" aria-hidden="true"></div>
      <div class="sbody">
        <div class="slabel">{E(s['label'])}{' · PEAK' if s.get('peak') else ''}</div>
        <h3>{E(s['title'])}</h3>
        <p>{E(s['body'])}</p>
      </div>
    </div>''' for s in d['callWalk'])
sig = "".join(f'''
    <article class="sig" style="--ac:{E(s['accent'])}">
      <div class="sk">{E(s['label'])}</div>
      <h3>{E(s['title'])}</h3>
      <p>{E(s['body'])}</p>
      {f'<p class="note"><b>Move:</b> {E(s["note"])}</p>' if s.get('note') else ''}
    </article>''' for s in d['signalThreads'])
sc = d['scenarios']
def scen(k, r):
    x = sc[k]
    return f'''
    <div class="scen {k}">
      <div class="sck">{r}</div>
      <h3>{E(x['title'])}</h3>
      <p>{E(x['body'])}</p>
      {f'<p class="note">{E(x["note"])}</p>' if x.get('note') else ''}
    </div>'''
scen_html = scen('best', 'BEST') + scen('base', 'BASE · most likely') + scen('worst', 'WORST')
risk = "".join(f'''
    <div class="risk" style="--sv:{sev.get(r['variant'],('#8E8E95','NOTE'))[0]}">
      <div class="rk">{sev.get(r['variant'],('#8E8E95','NOTE'))[1]} · {E(r['label'])}</div>
      <p>{E(r['body'])}</p>
    </div>''' for r in d['riskFlags'])
proto = "".join(f'''
    <div class="pstep{' active' if p.get('active') else ''}">
      <div class="pn">{E(p['label'])}{' · DO NOW' if p.get('active') else ''}</div>
      <div class="pbody"><h3>{E(p['title'])}</h3><p>{E(p['body'])}</p></div>
    </div>''' for p in d['protocol'])

CSS = '''<style>
  :root{
    --case:#0B0B0C; --panel:#131315; --panel2:#17171A; --line:#232326;
    --dial:#E8E4DA; --graphite:#8E8E95; --faint:#6E6E75;
    --gold:#C9A227; --gold-lift:#E0BE4A; --verm:#E34F1C; --red:#B4342A; --ok:#5C8A4E; --cyan:#00F0FF;
    --mono: ui-monospace,"SF Mono","Cascadia Mono",Menlo,monospace;
    --sans:"Helvetica Neue",Helvetica,Arial,sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  .recoil{background:var(--case);color:var(--dial);font-family:var(--sans);line-height:1.5;
    background-image:radial-gradient(1200px 640px at 50% -8%, rgba(201,162,39,.06), transparent 62%);
    min-height:100%;padding:0 0 90px}
  .recoil ::selection{background:rgba(201,162,39,.28);color:#fff}
  .wrap{max-width:780px;margin:0 auto;padding:0 26px}
  .recoil h1,.recoil h2,.recoil h3{text-wrap:balance;font-weight:700;letter-spacing:-.015em}
  .recoil p{text-wrap:pretty}
  .cover{padding:56px 0 8px;position:relative}
  .glyph{position:absolute;top:44px;right:2px;font-size:76px;color:var(--gold);opacity:.09;line-height:1;user-select:none}
  .badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
  .badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);
    border:1px solid rgba(201,162,39,.4);border-radius:100px;padding:5px 11px}
  .cover h1{font-size:clamp(28px,3.2vw + 14px,42px);line-height:1.08;max-width:20ch}
  .cover .sub{margin-top:14px;font-size:16.5px;color:var(--dial);opacity:.9;max-width:62ch;line-height:1.55}
  .cover .meta{margin-top:16px;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:var(--graphite);line-height:1.9}
  .lbq{margin:30px 0 8px;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:12px;
    background:linear-gradient(180deg,rgba(201,162,39,.06),transparent 70%);padding:26px 28px 22px;position:relative;overflow:hidden}
  .lbq::after{content:"";position:absolute;right:-30px;top:-30px;width:90px;height:90px;pointer-events:none;
    background:linear-gradient(140deg,transparent 44%,var(--gold) 47%,var(--gold-lift) 50%,var(--gold) 53%,transparent 56%);opacity:.14}
  .lbq .lk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--gold);margin-bottom:12px}
  .lbq blockquote{font-size:clamp(18px,1.4vw + 12px,23px);line-height:1.45;font-weight:600;letter-spacing:-.01em;color:#F1EEE6}
  .lbq .attr{margin-top:14px;font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--graphite)}
  .sec{margin-top:46px}
  .eyebrow{font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--graphite);
    display:flex;align-items:center;gap:12px;margin-bottom:20px}
  .eyebrow::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
  .eyebrow b{color:var(--gold);font-weight:700}
  .manifold{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:16px 14px 8px}
  .mcap{margin-top:12px;font-size:13px;color:var(--graphite);line-height:1.6;max-width:64ch}
  .bms{display:grid;grid-template-columns:1fr;gap:10px}
  .bm{border:1px solid var(--line);border-left:3px solid var(--bc);border-radius:11px;background:#101012;padding:14px 16px}
  .bmh{display:flex;align-items:center;gap:10px;margin-bottom:6px}
  .bmk{font-family:var(--mono);font-size:8.5px;letter-spacing:.16em;font-weight:700;color:var(--bc);
    border:1px solid var(--bc);border-radius:100px;padding:2px 8px}
  .bmat{font-family:var(--mono);font-size:9px;letter-spacing:.1em;color:var(--faint)}
  .bml{font-size:15px;font-weight:700;letter-spacing:-.01em;margin-bottom:4px}
  .bmw{font-size:13px;color:#c0beb6;line-height:1.55}
  .bmq{margin-top:7px;font-size:12.5px;color:var(--graphite);font-style:italic;border-top:1px solid var(--line);padding-top:7px;line-height:1.5}
  .step{display:grid;grid-template-columns:14px 1fr;gap:16px;padding-bottom:22px}
  .srail{position:relative}
  .srail::before{content:"";position:absolute;left:5px;top:4px;width:5px;height:5px;border-radius:50%;background:var(--graphite)}
  .srail::after{content:"";position:absolute;left:7px;top:10px;bottom:-22px;width:1px;background:var(--line)}
  .step:last-child .srail::after{display:none}
  .step.peak .srail::before{background:var(--gold);box-shadow:0 0 0 3px rgba(201,162,39,.16)}
  .slabel{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--graphite);margin-bottom:5px}
  .step.peak .slabel{color:var(--gold)}
  .sbody h3{font-size:16.5px;margin-bottom:6px}
  .sbody p{font-size:14px;color:#c4c2ba;line-height:1.6}
  .sig{border:1px solid var(--line);border-left:3px solid var(--ac);border-radius:11px;background:linear-gradient(180deg,var(--panel),#0e0e10);
    padding:17px 19px;margin-bottom:12px}
  .sig .sk{font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--ac);margin-bottom:7px}
  .sig h3{font-size:16px;margin-bottom:7px}
  .sig p{font-size:13.5px;color:#c0beb6;line-height:1.6}
  .sig .note{margin-top:9px;font-size:12.5px;color:var(--graphite);border-top:1px solid var(--line);padding-top:9px}
  .sig .note b{color:var(--dial)}
  .scens{display:grid;grid-template-columns:1fr;gap:11px}
  .scen{border:1px solid var(--line);border-radius:11px;padding:16px 18px;background:var(--panel)}
  .scen.base{border-color:rgba(201,162,39,.45)}
  .scen .sck{font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:7px;color:var(--graphite)}
  .scen.best .sck{color:var(--ok)} .scen.base .sck{color:var(--gold)} .scen.worst .sck{color:var(--verm)}
  .scen h3{font-size:15.5px;margin-bottom:6px}
  .scen p{font-size:13.5px;color:#c0beb6;line-height:1.58}
  .scen .note{margin-top:8px;font-size:12.5px;color:var(--graphite)}
  .risk{border:1px solid var(--line);border-left:3px solid var(--sv);border-radius:10px;padding:13px 16px;margin-bottom:10px;background:#101012}
  .risk .rk{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;color:var(--sv);margin-bottom:5px;font-weight:700}
  .risk p{font-size:13px;color:#c0beb6;line-height:1.55}
  .pstep{display:grid;grid-template-columns:96px 1fr;gap:14px;padding:14px 0;border-top:1px solid var(--line)}
  .pstep:first-of-type{border-top:0}
  .pn{font-family:var(--mono);font-size:10px;letter-spacing:.12em;color:var(--graphite);padding-top:3px}
  .pstep.active .pn{color:var(--gold);font-weight:700}
  .pbody h3{font-size:15px;margin-bottom:4px}
  .pbody p{font-size:13.5px;color:#c0beb6;line-height:1.58}
  .foot{margin-top:52px;padding-top:18px;border-top:1px solid var(--line);text-align:center;
    font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--faint);line-height:2}
  .foot b{color:var(--gold)}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>'''

body = f'''
<div class="recoil">
  <div class="wrap">
    <header class="cover">
      <span class="glyph" aria-hidden="true">聴</span>
      <div class="badges">{badges}</div>
      <h1>{E(cov['title'])}</h1>
      <p class="sub">{E(cov['subtitle'])}</p>
      <div class="meta">{E(cov['meta'])}</div>
      <div class="lbq">
        <div class="lk">語 · THE LOAD-BEARING MOMENT</div>
        <blockquote>&ldquo;{E(q['text'])}&rdquo;</blockquote>
        <div class="attr">{E(q['attribution'])}</div>
      </div>
    </header>
    {bm}
    {manifold}
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The call, walked &nbsp;·&nbsp; reverse listening + deep recall</div>{cw}</section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The signals that carry</div>{sig}</section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> Three futures</div><div class="scens">{scen_html}</div></section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> Risk register</div>{risk}</section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The protocol &nbsp;·&nbsp; one dated hook, then let it breathe</div>{proto}</section>
    <footer class="foot">ARCS · FIELD OS · RECOIL REPORT · REVERSE LISTENING + DEEP RECALL<br><b>GROUND IN THE TRANSCRIPT · SCORE AGAINST REALITY · CAPTURE THE 100% SIGNAL</b></footer>
  </div>
</div>'''

open(out, "w").write(CSS + body)
print("wrote", out, len(CSS + body), "bytes | em-dashes:", (CSS + body).count("—"))
