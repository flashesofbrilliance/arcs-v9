/* arcs-token-tuner: live layout and text controls for a page, internal only.
   ?tune  sliders bound to the page's :root tokens, one slider per CSS breakpoint, text-wrap selects.
   ?edit  every element carrying data-src="/json/pointer" becomes editable (a --tune build of a data page emits those).
   It writes CSS custom properties on <html>, rewrites the page's own @media and @container width rules (px or rem), and adds one <style> for wrapping.
   "Copy CSS" gives one line to paste after the page's last :root block. "Copy JSON" gives one RFC 6902 patch for the
   page's data file (text edits, and the breakpoint when <main data-bp-src> names its field); apply it with the builder.
   Breakpoints move for JS too: in tune mode window.matchMedia is wrapped so a query such as (max-width: 1023px) follows
   the slider, which is why the inliner puts this script first in <body>, before the page's own scripts.
   Viewport: Mobile 375, Tablet 768, Desktop 1280 render the page in an iframe of the same URL (?tune&tuneframe), so
   its own @media rules and matchMedia answer to that width, not the window's; Fit drops the frame. The frame reads the
   panel's saved state and the panel pushes every change to it. Print applies the page's @media print rules (and turns
   @media screen off) so PDF layout can be tuned; @page size and margins are not simulated, so pick the width yourself.
   Double-click (tune mode, in Fit or in a frame): any text element without data-src becomes editable in place; Enter or
   Esc or a click away commits. "Copy edits" gives a JSON list of {old, new} text pairs, one per changed text node;
   apply it to the page's SOURCE with token_tuner_inline.py --apply-text edits.json SOURCE.html, which refuses any old
   text that is missing or not unique. Or hand any export (Copy JSON, Copy CSS, Copy edits, Export versions) to the page's own
   builder with --apply; scripts/page_tune.py routes each part to that page's source. Never hand-edit a built file.
   State autosaves (debounced, localStorage per page path, sessionStorage if that is blocked), text edits included, and
   comes back on reload. "Drop breadcrumb" snapshots it as v1, v2... with a time, an optional note and an empty "why"
   (reserved for a later prompt); any version restores, and "Export versions" gives JSON that --apply-text also takes.
   Plain view (2026-11-11): every control carries a plain name ("Body text width"), the raw token or query in its tooltip.
   A page can name its own controls with a script element of type application/json carrying data-tune-labels, whose
   body is a map such as {"--measure": "...", "640px": "...", "40rem": "..."}; otherwise a readable name is generated. "Saved" shows the autosave, "Back"
   steps back through the last 5 changes, Reset asks first, and a Lock on any control keeps its value through Back,
   Restore and Reset (locks save with the state). The copy tools sit under a collapsed "For developers".
   Inline it with scripts/token_tuner_inline.py; page_gate.py --counterpart fails any page that still carries it.
   Source of truth: src/ui-kit/token-tuner.js. Kit primitive: src/ui-kit/recoil-report/40-token-tuner.html. */
