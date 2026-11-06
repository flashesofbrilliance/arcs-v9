<title>@@TITLE@@</title>
<!-- @arcs-template: precall-brief -->
<!-- @arcs-mode: operate -->
<!-- Built by scripts/precall_brief_build.py from this template plus a data file (schema: src/ui-kit/precall-brief/brief.schema.json). Never hand-edit a built page. -->
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap">
<style>
/* Layout: one 856px lane (reading measure 760px + padding). Cockpit is a single column; lanes hold auto-fit card grids.
   Tokens come from the ARCS kit (src/ui-kit/recoil-report/_tokens.css, inlined verbatim below). This page adds only a
   spacing scale, the reading measure, and the light palette under the kit's own names. One disclosure component (.disc)
   drives every fold: cockpit sections, cockpit items, lanes and cards. Dark-first; light via OS setting or the toggle. */
/*@@KIT_TOKENS@@*/

/* Page layer: spacing scale and measure (layout tokens, not palette) */
:root{
  --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px; --sp-6:32px;
  --measure:760px; --lane:856px; --grid-floor:340px;
  --accent:var(--cyan); --fg:var(--text); --fg-2:var(--dimmed);
  color-scheme:dark;
}
/* Light palette: same token names, darker accents for AA contrast on white */
@media (prefers-color-scheme: light){
  :root:not([data-theme="dark"]){
    --bg:#f6f8fb; --surface:#ffffff; --surface-2:#eef2f7; --elevated:#f1f5f9; --border:#cfd8e3;
    --text:#0f172a; --muted:#475569; --dimmed:#475569; --text-secondary:#334155;
    --cyan:#00727a; --green:#047857; --gold:#8a6100; --red:#be123c;
    --cyan-bg:rgba(0,114,122,.08); --green-bg:rgba(4,120,87,.08); --gold-bg:rgba(138,97,0,.08); --red-bg:rgba(190,18,60,.08);
    color-scheme:light;
  }
}
:root[data-theme="light"]{
  --bg:#f6f8fb; --surface:#ffffff; --surface-2:#eef2f7; --elevated:#f1f5f9; --border:#cfd8e3;
  --text:#0f172a; --muted:#475569; --dimmed:#475569; --text-secondary:#334155;
  --cyan:#00727a; --green:#047857; --gold:#8a6100; --red:#be123c;
  --cyan-bg:rgba(0,114,122,.08); --green-bg:rgba(4,120,87,.08); --gold-bg:rgba(138,97,0,.08); --red-bg:rgba(190,18,60,.08);
  color-scheme:light;
}

/* Wrap-safety base (from _PATTERNS/arcs-artifact-css-base.css, adapted: cards fill their grid track) */
p, li, blockquote{max-width:var(--measure);text-wrap:pretty}
.card p, .card li, .card dd, .cockpit li, .cockpit p, .sub, .pinned p, .lane-job{max-width:none}
h1, h2, h3{text-wrap:balance}
.nowrap, .chip, .stamp-time{white-space:nowrap}

*{box-sizing:border-box}
html{scroll-padding-top:96px}
body{background:var(--bg);color:var(--text);font:var(--fs-body)/1.55 var(--ds-font-sans);margin:0;
  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top, 0px);z-index:20;background:var(--bg)}
button{font:500 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;
  color:var(--cyan);background:transparent;border:1px solid var(--border);border-radius:var(--ds-r-xs);padding:var(--sp-2) var(--sp-3);min-height:32px}
button.solid{color:var(--bg);background:var(--cyan);border-color:var(--cyan)}
button:focus-visible, summary:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible{outline:2px solid var(--gold);outline-offset:2px}

/* Status bar */
.bar{position:sticky;top:env(safe-area-inset-top, 0px);z-index:10;background:var(--bg);border-bottom:1px solid var(--border);
  padding:var(--sp-3) 0;display:flex;flex-wrap:wrap;gap:var(--sp-2) var(--sp-4);align-items:center;justify-content:space-between}
