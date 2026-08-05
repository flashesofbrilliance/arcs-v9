#!/usr/bin/env python3
"""Render an enriched-profile + serialized-recoil SEED artifact (self-contained HTML).
Reuses the ARCS Recoil design grammar (scripts/gen_recoil_artifact.py) and adds
profile dossier / rhetorical fingerprint / adaptive-altitude ladder / resonance map /
operator-ensemble grid / deck-seed sections. Output is a full standalone HTML document
(doctype/head/body) so it opens locally per ADR-041 (deliverable durability, local-first).

Usage: python3 scripts/gen_profile_seed.py <reportId> <out.html>
"""
import json, html, sys

reportId = sys.argv[1] if len(sys.argv) > 1 else "2026-11-13-robin-daniels-serialization"
out = sys.argv[2] if len(sys.argv) > 2 else "_ARTIFACTS/robin-daniels-recoil-seed.html"
d = json.load(open(f"runtime/recoil/generated/{reportId}.json"))
E = lambda s: html.escape(str(s))

KIND = {"peak": "#C9A227", "kairos": "#00F0FF", "park": "#E34F1C", "rising": "#8E8E95", "base": "#6E6E75"}
SEV = {"warning": ("#E34F1C", "WARNING"), "caution": ("#C9A227", "CAUTION"),
       "info": ("#00F0FF", "NOTE"), "success": ("#5C8A4E", "GOOD")}

cov, q = d["cover"], d["loadBearingQuote"]
badges = "".join(f'<span class="badge">{E(b)}</span>' for b in cov["badges"])
meta_html = E(cov["meta"]).replace("\n", "<br>")

# --- profile dossier ---
dos = d["dossier"]
facts = "".join(f"<li>{E(f)}</li>" for f in dos["facts"])
dossier = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The dossier &nbsp;&middot;&nbsp; who you are actually talking to</div>
      <div class="dossier">
        <h3 class="dh">{E(dos["headline"])}</h3>
        <p class="darc">{E(dos["arc"])}</p>
        <ul class="dfacts">{facts}</ul>
      </div>
    </section>'''

# --- kinematic manifold ---
kin = d.get("kinematics")
manifold = ""
if kin:
    pts = kin["points"]
    W, H, PT, PB, PL, PR = 720, 210, 26, 52, 16, 16
    n = len(pts)
    xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
    ys = [PT + (H - PT - PB) * (1 - (p["v"] / 100)) for p in pts]
    line = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
    area = f"M{xs[0]:.1f},{H-PB} " + " ".join(f"L{xs[i]:.1f},{ys[i]:.1f}" for i in range(n)) + f" L{xs[-1]:.1f},{H-PB} Z"
    # call-1 / call-2 divider (between index 5 and 6)
    xdiv = (xs[5] + xs[6]) / 2
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
                   f'fill="#6E6E75" font-family="ui-monospace,monospace" font-size="8">{E(p["t"])}</text>')
    manifold = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The kinematic manifold &nbsp;&middot;&nbsp; two calls, one gradient</div>
      <div class="manifold">
        <svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img"
             aria-label="Resonance gradient across both calls">
          <defs>
            <linearGradient id="mfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#C9A227" stop-opacity="0.18"/>
              <stop offset="1" stop-color="#C9A227" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="#232326" stroke-width="1"/>
          <line x1="{xdiv:.1f}" y1="{PT-6}" x2="{xdiv:.1f}" y2="{H-PB}" stroke="#232326" stroke-width="1" stroke-dasharray="3 4"/>
          <text x="{(PL+xdiv)/2:.1f}" y="{PT-10}" text-anchor="middle" fill="#6E6E75" font-family="ui-monospace,monospace" font-size="8.5" letter-spacing="0.12em">CALL 1 &middot; OCT 23 &middot; WARM</text>
          <text x="{(xdiv+W-PR)/2:.1f}" y="{PT-10}" text-anchor="middle" fill="#6E6E75" font-family="ui-monospace,monospace" font-size="8.5" letter-spacing="0.12em">CALL 2 &middot; NOV 13 &middot; COOLED</text>
          <path d="{area}" fill="url(#mfill)"/>
          <path d="{line}" fill="none" stroke="#C9A227" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
          {dots}{labels}
        </svg>
      </div>
      <p class="mcap">{E(kin["caption"])}</p>
    </section>'''

