#!/usr/bin/env node
// phosphor_gain_check.mjs: amendment 30. A hot synthetic track (RMS about -14 dBFS, strong low-end peaks) through the real output chain must not be amplified or flat-topped.
// Usage: node scripts/phosphor_gain_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_gain_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
// build a 20 s mono WAV at 44.1 kHz: 120 BPM kicks (90 Hz decaying sine), a bass tone, and noise, scaled to -14 dBFS RMS
const SR = 44100, N = SR * 20, x = new Float32Array(N); let seed = 12345; const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1
for (let i = 0; i < N; i++) { const t = i / SR, ph = (t % 0.5), kick = Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-ph * 25)) * ph) * Math.exp(-ph * 9) * 1.0; x[i] = kick + 0.25 * Math.sin(2 * Math.PI * 55 * t) + 0.18 * rnd() }
let e = 0; for (const v of x) e += v * v; const rms = Math.sqrt(e / N), want = Math.pow(10, -14 / 20), k = want / rms; let pk = 0; for (let i = 0; i < N; i++) { x[i] *= k; pk = Math.max(pk, Math.abs(x[i])) } const peak = Math.min(1, pk)
const buf = Buffer.alloc(44 + N * 2); buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 2, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22); buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 2, 40)
for (let i = 0; i < N; i++) buf.writeInt16LE(Math.max(-32768, Math.min(32767, Math.round(Math.max(-1, Math.min(1, x[i])) * 32767))), 44 + i * 2)
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), pg = await (await b.newContext({ viewport: { width: 1270, height: 990 } })).newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1000)
await pg.setInputFiles('#file', { name: 'hot.wav', mimeType: 'audio/wav', buffer: buf }); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 })
await pg.evaluate(() => window.PhosphorTest.seek(2)); await pg.click('#play'); await pg.waitForTimeout(900)
const r = await pg.evaluate(async () => { const o = { inE: 0, outE: 0, n: 0, tot: 0, hot: 0, outPk: 0 }; for (let k = 0; k < 100; k++) { const a = window.PhosphorTest.fx.bufs(), b = window.PhosphorTest.fx.bufsIn(); for (const v of a) { const x = Math.abs(v); if (x > o.outPk) o.outPk = x; o.outE += v * v; if (x > 0.45) o.hot++; o.tot++ } for (const v of b) { o.inE += v * v; o.n++ } await new Promise((r) => setTimeout(r, 50)) } return { net: 10 * Math.log10(o.outE / o.tot) - 10 * Math.log10(o.inE / o.n), pct: 100 * o.hot / o.tot, pk: o.outPk } })
check(r.net >= -3 && r.net <= 1, `G4: the hot track comes out ${r.net.toFixed(1)} dB from its input level (want between minus 3 and plus 1; input peak ${peak.toFixed(2)})`)
check(r.pct < 0.5 && r.pk <= 0.47, `G4: ${r.pct.toFixed(2)} percent of samples above 0.45 (want under 0.5) and the peak is ${r.pk.toFixed(3)} (ceiling 0.5, want at most 0.47)`)
check(errs.length === 0, `G4: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
