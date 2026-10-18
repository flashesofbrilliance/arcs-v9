#!/usr/bin/env node
/**
 * tao_studio_export.mjs: export what the Tao print studio shows for a recipe, as a PNG.
 *
 *   node scripts/tao_studio_export.mjs <recipe.json | '{"json":"inline"}'> <out.png> [--scale 3]
 *
 * Opens _ARTIFACTS/tao-print-studio.html headless, loads the recipe the way the studio restores its own state, waits for
 * the web fonts and (in mosaic mode) the raster, then frames the print with a title band and a provenance band and saves a
 * PNG. Same code path as the page, so every studio option exports exactly as it looks. Web fonts load from Google Fonts;
 * offline, the studio falls back to system type. Needs Playwright (repo node_modules or global). No new dependencies.
 * The recipe is the text the studio's "Copy recipe" button copies. Not an edition.
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const pos = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const [recipeArg, out] = pos;
if (!recipeArg || !out) { console.error('usage: tao_studio_export.mjs <recipe.json|inline json> <out.png> [--scale 3]'); process.exit(2); }
const SCALE = +opt('scale', 3);
const recipe = JSON.parse(existsSync(recipeArg) ? readFileSync(recipeArg, 'utf8') : recipeArg);
const studio = pathToFileURL(resolve(dirname(fileURLToPath(import.meta.url)), '..', '_ARTIFACTS', 'tao-print-studio.html')).href;

function loadPlaywright() {
  const req = createRequire(import.meta.url);
  for (const base of [process.cwd(), execFileSync('npm', ['root', '-g']).toString().trim()]) {
    try { return req(req.resolve('playwright', { paths: [base] })); } catch {}
  }
  console.error('Playwright not found (repo node_modules or global).'); process.exit(3);
}
const { chromium } = loadPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: SCALE });
const errs = [];
page.on('pageerror', (e) => errs.push(e.message));
await page.addInitScript((r) => { try { localStorage.setItem('tao-print-studio', JSON.stringify(r)); } catch (e) {} }, recipe);
await page.goto(studio);
await page.evaluate(() => document.fonts.ready);
if (+recipe.pixel > 0) await page.waitForSelector('#print canvas', { timeout: 15000 });
await page.waitForTimeout(1800);
const info = await page.evaluate(() => {
  const rid = document.getElementById('proverb').value;
  const row = PROVERBS.filter((p) => p.id === rid)[0] || PROVERBS[0];
  return { id: row.id, aspect: row.aspect, verb: row.verb, ref: row.source, fid: document.getElementById('fidelity').value / 100, seed: document.getElementById('seed').value, palette: document.getElementById('palette').value, ground: document.getElementById('ground').value };
});
await page.evaluate((i) => {
  const pr = document.getElementById('print');
  const band = (cls, html) => { const d = document.createElement('div'); d.style.cssText = 'display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;font-family:var(--ds-font-mono);font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:var(--dimmed)' + cls; d.innerHTML = html; return d; };
  const sheet = document.createElement('div');
  sheet.id = 'sheet';
  sheet.style.cssText = 'width:996px;padding:48px;box-sizing:border-box;background:var(--bg);color:var(--text)';
  const top = band(';padding-bottom:20px;border-bottom:1px solid var(--border);margin-bottom:28px', '<b style="color:var(--cyan);font-weight:600">The Tao of ARCS</b><span>' + i.id + ' &middot; ' + i.aspect + '.' + i.verb + '</span>');
  const bot = band(';padding-top:20px;border-top:1px solid var(--border);margin-top:28px;letter-spacing:.04em;text-transform:none', '<span>fidelity ' + i.fid.toFixed(2) + ' &middot; seed ' + i.seed + ' &middot; ' + i.palette + ' palette &middot; ' + i.ground + ' ground</span><span>Reproducible from id, recipe and seed. Not an edition.</span>');
  pr.style.width = '900px';
  document.body.replaceChildren(sheet);
  sheet.append(top, pr, bot);
}, info);
await page.locator('#sheet').screenshot({ path: resolve(out) });
await browser.close();
if (errs.length) console.error('page errors:', errs.join(' | '));
console.log(resolve(out));
