#!/usr/bin/env node
// phosphor_check.mjs: the checks pre-registered in _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md.
// V1 ground truth on generated tones (no copyrighted file), V4 pure function, V5 audio clock, V6 chapters,
// V7 resolution ladder (blocks) and palette, V8 privacy, V9 errors and reduced motion, V10 frame time, V11 ladder sheet.
// Real files (V2, V3, V6) are optional and local: set PHOSPHOR_FILES to a comma-separated list of paths.
// Usage: node scripts/phosphor_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const file = process.argv[2]
if (!file) { console.error('usage: phosphor_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable (set PLAYWRIGHT_ROOT)'); process.exit(2) }
const fails = []
const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const url = pathToFileURL(path.resolve(file)).href
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'phosphor-'))

function wav(name, fn, secs = 8, sr = 44100) {
  const n = secs * sr, buf = Buffer.alloc(44 + n * 2)
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22)
  buf.writeUInt32LE(sr, 24); buf.writeUInt32LE(sr * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(n * 2, 40)
  for (let i = 0; i < n; i++) buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, fn(i / sr))) * 32000), 44 + i * 2)
  const p = path.join(tmp, name); fs.writeFileSync(p, buf); return p
}
const b = await pw.chromium.launch()
const errors = []
async function open() {
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1000 } }), pg = await ctx.newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
  const reqs = []; pg.on('request', (r) => reqs.push(r.url()))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 30000 })
  return { ctx, pg, reqs }
}
const load = async (pg, p) => { await pg.setInputFiles('#file', p); await pg.waitForFunction((n) => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 }); }
const seek = (pg, frac) => pg.evaluate((f) => { const s = document.getElementById('scrub'); s.value = Math.round(f * 1000); s.dispatchEvent(new Event('input', { bubbles: true })) }, frac)
const hash = (pg) => pg.evaluate(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i += 7) h = Math.imul(h ^ d[i], 16777619) >>> 0; return h })
const setRes = (pg, v) => pg.evaluate((v) => { const r = document.getElementById('res'); r.value = v; r.dispatchEvent(new Event('input', { bubbles: true })) }, v)