.bar-left{display:flex;gap:var(--sp-3);align-items:baseline;flex-wrap:wrap;min-width:0}
.bar-right{display:flex;gap:var(--sp-2);align-items:center;flex-wrap:wrap;min-width:0}
.tminus{font:600 var(--fs-headline)/1 var(--ds-font-mono);color:var(--cyan);font-variant-numeric:tabular-nums}
.state{font:500 var(--fs-label)/1.3 var(--ds-font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed)}
@media (max-width: 640px){ .meet{display:none} .state{display:none} }
.meet code{font:400 var(--fs-label)/1.2 var(--ds-font-mono);overflow-wrap:anywhere}

/* Page frame */
.wrap{max-width:var(--lane);margin:0 auto;padding-block:var(--sp-6) 72px;display:grid;gap:var(--sp-6)}
header{display:grid;gap:var(--sp-2)}
header h1{font:600 var(--fs-display)/1.1 var(--ds-font-display);margin:0}
.eyebrow{font:500 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--cyan)}
.sub{color:var(--text-secondary);margin:0}
.legend{display:flex;flex-wrap:wrap;gap:var(--sp-2) var(--sp-3);align-items:center;font:500 var(--fs-label)/1.4 var(--ds-font-mono);color:var(--dimmed)}
.pinned{border:1px dashed var(--gold);border-radius:var(--ds-r-sm);padding:var(--sp-3) var(--sp-4);display:grid;gap:var(--sp-1);background:var(--gold-bg)}
.pinned p{margin:0}
.pin-label{font:600 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}

/* Atom: chip (evidence only) */
.chip{font:500 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.12em;padding:var(--sp-1) 6px;border-radius:var(--ds-r-xs);border:1px solid currentColor}
.stated{color:var(--green)} .judgment{color:var(--gold)} .unverified{color:var(--red)}

/* Molecule: disclosure (the one fold control) */
.disc{list-style:none;cursor:pointer;display:flex;align-items:center;gap:var(--sp-2)}
.disc::-webkit-details-marker{display:none}
.disc::before{content:"\25B8";flex:none;font-size:var(--fs-label);line-height:1;color:var(--dimmed);transition:transform var(--dur-fast) var(--ease-out)}
details[open]>.disc::before{transform:rotate(90deg)}
details[open]>.unfold{animation:unfold var(--dur-base) var(--ease-out)}
@keyframes unfold{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}

/* Organism: cockpit */
.cockpit{border:1px solid var(--cyan);border-radius:var(--ds-r-md);background:var(--surface);padding:var(--sp-4) var(--sp-5);display:grid;gap:var(--sp-3)}
.cockpit-head{display:flex;justify-content:space-between;align-items:center;gap:var(--sp-3);flex-wrap:wrap}
.cockpit-head h2{font:600 var(--fs-headline)/1.1 var(--ds-font-display);margin:0;color:var(--cyan)}
.csec{border-top:1px solid var(--border);padding-top:var(--sp-2)}
.csum{font:600 var(--fs-label)/1.3 var(--ds-font-mono);letter-spacing:.12em;text-transform:uppercase;padding-block:var(--sp-1)}
.csec.say{--tone:var(--cyan)} .csec.ask{--tone:var(--gold)} .csec.trip{--tone:var(--red)} .csec.rule{--tone:var(--green)}
.csec>.csum{color:var(--tone)}
.citems{display:grid;gap:var(--sp-1);padding:var(--sp-2) 0 var(--sp-1) var(--sp-5)}
.citem-row{display:grid;grid-template-columns:1fr auto;align-items:start;column-gap:var(--sp-2);border-left:2px solid var(--tone);padding:var(--sp-2) 0 var(--sp-2) var(--sp-3)}
.citem{min-width:0}
.citem>.disc{display:grid;grid-template-columns:auto 1fr;column-gap:var(--sp-2);align-items:baseline}
.ch{font:600 var(--fs-headline)/1.3 var(--ds-font-sans)}
.cl{grid-column:2;color:var(--text-secondary)}
.jump{display:inline-flex;align-items:center;min-height:32px;padding:0 var(--sp-2);font:500 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.06em;color:var(--cyan);text-decoration:none;white-space:nowrap;border-radius:var(--ds-r-xs)}
.jump:hover{text-decoration:underline}
.citem ul{margin:var(--sp-2) 0 0 var(--sp-5);padding-left:var(--sp-4);display:grid;gap:var(--sp-1);color:var(--text-secondary)}

