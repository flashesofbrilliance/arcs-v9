#!/usr/bin/env node
// keyline_check.mjs: the tabbed-brief keyline gate (R2 lockup rule, 2026-11-13).
// Every two-column molecule (signal ledger rows, cold-read slots, timeline, two-column tables, receipt rows)
// must start its second column at exactly --key + --s-5 from the row's left edge, so content columns share one edge.
// Measured headless at 1280 and 820 with every fold open and every pane shown. Fails on any offset off by more than 1px.
// Usage: node scripts/keyline_check.mjs public/gravity-brief*.html   (exit 1 on any miss)
import { chromium } from 'playwright-core';
import path from 'node:path';

const files = process.argv.slice(2);
if (!files.length) { console.error('usage: keyline_check.mjs <page.html>...'); process.exit(2); }
const exe = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const b = await chromium.launch({ executablePath: exe });
let bad = 0;
for (const f of files) for (const w of [1280, 820]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  await p.goto('file://' + path.resolve(f)); await p.waitForTimeout(200);
  const misses = await p.evaluate(() => {
    document.querySelectorAll('[hidden]').forEach(e => e.hidden = false);
    document.querySelectorAll('[aria-expanded="false"]').forEach(e => e.setAttribute('aria-expanded', 'true'));
    const probe = document.createElement('div'); probe.style.cssText = 'position:absolute;width:calc(var(--key) + var(--s-5))';
    document.querySelector('.tb-body').appendChild(probe); const want = probe.getBoundingClientRect().width; probe.remove();
    const pairs = [
      ['.sl-row', r => r.querySelector('.sl-ev')],
      ['.tb-tl-i', r => r.querySelector('.tb-tl-t')],
      ['.cr-slots:not(.tb-coldread .cr-slots)', r => r.querySelector('dd')],
      ['.rcpt-rows', r => r.querySelector('dd')],
      ['.tb-table tr', r => r.children.length === 2 ? r.children[1] : null],
    ];
    const out = [];
    for (const [sel, second] of pairs) for (const row of document.querySelectorAll(sel)) {
      const s = second(row); if (!s) continue;
      const a = row.getBoundingClientRect(), c = s.getBoundingClientRect();
      if (!a.width || c.left - a.left < 8) continue; // stacked (one column): nothing to align
      const off = c.left - a.left;
      if (Math.abs(off - want) > 1) out.push(sel + ' second column at ' + off.toFixed(1) + 'px, want ' + want.toFixed(1));
    }
    return [...new Set(out)];
  });
  for (const m of misses) { console.log('✖ keyline ' + f + ' @' + w + ': ' + m); bad++; }
  await p.close();
}
await b.close();
if (bad) { console.log('keyline: ' + bad + ' miss(es)'); process.exit(1); }
console.log('✓ keyline: every two-column molecule starts its second column on --key + --s-5 (' + files.length + ' pages, 1280 and 820)');
