#!/usr/bin/env node
// phosphor_quick_check.mjs: T1 to T3, D1, D2, R1, P1 to P3, A1 to A4 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 9).
// Usage: node scripts/phosphor_quick_check.mjs <page.html>   (run phosphor_stage_check.mjs once first so the click track exists)
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_quick_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav')
if (!fs.existsSync(wav)) { console.error('run phosphor_stage_check.mjs once first to make the click track'); process.exit(2) }

const b = await pw.chromium.launch({ args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', `--use-file-for-fake-audio-capture=${wav}`, '--autoplay-policy=no-user-gesture-required'] })
const url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, permissions: ['microphone'] })
async function open(load = true) {
  const pg = await ctx.newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
  await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
  if (load) { await pg.setInputFiles('#file', wav); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 60000 }) }
  return pg
}
const pg = await open()
const E = (f, ...a) => pg.evaluate(f, ...a)
await pg.evaluate(() => localStorage.clear())

// T tap tempo
const t1 = await E(() => { const T = window.PhosphorTest, r = T.tap.at(0, 0); T.tap.at(500, 0.5); T.tap.at(1000, 1); const bpm = T.tap.at(1500, 1.5), g = T.magnets().filter((m) => m.k === 'grid').slice(0, 6).map((m) => m.t); return { bpm, g } })
check(t1.bpm === 120 && t1.g.slice(1).every((v, i) => Math.abs(v - t1.g[i] - 0.5) < 1e-6), `T1: four taps 500 ms apart read ${t1.bpm} BPM and the grid lines are 0.5 s apart`)
const t2 = await E(() => { const T = window.PhosphorTest; T.tap.at(5000, 2); return T.tap.taps() })
check(t2 === 1, `T2: a gap of more than 2 s starts over (${t2} tap held)`)
const t3 = await E(() => { const T = window.PhosphorTest; T.tap.at(10000, 3); const hi = T.tap.at(10100, 3.1); T.tap.at(20000, 4); const lo = T.tap.at(21900, 5.9); return { hi, lo } })
check(t3.hi === 240 && t3.lo === 40, `T3: tempo is held between 40 and 240 BPM (${t3.lo}, ${t3.hi})`)
const t4 = await E(() => { const T = window.PhosphorTest; T.tap.at(40000, 1); T.tap.at(40500, 1.5); T.tap.at(41000, 2); return T.tap.at(41500, 2.5) })
check(t4 === 120 && (await E(() => document.querySelector('.tapb').textContent)) === 'Tap tempo 120', 'T1: the button shows the tempo it found')

// D1 downbeat here
const d1 = await E(() => { const T = window.PhosphorTest, on = T.magnets().filter((m) => m.k === 'onset').map((m) => m.t), o = on[10], sc = document.getElementById('scrub'); sc.value = Math.round((o + 0.1) / T.dur() * 1000); sc.dispatchEvent(new Event('input')); return { o } })
await pg.waitForTimeout(150)
await pg.evaluate(() => { document.getElementById('slices').open = true; window.PhosphorTest.tap.set(120, 0) }); await pg.click('#tmrow .dbb')
const d1r = await E(() => { const T = window.PhosphorTest; return { base: T.seq.base(), P: 0.5 } })
const want = ((d1.o % d1r.P) + d1r.P) % d1r.P
check(Math.abs(d1r.base - want) < 0.001 || Math.abs(Math.abs(d1r.base - want) - 0.5) < 0.001, `D1: Downbeat here puts the grid on the nearest hit (grid origin ${d1r.base.toFixed(3)} against hit ${want.toFixed(3)})`)

// R1 detail lane
const r1 = await E(() => {
  const T = window.PhosphorTest, S = T.seq; S.clear(); S.set('detail', 0, 3); S.set('detail', 8, 9)
  const st = S.step(), b0 = S.base(); S.on(false); T.loop(true, 1, 'up'); const off = T.rungAt(b0 + 0.01)
  S.on(true); const on0 = T.rungAt(b0 + 2 * st + 0.001), on9 = T.rungAt(b0 + 9 * st + 0.001), before = T.rungAt(b0 + 0.001)
  S.on(false); T.loop(false, 1, 'up'); S.clear(); return { off, on0, on9, before }
})
check(r1.on0 === 2 && r1.on9 === 8, `R1: a Detail cell holds its rung until the next set step (value 3 gives rung ${r1.on0}, value 9 gives rung ${r1.on9})`)
check(r1.off === 0 && r1.before === 2, `R1: with steps off the loop decides (rung ${r1.off}); with steps on the Detail value outranks it (rung ${r1.before} at the first step)`)