/* Organism: lane */
.lanes{display:grid;gap:var(--sp-5)}
.lane-head{flex-wrap:wrap;border-bottom:1px solid var(--border);padding-bottom:var(--sp-2);column-gap:var(--sp-3)}
.lane-head h2{font:600 var(--fs-headline)/1.1 var(--ds-font-display);margin:0}
.when{font:500 var(--fs-label)/1 var(--ds-font-mono);color:var(--dimmed);letter-spacing:.06em}
.now{font:600 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.14em;color:var(--bg);background:var(--cyan);padding:var(--sp-1) 6px;border-radius:var(--ds-r-xs)}
.lane-wrap{position:relative}
.lane-all{position:absolute;top:0;right:0}
.lane-head{padding-right:104px}
.lane-job{flex-basis:100%;padding-left:var(--sp-5);color:var(--text-secondary)}
.grid{display:grid;grid-template-columns:repeat(auto-fit, minmax(min(var(--grid-floor), 100%), 1fr));gap:var(--sp-4);align-items:start;margin-top:var(--sp-4)}

/* Organism: card */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--ds-r-sm);min-width:0}
.wide{grid-column:1/-1}
.card-sum{padding:var(--sp-3) var(--sp-4)}
.card-sum h3{flex:1;min-width:0;font:600 var(--fs-label)/1.3 var(--ds-font-mono);letter-spacing:.12em;text-transform:uppercase;margin:0;display:flex;justify-content:space-between;align-items:center;gap:var(--sp-2)}
.cbody{display:grid;gap:var(--sp-3);padding:0 var(--sp-4) var(--sp-4)}
.card p{margin:0}
.card.flash{animation:flash var(--dur-sweep) var(--ease-out)}
@keyframes flash{0%{border-color:var(--cyan);box-shadow:0 0 0 2px var(--cyan)}100%{border-color:var(--border);box-shadow:none}}

/* Molecules inside cards */
.kv{display:grid;grid-template-columns:minmax(72px,auto) 1fr;gap:var(--sp-1) var(--sp-3);margin:0}
.kv dt{font:500 var(--fs-label)/1.7 var(--ds-font-mono);color:var(--dimmed);text-transform:uppercase;letter-spacing:.08em}
.kv dd{margin:0;min-width:0}
.quote{border-left:2px solid var(--cyan);padding-left:var(--sp-3)}
ul.clean{margin:0;padding-left:var(--sp-4);display:grid;gap:6px}
ol.ask{list-style:none;margin:0;padding:0;display:grid;gap:var(--sp-2);counter-reset:q 0}
ol.ask li{display:grid;grid-template-columns:auto auto 1fr;gap:var(--sp-2);align-items:start}
ol.ask li::before{counter-increment:q;content:counter(q,decimal-leading-zero);font:500 var(--fs-label)/2 var(--ds-font-mono);color:var(--cyan)}
ol.ask input{margin-top:5px;accent-color:var(--green);width:16px;height:16px}
ol.ask li.done label{text-decoration:line-through;text-decoration-color:var(--green)}
.stamp{font:500 var(--fs-label)/1.5 var(--ds-font-mono);color:var(--dimmed)}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:var(--fs-body)}
th, td{text-align:left;padding:var(--sp-2);border-bottom:1px solid var(--border);vertical-align:top}
th{font:500 var(--fs-label)/1.2 var(--ds-font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--dimmed)}
td.p{font-family:var(--ds-font-mono);font-variant-numeric:tabular-nums;color:var(--cyan);white-space:nowrap}
td.basis{color:var(--text-secondary);font-size:var(--fs-label);min-width:180px}
select{font:500 var(--fs-label)/1 var(--ds-font-mono);background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:var(--ds-r-xs);padding:6px}
.score{font:500 var(--fs-label)/1.4 var(--ds-font-mono);color:var(--dimmed)}
.score b{color:var(--gold);font-weight:500}
footer{font:400 var(--fs-label)/1.5 var(--ds-font-mono);color:var(--dimmed)}

