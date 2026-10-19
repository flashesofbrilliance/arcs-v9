#!/usr/bin/env node
// phosphor_lowband_check.mjs: L-low1 to L-low3 (amendment 58): the lowest bands separate two bass tones 10 Hz apart.
// Usage: node scripts/phosphor_lowband_check.mjs <page.html>   (writes its own test tones to a temp folder)
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]
if (!page) { console.log('usage: node scripts/phosphor_lowband_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'phos-lowband-'))
const wav = (hz, name) => { const sr = 44100, n = sr * 6, b = Buffer.alloc(44 + n * 2); b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40); for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(12000 * Math.sin(2 * Math.PI * hz * i / sr)), 44 + i * 2); const f = path.join(dir, name); fs.writeFileSync(f, b); return f }
const f50 = wav(50, 't50.wav'), f60 = wav(60, 't60.wav'), f200 = wav(200, 't200.wav')
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href
const run = async (file) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200); await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 }); const r = await pg.evaluate(() => window.PhosphorTest.bandMean()); await ctx.close(); return r }
const top = (r) => r.mean.indexOf(Math.max(...r.mean))
const a = await run(f50), c = await run(f60), d = await run(f200)
const ia = top(a), ic = top(c), id = top(d)
check(ia !== ic, `L-low1: 50 Hz and 60 Hz peak in different bands (${ia} at ${a.centers[ia].toFixed(1)} Hz, ${ic} at ${c.centers[ic].toFixed(1)} Hz)`)
check(Math.abs(a.centers[ia] - 50) < 5 && Math.abs(c.centers[ic] - 60) < 6, `L-low2: each peak band center is within one band of its tone`)
check(Math.abs(d.centers[id] - 200) < 20, `L-low3: a 200 Hz tone still peaks near 200 Hz (${d.centers[id].toFixed(1)} Hz)`)
await b.close(); fs.rmSync(dir, { recursive: true, force: true })
process.exit(failed() ? 1 : 0)
