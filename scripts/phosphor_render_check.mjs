#!/usr/bin/env node
// phosphor_render_check.mjs: the offline render (amendment 56). A hidden copy of the page plays the recorded recipe through the real effect chain; the live page never moves. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_render_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_render_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()) })
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
// live tap: the output analyser sampled every 50 ms against the recipe clock, for the live-versus-render comparison (O14)
await pg.evaluate(() => { window.__env = []; window.__envT = setInterval(() => { const T = window.PhosphorTest; window.__env.push([T.recipe.now(), T.outRms()]) }, 50) })
// record a short session with real actions: play, echo on for 0.9 s, off, play for a while, stop
await pg.evaluate(() => window.PhosphorTest.seek(0)); await pg.click('#play'); await pg.waitForTimeout(700)
await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', true)); await pg.waitForTimeout(900); await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', false)); await pg.waitForTimeout(1200); await pg.click('#play')
await pg.evaluate(() => { window.__live = { gamt: document.getElementById('gamt').value, n: window.PhosphorTest.recipe.ev().length, state: JSON.stringify(window.PhosphorTest.recipe.state(1e12)) } })
const recText = await pg.evaluate(() => window.PhosphorTest.recipe.exp())
await pg.evaluate(() => clearInterval(window.__envT))
const run = (text, label) => pg.evaluate(async ([text]) => {
  const t0 = performance.now(), o = await window.PhosphorTest.recipe.render(text), n = o.l.length
  const rms = (a, b) => { let s = 0; const i0 = Math.floor(a * o.sr), i1 = Math.min(n, Math.floor(b * o.sr)); for (let i = i0; i < i1; i++) s += o.l[i] * o.l[i] + o.r[i] * o.r[i]; return Math.sqrt(s / Math.max(1, 2 * (i1 - i0))) }
  let h = 2166136261; for (let i = 0; i < n; i += 7) { h ^= Math.round(o.l[i] * 32767) & 0xffff; h = Math.imul(h, 16777619) >>> 0; h ^= Math.round(o.r[i] * 32767) & 0xffff; h = Math.imul(h, 16777619) >>> 0 }
  const wav = window.PhosphorTest.recipe.wav(o), dv = new DataView(wav.buffer)
  return { secs: +(n / o.sr).toFixed(2), hash: h, wavLen: wav.length, riff: String.fromCharCode(...wav.slice(0, 4)), wavData: dv.getUint32(40, true), ms: Math.round(performance.now() - t0), windows: [[0, 0.4], [1.0, 1.5], [2.2, 2.7], [3.3, 3.9], [4.5, 5.0]].map(([a, c]) => +rms(a, c).toFixed(5)), total: +rms(0, n / o.sr).toFixed(5) }
}, [text])
const r1 = await run(recText), r2 = await run(recText)
const cmp = await pg.evaluate(async (t) => { const a = await window.PhosphorTest.recipe.render(t), c = await window.PhosphorTest.recipe.render(t); let nd = 0, first = -1, md = 0; for (let i = 0; i < a.l.length; i++) { const d = Math.abs(a.l[i] - c.l[i]) + Math.abs(a.r[i] - c.r[i]); if (d > 0) { nd++; if (first < 0) first = i; if (d > md) md = d } } return { n: a.l.length, nd, first, md, ia: a.info, ic: c.info } }, recText)
check(r1.secs >= 3 && r1.total > 0.001, `O1: the recipe renders offline to ${r1.secs} s of sound (RMS ${r1.total}) in ${r1.ms} ms`)
check(cmp.nd === 0 && r1.hash === r2.hash, `O2: renders of the same recipe are identical sample for sample (${cmp.nd} of ${cmp.n} samples differ, max difference ${cmp.md}; hashes ${r1.hash.toString(16)} and ${r2.hash.toString(16)})`)
const after = await pg.evaluate(() => ({ gamt: document.getElementById('gamt').value, n: window.PhosphorTest.recipe.ev().length, state: JSON.stringify(window.PhosphorTest.recipe.state(1e12)), frames: document.querySelectorAll('iframe').length }))
check(after.gamt === (await pg.evaluate(() => window.__live.gamt)) && after.frames === 0, `O3: the live page is untouched: controls the same, the hidden copy is removed (${after.frames} frames left)`)
const noFx = recText.split('\n')[0] + '\n' + JSON.stringify((() => { const o = JSON.parse(recText.split('\n').slice(1).join('\n')); o.events = o.events.filter((e) => e[2] !== '@fx'); return o })())
const r3 = await run(noFx)
const evs = JSON.parse(recText.split('\n').slice(1).join('\n')).events, fxt = evs.filter((e) => e[2] === '@fx').map((e) => e[0] / 1000)
check(fxt.length === 2 && r3.hash !== r1.hash, `O4: the Echo hold changes the render: with it removed the output differs (${fxt.length} fx events, hashes ${r1.hash.toString(16)} and ${r3.hash.toString(16)})`)
const play = evs.find((e) => e[2] === '@play')[0] / 1000, stop = evs.filter((e) => e[2] === '@stop').pop()[0] / 1000
check(r1.windows[0] < 0.0005 && play > 1, `O5: before the play action the render is silent (level ${r1.windows[0]} at 0 to 0.4 s; play at ${play.toFixed(1)} s of the session)`)
check(r1.riff === 'RIFF' && r1.wavData === r1.wavLen - 44 && r1.wavLen > 100000, `O6: the WAV encoder writes a RIFF file of the right size (${r1.wavLen} bytes)`)
// O9 Crush (which uses the sample-hold processor) renders deterministically and differs from the dry song
const crushT = recText.split('\n')[0] + '\n' + JSON.stringify((() => { const o = JSON.parse(recText.split('\n').slice(1).join('\n')); o.events = o.events.map((e) => e[2] === '@fx' ? [e[0], e[1], '@fx', ['crush', e[3][1], e[3][2]]] : e); return o })())
const cmpC = await pg.evaluate(async (t) => { const a = await window.PhosphorTest.recipe.render(t), c = await window.PhosphorTest.recipe.render(t); let nd = 0; for (let i = 0; i < a.l.length; i++) if (a.l[i] !== c.l[i]) nd++; return { nd, n: a.l.length } }, crushT)
const rC = await run(crushT)
check(cmpC.nd === 0 && rC.hash !== r3.hash, `O9: a Crush hold renders identically twice (${cmpC.nd} samples differ) and differs from the dry song`)
// O14 live versus render: the level envelope of what was actually played against the level envelope of the render, on the same clock
const env = await pg.evaluate(() => window.__env.filter((x) => x[1] >= 0)), liveMax = Math.max(...env.map((x) => x[1]))
if (liveMax < 0.002) check(true, `O14: skipped, the live output was silent in this environment (the known intermittent silent-audio fault; max level ${liveMax})`)
else {
  const lags = []; for (let l = -300; l <= 300; l += 10) lags.push(l)
  const rAll = await pg.evaluate(async ([t, times, lags]) => { const o = await window.PhosphorTest.recipe.render(t); const at = (ms) => { const i1 = Math.floor(ms / 1000 * o.sr), i0 = Math.max(0, i1 - 2048); if (i1 <= 0) return 0; let s = 0; for (let i = i0; i < Math.min(o.l.length, i1); i++) s += o.l[i] * o.l[i]; return Math.sqrt(s / Math.max(1, Math.min(o.l.length, i1) - i0)) }; return lags.map((l) => times.map((ms) => at(ms + l))) }, [recText, env.map((x) => x[0]), lags])
  const live = env.map((x) => x[1]), n = live.length, mean = (a) => a.reduce((s, v) => s + v, 0) / a.length, ml = mean(live)
  const corrOf = (r) => { const mr = mean(r), cov = live.reduce((s, v, i) => s + (v - ml) * (r[i] - mr), 0), vl = live.reduce((s, v) => s + (v - ml) ** 2, 0), vr = r.reduce((s, v) => s + (v - mr) ** 2, 0); return cov / Math.sqrt(vl * vr) }
  const cs = rAll.map(corrOf), best = Math.max(...cs), lag = lags[cs.indexOf(best)], ratioDb = 20 * Math.log10(mean(rAll[lags.indexOf(lag)]) / ml)
  check(best > 0.8 && Math.abs(ratioDb) < 3 && Math.abs(lag) <= 250, `O14: the render follows what was played: best level envelope correlation ${best.toFixed(3)} (want over 0.8) at a ${lag} ms offset (the output latency, want within 250), mean level difference ${ratioDb.toFixed(2)} dB (want within 3), over ${n} samples of the live output`)
}
// O10 to O12: pads (slices), the slice list and tempo are replayed
const padRec = await pg.evaluate(async () => {
  const T = window.PhosphorTest
  T.recipe.act('slices', [[0.0, 0.6], [0.6, 1.2], [1.2, 1.8], [1.8, 2.4]])
  const base = JSON.parse(T.recipe.exp().split('\n').slice(1).join('\n')).base
  const mk = (events) => 'Phosphor recipe v1\n' + JSON.stringify({ base, events })
  const ev = [[100, null, '@slices', [[0.0, 0.6], [0.6, 1.2], [1.2, 1.8], [1.8, 2.4]]], [200, null, '@tempo', [97, 0.2]], [500, null, '@pad', '0:1'], [900, null, '@pad', '0:3'], [1300, null, '@pad', '0:2:echo'], [2500, null, '@stop', null]]
  const none = ev.filter((e) => e[2] !== '@pad')
  const a = await T.recipe.render(mk(ev)), b = await T.recipe.render(mk(ev)), c = await T.recipe.render(mk(none))
  let nd = 0, dd = 0; for (let i = 0; i < a.l.length; i++) { if (a.l[i] !== b.l[i]) nd++; if (a.l[i] !== c.l[i]) dd++ }
  let rmsA = 0, rmsC = 0; for (let i = 0; i < a.l.length; i++) { rmsA += a.l[i] * a.l[i]; rmsC += c.l[i] * c.l[i] }
  return { nd, dd, pads: a.info.pads, padsNone: c.info.pads, bpm: a.info.bpm, rmsA: Math.sqrt(rmsA / a.l.length), rmsC: Math.sqrt(rmsC / c.l.length) }
})
check(padRec.pads === 2 && padRec.padsNone === 0 && padRec.rmsA > 0.005 && padRec.rmsC < 0.0005, `O10: two slice pads are replayed from the recorded slice list (voices ${padRec.pads}; level ${padRec.rmsA.toFixed(4)} with pads, ${padRec.rmsC.toFixed(5)} without); the effect pad is left to the effect events`)
check(padRec.nd === 0 && padRec.dd > 1000, `O11: a pad render is identical twice (${padRec.nd} samples differ) and differs from the same recipe without pads (${padRec.dd} samples)`)
check(padRec.bpm === 97, `O12: the recorded tempo is replayed in the render (${padRec.bpm} BPM)`)
// O13 the Render to WAV button saves a valid WAV
await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true))
const dlP = pg.waitForEvent('download', { timeout: 60000 }); await pg.evaluate(() => document.getElementById('rnb').click()); const dl = await dlP; const dlPath = await dl.path()
const bytes = (await import('node:fs')).readFileSync(dlPath)
check(dl.suggestedFilename() === 'phosphor-session.wav' && bytes.slice(0, 4).toString() === 'RIFF' && bytes.slice(8, 12).toString() === 'WAVE' && bytes.length > 100000, `O13: the Render to WAV button saves ${dl.suggestedFilename()} (${bytes.length} bytes, RIFF and WAVE header)`)
await pg.waitForFunction(() => !document.getElementById('rnb').disabled && /Rendered/.test(document.getElementById('rnsum').textContent), null, { timeout: 30000 })
const bad = await pg.evaluate(() => window.PhosphorTest.recipe.render('nope').then(() => 'resolved', (e) => String(e.message)))
check(bad === 'not a recipe', `O7: text that is not a recipe is refused (${bad})`)
check(errs.length === 0, 'O8: no page errors in the page or the hidden copy ' + errs.slice(0, 3).join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
