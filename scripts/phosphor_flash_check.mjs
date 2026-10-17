#!/usr/bin/env node
// phosphor_flash_check.mjs: Picture strength and the flash limit (amendment 35). Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_flash_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_flash_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href, errs = []
const open = async () => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); return pg }
const run = async (pg, seq) => pg.evaluate((s) => s.map(([L, t]) => window.PhosphorTest.glim(L, t)), seq)
let pg = await open()
check(await pg.evaluate(() => window.PhosphorTest.gstr()) === 1 && await pg.evaluate(() => document.getElementById('gs0').checked), 'S1: the picture starts at Soft (strength 1)')
// S2: 8 Hz full swing is limited within a second; unit sequence, times in ms
const fast = []; for (let i = 0; i < 16; i++) fast.push([i % 2 ? 0.5 : 0.2, 1000 + i * 125])
const r = await run(pg, fast); const firstLock = r.indexOf(true)
check(firstLock > 0 && firstLock <= 5, `S2: an 8-per-second swing locks the picture to Soft by frame ${firstLock + 1} (${(firstLock) * 125} ms in)`)
const after = await run(pg, [[0.3, 1000 + 16 * 125 + 2000]]); check(after[0] === true, 'S2b: it stays locked for the three seconds after the last swing')
const rel = await run(pg, [[0.3, 1000 + 16 * 125 + 3500], [0.3, 1000 + 16 * 125 + 4500]]); check(rel[1] === false, 'S2c: it lets go once the picture is calm')
await pg.context().close()
// S3: not counted: slow (one flash a second), small swings, and swings between bright frames
pg = await open(); const cases = {
  'one flash a second': Array.from({ length: 12 }, (_, i) => [i % 2 ? 0.5 : 0.2, 1000 + i * 500]),
  'small swings of 0.05 at 8 a second': Array.from({ length: 16 }, (_, i) => [i % 2 ? 0.25 : 0.2, 1000 + i * 125]),
  'bright-to-bright swings (darker side 0.85)': Array.from({ length: 16 }, (_, i) => [i % 2 ? 0.97 : 0.85, 1000 + i * 125]) }
for (const [name, seq] of Object.entries(cases)) { await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); const rr = await run(pg, seq); check(!rr.includes(true), `S3: ${name} does not lock`) }
await pg.context().close()
// S4: the real picture. Hold Tear, Split and Blocks at each strength, sample the shown canvas every frame for 4 s, count flashes per second the WCAG way
const flashes = async (pg, strobe = false) => pg.evaluate((strobe) => new Promise((res) => {
  const cv = document.querySelector('.frame canvas'), t = document.createElement('canvas'); t.width = 16; t.height = 9; const x = t.getContext('2d', { willReadFrequently: true }), ev = []; const mc = document.createElement('canvas'); mc.width = 64; mc.height = 36; const mv = mc.getContext('2d', { willReadFrequently: true }); let pm = null, mot = 0; let prev = null, dir = 0, worst = 0, n = 0, t0 = performance.now(), mean = 0
  const lum = () => { x.drawImage(cv, 0, 0, 16, 9); const d = x.getImageData(0, 0, 16, 9).data; let s = 0; for (let i = 0; i < d.length; i += 4) s += 0.2126 * (d[i] / 255) ** 2.2 + 0.7152 * (d[i + 1] / 255) ** 2.2 + 0.0722 * (d[i + 2] / 255) ** 2.2; return s / 144 }
  const tick = () => { const now = performance.now(), L = strobe ? (Math.floor(now / 62.5) % 2 ? 0.5 : 0.2) : lum(); mean += L; n++; if (!strobe) { mv.drawImage(cv, 0, 0, 64, 36); const dd = mv.getImageData(0, 0, 64, 36).data; if (pm) { let c = 0; for (let i = 0; i < dd.length; i += 4) if (Math.abs(dd[i] - pm[i]) + Math.abs(dd[i + 1] - pm[i + 1]) + Math.abs(dd[i + 2] - pm[i + 2]) > 60) c++; mot += c / 2304 } pm = dd.slice() }
    if (prev !== null) { const d = L - prev; if (Math.abs(d) >= 0.1 && Math.min(L, prev) < 0.8 && (d > 0 ? 1 : -1) !== dir) { ev.push(now); dir = d > 0 ? 1 : -1 } }
    prev = L; while (ev.length && now - ev[0] > 1000) ev.shift(); worst = Math.max(worst, Math.floor(ev.length / 2))
    if (now - t0 < 4000) requestAnimationFrame(tick); else res({ worst, mean: mean / n, frames: n, mot: mot / n }) }
  requestAnimationFrame(tick) }), strobe)
const res = {}
for (const [id, name] of [['gs0', 'Soft'], ['gs1', 'Medium'], ['gs2', 'Strong']]) {
  pg = await open(); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); await pg.click('#play'); await pg.waitForTimeout(600)
  await pg.evaluate((id) => { const e = document.getElementById(id); e.checked = true; e.dispatchEvent(new Event('change', { bubbles: true })); for (const k of ['tear', 'rgb', 'blocks']) window.PhosphorTest.hold.on(k, 'latch', true) }, id); await pg.waitForTimeout(500)
  res[name] = await flashes(pg); await pg.context().close()
}
for (const [k, v] of Object.entries(res)) check(v.worst <= 3 && v.frames > 60, `S4: at ${k} the shown picture never flashes more than 3 times in a second (worst ${v.worst}, ${v.frames} frames)`)
check(res.Strong.mot > res.Soft.mot * 1.3, `S4b: Strong moves the picture more than Soft (${res.Soft.mot.toFixed(4)} to ${res.Medium.mot.toFixed(4)} to ${res.Strong.mot.toFixed(4)} changed share per frame)`)
pg = await open(); const st = await flashes(pg, true); await pg.context().close(); check(st.worst >= 3, `S4c: the measurer itself sees a strobe (${st.worst} flashes in a second), so a zero above means something`)
check(res.Soft.worst <= 2 && res.Medium.worst <= 2 && res.Strong.worst <= 2, 'S5: the limit holds at two flashes a second or fewer at every strength')
check(errs.length === 0, 'S6: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