// P presets
const def = await E(() => window.PhosphorTest.sig())
const sigs = {}
for (const n of ['rain', 'robot', 'party', 'sleepy', 'dino']) { await E((n) => window.PhosphorTest.preset(n), n); sigs[n] = await E(() => window.PhosphorTest.sig()) }
check(new Set(Object.values(sigs).map((s) => JSON.stringify(s))).size === 5, `P1: the five presets leave five different states (${Object.entries(sigs).map(([k, s]) => k + ' ' + s.pal + '/' + s.cells).join(', ')})`)
check(Object.values(sigs).every((s) => s.playing === false && s.src === def.src), 'P3: no preset starts playback or changes the source')
await E(() => window.PhosphorTest.preset('plain')); const plain = await E(() => window.PhosphorTest.sig())
check(JSON.stringify({ ...plain, seqOn: 0, playing: 0 }) === JSON.stringify({ ...def, seqOn: 0, playing: 0 }), `P2: Plain restores the defaults (${plain.pal}, ${plain.bits} bit, ${plain.cells} steps)`)

// A autosave
await E(() => window.PhosphorTest.preset('dino')); await E(() => { const c = document.getElementById('inv'); c.checked = true; c.dispatchEvent(new Event('change', { bubbles: true })) }); await pg.waitForTimeout(700)
const saved = await E(() => window.PhosphorTest.saved())
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const back = await E(() => window.PhosphorTest.sig()), inv = await E(() => document.getElementById('inv').checked)
check(back.pal === 'mono' && back.bits === 3 && back.mode === 3 && back.rl === '4down' && back.q === 'valley' && back.gate === 1 && back.cells === 8, `A1: settings and the step pattern survive a reload (${back.pal}, ${back.bits} bit, ${back.rl}, ${back.q}, ${back.cells} steps)`)
check(inv === false && back.seqOn === false && back.playing === false, 'A2: invert, the Run switch and playback are never restored')
const keys = await E(() => Object.keys(localStorage))
check(saved && saved.length < 3000 && !/pcm|audio|blob|data:/i.test(saved) && keys.every((k) => /^phosphor\./.test(k)), `A3: only small settings are stored, no audio (${saved ? saved.length : 0} characters, keys ${keys.join(', ')})`)
await pg.evaluate(() => { document.querySelector('details.grp:has(#forget) > summary').click() }); await pg.click('#forget')
check((await E(() => window.PhosphorTest.saved())) === null, 'A4: Forget everything saved here removes it')
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const clean = await E(() => window.PhosphorTest.sig()); check(clean.pal === 'amber' && clean.mode === 2 && clean.cells === 0, 'A4: after Forget the page opens on its defaults (the Ring in amber)')

// D2 Sing downbeat trim
const sp = await open(false)
await sp.click('label[for="srcB"]'); await sp.waitForFunction(() => window.PhosphorTest.sing.state() === 'armed', null, { timeout: 15000 })
await sp.click('#rec'); await sp.waitForTimeout(3400); await sp.click('#rec')
await sp.waitForFunction(() => window.PhosphorTest.sing.state() === 'loop' && document.getElementById('status').textContent === '' && document.getElementById('src').textContent === 'My loop', null, { timeout: 30000 })
const g0 = await sp.evaluate(() => window.PhosphorTest.seq.base()), dur0 = await sp.evaluate(() => window.PhosphorTest.sing.dur())
await sp.click('#dbtrim'); await sp.waitForFunction(() => document.getElementById('status').textContent === '' && window.PhosphorTest.sing.hist() === 1, null, { timeout: 30000 })
const dur1 = await sp.evaluate(() => window.PhosphorTest.sing.dur())
check(g0 > 0.03 ? Math.abs((dur0 - dur1) - g0) < 0.02 : Math.abs(dur0 - dur1) < 0.02, `D2: Start on the downbeat trims the loop by the grid origin (${dur0.toFixed(3)} then ${dur1.toFixed(3)} s, origin ${g0.toFixed(3)} s)`)
await sp.click('#clk'); await sp.click('#dbtrim'); await sp.waitForTimeout(300)
check(/click/i.test(await sp.evaluate(() => document.getElementById('recmsg').textContent)), 'D2: with the click on it explains instead of trimming')
check(reqs.length === 0, `no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