# --- load-bearing quote ---
lbq = f'''
      <div class="lbq">
        <div class="lk">&#35486; &middot; THE LOAD-BEARING MOMENT</div>
        <blockquote>&ldquo;{E(q['text'])}&rdquo;</blockquote>
        <div class="attr">{E(q['attribution'])}</div>
      </div>'''

# --- call walk ---
cw = "".join(f'''
    <div class="step{' peak' if s.get('peak') else ''}">
      <div class="srail" aria-hidden="true"></div>
      <div class="sbody">
        <div class="slabel">{E(s['label'])}{' &middot; PEAK' if s.get('peak') else ''}</div>
        <h3>{E(s['title'])}</h3>
        <p>{E(s['body'])}</p>
      </div>
    </div>''' for s in d['callWalk'])

# --- interference / wave mechanics (per-call phase sparklines + quote pairs) ---
PHASE = {"constructive": "#C9A227", "harmonic": "#00F0FF", "discord": "#5C8A4E", "dissonant": "#E34F1C"}
PHLAB = {"constructive": "CONSTRUCTIVE", "harmonic": "HARMONIC", "discord": "PRODUCTIVE DISCORD", "dissonant": "DISSONANT / LOSSY"}
interference = ""
if d.get("interference"):
    itf = d["interference"]
    legend = "".join(
        f'<span class="lgi"><span class="lgd" style="--c:{l["color"]}"></span>{E(l["label"])}</span>'
        for l in itf["legend"])

    def sparkline(spark):
        W, H, PT, PB, PL, PR = 640, 96, 16, 20, 14, 14
        n = len(spark)
        xs = [PL + (W - PL - PR) * (i / (n - 1 if n > 1 else 1)) for i in range(n)]
        ys = [PT + (H - PT - PB) * (1 - (p["v"] / 100)) for p in spark]
        line = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
        dots = ""
        for i, p in enumerate(spark):
            c = PHASE.get(p["phase"], "#8E8E95")
            dots += (f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="5.5" fill="{c}" '
                     f'stroke="#0B0B0C" stroke-width="1.5"/>')
        return (f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" '
                f'role="img" aria-label="Per-beat phase across the call">'
                f'<line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="#232326" stroke-width="1"/>'
                f'<path d="{line}" fill="none" stroke="#3a3a3e" stroke-width="1.5" '
                f'stroke-linejoin="round" stroke-linecap="round"/>{dots}</svg>')

    calls_html = ""
    for c in itf["calls"]:
        beats = "".join(f'''
          <div class="beat" style="--pc:{PHASE.get(b['phase'],'#8E8E95')}">
            <div class="bph">{E(PHLAB.get(b['phase'], b['phase'].upper()))}</div>
            <div class="bqp"><span class="bql">YOU</span><p>{E(b['zach'])}</p></div>
            <div class="bqp"><span class="bql">ROBIN</span><p>{E(b['robin'])}</p></div>
            <p class="bread">{E(b['read'])}</p>
          </div>''' for b in c["beats"])
        calls_html += f'''
        <div class="ical">
          <div class="icalh"><span class="icaln">{E(c['id'])}</span><span class="icalv">{E(c['verdict'])}</span></div>
          <div class="ispark">{sparkline(c['spark'])}</div>
          <div class="beats">{beats}</div>
        </div>'''

    interference = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Wave mechanics &nbsp;&middot;&nbsp; where we were in phase, where you mid-curved</div>
      <p class="lede">{E(itf["summary"])}</p>
      <div class="legend">{legend}</div>
      {calls_html}
      <div class="midcurve"><span class="mck">THE MID-CURVES</span><p>{E(itf["midcurves"])}</p></div>
    </section>'''

# --- rhetorical fingerprint ---
rf = d["rhetoricalFingerprint"]
regs = "".join(f'''
      <div class="reg">
        <div class="regh"><span class="regn">{E(r['name'])}</span><span class="regalt">{E(r['altitude'])}</span></div>
        <p class="regcues">{E(" &middot; ".join(r['cues']))}</p>
        <p class="regq">&ldquo;{E(r['quote'])}&rdquo;<span class="regsrc">{E(r['source'])}</span></p>
      </div>''' for r in rf["registers"])
vocab = "".join(f'<span class="vchip">{E(v)}</span>' for v in rf["vocab"])
rhetorical = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Rhetorical fingerprint &nbsp;&middot;&nbsp; how he argues, what he answers to</div>
      <p class="lede">{E(rf["summary"])}</p>
      <div class="regs">{regs}</div>
      <div class="vocab">{vocab}</div>
    </section>'''

