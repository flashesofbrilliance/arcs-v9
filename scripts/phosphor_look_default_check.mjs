#!/usr/bin/env node
// phosphor_look_default_check.mjs: D1 to D4 and R1 to R3 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 16). The default look and the session recorder.
// Usage: node scripts/phosphor_look_default_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_look_default_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
async function fresh() {
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true }), pg = await ctx.newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
  await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
  return { pg, ctx }
}
// D1
let { pg, ctx } = await fresh()
await pg.evaluate(() => localStorage.clear()); await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
let sig = await pg.evaluate(() => window.PhosphorTest.sig())
check(sig.mode === 4 && sig.pal === 'orig', `D1: a fresh page opens on the Sun in the original palette (mode ${sig.mode}, ${sig.pal})`)
// D2 ramp then cancel
await pg.click('#play'); await pg.waitForTimeout(300)
const r0 = await pg.evaluate(() => +document.getElementById('res').value); await pg.waitForTimeout(3000); const r1 = await pg.evaluate(() => +document.getElementById('res').value)
check(r0 <= 4 && r1 > r0, `D2: the first Play starts coarse and the picture sharpens (resolution ${r0} then ${r1} after 3 s)`)
await pg.dispatchEvent('#res', 'pointerdown'); const hold = await pg.evaluate(() => +document.getElementById('res').value); await pg.waitForTimeout(3500); const held = await pg.evaluate(() => +document.getElementById('res').value)
check(held === hold, `D2: touching the Resolution slider stops the ramp (${hold} then ${held})`)
const saved = await pg.evaluate(() => window.PhosphorTest.saved()); check(!saved || JSON.parse(saved).res !== 4, 'D2: ramp steps are not saved as a user choice')
await ctx.close()
// D3 saved settings win
;({ pg, ctx } = await fresh())
await pg.evaluate(() => localStorage.setItem('phosphor.settings.v1', JSON.stringify({ mode: 0, zs: [1, 1, 1, 1], pal: 'orig', curve: 'lin', amt: 0, bits: 8, wood: false, crt: false, calm: true, res: 9, chs: false, rl: { on: false, bars: 2, dir: 'up' }, seq: { quant: 'beat', gate: 0.5, bars: 1, cells: {} } })))
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
sig = await pg.evaluate(() => window.PhosphorTest.sig()); check(sig.mode === 0 && sig.pal === 'orig', `D3: saved settings beat the default (mode ${sig.mode}, ${sig.pal})`)
// D4 plain
await pg.evaluate(() => window.PhosphorTest.preset('plain')); sig = await pg.evaluate(() => window.PhosphorTest.sig()); check(sig.mode === 4 && sig.pal === 'orig' && sig.cells === 0, `D4: Plain restores the new default (mode ${sig.mode}, ${sig.pal}, ${sig.cells} steps)`)
await ctx.close()
// R recorder
;({ pg, ctx } = await fresh())
await pg.evaluate(() => localStorage.clear())
await pg.evaluate(() => { document.querySelector('details.grp:has(#sessrec) > summary').click() }); await pg.waitForTimeout(250)
await pg.click('#sessrec'); await pg.click('body', { position: { x: 5, y: 5 } }); await pg.waitForTimeout(400) // blur the button: Space on a focused button would press it
await pg.evaluate(() => { const s = document.getElementById('palsel'); s.value = 'heat'; s.dispatchEvent(new Event('change', { bubbles: true })) })
await pg.keyboard.press('Space'); await pg.waitForTimeout(600); await pg.keyboard.press('Space'); await pg.waitForTimeout(1200)
await pg.evaluate(() => { const r = document.getElementById('res'); r.value = 5; r.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.dispatchEvent('#kcol', 'pointerdown')
await pg.waitForTimeout(600)
const dls = []; pg.on('download', (d) => dls.push(d))
await pg.click('#sessrec'); await pg.waitForFunction(() => /Saved phosphor-session/.test(document.getElementById('sesshint').textContent), null, { timeout: 15000 })
await pg.waitForTimeout(800)
const names = []; let webm = 0, json = null
for (const d of dls) { const n = d.suggestedFilename(); names.push(n); const p = path.join(os.tmpdir(), n); await d.saveAs(p); if (n.endsWith('.webm')) webm = fs.statSync(p).size; if (n.endsWith('.json')) json = JSON.parse(fs.readFileSync(p, 'utf8')) }
check(names.length === 2 && webm > 10000 && json, `R1: stopping saves a video and a list (${names.join(', ')}; video ${webm} bytes)`)
const ev = json ? json.events : []
check(ev.some((e) => e.k === 'set' && e.id === 'palsel' && e.v === 'heat') && ev.some((e) => e.k === 'set' && e.id === 'res' && e.v === '5') && ev.some((e) => e.k === 'key' && e.id === 'Space') && ev.every((e) => typeof e.t === 'number'), `R2: the list holds the controls touched with their values, the keys pressed, and times (${ev.length} events: ${ev.map((e) => e.k + ':' + e.id + (e.v === null ? '' : '=' + e.v)).slice(0, 6).join(' ')})`)
check(json && json.startSettings && json.startSettings.pal !== undefined, 'R2: the list starts with the settings at the start of the recording')
check(reqs.length === 0, `R3: no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
