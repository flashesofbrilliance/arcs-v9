/* tabbed-brief template behaviour (2026-11-09). Needs kit 42 shnavInit loaded first. Interaction rules: src/ui-kit/tabbed-brief/README.md */
(function () {
  var doc = document.documentElement, root = document.querySelector('.tb'), KEY = (root && root.getAttribute('data-store')) || 'tbTheme';
  var DEF = (root && root.getAttribute('data-default-theme')) === 'dark' ? 'dark' : 'light';
  var reduce = function () { return matchMedia('(prefers-reduced-motion: reduce)').matches; };

  /* header controls (kit 51): theme switch + reading options, one saved object per page, the page's default theme until the reader picks one */
  var st = {}; try { var raw = localStorage.getItem(KEY) || ''; st = raw.charAt(0) === '{' ? JSON.parse(raw) : (raw ? { theme: raw } : {}); } catch (e) {}
  var ATTR = { font: 'data-font', size: 'data-size', space: 'data-space' };
  var tg = document.querySelector('.dprefs-theme'), aa = document.querySelector('.dprefs-aa'), panel = aa && document.getElementById(aa.getAttribute('aria-controls'));
  function save() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  function applyPrefs() {
    var th = st.theme || DEF; doc.setAttribute('data-theme', th === 'dark' ? 'dark' : 'light');
    for (var k in ATTR) { var v = st[k]; if (v && v !== 'std') doc.setAttribute(ATTR[k], v); else doc.removeAttribute(ATTR[k]); }
    if (tg) tg.setAttribute('aria-pressed', String(th === 'dark'));
    if (panel) [].forEach.call(panel.querySelectorAll('button[data-k]'), function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === (st[b.getAttribute('data-k')] || 'std'))); });
  }
  function place() { var r = aa.getBoundingClientRect(), vw = doc.clientWidth; panel.style.top = Math.round(r.bottom + 8) + 'px'; panel.style.right = Math.max(16, Math.min(Math.round(vw - r.right), vw - panel.offsetWidth - 16)) + 'px'; }
  function openPrefs(o) { panel.hidden = !o; aa.setAttribute('aria-expanded', String(o)); if (o) { place(); (panel.querySelector('button[aria-pressed="true"]') || panel.querySelector('button')).focus(); } else aa.focus(); }
  if (tg) tg.addEventListener('click', function () { st.theme = (st.theme || DEF) === 'dark' ? 'light' : 'dark'; save(); applyPrefs(); });
  if (aa && panel) {
    aa.addEventListener('click', function () { openPrefs(panel.hidden); });
    panel.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.hasAttribute('data-close')) openPrefs(false);
      else if (b.hasAttribute('data-reset')) { st = {}; save(); applyPrefs(); }
      else if (b.getAttribute('data-k')) { st[b.getAttribute('data-k')] = b.getAttribute('data-v'); save(); applyPrefs(); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) openPrefs(false); });
    addEventListener('resize', function () { if (!panel.hidden) place(); });
    addEventListener('scroll', function () { if (!panel.hidden) place(); }, { passive: true });
  }
  applyPrefs();

  /* fold sections: button inside the heading toggles its body */
  function setFold(btn, open) { btn.setAttribute('aria-expanded', String(open)); var b = document.getElementById(btn.getAttribute('aria-controls')); if (b) b.hidden = !open; syncExpand(); }
  var folds = [].slice.call(document.querySelectorAll('.tb-fold-btn'));
  folds.forEach(function (b) { b.addEventListener('click', function () { setFold(b, b.getAttribute('aria-expanded') !== 'true'); }); });

  /* role sections: on wide screens a tab shows one; below the breakpoint each role is a fold */
  var seats = [].slice.call(document.querySelectorAll('.seat-btn'));
  var stacked = false;
  function setSeat(btn, open) { btn.setAttribute('aria-expanded', String(open)); var b = document.getElementById(btn.getAttribute('aria-controls')); if (b) b.hidden = !open; syncExpand(); }
  seats.forEach(function (b) { b.addEventListener('click', function () { if (stacked) setSeat(b, b.getAttribute('aria-expanded') !== 'true'); }); });

  /* expand all: every fold, plus the role sections while they are folds */
  var ex = document.getElementById('tb-expand');
  function group() { return folds.concat(stacked ? seats : []); }
  function syncExpand() { if (!ex) return; var all = group().every(function (b) { return b.getAttribute('aria-expanded') === 'true'; });
    ex.textContent = all ? 'Collapse all' : 'Expand all'; ex.setAttribute('aria-pressed', String(all)); }
  if (ex) ex.addEventListener('click', function () { var all = ex.getAttribute('aria-pressed') === 'true';
    group().forEach(function (b) { (seats.indexOf(b) > -1 ? setSeat : setFold)(b, !all); }); });

  /* jumps: clear the sticky head (meta strip and nav) by 12px; respect reduced motion */
  var nav = document.querySelector('.tb-head') || document.querySelector('.tb-navwrap');
  function cover() { return nav ? nav.getBoundingClientRect().height : 0; }
  function jumpTo(el, how) { if (!el) return; var y = el.getBoundingClientRect().top + scrollY - cover() - 12; scrollTo({ top: Math.max(0, y), behavior: how || (reduce() ? 'auto' : 'smooth') }); }
  var booting = true; addEventListener('load', function () { setTimeout(function () { booting = false; }, 0); });
  function setHash(h) { if (booting) return; try { history.replaceState(null, '', h ? '#' + h : location.pathname + location.search); } catch (e) {} }

  /* panes and the kit 42 nav */
  var panes = [].slice.call(document.querySelectorAll('.tb-pane'));
  var first = panes[0] ? panes[0].id : '';
  var cur = first; var h0 = location.hash.slice(1);
  if (h0 && document.getElementById('pane-' + h0)) cur = 'pane-' + h0;
  function show(id) { cur = id; panes.forEach(function (p) { p.hidden = p.id !== id; }); }
  var shnav = document.getElementById('shnav');
  var pagesMode = !!(root && root.getAttribute('data-pages') === '1'); /* one pane per page: the nav is links, roles never fold */
  var api = window.shnavInit && shnavInit(shnav, {
    links: pagesMode,
    onMode: function (m) {
      stacked = m === 'menu' && !pagesMode; doc.classList.toggle('stacked', stacked);
      seats.forEach(function (b) { if (stacked) { b.removeAttribute('aria-disabled'); b.tabIndex = 0; setSeat(b, b.getAttribute('aria-expanded') !== 'false'); }
        else { b.setAttribute('aria-disabled', 'true'); b.tabIndex = -1; setSeat(b, true); } });
      if (stacked) panes.forEach(function (p) { p.hidden = false; });
      else if (!pagesMode) { show(cur); var t = shnav.querySelector('[data-target="' + cur + '"]'); if (t) t.click(); } /* in pages mode a click is a navigation: never synthesize one */
      syncExpand();
    },
    onPick: function (t, isMenu) {
      if (pagesMode) return;
      setHash(t === first ? '' : t.replace(/^pane-/, ''));
      if (!isMenu) { show(t); var body = document.querySelector('.tb-body'); if (body && body.getBoundingClientRect().top < cover()) jumpTo(body, 'auto'); return; }
      if (t === first) { scrollTo({ top: 0, behavior: reduce() ? 'auto' : 'smooth' }); return; }
      var p = document.getElementById(t), b = p && p.querySelector('.seat-btn');
      if (b) setSeat(b, true); jumpTo(p); if (b) b.focus({ preventScroll: true });
    }
  });

  /* actions: a tab target or a section target, from data */
  function openSection(id, how) { var s = document.getElementById(id); if (!s) return; var b = s.querySelector('.tb-fold-btn'); if (b) setFold(b, true); setHash(id); jumpTo(s, how); }
  [].forEach.call(document.querySelectorAll('[data-go-tab]'), function (a) { a.addEventListener('click', function (e) { e.preventDefault();
    var t = shnav.querySelector('[data-target="pane-' + a.getAttribute('data-go-tab') + '"]'); if (t) t.click(); }); });
  [].forEach.call(document.querySelectorAll('[data-go-section]'), function (a) { a.addEventListener('click', function (e) { e.preventDefault(); openSection(a.getAttribute('data-go-section')); }); });

  /* a hash on load: a section, or a role on narrow screens (wide screens already showed the tab) */
  addEventListener('load', function () { var h = location.hash.slice(1); if (!h) return;
    if (document.getElementById(h) && document.getElementById(h).classList.contains('tb-fold')) { openSection(h, 'auto'); return; }
    var p = document.getElementById('pane-' + h); if (p && stacked) { var b = p.querySelector('.seat-btn'); if (b) setSeat(b, true); jumpTo(p, 'auto'); } });
  addEventListener('beforeprint', function () { panes.forEach(function (p) { p.hidden = false; }); group().forEach(function (b) { (seats.indexOf(b) > -1 ? setSeat : setFold)(b, true); }); });
  syncExpand();
})();