# --- adaptive altitude ladder ---
aa = d["adaptiveAltitude"]
rungs = "".join(f'''
      <div class="rung">
        <div class="rlvl">{E(r['alt'])}</div>
        <div class="rbody"><p class="rdo">{E(r['whatHeDoes'])}</p><p class="rtrig"><b>Trigger:</b> {E(r['trigger'])}</p></div>
      </div>''' for r in aa["ladder"])
altitude = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Adaptive altitude &nbsp;&middot;&nbsp; meet him at his height, let him climb</div>
      <p class="lede">{E(aa["summary"])}</p>
      <div class="ladder">{rungs}</div>
      <div class="mismatch"><span class="mmk">THE MISMATCH</span><p>{E(aa["mismatch"])}</p></div>
    </section>'''

# --- resonance map ---
rm = d["resonanceMap"]
lands = "".join(f"<li>{E(x)}</li>" for x in rm["lands"])
loses = "".join(f"<li>{E(x)}</li>" for x in rm["loses"])
resonance = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> Resonance map &nbsp;&middot;&nbsp; what lands, what loses him</div>
      <div class="rmap">
        <div class="rcol lands"><div class="rmk">&#9650; LANDS</div><ul>{lands}</ul></div>
        <div class="rcol loses"><div class="rmk">&#9660; LOSES HIM</div><ul>{loses}</ul></div>
      </div>
    </section>'''

# --- operator ensemble ---
ops = "".join(f'''
      <div class="op">
        <div class="oph"><span class="opg">{E(o['glyph'])}</span><span class="opn">{E(o['name'])}</span></div>
        <p>{E(o['verdict'])}</p>
      </div>''' for o in d["operators"])
operators = f'''
    <section class="sec">
      <div class="eyebrow"><b>&#9633;</b> The ensemble reads it &nbsp;&middot;&nbsp; {len(d["operators"])} operators, one verdict each</div>
      <div class="ops">{ops}</div>
    </section>'''

# --- signal threads ---
sig = "".join(f'''
    <article class="sig" style="--ac:{E(s['accent'])}">
      <div class="sk">{E(s['label'])}</div>
      <h3>{E(s['title'])}</h3>
      <p>{E(s['body'])}</p>
      {f'<p class="note"><b>Move:</b> {E(s["note"])}</p>' if s.get('note') else ''}
    </article>''' for s in d['signalThreads'])

# --- scenarios ---
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
scen_html = scen('best', 'BEST') + scen('base', 'BASE &middot; most likely') + scen('worst', 'WORST')

