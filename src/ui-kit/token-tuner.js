/* arcs-token-tuner: live layout and text controls for a page, internal only.
   ?tune  sliders bound to the page's :root tokens, one slider per CSS breakpoint, text-wrap selects.
   ?edit  every element carrying data-src="/json/pointer" becomes editable (a --tune build of a data page emits those).
   It writes CSS custom properties on <html>, rewrites the page's own @media rules, and adds one <style> for wrapping.
   "Copy CSS" gives one line to paste after the page's last :root block. "Copy JSON" gives one RFC 6902 patch for the
   page's data file (text edits, and the breakpoint when <main data-bp-src> names its field); apply it with the builder.
   Breakpoints move for JS too: in tune mode window.matchMedia is wrapped so a query such as (max-width: 1023px) follows
   the slider, which is why the inliner puts this script first in <body>, before the page's own scripts.
   Viewport: Mobile 375, Tablet 768, Desktop 1280 render the page in an iframe of the same URL (?tune&tuneframe), so
   its own @media rules and matchMedia answer to that width, not the window's; Fit drops the frame. The frame reads the
   panel's saved state and the panel pushes every change to it. Print applies the page's @media print rules (and turns
   @media screen off) so PDF layout can be tuned; @page size and margins are not simulated, so pick the width yourself.
   Inline it with scripts/token_tuner_inline.py; page_gate.py --counterpart fails any page that still carries it.
   Source of truth: src/ui-kit/token-tuner.js. Kit primitive: src/ui-kit/recoil-report/40-token-tuner.html. */
