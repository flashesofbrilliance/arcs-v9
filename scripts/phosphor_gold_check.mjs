#!/usr/bin/env node
// phosphor_gold_check.mjs: Q1 to Q5 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 15). The Gold chime.
// Usage: node scripts/phosphor_gold_check.mjs <page.html>   (optional PHOSPHOR_FILES=song.mp3 adds the loud-song ceiling check)
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_gold_check.mjs <page.html>'); process.exit(2) }
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
const goertzel = (d0, f, sr) => { const d = d0.map((v, i) => v * (0.5 - 0.5 * Math.cos(2 * Math.PI * i / (d0.length - 1)))), w = 2 * Math.PI * f / sr, c = 2 * Math.cos(w); let s1 = 0, s2 = 0; for (const v of d) { const s = v + c * s1 - s2; s2 = s1; s1 = s } return Math.sqrt(s1 * s1 + s2 * s2 - c * s1 * s2) / d.length }
const rmsOf = (d) => Math.sqrt(d.reduce((s, v) => s + v * v, 0) / d.length)
const root = await E(() => window.PhosphorTest.fx.gold.root())
const k = 12 * Math.log2(root / 440)
check(root >= 200 && root <= 520 && Math.abs(k - Math.round(k)) < 1e-6, `Q1: the root is ${root.toFixed(2)} Hz, inside 200 to 520 Hz (a low root is lifted by octaves) and an exact 12-tone pitch (${k.toFixed(3)} semitones from A 440)`)
await E(() => window.PhosphorTest.fx.gold.play()); await pg.waitForTimeout(120)
const sr = await E(() => window.PhosphorTest.fx.sr()), buf = await E(() => window.PhosphorTest.fx.bufs())
const at = goertzel(buf, root, sr), fifth = goertzel(buf, root * 1.5, sr), off = goertzel(buf, root * 1.26, sr)
check(at > off * 5 && fifth > off * 5, `Q2: energy at the root (${at.toFixed(4)}) and a fifth above (${fifth.toFixed(4)}) well above a nearby frequency (${off.toFixed(5)})`)
const r1 = rmsOf(await E(() => window.PhosphorTest.fx.bufs())); await pg.waitForTimeout(2500); const r2 = rmsOf(await E(() => window.PhosphorTest.fx.bufs()))
check(r2 < r1 * 0.1, `Q3: the chime decays (rms ${r1.toFixed(4)} then ${r2.toFixed(5)} 2.5 s later)`)
for (let i = 0; i < 8; i++) await E(() => window.PhosphorTest.fx.gold.play())
check((await E(() => window.PhosphorTest.fx.gold.voices())) <= 4, `Q5: pressing it eight times in a row rings at most four chimes (${await E(() => window.PhosphorTest.fx.gold.voices())})`)
const song = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)[0]
if (song) {
  await pg.setInputFiles('#file', song); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 })
  await E(() => document.getElementById('play').click()); await pg.waitForTimeout(500)
  const sroot = await E(() => window.PhosphorTest.fx.gold.root())
  let pk = 0; for (let i = 0; i < 6; i++) { await E(() => window.PhosphorTest.fx.gold.play()); for (let j = 0; j < 12; j++) { pk = Math.max(pk, await E(() => window.PhosphorTest.outPeak())); await pg.waitForTimeout(60) } }
  check(pk <= 0.5, `Q4: over a loud song (root ${sroot.toFixed(1)} Hz) the chime keeps the output at ${pk.toFixed(3)} (ceiling 0.5)`)
}
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
