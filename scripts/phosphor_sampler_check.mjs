#!/usr/bin/env node
// phosphor_sampler_check.mjs: checks Z1 to Z3, C1, A1, A2, B1 to B4 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 8).
// Uses its own 120 BPM click track (kicks on 0.3 s + 0.5 s k). Usage: node scripts/phosphor_sampler_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_sampler_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav')
if (!fs.existsSync(wav)) { const sr = 22050, n = sr * 24, b = Buffer.alloc(44 + n * 2); b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40); for (let i = 0; i < n; i++) { const t = i / sr, k = (t - 0.3) % 0.5; b.writeInt16LE(Math.round((t >= 0.3 ? Math.exp(-k * 18) * Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-k * 30)) * k) * 0.9 : 0) * 32767), 44 + i * 2) } fs.writeFileSync(wav, b) }

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
await pg.setInputFiles('#file', wav)
await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 60000 })
await pg.evaluate(() => { document.getElementById('slices').open = true })
const S = (f, ...a) => pg.evaluate(f, ...a)
const DUR = await S(() => window.PhosphorTest.dur())

// Z1 zoom keeps the time under the cursor
const z1 = await S(() => { const T = window.PhosphorTest.sampler, d = window.PhosphorTest.dur(); T.zoom(0.25, 10); const v = T.view(); return { span: v.b - v.a, frac: (10 - v.a) / (v.b - v.a), d } })
check(Math.abs(z1.span - z1.d * 0.25) < 0.05 && Math.abs(z1.frac - 10 / z1.d) < 0.02, `Z1: zooming to a quarter keeps the time under the cursor fixed (window ${z1.span.toFixed(2)} s of ${z1.d.toFixed(1)}, cursor fraction ${z1.frac.toFixed(3)} against ${(10 / z1.d).toFixed(3)})`)
const clamp = await S((d) => { const T = window.PhosphorTest.sampler; T.set(-5, 3); const a = T.view(); T.set(d - 2, d + 9); const b = T.view(); return { a, b } }, DUR)
check(clamp.a.a === 0 && clamp.b.b <= DUR + 1e-9 && clamp.b.a >= 0, `Z1: the window stays inside the song (${clamp.a.a}-${clamp.a.b.toFixed(2)}, ${clamp.b.a.toFixed(2)}-${clamp.b.b.toFixed(2)})`)

// Z2 pixels differ, Z3 pan
await S(() => window.PhosphorTest.sampler.set(0, window.PhosphorTest.dur()))
const full = await S(() => window.PhosphorTest.sampler.bg())
await S(() => window.PhosphorTest.sampler.set(2, 4)); const zoomed = await S(() => window.PhosphorTest.sampler.bg())
check(full !== zoomed, `Z2: the strip draws different pixels when zoomed (${full} against ${zoomed})`)
await S(() => window.PhosphorTest.sampler.set(0, 6))
await pg.evaluate(() => { const z = document.getElementById('zpan'); z.value = 500; z.dispatchEvent(new Event('input')) })
const pan = await S(() => window.PhosphorTest.sampler.view())
check(Math.abs(pan.a - (DUR - 6) * 0.5) < 0.05 && Math.abs(pan.b - pan.a - 6) < 1e-6, `Z3: the pan slider at the middle puts the window in the middle (${pan.a.toFixed(2)} to ${pan.b.toFixed(2)})`)
await S(() => window.PhosphorTest.sampler.set(0, window.PhosphorTest.dur()))

// C1 scrub on the ruler
await pg.evaluate(() => document.getElementById('strip').scrollIntoView({ block: 'center' }))
const box = await pg.locator('#strip').boundingBox()
const ruleY = box.y + (11 / 88) * box.height
await pg.mouse.move(box.x + box.width * 0.25, ruleY); await pg.mouse.down(); await pg.mouse.move(box.x + box.width * 0.5, ruleY, { steps: 6 })
const mid = await S(() => window.PhosphorTest.sampler.now())
await pg.mouse.up()
check(Math.abs(mid - DUR * 0.5) < DUR * 0.01, `C1: dragging the ruler puts the playhead at the cursor (${mid.toFixed(2)} s, wanted ${(DUR * 0.5).toFixed(2)})`)
check((await S(() => window.PhosphorTest.slices().length)) === 0, 'C1: scrubbing did not cut a slice')