@media (pointer: coarse){ button, .jump{min-height:44px} }
@media (prefers-reduced-motion: reduce){
  .disc::before{transition:none}
  details[open]>.unfold, .card.flash{animation:none}
}
</style>

<div class="bar" role="status">
  <div class="bar-left"><span class="tminus" id="tminus">--:--</span><span class="state" id="state"></span></div>
  <div class="bar-right"><span class="meet"><code id="meet"></code></span><button id="copy" class="solid" type="button">Copy link</button><button id="theme" type="button" aria-label="Switch color theme">Light</button></div>
</div>
<main class="wrap">
  <header>
    <div class="eyebrow" id="eyebrow"></div>
    <h1 id="title"></h1>
    <p class="sub" id="sub"></p>
    <div class="legend" aria-label="Evidence labels"><span class="chip stated">STATED</span>someone said or wrote it <span class="chip judgment">JUDGMENT</span>no data behind it <span class="chip unverified">UNVERIFIED</span>claimed, not checked</div>
  </header>
  <aside class="pinned" id="pinned" aria-label="Pinned note" hidden><span class="pin-label" id="pin-label"></span><p id="pin-text"></p></aside>
  <section class="cockpit" id="cockpit" aria-labelledby="cockpit-h"></section>
  <div id="lanes" class="lanes"></div>
  <footer id="footer"></footer>
</main>

