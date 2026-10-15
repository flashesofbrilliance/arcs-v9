#!/usr/bin/env node
// phosphor_stage_check.mjs: checks the beat-synced resolution loop (L1 to L5) and full screen (F1 to F4).
// Makes its own 120 BPM click track, so it needs no local songs. Usage: node scripts/phosphor_stage_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_stage_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

// 24 s mono 22.05 kHz click track: a decaying 60 Hz kick every 0.5 s starting at 0.3 s (120 BPM), plus a quiet pad.
const sr = 22050, secs = 24, n = sr * secs, pcm = Buffer.alloc(44 + n * 2)
pcm.write('RIFF', 0); pcm.writeUInt32LE(36 + n * 2, 4); pcm.write('WAVEfmt ', 8); pcm.writeUInt32LE(16, 16); pcm.writeUInt16LE(1, 20); pcm.writeUInt16LE(1, 22)
pcm.writeUInt32LE(sr, 24); pcm.writeUInt32LE(sr * 2, 28); pcm.writeUInt16LE(2, 32); pcm.writeUInt16LE(16, 34); pcm.write('data', 36); pcm.writeUInt32LE(n * 2, 40)
for (let i = 0; i < n; i++) {
  const t = i / sr, k = (t - 0.3) % 0.5, on = t >= 0.3
  const kick = on ? Math.exp(-k * 18) * Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-k * 30)) * k) * 0.9 : 0
  const pad = 0.05 * Math.sin(2 * Math.PI * 220 * t)
  pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, kick + pad)) * 32767), 44 + i * 2)
}
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav'); fs.writeFileSync(wav, pcm)

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
await pg.goto(url)
await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
await pg.setInputFiles('#file', wav)
await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 60000 })

const info = await pg.evaluate(() => ({ bpm: window.PhosphorTest.bpm(), g0: window.PhosphorTest.grid0() }))
check(Math.abs(info.bpm - 120) <= 2, `L1: the detector reads the 120 BPM click track as ${info.bpm} BPM`)
check(Math.abs(info.g0 - 0.3 % 0.5) < 0.06, `L1: the grid starts on the first kick (origin ${info.g0.toFixed(3)} s, wanted 0.300)`)

const seq = await pg.evaluate(() => {
  const T = window.PhosphorTest, g0 = T.grid0(), P = 0.5, out = {}
  for (const dir of ['up', 'down', 'pp']) {
    T.loop(true, 1, dir); out[dir] = []
    for (let b = 0; b < 4; b++) out[dir].push(T.rungAt(g0 + b * P + 0.1))
  }
  T.loop(true, 2, 'up'); out.bar2 = []
  for (let b = 0; b < 8; b++) out.bar2.push(T.rungAt(g0 + b * P + 0.1))
  T.loop(true, 1, 'up'); out.within = []
  for (let k = 0; k < 10; k++) out.within.push(T.rungAt(g0 + 0.02 + k * 0.045))
  out.wrap = [T.rungAt(g0 + 0.1), T.rungAt(g0 + 2.0 + 0.1), T.rungAt(g0 + 4.0 + 0.1)]
  T.loop(false, 2, 'up'); out.off = T.rungAt(g0 + 0.1)
  return out
})
const inc = (a) => a.every((v, i) => i === 0 || v >= a[i - 1]), dec = (a) => a.every((v, i) => i === 0 || v <= a[i - 1])
check(inc(seq.up) && seq.up[0] < seq.up[3] && seq.up[3] === 8, `L2: forward runs coarse to fine over one bar (${seq.up.join(' ')})`)
check(dec(seq.down) && seq.down[0] === 8 && seq.down[3] < seq.down[0], `L2: backward runs fine to coarse (${seq.down.join(' ')})`)
const pp = seq.pp
check(pp[0] < Math.max(...pp) && pp[pp.length - 1] < Math.max(...pp) && pp[1] === pp[2], `L2: forward and back rises then falls and returns near where it began (${pp.join(' ')})`)
check(new Set(seq.bar2).size >= 7 && inc(seq.bar2), `L3: two bars spread the ladder over eight beats (${seq.bar2.join(' ')})`)
check(new Set(seq.within).size <= 2, `L4: the rung changes only on a beat, not between beats (${seq.within.join(' ')})`)
check(seq.wrap[0] === seq.wrap[1] && seq.wrap[1] === seq.wrap[2], `L4: the loop repeats exactly each cycle (${seq.wrap.join(' ')})`)
check(seq.off === 8, `L5: turning the loop off hands control back to the Resolution slider (rung ${seq.off})`)

await pg.click('details.grp:has(#rloop) > summary'); await pg.check('#rloop'); await pg.check('#rd1', { force: true }).catch(() => {})
check(await pg.evaluate(() => document.getElementById('res').disabled), 'L5: the Resolution slider locks while the loop runs')
await pg.uncheck('#rloop')

// full screen
check(await pg.evaluate(() => !document.getElementById('frame').classList.contains('fs')), 'F1: the page opens windowed')
await pg.click('#fsb')
check(await pg.evaluate(() => document.getElementById('frame').classList.contains('fs') && window.PhosphorTest.fs()), 'F1: the full screen button turns the stage on')
const dims = await pg.evaluate(() => { const c = document.getElementById('cv'), r = c.getBoundingClientRect(); return { w: c.width, h: c.height, rw: r.width, rh: r.height, vw: innerWidth, vh: innerHeight } })
check(dims.rw >= dims.vw - 2 && dims.rh >= dims.vh - 80, `F2: the picture fills the screen (${Math.round(dims.rw)} x ${Math.round(dims.rh)} of ${dims.vw} x ${dims.vh})`)
check(dims.w >= 1600, `F2: the canvas is redrawn larger for full screen (${dims.w} x ${dims.h})`)
await pg.click('#hplay'); await pg.waitForTimeout(700)
check(await pg.evaluate(() => window.PhosphorTest.tnow() > 0.3), 'F3: the full screen bar plays the song')
await pg.waitForTimeout(3200)
check(await pg.evaluate(() => document.getElementById('frame').classList.contains('idle')), 'F3: the bar fades out after a few seconds of no movement')
await pg.mouse.move(400, 400); await pg.mouse.move(420, 410)
check(await pg.evaluate(() => !document.getElementById('frame').classList.contains('idle')), 'F3: moving the pointer brings the bar back')
await pg.keyboard.press('Escape')
check(await pg.evaluate(() => !document.getElementById('frame').classList.contains('fs') && document.getElementById('cv').width === 960), 'F4: Escape leaves full screen and restores the canvas')
await pg.keyboard.press('f')
check(await pg.evaluate(() => window.PhosphorTest.fs()), 'F4: the F key toggles full screen on')
await pg.keyboard.press('f')
check(await pg.evaluate(() => !window.PhosphorTest.fs()), 'F4: and off again')

check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
