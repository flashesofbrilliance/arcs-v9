#!/usr/bin/env node
// phosphor_sing_check.mjs: checks S1 to S8 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 7).
// Uses Chromium's fake microphone fed from a 120 BPM click track (made by phosphor_stage_check.mjs; made here if missing).
// Usage: node scripts/phosphor_sing_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_sing_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav')
if (!fs.existsSync(wav)) { const sr = 22050, n = sr * 24, b = Buffer.alloc(44 + n * 2); b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40); for (let i = 0; i < n; i++) { const t = i / sr, k = (t - 0.3) % 0.5; b.writeInt16LE(Math.round((t >= 0.3 ? Math.exp(-k * 18) * Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-k * 30)) * k) * 0.9 : 0) * 32767), 44 + i * 2) } fs.writeFileSync(wav, b) }

const b = await pw.chromium.launch({ args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', `--use-file-for-fake-audio-capture=${wav}`, '--autoplay-policy=no-user-gesture-required'] })
const url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, permissions: ['microphone'] })
const pg = await ctx.newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
pg.on('request', (r) => { if (!r.url().startsWith('file:') && !r.url().startsWith('blob:') && !r.url().startsWith('data:')) reqs.push(r.url()) })
await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
const T = (f) => pg.evaluate(f)

// S1 mirror
await pg.click('label[for="srcB"]')
await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'armed', null, { timeout: 15000 })
let lvl = 0; for (let i = 0; i < 40 && lvl < 0.005; i++) { await pg.waitForTimeout(100); lvl = await T(() => window.PhosphorTest.sing.lvl()) }
check(lvl > 0.005, `S1: the page hears the microphone before any recording (level ${lvl.toFixed(3)})`)
const live = await T(() => window.PhosphorTest.sing.live())
check(live === 1, 'S1: one microphone track is open')

// S2 first take
await pg.click('#rec'); await pg.waitForTimeout(3000); await pg.click('#rec')
await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && document.getElementById('status').textContent === '' && document.getElementById('src').textContent === 'My loop', null, { timeout: 30000 })
const dur1 = await T(() => window.PhosphorTest.sing.dur())
check(dur1 > 2.6 && dur1 < 3.2, `S2: a three second take becomes a loop of about that length (${dur1.toFixed(2)} s)`)
await pg.waitForFunction(() => document.getElementById('play').textContent === 'Pause', null, { timeout: 8000 }).catch(() => {})
check(await T(() => window.PhosphorTest.sing.loop()), 'S2: the loop is set to repeat')
const samples = []; for (let i = 0; i < 10; i++) { samples.push(await T(() => window.PhosphorTest.tnow())); await pg.waitForTimeout(700) }
const wraps = samples.filter((v, i) => i && v < samples[i - 1]).length
check(Math.max(...samples) <= dur1 + 0.001 && wraps >= 1, `S2: playback wraps around inside the loop (${wraps} wrap, longest ${Math.max(...samples).toFixed(2)} s)`)

// S3 layer and undo
const sum1 = await T(() => window.PhosphorTest.sing.sum())
await pg.click('#rec'); check((await T(() => window.PhosphorTest.sing.state())) === 'layer', 'S3: tapping again starts a layer')
await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && window.PhosphorTest.sing.hist() === 1 && document.getElementById('status').textContent === '', null, { timeout: 30000 })
const dur2 = await T(() => window.PhosphorTest.sing.dur()), sum2 = await T(() => window.PhosphorTest.sing.sum())
check(Math.abs(dur2 - dur1) < 0.01 && Math.abs(sum2 - sum1) > 1e-3, `S3: the layer keeps the loop length and changes the sound (${dur1.toFixed(3)} then ${dur2.toFixed(3)} s)`)
await pg.click('#undo'); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && window.PhosphorTest.sing.hist() === 0, null, { timeout: 30000 })
const sum3 = await T(() => window.PhosphorTest.sing.sum())
check(Math.abs(sum3 - sum1) < 1e-6, 'S3: Undo brings back the loop before the layer')

// S4 click rounds to whole bars
await pg.click('#clr'); await pg.click('#bpm'); await pg.selectOption('#bpm', '120'); await pg.click('#clk')
await pg.click('#rec'); await pg.waitForTimeout(3400); await pg.click('#rec')
await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && document.getElementById('status').textContent === '' && document.getElementById('src').textContent === 'My loop', null, { timeout: 30000 })
const d4 = await T(() => window.PhosphorTest.sing.dur()), b4 = await T(() => window.PhosphorTest.sing.bpm()), g4 = await T(() => window.PhosphorTest.sing.gridN())
check(Math.abs(d4 - 4) < 0.02 && b4 === 120 && g4 >= 2, `S4: with the click at 120 BPM a 3.4 s take rounds to the nearest whole bar, 2 bars (${d4.toFixed(3)} s, ${b4} BPM, ${g4} grid lines)`)

