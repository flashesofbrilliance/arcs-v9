#!/usr/bin/env python3
"""myally_hub_crawl.py: unit checks and an interaction crawl for public/myally-hub.html.

Two layers, both read-only:
  1. Unit checks on the Step 1 tree (out/step1_tree.json): parents exist, every row fits the
     day columns, hours add up to the fee's hours, every kind has an icon and a legend entry.
  2. A headless crawl (Playwright + installed Chrome, found the same way page_gate.py finds them)
     at 375, 800 and 1280 px: every tab shows one panel; locked tabs never open; every Step 1 row
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
LOCKED = ["t-prop", "t-plan"]  # hidden for now (Zach, 2026-11-08); links to them land on Step 1


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
    const r = await page.evaluate(async (LOCKED) => {
      const out = [], sleep = ms => new Promise(r => setTimeout(r, ms));
      const errs = [];
      const hook = w => w.addEventListener('error', e => errs.push(e.message));
      // tabs
      const tabs = [...document.querySelectorAll('[role=tab]')];
      for (const id of LOCKED) { const t = document.getElementById(id); if (t && !t.hidden) out.push(`locked tab ${id} is visible`); }
      for (const t of tabs.filter(t => !t.hidden)) {
        t.click(); await sleep(150);
        const vis = [...document.querySelectorAll('[role=tabpanel]')].filter(p => !p.hidden).map(p => p.id);
        if (vis.length !== 1 || vis[0] !== t.getAttribute('aria-controls')) out.push(`tab ${t.id}: panels shown ${vis.join(',')}`);
      }
      // a message asking for a locked tab must land on Step 1
      for (const k of ['prop', 'plan']) {
        window.postMessage({ alyceTab: k }, '*'); await sleep(120);
        if (document.getElementById('t-s1').getAttribute('aria-selected') !== 'true') out.push(`message alyceTab:${k} opened a locked tab`);
      }
      document.getElementById('t-s1').click(); await sleep(100);
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
        for (const a of f.contentDocument.querySelectorAll('a[href^="#"]')) {
          const h = a.getAttribute('href'); if (h.length > 1 && !f.contentDocument.getElementById(decodeURIComponent(h.slice(1)))) out.push(`${t}: dead link ${h}`);
        }
      }
      document.getElementById('t-s1').click();
      return out.concat(errs.map(e => 'script error: ' + e));
    }, JSON.parse(process.env.LOCKED));
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
        env = dict(os.environ, NODE_PATH=paths[0], LOCKED=json.dumps(LOCKED))
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
