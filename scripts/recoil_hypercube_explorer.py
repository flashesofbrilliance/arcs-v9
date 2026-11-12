#!/usr/bin/env python3
"""recoil_hypercube_explorer: build the J4 hypercube explorer page (backlog row recoil-hypercube-index, R8).

The page is assembled, never hand-edited:
  atoms      src/ui-kit/recoil-report/_tokens.css, inlined verbatim
  molecules  kit @prim blocks (PRIMS below), pulled from the kit files at build time
  template   recoil-skim in src/ui-kit/templates.json
  data       none in the committed page: it loads an SSOT v2 JSON (the runner's working copy,
             runtime/recoil/runs/<stem>/ssot.v2.json) from a file picker or ?src=<url>.
             With no data, or data with no cells, it renders empty and grain with n = 0.

What it shows: a 2D slice over any two of the five ADR-060 axes (rows x columns), the other three
filtered to All or one value; a filled-cell list (kit 57 ledger rows), each cell linking to the atoms it
cites; the claims those cells cite (kit 59); how each axis is set (kit 63).

  python3 scripts/recoil_hypercube_explorer.py                       write _ARTIFACTS/recoil-hypercube-explorer.html
  python3 scripts/recoil_hypercube_explorer.py --check               exit 1 if the committed page differs
  python3 scripts/recoil_hypercube_explorer.py --data SSOT OUT.html  a copy with one record embedded (OUT must sit
                                                                     under runtime/recoil/runs/, gitignored)
Stdlib only.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
OUT = os.path.join(ROOT, "_ARTIFACTS/recoil-hypercube-explorer.html")
RUNS = os.path.join(ROOT, "runtime/recoil/runs")
PRIMS = ["27-section-label", "28-chip", "32-evidence-ref", "37-fidelity-grain",
         "24-segmented-control", "22-pad-grid", "56-fold", "57-ledger-row", "58-toast", "59-claim-check",
         "63-operator-pass"]


def prim(name):
    text = open(os.path.join(KIT, name + ".html"), encoding="utf-8").read()
    m = re.search(r"/\* @prim:begin %s \*/\n.*?/\* @prim:end %s \*/\n" % (name, name), text, re.S)
    if not m:
        raise SystemExit(f"kit primitive {name} has no @prim block")
    return m.group(0)


PAGE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; }
main { --measure: 72rem; max-width: var(--measure); margin: 0 auto; padding: 32px 16px 96px; display: flex; flex-direction: column; gap: 24px; }
.hx-head { display: flex; flex-direction: column; gap: 8px; }
.hx-head h1 { font-family: var(--ds-font-display); font-size: var(--fs-display); font-weight: 600; line-height: 1.15; }
.hx-lede { max-width: none; color: var(--text-secondary); }
.hx-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.hx-load { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
.hx-load label { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); }
.hx-path { font-family: var(--ds-font-mono); font-size: var(--fs-body); color: var(--text-secondary); overflow-wrap: anywhere; }
.hx-load input[type=file] { font: inherit; color: var(--text-secondary); min-height: 44px; }
.hx-load input[type=file]:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.hx-controls { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.hx-controls fieldset { border: 0; min-width: 0; }
.hx-controls legend { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 6px; }
.hx-filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(30rem, 1fr)); gap: 16px; margin-top: 16px; }
.hx-filters fieldset { border: 0; min-width: 0; }
.hx-filters legend { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 6px; }
.seg label { padding: 10px 4px; min-height: 44px; display: flex; align-items: center; justify-content: center; overflow-wrap: anywhere; }
.slice.pads { grid-template-columns: minmax(4.5rem, auto) repeat(5, minmax(0, 1fr)); margin-top: 24px; }
.slice .ph { cursor: default; }
.slice .pr, .slice .pad small { font-size: var(--fs-body); }
.pad[disabled] { cursor: default; color: var(--muted); background: var(--surface); }
.pad[disabled]:hover { border-color: var(--border); }
.pad.filled { color: var(--text); border-color: var(--cyan); background: var(--cyan-bg); }
.pad small b { font-weight: 700; }
.hx-empty { padding: 16px; border: 1px solid var(--border); border-radius: var(--ds-r-sm); background: var(--surface); }
.lr-body a { color: var(--cyan); text-decoration: underline; text-underline-offset: 3px; display: inline-flex; align-items: center; min-height: 44px; min-width: 44px; justify-content: center; }
.lr-key { overflow-wrap: anywhere; }
:target { outline: 2px solid var(--cyan); outline-offset: -2px; }
@media (max-width: 760px) { .hx-controls, .hx-filters { grid-template-columns: minmax(0, 1fr); } .slice.pads { gap: 4px; } .hx-filters { grid-template-columns: minmax(0, 1fr); } }
"""

