#!/usr/bin/env node
// phosphor_rack_check.mjs: E1 to E7 and L1 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 13). Echo, Room, Shimmer, Sweep and the note keys in the deck.
// Usage: node scripts/phosphor_rack_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_rack_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
async function open(w = 1280, h = 900) {
  const pg = await (await b.newContext({ viewport: { width: w, height: h } })).newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
  await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
  return pg
}
const rmsOf = (d) => { let s = 0; for (const v of d) s += v * v; return Math.sqrt(s / d.length) }
const goertzel = (d0, f, sr) => { const d = d0.map((v, i) => v * (0.5 - 0.5 * Math.cos(2 * Math.PI * i / (d0.length - 1)))), w = 2 * Math.PI * f / sr, c = 2 * Math.cos(w); let s1 = 0, s2 = 0; for (const v of d) { const s = v + c * s1 - s2; s2 = s1; s1 = s } return Math.sqrt(s1 * s1 + s2 * s2 - c * s1 * s2) / d.length }
const pg = await open()
const E = (f, ...a) => pg.evaluate(f, ...a)
const buf = async () => await E(() => window.PhosphorTest.fx.bufs())
const tailAfterRelease = async (kind) => {
  await pg.keyboard.down('1'); if (kind) await E((k) => window.PhosphorTest.fx.on(k, true), kind); await pg.waitForTimeout(500)
  await pg.keyboard.up('1'); if (kind) await E((k) => window.PhosphorTest.fx.on(k, false), kind)
  await pg.waitForTimeout(450); const a = rmsOf(await buf()); await pg.waitForTimeout(2050); const c = rmsOf(await buf()); return { a, c }
}
await pg.click('#notesb')
const none = await tailAfterRelease(null)
check(none.a < 0.0005, `baseline: with no effect the sound is gone 0.45 s after the key is released (rms ${none.a.toFixed(5)})`)
// E1 echo
const ec = await tailAfterRelease('echo')
check(ec.a > 0.002 && ec.c < ec.a * 0.2, `E1: Echo leaves a tail after release that then decays (rms ${ec.a.toFixed(4)} at 0.45 s, ${ec.c.toFixed(4)} at 2.5 s)`)
// E2 room
const rm = await tailAfterRelease('room')
check(rm.a > 0.002 && rm.c < rm.a * 0.2, `E2: Room leaves a tail after release that then decays (rms ${rm.a.toFixed(4)} at 0.45 s, ${rm.c.toFixed(4)} at 2.5 s)`)
// E3 shimmer
const spread = async (kind) => {
  await pg.keyboard.down('1'); if (kind) await E((k) => window.PhosphorTest.fx.on(k, true), kind); await pg.waitForTimeout(600)
  const rs = []; for (let i = 0; i < 28; i++) { rs.push(rmsOf((await buf()).slice(0, 512))); await pg.waitForTimeout(40) }
  await pg.keyboard.up('1'); if (kind) await E((k) => window.PhosphorTest.fx.on(k, false), kind); await pg.waitForTimeout(700)
  const m = rs.reduce((x, y) => x + y, 0) / rs.length; return Math.sqrt(rs.reduce((x, y) => x + (y - m) * (y - m), 0) / rs.length)
}
const sd0 = await spread(null), sd1 = await spread('shim')
check(sd1 > Math.max(sd0 * 3, 0.002), `E3: Shimmer makes the level beat (spread ${sd0.toFixed(5)} dry, ${sd1.toFixed(5)} with Shimmer)`)
// E4 sweep
const sr = await E(() => window.PhosphorTest.fx.sr())
await pg.keyboard.down('1'); await pg.waitForTimeout(500); const fxbuf = async () => await E(() => window.PhosphorTest.fx.bufsFx()); const h3dry = goertzel(await fxbuf(), 3 * 261.6256, sr)
await E(() => window.PhosphorTest.fx.on('sweep', true)); await pg.waitForTimeout(1800); const h3 = goertzel(await fxbuf(), 3 * 261.6256, sr)
await E(() => window.PhosphorTest.fx.on('sweep', false)); await pg.waitForTimeout(900); const h3back = goertzel(await fxbuf(), 3 * 261.6256, sr); await pg.keyboard.up('1')
check(h3 < h3dry * 0.3 && h3back > h3dry * 0.7, `E4: Sweep (measured right after the effect stages, before the soft ceiling adds its own harmonics) removes the third harmonic and it returns after release (${h3dry.toFixed(4)} dry, ${h3.toFixed(4)} swept, ${h3back.toFixed(4)} after)`)
// E6 pads and lanes
await pg.evaluate(() => document.querySelector('details.grp:has(#gpads) > summary').click()); await pg.waitForTimeout(250)
const pads = await E(() => ['echo', 'room', 'shim', 'sweep'].every((k) => !!document.querySelector('#gpads [data-g="' + k + '"]')))
await pg.dispatchEvent('#gpads [data-g="echo"]', 'pointerdown'); await pg.waitForTimeout(150)
const lbl = await E(() => document.getElementById('gmo').textContent); await pg.dispatchEvent('#gpads [data-g="echo"]', 'pointerup'); await pg.waitForTimeout(150)
const lane = await E(() => { const S = window.PhosphorTest.seq; S.clear(); S.set('echo', 1, 1); S.set('sweep', 5, 1); const b0 = S.base(), st = S.step(); return !!S.active(b0 + st + 0.01).echo && !!S.active(b0 + 5 * st + 0.01).sweep && !S.active(b0 + 3 * st + 0.01).echo })
check(pads && /echo/.test(lbl) && lane, `E6: four pads (Echo, Room, Shimmer, Sweep) and two lanes (Echo, Sweep) trigger (label "${lbl}")`)
// E5 ceiling with the sends on and a hot signal: sum of three notes plus all sends
await pg.keyboard.down('1'); await pg.keyboard.down('3'); await pg.keyboard.down('5'); await pg.keyboard.down('8')
await E(() => { ['echo', 'room', 'shim', 'dist'].forEach((k) => window.PhosphorTest.fx.on(k, true)) }); await pg.waitForTimeout(800)
let pk = 0; for (let i = 0; i < 25; i++) { pk = Math.max(pk, await E(() => window.PhosphorTest.outPeak())); await pg.waitForTimeout(40) }
check(pk <= 0.5, `E5: four notes with Echo, Room, Shimmer and Distort on peak at ${pk.toFixed(3)} (ceiling 0.5)`)
await E(() => { ['echo', 'room', 'shim', 'dist'].forEach((k) => window.PhosphorTest.fx.on(k, false)) })
for (const k of ['1', '3', '5', '8']) await pg.keyboard.up(k)

// L1 layout: the key at the centre of key 8 is on top and in view after scrolling to the bottom, desktop and phone
for (const [w, h, name] of [[1280, 900, 'desktop'], [390, 844, 'phone']]) {
  const lp = await open(w, h)
  await lp.click('#notesb'); await lp.evaluate(() => { const i = document.querySelector('.inst').getBoundingClientRect(); window.scrollTo(0, i.bottom + window.scrollY - innerHeight + 4) }); await lp.waitForTimeout(300)
  const r = await lp.evaluate(() => { const k = document.querySelectorAll('#nkeys .nk')[7], b = k.getBoundingClientRect(), el = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return { top: !!(el && el.closest('#nkeys')), inView: b.top >= 0 && b.bottom <= innerHeight, h: Math.round(b.height), deckH: Math.round(document.getElementById('deck').getBoundingClientRect().height), vh: innerHeight } })
  check(r.top && r.inView && r.h >= 44, `L1: ${name}: after scrolling to the bottom of the controls a note key is on top (${r.top}), in view (${r.inView}) and ${r.h} px tall (deck ${r.deckH} of ${r.vh} px)`)
  await lp.context().close()
}
check(reqs.length === 0, `E7: no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