# --- risk register ---
risk = "".join(f'''
    <div class="risk" style="--sv:{SEV.get(r['variant'],('#8E8E95','NOTE'))[0]}">
      <div class="rk">{SEV.get(r['variant'],('#8E8E95','NOTE'))[1]} &middot; {E(r['label'])}</div>
      <p>{E(r['body'])}</p>
    </div>''' for r in d['riskFlags'])

# --- protocol ---
proto = "".join(f'''
    <div class="pstep{' active' if p.get('active') else ''}">
      <div class="pn">{E(p['label'])}{' &middot; DO NOW' if p.get('active') else ''}</div>
      <div class="pbody"><h3>{E(p['title'])}</h3><p>{E(p['body'])}</p></div>
    </div>''' for p in d['protocol'])

# --- deck seed ---
ds = d["deckSeed"]
slides = "".join(f'''
      <div class="slide">
        <div class="sn">{E(s['n'])}</div>
        <div class="sbd"><h3>{E(s['title'])}</h3><p>{E(s['beat'])}</p></div>
      </div>''' for s in ds["slides"])
deckseed = f'''
    <section class="sec deckseed">
      <div class="eyebrow"><b>&#9633;</b> The seed for the deck &nbsp;&middot;&nbsp; this is what the artifact feeds</div>
      <div class="thesis"><span class="thk">THESIS</span><p>{E(ds["thesis"])}</p></div>
      <div class="slides">{slides}</div>
    </section>'''

# --- wedge (the one narrow, survivable hook) ---
wedge = ""
if d.get("wedge"):
    w = d["wedge"]
    whys = "".join(f"<li>{E(x)}</li>" for x in w["why_survivable"])
    rungs = "".join(f'''
      <div class="wrung">
        <div class="wrk">{E(r['rung'])}</div>
        <p>{E(r['ask'])}</p>
      </div>''' for r in w["ladder"])
    wedge = f'''
    <section class="sec wedgesec">
      <div class="eyebrow"><b>&#9633;</b> The wedge &nbsp;&middot;&nbsp; most survivable, highest leverage, lowest downside</div>
      <div class="wtop">
        <div class="wrec">{E(w["recommendation"])}</div>
        <p class="wthis">{E(w["this"])}</p>
        <p class="wnot">{E(w["not_this"])}</p>
      </div>
      <ul class="wwhy">{whys}</ul>
      <div class="wtaste"><span class="wtk">THE TASTE</span><p>{E(w["the_taste"])}</p></div>
      <div class="wladder">{rungs}</div>
      <div class="wwell"><span class="wtk">THE GRAVITY WELL</span><p>{E(w["gravity_well"])}</p></div>
    </section>'''

