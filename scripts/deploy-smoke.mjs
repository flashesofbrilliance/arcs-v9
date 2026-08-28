// Render smoke-gate — proves the critical public pages actually MOUNT (not a black/blank screen)
// before a deployment is trusted as production. Catches the class of failure that blanked
// resume.arcs.care on 2026-08-28 (a client-rendered React page throwing at mount → dark body,
// HTTP 200, invisible to a status-code check).
//
// Usage:
//   node scripts/deploy-smoke.mjs                       # checks the live production domains
//   node scripts/deploy-smoke.mjs https://<preview>.vercel.app   # checks a preview before promoting
//
// Exit 0 = every page rendered real content; exit 1 = at least one blanked / errored.
// Requires playwright + chromium (already in this repo's node_modules).
import { chromium } from 'playwright';

const base = (process.argv[2] || '').replace(/\/$/, '');
// [path, minVisibleTextChars, mustContain]  — tuned per page; the résumé is the canary (client React).
const PAGES = base
  ? [['/', 300, null], ['/resume.html', 800, /EXPERIENCE|Decision Intelligence/i]]
  : [
      ['https://resume.arcs.care', 800, /EXPERIENCE|Decision Intelligence/i],
      ['https://app.arcs.care',   200, null],
      ['https://arcs.care',       200, null],
    ];

const url = (p) => (p.startsWith('http') ? p : base + p);
const fails = [];
const notes = [];
const browser = await chromium.launch();

for (const [p, minChars, mustContain] of PAGES) {
  const page = await browser.newPage();
  const fatal = [];
  page.on('pageerror', (e) => fatal.push(String(e && e.message || e)));
  let status = 0;
  try {
    const resp = await page.goto(url(p), { waitUntil: 'networkidle', timeout: 45000 });
    status = resp ? resp.status() : 0;
    // Vercel bot-challenge ("Security Checkpoint") auto-passes in a real browser; give it a beat + retry once.
    if (/Security Checkpoint/i.test(await page.title())) {
      await page.waitForTimeout(3500);
      await page.goto(url(p), { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    }
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    await page.waitForTimeout(600); // let client render settle
    const text = (await page.evaluate(() => document.body.innerText || '')).trim();
    const label = url(p);
    // The gate measures WHAT RENDERED, not incidental script noise. A mount-crash (the failure this
    // gate exists for) blanks the page → low text. A benign resource error ("Unexpected token '<'"
    // from a service worker / challenge / CDN blip) leaves content intact and must NOT fail the gate.
    const blank = text.length < minChars;
    const missing = mustContain && !mustContain.test(text);
    if (blank) fails.push(`${label}: only ${text.length} chars of visible text (< ${minChars}) — blank/black screen`);
    if (missing) fails.push(`${label}: expected content ${mustContain} not found`);
    if ((blank || missing) && fatal.length) fails.push(`${label}: ↳ with mount error → ${fatal[0].slice(0, 120)}`);
    if (!blank && !missing) {
      const warn = fatal.length ? ` — note: non-fatal script error "${fatal[0].slice(0, 60)}"` : '';
      notes.push(`${label}: rendered ✓ (${text.length} chars, http ${status})${warn}`);
    }
  } catch (e) {
    fails.push(`${url(p)}: navigation failed → ${(e.message || '').split('\n')[0]}`);
  }
  await page.close();
}
await browser.close();

console.log(`\n=== deploy render smoke-gate ${base ? '(' + base + ')' : '(live production)'} ===`);
notes.forEach((n) => console.log('  · ' + n));
if (!fails.length) { console.log('\nPASS ✓  every critical page mounted with real content.'); process.exit(0); }
console.log(`\nFAIL ✗  ${fails.length} issue(s) — DO NOT promote:`); fails.forEach((f) => console.log('  - ' + f)); process.exit(1);