(function () {
  // window.__arcsTuneForce (set by the bookmarklet, scripts/tune_serve.py) starts tune mode on a page with no ?tune
  var Q = location.search, FORCE = !!window.__arcsTuneForce;
  var TUNE = FORCE || /[?&]tune(=|&|$)/.test(Q), EDIT = /[?&]edit(=|&|$)/.test(Q);
  if (!TUNE && !EDIT) return;
  var SELF = (document.currentScript && document.currentScript.src) || '';   // empty when inlined
  if (window.__arcsTokenTuner) return;
  window.__arcsTokenTuner = true;

  // name, unit, min, max, step. A token the page does not declare shows as "not declared" and stays inert.
  var SPEC = [
    ['--measure', 'px', 480, 960, 8],
    ['--sp-1', 'px', 0, 24, 1],
    ['--sp-2', 'px', 0, 40, 1],
    ['--sp-3', 'px', 0, 56, 1],
    ['--sp-4', 'px', 0, 88, 2],
    ['--sp-5', 'px', 0, 128, 2],
    ['--gap', 'px', 0, 48, 1],
    ['--fs-step', 'rem', 0.9, 1.8, 0.025],
    ['--fs-body', 'rem', 0.75, 1.25, 0.0125],
    ['--lh', '', 1.1, 2.0, 0.05],
    ['--ls', 'em', -0.05, 0.1, 0.005]
  ];
  // plain names for the tokens; a page's data-tune-labels map wins over these
  var NAMES = {
    '--measure': 'Text column width', '--sp-1': 'Tiny gap (inside a line or label)', '--sp-2': 'Small gap (between lines in a card)',
    '--sp-3': 'Medium gap (between paragraphs)', '--sp-4': 'Large gap (between blocks)', '--sp-5': 'Section gap (between page sections)',
    '--gap': 'Space between columns and cards', '--fs-step': 'Heading and callout size', '--fs-body': 'Body text size',
    '--lh': 'Line spacing', '--ls': 'Letter spacing'
  };
  // what a reader sees for a value: px as is, rem as "× normal" (1rem is the normal text size), a bare ratio as "×"
  function show(n, unit) { var v = Math.round(n * 1000) / 1000; return unit === 'rem' ? v + ' × normal' : unit === '' ? v + '×' : v + (unit === 'px' ? ' px' : unit); }
  // text-wrap groups: one select each, applied with one injected rule
  var WRAPS = [['Headings', ':is(h1,h2,h3,h4)', 'How headings break across lines'], ['Body', ':is(p,li,dd)', 'How paragraphs break across lines']];
  var WRAP_OPTS = [['', 'As the page sets it'], ['balance', 'Even line lengths'], ['pretty', 'Avoid one word alone on the last line'], ['wrap', 'Plain wrapping'], ['stable', 'Plain, steady while typing']];
  var root = document.documentElement;
  var KEY = 'arcsTokenTuner:' + location.pathname, VKEY = 'arcsTokenTuner:versions:' + location.pathname;
  function load(k) {
    var v = null;
    try { v = localStorage.getItem(k); } catch (e) {}
    if (v == null) { try { v = sessionStorage.getItem(k); } catch (e) {} }
    try { return JSON.parse(v || 'null'); } catch (e) { return null; }
  }
  function store(k, obj) {
    var t = JSON.stringify(obj);
    try { localStorage.setItem(k, t); return true; } catch (e) {}
    try { sessionStorage.setItem(k, t); return true; } catch (e) {}
    return false;
  }
  var saved = load(KEY) || {};
  var BP = saved.bp || {};          // breakpoint key -> new key, only the moved ones
  var PRINT = !!saved.print;        // print preview: @media print on, @media screen off
  var FRAME = TUNE && /[?&]tuneframe(=|&|$)/.test(Q) && window.parent !== window;
  var VPS = [['Mobile', 375], ['Tablet', 768], ['Desktop', 1280], ['Fit', 0]];
  function fmt(n, unit) { return (Math.round(n * 10000) / 10000) + unit; }

  /* ---------- breakpoints: one key per width; (max-width: 1023px) pairs with (min-width: 1024px) ---------- */
  var MQ_RE = /\((min|max)-width:\s*(\d+(?:\.\d+)?)px\)/g;
  function keyOf(kind, v) { return kind === 'max' && v % 2 === 1 ? v + 1 : v; }
  function remap(text) {
    return text.replace(MQ_RE, function (m, k, v) {
      v = +v; var key = keyOf(k, v), nk = BP[key];
      return nk == null ? m : '(' + k + '-width: ' + (nk + (v - key)) + 'px)';
    });
  }
  // print preview, one comma-separated query at a time: print -> all, screen -> not all (and the reverse under "not")
  function printify(text) {
    return text.split(',').map(function (q) {
      var neg = /^\s*not\s/i.test(q);
      if (/\bprint\b/i.test(q)) return neg ? 'not all' : q.replace(/\bonly\s+/i, '').replace(/\bprint\b/i, 'all');
      if (/\bscreen\b/i.test(q)) return neg ? q.replace(/\bnot\s+screen\b/i, 'all') : 'not all';
      return q;
    }).join(',');
  }
  function media(text) { return PRINT ? printify(remap(text)) : remap(text); }
  // matchMedia follows the sliders: a wrapped list re-evaluates and fires 'change' when its remapped answer flips
  var realMM = window.matchMedia ? window.matchMedia.bind(window) : null, lists = [];
  if (TUNE && realMM) {
    window.matchMedia = function (q) {
      q = String(q);
      if (!/-width:\s*[\d.]+px|\b(print|screen)\b/.test(q)) return realMM(q);
      var cur = realMM(media(q)), ls = [], o = { media: q, onchange: null };
      Object.defineProperty(o, 'matches', { get: function () { return cur.matches; } });
      function fire() { var ev = { matches: cur.matches, media: q }; ls.forEach(function (f) { f.call(o, ev); }); if (o.onchange) o.onchange(ev); }
      o.addEventListener = function (t, f) { if (t === 'change') ls.push(f); };
      o.removeEventListener = function (t, f) { var i = ls.indexOf(f); if (i > -1) ls.splice(i, 1); };
      o.addListener = function (f) { ls.push(f); };
      o.removeListener = function (f) { o.removeEventListener('change', f); };
      o._re = function () { var was = cur.matches; cur.removeEventListener('change', fire); cur = realMM(media(q)); cur.addEventListener('change', fire); if (cur.matches !== was) fire(); };
      cur.addEventListener('change', fire);
      lists.push(o);
      return o;
    };
  }
  var mediaRules = [], contRules = [];
  // @container width queries (kit 54 signal ledger, 55 sound bite): one key per width and unit, prefixed c
  var CQ_RE = /\((min|max)-width:\s*(\d+(?:\.\d+)?)(px|rem)\)/g;
  function ckey(v, u) { return 'c' + v + u; }
  function cremap(text) {
    return text.replace(CQ_RE, function (m, k, v, u) { var nk = BP[ckey(+v, u)]; return nk == null ? m : '(' + k + '-width: ' + nk + u + ')'; });
  }
  function scan(rules) {
    [].forEach.call(rules || [], function (r) {
      if (r.media && r.cssRules) { mediaRules.push({ rule: r, orig: r.media.mediaText }); }
      else if (r.cssRules && /^@container\b/.test(r.cssText || '')) {
        contRules.push({ rule: r, orig: r.conditionText, cur: r.conditionText });
      }
      if (r.cssRules) scan(r.cssRules);
    });
  }
  // conditionText is read-only on CSSContainerRule, so a moved query replaces the rule in place
  function applyCont() {
    contRules.forEach(function (c) {
      var t = cremap(c.orig); if (t === c.cur) return;
      var par = c.rule.parentRule || c.rule.parentStyleSheet, i = [].indexOf.call(par.cssRules, c.rule);
      if (i < 0) return;
      var body = c.rule.cssText.slice(c.rule.cssText.indexOf('{'));
      try { par.deleteRule(i); par.insertRule('@container ' + t + ' ' + body, i); c.rule = par.cssRules[i]; c.cur = t; } catch (e) { /* leave the rule as it was */ }
    });
  }
  [].forEach.call(document.styleSheets, function (s) { try { scan(s.cssRules); } catch (e) { /* cross-origin sheet: skip */ } });
  var menuEls = [];
  function collectMenus() {
    [].forEach.call(document.querySelectorAll('[data-menu-below]'), function (el) {
      menuEls.push({ el: el, orig: +el.getAttribute('data-menu-below') });
    });
  }
  function applyBP() {
    mediaRules.forEach(function (m) { var t = media(m.orig); if (m.rule.media.mediaText !== t) m.rule.media.mediaText = t; });
    menuEls.forEach(function (m) { var k = m.orig; m.el.setAttribute('data-menu-below', BP[k] != null ? BP[k] : k); });
    lists.forEach(function (o) { o._re(); });
    applyCont();
  }
  if (TUNE) applyBP();

  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }

  /* ---------- double-click text editing, for pages without data-src: pairs of old and new text-node values ---------- */
  var BLOCKS = 'p,li,h1,h2,h3,h4,h5,h6,td,th,dt,dd,figcaption,blockquote,summary,caption,label,button,a';
  function dblEdit(report) {
    var touched = [];   // touched: {el, html, nodes:[[node, value]]}
    var st = document.createElement('style'); st.setAttribute('data-arcs-token-tuner', 'dbl');
    st.textContent = '[data-tt-dbl][contenteditable]{outline:1px solid var(--cyan,LinkText);outline-offset:2px;cursor:text}' +
      '[data-tt-dbl]:not([contenteditable]){outline:1px solid var(--gold,Highlight);outline-offset:2px}';
    (document.head || root).appendChild(st);
    var ops = [];       // structural undo stack: {k:'merge', a, b} or {k:'remove', el, parent, next}
    function collect() {
      var list = [];
      touched.forEach(function (t) {
        if (t.into) return;                                   // merged into another line; reported there
        var parts = t.parts || [t.html];
        if (t.removed) { list.push({ op: 'remove', parts: parts }); return; }
        if (parts.length > 1) { list.push({ op: 'merge', parts: parts, new: t.el.innerHTML }); return; }
        var live = t.nodes.every(function (n) { return t.el.contains(n[0]); });
        var count = 0, w = document.createTreeWalker(t.el, NodeFilter.SHOW_TEXT); while (w.nextNode()) count++;
        if (live && count === t.nodes.length) {
          t.nodes.forEach(function (n) { if (n[0].nodeValue !== n[1]) list.push({ old: n[1], new: n[0].nodeValue }); });
        } else if (t.el.innerHTML !== t.html) {
          list.push({ old: t.html, new: t.el.innerHTML, html: true });   // structure changed: whole element
        }
        if (t.el.innerHTML !== t.html) t.el.setAttribute('data-tt-dbl', ''); else t.el.removeAttribute('data-tt-dbl');
      });
      last = JSON.stringify(list);
      report(list);
    }
    function blank(el) { return !el.textContent.replace(/[\s ​]+/g, '') && !el.querySelector('img,svg,video,iframe,input'); }
    function done(el) {
      if (!el.hasAttribute('contenteditable')) return;
      el.removeAttribute('contenteditable');
      var t = touch(el);
      if (!t.into && el.isConnected && blank(el)) {          // a line left with no text is removed
        t.removed = true; ops.push({ k: 'remove', el: el, parent: el.parentNode, next: el.nextSibling }); el.remove();
      }
      collect();
    }
    function edge(el, atEnd) {                                // caret collapsed at the start (or end) of el?
      var s = getSelection(); if (!s.rangeCount || !s.isCollapsed) return false;
      var r = s.getRangeAt(0), x = document.createRange(); x.selectNodeContents(el);
      if (atEnd) x.setStart(r.endContainer, r.endOffset); else x.setEnd(r.startContainer, r.startOffset);
      return !x.toString().replace(/[​]/g, '').length;
    }
    function sib(el, next) {
      var s = next ? el.nextElementSibling : el.previousElementSibling;
      return s && s.matches(BLOCKS) && !s.closest('[data-src],[data-arcs-token-tuner]') ? s : null;
    }
    function editable(el) {
      if (el.hasAttribute('contenteditable')) return;
      el.setAttribute('data-tt-dbl', ''); el.setAttribute('contenteditable', 'true');
      el.addEventListener('blur', function () { done(el); }, { once: true });
    }
    function merge(a, b) {                                    // b's content joins the end of a; b leaves the page
      var ta = touch(a), tb = touch(b);
      ta.parts = (ta.parts || [ta.html]).concat(tb.parts || [tb.html]);
      tb.into = ta;
      var at = a.textContent, bt = b.textContent, mark = document.createTextNode('');
      if (at && bt && !/\s$/.test(at) && !/^\s/.test(bt)) a.appendChild(document.createTextNode(' '));
      a.appendChild(mark);
      while (b.firstChild) a.appendChild(b.firstChild);
      ops.push({ k: 'merge', a: a, b: b });
      b.removeAttribute('contenteditable'); b.remove();
      editable(a); a.focus();
      var r = document.createRange(); r.setStartAfter(mark); r.collapse(true);
      var s = getSelection(); s.removeAllRanges(); s.addRange(r);
      collect();
    }
    document.addEventListener('dblclick', function (e) {
      var t = e.target, el = t && t.closest && t.closest(BLOCKS);
      // pages that set text in bare div/span (the Almanac): the element that directly holds the clicked text is editable too
      if (!el && t && t.nodeType === 1 && !/^(SCRIPT|STYLE|BODY|HTML|MAIN)$/.test(t.tagName) &&
          [].some.call(t.childNodes, function (n) { return n.nodeType === 3 && n.nodeValue.trim(); })) el = t;
      if (!el || el.closest('[data-src],[data-arcs-token-tuner]') || el.isContentEditable) return;
      e.preventDefault();
      touch(el);
      el.setAttribute('data-tt-dbl', ''); el.setAttribute('contenteditable', 'true'); el.focus();
      el.addEventListener('blur', function () { done(el); }, { once: true });
    }, true);
    document.addEventListener('keydown', function (e) {
      var el = e.target && e.target.closest && e.target.closest('[data-tt-dbl][contenteditable]'); if (!el) return;
      e.stopPropagation();
      if (e.key === 'Enter' || e.key === 'Escape') { e.preventDefault(); done(el); el.blur(); return; }
      // Backspace at a line's start joins it onto the line above; Delete at its end pulls the next line up
      var other;
      if (e.key === 'Backspace' && edge(el, false) && (other = sib(el, false))) { e.preventDefault(); merge(other, el); }
      else if (e.key === 'Delete' && edge(el, true) && (other = sib(el, true))) { e.preventDefault(); merge(el, other); }
    }, true);
    document.addEventListener('click', function (e) {
      var el = e.target && e.target.closest && e.target.closest('[data-tt-dbl][contenteditable]');
      if (el) { e.preventDefault(); e.stopPropagation(); }
    }, true);
    function touch(el) {
      var t = touched.filter(function (x) { return x.el === el; })[0];
      if (!t) {
        t = { el: el, html: el.innerHTML, nodes: [] };
        var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); while (w.nextNode()) t.nodes.push([w.currentNode, w.currentNode.nodeValue]);
        touched.push(t);
      }
      return t;
    }
    function revert() {
      for (var i = ops.length - 1; i >= 0; i--) {             // undo joins and removals newest first
        var o = ops[i];
        if (o.k === 'merge') o.a.parentNode && o.a.parentNode.insertBefore(o.b, o.a.nextSibling);
        else if (o.parent) o.parent.insertBefore(o.el, o.next && o.next.parentNode === o.parent ? o.next : null);
      }
      ops = [];
      touched.forEach(function (t) { t.el.innerHTML = t.html; t.el.removeAttribute('data-tt-dbl'); t.el.removeAttribute('contenteditable'); });
      touched = [];
    }
    var last = '[]';
    return {
      reset: function () { revert(); last = '[]'; report([]); },
      // make this document show exactly these pairs; no report. Returns the pairs that no longer match the page.
      apply: function (list) {
        list = list || [];
        var j = JSON.stringify(list);
        if (j === last) return [];
        revert();
        var missing = [];
        list.forEach(function (pr) {
          if (pr.op) {                                        // a join or a removal: find the run of lines by their original html
            var heads = [].filter.call(document.querySelectorAll(BLOCKS), function (el) { return el.innerHTML === pr.parts[0] && !el.closest('[data-arcs-token-tuner]'); });
            var run = heads.length === 1 ? [heads[0]] : null;
            for (var k = 1; run && k < pr.parts.length; k++) {
              var nx = run[k - 1].nextElementSibling;
              if (nx && nx.innerHTML === pr.parts[k]) run.push(nx); else run = null;
            }
            if (!run) { missing.push(pr); return; }
            var ta = touch(run[0]);
            run.slice(1).forEach(function (b) { var tb = touch(b); tb.into = ta; ops.push({ k: 'merge', a: run[0], b: b }); b.remove(); });
            ta.parts = pr.parts.slice();
            if (pr.op === 'remove') { ta.removed = true; ops.push({ k: 'remove', el: run[0], parent: run[0].parentNode, next: run[0].nextSibling }); run[0].remove(); }
            else { run[0].innerHTML = pr.new; run[0].setAttribute('data-tt-dbl', ''); }
            return;
          }
          if (pr.html) {
            var els = [].filter.call(document.querySelectorAll(BLOCKS), function (el) { return el.innerHTML === pr.old && !el.closest('[data-arcs-token-tuner]'); });
            if (els.length !== 1) { missing.push(pr); return; }
            touch(els[0]); els[0].innerHTML = pr.new; els[0].setAttribute('data-tt-dbl', '');
            return;
          }
          var hits = [], w = document.createTreeWalker(document.body || root, NodeFilter.SHOW_TEXT);
          while (w.nextNode()) {
            var n = w.currentNode, par = n.parentNode;
            if (n.nodeValue === pr.old && par && !/^(SCRIPT|STYLE)$/.test(par.nodeName)) hits.push(n);
          }
          if (hits.length !== 1) { missing.push(pr); return; }
          var el = (hits[0].parentNode.closest && hits[0].parentNode.closest(BLOCKS)) || hits[0].parentNode;
          touch(el); hits[0].nodeValue = pr.new; el.setAttribute('data-tt-dbl', '');
        });
        last = JSON.stringify(list.filter(function (pr) { return missing.indexOf(pr) < 0; }));
        return missing;
      }
    };
  }

  /* ---------- frame mode: no panel; mirror the panel's saved state, re-read on every push from the parent ---------- */
  if (FRAME) {
    var wrapF = null, menusDone = false, edF = null;
    window.__arcsTunerSync = function (state) {
      var s = state || load(KEY) || {};
      BP = s.bp || {}; PRINT = !!s.print;
      SPEC.forEach(function (sp) {
        var v = s.tok && s.tok[sp[0]];
        if (v != null) root.style.setProperty(sp[0], fmt(v, sp[1])); else root.style.removeProperty(sp[0]);
      });
      if (!wrapF) { wrapF = document.createElement('style'); wrapF.setAttribute('data-arcs-token-tuner', 'wrap'); document.head.appendChild(wrapF); }
      wrapF.textContent = WRAPS.map(function (w, i) { var v = s.wrap && s.wrap[i]; return v ? w[1] + '{text-wrap:' + v + '!important}' : ''; }).join('');
      if (!menusDone && document.readyState !== 'loading') { collectMenus(); menusDone = true; }
      applyBP();
      if (edF) edF.apply(s.dbl);
    };
    window.__arcsTunerSync();
    ready(function () {
      edF = dblEdit(function (list) { try { parent.__arcsTunerText(list); } catch (e) {} });
      window.__arcsTunerSync();
    });
    return;
  }
  ready(build);

  function build() {
    function declared(name) {
      // Read with the tuner's own override removed, so "original" means what the page ships.
      var had = root.style.getPropertyValue(name);
      if (had) root.style.removeProperty(name);
      var v = getComputedStyle(root).getPropertyValue(name).trim();
      if (had) root.style.setProperty(name, had);
      return v;
    }
    function parse(v, unit) {
      var m = /^(-?[\d.]+)([a-z%]*)$/.exec(v);
      if (!m || m[2] !== unit) return null;
      return parseFloat(m[1]);
    }
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

    var main = document.querySelector('[data-bp-src]');
    var bpData = main ? { key: +main.getAttribute('data-bp'), path: main.getAttribute('data-bp-src') } : null;
    collectMenus();
    if (TUNE) applyBP();
    var keys = {};
    mediaRules.forEach(function (m) { var r; MQ_RE.lastIndex = 0; while ((r = MQ_RE.exec(m.orig))) keys[keyOf(r[1], +r[2])] = 1; });
    menuEls.forEach(function (m) { keys[m.orig] = 1; });
    var bpKeys = Object.keys(keys).map(Number).sort(function (a, b) { return a - b; });
    var ckeys = {};
    contRules.forEach(function (c) { var r; CQ_RE.lastIndex = 0; while ((r = CQ_RE.exec(c.orig))) ckeys[ckey(+r[2], r[3])] = { v: +r[2], u: r[3] }; });
    var cKeys = Object.keys(ckeys).sort(function (a, b) { return (ckeys[a].u === 'rem' ? 16 : 1) * ckeys[a].v - (ckeys[b].u === 'rem' ? 16 : 1) * ckeys[b].v; });

    var editables = EDIT ? [].slice.call(document.querySelectorAll('[data-src]')) : [];
    var canPatch = editables.length > 0 || !!bpData;

    var host = document.createElement('div');
    host.setAttribute('data-arcs-token-tuner', '');
    var shadow = host.attachShadow({ mode: 'open' });
    shadow.innerHTML =
      '<style>' +
      ':host{all:initial}' +
      '.p{position:fixed;right:12px;bottom:12px;z-index:2147483647;width:320px;max-width:calc(100vw - 24px);max-height:calc(100vh - 24px);overflow:auto;' +
      'background:var(--surface,Canvas);color:var(--text,CanvasText);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-md,10px);font:12px/1.4 ui-monospace,Menlo,monospace}' +
      '.h{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 8px;padding:8px 10px;border-bottom:1px solid var(--border,GrayText);position:sticky;top:0;background:var(--surface,Canvas)}' +
      '.h b{letter-spacing:.12em;text-transform:uppercase;font-size:11px;color:var(--cyan,LinkText)}' +
      '.b{padding:8px 10px;display:grid;gap:10px}' +
      '.g{margin:4px 0 0;letter-spacing:.12em;text-transform:uppercase;font-size:11px;color:var(--text-secondary,GrayText)}' +
      '.r{display:grid;grid-template-columns:1fr auto auto;gap:2px 8px;align-items:center}' +
      '.r label{font:13px/1.3 system-ui,sans-serif}.r .lk{padding:1px 6px;font-size:11px}' +
      '.r input:disabled,.r select:disabled{opacity:.5;cursor:not-allowed}' +
      '.dev{border-top:1px solid var(--border,GrayText);padding:6px 10px 10px}.dev summary{cursor:pointer;color:var(--text-secondary,GrayText)}' +
      '.p.min .dev{display:none}' +
      '.r label{color:var(--text,CanvasText)}.r output{color:var(--text-secondary,GrayText);font-variant-numeric:tabular-nums}' +
      '.r input,.r select{grid-column:1 / -1;width:100%;accent-color:var(--cyan,LinkText);margin:0}' +
      '.r select{font:inherit;color:var(--text,CanvasText);background:var(--bg,Canvas);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-sm,6px);padding:3px}' +
      '.r.changed output{color:var(--gold,Highlight)}' +
      '.r.off label,.r.off output{color:var(--muted,GrayText)}' +
      '.f{display:flex;flex-wrap:wrap;gap:6px}' +
      '.c{padding:8px 10px 0;display:grid;gap:4px}' +
      'button{font:inherit;color:var(--text,CanvasText);background:var(--surface-2,Canvas);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-sm,6px);padding:5px 9px;cursor:pointer;white-space:nowrap}' +
      'button:hover{border-color:var(--cyan,LinkText)}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--cyan,LinkText);outline-offset:2px}' +
      '.out{width:100%;box-sizing:border-box;font:inherit;color:var(--text,CanvasText);background:var(--bg,Canvas);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-sm,6px);padding:5px}' +
      '.msg{color:var(--green,CanvasText);min-height:1em}' +
      '.p.min .b,.p.min .c,.p.min .f [data-act]:not([data-act=min]){display:none}' +
      '.v{display:flex;flex-wrap:wrap;gap:4px;padding:8px 10px 0}' +
      'button[aria-pressed=true]{border-color:var(--cyan,LinkText);color:var(--cyan,LinkText)}' +
      '.st{position:fixed;inset:0;z-index:2147483646;overflow:auto;background:var(--surface-2,GrayText)}' +
      '.st[hidden]{display:none}' +
      '.st iframe{display:block;margin:0 auto;height:100%;border:0;border-left:1px solid var(--border,GrayText);border-right:1px solid var(--border,GrayText);background:var(--bg,Canvas)}' +
      '.vl{display:grid;gap:4px}.vr{display:grid;grid-template-columns:1fr auto;gap:6px;align-items:center}' +
      '.vr span{color:var(--text-secondary,GrayText);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
      '.sv{color:var(--text-secondary,GrayText)}' +
      '@media print{.p,.st{display:none}}' +
      '</style>' +
      (TUNE ? '<div class="st" hidden><iframe title="This page at the chosen viewport width"></iframe></div>' : '') +
      '<div class="p" role="region" aria-label="Token tuner">' +
      '<div class="h"><b>' + (TUNE ? 'Page tuner' : 'Text editor') + '</b><span class="f">' +
      '<button type="button" data-act="back" disabled title="Undo the last change, up to 5 steps">Back</button>' +
      '<button type="button" data-act="reset">Reset</button><button type="button" data-act="min" aria-expanded="true">Hide</button></span></div>' +
      (TUNE ? '<div class="v" role="group" aria-label="Viewport">' + VPS.map(function (v) {
        return '<button type="button" data-vp="' + v[1] + '" aria-pressed="false"' + (v[1] ? ' title="' + v[1] + 'px wide"' : ' title="The window width, no frame"') + '>' + v[0] + (v[1] ? ' ' + v[1] : '') + '</button>';
      }).join('') + '<button type="button" data-act="print" aria-pressed="false" title="Apply the page\'s @media print rules">Print</button></div>' : '') +
      '<div class="c">' + (TUNE ? '<div class="sv" aria-live="off">Changes save on their own.</div><div class="sv">Double-click any text on the page to change it.</div>' : '') +
      '<div class="msg" aria-live="polite"></div></div>' +
      '<div class="b"></div>' +
      '<details class="dev"><summary>For developers</summary><div class="c">' +
      '<span class="f"><button type="button" data-act="copy">Copy CSS</button>' +
      (canPatch ? '<button type="button" data-act="copyjson">Copy JSON</button>' : '') +
      (TUNE ? '<button type="button" data-act="copytext">Copy edits</button><button type="button" data-act="export">Export versions</button>' : '') + '</span>' +
      '<input class="out" data-out="css" readonly aria-label="Changed tokens and rules as one CSS line" value="">' +
      (canPatch ? '<input class="out" data-out="json" readonly aria-label="Changed data as one JSON patch" value="">' : '') +
      (TUNE ? '<input class="out" data-out="text" readonly aria-label="Text edits as old and new pairs" placeholder="double-click text to edit it" value="">' +
        '<input class="out" data-out="versions" readonly aria-label="All versions as JSON" value=""><div class="sv" data-v="off"></div>' : '') +
      '</div></details>' +
      '</div>';

    var body = shadow.querySelector('.b');
    var out = shadow.querySelector('[data-out=css]'), outJ = shadow.querySelector('[data-out=json]'), outT = shadow.querySelector('[data-out=text]');
    var DBL = [], dbl = null;   // one list of text pairs, shared by this page and the viewport frame
    function textList() { return DBL; }
    var versions = load(VKEY) || [], saveT = null, pending = null, sv = shadow.querySelector('.sv');
    var LOCK = saved.lock || {};      // control id -> true: kept through Back, Restore and Reset
    var hist = [], backBtn = shadow.querySelector('[data-act=back]');   // the last 5 states before this one, then this one
    function sig(st) { var c = JSON.parse(JSON.stringify(st)); delete c.vp; delete c.lock; return JSON.stringify(c); }
    function showBack() { if (backBtn) { backBtn.disabled = hist.length < 2; backBtn.textContent = hist.length > 1 ? 'Back (' + (hist.length - 1) + ')' : 'Back'; } }
    function flush() {
      if (!pending) return;
      if (!hist.length || sig(hist[hist.length - 1]) !== sig(pending)) { hist.push(JSON.parse(JSON.stringify(pending))); if (hist.length > 6) hist.shift(); }
      showBack();
      var ok = store(KEY, pending); pending = null;
      if (sv) sv.textContent = ok ? 'Saved ' + new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : 'Not saved: this browser blocks storage';
    }
    var PAGE_LABELS = {};
    try { var lj = document.querySelector('script[type="application/json"][data-tune-labels]'); if (lj) PAGE_LABELS = JSON.parse(lj.textContent) || {}; } catch (e) { /* a broken map falls back to generated names */ }
    function plain(raw, fallback) { return PAGE_LABELS[raw] || fallback || raw; }
    function bpName(k) { return 'Below ' + k + ' px, ' + (k <= 480 ? 'small phone' : k <= 800 ? 'phone and small tablet' : k <= 1100 ? 'tablet and small laptop' : 'laptop'); }
    // the first few words of the element a rule styles, e.g. "If it fits the…"
    function words(sel) {
      var el = null;
      try { el = sel && document.querySelector(sel.split(',')[0]); } catch (e) {}
      var t = el ? (el.innerText || el.textContent).replace(/\s+/g, ' ').trim().split(' ') : [];   // innerText keeps the gaps between cells
      return t.length ? '"' + t.slice(0, 5).join(' ') + (t.length > 5 ? '…' : '') + '"' : '';
    }
    // a container query is named after where it lives on the page: 'Where "If it fits the…" sits, below 40 × normal'
    function contName(k) {
      var w = '';
      contRules.some(function (c) {
        var r; CQ_RE.lastIndex = 0;
        while ((r = CQ_RE.exec(c.orig))) if (ckey(+r[2], r[3]) === k) {
          [].some.call(c.rule.cssRules || [], function (s) { w = words(s.selectorText); return !!w; });
          if (w) return true;
        }
        return false;
      });
      return (w ? 'Where ' + w + ' sits, below ' : 'Card layout, below ') + show(ckeys[k].v, ckeys[k].u) + ' wide';
    }
    function lockBtn(r, id, name) {
      r.id = id;
      var b = document.createElement('button'); b.type = 'button'; b.classList.add('lk'); b.setAttribute('data-lock', id);
      b.setAttribute('aria-label', 'Lock ' + name); r.lock = b;
      r.row.insertBefore(b, r.input);
      setLock(r, !!LOCK[id], true);
    }
    function setLock(r, on, quiet) {
      if (on) LOCK[r.id] = true; else delete LOCK[r.id];
      r.input.disabled = on;
      r.lock.setAttribute('aria-pressed', String(on)); r.lock.textContent = on ? 'Locked' : 'Lock';
      r.lock.title = on ? 'Locked: Back, Restore and Reset leave this as it is. Click to unlock.' : 'Lock this value so Back, Restore and Reset leave it alone';
      if (!quiet) refresh();
    }
    addEventListener('pagehide', flush);
    var msg = shadow.querySelector('.msg');
    var rows = [], bpRows = [], wrapRows = [], showVW = function () {};
    var VP = +saved.vp || 0, stage = shadow.querySelector('.st'), frame = stage && stage.querySelector('iframe');
    var lastKeep = null;
    function frameSync() { try { if (VP && frame.contentWindow.__arcsTunerSync) frame.contentWindow.__arcsTunerSync(lastKeep); } catch (e) {} }
    function setVP(w) {
      VP = w;
      [].forEach.call(shadow.querySelectorAll('[data-vp]'), function (b) { b.setAttribute('aria-pressed', String(+b.getAttribute('data-vp') === w)); });
      if (!stage) return;
      stage.hidden = !w;
      root.style.overflow = w ? 'hidden' : '';
      if (w) {
        frame.style.width = w + 'px';
        if (!frame.getAttribute('src')) {
          var fq = /[?&]tune(=|&|$)/.test(location.search) ? location.search : (location.search ? location.search + '&tune' : '?tune');
          frame.setAttribute('src', location.pathname + fq + '&tuneframe');
          // a page that does not carry the tuner (opened from the bookmarklet) gets it injected into the frame too
          if (SELF || window.__arcsTuneSrc) frame.addEventListener('load', function () {
            try {
              var fw = frame.contentWindow, fd = frame.contentDocument;
              if (fw.__arcsTokenTuner) return;
              var s = fd.createElement('script');
              if (SELF) s.src = SELF; else { fw.__arcsTuneSrc = window.__arcsTuneSrc; s.textContent = window.__arcsTuneSrc; }
              (fd.body || fd.documentElement).appendChild(s);
            } catch (e) {}
          });
        }
      }
      showVW();
    }
    function setPrint(on) {
      PRINT = on;
      var b = shadow.querySelector('[data-act=print]'); if (b) b.setAttribute('aria-pressed', String(on));
      lists.forEach(function (o) { o._re(); });
      applyBP(); showVW();
    }
    function group(t) { var g = document.createElement('p'); g.classList.add('g'); g.textContent = t; body.appendChild(g); return g; }

    /* breadcrumbs */
    var vlist = null, vnote = null, vout = shadow.querySelector('[data-out=versions]'), voff = shadow.querySelector('[data-v=off]');
    function renderVersions() {
      if (!vlist) return;
      var older = Math.max(0, versions.length - 5);   // the newest 5 show here; every version stays in Export
      if (voff) voff.textContent = older ? older + ' older version(s) are only in Export versions.' : '';
      vlist.innerHTML = versions.slice(older).reverse().map(function (v) {
        var t = new Date(v.at), when = t.toLocaleDateString() + ' ' + t.toLocaleTimeString();
        return '<div class="vr"><span title="' + esc(v.note || '') + '">v' + v.v + ' ' + esc(when) + (v.note ? ' ' + esc(v.note) : '') + '</span>' +
          '<button type="button" data-restore="' + v.v + '">Restore</button></div>';
      }).join('') || '<span class="sv">No saved versions yet.</span>';
      vout.value = versions.length ? JSON.stringify({ page: location.pathname, versions: versions }) : '';
    }

    /* tokens */
    if (TUNE) {
      group('Size and spacing');
      var absent = [];
      SPEC.forEach(function (s) {
        var name = s[0], unit = s[1];
        var orig = declared(name);
        var n = parse(orig, unit);
        var row = document.createElement('div');
        row.classList.add('r');
        var id = 'tt' + name.replace(/[^a-z0-9]/g, '');
        if (n === null) { absent.push(name + (orig ? ' (not a ' + (unit || 'number') + ' value)' : '')); return; }   // listed under For developers
        // Anchor the step grid on the page value, so the browser never snaps it to a neighbour.
        var step = s[4], min = n - Math.floor(Math.max(0, n - s[2]) / step + 1e-9) * step, max = Math.max(s[3], n);
        var nm = plain(name, NAMES[name]);
        row.innerHTML = '<label for="' + id + '" title="' + esc(name) + '">' + esc(nm) + '</label><output></output>' +
          '<input type="range" id="' + id + '" min="' + min + '" max="' + max + '" step="' + step + '">';
        var input = row.querySelector('input'), o = row.querySelector('output');
        var r = { name: name, unit: unit, orig: n, input: input, out: o, row: row };
        input.value = (saved.tok && saved.tok[name] != null) ? saved.tok[name] : n;
        input.addEventListener('input', function () { applyTok(r); });
        rows.push(r);
        body.appendChild(row);
        lockBtn(r, 'tok:' + name, nm);
        applyTok(r, true);
      });
      if (absent.length && voff) { var ab = document.createElement('div'); ab.classList.add('sv'); ab.textContent = 'Not on this page: ' + absent.join(', '); voff.parentNode.appendChild(ab); }

      /* breakpoints */
      var vw = group('Layout switches');
      showVW = function () { vw.textContent = 'Layout switches (showing ' + (VP || root.clientWidth) + 'px wide' + (PRINT ? ', print' : '') + ')'; };
      showVW(); addEventListener('resize', showVW);
      bpKeys.forEach(function (k) {
        var row = document.createElement('div'); row.classList.add('r');
        var id = 'ttbp' + k, step = 4, min = k - Math.floor(Math.max(0, k - 360) / step) * step, max = Math.max(1440, k);
        var nm = plain(k + 'px', bpName(k));
        row.innerHTML = '<label for="' + id + '" title="' + esc('@media width ' + k + 'px' + (bpData && bpData.key === k ? ', data ' + bpData.path : '')) + '">' + esc(nm) + '</label><output></output>' +
          '<input type="range" id="' + id + '" min="' + min + '" max="' + max + '" step="' + step + '">';
        var r = { key: k, input: row.querySelector('input'), out: row.querySelector('output'), row: row };
        r.input.value = BP[k] != null ? BP[k] : k;
        r.input.addEventListener('input', function () { applyBPRow(r); });
        bpRows.push(r); body.appendChild(row); lockBtn(r, 'bp:' + k, nm); applyBPRow(r, true);
      });
      cKeys.forEach(function (k) {
        var c = ckeys[k], row = document.createElement('div'); row.classList.add('r');
        var rem = c.u === 'rem', step = rem ? 0.25 : 4, min = rem ? 10 : 160, max = Math.max(rem ? 100 : 1600, c.v);
        var nm = plain(c.v + c.u, contName(k));
        row.innerHTML = '<label for="ttbp' + k.replace('.', '_') + '" title="' + esc('@container width ' + c.v + c.u) + '">' + esc(nm) + '</label><output></output>' +
          '<input type="range" id="ttbp' + k.replace('.', '_') + '" min="' + min + '" max="' + max + '" step="' + step + '">';
        var r = { key: k, orig: c.v, unit: c.u, input: row.querySelector('input'), out: row.querySelector('output'), row: row };
        r.input.value = BP[k] != null ? BP[k] : c.v;
        r.input.addEventListener('input', function () { applyBPRow(r); });
        bpRows.push(r); body.appendChild(row); lockBtn(r, 'bp:' + k, nm); applyBPRow(r, true);
      });
      if (!bpKeys.length && !cKeys.length) { var none = document.createElement('div'); none.classList.add('r', 'off'); none.innerHTML = '<label>This page has no layout switches.</label>'; body.appendChild(none); }

      /* wrapping */
      group('Line breaks');
      var wrapStyle = document.createElement('style'); wrapStyle.setAttribute('data-arcs-token-tuner', 'wrap');
      document.head.appendChild(wrapStyle);
      WRAPS.forEach(function (w, i) {
        var row = document.createElement('div'); row.classList.add('r');
        var nm = plain(w[1], w[2]);
        row.innerHTML = '<label for="ttw' + i + '" title="' + esc(w[1] + ' { text-wrap }') + '">' + esc(nm) + '</label><output></output><select id="ttw' + i + '">' +
          WRAP_OPTS.map(function (o) { return '<option value="' + o[0] + '" title="' + (o[0] ? 'text-wrap: ' + o[0] : 'no override') + '">' + o[1] + '</option>'; }).join('') + '</select>';
        var r = { sel: w[1], input: row.querySelector('select'), out: row.querySelector('output'), row: row };
        r.input.value = (saved.wrap && saved.wrap[i]) || '';
        r.input.addEventListener('change', function () { applyWrap(); });
        wrapRows.push(r); body.appendChild(row); lockBtn(r, 'wrap:' + i, nm);
      });
      var applyWrap = function (quiet) {
        wrapStyle.textContent = wrapRows.filter(function (r) { return r.input.value; }).map(function (r) { return r.sel + '{text-wrap:' + r.input.value + '!important}'; }).join('');
        wrapRows.forEach(function (r) { r.row.classList.toggle('changed', !!r.input.value); });
        if (!quiet) refresh();
      };
      applyWrap(true);

      /* saved versions, below the controls */
      group('Saved versions');
      var bc = document.createElement('div'); bc.classList.add('vl');
      bc.innerHTML = '<input class="out" data-v="note" aria-label="Note for this version" placeholder="What changed? (optional)">' +
        '<span class="f"><button type="button" data-act="crumb">Save this version</button></span><div class="vl" data-v="list"></div>';
      body.appendChild(bc);
      vnote = bc.querySelector('[data-v=note]'); vlist = bc.querySelector('[data-v=list]');
    }

    /* in-place text */
    var base = [];
    function toMd(n) {
      var s = '';
      [].forEach.call(n.childNodes, function (c) {
        if (c.nodeType === 3) s += c.nodeValue;
        else if (c.nodeType === 1) {
          var t = c.tagName;
          if (t === 'A') s += '[' + toMd(c) + '](' + c.getAttribute('href') + ')';
          else if (t === 'STRONG' || t === 'B') s += '**' + toMd(c) + '**';
          else if (t === 'BR') s += ' ';
          else s += toMd(c);
        }
      });
      return s.replace(/‑/g, '-').replace(/ /g, ' ');
    }
    function mdToHtml(s) {
      return esc(s).replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2">$1</a>').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }
    if (editables.length) {
      var es = document.createElement('style'); es.setAttribute('data-arcs-token-tuner', 'edit');
      es.textContent = '[data-src][contenteditable]{outline:1px dashed var(--border,GrayText);outline-offset:2px;cursor:text}' +
        '[data-src][contenteditable]:hover,[data-src][contenteditable]:focus{outline:1px solid var(--cyan,LinkText)}' +
        '[data-src][data-edited]{outline:1px solid var(--gold,Highlight)}';
      document.head.appendChild(es);
      editables.forEach(function (el) {
        var b = { el: el, path: el.getAttribute('data-src'), md: toMd(el), html: el.innerHTML };
        base.push(b);
        el.setAttribute('contenteditable', 'true');
        if (saved.text && saved.text[b.path] != null && saved.text[b.path] !== b.md) el.innerHTML = mdToHtml(saved.text[b.path]);
        mark(b);
      });
      // editing inside a button or link must not toggle a fold or follow the link
      document.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('[data-src][contenteditable]'); if (t && t.closest('button,a')) { e.preventDefault(); e.stopPropagation(); } }, true);
      document.addEventListener('keydown', function (e) {
        var t = e.target.closest && e.target.closest('[data-src][contenteditable]'); if (!t) return;
        e.stopPropagation();
        if (e.key === 'Enter') e.preventDefault();               // one data string, one line
        if (e.key === 'Escape') t.blur();
      }, true);
      document.addEventListener('input', function (e) { var t = e.target.closest && e.target.closest('[data-src]'); if (t) { base.forEach(function (b) { if (b.el === t) mark(b); }); refresh(); } }, true);
    }
    function mark(b) { if (toMd(b.el) !== b.md) b.el.setAttribute('data-edited', ''); else b.el.removeAttribute('data-edited'); }

    function applyTok(r, quiet) {
      var v = parseFloat(r.input.value);
      var changed = Math.abs(v - r.orig) > 1e-9;
      if (changed) root.style.setProperty(r.name, fmt(v, r.unit));
      else root.style.removeProperty(r.name);
      r.out.textContent = show(v, r.unit) + (changed ? ' (was ' + show(r.orig, r.unit) + ')' : '');
      r.row.classList.toggle('changed', changed);
      if (!quiet) refresh();
    }
    function applyBPRow(r, quiet) {
      var o = r.orig != null ? r.orig : r.key, u = r.unit || 'px', v = parseFloat(r.input.value), changed = v !== o;
      if (changed) BP[r.key] = v; else delete BP[r.key];
      applyBP();
      r.out.textContent = show(v, u) + (changed ? ' (was ' + show(o, u) + ')' : '');
      r.row.classList.toggle('changed', changed);
      if (!quiet) refresh();
    }
    function cssLine() {
      var parts = rows.filter(function (r) { return r.row.classList.contains('changed'); })
        .map(function (r) { return r.name + ':' + fmt(parseFloat(r.input.value), r.unit) + ';'; });
      var s = parts.length ? ':root{' + parts.join('') + '}' : '';
      wrapRows.forEach(function (r) { if (r.input.value) s += r.sel + '{text-wrap:' + r.input.value + '}'; });
      var loose = bpRows.filter(function (r) { return BP[r.key] != null && !(bpData && bpData.key === r.key); });
      if (loose.length) s += '/* breakpoints, set in source: ' + loose.map(function (r) { var u = r.unit || 'px'; return (r.orig != null ? r.orig : r.key) + u + (r.unit ? ' (container)' : '') + ' to ' + BP[r.key] + u; }).join(', ') + ' */';
      return s;
    }
    function ops() {
      var o = [], seen = {};
      base.forEach(function (b) { var now = toMd(b.el); if (now !== b.md) seen[b.path] = now; });
      for (var p in seen) o.push({ op: 'replace', path: p, value: seen[p] });
      if (bpData && BP[bpData.key] != null) o.push({ op: 'add', path: bpData.path, value: BP[bpData.key] });
      return o;
    }
    function refresh() {
      out.value = cssLine();
      if (outT) { var tl = textList(); outT.value = tl.length ? JSON.stringify(tl) : ''; }
      var o = ops();
      if (outJ) outJ.value = o.length ? JSON.stringify(o) : '';
      var keep = { vp: VP, print: PRINT, tok: {}, bp: JSON.parse(JSON.stringify(BP)), wrap: wrapRows.map(function (r) { return r.input.value; }), text: {}, dbl: DBL, lock: JSON.parse(JSON.stringify(LOCK)) };
      rows.forEach(function (r) { if (r.row.classList.contains('changed')) keep.tok[r.name] = parseFloat(r.input.value); });
      base.forEach(function (b) { var now = toMd(b.el); if (now !== b.md) keep.text[b.path] = now; });
      lastKeep = keep;
      pending = keep; clearTimeout(saveT); saveT = setTimeout(flush, 400);   // autosave off the input path
      frameSync();
    }
    function say(t) { msg.textContent = t; }
    // a locked control keeps its current value; everything else takes the state's value (or the page's own)
    function restoreState(st, keepView) {
      st = st || {};
      rows.forEach(function (r) { if (LOCK[r.id]) return; r.input.value = (st.tok && st.tok[r.name] != null) ? st.tok[r.name] : r.orig; applyTok(r, true); });
      bpRows.forEach(function (r) { if (LOCK[r.id]) return; var o = r.orig != null ? r.orig : r.key; r.input.value = (st.bp && st.bp[r.key] != null) ? st.bp[r.key] : o; applyBPRow(r, true); });
      wrapRows.forEach(function (r, i) { if (!LOCK[r.id]) r.input.value = (st.wrap && st.wrap[i]) || ''; });
      if (wrapRows.length) applyWrap(true);
      if (!keepView) { setPrint(!!st.print); setVP(+st.vp || 0); }
      DBL = st.dbl || [];
      var miss = dbl ? dbl.apply(DBL) : [];
      if (miss.length) DBL = DBL.filter(function (pr) { return miss.indexOf(pr) < 0; });
      refresh();
      return miss;
    }
    function copy(t, field, done) {
      if (!t) { say('Nothing changed yet.'); return; }
      var ok = function () { say(done); };
      var fallback = function () {
        field.focus(); field.select();
        try { document.execCommand('copy') ? ok() : say('Select the line and copy it by hand.'); }
        catch (err) { say('Select the line and copy it by hand.'); }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, fallback);
      else fallback();
    }

    shadow.addEventListener('click', function (e) {
      var act = e.target && e.target.getAttribute && e.target.getAttribute('data-act');
      var vp = e.target && e.target.getAttribute && e.target.getAttribute('data-vp');
      var rv = e.target && e.target.getAttribute && e.target.getAttribute('data-restore');
      var lk = e.target && e.target.getAttribute && e.target.getAttribute('data-lock');
      if (lk != null) {
        var lr = rows.concat(bpRows, wrapRows).filter(function (x) { return x.id === lk; })[0];
        if (lr) { setLock(lr, !LOCK[lk]); say(LOCK[lk] ? 'Locked. Back, Restore and Reset will leave it alone.' : 'Unlocked.'); }
        return;
      }
      if (act === 'back') {
        flush();
        if (hist.length < 2) { say('Nothing to go back to.'); return; }
        hist.pop();
        var miss1 = restoreState(hist[hist.length - 1], true);
        hist[hist.length - 1] = JSON.parse(JSON.stringify(lastKeep));   // what the page shows now, locks included
        showBack();
        say('Went back one step' + (miss1.length ? '; ' + miss1.length + ' text edit(s) no longer match the page' : '') + '.');
        return;
      }
      if (rv != null) {
        var ver = versions.filter(function (x) { return String(x.v) === rv; })[0];
        if (ver) { var miss = restoreState(ver.state); say('Restored v' + ver.v + (miss.length ? '; ' + miss.length + ' text edit(s) no longer match the page' : '') + '.'); }
        return;
      }
      if (act === 'crumb') {
        flush();
        var n = versions.length ? versions[versions.length - 1].v + 1 : 1;
        versions.push({ v: n, at: new Date().toISOString(), note: vnote.value.trim(), why: '', state: JSON.parse(JSON.stringify(lastKeep || {})) });
        if (!store(VKEY, versions)) say('This browser blocks storage: v' + n + ' lasts until you close the page.'); else say('Saved version v' + n + '.');
        vnote.value = ''; renderVersions();
        return;
      }
      if (act === 'export') { copy(vout.value, vout, 'Copied. Save it as versions.json; --apply-text versions.json SOURCE.html applies the latest (or --version N).'); return; }
      if (vp != null) { setVP(+vp); refresh(); return; }
      if (act === 'print') { setPrint(!PRINT); refresh(); return; }
      if (act === 'min') {
        var p = shadow.querySelector('.p'), min = p.classList.toggle('min');
        e.target.textContent = min ? 'Show' : 'Hide';
        e.target.setAttribute('aria-expanded', String(!min));
      } else if (act === 'reset') {
        var nLock = Object.keys(LOCK).length;
        if (!confirm('Reset to the original page?' + (nLock ? '\n' + nLock + ' locked control(s) stay as they are.' : '') + '\nBack can undo this.')) return;
        rows.forEach(function (r) { if (LOCK[r.id]) return; r.input.value = r.orig; applyTok(r, true); });
        bpRows.forEach(function (r) { if (LOCK[r.id]) return; r.input.value = r.orig != null ? r.orig : r.key; applyBPRow(r, true); });
        wrapRows.forEach(function (r) { if (!LOCK[r.id]) r.input.value = ''; });
        if (wrapRows.length) applyWrap(true);
        base.forEach(function (b) { b.el.innerHTML = b.html; mark(b); });
        if (dbl) dbl.reset();
        DBL = [];
        refresh();
        say('Reset to the original page' + (nLock ? ', locked controls kept' : '') + '.');
      } else if (act === 'copy') {
        copy(cssLine(), out, 'Copied. Paste it after the page\'s last :root block.');
      } else if (act === 'copytext') {
        copy(outT.value, outT, 'Copied. Save it as edits.json, then run token_tuner_inline.py --apply-text edits.json SOURCE.html.');
      } else if (act === 'copyjson') {
        copy(outJ.value, outJ, 'Copied. Save it as patch.json, then run the builder with --apply patch.json.');
      }
    });

    if (TUNE) {
      dbl = dblEdit(function (list) { DBL = list; refresh(); });
      window.__arcsTunerText = function (list) { DBL = list; if (dbl) dbl.apply(list); refresh(); };
      setPrint(PRINT); setVP(VP);
      if (saved.dbl && saved.dbl.length) {
        DBL = saved.dbl; var miss0 = dbl.apply(DBL);
        if (miss0.length) { DBL = DBL.filter(function (pr) { return miss0.indexOf(pr) < 0; }); say(miss0.length + ' saved text edit(s) no longer match the page and were dropped.'); }
      }
      renderVersions();
    }
    if (frame) frame.addEventListener('load', frameSync);
    refresh();
    hist = [JSON.parse(JSON.stringify(lastKeep))]; showBack();   // Back stops at the state the page opened in
    (document.body || root).appendChild(host);
  }
})();