BODY = """<main>
<header class="hx-head">
  <div class="section-label">Recoil J4 · ADR-060</div>
  <h1>Why it works: the hypercube explorer</h1>
  <p class="hx-lede">One call placed on five axes of five (3,125 coordinates). Only filled cells light up, and every filled cell cites the atoms of the verb read or claim it came from. Pick two axes to slice; filter the other three.</p>
  <div class="hx-chips" id="hx-status"></div>
  <div class="hx-load"><label for="hx-file">Load an SSOT v2 file</label><input type="file" id="hx-file" accept="application/json,.json"><span class="hx-path" id="hx-src">runtime/recoil/runs/&lt;stem&gt;/ssot.v2.json</span></div>
</header>
<section aria-labelledby="h-slice">
  <h2 class="section-label" id="h-slice">Slice</h2>
  <div class="hx-controls">
    <fieldset><legend>Rows</legend><div class="seg" role="radiogroup" aria-label="Row axis" id="hx-rows"></div></fieldset>
    <fieldset><legend>Columns</legend><div class="seg" role="radiogroup" aria-label="Column axis" id="hx-cols"></div></fieldset>
  </div>
  <div class="hx-filters" id="hx-filters"></div>
  <div class="slice pads" id="hx-grid" role="group" aria-label="Slice of filled cells"></div>
</section>
<div class="folds">
  <details class="fold" id="f-cells" open>
    <summary><div class="fold-title"><h2>Filled cells</h2><span class="fold-verdict" id="v-cells"></span></div><span class="chip" id="c-cells"></span></summary>
    <div class="fold-body"><div class="ledger" id="hx-cells"></div></div>
  </details>
  <details class="fold" id="f-claims">
    <summary><div class="fold-title"><h2>Claims the cells cite</h2><span class="fold-verdict" id="v-claims"></span></div></summary>
    <div class="fold-body"><div class="claims" id="hx-claims"></div></div>
  </details>
  <details class="fold" id="f-atoms">
    <summary><div class="fold-title"><h2>Atoms the cells cite</h2><span class="fold-verdict" id="v-atoms"></span></div></summary>
    <div class="fold-body"><div class="ledger" id="hx-atoms"></div></div>
  </details>
  <details class="fold" id="f-axes">
    <summary><div class="fold-title"><h2>How each axis is set</h2><span class="fold-verdict">Verb and operator by code where the record fixes them; the rest by one checked judgment call</span></div></summary>
    <div class="fold-body"><div class="passes">
      <div class="pass"><div><span class="pass-k">Verb</span><p>analyze, assess, evaluate, synthesize, recapitulate</p></div><div><span class="pass-k">Source</span><p>The J2 verb pass the cell came from.</p></div><div><span class="pass-k">Set by</span><p><span class="pass-v held">Code</span>A claim no verb pass lists gets its verb by judgment.</p></div></div>
      <div class="pass"><div><span class="pass-k">Operator</span><p>LAB, KKL, BAR, COURT, FUNHOUSE</p></div><div><span class="pass-k">Source</span><p>The J3 ruling: GROUNDED to LAB, INFERENCE to KKL, STRUCK to FUNHOUSE (ADR-060 section 4).</p></div><div><span class="pass-k">Set by</span><p><span class="pass-v held">Code</span>When the claims in a source disagree, or there are none, by judgment.</p></div></div>
      <div class="pass"><div><span class="pass-k">Lens, resolution, L-stack</span><p>D W H C R · Exec to Surgical · L1 to L5</p></div><div><span class="pass-k">Source</span><p>One model call places each source; code keeps only valid values and the source's own atoms.</p></div><div><span class="pass-k">Set by</span><p><span class="pass-v changed">Judgment</span>Graded by code from the atoms cited; one atom is grade D.</p></div></div>
    </div></div>
  </details>
</div>
<div class="toast gold" role="status" data-toast>
  <span class="toast-title">No cell is invented</span>
  <button class="toast-close" type="button" aria-label="Dismiss the guard note" data-toast-close><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
  <p class="toast-msg">A cell exists only where a verb read or a claim cites atoms. An empty record renders an empty slice, never a filled one.</p>
  <span class="toast-meta">J4 gate · scripts/recoil_stage_j4.py</span>
</div>
</main>"""

