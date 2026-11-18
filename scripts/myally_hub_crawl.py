#!/usr/bin/env python3
"""myally_hub_crawl.py: unit checks and an interaction crawl for public/myally-hub.html.

Two layers, both read-only:
  1. Unit checks on the Step 1 tree (out/step1_tree.json): parents exist, every row fits the
     day columns, every "Your week" id exists and starts on its day, hours add up to the fee's hours, every kind has an icon and a legend entry.
  2. A headless crawl (Playwright + installed Chrome, found the same way page_gate.py finds them)
     at 375, 800 and 1280 px: every tab shows one panel; locked tabs show only the note and hold no
     content; every Step 1 row
     opens its own details; clicking a workstream keeps it open, the twisty closes it; every chip
     navigates; Close all / Open all work; arrow keys move focus; the day columns fill the grid
     and every bar sits inside them; no page-level horizontal overflow; every control inside the
     embedded Debrief and Primer pages clicks without a script error.

  python3 scripts/myally_hub_crawl.py            # both layers
  python3 scripts/myally_hub_crawl.py --unit     # layer 1 only (fast, no browser)

Exit 1 on any failure. Stdlib only; the browser step shells out to node + playwright.
"""
import functools, http.server, json, os, re, subprocess, sys, tempfile, threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUB = os.environ.get("MYALLY_HUB_PUBLIC", os.path.join(ROOT, "public"))  # override to crawl another copy (proves the checks fail on a bad page)
HUB = os.path.join(PUB, "myally-hub.html")
TREE = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld", "out", "step1_tree.json")
REC = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld", "engagement.json")
LOCKED = ["t-prop", "t-plan"]  # content off the site during Step 1 (Zach, 2026-11-08); tabs show a note


def unit() -> list:
    fails = []
    tree = json.load(open(TREE, encoding="utf-8"))
    rec = json.load(open(REC, encoding="utf-8"))
    hub = open(HUB, encoding="utf-8").read()
    rows, cols = tree["rows"], len(tree["weeks"])
    ids = {r["id"] for r in rows}
    for r in rows:
        if r["parent"] is not None and r["parent"] not in ids:
            fails.append(f"row {r['id']}: parent {r['parent']} missing")
        if r["start"] < 0 or r["start"] + max(r["len"], 1) > cols:
            fails.append(f"row {r['id']}: start {r['start']} len {r['len']} runs past {cols} columns")
        if r["kind"] == "ms" and r["len"] != 0:
            fails.append(f"row {r['id']}: a milestone has len 0")
        pf = r.get("proof")
        if pf is not None and (set(pf) != {"lead", "url", "label"} or not pf["url"].startswith("https://") or not pf["lead"].strip()):
            fails.append(f"row {r['id']}: proof needs lead, an https url and a label")
    # "Your week" (step1_tree.week) summarizes rows by day: every id it cites must exist and start on that day,
    # so the plain sentence cannot drift from the grid it stands in for (2026-11-09).
    byid = {r["id"]: r for r in rows}
    days = [w.get("day") for w in tree.get("week", [])]
    if days != list(range(cols)):
        fails.append(f"week: days are {days}, want one entry per column 0..{cols - 1}")
    for w in tree.get("week", []):
        if not w.get("text") or not w.get("ids"):
            fails.append(f"week day {w.get('day')}: needs text and ids")
        for i in w.get("ids", []):
            if i not in byid:
                fails.append(f"week day {w.get('day')}: row {i} does not exist")
            elif byid[i]["start"] != w.get("day"):
                fails.append(f"week day {w.get('day')}: row {i} starts on day {byid[i]['start']}")
    work = sum(r.get("hours", 0) for r in rows if r["parent"] and r["kind"] in ("task", "ms"))
    want = rec["fields"]["hours_step1"]["value"]
    if abs(work - want) > 1e-9:
        fails.append(f"hours add up to {work}, Step 1 is {want}")
    icons = set(re.findall(r'<symbol id="i-([a-z]+)"', hub))
    alias = {"oh": "gift"}
    for k in {r["kind"] for r in rows}:
        if alias.get(k, k) not in icons:
            fails.append(f"kind {k}: no icon symbol")
        if k != "phase" and f'class="ico c-{k}"' not in hub:
            fails.append(f"kind {k}: no legend entry")
    # Later-phase pricing stays off the site until that phase is signed (Zach, 2026-11-08). An allowlist, not a
    # threshold: a $10,000 floor let "$8,500 audit" through (2026-11-09). Every figure of $1,000 or more must be
    # one the client already has in writing: a step ($1,500), all three steps ($4,500), their ceiling ($5,000).
    # Checked on the decoded page, embedded copies included.
    import html as _h
    allowed = {"$1,500", "$4,500", "$5,000"}
    big = sorted({m for m in re.findall(r"\$\d{1,3}(?:,\d{3})+", _h.unescape(_h.unescape(hub))) if m not in allowed})
    if big:
        fails.append("pricing not on the allowlist (later-phase figures?): " + ", ".join(big[:8]))
    # An embedded page must not show its own top bar inside the hub: a second wordmark, theme toggle, menu and
    # an MNDA link to a locked tab (Zach saw it on the Primer tab, 2026-11-09). myally_primer_terms.py adds the
    # data-embed="hub" style that hides it.
    for m in re.finditer(r'<iframe title="([^"]+)" srcdoc="([^"]*)"', hub):
        doc = _h.unescape(m.group(2))
        if '<header class="top"' in doc and 'data-embed="hub"' not in doc:
            fails.append(f"embedded {m.group(1)}: its own top bar shows inside the hub (missing the data-embed hide)")
    return fails


