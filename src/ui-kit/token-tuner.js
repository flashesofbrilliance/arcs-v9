/* arcs-token-tuner: live sliders bound to the page's :root tokens. Internal only.
   Loads only when the URL carries ?tune. It writes CSS custom properties on <html> and nothing else,
   so every element that reads a token moves together and the theme toggle (a data-theme attribute) keeps working.
   "Copy CSS" puts the changed tokens on the clipboard as one :root{...} line to paste back into the page.
   Inline it with scripts/token_tuner_inline.py; page_gate.py --counterpart fails any page that still carries it.
   Source of truth: src/ui-kit/token-tuner.js. Kit primitive: src/ui-kit/recoil-report/40-token-tuner.html. */
(function () {
  if (!/[?&]tune(=|&|$)/.test(location.search)) return;
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
    ['--fs-step', 'rem', 0.9, 1.8, 0.025],
    ['--fs-body', 'rem', 0.75, 1.25, 0.0125],
    ['--lh', '', 1.1, 2.0, 0.05]
  ];
  var root = document.documentElement;
  var KEY = 'arcsTokenTuner:' + location.pathname;

  function declared(name) {
    // Read with the tuner's own override removed, so "original" means what the page ships.
    var saved = root.style.getPropertyValue(name);
    if (saved) root.style.removeProperty(name);
    var v = getComputedStyle(root).getPropertyValue(name).trim();
    if (saved) root.style.setProperty(name, saved);
    return v;
  }
  function parse(v, unit) {
    var m = /^(-?[\d.]+)([a-z%]*)$/.exec(v);
    if (!m || m[2] !== unit) return null;
    return parseFloat(m[1]);
  }
  function fmt(n, unit) { return (Math.round(n * 10000) / 10000) + unit; }

  var saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }

  var host = document.createElement('div');
  host.setAttribute('data-arcs-token-tuner', '');
  var shadow = host.attachShadow({ mode: 'open' });
  shadow.innerHTML =
    '<style>' +
    ':host{all:initial}' +
    '.p{position:fixed;right:12px;bottom:12px;z-index:2147483647;width:300px;max-width:calc(100vw - 24px);max-height:calc(100vh - 24px);overflow:auto;' +
    'background:var(--surface,Canvas);color:var(--text,CanvasText);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-md,10px);font:12px/1.4 ui-monospace,Menlo,monospace}' +
    '.h{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 10px;border-bottom:1px solid var(--border,GrayText)}' +
    '.h b{letter-spacing:.12em;text-transform:uppercase;font-size:11px;color:var(--cyan,LinkText)}' +
    '.b{padding:8px 10px;display:grid;gap:10px}' +
    '.r{display:grid;grid-template-columns:1fr auto;gap:2px 8px;align-items:center}' +
    '.r label{color:var(--text,CanvasText)}.r output{color:var(--text-secondary,GrayText);font-variant-numeric:tabular-nums}' +
    '.r input{grid-column:1 / -1;width:100%;accent-color:var(--cyan,LinkText);margin:0}' +
    '.r.changed output{color:var(--gold,Highlight)}' +
    '.r.off label,.r.off output{color:var(--muted,GrayText)}' +
    '.h{position:sticky;top:0;background:var(--surface,Canvas)}.f{display:flex;gap:6px}' +
    '.c{padding:8px 10px 0;display:grid;gap:4px}' +
    'button{font:inherit;color:var(--text,CanvasText);background:var(--surface-2,Canvas);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-sm,6px);padding:5px 9px;cursor:pointer;white-space:nowrap}' +
    'button:hover{border-color:var(--cyan,LinkText)}button:focus-visible,input:focus-visible{outline:2px solid var(--cyan,LinkText);outline-offset:2px}' +
    '.out{width:100%;box-sizing:border-box;font:inherit;color:var(--text,CanvasText);background:var(--bg,Canvas);border:1px solid var(--border,GrayText);border-radius:var(--ds-r-sm,6px);padding:5px}' +
    '.msg{color:var(--green,CanvasText);min-height:1em}' +
    '.p.min .b,.p.min .c,.p.min [data-act=copy],.p.min [data-act=reset]{display:none}' +
    '</style>' +
    '<div class="p" role="region" aria-label="Token tuner">' +
    '<div class="h"><b>Token tuner</b><span class="f"><button type="button" data-act="copy">Copy CSS</button>' +
    '<button type="button" data-act="reset">Reset</button><button type="button" data-act="min" aria-expanded="true">Hide</button></span></div>' +
    '<div class="c"><input class="out" readonly aria-label="Changed tokens as one CSS line" value="">' +
    '<div class="msg" aria-live="polite"></div></div>' +
    '<div class="b"></div>' +
    '</div>';

  var body = shadow.querySelector('.b');
  var out = shadow.querySelector('.out');
  var msg = shadow.querySelector('.msg');
  var rows = [];

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
    input.value = (saved[name] != null) ? saved[name] : n;
    input.addEventListener('input', function () { apply(r); });
    rows.push(r);
    body.appendChild(row);
    apply(r);
  });

  function apply(r) {
    var v = parseFloat(r.input.value);
    var changed = Math.abs(v - r.orig) > 1e-9;
    if (changed) root.style.setProperty(r.name, fmt(v, r.unit));
    else root.style.removeProperty(r.name);
    r.out.textContent = fmt(v, r.unit) + (changed ? ' (was ' + fmt(r.orig, r.unit) + ')' : '');
    r.row.classList.toggle('changed', changed);
    refresh();
  }
  function line() {
    var parts = rows.filter(function (r) { return r.row.classList.contains('changed'); })
      .map(function (r) { return r.name + ':' + fmt(parseFloat(r.input.value), r.unit) + ';'; });
    return parts.length ? ':root{' + parts.join('') + '}' : '';
  }
  function refresh() {
    out.value = line();
    var keep = {};
    rows.forEach(function (r) { if (r.row.classList.contains('changed')) keep[r.name] = parseFloat(r.input.value); });
    try { sessionStorage.setItem(KEY, JSON.stringify(keep)); } catch (e) {}
  }
  function say(t) { msg.textContent = t; }

  shadow.addEventListener('click', function (e) {
    var act = e.target && e.target.getAttribute && e.target.getAttribute('data-act');
    if (act === 'min') {
      var p = shadow.querySelector('.p'), min = p.classList.toggle('min');
      e.target.textContent = min ? 'Show' : 'Hide';
      e.target.setAttribute('aria-expanded', String(!min));
    } else if (act === 'reset') {
      rows.forEach(function (r) { r.input.value = r.orig; apply(r); });
      say('Reset to the page values.');
    } else if (act === 'copy') {
      var t = line();
      if (!t) { say('Nothing changed yet.'); return; }
      var done = function () { say('Copied. Paste it after the page\'s last :root block.'); };
      var fallback = function () {
        out.focus(); out.select();
        try { document.execCommand('copy') ? done() : say('Select the line and copy it by hand.'); }
        catch (err) { say('Select the line and copy it by hand.'); }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(done, fallback);
      else fallback();
    }
  });

  (document.body || root).appendChild(host);
})();
