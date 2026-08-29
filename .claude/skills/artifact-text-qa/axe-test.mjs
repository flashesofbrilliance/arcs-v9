// WCAG accessibility scan via axe-core across every tab. Usage: node axe-test.mjs path/to/page.html
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const axeSource = readFileSync(require.resolve('axe-core'), 'utf8');

const FILE = path.resolve(process.argv[2] || './index.html');
const URL = pathToFileURL(FILE).href;
const TABS = ['about', 'services', 'cases', 'clients', 'testimonials', 'contact'];

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1000, height: 1200 });
await page.goto(URL, { waitUntil: 'load' });
await page.addScriptTag({ content: axeSource });

const seen = new Map();
for (const t of TABS) {
  await page.evaluate((tab) => {
    document.querySelectorAll('.tab-panel').forEach((p) => p.classList.toggle('active', p.id === 'tab-' + tab));
  }, t);
  const res = await page.evaluate(async () => await window.axe.run(document, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
  }));
  for (const v of res.violations) {
    const key = v.id;
    if (!seen.has(key)) seen.set(key, { impact: v.impact, help: v.help, nodes: new Set() });
    v.nodes.forEach((n) => seen.get(key).nodes.add(`[${t}] ${n.target.join(' ')} :: ${(n.html || '').slice(0, 70)}`));
  }
}
await browser.close();

console.log(`\n=== axe-core WCAG 2.1 A/AA scan: ${path.basename(FILE)} ===`);
if (!seen.size) { console.log('PASS ✓  no WCAG A/AA violations across any tab.'); process.exit(0); }
let total = 0;
for (const [id, v] of [...seen.entries()].sort((a, b) => b[1].nodes.size - a[1].nodes.size)) {
  total += v.nodes.size;
  console.log(`\n✗ ${id} (${v.impact}) — ${v.help}  [${v.nodes.size} node(s)]`);
  [...v.nodes].slice(0, 4).forEach((n) => console.log('    ' + n));
}
console.log(`\nFAIL ✗  ${seen.size} rule(s), ${total} node(s).`);
process.exit(1);
