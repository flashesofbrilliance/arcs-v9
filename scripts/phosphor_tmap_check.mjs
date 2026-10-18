#!/usr/bin/env node
// phosphor_tmap_check.mjs: the tempo map (amendment 39). A synthetic song whose tempo changes: 12 beats at 100 BPM, 12 at 120, 12 at 90 (about 21 s; the page analyses the first 24 s).
// Usage: node scripts/phosphor_tmap_check.mjs <page.html>
import { chromium } from 'playwright'
import { writeFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_tmap_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
// ground truth: beat times and the wav
const T0 = 0.3, SEG = [[100, 12], [120, 12], [90, 12]], beats = []; { let t = T0; for (const [bpm, n] of SEG) for (let i = 0; i < n; i++) { beats.push(t); t += 60 / bpm } beats.push(t) }
const SR = 22050, len = Math.ceil((beats[36] + 2) * SR), pcm = new Int16Array(len)
beats.forEach((bt, k) => { const f = k % 4 === 0 ? 1500 : 1000, s0 = Math.round(bt * SR); for (let i = 0; i < 0.04 * SR && s0 + i < len; i++) pcm[s0 + i] = Math.round(Math.sin(2 * Math.PI * f * i / SR) * Math.exp(-i / (0.012 * SR)) * 26000) })
const hdr = Buffer.alloc(44); hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + len * 2, 4); hdr.write('WAVEfmt ', 8); hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(1, 22); hdr.writeUInt32LE(SR, 24); hdr.writeUInt32LE(SR * 2, 28); hdr.writeUInt16LE(2, 32); hdr.writeUInt16LE(16, 34); hdr.write('data', 36); hdr.writeUInt32LE(len * 2, 40)
const wav = path.join(mkdtempSync(path.join(tmpdir(), 'tmap-')), 'drift.wav'); writeFileSync(wav, Buffer.concat([hdr, Buffer.from(pcm.buffer)]))
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', wav); await pg.waitForTimeout(3500)
if (process.env.TMAP_DEBUG) { const on = (await pg.evaluate(() => window.PhosphorTest.magnets().filter((m) => m.k === 'onset').map((m) => +m.t.toFixed(3)))); console.log('onsets', on.length, on.slice(0, 20).join(' '), '| beats', beats.slice(0, 12).map((x) => x.toFixed(3)).join(' ')) }
const T = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.tmap[fn](...a), [fn, a]), Q = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.pins[fn](...a), [fn, a])
const nearest = (arr, t) => arr.reduce((m, x) => Math.min(m, Math.abs(x - t)), 9)
// control: one steady tempo (the average, 110 BPM) can not follow the drift
await pg.evaluate((t0) => window.PhosphorTest.tap.set(110, t0), T0); const flat = await T('grid'); const flatErr = Math.max(...beats.map((bt) => nearest(flat, bt)))
check(flatErr > 0.08, `C0: one steady 110 BPM grid misses the true beats by up to ${(flatErr * 1000).toFixed(0)} ms (the problem)`)
// anchors at beats 0, 16, 32, 48
for (const k of [0, 12, 24, 36]) { await pg.evaluate((t) => window.PhosphorTest.seek(t), beats[k]); await pg.evaluate(() => { const c = document.getElementById('pinanchor'); if (!c.checked) c.click() }); await Q('add', 'beat ' + k, 'note', true) }
await pg.fill('#pinbeats', '12,12,12'); if (process.env.TMAP_DEBUG) console.log('anchors', JSON.stringify((await Q('list')).map((p) => [p.note, p.at])), 'truth', [0, 16, 32, 48].map((k) => beats[k].toFixed(3)).join(' '), 'dur', await pg.evaluate(() => window.PhosphorTest.dur()))
const made = await T('make'); await pg.waitForTimeout(300)
check(made && JSON.stringify(made.segs) === JSON.stringify(['100.0', '120.0', '90.0']), `M1: the segment tempos read back as ${made && made.segs.join(', ')} (true 100, 120, 90)`)
let worst = 0; for (let k = 0; k <= 36; k++) worst = Math.max(worst, Math.abs((await T('time', k)) - beats[k]))
check(worst < 0.003, `M2: the map puts all 37 beats within ${(worst * 1000).toFixed(2)} ms of the true beat times`)
const g = await T('grid'); const gErr = Math.max(...beats.slice(0, 37).map((bt) => nearest(g, bt)))
check(gErr < 0.003, `M3: the grid magnets (what the strip snaps to) sit within ${(gErr * 1000).toFixed(2)} ms of every true beat`)
const mid = [(beats[14] + beats[15]) / 2, (beats[30] + beats[31]) / 2]; const bt = await Promise.all(mid.map((t) => T('beat', t)))
check(Math.abs(bt[0] - 14.5) < 0.01 && Math.abs(bt[1] - 30.5) < 0.01, `M4: the beat position halfway between true beats 14 and 15 reads ${bt[0].toFixed(3)} (want 14.5), and 30 and 31 reads ${bt[1].toFixed(3)} (want 30.5)`)
const bars = (await T('bars', beats[13])).slice(0, 6); const wantBars = [16, 20, 24, 28, 32, 36].map((k) => beats[k])
check(bars.every((x, i) => Math.abs(x - wantBars[i]) < 0.003), `M5: the next six bar lines after beat 13 land on true beats 16, 20, 24 ... (worst ${(Math.max(...bars.map((x, i) => Math.abs(x - wantBars[i]))) * 1000).toFixed(2)} ms)`)
await pg.evaluate((t) => window.PhosphorTest.seek(t), beats[17] + 0.04); await pg.evaluate(() => { const c = document.getElementById('pinanchor'); if (c.checked) c.click() }); await Q('add', 'near beat 17', 'note', false)
const pins = await Q('list'), snap = pins.find((p) => p.note === 'near beat 17')
check(snap && Math.abs(snap.at - beats[17]) < 0.004, `M6: a pin dropped 40 ms after beat 17 snaps to the mapped beat (${snap && snap.at.toFixed(3)} against ${beats[17].toFixed(3)})`)
// M9 estimate path: two anchors a whole stretch apart with no typed counts still count the beats (12 beats at 100 BPM against a 110 BPM song tempo)
await Q('clear'); await pg.evaluate(() => window.PhosphorTest.tap.set(110, 0.3)); for (const k of [0, 12]) { await pg.evaluate((t) => window.PhosphorTest.seek(t), beats[k]); await pg.evaluate(() => { const c = document.getElementById('pinanchor'); if (!c.checked) c.click() }); await Q('add', 'e' + k, 'note', true) }
await pg.fill('#pinbeats', ''); const est = await T('make'); check(est && est.segs.join() === '100.0' && /estimate/.test(await pg.textContent('#pinmsg')), `M9: with no typed counts the estimate still finds 12 beats (${est && est.segs.join()} BPM) and the message says it estimated`)
await pg.evaluate(() => window.PhosphorTest.tap.set(100, 0.3)); check(!(await T('on')), 'M7: changing the tempo by hand clears the map')
check(errs.length === 0, 'M8: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