// S6 nothing sent or stored, voice never offered as a file
check(reqs.length === 0, `S6: no network requests (${reqs.length})`)
const store = await T(() => JSON.stringify(Object.assign({}, localStorage)).length)
check(store < 2000, `S6: nothing audio is kept in browser storage (${store} characters)`)
check(await T(() => document.getElementById('twinb').disabled), 'S6: Save as twin stays off for a voice loop')

// S7 play log
const log = await T(() => window.PhosphorTest.sing.plog())
check(log.some((x) => x.e === 'tap:rec') && log.some((x) => x.e === 'rec') && log.every((x) => typeof x.t === 'number' && typeof x.e === 'string'), `S7: the play log holds names and times only (${log.length} events)`)

// O sing over a song: the 22.05 kHz click track is the backing while the audio context runs at its own rate
await pg.click('label[for="srcA"]'); await pg.waitForTimeout(300)
await pg.setInputFiles('#file', wav); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'My loop' && document.getElementById('status').textContent === '', null, { timeout: 60000 })
const songDur = await pg.evaluate(() => window.PhosphorTest.dur())
await pg.click('label[for="srcB"]'); await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'armed', null, { timeout: 15000 })
check(await pg.evaluate(() => window.PhosphorTest.sing.ovr()), 'O1: Sing over this song is offered when a song is loaded')
await pg.click('#ovr'); await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && document.getElementById('status').textContent === '' && document.getElementById('src').textContent === 'Song and voice', null, { timeout: 60000 })
const o1 = await pg.evaluate(() => ({ d: window.PhosphorTest.sing.dur(), sr: window.PhosphorTest.sing.srate(), ac: new AudioContext().sampleRate }))
check(Math.abs(o1.d - songDur) < 0.01 && o1.sr === 44100, `O1: the song becomes the loop base at the page's decode rate and keeps its length (${o1.d.toFixed(3)} s against ${songDur.toFixed(3)} s, ${o1.sr} Hz, microphone context ${o1.ac} Hz${o1.ac === o1.sr ? ', same rate: the resample path is not exercised here' : ', different rate: resample path exercised'})`)
const base = await pg.evaluate(() => window.PhosphorTest.sing.sum())
await pg.waitForFunction(() => document.getElementById('play').textContent === 'Pause', null, { timeout: 8000 }).catch(() => {})
await pg.click('#rec'); await pg.waitForTimeout(3500); await pg.click('#rec')
await pg.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && window.PhosphorTest.sing.hist() === 1 && document.getElementById('status').textContent === '', null, { timeout: 90000 })
const o2 = await pg.evaluate(() => ({ d: window.PhosphorTest.sing.dur(), s: window.PhosphorTest.sing.sum() }))
check(Math.abs(o2.s - base) > 1e-3, `O2: the voice layer changes the mix (${base.toFixed(2)} then ${o2.s.toFixed(2)})`)
check(Math.abs(o2.d - songDur) < 0.01, `O3: the length is unchanged after the layer (${o2.d.toFixed(3)} s)`)
await pg.click('#undo'); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && window.PhosphorTest.sing.hist() === 0, null, { timeout: 90000 })
check(Math.abs((await pg.evaluate(() => window.PhosphorTest.sing.sum())) - base) < 1e-6, 'O4: Undo restores the song exactly')
check(await pg.evaluate(() => document.getElementById('twinb').disabled), 'O5: Save as twin stays off for a performance (the song alone cannot stand in for it)')

// S8 leaving Sing stops the microphone
await pg.click('label[for="srcA"]'); await pg.waitForTimeout(300)
check((await T(() => window.PhosphorTest.sing.live())) === 0 && (await T(() => window.PhosphorTest.sing.state())) === 'off', 'S8: going back to Song closes the microphone')

// S5 blocked microphone
const bp = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
bp.on('pageerror', (e) => errors.push('blocked page: ' + e))
await bp.addInitScript(() => { navigator.mediaDevices.getUserMedia = () => Promise.reject(new DOMException('denied', 'NotAllowedError')) })
await bp.goto(url); await bp.waitForFunction(() => document.getElementById('status').textContent === '')
await bp.click('label[for="srcB"]'); await bp.waitForTimeout(600)
check(/blocked/i.test(await bp.evaluate(() => document.getElementById('recmsg').textContent)) && (await bp.evaluate(() => window.PhosphorTest.sing.state())) === 'off', 'S5: a blocked microphone gives a plain message and the page keeps working')
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
