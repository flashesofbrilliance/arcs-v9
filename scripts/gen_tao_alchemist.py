#!/usr/bin/env python3
"""Generate the Alchemist reaction chamber from the Tao SSOT.

Atomic proverb cards (uniform SSOT data contract) are draggable; drop two into the
crucible and the chamber shows the reaction: the two reagents, their combined
coordinate, resonance (same aspect) vs transmutation (cross-aspect), and the charge.
HONEST STUB: the deep transmuted proverb is the Alchemist operator's work (an
offstage enricher), so it is marked pending (~), not faked. Client-side only.

Reads runtime/tao/proverbs.json, writes _ARTIFACTS/arcs-tao-alchemist.html.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSOT = os.path.join(ROOT, "runtime/tao/proverbs.json")
OUT = os.path.join(ROOT, "_ARTIFACTS/arcs-tao-alchemist.html")

ASPECTS = ["D", "R", "W", "C", "H"]
ANAME = {"D": "Decision", "R": "Risk", "W": "Window", "C": "Clarity", "H": "Horizon"}
ACOLOR = {"D": "#00F0FF", "R": "#FF4D6D", "W": "#FFD700", "C": "#00FF9D", "H": "#A78BFA", "~": "#94a3b8"}
E = lambda s: html.escape(str(s), quote=True)

d = json.load(open(SSOT))
ps = d["proverbs"]

# atomic data contract for JS: id, aspect, verb, source, text, color
data = [{"id": p["id"], "a": p.get("aspect", "~"), "v": p.get("verb", "~"),
         "s": p.get("source", ""), "t": p["text"], "c": ACOLOR.get(p.get("aspect", "~"), "#94a3b8")}
        for p in ps]

def shelf_card(p):
    a = p["a"]; col = p["c"]
    coord = f'{a}&middot;{p["v"]}' if a != "~" else "founding"
    return (f'<div class="scard" draggable="true" data-id="{E(p["id"])}" style="--ac:{col}" '
            f'title="{E(p["t"])}">'
            f'<span class="sc-coord">{coord}</span>'
            f'<span class="sc-text">{E(p["t"])}</span></div>')

shelf = "\n".join(shelf_card(p) for p in data)
achips = '<button class="chip on" data-v="">ALL</button>' + "".join(
    f'<button class="chip" data-v="{a}" style="--c:{ACOLOR[a]}">{a}</button>' for a in ASPECTS)
data_json = json.dumps({p["id"]: p for p in data}, ensure_ascii=False)

page = f'''<style>
  :root{{--bg:#020408;--panel:#0d1117;--elevated:#111827;--border:#1e293b;--text:#e2e8f0;
    --sec:#94a3b8;--dim:#64748b;--mut:#475569;--cyan:#00F0FF;--gold:#FFD700;
    --mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --sans:'Inter',system-ui,-apple-system,sans-serif;
    --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;}}
  *{{box-sizing:border-box}}
  html{{background:var(--bg)}}
  body{{background:var(--bg);color:var(--text);font-family:var(--sans);margin:0;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1120px;margin:0 auto;padding:3rem 1.25rem 5rem}}
  header{{margin-bottom:1.6rem}}
  .mark{{font-size:1.4rem;color:var(--gold)}}
  .wordmark{{font-family:var(--mono);font-size:.66rem;font-weight:700;letter-spacing:.24em;color:var(--text);margin-left:.26em}}
  .wordmark b{{color:var(--cyan)}}
  h1{{font-family:var(--serif);font-size:clamp(1.5rem,4vw,2.1rem);font-weight:500;margin:.8rem 0 .3rem;letter-spacing:-.02em}}
  .sub{{font-size:.86rem;color:var(--sec);max-width:62ch;margin:0}}

  /* crucible */
  .crucible{{display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:stretch;margin:1.8rem 0 1rem}}
  .slot{{min-height:150px;border:1.5px dashed var(--border);border-radius:10px;padding:1.1rem;
    display:flex;flex-direction:column;justify-content:center;transition:.2s;background:var(--panel)}}
  .slot.over{{border-color:var(--cyan);background:rgba(0,240,255,.05)}}
  .slot.filled{{border-style:solid;border-color:var(--ac,var(--border))}}
  .slot .ph{{font-family:var(--mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);text-align:center}}
  .slot .stext{{font-family:var(--serif);font-size:1.05rem;line-height:1.35;color:var(--text)}}
  .slot .scoord{{font-family:var(--mono);font-size:.55rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ac);margin-top:.7rem}}
  .arc{{display:flex;align-items:center;justify-content:center;font-size:1.6rem;color:var(--mut);position:relative;min-width:44px}}
  .arc.spark{{color:var(--gold);animation:zap .5s ease}}
  @keyframes zap{{0%{{transform:scale(.6);filter:drop-shadow(0 0 0 var(--gold))}}50%{{transform:scale(1.3);filter:drop-shadow(0 0 14px var(--gold))}}100%{{transform:scale(1)}}}}
  @media (prefers-reduced-motion:reduce){{.arc.spark{{animation:none}}}}

  /* reaction */
  .reaction{{border:1px solid var(--border);border-radius:10px;background:var(--elevated);padding:1.3rem 1.4rem;margin:0 0 2rem;display:none}}
  .reaction.show{{display:block}}
  .rkind{{font-family:var(--mono);font-size:.62rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}
  .rkind b{{font-weight:700}}
  .rread{{font-family:var(--serif);font-size:1.15rem;line-height:1.4;color:var(--text);margin:.7rem 0 1rem}}
  .charge{{font-family:var(--mono);font-size:.62rem;line-height:1.7;color:var(--dim);border-left:2px solid var(--border);padding-left:.8rem}}
  .charge b{{color:var(--sec)}}
  .stub{{color:var(--gold)}}
  .clear{{font-family:var(--mono);font-size:.58rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;background:none;border:1px solid var(--border);border-radius:4px;color:var(--sec);padding:.4rem .7rem;cursor:pointer;margin-top:1rem}}
  .clear:hover{{border-color:var(--cyan);color:var(--cyan)}}

  /* shelf */
  .shelf-head{{display:flex;align-items:center;gap:.7rem;margin:1rem 0 .7rem}}
  .shelf-head .lbl{{font-family:var(--mono);font-size:.6rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}}
  .chip{{font-family:var(--mono);font-size:.58rem;font-weight:700;letter-spacing:.08em;background:none;border:1px solid var(--border);border-radius:4px;color:var(--dim);padding:.3rem .5rem;cursor:pointer}}
  .chip.on{{color:var(--text);border-color:var(--c,var(--cyan))}}
  .shelf{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.6rem;max-height:440px;overflow-y:auto;
    border:1px solid var(--border);border-radius:10px;padding:.7rem;background:var(--panel)}}
  .scard{{border:1px solid var(--border);border-top:2px solid var(--ac);border-radius:6px;padding:.6rem .7rem;
    background:var(--elevated);cursor:grab;transition:.15s}}
  .scard:hover{{border-color:var(--ac)}}
  .scard.dragging{{opacity:.4}}
  .sc-coord{{display:block;font-family:var(--mono);font-size:.5rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ac);margin-bottom:.35rem}}
  .sc-text{{font-family:var(--serif);font-size:.86rem;line-height:1.3;color:var(--text)}}
  footer{{margin-top:2.5rem;font-family:var(--mono);font-size:.58rem;letter-spacing:.1em;color:var(--mut);text-transform:uppercase}}
</style>

<div class="wrap">
  <header>
    <div><span class="mark">⊕</span><span class="wordmark"><b>ARCS</b> &middot; THE ALCHEMIST</span></div>
    <h1>The Reaction Chamber</h1>
    <p class="sub">Drag two proverbs into the crucible. The chamber reads the reaction, resonance when they share an aspect, transmutation when they cross. The deep synthesis, a genuinely new proverb, is the Alchemist's own work run offstage; here it is a stub, marked, never faked.</p>
  </header>

  <div class="crucible">
    <div class="slot" id="slotA" data-slot="A"><div class="ph">drop a proverb</div></div>
    <div class="arc" id="arc">&#8942;</div>
    <div class="slot" id="slotB" data-slot="B"><div class="ph">drop a proverb</div></div>
  </div>

  <div class="reaction" id="reaction">
    <div class="rkind" id="rkind"></div>
    <p class="rread" id="rread"></p>
    <div class="charge" id="charge"></div>
    <button class="clear" id="clear">Empty the crucible</button>
  </div>

  <div class="shelf-head">
    <span class="lbl">Reagents</span>
    <div id="chips">{achips}</div>
  </div>
  <div class="shelf" id="shelf">
{shelf}
  </div>

  <footer>The Tao of ARCS &middot; The Alchemist &middot; atomic cards, one SSOT contract, drag to compose &middot; 甘</footer>
</div>

<script>
  var DB = {data_json};
  var ANAME = {{"D":"Decision","R":"Risk","W":"Window","C":"Clarity","H":"Horizon","~":"the founding"}};
  var slots = {{A:null, B:null}};

  // shelf filter
  document.querySelectorAll('#chips .chip').forEach(function(b){{
    b.addEventListener('click', function(){{
      document.querySelectorAll('#chips .chip').forEach(function(x){{x.classList.remove('on');}});
      b.classList.add('on');
      var f = b.dataset.v;
      document.querySelectorAll('.scard').forEach(function(c){{
        c.style.display = (!f || DB[c.dataset.id].a === f) ? '' : 'none';
      }});
    }});
  }});

  // drag from shelf
  document.querySelectorAll('.scard').forEach(function(c){{
    c.addEventListener('dragstart', function(e){{ e.dataTransfer.setData('text/plain', c.dataset.id); c.classList.add('dragging'); }});
    c.addEventListener('dragend', function(){{ c.classList.remove('dragging'); }});
  }});

  // drop into slots
  ['A','B'].forEach(function(k){{
    var el = document.getElementById('slot'+k);
    el.addEventListener('dragover', function(e){{ e.preventDefault(); el.classList.add('over'); }});
    el.addEventListener('dragleave', function(){{ el.classList.remove('over'); }});
    el.addEventListener('drop', function(e){{
      e.preventDefault(); el.classList.remove('over');
      var id = e.dataTransfer.getData('text/plain'); if (!DB[id]) return;
      fill(k, id);
    }});
  }});

  function fill(k, id){{
    var p = DB[id]; slots[k] = p;
    var el = document.getElementById('slot'+k);
    el.classList.add('filled'); el.style.setProperty('--ac', p.c);
    var coord = p.a !== '~' ? (p.a + ' &middot; ' + p.v) : 'founding';
    el.innerHTML = '<div class="stext">' + esc(p.t) + '</div><div class="scoord" style="--ac:'+p.c+'">' + coord + ' &middot; ' + esc(p.s) + '</div>';
    if (slots.A && slots.B) react();
  }}

  function esc(s){{ var d=document.createElement('div'); d.textContent=s; return d.innerHTML; }}

  function react(){{
    var A = slots.A, B = slots.B;
    var arc = document.getElementById('arc');
    arc.classList.remove('spark'); void arc.offsetWidth; arc.classList.add('spark');
    var same = A.a === B.a && A.a !== '~';
    var rk = document.getElementById('rkind'), rr = document.getElementById('rread'), ch = document.getElementById('charge');
    if (same){{
      rk.innerHTML = '<b style="color:'+A.c+'">RESONANCE</b> &middot; two views of ' + ANAME[A.a];
      rr.textContent = 'Two readings of ' + ANAME[A.a] + '. The alchemist distills the invariant that survives beneath both.';
    }} else {{
      var an = ANAME[A.a] || 'the founding', bn = ANAME[B.a] || 'the founding';
      rk.innerHTML = '<b style="color:'+A.c+'">'+ (A.a==='~'?'FOUNDING':A.a) +'</b> &times; <b style="color:'+B.c+'">'+ (B.a==='~'?'FOUNDING':B.a) +'</b> &middot; TRANSMUTATION';
      rr.textContent = an + ' meets ' + bn + '. A true third proverb must hold both without collapsing either.';
    }}
    ch.innerHTML = '<b>Charge prepared</b> &mdash; reagents: ['+esc(A.s)+' '+A.a+'&middot;'+A.v+'] + ['+esc(B.s)+' '+B.a+'&middot;'+B.v+']'
      + '<br><b>Transmuted proverb:</b> <span class="stub">~ pending the Alchemist (offstage enricher); this chamber does not fake the synthesis.</span>';
    document.getElementById('reaction').classList.add('show');
  }}

  document.getElementById('clear').addEventListener('click', function(){{
    slots = {{A:null,B:null}};
    ['A','B'].forEach(function(k){{
      var el = document.getElementById('slot'+k);
      el.className = 'slot'; el.style.removeProperty('--ac');
      el.innerHTML = '<div class="ph">drop a proverb</div>';
    }});
    document.getElementById('reaction').classList.remove('show');
  }});
</script>'''

open(OUT, "w").write(page)
print(f"wrote {OUT}: {len(data)} atomic cards, drag-drop reaction chamber")