// ---- V1 ground truth tones
{
  const { ctx, pg } = await open()
  for (const f of [110, 440, 1760, 7040]) {
    await load(pg, wav(`tone${f}.wav`, (t) => 0.6 * Math.sin(2 * Math.PI * f * t)))
    await seek(pg, 0.5); await pg.waitForTimeout(150)
    const txt = await pg.evaluate(() => document.getElementById('nowsub').textContent)
    const m = txt.match(/near ([\d.]+) (Hz|kHz)/), hz = m ? parseFloat(m[1]) * (m[2] === 'kHz' ? 1000 : 1) : 0
    check(hz > 0 && Math.abs(Math.log(hz / f)) < Math.log(1.2), `V1: a ${f} Hz tone is reported near ${hz} Hz (within 20 percent)`)
  }
  await ctx.close()
}
// ---- V4, V7, V10, V11 on the demo
{
  const { ctx, pg } = await open()
  for (const m of [0, 1, 2, 3]) {
    await pg.evaluate((m) => { const r = document.getElementById('m' + m); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) }, m)
    await seek(pg, 0.4); const h1 = await hash(pg); await seek(pg, 0.8); const hx = await hash(pg); await seek(pg, 0.4); const h2 = await hash(pg)
    check(h1 === h2 && h1 !== hx, `V4: mode ${m} draws the same pixels when you return to the same time, and different pixels at another time`)
  }
  await pg.evaluate(() => { const r = document.getElementById('m1'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) })
  await seek(pg, 0.5); await setRes(pg, 4)   // 256 x 144 rung
  const blocks = await pg.evaluate(() => { const c = document.getElementById('cv'), W = c.width, H = c.height, d = c.getContext('2d').getImageData(0, 0, W, H).data, bw = W / 256, bh = H / 144; let bad = 0, n = 0; for (let by = 5; by < 140; by += 9) for (let bx = 5; bx < 250; bx += 11) { const x0 = Math.floor(bx * bw) + 1, y0 = Math.floor(by * bh) + 1, x1 = Math.floor((bx + 1) * bw) - 2, y1 = Math.floor((by + 1) * bh) - 2, i0 = (y0 * W + x0) * 4, i1 = (y1 * W + x1) * 4; n++; if (d[i0] !== d[i1] || d[i0 + 1] !== d[i1 + 1] || d[i0 + 2] !== d[i1 + 2]) bad++ } return { bad, n } })
  check(blocks.bad === 0, `V7: at the 256 x 144 rung the picture is made of uniform blocks (${blocks.n} sampled, ${blocks.bad} not uniform)`)
  await setRes(pg, 9); const hv = await hash(pg)
  await pg.evaluate(() => { const r = document.getElementById('pal'); r.value = 8; r.dispatchEvent(new Event('input', { bubbles: true })) }); check((await hash(pg)) === hv, 'V7: at 8 bit palette and the vector rung the frame is unquantized (unchanged)')
  await pg.evaluate(() => { const r = document.getElementById('pal'); r.value = 1; r.dispatchEvent(new Event('input', { bubbles: true })) })
  const distinct = await pg.evaluate(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data, s = [new Set(), new Set(), new Set()]; for (let i = 0; i < d.length; i += 4) for (let k = 0; k < 3; k++) s[k].add(d[i + k]); return s.map((x) => x.size) })
  check(distinct.every((n) => n <= 2), `V7: at 1 bit palette each color channel has at most 2 values (${distinct.join(', ')})`)
  await pg.evaluate(() => { const r = document.getElementById('pal'); r.value = 8; r.dispatchEvent(new Event('input', { bubbles: true })) })
  const rungs = await pg.evaluate(() => document.querySelectorAll('#rungs canvas').length)
  check(rungs === 9, `V11: the ladder sheet shows 9 rungs (${rungs})`)
  // V10 frame time while playing at 1080p
  await pg.evaluate(() => { const r = document.getElementById('res'); r.value = 6; r.dispatchEvent(new Event('input', { bubbles: true })) })
  await seek(pg, 0.05); await pg.locator('#play').click(); await pg.waitForTimeout(2600)
  const ms = await pg.evaluate(() => { const m = document.getElementById('srcsub').textContent.match(/Draw ([\d.]+) ms/); return m ? parseFloat(m[1]) : 99 })
  check(ms <= 12, `V10: median draw time while playing at 1920 x 1080 is ${ms} ms (want 12 or less)`)
  // V5 audio clock: visual time vs elapsed
  const t5 = await pg.evaluate(() => document.getElementById('clock').textContent)
  check(/^0:0[3-6]/.test(t5), `V5: after about 2.6 s of playback the clock reads ${t5.split(' ')[0]} (started near 0:01)`)
  await pg.locator('#play').click(); await ctx.close()
}
// ---- V6 chapters on the demo (scaled windows) and V8 privacy
{
  const { ctx, pg, reqs } = await open()
  const chap = await pg.evaluate(() => [...document.querySelectorAll('#chap button')].map((x) => x.textContent))
  check(chap.length >= 3 && chap.length <= 8, `V6: the demo has ${chap.length} chapters (3 to 8)`)
  await pg.locator('#chap button').nth(2).click(); await pg.waitForTimeout(150)
  const ck = await pg.evaluate(() => ({ t: document.getElementById('clock').textContent.split(' ')[0], cur: document.querySelector('#chap button[aria-current=true]').textContent }))
  check(ck.cur.startsWith('III'), `V6: clicking a chapter bookmark seeks there (${ck.cur}, clock ${ck.t})`)
  const size = fs.statSync(file).size
  check(size < 150000, `V8: the page file is ${size} bytes (no embedded audio, under 150000)`)
  check(reqs.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')), 'V8: the page made no network requests')
  await ctx.close()
}
// ---- reduced motion
{
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' }), pg = await ctx.newPage()
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '', null, { timeout: 30000 })
  const st = await pg.evaluate(() => document.getElementById('play').textContent)
  check(st === 'Play', 'V9: with reduced motion nothing plays on its own')
  await ctx.close()
}
// ---- optional real files (local only): V2 cross-check against numpy, V3 duration vs ffprobe, V6 chapters
const files = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)
for (const f of files) {
  const label = path.extname(f).toLowerCase()
  const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'json', f]).toString())
  const want = parseFloat(probe.format.duration)
  const { ctx, pg } = await open(); await load(pg, f)
  const got = await pg.evaluate(() => { const m = document.getElementById('srcsub').textContent.match(/^(\d+) s/); const c = document.getElementById('clock').textContent.split('/')[1].trim().split(':'); return +c[0] * 60 + +c[1] })
  check(Math.abs(got - want) <= 1.01, `V3 ${label}: duration ${got} s against ffprobe ${want.toFixed(1)} s (clock is whole seconds)`)
  const chap = await pg.evaluate(() => [...document.querySelectorAll('#chap button')].map((x) => x.textContent))
  if (want < 20) console.log(`- V6 ${label}: not applicable, the clip is ${want.toFixed(1)} s and chapters need about 9 s or more (${chap.length} found)`)
  else check(chap.length >= 3 && chap.length <= 8, `V6 ${label}: ${chap.length} chapters (${chap.join(' ')}) (3 to 8)`)
  // V2: independent numpy recomputation of the band values, compared with the bar heights the page draws
  try {
    const fracs = [0.08, 0.17, 0.25, 0.33, 0.42, 0.5, 0.58, 0.67, 0.75, 0.83, 0.92]
    const py = JSON.parse(execFileSync('python3', [path.join(path.dirname(new URL(import.meta.url).pathname), 'phosphor_crosscheck.py'), f, ...fracs.map(String)], { maxBuffer: 1 << 26 }).toString())
    await pg.evaluate(() => { const r = document.getElementById('m1'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); const s = document.getElementById('res'); s.value = 9; s.dispatchEvent(new Event('input', { bubbles: true })) })
    const xs = [], ys = []
    for (const fr of fracs) {
      await seek(pg, fr); await pg.waitForTimeout(60)
      const bars = await pg.evaluate(() => { const c = document.getElementById('cv'), W = c.width, H = c.height, g = c.getContext('2d'), base = Math.floor(H * 0.86), bw = W / 64, out = []; for (let b = 0; b < 64; b++) { const x = Math.floor((b + 0.5) * bw), col = g.getImageData(x, 0, 1, base).data; let n = 0; for (let y = base - 1; y >= 0; y--) { const i = y * 4; if (col[i] < 60 && col[i + 1] > 190 && col[i + 2] > 190) n++; else break } out.push(n / (H * 0.78)) } return out })
      const want = py.frames[String(fr)]
      for (let b = 0; b < 64; b++) { xs.push(bars[b]); ys.push(want[b]) }
    }
    const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length, mx = mean(xs), my = mean(ys)
    let sxy = 0, sxx = 0, syy = 0; for (let i = 0; i < xs.length; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; syy += (ys[i] - my) ** 2 }
    const r = sxy / Math.sqrt(sxx * syy)
    check(r >= 0.98, `V2 ${label}: bar heights against numpy band values, Pearson ${r.toFixed(4)} over ${xs.length} values (want 0.98 or more)`)
  } catch (e) { check(false, `V2 ${label}: cross-check could not run (${String(e.message).slice(0, 80)})`) }
  await ctx.close()
}
check(errors.length === 0, `V9: no console errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close(); fs.rmSync(tmp, { recursive: true, force: true })
process.exit(fails.length ? 1 : 0)
