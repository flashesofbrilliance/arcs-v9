#!/usr/bin/env node
// phosphor_sun_check.mjs: S1 to S4 and S8 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 17). The Sun view ported from Raw Capture.
// Needs a real song for S3: PHOSPHOR_FILES=song.mp3. Usage: node scripts/phosphor_sun_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: PHOSPHOR_FILES=song.mp3 node scripts/phosphor_sun_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const E = (f, ...a) => pg.evaluate(f, ...a)
const pic = () => E(() => { const c = document.getElementById('cv'), g = c.getContext('2d'), w = c.width, h = c.height, d = g.getImageData(0, 0, w, h).data, L = new Float32Array(w * h); for (let i = 0; i < w * h; i++) L[i] = (0.2126 * d[i * 4] + 0.7152 * d[i * 4 + 1] + 0.0722 * d[i * 4 + 2]) / 255; let hash = 2166136261; for (let i = 0; i < d.length; i += 7) hash = Math.imul(hash ^ d[i], 16777619) >>> 0
  // the brightest 0.5 percent: where are they, and the disc size
  const idx = Array.from(L.keys()).sort((a, b2) => L[b2] - L[a]).slice(0, Math.floor(w * h * 0.005)); let mx = 0, my = 0; for (const i of idx) { mx += (i % w) / w; my += Math.floor(i / w) / h } mx /= idx.length; my /= idx.length
  let top = 0, bot = 0, tn = 0, bn = 0; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { if (y < h / 3) { top += L[y * w + x]; tn++ } else if (y > 2 * h / 3) { bot += L[y * w + x]; bn++ } }
  let bright = 0; for (let y = 0; y < h * 0.55; y++) for (let x = 0; x < w; x++) if (L[y * w + x] > 0.92) bright++
  return { hash, mx, my, top: top / tn, bot: bot / bn, bright: bright / (w * h) } })
const sig = await E(() => window.PhosphorTest.sig())
check(sig.mode === 4 && sig.pal === 'orig', `S1: a fresh page opens on the Sun in the original palette (mode ${sig.mode}, ${sig.pal})`)
const p0 = await pic()
check(p0.mx > 0.5 && p0.mx < 0.9 && p0.my < 0.45 && p0.bot < p0.top - 0.1, `S2: the brightest pixels are in the sun (x ${p0.mx.toFixed(2)}, y ${p0.my.toFixed(2)} of the frame) and the lower third (${p0.bot.toFixed(2)}) is darker than the sky (${p0.top.toFixed(2)})`)
const p1 = await pic(); check(p1.hash === p0.hash, 'S4: the same moment draws the same pixels')
await E(() => document.querySelector('#kid [data-km="1"]').click()); await E(() => document.querySelector('#kid [data-km="4"]').click())
check((await E(() => window.PhosphorTest.zoom().mode)) === 4 && (await E(() => !!document.querySelector('.hudk [data-km="4"]'))), 'S8: the Sun view is reachable from the kid button and the full screen bar')
const song = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)[0]
if (song) {
  await pg.setInputFiles('#file', song); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 })
  await E(() => { const r = document.getElementById('res'); r.value = 9; r.dispatchEvent(new Event('input', { bubbles: true })) })
  const dur = await E(() => window.PhosphorTest.dur()), rows = []
  for (let i = 1; i <= 14; i++) { const tt = dur * i / 15; await E((tt) => { const s = document.getElementById('scrub'); s.value = Math.round(tt / window.PhosphorTest.dur() * 1000); s.dispatchEvent(new Event('input')) }, tt); await pg.waitForTimeout(160); rows.push({ rms: await E((tt) => window.PhosphorTest.rmsAt(tt), tt), ...(await pic()) }) }
  const hi = rows.reduce((m, r) => (r.rms > m.rms ? r : m)), lo = rows.reduce((m, r) => (r.rms < m.rms ? r : m))
  const spread = hi.rms - lo.rms
  check(spread < 0.05 || hi.bright >= lo.bright * 1.15, `S3: at the loudest moment (rms ${hi.rms.toFixed(2)}) the sun's bright area (${hi.bright.toFixed(4)}) is larger than at the quietest (rms ${lo.rms.toFixed(2)}, ${lo.bright.toFixed(4)})${spread < 0.05 ? ' (this song barely changes loudness, so the check does not apply)' : ''}`)
  check(spread < 0.05 || hi.my <= lo.my + 0.005, `S3: the sun is as high or higher at the loudest moment (y ${hi.my.toFixed(3)} against ${lo.my.toFixed(3)} of the frame)`)
}
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