CRAWL_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [url, exe] = process.argv.slice(2);
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const fails = [];
  for (const width of [375, 800, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    page.on('pageerror', e => fails.push(`${width}: page error: ${e.message}`));
    page.on('frameattached', f => f.page().on('pageerror', () => {}));
    await page.goto(url);
    await page.waitForTimeout(300);
    const r = await page.evaluate(async ([LOCKED, UNLOCK, GLOSS]) => {
      const lockOpen = () => false;
      const out = [], sleep = ms => new Promise(r => setTimeout(r, ms));
      const errs = [];
      const hook = w => w.addEventListener('error', e => errs.push(e.message));
      // tabs
      const tabs = [...document.querySelectorAll('[role=tab]')];
      const shown = () => [...document.querySelectorAll('[role=tabpanel]')].filter(p => !p.hidden).map(p => p.id);
      for (const id of LOCKED) {
        const t = document.getElementById(id);
        if (!t || t.hidden) { out.push(`locked tab ${id} is missing or hidden (it should show with a lock)`); continue; }
        if (!t.querySelector('.lk')) out.push(`locked tab ${id} has no lock icon`);
      }
      for (const t of tabs.filter(t => !t.hidden)) {
        t.click(); await sleep(150);
        const want = LOCKED.includes(t.id) ? 'pane-lock' : t.getAttribute('aria-controls');
        const vis = shown();
        if (vis.length !== 1 || vis[0] !== want) out.push(`tab ${t.id}: panels shown ${vis.join(',')}, want ${want}`);
      }
      // a message or link to a locked tab shows the lock note, never the content
      for (const k of ['prop', 'plan']) {
        window.postMessage({ alyceTab: k }, '*'); await sleep(120);
        const vis = shown();
        if (vis.includes('pane-prop') || vis.includes('pane-plan')) out.push(`message alyceTab:${k} opened locked content`);
      }
      // the locked tabs hold no content: Proposal's frame is empty and Timeline has no rows
      const pf = document.querySelector('#pane-prop iframe');
      if (pf && pf.contentDocument && pf.contentDocument.body && pf.contentDocument.body.innerText.trim()) out.push('Proposal frame still has content');
      if (document.querySelectorAll('#pane-plan .row[data-id]').length) out.push('Timeline still has rows');
      document.getElementById('t-s1').click(); await sleep(100);
      // The agreement and Discuss live in one place: an "Agreement" menu in the header (desktop), the same group in the
      // hamburger menu (phones). Four links (PDF, Word, shared doc, Discuss), 44px targets, an accessible name each.
      const phone = innerWidth <= 560;
      let acts = [];
      if (phone) {
        const bg = document.getElementById('burger'); if (bg) { bg.click(); await sleep(150); }
        const g = document.querySelector('.shell-bar .menuacts');
        if (!g || getComputedStyle(g).display === 'none') out.push('phone menu has no Agreement group');
        acts = [...document.querySelectorAll('.shell-bar .menuacts a')];
      } else {
        const ab = document.querySelector('.shell-meta .agb');
        if (!ab) out.push('header has no Agreement menu button');
        else { ab.click(); await sleep(120); if (ab.getAttribute('aria-expanded') !== 'true') out.push('Agreement menu does not open'); }
        acts = [...document.querySelectorAll('#agrmenu a')];
      }
      if (acts.length !== 4) out.push(`agreement actions: ${acts.length}, want 4`);
      for (const a of acts) { const b = a.getBoundingClientRect(); if (b.height < 43.5) out.push(`agreement action "${a.getAttribute('aria-label')}" under 44px`); if (!a.getAttribute('href')) out.push('agreement action without a link'); }
      if (!acts.some(a => /^Discuss/.test(a.getAttribute('aria-label') || ''))) out.push('no Discuss call to action');
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); document.body.click(); await sleep(80);
      // the Now note dismisses; the strip shows a "Not started" pill until work starts, then shows a day progressbar
      if (!document.querySelector('#pane-s1>.stamp .stamp-x[aria-label]')) out.push('Now note has no dismiss button');
      const strip = document.getElementById('s1prog');
      if (!strip) out.push('no progress strip');
      else if (!strip.querySelector('[role=progressbar][aria-valuenow]') && !/Not started/i.test(strip.textContent)) out.push('progress strip shows neither a progressbar nor "Not started."');
      // "Your week" leads; the grid sits in a closed disclosure that opens to a working grid
      const all = document.getElementById('s1all');
      if (!all || all.open) out.push('"See every item" is missing or open by default');
      if (document.querySelectorAll('#s1wk li').length !== 6) out.push('"Your week" does not list six days');
      const sm = all && all.querySelector('summary');
      if (sm && sm.getBoundingClientRect().height < 44) out.push('"See every item" is under 44px tall');
      if (all) { all.open = true; await sleep(120); }
      const g = document.getElementById('s1g'), det = document.getElementById('s1detail');
      // every row opens its own details; clicking a workstream keeps it open
      const ids = [...g.querySelectorAll('.row[data-id]')].map(r => r.dataset.id);
      for (const id of ids) {
        const row = document.getElementById('s1r-' + id);
        if (!row) { out.push(`row ${id} vanished after clicking an earlier row`); continue; }
        row.querySelector('.tx').click(); await sleep(15);
        const h = det.querySelector('h2'), lab = row.querySelector('.tx').childNodes[0].textContent.trim();
        if (!h || h.textContent.trim() !== lab) out.push(`row ${id}: details show "${h && h.textContent.trim()}"`);
        const now = document.getElementById('s1r-' + id);
        if (now && now.getAttribute('aria-expanded') === 'false') out.push(`row ${id}: clicking the workstream closed it`);
      }
      // 961px and up: details are a card pinned bottom-right; Escape and the close button shut it and focus returns to the row
      if (innerWidth >= 961) {
        const r0 = () => document.getElementById('s1r-' + ids[0]);  // re-query: every redraw replaces the rows
        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); await sleep(30);
        if (det.classList.contains('on')) out.push('sheet: Escape did not close it');
        if (document.activeElement !== document.getElementById('s1r-' + ids[ids.length - 1])) out.push('sheet: focus did not return to the row');
        r0().querySelector('.tx').click(); await sleep(450);
        const dr = det.getBoundingClientRect();
        if (!det.classList.contains('on')) out.push('sheet: choosing a row did not open it');
        if (!det.contains(document.activeElement)) out.push('sheet: focus did not move into it');
        if (dr.right > innerWidth + 1 || dr.bottom > innerHeight + 1 || dr.width < 320 || dr.width > 460 || dr.height > innerHeight / 2 + 1) out.push(`sheet: ${Math.round(dr.width)}x${Math.round(dr.height)} at ${Math.round(dr.left)},${Math.round(dr.top)}; want 320 to 460px wide, at most half the window tall, inside it`);
        const cb = det.querySelector('[data-close]'), cr = cb && cb.getBoundingClientRect();
        if (!cr || cr.width < 44 || cr.height < 44) out.push('sheet: close button missing or under 44px');
        cb && cb.click(); await sleep(30);
        if (det.classList.contains('on')) out.push('sheet: close button did not close it');
        r0().querySelector('.tx').click(); await sleep(30);
      } else if (getComputedStyle(det).position === 'fixed') out.push('details are a sheet below 961px');
      // The details card is plain text (Zach, 2026-11-09: definitions there fought the row hover). None may appear.
      for (const id of ids) {
        const row = document.getElementById('s1r-' + id); if (!row) continue;
        row.querySelector('.tx').click(); await sleep(10);
        if (det.querySelector('.dfn,.termwrap,.pd-terms')) out.push(`details for ${id}: carries a definition; the card is plain text`);
      }
      if (!document.querySelector('#pane-s1 .dfn')) out.push('no hover definitions found on the Step 1 tab');
      // First use: on every surface of the Step 1 tab, the first use of each Primer term (TERMS in
      // myally_primer_terms.py, carried in the hub's GLOSS block) must be a definition. Text inside buttons, links,
      // summaries, tile labels and figures is skipped (no control inside a control), and the details card is plain
      // text by design. The grid rows are controls.
      const SKIP = 'a,button:not(.dfn),summary,.tip,.glab,.gf,.wd,.vh,.stamp-vh,.pill,#s1g,#s1dh,.pd-kind';
      const RX = Object.entries(GLOSS).map(([gid, ph]) => [gid, new RegExp('(^|[^\\w/-])(' + ph.map(p => p.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&')).join('|') + ')(?![\\w/-])', 'i')]);
      const firstUse = (root, where) => {
        if (!root) return;
        const done = new Set();
        const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: n => n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
        while (w.nextNode()) {
          const n = w.currentNode, d = n.parentElement.closest('.dfn');
          for (const [gid, re] of RX) {
            if (done.has(gid) || !re.test(n.nodeValue)) continue;
            if (d && d.dataset.gid !== gid) continue;  // inside a longer term's definition ("database" in "Database rules")
            done.add(gid);
            if (!d) out.push(`${where}: first use of "${n.nodeValue.match(re)[2]}" has no definition`);
          }
        }
      };
      firstUse(document.querySelector('#pane-s1>.stamp'), 'Now note');
      firstUse(document.getElementById('s1sum'), 'tiles');
      firstUse(document.querySelector('.s1week'), 'Your week');
      firstUse(document.getElementById('s1plan'), 'The whole plan');
      firstUse(document.getElementById('s1prog'), 'Where things stand');
      det.querySelector('[data-back]')?.click(); await sleep(15);
      // definitions outside the details card open by click (tap), stay inside the window and close on Escape
      for (const b of [...document.querySelectorAll('#pane-s1 .dfn')].filter(b => !det.contains(b) && b.offsetParent)) {
        b.click(); await sleep(10);
        const t = b.nextElementSibling, tr = t.getBoundingClientRect();
        if (t.hidden) out.push(`"${b.textContent}": definition did not open`);
        else if (tr.left < -1 || tr.right > document.documentElement.clientWidth + 1) out.push(`"${b.textContent}": definition spills out of the window`);
        if (!b.getAttribute('aria-describedby') || document.getElementById(b.getAttribute('aria-describedby')) !== t) out.push(`"${b.textContent}": not described by its definition`);
        b.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true })); await sleep(10);
        if (!t.hidden) out.push(`"${b.textContent}": Escape did not close it`);
      }
      // twisty closes and reopens
      const ph = g.querySelector('.row.l0'), pid = ph.dataset.id;
      ph.querySelector('.tw').dispatchEvent(new MouseEvent('click', { bubbles: true })); await sleep(15);
      if (document.getElementById('s1r-' + pid).getAttribute('aria-expanded') !== 'false') out.push('twisty did not close the workstream');
      document.getElementById('s1r-' + pid).querySelector('.tw').dispatchEvent(new MouseEvent('click', { bubbles: true })); await sleep(15);
      // chips (re-query after each redraw)
      det.querySelector('[data-back]')?.click(); await sleep(15);
      const chipIds = [...det.querySelectorAll('[data-go]')].map(c => c.dataset.go);
      for (const id of chipIds) {
        det.querySelector(`[data-go="${id}"]`)?.click(); await sleep(15);
        const want = document.getElementById('s1r-' + id)?.querySelector('.tx').childNodes[0].textContent.trim();
        if (det.querySelector('h2')?.textContent.trim() !== want) out.push(`chip ${id} did not open its row`);
        det.querySelector('[data-back]')?.click(); await sleep(15);
      }
      // close all / open all
      const tog = document.getElementById('s1tog');
      tog.click(); await sleep(15); const closed = g.querySelectorAll('.row.l1').length;
      tog.click(); await sleep(15); const opened = g.querySelectorAll('.row.l1').length;
      if (closed !== 0 || opened === 0) out.push(`Close all/Open all: ${closed} then ${opened} rows`);
      // keyboard
      const first = g.querySelector('.row[data-id]'); first.focus();
      first.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true })); await sleep(15);
      if (document.activeElement === first) out.push('ArrowDown did not move focus');
      // columns fill the grid; bars sit inside the columns
      const wk = [...g.querySelectorAll('.wk')].map(w => w.getBoundingClientRect());
      const wrap = g.closest('.wrap'), inner = wrap.getBoundingClientRect().left + wrap.clientLeft + wrap.clientWidth;
      if (wrap.scrollWidth <= wrap.clientWidth && inner - wk[wk.length - 1].right > 8) out.push(`blank strip ${Math.round(inner - wk[wk.length - 1].right)}px right of the last day`);
      for (const b of g.querySelectorAll('.b,.pt')) {
        const bb = b.getBoundingClientRect();
        if (bb.right > wk[wk.length - 1].right + 2 || bb.left < wk[0].left - 2) out.push(`bar outside the day columns on row ${b.closest('.row').dataset.id}`);
      }
      if (document.documentElement.scrollWidth > innerWidth + 1) out.push(`page scrolls sideways (${document.documentElement.scrollWidth}px)`);
      // embedded pages: click every visible control
      for (const t of ['t-debrief', 't-primer']) {
        const tb = document.getElementById(t); if (!tb || tb.hidden) continue;
        tb.click(); await sleep(400);
        const f = document.querySelector('#' + tb.getAttribute('aria-controls') + ' iframe');
        hook(f.contentWindow);
        for (const b of [...f.contentDocument.querySelectorAll('button,summary,[role=tab]')]) { if (b.offsetParent) { b.click(); await sleep(5); } }
        if (t === 't-primer') {
          const gls = [...f.contentDocument.querySelectorAll('a.gl')];
          if (!gls.length) out.push('Primer: no hover definitions');
          for (const g of gls) { g.click(); await sleep(10); const tp = g.parentNode.querySelector('.tip'); if (!tp || tp.hidden) out.push(`Primer: definition for "${g.textContent}" did not open`); g.click(); await sleep(5); }
        }
        for (const a of f.contentDocument.querySelectorAll('a[href^="#"]')) {
          const h = a.getAttribute('href'); if (h.length > 1 && !f.contentDocument.getElementById(decodeURIComponent(h.slice(1)))) out.push(`${t}: dead link ${h}`);
        }
      }
      document.getElementById('t-s1').click(); await sleep(100);
      // reading options (the "Aa" control): largest text, roomy spacing and the easy-read font reach the new
      // pieces with nothing clipped, no sideways scroll, 44px targets and the sheet still scrolling
      const de = document.documentElement;
      de.setAttribute('data-size', 'xl'); de.setAttribute('data-space', 'roomy'); de.setAttribute('data-font', 'easy');
      document.getElementById('s1all').open = true; await sleep(150);
      document.getElementById('s1r-' + ids[0])?.querySelector('.tx').click(); await sleep(450);
      const ro = [];
      if (de.scrollWidth > innerWidth + 1) ro.push(`page scrolls sideways (${de.scrollWidth}px)`);
      for (const el of document.querySelectorAll('#s1prog .s1si, .shell-bar .menuacts a, #agrmenu a, .s1sum .glab, .s1week li, .s1week .wt, #s1all>summary, #s1detail h2, #s1detail h3, #s1detail .pd-list button, #s1detail .pd-x, #s1detail .pd-ok button')) {
        if (el.scrollWidth > el.clientWidth + 1) ro.push(`clipped text in ${el.className || el.tagName}: "${el.textContent.trim().slice(0, 30)}"`);
      }
      for (const el of document.querySelectorAll('#s1all>summary, #s1detail .pd-list button, #s1detail .pd-ok button, #s1detail [data-close]')) {
        const b = el.getBoundingClientRect(); if (b.width && b.height < 44 - 0.5) ro.push(`target under 44px: "${(el.textContent.trim() || el.getAttribute('aria-label') || '').slice(0, 30)}" ${Math.round(b.height)}px`);
      }
      for (const q of ['.s1week li', '#s1detail h2', '#s1detail .pd-list button']) {
        const el = document.querySelector(q); if (el && !/verdana/i.test(getComputedStyle(el).fontFamily)) ro.push(`${q} ignores the easy-read font`);
      }
      if (innerWidth >= 961) {
        const dr = det.getBoundingClientRect();
        // the header stays pinned; the body under it is what scrolls
        const sb = det.querySelector('.pd-b') || det;
        if (getComputedStyle(sb).overflowY !== 'auto' || dr.bottom > innerHeight + 1 || dr.height > innerHeight / 2 + 1 || sb.scrollHeight <= sb.clientHeight) ro.push(`sheet does not scroll inside the window (body overflow ${getComputedStyle(sb).overflowY}, bottom ${Math.round(dr.bottom)} of ${innerHeight}, ${det.className}, ${getComputedStyle(det).position})`);
      }
      ro.forEach(x => out.push('reading options: ' + x));
      ['data-size', 'data-space', 'data-font'].forEach(k => de.removeAttribute(k));
      return out.concat(errs.map(e => 'script error: ' + e));
    }, [JSON.parse(process.env.LOCKED), JSON.parse(process.env.UNLOCK), JSON.parse(process.env.GLOSS)]);
    r.forEach(x => fails.push(`${width}px: ${x}`));
    await page.close();
  }
  await browser.close();
  console.log(JSON.stringify(fails));
})().catch(e => { console.error(e.message); process.exit(2); });
"""


def crawl() -> list:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import page_gate  # reuse its playwright + Chrome discovery
    paths = page_gate.node_path()
    if not paths:
        print("warn: crawl skipped, playwright not installed (repo, main checkout or global); unit checks only")
        return []
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=PUB)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/myally-hub.html"
    exe = page_gate.BROWSERS.get("chrome") if sys.platform == "darwin" and os.path.exists(page_gate.BROWSERS.get("chrome", "")) else ""
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as fh:
        fh.write(CRAWL_JS)
    try:
        hub = open(HUB, encoding="utf-8").read()
        gl = json.loads(re.search(r"/\*GLOSS:BEGIN\*/(.*?)/\*GLOSS:END\*/", hub, re.S).group(1).replace("<\\/", "</"))
        env = dict(os.environ, NODE_PATH=paths[0], LOCKED=json.dumps(LOCKED), UNLOCK="{}", GLOSS=json.dumps({k: v["p"] for k, v in gl.items()}))
        r = subprocess.run(["node", fh.name, url, exe], capture_output=True, text=True, env=env, timeout=300)
    finally:
        os.unlink(fh.name)
        srv.shutdown()
    if r.returncode != 0:
        return [f"crawl failed to run: {(r.stderr.strip().splitlines() or ['?'])[0]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    fails = unit()
    if "--unit" not in sys.argv:
        fails += crawl()
    for f in fails:
        print("✖", f)
    print(f"myally_hub_crawl: {'FAIL' if fails else 'OK'} ({len(fails)} problem(s))")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
