#!/usr/bin/env node
// phosphor_seq_check.mjs: checks Q1 to Q6 and U1, U2 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 5).
// Makes its own 120 BPM click track. Optional PHOSPHOR_FILES=song.mp3 adds the quiet-spot (valley) check on a real song.
// Usage: node scripts/phosphor_seq_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_seq_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

const sr = 22050, secs = 24, n = sr * secs, pcm = Buffer.alloc(44 + n * 2)
pcm.write('RIFF', 0); pcm.writeUInt32LE(36 + n * 2, 4); pcm.write('WAVEfmt ', 8); pcm.writeUInt32LE(16, 16); pcm.writeUInt16LE(1, 20); pcm.writeUInt16LE(1, 22)
pcm.writeUInt32LE(sr, 24); pcm.writeUInt32LE(sr * 2, 28); pcm.writeUInt16LE(2, 32); pcm.writeUInt16LE(16, 34); pcm.write('data', 36); pcm.writeUInt32LE(n * 2, 40)
for (let i = 0; i < n; i++) { const t = i / sr, k = (t - 0.3) % 0.5, on = t >= 0.3; const kick = on ? Math.exp(-k * 18) * Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-k * 30)) * k) * 0.9 : 0; pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, kick + 0.05 * Math.sin(2 * Math.PI * 220 * t))) * 32767), 44 + i * 2) }
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav'); fs.writeFileSync(wav, pcm)

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = []
async function open(file) {
  const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
  await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
  await pg.setInputFiles('#file', file)
  await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 })
  return pg
}
const pg = await open(wav)

// Q1 beat: exactly on the grid
const q1 = await pg.evaluate(() => { const S = window.PhosphorTest.seq; S.quant('beat'); const st = S.step(), b0 = S.base(); let worst = 0; for (let j = 0; j < 32; j++) worst = Math.max(worst, Math.abs(S.fire(j) - (b0 + j * st))); return { worst, st } })
check(q1.worst < 0.001, `Q1: Beat steps land exactly on the grid (worst error ${(q1.worst * 1000).toFixed(2)} ms, step ${(q1.st * 1000).toFixed(0)} ms)`)

// Q2 hits: snap to a real onset inside half a step, leave alone when none is near
const q2 = await pg.evaluate(() => {
  const T = window.PhosphorTest, S = T.seq, on = T.magnets().filter((m) => m.k === 'onset').map((m) => m.t)
  S.quant('onset'); const o = on[6], tol = 0.1
  return { o, near: S.snap(o + 0.04, tol), far: S.snap(o + 0.2, tol), n: on.length, isOnset: on.includes(S.snap(o - 0.03, tol)) }
})
check(q2.n > 10 && Math.abs(q2.near - q2.o) < 1e-9 && q2.isOnset, `Q2: Hits pulls a time 40 ms off a hit onto the hit (${q2.n} onsets; ${q2.near.toFixed(3)} against ${q2.o.toFixed(3)})`)
check(Math.abs(q2.far - (q2.o + 0.2)) < 1e-9, 'Q2: Hits leaves a time alone when no hit is inside the range')

// Q3 slice edges
const q3 = await pg.evaluate(() => { const T = window.PhosphorTest; T.add(10, 12); const S = T.seq; S.quant('edge'); return { a: S.snap(10.03, 0.1), b: S.snap(11.0, 0.1), c: S.snap(12.04, 0.1) } })
check(Math.abs(q3.a - 10) < 1e-6 && Math.abs(q3.c - 12) < 1e-6 && Math.abs(q3.b - 11) < 1e-9, `Q3: Slice edges pull to the cut edges and ignore the middle (${q3.a}, ${q3.b}, ${q3.c})`)
await pg.evaluate(() => window.PhosphorTest.seq.quant('beat'))

// Q4 gate lengths
const q4 = await pg.evaluate(() => {
  const S = window.PhosphorTest.seq, st = S.step(), out = {}
  S.clear(); S.set('stutter', 3, 1)
  for (const g of [0.25, 0.5, 1]) { S.gate(g); let on = 0, t0 = S.base() + 3 * st - 0.05; for (let t = t0; t < t0 + st * 2; t += 0.001) if (S.active(t).stutter) on++; out[g] = on / 1000 / st }
  return out
})
check(Object.entries(q4).every(([g, v]) => Math.abs(v - +g) < 0.03), `Q4: the effect stays on for gate x step (${JSON.stringify(q4)})`)