// A1 slice at hits
await pg.click('label[for="ah2"]'); await pg.click('#ash')
const a1 = await S(() => { const T = window.PhosphorTest, on = T.magnets().filter((m) => m.k === 'onset').map((m) => m.t), sl = T.slices(); let worst = 0, gaps = 0; sl.forEach((s, i) => { worst = Math.max(worst, Math.min(...on.map((o) => Math.abs(o - s.t0)))); if (i && Math.abs(sl[i - 1].t1 - s.t0) > 1e-6) gaps++ }); return { n: sl.length, worst, gaps, on: on.length } })
check(a1.n > 8 && a1.n <= 32 && a1.worst < 0.04 && a1.gaps === 0, `A1: Slice at hits (Many) cut ${a1.n} contiguous slices, every cut within ${(a1.worst * 1000).toFixed(0)} ms of an onset (${a1.on} onsets)`)

// A2 on the beat, quarter notes
await pg.click('label[for="ab0"]'); await pg.click('#asb')
const a2 = await S(() => { const sl = window.PhosphorTest.slices(); const lens = sl.slice(0, -1).map((s) => s.t1 - s.t0); return { n: sl.length, worst: Math.max(...lens.map((l) => Math.abs(l - 0.5))) } })
check(a2.n >= 40 && a2.n <= 64, `A2: quarter note slices at 120 BPM fill the cap of 64 or the song (${a2.n} slices)`)
check(a2.worst < 0.02, `A2: interior slices are 0.5 s within ${(a2.worst * 1000).toFixed(1)} ms`)

// B1 plan math
const b1 = await S(() => {
  const T = window.PhosphorTest, P = T.sampler.plan, sl = T.slices(), same = P(120, 120), half = P(120, 60), dbl = P(120, 240)
  const rel = (p) => p.ev.map((e) => e.st)
  const idOk = sl.slice(0, 8).every((s, i) => Math.abs(same.ev[i].st - (s.t0 - sl[0].t0)) < 1e-6)
  const halfOk = half.ev.slice(0, 8).every((e, i) => Math.abs(e.st - 2 * same.ev[i].st) < 1e-6) && Math.abs(half.loopLen - 2 * same.loopLen) < 1e-6
  const dblOk = dbl.ev.slice(0, 8).every((e, i) => Math.abs(e.st - 0.5 * same.ev[i].st) < 1e-6)
  const noOverlap = dbl.ev.every((e, i) => i === dbl.ev.length - 1 || e.st + e.dur <= dbl.ev[i + 1].st + 1e-9)
  const halfFull = half.ev.every((e) => Math.abs(e.dur - e.len) < 1e-9 || e.dur <= e.len)
  return { idOk, halfOk, dblOk, noOverlap, halfFull }
})
check(b1.idOk, 'B1: at the same tempo the plan is the identity')
check(b1.halfOk, 'B1: at half tempo every start time doubles and so does the loop')
check(b1.dblOk && b1.noOverlap, 'B1: at double tempo start times halve and no slice runs into the next')

// B2 to B4 play it at half tempo
await S(() => { document.getElementById('sbpm').value = 120; document.getElementById('tbpm').value = 60 })
await pg.click('#spl'); await pg.waitForTimeout(500)
check(await S(() => window.PhosphorTest.sampler.on()), 'B2: Play slices at that tempo starts')
const clk = []; for (let i = 0; i < 12; i++) { clk.push(await S(() => window.PhosphorTest.sampler.now())); await pg.waitForTimeout(150) }
check(clk.every((v) => v >= 0 && v < DUR) && clk.some((v, i) => i && v !== clk[i - 1]), `B2: the picture clock follows the sounding slice and stays inside the song (${clk.slice(0, 6).map((v) => v.toFixed(2)).join(' ')} ...)`)
const rates = await S(() => window.PhosphorTest.sampler.rates())
check(rates.length > 8 && rates.every((r) => r === 1), `B3: every sliced source plays at normal rate, so pitch is kept (${rates.length} sources)`)
await pg.click('#spl'); await pg.waitForTimeout(200)
check(!(await S(() => window.PhosphorTest.sampler.on())) && (await S(() => document.getElementById('play').textContent)) === 'Play', 'B4: stopping releases the sliced loop')
check(reqs.length === 0, `no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