SCRIPT = r"""
var AX = {lens: ['D','W','H','C','R'], resolution: ['Exec','Strategic','Operational','Tactical','Surgical'],
  operator: ['LAB','KKL','BAR','COURT','FUNHOUSE'], verb: ['analyze','assess','evaluate','synthesize','recapitulate'],
  l: ['L1','L2','L3','L4','L5']};
var NAME = {lens: 'Lens', resolution: 'Resolution', operator: 'Operator', verb: 'Verb', l: 'L-stack'};
var LENS = {D: 'Decision', W: 'Window', H: 'Human', C: 'Coherence', R: 'Risk'};
var KEYS = ['lens','resolution','operator','verb','l'];
var S = {doc: null, rows: 'lens', cols: 'verb', f: {}, pick: null, src: ''};
function esc(s){return String(s == null ? '' : s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function $(id){return document.getElementById(id);}
function cells(){return (S.doc && S.doc.cells) || [];}
function atoms(){var m = {}; ((S.doc && S.doc.call && S.doc.call.atoms) || []).forEach(function(a){m[a.id] = a;}); return m;}
function seg(host, name, opts, cur, on){
  host.innerHTML = opts.map(function(o, i){var id = name + '-' + i;
    return '<input type="radio" name="' + name + '" id="' + id + '" value="' + esc(o[0]) + '"' + (o[0] === cur ? ' checked' : '') + '><label for="' + id + '">' + esc(o[1]) + '</label>';}).join('');
  host.onchange = function(e){on(e.target.value);};
}
function shown(){return cells().filter(function(c){
  for (var k in S.f) { if (S.f[k] && c[k] !== S.f[k]) return false; }
  if (S.pick && (c[S.rows] !== S.pick[0] || c[S.cols] !== S.pick[1])) return false;
  return true;});}
function render(){
  var all = cells(), n = all.length, rid = S.doc && S.doc.meta ? S.doc.meta.report_id : '';
  var grain = n === 0;
  document.body.classList.toggle('grain', grain);
  $('hx-status').innerHTML = (S.doc ? '<span class="chip">' + esc(rid || 'record') + '</span>' : '<span class="chip">No record loaded</span>')
    + '<span class="chip' + (grain ? '' : ' cyan') + '">' + n + ' of 3,125 filled</span>'
    + (grain ? '<span class="chip">Grain · n = 0</span>' : '');
  var axes = KEYS.map(function(k){return [k, NAME[k]];});
  seg($('hx-rows'), 'rows', axes, S.rows, function(v){S.rows = v; if (S.cols === v) S.cols = KEYS[(KEYS.indexOf(v) + 1) % 5]; S.pick = null; render();});
  seg($('hx-cols'), 'cols', axes, S.cols, function(v){S.cols = v; if (S.rows === v) S.rows = KEYS[(KEYS.indexOf(v) + 4) % 5]; S.pick = null; render();});
  var rest = KEYS.filter(function(k){return k !== S.rows && k !== S.cols;});
  $('hx-filters').innerHTML = rest.map(function(k){return '<fieldset><legend>' + NAME[k] + '</legend><div class="seg" role="radiogroup" aria-label="Filter ' + NAME[k] + '" id="hx-f-' + k + '"></div></fieldset>';}).join('');
  rest.forEach(function(k){seg($('hx-f-' + k), 'f-' + k, [['', 'All']].concat(AX[k].map(function(v){return [v, v];})), S.f[k] || '', function(v){S.f[k] = v; S.pick = null; render();});});
  Object.keys(S.f).forEach(function(k){if (rest.indexOf(k) < 0) delete S.f[k];});
  var base = all.filter(function(c){for (var k in S.f) { if (S.f[k] && c[k] !== S.f[k]) return false; } return true;});
  var g = '<span class="pr" aria-hidden="true"></span>' + AX[S.cols].map(function(v){return '<span class="ph" aria-hidden="true">' + esc(v) + '</span>';}).join('');
  AX[S.rows].forEach(function(r){
    g += '<span class="pr" aria-hidden="true">' + esc(S.rows === 'lens' ? r + ' ' + LENS[r] : r) + '</span>';
    AX[S.cols].forEach(function(cv){
      var k = base.filter(function(c){return c[S.rows] === r && c[S.cols] === cv;}).length;
      var on = S.pick && S.pick[0] === r && S.pick[1] === cv;
      g += '<button class="pad' + (k ? ' filled' : '') + '" type="button" data-r="' + esc(r) + '" data-c="' + esc(cv) + '"'
        + (k ? ' aria-pressed="' + (on ? 'true' : 'false') + '"' : ' disabled') + ' aria-label="' + esc(NAME[S.rows] + ' ' + r + ', ' + NAME[S.cols] + ' ' + cv + ': ' + k + ' filled') + '"><small>' + (k ? '<b>' + k + '</b>' : '0') + '</small></button>';
    });
  });
  $('hx-grid').innerHTML = g;
  $('hx-grid').onclick = function(e){var b = e.target.closest('.pad'); if (!b || b.disabled) return;
    var p = [b.getAttribute('data-r'), b.getAttribute('data-c')];
    S.pick = (S.pick && S.pick[0] === p[0] && S.pick[1] === p[1]) ? null : p; render();};
  var list = shown(), am = atoms(), used = [], usedClaims = [];
  $('c-cells').textContent = list.length + ' shown';
  $('v-cells').textContent = n ? (S.pick ? NAME[S.rows] + ' ' + S.pick[0] + ' by ' + NAME[S.cols] + ' ' + S.pick[1] + ': ' + list.length + ' cell(s)' : list.length + ' of ' + n + ' filled cells match the filters')
    : 'Nothing filled yet: J4 has not placed this record (n = 0)';
  $('hx-cells').innerHTML = list.length ? list.map(function(c){
    (c.cites || []).forEach(function(a){if (used.indexOf(a) < 0) used.push(a);});
    (c.claims || []).forEach(function(a){if (usedClaims.indexOf(a) < 0) usedClaims.push(a);});
    var gd = c.grade || {}, weak = gd.letter === 'D' || gd.letter === 'E' || gd.letter === 'NS';
    return '<div class="ledger-row' + (weak ? ' grain' : '') + '"><div class="lr-key">' + esc(c.id) + '</div><div class="lr-body"><div class="lr-chips">'
      + '<span class="chip">' + esc(LENS[c.lens] || c.lens) + '</span><span class="chip">' + esc(c.operator) + '</span><span class="chip' + (weak ? '' : ' green') + '">Grade ' + esc(gd.letter || 'NS') + '</span></div>'
      + '<span>' + esc(c.note) + (weak ? ' (n = ' + esc(gd.n == null ? 0 : gd.n) + ')' : '') + '</span>'
      + '<span class="ref">atoms ' + (c.cites || []).map(function(a){return '<a href="#' + esc(a) + '">' + esc(a) + '</a>';}).join(', ')
      + ((c.claims || []).length ? ' · claims ' + c.claims.map(function(k){return '<a href="#' + esc(k) + '">' + esc(k) + '</a>';}).join(', ') : '') + '</span></div></div>';
  }).join('') : '<div class="ledger-row grain"><div class="lr-key">n = 0</div><div class="lr-body"><span>' + (n ? 'No filled cell matches this slice.' : (S.doc ? 'This record has no cells. Run J4: scripts/recoil_service.py run --call &lt;call&gt; --only J4.' : 'Load a record to see its cells.')) + '</span></div></div>';
  var cm = {}; ((S.doc && S.doc.claims) || []).forEach(function(c){cm[c.id] = c;});
  $('v-claims').textContent = usedClaims.length + ' claim(s) in the cells shown';
  $('hx-claims').innerHTML = usedClaims.length ? usedClaims.map(function(k){var c = cm[k] || {}, r = c.ruling || '';
    var cls = r === 'GROUNDED' ? 'sharp' : (r === 'STRUCK' ? 'slip' : 'degraded');
    return '<div class="claim ' + cls + '" id="' + esc(k) + '"><div class="claim-said"><span class="claim-k">' + esc(k) + '</span><span>' + esc(c.said) + '</span></div><span class="chip">' + esc(r || 'unknown') + '</span><div class="claim-record"><span class="claim-v">' + esc(r || 'n/a') + '</span><span class="claim-note">' + esc(c.mechanism) + '</span><span class="ref">atoms ' + esc((c.cites || []).join(', ')) + '</span></div></div>';}).join('')
    : '<div class="claim grain"><div class="claim-said"><span class="claim-k">n = 0</span><span>No claim cited.</span></div></div>';
  $('v-atoms').textContent = used.length + ' atom(s) in the cells shown';
  $('hx-atoms').innerHTML = used.length ? used.map(function(id){var a = am[id] || {};
    return '<div class="ledger-row" id="' + esc(id) + '"><div class="lr-key">' + esc(id) + ' [' + esc(a.t) + ']</div><div class="lr-body"><div class="lr-chips"><span class="chip">' + esc(a.speaker) + '</span><span class="chip">' + esc(a.kind) + '</span></div><span>' + esc(a.text) + '</span></div></div>';}).join('')
    : '<div class="ledger-row grain"><div class="lr-key">n = 0</div><div class="lr-body"><span>No atom cited.</span></div></div>';
}
function load(doc, src){S.doc = doc; S.src = src || ''; S.pick = null; if (src) $('hx-src').textContent = src; render();}
window.hxLoad = load;
$('hx-file').onchange = function(e){var f = e.target.files[0]; if (!f) return; var r = new FileReader();
  r.onload = function(){try { load(JSON.parse(r.result), f.name); } catch (err) { $('hx-src').textContent = 'Not JSON: ' + f.name; }}; r.readAsText(f);};
document.addEventListener('click', function(e){var a = e.target.closest('a[href^="#"]'); if (!a) return;
  var t = document.getElementById(a.getAttribute('href').slice(1)); var d = t && t.closest('details'); if (d) d.open = true;});
document.querySelectorAll('[data-toast-close]').forEach(function(b){b.onclick = function(){b.closest('[data-toast]').hidden = true;};});
(function(){
  var embedded = document.getElementById('hx-data');
  if (embedded && embedded.textContent.trim()) { load(JSON.parse(embedded.textContent), embedded.getAttribute('data-src')); return; }
  var m = /[?&]src=([^&]+)/.exec(location.search);
  if (m) { var u = decodeURIComponent(m[1]); fetch(u).then(function(r){return r.json();}).then(function(d){load(d, u);}).catch(function(){$('hx-src').textContent = 'Could not load ' + u; render();}); return; }
  render();
})();
"""


