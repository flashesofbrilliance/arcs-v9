#!/usr/bin/env python3
"""Robin one-door: sequenced seed -> gravity well -> corpus. Cockpit grammar (matches
robin-codex.arcs.care). 3-call meta-manifold with coachable-moment bookmark pins.
Usage: python3 scripts/gen_robin_onedoor.py <reportId> <out.html>"""
import json, html, sys, urllib.parse
reportId = sys.argv[1] if len(sys.argv) > 1 else "2026-08-05-robin-onedoor"
out = sys.argv[2] if len(sys.argv) > 2 else "_ARTIFACTS/robin-onedoor.html"
d = json.load(open(f"runtime/recoil/generated/{reportId}.json"))
E = lambda s: html.escape(str(s))
KIND = {"kairos": "#FFD700", "peak": "#00FF9D", "park": "#FF4D6D", "rising": "#94a3b8", "base": "#64748b"}

hk, sd, wl, cp = d["hook"], d["seed"], d["well"], d["corpus"]

# --- meta-manifold with bookmark pins ---
m = wl["manifold"]; pts = m["points"]
W, H, PT, PB, PL, PR = 720, 220, 34, 46, 16, 16
n = len(pts)
xs = [PL + (W - PL - PR) * (i / (n - 1)) for i in range(n)]
ys = [PT + (H - PT - PB) * (1 - (p["v"] / 100)) for p in pts]
line = " ".join(f"{'M' if i==0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
area = f"M{xs[0]:.1f},{H-PB} " + " ".join(f"L{xs[i]:.1f},{ys[i]:.1f}" for i in range(n)) + f" L{xs[-1]:.1f},{H-PB} Z"
dots = hits = ""
for i, p in enumerate(pts):
    c = KIND.get(p["kind"], "#64748b")
    r = 6 if p["kind"] in ("kairos", "peak", "park") else 3.2
    dots += (f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="{r}" fill="{c}" stroke="#020408" stroke-width="1.5"/>')
    hits += (f'<circle class="hit" cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="16" fill="transparent" '
             f'data-tip data-c="{c}" data-t="{E(p["t"])}" data-n="{E(p.get("note",""))}"/>')
# dividers + call labels
divs = ""
bounds = [PL] + [ (xs[i-1]+xs[i])/2 for i in m["dividers"] ] + [W-PR]
for x in [ (xs[i-1]+xs[i])/2 for i in m["dividers"] ]:
    divs += f'<line x1="{x:.1f}" y1="{PT-8}" x2="{x:.1f}" y2="{H-PB}" stroke="#1e293b" stroke-width="1" stroke-dasharray="3 4"/>'
for j, lab in enumerate(m["callLabels"]):
    cx = (bounds[j] + bounds[j+1]) / 2
    divs += (f'<text x="{cx:.1f}" y="{PT-14}" text-anchor="middle" fill="#64748b" '
             f'font-family="ui-monospace,monospace" font-size="8.5" letter-spacing="0.1em">{E(lab)}</text>')
manifold_svg = f'''<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Three calls as one arc">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00F0FF" stop-opacity="0.14"/><stop offset="1" stop-color="#00F0FF" stop-opacity="0"/></linearGradient></defs>
  <line x1="{PL}" y1="{H-PB}" x2="{W-PR}" y2="{H-PB}" stroke="#1e293b" stroke-width="1"/>
  {divs}<path d="{area}" fill="url(#g)"/>
  <path d="{line}" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>{dots}{hits}
</svg>'''

# bookmarks grouped by call
groups = {}
for b in wl["bookmarks"]:
    groups.setdefault(b["call"], []).append(b)
bm_html = ""
for call, labs in [("C1", "Call 1"), ("C2", "Call 2"), ("C3", "Call 3")]:
    if call not in groups: continue
    grp = groups[call]; cards = ""
    for idx, b in enumerate(grp):
        last = idx == len(grp) - 1
        cls = "bm unlock" if last else "bm"
        bc = "#FFD700" if last else b['color']
        tag = "&#8627; THE UNLOCK" if last else E(b['tag'].replace('-', ' ').upper())
        cards += f'''
        <div class="{cls}" style="--bc:{bc}">
          <div class="bmtop"><span class="bmt">{tag}</span></div>
          <div class="bml">{E(b['label'])}</div>
          <p class="bmles">{E(b['lesson'])}</p>
        </div>'''
    bm_html += f'<div class="bmgroup"><div class="bmg">{labs}</div><div class="bmcards">{cards}</div></div>'

vy = wl.get("volley")
flags_html = ""
if vy:
    qs = vy["quadrants"]
    def _cell(q):
        sub = q['lab'].split('·', 1)[-1].strip() if '·' in q['lab'] else q['lab']
        return f'''<div class="quad" style="--qc:{q['c']}"><div class="quadl">{E(sub)}</div><p>{E(q['d'])}</p></div>'''
    rows = ""
    for who, pair, wc in [("ME", qs[0:2], "#64748b"), ("YOU", qs[2:4], "#00F0FF")]:
        cells = "".join(_cell(q) for q in pair)
        rows += f'''<div class="vrow"><div class="vrl" style="--vlc:{wc}">{who} &rarr;</div><div class="vrcells">{cells}</div></div>'''
    flags_html = f'''
    <div class="flagsblock"><div class="flagsh">{E(vy['title'])}</div><p class="flagsintro">{E(vy['intro'])}</p>
      {rows}
      <div class="shouldhave"><span class="shk">&darr; THE LEARNING &middot; WHAT I SHOULD HAVE HEARD, HAD I BEEN LISTENING</span><p>{E(vy['shouldHave'])}</p></div></div>'''

tr = d.get("trust")
tr_html = ""
if tr:
    prows = "".join(f'''
        <div class="prow"><div class="pwho">{E(pp['who'])}</div><div class="pbody"><p class="pobj">&ldquo;{E(pp['obj'])}&rdquo;</p><p class="pans">{E(pp['ans'])}</p></div></div>''' for pp in tr["personas"])
    tr_html = f'''
  <section class="mv trust"><div class="mvk">{E(tr['k'])}</div><h2>{E(tr['title'])}</h2>
    <p class="mvintro">{E(tr['intro'])}</p>
    <div class="prows">{prows}</div>
  </section>'''

comp = d.get("composition")
comp_html = ""
if comp:
    inputs = "".join(f'''
      <div class="cin" style="--ic:{i['color']}">
        <div class="cintag">{E(i['type'])}</div>
        <div class="cinh">{E(i['h'])}</div>
        <p>{E(i['b'])}</p>
        {f'<a class="cinlink" href="{E(i["href"])}" target="_blank" rel="noopener">&#8599; {E(i.get("linklabel","see it"))}</a>' if i.get('href') else ''}
      </div>''' for i in comp["inputs"])
    outp = comp["output"]
    extras = ""
    if outp.get("receipt"):
        rjson = json.dumps(outp["receipt"], indent=2)
        jhref = "data:application/json;charset=utf-8," + urllib.parse.quote(rjson)
        rv = outp["revisit"]
        gt, gd = urllib.parse.quote(rv["title"]), urllib.parse.quote(rv["description"])
        gcal = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={gt}&dates={rv['start']}/{rv['end']}&details={gd}"
        iso = lambda z: f"{z[0:4]}-{z[4:6]}-{z[6:8]}T{z[9:11]}:{z[11:13]}:{z[13:15]}Z"
        outlook = (f"https://outlook.office.com/calendar/0/deeplink/compose?subject={gt}"
                   f"&startdt={urllib.parse.quote(iso(rv['start']))}&enddt={urllib.parse.quote(iso(rv['end']))}"
                   f"&body={gd}&path=/calendar/action/compose&rru=addevent")
        ics = ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ARCS//revisit//EN\r\nBEGIN:VEVENT\r\n"
               f"UID:robin-revisit-{rv['start']}@arcs.care\r\nDTSTAMP:20260805T000000Z\r\n"
               f"DTSTART:{rv['start']}\r\nDTEND:{rv['end']}\r\nSUMMARY:{rv['title']}\r\n"
               f"DESCRIPTION:{rv['description']}\r\nEND:VEVENT\r\nEND:VCALENDAR")
        ihref = "data:text/calendar;charset=utf-8," + urllib.parse.quote(ics)
        rc = outp["receipt"]
        rows = f'<div class="rcrow"><div class="rck">The bet</div><div class="rcv">{E(rc["bet"])}</div></div>'
        for pr in rc["predictions"]:
            rows += f'<div class="rcrow"><div class="rck">{int(pr["confidence"]*100)}% odds</div><div class="rcv">{E(pr["claim"])}</div></div>'
        rows += f'<div class="rcrow"><div class="rck">Filed</div><div class="rcv">Aug 5, 2026</div></div>'
        rows += f'<div class="rcrow"><div class="rck">Score-back</div><div class="rcv">{E(rc["revisit"])}</div></div>'
        extras = f'''
      <div class="rcard">
        <div class="rctop"><span class="rcid">RECEIPT &middot; PRE-CALL BRIEF</span><span class="rcst">WRITTEN BEFORE &middot; SCORED AFTER</span></div>
        {rows}
        <div class="rcseal">WRITTEN BEFORE THE CALL &middot; SCORED AFTER &middot; IF IT CANNOT FAIL, IT ISN'T A RECEIPT</div>
      </div>
      <div class="rcptrow">
        <a class="rbtn json" download="robin-precall-receipt.json" href="{jhref}">&#8681;&nbsp; Keep the receipt (JSON)</a>
        <a class="rbtn" href="{gcal}" target="_blank" rel="noopener">Google Calendar</a>
        <a class="rbtn" href="{outlook}" target="_blank" rel="noopener">Outlook</a>
        <a class="rbtn" download="arcs-revisit.ics" href="{ihref}">.ics</a>
      </div>
      <p class="rcpthint">Set a time to revisit and score it &middot; {E(rv.get('label',''))}</p>
      <p class="rcpthint">Illustrative: this one is filled in by hand to show the shape.</p>'''
    led = comp.get("ledger")
    ledger_html = ""
    if led:
        lrows = "".join(f'''
        <div class="lrow">
          <div class="lbel">{E(r['belief'])}</div>
          <div class="lpair"><div class="lt0"><span class="ltk">T0</span> {E(r['t0'])} <span class="lpct">{r['p0']}%</span></div><div class="larrow">&rarr;</div><div class="lt1"><span class="ltk">T1</span> {E(r['t1'])} <span class="lpct up">{r['p1']}%</span></div></div>
          <p class="lmoved">{E(r['moved'])}</p>
        </div>''' for r in led["rows"])
        ledger_html = f'''
    <div class="ledger"><div class="ledgerh">{E(led['title'])}</div><p class="ledgerintro">{E(led['intro'])}</p>
      <div class="lrows">{lrows}</div>
      <p class="ledgernote">{E(led['note'])}</p></div>'''
    bd = comp.get("board")
    board_html = ""
    if bd:
        chiefs = "".join(f'''
        <div class="chief" style="--cc:{ch['c']}"><div class="chiefw">{E(ch['who'])}</div><p>{E(ch['d'])}</p></div>''' for ch in bd["chiefs"])
        board_html = f'''
    <div class="boardblock"><div class="ledgerh">{E(bd['title'])}</div><p class="ledgerintro">{E(bd['intro'])}</p>
      <div class="chiefs">{chiefs}</div>
      {f'<p class="boardopen">{E(bd["open"])}</p>' if bd.get('open') else ''}
      <div class="shouldhave"><span class="shk">HOW THE CUT IS MADE</span><p>{E(bd['cut'])}</p></div></div>'''
    comp_html = f'''
  <section class="mv comp"><div class="mvk">{E(comp['k'])}</div><h2>{E(comp['title'])}</h2>
    <p class="mvintro">{E(comp['intro'])}</p>
    <div class="cinputs">{inputs}</div>
    <div class="cmerge">&#8595;&nbsp;&nbsp;they merge into&nbsp;&nbsp;&#8595;</div>
    <div class="cout"><div class="couth">{E(outp['h'])}</div><p>{E(outp['b'])}</p>{extras}</div>
    {ledger_html}
    {board_html}
  </section>'''

hz = d.get("horizon")
hz_html = ""
if hz:
    seeds = "".join(f'''
      <div class="seed"><h3>{E(s['h'])}</h3><p>{E(s['b'])}</p></div>''' for s in hz["seeds"])
    hz_html = f'''
  <section class="mv horizon"><div class="mvk">{E(hz['k'])}</div><h2>{E(hz['title'])}</h2>
    <p class="mvintro">{E(hz['intro'])}</p>
    <div class="seeds">{seeds}</div>
  </section>'''

st = d.get("start")
st_html = ""
if st:
    needs = "".join(f'''
      <div class="need"><h3>{E(n['h'])}</h3><p>{E(n['b'])}</p></div>''' for n in st["needs"])
    st_html = f'''
  <section class="mv start"><div class="mvk">{E(st['k'])}</div><h2>{E(st['title'])}</h2>
    <p class="mvintro">{E(st['intro'])}</p>
    <div class="needs">{needs}</div>
    <p class="needclose">{E(st['close'])}</p>
  </section>'''

corpus_cards = "".join(f'''
      <div class="cc">
        <h3>{E(c['h'])}</h3><p>{E(c['b'])}</p>
        {f'<a class="cclink" href="{E(c["cta"]["href"])}" target="_blank" rel="noopener">{E(c["cta"]["label"])} &rarr;</a>' if c.get('cta') else ''}
      </div>''' for c in cp["cards"])

fc = d.get("faces")
faces_html = ""
if fc:
    items = ""
    for i in fc["items"]:
        opentag = f'<a class="face" href="{E(i["href"])}" target="_blank" rel="noopener">' if i.get('href') else '<div class="face here">'
        closetag = '</a>' if i.get('href') else '</div>'
        meta = f' &middot; <b>{E(i["cta"])}</b>' if i.get('cta') else (' &middot; you are here' if i.get('here') else '')
        items += f'''{opentag}<span class="facen">{E(i['n'])}</span><span class="faceb"><span class="facet">{E(i['t'])}{meta}</span><span class="faced">{E(i['d'])}</span></span>{closetag}'''
    faces_html = f'''<div class="facesnav"><div class="facesl">{E(fc['label'])}</div>{items}</div>'''

CSS = '''<style>
:root{--bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--border:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--dimmed:#64748b;--cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;--mono:ui-monospace,"SF Mono","Fira Code",monospace;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;padding:48px 22px 96px}
.page{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
h1,h2,h3{text-wrap:balance}p{text-wrap:pretty}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed)}
h1{font-size:28px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.18}
.sub{font-size:15px;color:var(--muted);margin-top:10px;max-width:64ch}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3}
.mv{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:26px 26px 28px;position:relative}
.mv.seed{border-color:rgba(255,215,0,.25)}
.mv.well{border-color:rgba(0,240,255,.28)}
.mv.corpus{border-color:rgba(0,255,157,.22)}
.mvk{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dimmed);margin-bottom:10px}
.mv.seed .mvk{color:var(--gold)}.mv.well .mvk{color:var(--cyan)}.mv.corpus .mvk{color:var(--green)}
.mv h2{font-size:21px;font-weight:700;letter-spacing:-.01em;margin-bottom:12px}
.mvintro{font-size:14.5px;color:var(--muted);line-height:1.6;margin-bottom:18px;max-width:68ch}
.lbq{border-left:3px solid var(--gold);padding:6px 0 6px 16px;margin:4px 0 16px}
.lbq blockquote{font-size:19px;font-weight:600;line-height:1.4;color:#fff}
.lbq .attr{font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dimmed);margin-top:10px;line-height:1.6}
.cta{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(255,215,0,.4);border-radius:8px;padding:11px 18px;text-decoration:none;transition:background .15s}
.cta:hover{background:rgba(255,215,0,.08)}
.manifold{border:1px solid var(--border);border-radius:12px;background:var(--surface2);padding:14px 14px 8px;margin-bottom:14px}
.mcap{font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:20px;max-width:68ch}
.bmgroup{margin-bottom:14px}
.bmg{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);margin-bottom:9px}
.bmcards{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.bm{border:1px solid var(--border);border-left:3px solid var(--bc);border-radius:10px;background:var(--surface2);padding:13px 15px}
.bm.unlock{grid-column:1 / -1;background:linear-gradient(180deg,rgba(255,215,0,.07),transparent 70%)}
.bm.unlock .bml{color:#fff}
.bmtop{margin-bottom:6px}
.bmt{font-family:var(--mono);font-size:8px;font-weight:700;letter-spacing:.12em;color:var(--bc)}
.bml{font-size:14px;font-weight:700;color:#fff;margin-bottom:5px}
.bmles{font-size:12.5px;color:var(--muted);line-height:1.5}
.cc{border-top:1px solid var(--border);padding:16px 0}
.cc:first-of-type{border-top:0;padding-top:2px}
.cc h3{font-size:16px;margin-bottom:6px}
.cc p{font-size:14px;color:var(--muted);line-height:1.6;max-width:68ch}
.cclink{display:inline-block;margin-top:9px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);text-decoration:none}
.cclink:hover{text-decoration:underline}
.horizon{border-color:rgba(255,215,0,.22)}
.horizon .mvk{color:var(--gold)}
.start{border-color:rgba(0,255,157,.3)}
.start .mvk{color:var(--green)}
.seeds{display:grid;gap:11px}
.seed{border-left:3px solid var(--gold);background:var(--surface2);border:1px solid var(--border);border-left-width:3px;border-radius:10px;padding:15px 17px}
.seed h3{font-size:15px;margin-bottom:6px;color:#fff}
.seed p{font-size:13px;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
.comp{border-color:rgba(148,163,184,.25)}
.comp .mvk{color:var(--muted)}
.rcpt{margin-top:14px;border-top:1px solid var(--border);padding-top:14px}
.rcpth{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);margin-bottom:8px}
.rcptrow{display:flex;flex-wrap:wrap;gap:8px}
.rbtn{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;color:var(--muted);text-decoration:none;border:1px solid var(--border);border-radius:8px;padding:10px 13px;background:var(--surface2);transition:color .15s,border-color .15s}
.rbtn:hover{color:var(--text);border-color:var(--cyan)}
.rbtn.json{color:var(--cyan);border-color:rgba(0,240,255,.35)}
.needs{display:grid;gap:10px;margin-bottom:14px}
.need{display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:baseline;border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:14px 16px}
.need h3{font-size:14px;color:#fff;white-space:nowrap}
.need p{font-size:13px;color:var(--muted);line-height:1.5}
.needclose{font-size:14px;color:var(--text);line-height:1.6}
.flagsblock{margin-top:16px;border:1px solid var(--border);border-radius:12px;background:var(--surface2);padding:18px 20px}
.flagsh{font-size:16px;font-weight:700;color:#fff;margin-bottom:8px}
.flagsintro{font-size:13.5px;color:var(--muted);line-height:1.6;margin-bottom:16px}
.flags{display:grid;gap:9px}
.flag{border-left:3px solid var(--fc);background:var(--surface);border:1px solid var(--border);border-left-width:3px;border-radius:9px;padding:12px 15px}
.flagk{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--fc);margin-bottom:6px}
.flag p{font-size:13px;color:var(--muted);line-height:1.55}
.quads{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.vrow{display:grid;grid-template-columns:46px 1fr;gap:12px;align-items:start;margin-bottom:10px}
.vrl{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.08em;color:var(--vlc);padding-top:15px;text-align:right}
.vrcells{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:560px){.vrow{grid-template-columns:1fr;gap:6px}.vrl{text-align:left;padding-top:0}.vrcells{grid-template-columns:1fr}}
.quad{border:1px solid var(--border);border-top:2px solid var(--qc);border-radius:10px;background:var(--surface);padding:14px 15px}
.quad:last-child{background:linear-gradient(180deg,rgba(255,215,0,.06),transparent)}
.quadl{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--qc);margin-bottom:7px}
.quad p{font-size:12.5px;color:var(--muted);line-height:1.5}
.shouldhave{border:1px solid rgba(255,215,0,.32);border-radius:11px;background:linear-gradient(180deg,rgba(255,215,0,.06),transparent);padding:15px 17px}
.shk{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.14em;color:var(--gold);display:block;margin-bottom:8px}
.shouldhave p{font-size:14px;color:#e4ded4;line-height:1.6}
.ledger,.boardblock{margin-top:14px;border:1px solid var(--border);border-radius:12px;background:var(--surface2);padding:18px 20px}
.ledgerh{font-size:16px;font-weight:700;color:#fff;margin-bottom:8px}
.ledgerintro{font-size:13.5px;color:var(--muted);line-height:1.6;margin-bottom:16px}
.lrows{display:grid;gap:10px}
.lrow{border:1px solid var(--border);border-radius:10px;background:var(--surface);padding:13px 15px}
.lbel{font-size:13.5px;font-weight:700;color:#fff;margin-bottom:8px}
.lpair{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center;margin-bottom:8px}
.lt0,.lt1{font-size:12.5px;color:var(--muted);line-height:1.4}
.ltk{font-family:var(--mono);font-size:8px;font-weight:700;letter-spacing:.1em;color:var(--dimmed);border:1px solid var(--border);border-radius:4px;padding:1px 4px;margin-right:4px}
.lpct{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--dimmed)}
.lpct.up{color:var(--green)}
.larrow{color:var(--cyan);font-size:16px;text-align:center}
.lmoved{font-size:12px;color:var(--dimmed);line-height:1.5;border-top:1px solid var(--border);padding-top:7px}
.ledgernote{font-size:13px;color:var(--muted);line-height:1.6;margin-top:14px;font-style:italic}
.boardopen{font-size:13px;color:var(--muted);line-height:1.6;font-style:italic;margin-bottom:14px}
.chiefs{display:grid;gap:9px;margin-bottom:14px}
.chief{border-left:3px solid var(--cc);background:var(--surface);border:1px solid var(--border);border-left-width:3px;border-radius:9px;padding:12px 15px}
.chiefw{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;color:var(--cc);margin-bottom:6px}
.chief p{font-size:12.5px;color:var(--muted);line-height:1.55}
@media(max-width:560px){.quads{grid-template-columns:1fr}.lpair{grid-template-columns:1fr;gap:4px}.larrow{transform:rotate(90deg)}}
.rcard{border:1px solid var(--border);border-radius:11px;background:#0b0f16;overflow:hidden;margin-top:6px}
.rctop{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:11px 15px;border-bottom:1px solid var(--border);background:rgba(0,240,255,.04)}
.rcid{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.14em;color:var(--cyan)}
.rcst{font-family:var(--mono);font-size:8px;letter-spacing:.1em;color:var(--dimmed)}
.rcrow{display:grid;grid-template-columns:110px 1fr;gap:12px;padding:11px 15px;border-bottom:1px solid rgba(30,41,59,.5)}
.rck{font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--dimmed);padding-top:2px}
.rcv{font-size:13px;color:var(--text);line-height:1.45}
.rcseal{padding:9px 15px;font-family:var(--mono);font-size:8px;letter-spacing:.08em;color:var(--dimmed);text-align:center;background:rgba(0,240,255,.03)}
.rcpthint{font-family:var(--mono);font-size:9px;letter-spacing:.06em;color:var(--dimmed);margin-top:8px}
.trust{border-color:rgba(148,163,184,.25)}
.trust .mvk{color:var(--muted)}
.prows{display:grid;gap:9px}
.prow{display:grid;grid-template-columns:130px 1fr;gap:14px;border:1px solid var(--border);border-radius:10px;background:var(--surface2);padding:14px 16px}
.pwho{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan);padding-top:2px}
.pobj{font-size:13.5px;font-style:italic;color:var(--text);margin-bottom:6px}
.pans{font-size:13px;color:var(--muted);line-height:1.55}
@media(max-width:560px){.rcrow{grid-template-columns:1fr;gap:3px}.prow{grid-template-columns:1fr;gap:5px}}
@media(max-width:560px){.need{grid-template-columns:1fr;gap:4px}}
.cinputs{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:6px}
.cin{border:1px solid var(--border);border-top:2px solid var(--ic);border-radius:10px;background:var(--surface2);padding:14px 15px}
.cintag{font-family:var(--mono);font-size:8.5px;font-weight:700;letter-spacing:.12em;color:var(--ic);margin-bottom:7px}
.cinh{font-size:14px;font-weight:700;color:#fff;margin-bottom:6px}
.cin p{font-size:12px;color:var(--muted);line-height:1.5;overflow-wrap:anywhere}
.cinlink{display:inline-block;margin-top:9px;font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.06em;color:var(--cyan);text-decoration:none}
.cinlink:hover{text-decoration:underline}
.cmerge{text-align:center;font-family:var(--mono);font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);margin:14px 0}
.cout{border:1px solid rgba(0,240,255,.3);border-radius:11px;background:linear-gradient(180deg,rgba(0,240,255,.06),transparent);padding:16px 18px}
.couth{font-size:15px;font-weight:700;color:#fff;margin-bottom:7px}
.cout p{font-size:13px;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
@media(max-width:560px){.cinputs{grid-template-columns:1fr}}
.facesnav{border:1px solid rgba(0,240,255,.22);border-radius:12px;background:var(--surface2);padding:14px 16px;display:grid;gap:2px}
.facesl{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);margin-bottom:6px}
.face{display:grid;grid-template-columns:26px 1fr;gap:10px;align-items:baseline;padding:9px 8px;border-radius:8px;text-decoration:none;color:var(--text)}
a.face:hover{background:var(--surface)}.face.here{opacity:.65}
.facen{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--cyan)}
.faceb{display:flex;flex-direction:column;gap:2px}
.facet{font-size:14.5px;font-weight:700;color:#fff}.facet b{color:var(--gold);font-family:var(--mono);font-size:10px;letter-spacing:.06em;font-weight:700}
.faced{font-size:12px;color:var(--muted)}
.foot{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--dimmed);text-align:center;padding-top:8px;line-height:2}
@media(max-width:560px){.bmcards{grid-template-columns:1fr}}
.hit{cursor:pointer}
#tip{position:fixed;z-index:80;max-width:min(280px,88vw);pointer-events:none;opacity:0;transition:opacity .12s;background:#0b0f16;border:1px solid var(--tc,#1e293b);border-radius:10px;padding:11px 13px;box-shadow:0 8px 30px rgba(0,0,0,.55)}
#tip.on{opacity:1}
#tip .tt{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--tc,#94a3b8);margin-bottom:6px}
#tip .tn{font-size:13px;color:var(--text);line-height:1.45}
@media(hover:none){.hit{cursor:default}}
#pw-gate{position:fixed;inset:0;background:#020408;display:flex;align-items:center;justify-content:center;z-index:100;flex-direction:column;gap:16px}#pw-gate.hidden{display:none}
.pw-label{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#475569}
.pw-input{background:#0d1117;border:1px solid #1e293b;border-radius:8px;color:#e2e8f0;font-size:16px;padding:10px 16px;outline:none;width:200px;text-align:center;letter-spacing:.1em}
.pw-input:focus{border-color:#00F0FF}.pw-input.shake{animation:shk .3s ease;border-color:#FF4D6D}
@keyframes shk{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
</style>'''

body = f'''<div class="page">
  <div><div class="eyebrow">{E(hk['eyebrow'])}</div><h1>{E(hk['title'])}</h1><p class="sub">{E(hk['sub'])}</p></div>
  <div class="rule"></div>
  {faces_html}
  <section class="mv seed"><div class="mvk">{E(sd['k'])}</div><h2>{E(sd['title'])}</h2>
    <div class="lbq"><blockquote>&ldquo;{E(sd['quote'])}&rdquo;</blockquote><div class="attr">{E(sd['attribution'])}</div></div>
    <a class="cta" href="{E(sd['cta']['href'])}" target="_blank" rel="noopener">{E(sd['cta']['label'])} &rarr;</a>
  </section>
  <section class="mv well"><div class="mvk">{E(wl['k'])}</div><h2>{E(wl['title'])}</h2>
    <p class="mvintro">{E(wl['intro'])}</p>
    <div class="manifold">{manifold_svg}</div>
    <p class="mcap">{E(m['caption'])}</p>
    {bm_html}
    {flags_html}
  </section>
  {comp_html}
  <section class="mv corpus"><div class="mvk">{E(cp['k'])}</div><h2>{E(cp['title'])}</h2>{corpus_cards}</section>
  {hz_html}
  {st_html}
  {tr_html}
  <div class="foot">ARCS &middot; ONE DOOR &middot; MOVE AT YOUR OWN PACE &middot; NOTHING HERE ASKS YOU FOR ANYTHING</div>
</div>'''

GATE = '''<div id="pw-gate"><div class="pw-label">ARCS &middot; Private &middot; for Robin</div><input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>'''
ANALYTICS_HEAD = '''<script defer src="/_vercel/insights/script.js"></script>'''
AJS = '''<script>document.querySelectorAll('.cta,.cclink,.rbtn,.cinlink').forEach(function(a){a.addEventListener('click',function(){try{if(window.va)va('event',{name:'studio_click',data:{label:(a.textContent||'').trim().slice(0,40)}});}catch(e){}});});</script>'''
TIP = '''<div id="tip"></div>'''
TIPJS = '''<script>(function(){var tip=document.getElementById('tip');if(!tip)return;
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function show(el,e){var c=el.getAttribute('data-c')||'#94a3b8';tip.style.setProperty('--tc',c);
tip.innerHTML='<div class="tt">'+esc(el.getAttribute('data-t'))+'</div><div class="tn">'+esc(el.getAttribute('data-n'))+'</div>';
tip.classList.add('on');move(e);}
function move(e){var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+16,y=e.clientY+16;if(x+w>window.innerWidth-8)x=e.clientX-w-16;if(y+h>window.innerHeight-8)y=e.clientY-h-16;tip.style.left=x+'px';tip.style.top=y+'px';}
function hide(){tip.classList.remove('on');}
document.querySelectorAll('[data-tip]').forEach(function(el){
el.addEventListener('mouseenter',function(e){show(el,e);});el.addEventListener('mousemove',move);el.addEventListener('mouseleave',hide);
el.addEventListener('click',function(e){e.stopPropagation();var r=el.getBoundingClientRect();show(el,{clientX:r.left+r.width/2,clientY:r.top+r.height/2});});});
document.addEventListener('click',hide);})();</script>'''
GATEJS = '''<script>(function(){var K='robin-onedoor-auth',P='robin';if(sessionStorage.getItem(K)==='1'){document.getElementById('pw-gate').classList.add('hidden');return;}var i=document.getElementById('pw-input');i.addEventListener('keydown',function(e){if(e.key!=='Enter')return;if(i.value.toLowerCase()===P){sessionStorage.setItem(K,'1');document.getElementById('pw-gate').classList.add('hidden');try{if(window.va)va('event',{name:'unlock',data:{page:'robin'}});}catch(e){}}else{i.classList.add('shake');i.value='';setTimeout(function(){i.classList.remove('shake');},350);}});})();</script>'''
DOC = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow"><title>Robin &middot; one door</title>{CSS}{ANALYTICS_HEAD}</head><body>{GATE}{body}{TIP}{TIPJS}{AJS}{GATEJS}</body></html>'''
open(out, "w").write(DOC)
print("wrote", out, len(DOC), "bytes | em-dashes:", DOC.count("—"))
