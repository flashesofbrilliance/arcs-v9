#!/usr/bin/env python3
"""Generate the 'Views of the Corpus' artifact from the Tao SSOT.

Hokusai's Thirty-Six Views: one subject (the 5x5 decision grid), many faces (one
per ADR). Each ADR renders as a small grid; a cell is lit in its aspect color where
a proverb was earned, faint where not. Density = how large that decision looms.
The sparse grids are Fuji in the distance; the honesty is the composition.

Reads runtime/tao/proverbs.json, writes _ARTIFACTS/arcs-tao-views.html (self-contained,
DESIGN.md grammar). Re-run as the SSOT compounds.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSOT = os.path.join(ROOT, "runtime/tao/proverbs.json")
OUT = os.path.join(ROOT, "_ARTIFACTS/arcs-tao-views.html")

ASPECTS = ["D", "R", "W", "C", "H"]
VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate"]
ASPECT_NAME = {"D": "Decision", "R": "Risk / Ruin", "W": "Window", "C": "Clarity", "H": "Horizon"}
ASPECT_COLOR = {"D": "#00F0FF", "R": "#FF4D6D", "W": "#FFD700", "C": "#00FF9D", "H": "#A78BFA"}
E = lambda s: html.escape(str(s), quote=True)

d = json.load(open(SSOT))
ps = d["proverbs"]

# group ADR-sourced proverbs into a 5x5 cell map per source
faces = {}
for p in ps:
    src = p.get("source", "")
    if not re.match(r"^ADR-\d+$", src):
        continue
    faces.setdefault(src, {})[(p["aspect"], p["verb"])] = p["text"]

def adr_num(src):
    return int(re.search(r"\d+", src).group())

ordered = sorted(faces.keys(), key=adr_num)
total_cells = sum(len(v) for v in faces.values())

# ---- render one face (a 5x5 grid) ----
def face_html(src):
    cells = faces[src]
    fill = len(cells)
    rows = []
    for a in ASPECTS:
        cs = []
        for v in VERBS:
            t = cells.get((a, v))
            if t:
                cs.append(f'<i class="c on" style="--ac:{ASPECT_COLOR[a]}" title="{E(a)} · {E(v)} — {E(t)}"></i>')
            else:
                cs.append('<i class="c"></i>')
        rows.append("".join(cs))
    grid = "".join(f'<div class="grow">{r}</div>' for r in rows)
    return (f'<figure class="face" data-fill="{fill}">'
            f'<div class="mini">{grid}</div>'
            f'<figcaption><b>{E(src)}</b><span>{fill}/25</span></figcaption>'
            f'</figure>')

wall = "\n".join(face_html(s) for s in ordered)

legend = "".join(
    f'<span class="leg"><i style="background:{ASPECT_COLOR[a]}"></i>{a} · {ASPECT_NAME[a]}</span>'
    for a in ASPECTS)

page = f'''<style>
  :root{{--bg:#020408;--panel:#0d1117;--border:#1e293b;--text:#e2e8f0;--sec:#94a3b8;
    --dim:#64748b;--mut:#475569;--cyan:#00F0FF;--gold:#FFD700;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --sans:'Inter',system-ui,-apple-system,sans-serif;
    --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;}}
  *{{box-sizing:border-box}}
  html{{background:var(--bg)}}
  body{{background:var(--bg);color:var(--text);font-family:var(--sans);margin:0;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1180px;margin:0 auto;padding:3.5rem 1.25rem 6rem}}
  header{{border-bottom:1px solid var(--border);padding-bottom:1.6rem;margin-bottom:2.2rem}}
  .mark{{font-size:1.5rem;color:var(--gold);display:inline-block}}
  .wordmark{{font-family:var(--mono);font-size:.68rem;font-weight:700;letter-spacing:.26em;color:var(--text);margin-left:.26em}}
  .wordmark b{{color:var(--cyan)}}
  h1{{font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.2rem);font-weight:500;margin:.9rem 0 .4rem;letter-spacing:-.02em}}
  .sub{{font-size:.9rem;color:var(--sec);max-width:64ch;margin:0}}
  .meta{{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--dim);margin-top:1rem;text-transform:uppercase}}
  .legend{{display:flex;gap:.4rem 1.2rem;flex-wrap:wrap;margin-top:1.1rem}}
  .leg{{font-family:var(--mono);font-size:.6rem;letter-spacing:.06em;color:var(--sec);display:flex;align-items:center;gap:.4rem}}
  .leg i{{width:8px;height:8px;border-radius:2px;display:inline-block}}

  .wall{{display:grid;grid-template-columns:repeat(auto-fill,minmax(158px,1fr));gap:1.2rem 1rem}}
  .face{{margin:0}}
  .mini{{display:flex;flex-direction:column;gap:3px;padding:10px;background:var(--panel);border:1px solid var(--border);border-radius:6px}}
  .grow{{display:grid;grid-template-columns:repeat(5,1fr);gap:3px}}
  .c{{aspect-ratio:1/1;border-radius:2px;background:rgba(148,163,184,.05);border:1px solid rgba(30,41,59,.7)}}
  .c.on{{background:var(--ac);border-color:var(--ac);box-shadow:0 0 7px color-mix(in srgb,var(--ac) 45%,transparent);cursor:help}}
  figcaption{{display:flex;justify-content:space-between;align-items:baseline;margin-top:.5rem;font-family:var(--mono);font-size:.6rem;letter-spacing:.08em}}
  figcaption b{{color:var(--text);font-weight:700}}
  figcaption span{{color:var(--mut)}}
  footer{{margin-top:3rem;border-top:1px solid var(--border);padding-top:1.2rem;font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--mut);text-transform:uppercase;display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}}
  @media print{{body{{background:#fff;color:#111}}.mini{{background:#fff}}}}
</style>

<div class="wrap">
  <header>
    <div><span class="mark">⊕</span><span class="wordmark"><b>ARCS</b> · THE TAO</span></div>
    <h1>Views of the Corpus</h1>
    <p class="sub">Thirty-six views of one form. Every ARCS decision is a face of the same 5&times;5 grid; a cell is lit where a proverb was earned, faint where none was. The empty cells are not absence but <b style="color:var(--text);font-weight:600">&#38291; (ma)</b>: the intentional negative space, the silence between the notes that gives the struck ones their weight. A grid that came back full would have no breath. The honesty is the composition.</p>
    <div class="meta">{len(ordered)} decisions · {total_cells} lit cells · rows D/R/W/C/H &times; cols analyze&middot;assess&middot;evaluate&middot;synthesize&middot;recapitulate · hover a lit cell for its proverb</div>
    <div class="legend">{legend}</div>
  </header>

  <div class="wall">
{wall}
  </div>

  <footer>
    <span>The Tao of ARCS · Views of the Corpus · generated from runtime/tao/proverbs.json</span>
    <span>Render through the fog to earned clarity · 甘</span>
  </footer>
</div>'''

open(OUT, "w").write(page)
print(f"wrote {OUT}: {len(ordered)} faces, {total_cells} lit cells")