(function () {
  var Q = location.search, TUNE = /[?&]tune(=|&|$)/.test(Q), EDIT = /[?&]edit(=|&|$)/.test(Q);
  if (!TUNE && !EDIT) return;
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
  // text-wrap groups: one select each, applied with one injected rule
  var WRAPS = [['Headings', ':is(h1,h2,h3,h4)'], ['Body', ':is(p,li,dd)']];
  var root = document.documentElement;
  var KEY = 'arcsTokenTuner:' + location.pathname;
  var saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
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
  var mediaRules = [];
  function scan(rules) {
    [].forEach.call(rules || [], function (r) {
      if (r.media && r.cssRules) { mediaRules.push({ rule: r, orig: r.media.mediaText }); }
      if (r.cssRules) scan(r.cssRules);
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
  }
  if (TUNE) applyBP();

  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }

  /* ---------- frame mode: no panel; mirror the panel's saved state, re-read on every push from the parent ---------- */
  if (FRAME) {
    var wrapF = null, menusDone = false;
    window.__arcsTunerSync = function () {
      var s = {};
      try { s = JSON.parse(sessionStorage.getItem(KEY) || '{}') || {}; } catch (e) { s = {}; }
      BP = s.bp || {}; PRINT = !!s.print;
      SPEC.forEach(function (sp) {
        var v = s.tok && s.tok[sp[0]];
        if (v != null) root.style.setProperty(sp[0], fmt(v, sp[1])); else root.style.removeProperty(sp[0]);
      });
      if (!wrapF) { wrapF = document.createElement('style'); wrapF.setAttribute('data-arcs-token-tuner', 'wrap'); document.head.appendChild(wrapF); }
      wrapF.textContent = WRAPS.map(function (w, i) { var v = s.wrap && s.wrap[i]; return v ? w[1] + '{text-wrap:' + v + '!important}' : ''; }).join('');
      if (!menusDone && document.readyState !== 'loading') { collectMenus(); menusDone = true; }
      applyBP();
    };
    window.__arcsTunerSync();
    ready(window.__arcsTunerSync);
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
      '.r{display:grid;grid-template-columns:1fr auto;gap:2px 8px;align-items:center}' +
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
      '@media print{.p,.st{display:none}}' +
      '</style>' +
      (TUNE ? '<div class="st" hidden><iframe title="This page at the chosen viewport width"></iframe></div>' : '') +
      '<div class="p" role="region" aria-label="Token tuner">' +
      '<div class="h"><b>' + (TUNE ? 'Token tuner' : 'Text editor') + '</b><span class="f"><button type="button" data-act="copy">Copy CSS</button>' +
      (canPatch ? '<button type="button" data-act="copyjson">Copy JSON</button>' : '') +
      '<button type="button" data-act="reset">Reset</button><button type="button" data-act="min" aria-expanded="true">Hide</button></span></div>' +
      (TUNE ? '<div class="v" role="group" aria-label="Viewport">' + VPS.map(function (v) {
        return '<button type="button" data-vp="' + v[1] + '" aria-pressed="false"' + (v[1] ? ' title="' + v[1] + 'px wide"' : ' title="The window width, no frame"') + '>' + v[0] + (v[1] ? ' ' + v[1] : '') + '</button>';
      }).join('') + '<button type="button" data-act="print" aria-pressed="false" title="Apply the page\'s @media print rules">Print</button></div>' : '') +
      '<div class="c"><input class="out" data-out="css" readonly aria-label="Changed tokens and rules as one CSS line" value="">' +
      (canPatch ? '<input class="out" data-out="json" readonly aria-label="Changed data as one JSON patch" value="">' : '') +
      '<div class="msg" aria-live="polite"></div></div>' +
      '<div class="b"></div>' +
      '</div>';

    var body = shadow.querySelector('.b');
    var out = shadow.querySelector('[data-out=css]'), outJ = shadow.querySelector('[data-out=json]');
    var msg = shadow.querySelector('.msg');
    var rows = [], bpRows = [], wrapRows = [], showVW = function () {};
    var VP = +saved.vp || 0, stage = shadow.querySelector('.st'), frame = stage && stage.querySelector('iframe');
    function frameSync() { try { if (VP && frame.contentWindow.__arcsTunerSync) frame.contentWindow.__arcsTunerSync(); } catch (e) {} }
    function setVP(w) {
      VP = w;
      [].forEach.call(shadow.querySelectorAll('[data-vp]'), function (b) { b.setAttribute('aria-pressed', String(+b.getAttribute('data-vp') === w)); });
      if (!stage) return;
      stage.hidden = !w;
      root.style.overflow = w ? 'hidden' : '';
      if (w) {
        frame.style.width = w + 'px';
        if (!frame.getAttribute('src')) frame.setAttribute('src', location.pathname + location.search + '&tuneframe');
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

    /* tokens */
    if (TUNE) {
      group('Tokens');
      SPEC.forEach(function (s) {
        var name = s[0], unit = s[1];
        var orig = declared(name);
        var n = parse(orig, unit);
        var row = document.createElement('div');
        row.classList.add('r');
        var id = 'tt' + name.replace(/[^a-z0-9]/g, '');
        if (n === null) {
          row.classList.add('off');
          row.innerHTML = '<label>' + name + '</label><output>' + (orig ? 'not a ' + (unit || 'number') + ' value' : 'not declared') + '</output>';
          body.appendChild(row);
          return;
        }
        // Anchor the step grid on the page value, so the browser never snaps it to a neighbour.
        var step = s[4], min = n - Math.floor(Math.max(0, n - s[2]) / step + 1e-9) * step, max = Math.max(s[3], n);
        row.innerHTML = '<label for="' + id + '">' + name + '</label><output></output>' +
          '<input type="range" id="' + id + '" min="' + min + '" max="' + max + '" step="' + step + '">';
        var input = row.querySelector('input'), o = row.querySelector('output');
        var r = { name: name, unit: unit, orig: n, input: input, out: o, row: row };
        input.value = (saved.tok && saved.tok[name] != null) ? saved.tok[name] : n;
        input.addEventListener('input', function () { applyTok(r); });
        rows.push(r);
        body.appendChild(row);
        applyTok(r, true);
      });

      /* breakpoints */
      var vw = group('Breakpoints');
      showVW = function () { vw.textContent = 'Breakpoints (viewport ' + (VP || root.clientWidth) + 'px' + (PRINT ? ', print' : '') + ')'; };
      showVW(); addEventListener('resize', showVW);
      bpKeys.forEach(function (k) {
        var row = document.createElement('div'); row.classList.add('r');
        var id = 'ttbp' + k, step = 4, min = k - Math.floor(Math.max(0, k - 360) / step) * step, max = Math.max(1440, k);
        row.innerHTML = '<label for="' + id + '">' + k + 'px' + (bpData && bpData.key === k ? ' (' + bpData.path + ')' : '') + '</label><output></output>' +
          '<input type="range" id="' + id + '" min="' + min + '" max="' + max + '" step="' + step + '">';
        var r = { key: k, input: row.querySelector('input'), out: row.querySelector('output'), row: row };
        r.input.value = BP[k] != null ? BP[k] : k;
        r.input.addEventListener('input', function () { applyBPRow(r); });
        bpRows.push(r); body.appendChild(row); applyBPRow(r, true);
      });
      if (!bpKeys.length) { var none = document.createElement('div'); none.classList.add('r', 'off'); none.innerHTML = '<label>no px width queries</label>'; body.appendChild(none); }

      /* wrapping */
      group('Wrapping');
      var wrapStyle = document.createElement('style'); wrapStyle.setAttribute('data-arcs-token-tuner', 'wrap');
      document.head.appendChild(wrapStyle);
      WRAPS.forEach(function (w, i) {
        var row = document.createElement('div'); row.classList.add('r');
        row.innerHTML = '<label for="ttw' + i + '">' + w[0] + ' text-wrap</label><output></output><select id="ttw' + i + '">' +
          ['', 'balance', 'pretty', 'wrap', 'stable'].map(function (v) { return '<option value="' + v + '">' + (v || 'as the page sets it') + '</option>'; }).join('') + '</select>';
        var r = { sel: w[1], input: row.querySelector('select'), out: row.querySelector('output'), row: row };
        r.input.value = (saved.wrap && saved.wrap[i]) || '';
        r.input.addEventListener('change', function () { applyWrap(); });
        wrapRows.push(r); body.appendChild(row);
      });
      var applyWrap = function (quiet) {
        wrapStyle.textContent = wrapRows.filter(function (r) { return r.input.value; }).map(function (r) { return r.sel + '{text-wrap:' + r.input.value + '!important}'; }).join('');
        wrapRows.forEach(function (r) { r.row.classList.toggle('changed', !!r.input.value); });
        if (!quiet) refresh();
      };
      applyWrap(true);
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
      r.out.textContent = fmt(v, r.unit) + (changed ? ' (was ' + fmt(r.orig, r.unit) + ')' : '');
      r.row.classList.toggle('changed', changed);
      if (!quiet) refresh();
    }
    function applyBPRow(r, quiet) {
      var v = parseFloat(r.input.value), changed = v !== r.key;
      if (changed) BP[r.key] = v; else delete BP[r.key];
      applyBP();
      r.out.textContent = v + 'px' + (changed ? ' (was ' + r.key + 'px)' : '');
      r.row.classList.toggle('changed', changed);
      if (!quiet) refresh();
    }
    function cssLine() {
      var parts = rows.filter(function (r) { return r.row.classList.contains('changed'); })
        .map(function (r) { return r.name + ':' + fmt(parseFloat(r.input.value), r.unit) + ';'; });
      var s = parts.length ? ':root{' + parts.join('') + '}' : '';
      wrapRows.forEach(function (r) { if (r.input.value) s += r.sel + '{text-wrap:' + r.input.value + '}'; });
      var loose = bpRows.filter(function (r) { return BP[r.key] != null && !(bpData && bpData.key === r.key); });
      if (loose.length) s += '/* breakpoints, set in source: ' + loose.map(function (r) { return r.key + 'px to ' + BP[r.key] + 'px'; }).join(', ') + ' */';
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
      var o = ops();
      if (outJ) outJ.value = o.length ? JSON.stringify(o) : '';
      var keep = { vp: VP, print: PRINT, tok: {}, bp: BP, wrap: wrapRows.map(function (r) { return r.input.value; }), text: {} };
      rows.forEach(function (r) { if (r.row.classList.contains('changed')) keep.tok[r.name] = parseFloat(r.input.value); });
      base.forEach(function (b) { var now = toMd(b.el); if (now !== b.md) keep.text[b.path] = now; });
      try { sessionStorage.setItem(KEY, JSON.stringify(keep)); } catch (e) {}
      frameSync();
    }
    function say(t) { msg.textContent = t; }
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
      if (vp != null) { setVP(+vp); refresh(); return; }
      if (act === 'print') { setPrint(!PRINT); refresh(); return; }
      if (act === 'min') {
        var p = shadow.querySelector('.p'), min = p.classList.toggle('min');
        e.target.textContent = min ? 'Show' : 'Hide';
        e.target.setAttribute('aria-expanded', String(!min));
      } else if (act === 'reset') {
        rows.forEach(function (r) { r.input.value = r.orig; applyTok(r, true); });
        bpRows.forEach(function (r) { r.input.value = r.key; applyBPRow(r, true); });
        wrapRows.forEach(function (r) { r.input.value = ''; });
        if (wrapRows.length) applyWrap(true);
        base.forEach(function (b) { b.el.innerHTML = b.html; mark(b); });
        refresh();
        say('Reset to the page values.');
      } else if (act === 'copy') {
        copy(cssLine(), out, 'Copied. Paste it after the page\'s last :root block.');
      } else if (act === 'copyjson') {
        copy(outJ.value, outJ, 'Copied. Save it as patch.json, then run the builder with --apply patch.json.');
      }
    });

    if (TUNE) { setPrint(PRINT); setVP(VP); }
    if (frame) frame.addEventListener('load', frameSync);
    refresh();
    (document.body || root).appendChild(host);
  }
})();