CSS = '''<style>
  :root{
    --case:#0B0B0C; --panel:#131315; --panel2:#17171A; --line:#232326;
    --dial:#E8E4DA; --graphite:#8E8E95; --faint:#6E6E75;
    --gold:#C9A227; --gold-lift:#E0BE4A; --verm:#E34F1C; --red:#B4342A; --ok:#5C8A4E; --cyan:#00F0FF;
    --mono: ui-monospace,"SF Mono","Cascadia Mono",Menlo,monospace;
    --sans:"Helvetica Neue",Helvetica,Arial,sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--case)}
  .recoil{background:var(--case);color:var(--dial);font-family:var(--sans);line-height:1.5;
    background-image:radial-gradient(1200px 640px at 50% -8%, rgba(201,162,39,.06), transparent 62%);
    min-height:100%;padding:0 0 90px}
  .recoil ::selection{background:rgba(201,162,39,.28);color:#fff}
  .wrap{max-width:820px;margin:0 auto;padding:0 26px}
  .recoil h1,.recoil h2,.recoil h3{text-wrap:balance;font-weight:700;letter-spacing:-.015em}
  .recoil p{text-wrap:pretty}
  .cover{padding:56px 0 8px;position:relative}
  .glyph{position:absolute;top:44px;right:2px;font-size:76px;color:var(--gold);opacity:.09;line-height:1;user-select:none}
  .badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
  .badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);
    border:1px solid rgba(201,162,39,.4);border-radius:100px;padding:5px 11px}
  .cover h1{font-size:clamp(28px,3.2vw + 14px,42px);line-height:1.08;max-width:22ch}
  .cover .sub{margin-top:14px;font-size:16.5px;color:var(--dial);opacity:.9;max-width:70ch;line-height:1.55}
  .cover .meta{margin-top:16px;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;color:var(--graphite);line-height:1.9}
  .lbq{margin:30px 0 8px;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:12px;
    background:linear-gradient(180deg,rgba(201,162,39,.06),transparent 70%);padding:26px 28px 22px;position:relative;overflow:hidden}
  .lbq::after{content:"";position:absolute;right:-30px;top:-30px;width:90px;height:90px;pointer-events:none;
    background:linear-gradient(140deg,transparent 44%,var(--gold) 47%,var(--gold-lift) 50%,var(--gold) 53%,transparent 56%);opacity:.14}
  .lbq .lk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--gold);margin-bottom:12px}
  .lbq blockquote{font-size:clamp(18px,1.4vw + 12px,23px);line-height:1.45;font-weight:600;letter-spacing:-.01em;color:#F1EEE6}
  .lbq .attr{margin-top:14px;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--graphite)}
  .sec{margin-top:46px}
  .eyebrow{font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--graphite);
    display:flex;align-items:center;gap:12px;margin-bottom:20px}
  .eyebrow::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
  .eyebrow b{color:var(--gold);font-weight:700}
  .lede{font-size:15.5px;color:#cdcbc3;line-height:1.62;max-width:72ch;margin-bottom:20px}
  /* dossier */
  .dossier{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:22px 24px}
  .dh{font-size:19px;color:#F1EEE6;margin-bottom:10px;max-width:40ch}
  .darc{font-size:14px;color:#c4c2ba;line-height:1.6;margin-bottom:14px}
  .dfacts{list-style:none;display:grid;gap:9px}
  .dfacts li{position:relative;padding-left:18px;font-size:13.5px;color:#c0beb6;line-height:1.55}
  .dfacts li::before{content:"\\25B8";position:absolute;left:0;top:0;color:var(--gold);font-size:11px}
  /* manifold */
  .manifold{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:16px 14px 8px}
  .mcap{margin-top:12px;font-size:13px;color:var(--graphite);line-height:1.6;max-width:74ch}
  /* call walk */
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
  /* rhetorical registers */
  .regs{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
  .reg{border:1px solid var(--line);border-radius:11px;background:var(--panel);padding:16px 18px}
  .regh{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:9px}
  .regn{font-size:15px;font-weight:700;color:#F1EEE6}
  .regalt{font-family:var(--mono);font-size:9px;letter-spacing:.16em;color:var(--gold);border:1px solid rgba(201,162,39,.4);border-radius:100px;padding:2px 8px}
  .regcues{font-size:12.5px;color:var(--graphite);line-height:1.55;margin-bottom:10px}
  .regq{font-size:13.5px;color:#c8c6be;font-style:italic;line-height:1.5;border-top:1px solid var(--line);padding-top:9px}
  .regsrc{display:block;font-style:normal;font-family:var(--mono);font-size:9px;letter-spacing:.08em;color:var(--faint);margin-top:6px}
  .vocab{display:flex;flex-wrap:wrap;gap:7px}
  .vchip{font-family:var(--mono);font-size:10px;letter-spacing:.04em;color:#c0beb6;background:#101012;border:1px solid var(--line);border-radius:6px;padding:4px 9px}
  /* altitude ladder */
  .ladder{display:grid;gap:0;border:1px solid var(--line);border-radius:12px;overflow:hidden}
  .rung{display:grid;grid-template-columns:200px 1fr;gap:14px;padding:15px 18px;border-top:1px solid var(--line);background:var(--panel)}
  .rung:first-child{border-top:0}
  .rung:nth-child(1){background:linear-gradient(90deg,rgba(92,138,78,.08),transparent 60%)}
  .rung:nth-child(4){background:linear-gradient(90deg,rgba(227,79,28,.08),transparent 60%)}
  .rlvl{font-family:var(--mono);font-size:11px;letter-spacing:.04em;color:var(--dial);font-weight:700;padding-top:2px}
  .rdo{font-size:13.5px;color:#c4c2ba;line-height:1.55;margin-bottom:5px}
  .rtrig{font-size:12.5px;color:var(--graphite);line-height:1.5}
  .rtrig b{color:var(--dial)}
  .mismatch{margin-top:14px;border:1px solid rgba(227,79,28,.35);border-left:3px solid var(--verm);border-radius:11px;background:linear-gradient(180deg,rgba(227,79,28,.06),transparent);padding:16px 18px}
  .mmk{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--verm);font-weight:700;display:block;margin-bottom:8px}
  .mismatch p{font-size:14px;color:#d6cfc7;line-height:1.55}
  /* resonance map */
  .rmap{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .rcol{border:1px solid var(--line);border-radius:12px;padding:16px 18px 18px;background:var(--panel)}
  .rcol.lands{border-top:2px solid var(--ok)}
  .rcol.loses{border-top:2px solid var(--verm)}
  .rmk{font-family:var(--mono);font-size:10px;letter-spacing:.14em;font-weight:700;margin-bottom:11px}
  .rcol.lands .rmk{color:var(--ok)}
  .rcol.loses .rmk{color:var(--verm)}
  .rcol ul{list-style:none;display:grid;gap:9px}
  .rcol li{font-size:13px;color:#c0beb6;line-height:1.5;padding-left:15px;position:relative}
  .rcol.lands li::before{content:"+";position:absolute;left:0;color:var(--ok);font-weight:700}
  .rcol.loses li::before{content:"\\2212";position:absolute;left:0;color:var(--verm);font-weight:700}
  /* operators */
  .ops{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .op{border:1px solid var(--line);border-radius:11px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:14px 16px}
  .oph{display:flex;align-items:center;gap:9px;margin-bottom:7px}
  .opg{font-size:15px;color:var(--gold)}
  .opn{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;font-weight:700;color:#F1EEE6}
  .op p{font-size:12.5px;color:#bdbbb3;line-height:1.55}
  /* signal threads */
  .sig{border:1px solid var(--line);border-left:3px solid var(--ac);border-radius:11px;background:linear-gradient(180deg,var(--panel),#0e0e10);
    padding:17px 19px;margin-bottom:12px}
  .sig .sk{font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--ac);margin-bottom:7px}
  .sig h3{font-size:16px;margin-bottom:7px}
  .sig p{font-size:13.5px;color:#c0beb6;line-height:1.6}
  .sig .note{margin-top:9px;font-size:12.5px;color:var(--graphite);border-top:1px solid var(--line);padding-top:9px}
  .sig .note b{color:var(--dial)}
  /* scenarios */
  .scens{display:grid;grid-template-columns:1fr;gap:11px}
  .scen{border:1px solid var(--line);border-radius:11px;padding:16px 18px;background:var(--panel)}
  .scen.base{border-color:rgba(201,162,39,.45)}
  .scen .sck{font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:7px;color:var(--graphite)}
  .scen.best .sck{color:var(--ok)} .scen.base .sck{color:var(--gold)} .scen.worst .sck{color:var(--verm)}
  .scen h3{font-size:15.5px;margin-bottom:6px}
  .scen p{font-size:13.5px;color:#c0beb6;line-height:1.58}
  .scen .note{margin-top:8px;font-size:12.5px;color:var(--graphite)}
  /* risk */
  .risk{border:1px solid var(--line);border-left:3px solid var(--sv);border-radius:10px;padding:13px 16px;margin-bottom:10px;background:#101012}
  .risk .rk{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;color:var(--sv);margin-bottom:5px;font-weight:700}
  .risk p{font-size:13px;color:#c0beb6;line-height:1.55}
  /* protocol */
  .pstep{display:grid;grid-template-columns:120px 1fr;gap:14px;padding:14px 0;border-top:1px solid var(--line)}
  .pstep:first-of-type{border-top:0}
  .pn{font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--graphite);padding-top:3px}
  .pstep.active .pn{color:var(--gold);font-weight:700}
  .pbody h3{font-size:15px;margin-bottom:4px}
  .pbody p{font-size:13.5px;color:#c0beb6;line-height:1.58}
  /* deck seed */
  .deckseed{border:1px solid rgba(201,162,39,.3);border-radius:14px;background:linear-gradient(180deg,rgba(201,162,39,.05),transparent 60%);padding:24px 24px 26px;margin-top:52px}
  .thesis{border-left:3px solid var(--gold);padding:4px 0 4px 16px;margin-bottom:20px}
  .thk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;color:var(--gold);font-weight:700;display:block;margin-bottom:8px}
  .thesis p{font-size:15px;color:#e4ded4;line-height:1.6;max-width:74ch}
  .slides{display:grid;gap:10px}
  .slide{display:grid;grid-template-columns:46px 1fr;gap:14px;align-items:start;border:1px solid var(--line);border-radius:11px;background:#101012;padding:14px 16px}
  .sn{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--gold);opacity:.55;line-height:1}
  .sbd h3{font-size:15px;margin-bottom:4px;color:#F1EEE6}
  .sbd p{font-size:13px;color:#bdbbb3;line-height:1.55}
  /* interference / wave mechanics */
  .legend{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:22px}
  .lgi{display:flex;align-items:center;gap:7px;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--graphite)}
  .lgd{width:9px;height:9px;border-radius:50%;background:var(--c);flex:none}
  .ical{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,var(--panel),#0e0e10);padding:16px 18px 18px;margin-bottom:14px}
  .icalh{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:6px}
  .icaln{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--dial);font-weight:700}
  .icalv{font-family:var(--mono);font-size:9.5px;letter-spacing:.04em;color:var(--gold)}
  .ispark{padding:2px 0 8px;border-bottom:1px solid var(--line);margin-bottom:14px}
  .beats{display:grid;gap:10px}
  .beat{border-left:3px solid var(--pc);background:#101012;border-radius:9px;padding:12px 15px}
  .bph{font-family:var(--mono);font-size:8.5px;letter-spacing:.16em;font-weight:700;color:var(--pc);margin-bottom:9px}
  .bqp{display:grid;grid-template-columns:44px 1fr;gap:10px;margin-bottom:6px;align-items:baseline}
  .bql{font-family:var(--mono);font-size:8px;letter-spacing:.1em;color:var(--faint);padding-top:2px}
  .bqp p{font-size:13px;color:#d2d0c8;line-height:1.5;font-style:italic}
  .bread{margin-top:8px;padding-top:8px;border-top:1px solid var(--line);font-size:12.5px;color:var(--graphite);line-height:1.55}
  .midcurve{margin-top:16px;border:1px solid rgba(227,79,28,.32);border-left:3px solid var(--verm);border-radius:11px;background:linear-gradient(180deg,rgba(227,79,28,.05),transparent);padding:16px 18px}
  .mck{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--verm);font-weight:700;display:block;margin-bottom:8px}
  .midcurve p{font-size:14px;color:#d6cfc7;line-height:1.58}
  /* wedge */
  .wedgesec{border:1px solid rgba(0,240,255,.28);border-radius:14px;background:linear-gradient(180deg,rgba(0,240,255,.045),transparent 60%);padding:24px 24px 26px}
  .wtop{margin-bottom:16px}
  .wrec{font-size:22px;font-weight:700;letter-spacing:-.02em;color:#F1EEE6;margin-bottom:12px}
  .wrec::before{content:"\\25C8 ";color:var(--cyan)}
  .wthis{font-size:15px;color:#d6d4cc;line-height:1.6;max-width:74ch;margin-bottom:10px}
  .wnot{font-size:13px;color:var(--graphite);line-height:1.55;max-width:74ch}
  .wwhy{list-style:none;display:grid;gap:9px;margin-bottom:18px}
  .wwhy li{position:relative;padding-left:18px;font-size:13.5px;color:#c0beb6;line-height:1.55}
  .wwhy li::before{content:"\\25B8";position:absolute;left:0;color:var(--cyan);font-size:11px}
  .wtaste,.wwell{border-left:3px solid var(--gold);padding:2px 0 2px 16px;margin-bottom:16px}
  .wwell{border-color:var(--cyan)}
  .wtk{font-family:var(--mono);font-size:9px;letter-spacing:.2em;font-weight:700;color:var(--gold);display:block;margin-bottom:7px}
  .wwell .wtk{color:var(--cyan)}
  .wtaste p,.wwell p{font-size:14.5px;color:#e4ded4;line-height:1.6;max-width:74ch}
  .wladder{display:grid;gap:8px;margin-bottom:16px}
  .wrung{display:grid;grid-template-columns:110px 1fr;gap:14px;align-items:baseline;border:1px solid var(--line);border-radius:10px;background:#101012;padding:12px 15px}
  .wrk{font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--cyan);font-weight:700}
  .wrung p{font-size:13px;color:#c4c2ba;line-height:1.5}
  @media (max-width:680px){
    .bqp,.wrung{grid-template-columns:1fr;gap:3px}
  }
  .foot{margin-top:52px;padding-top:18px;border-top:1px solid var(--line);text-align:center;
    font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;color:var(--faint);line-height:2}
  .foot b{color:var(--gold)}
  @media (max-width:680px){
    .regs,.rmap,.ops{grid-template-columns:1fr}
    .rung{grid-template-columns:1fr;gap:6px}
    .pstep{grid-template-columns:1fr;gap:4px}
  }
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>'''