<script type="application/json" id="brief-data">@@BRIEF_DATA@@</script>
<script>
(function(){
  document.documentElement.lang = 'en';
  // Keep anchor jumps clear of the sticky bar at every width
  const padTop = () => { const b = document.querySelector('.bar'); if (b) document.documentElement.style.scrollPaddingTop = (b.offsetHeight + 16) + 'px'; };
  addEventListener('resize', padTop); requestAnimationFrame(padTop);
  const B = JSON.parse(document.getElementById('brief-data').textContent);
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const KEY = 'precall-brief:' + B.id;
  let store = {}; try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
  store.asks = store.asks || {}; store.results = store.results || {};
  const CHIP = { stated: 'STATED', judgment: 'JUDGMENT', unverified: 'UNVERIFIED' };
  const chip = (k) => el('span', 'chip ' + k, CHIP[k] || k);
  const slug = (s) => 'c-' + s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

  $('eyebrow').textContent = B.eyebrow; $('title').textContent = B.title; $('sub').textContent = B.sub; $('footer').textContent = B.footer;
  $('meet').textContent = B.meet;
  if (B.pinned) { $('pin-label').textContent = B.pinned.label; $('pin-text').textContent = B.pinned.text; $('pinned').hidden = false; }
  // Theme: follows the system until toggled; the choice is remembered in this browser only
  const root = document.documentElement, tb = $('theme');
  const isLight = () => root.dataset.theme ? root.dataset.theme === 'light' : matchMedia('(prefers-color-scheme: light)').matches;
  const paint = () => { tb.textContent = isLight() ? 'Dark' : 'Light'; };
  try { const saved = localStorage.getItem('precall-theme'); if (saved) root.dataset.theme = saved; } catch (e) {}
  paint();
  tb.addEventListener('click', () => { root.dataset.theme = isLight() ? 'dark' : 'light'; try { localStorage.setItem('precall-theme', root.dataset.theme); } catch (e) {} paint(); });
  matchMedia('(prefers-color-scheme: light)').addEventListener('change', paint);
  $('copy').addEventListener('click', () => {
    const b = $('copy'), done = () => { b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy link', 1500); };
    const sel = () => { const r = document.createRange(); r.selectNodeContents($('meet')); const w = getSelection(); w.removeAllRanges(); w.addRange(r); };
    try { navigator.clipboard.writeText(B.meet).then(done, sel); } catch (e) { sel(); }
  });

  // Phase
  const start = Date.parse(B.start), end = Date.parse(B.end), openEnd = start + (B.openingMinutes || 5) * 60000;
  const pad = n => String(n).padStart(2, '0');
  function phase(now){ return now < start ? 'before' : now < openEnd ? 'opening' : now < end ? 'interview' : 'debrief'; }
  function tick(){
    const now = Date.now();
    if (now < start) {
      const d = Math.floor((start - now) / 1000), h = Math.floor(d / 3600), m = Math.floor(d % 3600 / 60);
      $('tminus').textContent = 'T-' + (h ? h + ':' : '') + pad(m) + ':' + pad(d % 60);
      $('state').textContent = B.when;
    } else if (now < end) {
      const d = Math.floor((now - start) / 1000);
      $('tminus').textContent = 'LIVE ' + pad(Math.floor(d / 60)) + ':' + pad(d % 60);
      $('state').textContent = now < openEnd ? 'Opening: confirm the person' : 'Interview';
    } else { $('tminus').textContent = 'DEBRIEF'; $('state').textContent = 'Score the predictions, then /recoil-close'; }
  }
  tick(); setInterval(tick, 1000);

  // Cockpit
  const ck = $('cockpit');
  const head = el('div', 'cockpit-head'); const h2 = el('h2', null, 'Cockpit'); h2.id = 'cockpit-h';
  const tog = el('button', null, 'Expand all'); tog.type = 'button';
  head.append(h2, tog); ck.appendChild(head);
  B.cockpit.sections.forEach(sec => {
    const d = el('details', 'csec ' + sec.id); d.open = true;
    d.appendChild(el('summary', 'disc csum', sec.title));
    const wrap = el('div', 'citems unfold');
    sec.items.forEach(it => {
      const row = el('div', 'citem-row'); const di = el('details', 'citem'); const s = el('summary', 'disc'); row.appendChild(di);
      s.append(el('span', 'ch', it.h), el('span', 'cl', it.lede)); di.appendChild(s);
      if (it.link) {
        const a = el('a', 'jump', 'Details \u2193'); a.href = '#' + slug(it.link);
        a.setAttribute('aria-label', 'Jump to ' + it.link);
        a.addEventListener('click', (e) => {
          e.preventDefault();
          const tgt = document.getElementById(slug(it.link)); if (!tgt) return;
          const ln = tgt.closest('details.lane'); if (ln) ln.open = true; tgt.open = true;
          tgt.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
          tgt.classList.remove('flash'); void tgt.offsetWidth; tgt.classList.add('flash');
        });
        row.appendChild(a);
      }
      const ul = el('ul', 'unfold'); it.bullets.forEach(b => ul.appendChild(el('li', null, b))); di.appendChild(ul);
      wrap.appendChild(row);
    });
    d.appendChild(wrap); ck.appendChild(d);
  });
  tog.addEventListener('click', () => {
    const items = ck.querySelectorAll('details.citem'), open = tog.textContent === 'Expand all';
    ck.querySelectorAll('details.csec').forEach(x => x.open = true);
    items.forEach(x => x.open = open); tog.textContent = open ? 'Collapse all' : 'Expand all';
  });

  // Cards
  function card(c, laneId, ci){
    const sec = el('details', 'card' + (c.wide ? ' wide' : '')); sec.id = slug(c.title);
    const sum = el('summary', 'disc card-sum'); const h = el('h3', null, c.title); if (c.chip) h.appendChild(chip(c.chip)); sum.appendChild(h);
    const s = el('div', 'cbody unfold');
    if (c.type === 'kv') { const dl = el('dl', 'kv'); c.rows.forEach(([k, v]) => { dl.append(el('dt', null, k), el('dd', null, v)); }); s.appendChild(dl); }
    else if (c.type === 'say') s.appendChild(el('p', 'quote', c.text));
    else if (c.type === 'list') { const ul = el('ul', 'clean'); c.items.forEach(t => ul.appendChild(el('li', null, t))); s.appendChild(ul); }
    else if (c.type === 'asks') {
      const ol = el('ol', 'ask'); ol.style.counterReset = 'q ' + ((c.numberFrom || 1) - 1);
      c.items.forEach((t, i) => {
        const id = 'ask-' + laneId + '-' + ci + '-' + i, li = el('li');
        const cb = el('input'); cb.type = 'checkbox'; cb.id = id; cb.checked = !!store.asks[id];
        const lab = el('label', null, t); lab.htmlFor = id; li.classList.toggle('done', cb.checked);
        cb.addEventListener('change', () => { li.classList.toggle('done', cb.checked); store.asks[id] = cb.checked; save(); });
        li.append(cb, lab); ol.appendChild(li);
      });
      s.appendChild(ol);
    } else if (c.type === 'exante') {
      const wrap = el('div', 'tablewrap'), t = el('table'), thead = el('thead'), tr = el('tr');
      ['Prediction', 'P', 'Basis', 'Result'].forEach(x => tr.appendChild(el('th', null, x))); thead.appendChild(tr); t.appendChild(thead);
      const tb = el('tbody'), score = el('p', 'score');
      function brier(){
        const done = c.items.map((it, i) => [it.p, store.results['ex-' + i]]).filter(([, r]) => r === 'hit' || r === 'miss');
        if (!done.length) { score.textContent = 'Mark results after the call to see your Brier score (0 is perfect, 0.25 is a coin flip).'; return; }
        const b = done.reduce((a, [p, r]) => a + Math.pow((r === 'hit' ? 1 : 0) - p, 2), 0) / done.length;
        score.textContent = ''; score.append('Brier score on ' + done.length + ' resolved: ', el('b', null, b.toFixed(2)), ' (0 is perfect, 0.25 is a coin flip)');
      }
      c.items.forEach((it, i) => {
        const id = 'ex-' + i, row = el('tr');
        row.append(el('td', null, it.text), el('td', 'p', it.p.toFixed(2)), el('td', 'basis', it.basis));
        const td = el('td'), sel = el('select'); sel.id = id; sel.setAttribute('aria-label', 'Result for prediction ' + (i + 1));
        [['', 'Open'], ['hit', 'Hit'], ['miss', 'Miss']].forEach(([v, l]) => { const o = el('option', null, l); o.value = v; sel.appendChild(o); });
        sel.value = store.results[id] || '';
        sel.addEventListener('change', () => { store.results[id] = sel.value; save(); brier(); });
        td.appendChild(sel); row.appendChild(td); tb.appendChild(row);
      });
      t.appendChild(tb); wrap.appendChild(t); s.append(wrap, score); brier();
      if (c.after) s.appendChild(el('p', 'stamp', c.after));
    }
    if (c.stamp) s.appendChild(el('p', 'stamp', c.stamp));
    sec.append(sum, s); return sec;
  }

  // Lanes: current phase first, the rest in call order
  let syncing = false;
  const cur = phase(Date.now());
  const order = [B.lanes.find(l => l.id === cur), ...B.lanes.filter(l => l.id !== cur)];
  order.forEach(l => {
    const lane = el('details', 'lane'); lane.id = l.id; lane.open = (l.id === cur);
    const sum = el('summary', 'disc lane-head');
    sum.append(el('h2', null, l.title), el('span', 'when', l.when));
    if (l.id === cur) sum.appendChild(el('span', 'now', 'NOW'));
    sum.appendChild(el('span', 'lane-job', l.job));
    const g = el('div', 'grid unfold'); l.cards.forEach((c, ci) => g.appendChild(card(c, l.id, ci)));
    lane.append(sum, g); const lw = el('div', 'lane-wrap'); lw.appendChild(lane); $('lanes').appendChild(lw);
    // Expand-all for this lane
    const btn = el('button', 'lane-all', 'Open all'); btn.type = 'button';
    btn.addEventListener('click', (e) => {
      e.preventDefault(); e.stopPropagation(); lane.open = true;
      const cards = g.querySelectorAll(':scope > details.card'), open = btn.textContent === 'Open all';
      syncing = true; cards.forEach(x => x.open = open); syncing = false;
      btn.textContent = open ? 'Fold all' : 'Open all';
    });
    lw.appendChild(btn);
    // Pair cards that share a row, so a row unfolds together
    const cs = [...g.querySelectorAll(':scope > details.card')]; let pend = null;
    cs.forEach(x => { if (x.classList.contains('wide')) { pend = null; return; } if (pend) { pend._mate = x; x._mate = pend; pend = null; } else pend = x; });
    cs.forEach(x => x.addEventListener('toggle', () => {
      if (syncing || !x._mate || x._mate.open === x.open || x._mate.offsetTop !== x.offsetTop) return;
      syncing = true; x._mate.open = x.open; syncing = false;
    }));
  });
})();
</script>