// Q5 zoom lane
const q5 = await pg.evaluate(() => { const S = window.PhosphorTest.seq; S.clear(); S.set('jog', 5, 3); const a = S.active(S.base() + 5 * S.step() + 0.01); return a.jog })
check(q5 === 3, `Q5: a Zoom cell holding 3 asks for stage 3 (${q5})`)

// Q6 playing the pattern turns the stutter on and stopping releases it
await pg.evaluate(() => { const S = window.PhosphorTest.seq; S.clear(); for (let i = 0; i < 16; i += 2) S.set('stutter', i, 1); S.gate(1); S.on(true) })
await pg.click('#play'); let sawOn = false
for (let i = 0; i < 30 && !sawOn; i++) { await pg.waitForTimeout(100); sawOn = await pg.evaluate(() => !!window.PhosphorTest.glitch().stut) }
check(sawOn, 'Q6: playing a pattern turns the stutter on')
await pg.click('#play'); await pg.waitForTimeout(400)
check(await pg.evaluate(() => !window.PhosphorTest.glitch().stut), 'Q6: pausing releases the stutter')
await pg.evaluate(() => { window.PhosphorTest.seq.on(false); window.PhosphorTest.seq.clear() })

// U1 grid
await pg.click('details.grp:has(#seqg) > summary')
const u1 = await pg.evaluate(() => ({ lanes: new Set([...document.querySelectorAll('#seqg .sq')].map((e) => e.dataset.l)).size, cells: document.querySelectorAll('#seqg .sq').length }))
check(u1.lanes === 7 && u1.cells === 112, `U1: the grid has 7 lanes of 16 cells (${u1.lanes}, ${u1.cells})`)
await pg.click('#seqg .sq[data-l="rgb"][data-i="2"]'); check(await pg.evaluate(() => document.querySelector('#seqg .sq[data-l="rgb"][data-i="2"]').getAttribute('aria-pressed') === 'true'), 'U1: a cell turns on when tapped')
for (let i = 0; i < 5; i++) await pg.click('#seqg .sq[data-l="jog"][data-i="0"]')
check(await pg.evaluate(() => document.querySelector('#seqg .sq[data-l="jog"][data-i="0"]').textContent === '5'), 'U1: a Zoom cell counts up to stage 5')
await pg.click('#seqg .sq[data-l="jog"][data-i="0"]'); check(await pg.evaluate(() => document.querySelector('#seqg .sq[data-l="jog"][data-i="0"]').getAttribute('aria-pressed') === 'false'), 'U1: and wraps to off')

// U2 full screen panel
check(await pg.evaluate(() => getComputedStyle(document.getElementById('seqo')).display === 'none'), 'U2: the Steps panel is hidden while windowed')
await pg.click('#fsb'); await pg.click('#hsteps')
check(await pg.evaluate(() => getComputedStyle(document.getElementById('seqo')).display !== 'none'), 'U2: the Steps button opens the panel in full screen')
await pg.click('#seqf .sq[data-l="blocks"][data-i="7"]')
check(await pg.evaluate(() => document.querySelector('#seqg .sq[data-l="blocks"][data-i="7"]').getAttribute('aria-pressed') === 'true'), 'U2: a cell tapped in full screen is the same pattern as in the Grown-up controls')
await pg.keyboard.press('Escape')
check(await pg.evaluate(() => !document.getElementById('frame').classList.contains('steps')), 'U2: leaving full screen closes the panel')

// optional: valley snap on a real song
const real = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)[0]
if (real) {
  const rp = await open(real)
  const v = await rp.evaluate(() => { const T = window.PhosphorTest, S = T.seq, va = T.magnets().filter((m) => m.k === 'valley').map((m) => m.t); S.quant('valley'); const o = va[2]; return { n: va.length, near: S.snap(o + 0.05, 0.1) - o } })
  check(v.n > 3 && Math.abs(v.near) < 1e-9, `Q2b: Quiet spots snaps to a real valley on a real song (${v.n} valleys)`)
}
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