body = f'''
<div class="recoil">
  <div class="wrap">
    <header class="cover">
      <span class="glyph" aria-hidden="true">&#32884;</span>
      <div class="badges">{badges}</div>
      <h1>{E(cov['title'])}</h1>
      <p class="sub">{E(cov['subtitle'])}</p>
      <div class="meta">{meta_html}</div>
      {lbq}
    </header>
    {dossier}
    {manifold}
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The calls, walked &nbsp;&middot;&nbsp; reverse listening + deep recall</div>{cw}</section>
    {interference}
    {rhetorical}
    {altitude}
    {resonance}
    {operators}
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The signals that carry</div>{sig}</section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> Three futures</div><div class="scens">{scen_html}</div></section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> Risk register</div>{risk}</section>
    <section class="sec"><div class="eyebrow"><b>&#9633;</b> The protocol &nbsp;&middot;&nbsp; one narrow hook, then let it breathe</div>{proto}</section>
    {wedge}
    {deckseed}
    <footer class="foot">ARCS &middot; FIELD OS &middot; SERIALIZED RECOIL + RESONANCE SEED &middot; ROBIN DANIELS<br><b>GROUND IN THE TRANSCRIPT &middot; SCORE AGAINST REALITY &middot; MEET HIM AT HIS ALTITUDE</b></footer>
  </div>
</div>'''

DOC = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robin Daniels &middot; Serialized Recoil + Resonance Seed</title>
{CSS}
</head>
<body>
{body}
</body>
</html>'''

open(out, "w").write(DOC)
print("wrote", out, len(DOC), "bytes | em-dashes:", DOC.count("—"))
