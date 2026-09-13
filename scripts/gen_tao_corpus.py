#!/usr/bin/env python3
"""Generate the browsable Tao corpus artifact from the SSOT.

The Views sheet (gen_tao_views.py) is the map; this is the territory: all proverbs,
filterable by aspect / verb / source / text, readable one at a time. Accent on top
(per house preference). Reads runtime/tao/proverbs.json, writes
_ARTIFACTS/arcs-tao-corpus.html. Re-run as the SSOT compounds.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSOT = os.path.join(ROOT, "runtime/tao/proverbs.json")
OUT = os.path.join(ROOT, "_ARTIFACTS/arcs-tao-corpus.html")

ASPECTS = ["D", "R", "W", "C", "H"]
VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate"]
ASPECT_NAME = {"D": "Decision", "R": "Risk / Ruin", "W": "Window", "C": "Clarity", "H": "Horizon"}
ACOLOR = {"D": "#00F0FF", "R": "#FF4D6D", "W": "#FFD700", "C": "#00FF9D", "H": "#A78BFA", "~": "#64748b"}
E = lambda s: html.escape(str(s), quote=True)

d = json.load(open(SSOT))
ps = d["proverbs"]

def sort_key(p):
    a = p.get("aspect", "~")
    ai = ASPECTS.index(a) if a in ASPECTS else 99
    vi = VERBS.index(p["verb"]) if p.get("verb") in VERBS else 99
    return (ai, vi, p.get("source", ""))

cards = []
for p in sorted(ps, key=sort_key):
    a = p.get("aspect", "~"); v = p.get("verb", "~"); src = p.get("source", "")
    col = ACOLOR.get(a, "#64748b")
    meta = " &middot; ".join(x for x in [
        (f'<b style="color:{col}">{E(a)}</b>' if a != "~" else '<b style="color:#64748b">founding</b>'),
        (E(v) if v != "~" else ""), E(src)] if x)
    cards.append(
        f'<article class="pcard" data-aspect="{E(a)}" data-verb="{E(v)}" data-source="{E(src)}" '
        f'data-text="{E(p["text"].lower())}" style="--ac:{col}">'
        f'<p class="ptext">{E(p["text"])}</p>'
        f'<div class="pmeta">{meta}</div></article>')

achips = '<button class="chip on" data-f="aspect" data-v="">ALL</button>' + "".join(
    f'<button class="chip" data-f="aspect" data-v="{a}" style="--c:{ACOLOR[a]}">{a} &middot; {ASPECT_NAME[a].split(" ")[0]}</button>'
    for a in ASPECTS)
vchips = '<button class="chip on" data-f="verb" data-v="">ALL</button>' + "".join(
    f'<button class="chip" data-f="verb" data-v="{v}">{v}</button>' for v in VERBS)

srcs = sorted({p.get("source", "") for p in ps if re.match(r"^ADR-\d+$", p.get("source", ""))},
              key=lambda s: int(re.search(r"\d+", s).group()))
sopts = '<option value="">all sources</option>' + "".join(f'<option value="{s}">{s}</option>' for s in srcs)

page = f'''<style>
  :root{{--bg:#020408;--panel:#0d1117;--elevated:#111827;--border:#1e293b;--text:#e2e8f0;
    --sec:#94a3b8;--dim:#64748b;--mut:#475569;--cyan:#00F0FF;--gold:#FFD700;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --sans:'Inter',system-ui,-apple-system,sans-serif;
    --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;}}
  *{{box-sizing:border-box}}
  html{{background:var(--bg);scroll-behavior:smooth}}
  body{{background:var(--bg);color:var(--text);font-family:var(--sans);margin:0;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1180px;margin:0 auto;padding:0 1.25rem 6rem}}

  .deck{{position:sticky;top:0;z-index:40;background:rgba(2,4,8,.94);backdrop-filter:blur(10px);
    border-bottom:1px solid var(--border);margin:0 -1.25rem 2rem;padding:.75rem 1.25rem}}
  .deck-in{{max-width:1180px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:.5rem .8rem}}
  .wordmark{{font-family:var(--mono);font-size:.66rem;font-weight:700;letter-spacing:.24em;color:var(--text)}}
  .wordmark b{{color:var(--cyan)}}
  .chip{{font-family:var(--mono);font-size:.58rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
    background:none;border:1px solid var(--border);border-radius:4px;color:var(--dim);padding:.34rem .55rem;cursor:pointer;transition:.15s}}
  .chip:hover{{color:var(--sec);border-color:var(--sec)}}
  .chip.on{{color:var(--text);border-color:var(--c,var(--cyan));background:color-mix(in srgb,var(--c,var(--cyan)) 12%,transparent)}}
  .chip:focus-visible{{outline:1px solid var(--cyan);outline-offset:-1px}}
  .grp{{display:flex;gap:.35rem;flex-wrap:wrap}}
  .sep{{width:1px;align-self:stretch;background:var(--border);margin:0 .2rem}}
  select,input[type=search]{{font-family:var(--mono);font-size:.6rem;background:var(--elevated);border:1px solid var(--border);
    color:var(--sec);border-radius:4px;padding:.35rem .5rem}}
  input[type=search]{{min-width:150px}}
  .count{{font-family:var(--mono);font-size:.58rem;letter-spacing:.1em;color:var(--mut);margin-left:auto;text-transform:uppercase}}

  header{{padding:3.2rem 0 .4rem}}
  .mark{{font-size:1.5rem;color:var(--gold)}}
  h1{{font-family:var(--serif);font-size:clamp(1.5rem,4vw,2.1rem);font-weight:500;margin:.8rem 0 .3rem;letter-spacing:-.02em}}
  .sub{{font-size:.88rem;color:var(--sec);max-width:60ch;margin:0}}

  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem;margin-top:1.5rem}}
  .pcard{{position:relative;background:var(--panel);border:1px solid var(--border);border-radius:8px;
    padding:1.3rem 1.25rem 1rem;overflow:hidden;display:flex;flex-direction:column;min-height:130px}}
  .pcard::after{{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:var(--ac);opacity:.85}}
  .ptext{{font-family:var(--serif);font-size:1.02rem;line-height:1.36;color:var(--text);margin:0 0 auto;text-wrap:pretty}}
  .pmeta{{font-family:var(--mono);font-size:.56rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:.9rem}}
  .pmeta b{{font-weight:700}}
  .empty{{text-align:center;color:var(--dim);font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;padding:3rem;grid-column:1/-1}}
  footer{{margin-top:3rem;border-top:1px solid var(--border);padding-top:1.2rem;font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;color:var(--mut);text-transform:uppercase;display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}}
  @media print{{.deck{{position:static}}body{{background:#fff;color:#111}}.pcard{{background:#fff}}.ptext{{color:#111}}}}
</style>

<div class="deck"><div class="deck-in">
  <span class="wordmark"><b>ARCS</b> &middot; TAO</span>
  <div class="grp">{achips}</div>
  <span class="sep"></span>
  <div class="grp">{vchips}</div>
  <span class="sep"></span>
  <select id="src">{sopts}</select>
  <input type="search" id="q" placeholder="search proverbs" aria-label="search proverbs">
  <span class="count" id="count"></span>
</div></div>

<div class="wrap">
  <header>
    <div><span class="mark">⊕</span></div>
    <h1>The Tao of ARCS, entire</h1>
    <p class="sub">The whole compounding corpus, every proverb the house has minted from its decisions. Filter by aspect, verb, or source; the empty spaces between are ma. {len(ps)} proverbs and counting.</p>
  </header>

  <div class="grid" id="grid">
{chr(10).join(cards)}
    <div class="empty" id="empty" style="display:none">No proverb matches. That silence is also ma.</div>
  </div>

  <footer>
    <span>The Tao of ARCS &middot; entire &middot; generated from runtime/tao/proverbs.json</span>
    <span>Render through the fog to earned clarity &middot; 甘</span>
  </footer>
</div>

<script>
  var state = {{aspect:"", verb:"", source:"", q:""}};
  var cards = Array.prototype.slice.call(document.querySelectorAll('.pcard'));
  var countEl = document.getElementById('count'), emptyEl = document.getElementById('empty');
  function apply(){{
    var n = 0;
    cards.forEach(function(c){{
      var ok = (!state.aspect || c.dataset.aspect === state.aspect)
        && (!state.verb || c.dataset.verb === state.verb)
        && (!state.source || c.dataset.source === state.source)
        && (!state.q || c.dataset.text.indexOf(state.q) !== -1);
      c.style.display = ok ? '' : 'none';
      if (ok) n++;
    }});
    countEl.textContent = n + ' / ' + cards.length;
    emptyEl.style.display = n ? 'none' : '';
  }}
  document.querySelectorAll('.chip').forEach(function(b){{
    b.addEventListener('click', function(){{
      var f = b.dataset.f;
      document.querySelectorAll('.chip[data-f="'+f+'"]').forEach(function(x){{x.classList.remove('on');}});
      b.classList.add('on');
      state[f] = b.dataset.v;
      apply();
    }});
  }});
  document.getElementById('src').addEventListener('change', function(e){{ state.source = e.target.value; apply(); }});
  document.getElementById('q').addEventListener('input', function(e){{ state.q = e.target.value.trim().toLowerCase(); apply(); }});
  apply();
</script>'''

open(OUT, "w").write(page)
print(f"wrote {OUT}: {len(ps)} proverbs browsable")
