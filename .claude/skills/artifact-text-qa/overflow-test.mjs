// Generalized visual-regression gate for any text-bearing HTML page/artifact.
// Catches horizontal overflow + text clipping across a viewport-width sweep and every tab/view.
// Usage:  node overflow-test.mjs path/to/page.html
// Exit:   0 = pass, 1 = one or more failures (listed per width/tab).
// Requires: playwright + a chromium build (already installed on this machine).
//
// If playwright isn't resolvable from the page's directory (e.g. a scratchpad outside the repo),
// symlink it first:  ln -sfn /Users/zharris/arcs-v9/node_modules node_modules
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const FILE = path.resolve(process.argv[2] || './index.html');
const URL = pathToFileURL(FILE).href;

// Full sweep: phones, phablets, the grid-reflow boundaries, the just-above-breakpoint danger zone, desktop, wide.
const WIDTHS = [360, 375, 414, 519, 600, 700, 760, 820, 841, 900, 1000, 1200, 1440];
const EPS = 1.5;

const fails = [];
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1000, height: 1200 });
await page.goto(URL, { waitUntil: 'load' });
// web fonts can finish loading AFTER the load event; wait so we measure the real-font layout, not the fallback.
await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});

// Discover tabs (if the page is a tabbed single-page layout); otherwise test the single view.
const tabs = await page.evaluate(() =>
  Array.from(document.querySelectorAll('.tab-link[data-tab]')).map((b) => b.getAttribute('data-tab'))
);
const views = tabs.length ? tabs : [null];

// Content hygiene (once): em-dashes dangle at line breaks and read as broken wraps.
if (await page.evaluate(() => document.body.innerText.includes('—')))
  fails.push('HYGIENE: em-dash (—) present in rendered text — replace with commas/periods/plain phrasing');

const scan = (view) => {
  const vw = document.documentElement.clientWidth;
  const EPS = 1.5;
  if (view) { const rr = document.getElementById('r-' + view); if (rr) { rr.checked = true; } else { document.querySelectorAll('.tab-panel').forEach((p) => p.classList.toggle('active', p.id === 'tab-' + view)); } }
  const root = view ? '#tab-' + view + ' ' : 'body ';
  const tag = (el) => (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : el.tagName);
  const inScroller = (el) => { // children of a horizontal scroller may extend past the viewport by design
    let p = el.parentElement;
    while (p) { const ox = getComputedStyle(p).overflowX; if (ox === 'auto' || ox === 'scroll') return true; p = p.parentElement; }
    return false;
  };
  const over = [];
  document.querySelectorAll(root + '*, footer *, .topbar *').forEach((el) => {
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return;
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.right > vw + EPS && !inScroller(el)) over.push(tag(el) + '@' + Math.round(r.right));
  });
  const clip = [];
  document.querySelectorAll(root + 'p,' + root + 'h1,' + root + 'h2,' + root + 'h3,' + root + 'li,' + root + 'blockquote').forEach((el) => {
    const cs = getComputedStyle(el);
    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') return;
    // A flex/grid element legitimately manages children that may extend; a block text element must not.
    if (['flex', 'grid', 'inline-flex', 'inline-grid'].includes(cs.display)) return;
    // Checked even when the element has inline children (e.g. a <p> with a <b>) — that is where clips hide.
    if (el.scrollWidth > el.clientWidth + EPS) clip.push(tag(el) + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth);
  });
  return { pageOverflow: document.scrollingElement.scrollWidth > vw + EPS, over: over.slice(0, 6), clip: clip.slice(0, 6) };
};

let checks = 0;
for (const w of WIDTHS) {
  await page.setViewportSize({ width: w, height: 1200 });
  await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
  for (const v of views) {
    const r = await page.evaluate(scan, v);
    checks++;
    const label = `@${w}px [${v || 'page'}]`;
    if (r.pageOverflow) fails.push(`OVERFLOW ${label}: page scrolls sideways`);
    if (r.over.length) fails.push(`OVERFLOW ${label}: ${r.over.join(', ')}`);
    if (r.clip.length) fails.push(`CLIP ${label}: ${r.clip.join(', ')}`);
  }
}
await browser.close();

console.log(`\n=== overflow/clip regression: ${path.basename(FILE)} ===`);
console.log(`widths: ${WIDTHS.join(', ')}\nviews: ${views.map((v) => v || 'page').join(', ')}\nlayout checks: ${checks}`);
if (!fails.length) { console.log(`\nPASS ✓  no horizontal overflow or text clipping at any width.`); process.exit(0); }
console.log(`\nFAIL ✗  ${fails.length} issue(s):`); fails.forEach((f) => console.log('  - ' + f)); process.exit(1);
