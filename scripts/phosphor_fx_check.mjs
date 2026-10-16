#!/usr/bin/env node
// phosphor_fx_check.mjs: F1 to F7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 12). Crush, Distort and the gate.
// Signal: the Notes strip (a triangle voice at about 261 Hz), measured at the output analyser (after the effects and the kid volume limiter).
// Usage: node scripts/phosphor_fx_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_fx_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const E = (f, ...a) => pg.evaluate(f, ...a)
const stats = (d) => { let s = 0, pk = 0, ch = 0; const set = new Set(); for (let i = 0; i < d.length; i++) { s += d[i] * d[i]; pk = Math.max(pk, Math.abs(d[i])); set.add(Math.round(d[i] * 1e5)); if (i && Math.abs(d[i] - d[i - 1]) > 1e-5) ch++ } const rms = Math.sqrt(s / d.length); return { crest: rms > 1e-6 ? pk / rms : 0, pk, ch, distinct: set.size, rms } }
const read = async () => stats(await E(() => window.PhosphorTest.fx.bufs()))
await pg.click('#notesb'); await pg.keyboard.down('1'); await pg.waitForTimeout(400)
const dry = await read()
check(dry.crest > 1.5 && dry.distinct > 100, `baseline: the dry triangle has crest ${dry.crest.toFixed(2)} and ${dry.distinct} distinct values`)

// F2 distort
await E(() => window.PhosphorTest.fx.on('dist', true)); await pg.waitForTimeout(250)
const dist = await read()
check(dist.crest < 1.35 && dist.crest < dry.crest - 0.25, `F2: Distort pushes the crest factor toward a square wave (${dry.crest.toFixed(2)} to ${dist.crest.toFixed(2)})`)
await E(() => window.PhosphorTest.fx.on('dist', false)); await pg.waitForTimeout(250)
const back = await read(); check(back.crest > dry.crest - 0.15, `F2: the sound returns after release (crest ${back.crest.toFixed(2)})`)

// F1 crush
await E(() => window.PhosphorTest.fx.on('crush', true)); await pg.waitForTimeout(250)
const cr = stats(await E(() => window.PhosphorTest.fx.bufsFx()))
check(cr.distinct < dry.distinct / 20 && cr.ch < dry.ch * 0.4, `F1: Crush (measured right after its stage, before the limiter) cuts the distinct values from ${dry.distinct} to ${cr.distinct} and the sample changes from ${dry.ch} to ${cr.ch}`)
await E(() => window.PhosphorTest.fx.on('crush', false)); await pg.waitForTimeout(250)

// F3 ceiling at the strongest settings
await E(() => { const g = document.getElementById('gamt'); g.value = 100; g.dispatchEvent(new Event('input', { bubbles: true })) })
await E(() => { window.PhosphorTest.fx.on('dist', true); window.PhosphorTest.fx.on('crush', true) }); await pg.waitForTimeout(300)
let pkmax = 0; for (let i = 0; i < 12; i++) { pkmax = Math.max(pkmax, (await read()).pk); await pg.waitForTimeout(30) }
check(pkmax <= 0.5, `F3: with both effects at full Amount the output peak is ${pkmax.toFixed(3)} (ceiling 0.5)`)
await E(() => { window.PhosphorTest.fx.on('dist', false); window.PhosphorTest.fx.on('crush', false); const g = document.getElementById('gamt'); g.value = 60; g.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.waitForTimeout(250)

// F4 level gate: the triangle sits near -17.7 dB rms; a threshold below lets the effect through, above keeps it out
await E(() => window.PhosphorTest.fx.gate('level', -30)); await E(() => window.PhosphorTest.fx.on('dist', true)); await pg.waitForTimeout(300)
const lo = await read()
await E(() => window.PhosphorTest.fx.gate('level', -10)); await pg.waitForTimeout(400)
const hi = await read()
check(lo.crest < 1.4 && hi.crest > 1.55, `F4: the Level gate is open below the signal and closed above it (threshold -30 dB crest ${lo.crest.toFixed(2)}; -10 dB crest ${hi.crest.toFixed(2)})`)
await E(() => window.PhosphorTest.fx.on('dist', false))

// F5 beat gate alternates
await E(() => window.PhosphorTest.fx.gate('beat', undefined, 4)); await E(() => window.PhosphorTest.fx.on('dist', true)); await pg.waitForTimeout(300)
const series = []; for (let i = 0; i < 34; i++) { series.push((await read()).crest); await pg.waitForTimeout(30) }
const lowC = Math.min(...series), highC = Math.max(...series); const mid = (lowC + highC) / 2
let flips = 0; for (let i = 1; i < series.length; i++) if ((series[i] > mid) !== (series[i - 1] > mid)) flips++
check(highC - lowC > 0.3 && flips >= 4 && flips <= 14, `F5: the Beat gate cuts the effect in and out in time (1/16 at 120 BPM; ${flips} changes in about a second, crest ${lowC.toFixed(2)} to ${highC.toFixed(2)})`)
await E(() => { window.PhosphorTest.fx.on('dist', false); window.PhosphorTest.fx.gate('off') }); await pg.waitForTimeout(250)

// F6 triggers: pad, Perform key, lane
await pg.evaluate(() => document.querySelector('details.grp:has(#gpads) > summary').click()); await pg.waitForTimeout(250)
await pg.dispatchEvent('#gpads [data-g="dist"]', 'pointerdown'); await pg.waitForTimeout(300)
const padOn = await read(); await pg.dispatchEvent('#gpads [data-g="dist"]', 'pointerup'); await pg.waitForTimeout(300); const padOff = await read()
check(padOn.crest < 1.4 && padOff.crest > 1.55, `F6: the Distort pad works while held and releases (crest ${padOn.crest.toFixed(2)} then ${padOff.crest.toFixed(2)})`)
await pg.keyboard.up('1'); await pg.click('#notesb'); await pg.keyboard.press('Backquote'); await pg.click('body', { position: { x: 5, y: 5 } })
await pg.click('#notesb'); await pg.keyboard.down('1'); await pg.click('body', { position: { x: 5, y: 5 } }).catch(() => {}); await pg.waitForTimeout(200)
await pg.keyboard.down('m'); await pg.waitForTimeout(300); const keyOn = await read(); await pg.keyboard.up('m'); await pg.waitForTimeout(300); const keyOff = await read()
check(keyOn.crest < 1.4 && keyOff.crest > 1.55, `F6: the M key (Distort) works in Perform and releases (crest ${keyOn.crest.toFixed(2)} then ${keyOff.crest.toFixed(2)})`)
await pg.keyboard.up('1')
const lane = await E(() => { const S = window.PhosphorTest.seq; S.clear(); S.set('dist', 0, 1); S.set('crush', 3, 1); const b0 = S.base(), st = S.step(); return { d: !!S.active(b0 + 0.01).dist, c: !!S.active(b0 + 3 * st + 0.01).crush, off: !S.active(b0 + 2 * st + 0.01).dist } })
check(lane.d && lane.c && lane.off, 'F6: the Crush and Distort step sequencer lanes fire on their steps only')
check(reqs.length === 0, `F7: no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