def build(data=None, src=""):
    tokens = open(os.path.join(KIT, "_tokens.css"), encoding="utf-8").read()
    css = tokens + "\n" + "".join(prim(p) for p in PRIMS) + PAGE_CSS
    if chr(0x2014) in "".join(prim(p) for p in PRIMS) + PAGE_CSS + BODY + SCRIPT:
        raise SystemExit("recoil_hypercube_explorer: an em-dash in the page's own text (data is not checked)")
    blob = ""
    if data is not None:
        payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        blob = f'<script type="application/json" id="hx-data" data-src="{src}">{payload}</script>\n'
    page = ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<!-- @arcs-template: recoil-skim -->\n<!-- @arcs-mode: operate -->\n"
            "<!-- generated by scripts/recoil_hypercube_explorer.py; edit the generator, not this file -->\n"
            "<title>Hypercube explorer</title>\n<meta name=\"robots\" content=\"noindex, nofollow\">\n"
            f"<style>\n{css}</style>\n</head>\n<body>\n{BODY}\n{blob}<script>{SCRIPT}</script>\n</body>\n</html>\n")
    return page


def main(argv):
    if argv[:1] == ["--check"]:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        ok = cur == build()
        print("recoil_hypercube_explorer: " + ("page matches its generator" if ok else "page differs; rerun the generator"))
        return 0 if ok else 1
    if argv[:1] == ["--data"]:
        if len(argv) != 3:
            raise SystemExit("usage: --data SSOT.json OUT.html")
        out = os.path.abspath(argv[2])
        if not out.startswith(RUNS + os.sep):
            raise SystemExit("recoil_hypercube_explorer: a page with data goes under runtime/recoil/runs/ (gitignored)")
        doc = json.load(open(argv[1], encoding="utf-8"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(build(doc, os.path.relpath(os.path.abspath(argv[1]), ROOT)))
        print(f"wrote {os.path.relpath(out, ROOT)} ({len(doc.get('cells') or [])} cells)")
        return 0
    open(OUT, "w", encoding="utf-8").write(build())
    print(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
