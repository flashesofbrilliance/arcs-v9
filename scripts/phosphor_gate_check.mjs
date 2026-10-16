#!/usr/bin/env node
// phosphor_gate_check.mjs: W1 to W12 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 26 and its addenda, the rhythm gate).
// Needs a synthetic break with kicks on steps 1 and 9 (PHOSPHOR_FILES=/path/break.wav). Usage: PHOSPHOR_FILES=break.wav node scripts/phosphor_gate_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break.wav node scripts/phosphor_gate_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), pg = await (await b.newContext({ viewport: { width: 1270, height: 990 } })).newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(page).href + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200)
await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 })
const F = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.fx[fn](...a), [fn, a])
check((await pg.evaluate(() => document.querySelector('input[name=fxg]:checked').value)) === 'off', 'W12: the gate is Off at defaults')
await pg.click('#play'); await pg.waitForTimeout(500)
const bpm = await pg.evaluate(() => window.PhosphorTest.bpm()), step = (60 / bpm) / 4
await F('on', 'crush', true); await pg.waitForTimeout(300)
// sample the wet level for a while
const sample = async (ms, dt = 8) => { return pg.evaluate(async ([ms, dt]) => { const o = [], t0 = performance.now(); while (performance.now() - t0 < ms) { const w = window.PhosphorTest.fx.wet('crush'), c = window.PhosphorTest.fx.clock(); o.push([performance.now() - t0, w.wet, w.dry, c.now, c.ref, c.P]); await new Promise((r) => setTimeout(r, dt)) } return o }, [ms, dt]) }
const sel = async (mode, div, dep) => { await pg.evaluate(([mode, div, dep]) => { const r = document.querySelector(`input[name=fxg][value=${mode}]`); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); const d = document.querySelector(`input[name=fxd][value="${div}"]`); d.checked = true; d.dispatchEvent(new Event('change', { bubbles: true })); const s = document.getElementById('fxdep'); s.value = dep; s.dispatchEvent(new Event('input', { bubbles: true })) }, [mode, div, dep]); await pg.waitForTimeout(200) }
// W1 square, full depth, 1/4 rate (div 1): ends dominate
await sel('beat', 1, 100); let s = await sample(2400); const hi = s.filter((x) => x[1] > 0.9).length, lo = s.filter((x) => x[1] < 0.1).length, mid = s.length - hi - lo
check(hi > 0.3 * s.length && lo > 0.3 * s.length && mid < 0.2 * s.length, `W1: Square at 1/4 sits near 1 (${hi}) and near 0 (${lo}) and rarely between (${mid}) of ${s.length} samples`)
check(s.every((x) => Math.abs(x[1] + x[2] - 1) < 0.02 && x[1] <= 1.0001 && x[2] <= 1.0001), 'W5: wet plus dry stays 1 and neither goes above 1 (the dry track keeps playing in parallel)')
// W2 triangle: intermediate values, rising and falling; period two steps at 1/16
await sel('tri', 4, 100); s = await sample(2400, 6); const mids = s.filter((x) => x[1] > 0.2 && x[1] < 0.8).length
let up = 0, down = 0; for (let i = 1; i < s.length; i++) { const d = s[i][1] - s[i - 1][1]; if (d > 0.01) up++; if (d < -0.01) down++ }
const peaks = []; for (let i = 1; i < s.length - 1; i++) if (s[i][1] > 0.9 && s[i][1] >= s[i - 1][1] && s[i][1] > s[i + 1][1]) peaks.push(s[i][0]); const gaps = peaks.slice(1).map((x, i) => x - peaks[i]).filter((g) => g > 30); const med = gaps.sort((a, z) => a - z)[gaps.length >> 1] || 0
check(mids > 0.3 * s.length && up > 5 && down > 5, `W2: Triangle passes through the in-between values (${mids} of ${s.length}) and both rises (${up}) and falls (${down})`)
check(med > 0 && Math.abs(med - 2 * step * 1000) < 0.15 * 2 * step * 1000, `W2: the Triangle period is ${med.toFixed(0)} ms against two steps ${(2 * step * 1000).toFixed(0)} ms at 1/16 (${bpm} BPM)`)
// W3 depth 0.5
await sel('beat', 2, 50); s = await sample(1600); check(Math.min(...s.map((x) => x[1])) >= 0.47, `W3: Depth 50 never takes the wet level below 0.5 (min ${Math.min(...s.map((x) => x[1])).toFixed(2)})`)
// W8 downbeat chop
await sel('bar', 4, 100); s = await sample(4 * (60 / bpm) * 1000 * 2, 8); const open = s.filter((x) => x[1] > 0.5).length / s.length
check(open > 0.02 && open < 0.2, `W8: the Downbeat chop is open for ${(open * 100).toFixed(0)} percent of two bars (one step in sixteen is 6 percent)`)
// W9 swing and W10 lay back, measured as where the rising edge falls inside a step on the audio clock
const phases = (arr, fall) => { const o = []; for (let i = 1; i < arr.length; i++) if (fall ? (arr[i - 1][1] >= 0.5 && arr[i][1] < 0.5) : (arr[i - 1][1] < 0.5 && arr[i][1] >= 0.5)) { const c = arr[i], k = Math.round((c[3] - c[4]) / c[5]); o.push({ k, frac: ((c[3] - c[4]) / c[5]) - k }) } return o }
await sel('beat', 4, 100); await pg.evaluate(() => window.PhosphorTest.groove.swing(50)); let sq0 = await sample(3200, 4); const p0 = phases(sq0)
const medv = (a) => a.slice().sort((x, y) => x - y)[a.length >> 1]
check(p0.length > 6 && Math.abs(medv(p0.map((x) => x.frac))) < 0.1, `W9: at Feel 50 the Square's rises land on the step (median offset ${(medv(p0.map((x) => x.frac))).toFixed(3)} of a step)`)
await pg.evaluate(() => window.PhosphorTest.groove.swing(67)); await pg.waitForTimeout(150); const sq1 = await sample(3200, 4); const p1 = phases(sq1)
const evenOff = medv(p1.map((x) => x.frac)), f1 = phases(sq1, true), oddOff = medv(f1.map((x) => x.frac))
check(p1.length > 6 && f1.length > 6 && Math.abs(evenOff) < 0.07 && Math.abs(oddOff - 0.34) < 0.08, `W9: with Feel 67 the rises (even steps) stay on the step (${evenOff.toFixed(3)}) and the falls (odd steps) are a third of a step late (${oddOff.toFixed(3)}; want 0.34)`)
await pg.evaluate(() => window.PhosphorTest.groove.swing(50))
await sel('beat', 4, 100); await pg.evaluate(() => { const r = document.getElementById('fxlag'); r.value = 30; r.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.waitForTimeout(150)
const p2 = phases(await sample(3200, 4)); const lagOff = medv(p2.map((x) => x.frac))
check(p2.length > 6 && Math.abs(lagOff - 0.30) < 0.07 && /behind/.test(await pg.evaluate(() => document.getElementById('fxlago').textContent)), `W10: Lay back 30 percent moves the rises ${lagOff.toFixed(3)} of a step behind (want 0.30)`)
await pg.evaluate(() => { const r = document.getElementById('fxlag'); r.value = 0; r.dispatchEvent(new Event('input', { bubbles: true })) })
// W11 seed: kicks on steps 1 and 9 (indexes 0 and 8) with weaker hats on every step, bar after bar at 120 BPM
const seedOut = await pg.evaluate(() => { const M = [], P = 0.5, strong = [0, 8], bars = 12, i = 0; for (let b = 0; b < bars; b++) for (let st = 0; st < 16; st++) { const t = (b * 16 + st) * (P / 4) + 1.0; M.push({ k: 'onset', t, s: strong.includes(st) ? 3 : 0.4 }) } return window.PhosphorTest.fx.seed(M, 120, 1.0) })
const openIdx = seedOut.map((v, i) => v ? i : -1).filter((i) => i >= 0)
check(JSON.stringify(openIdx) === '[0,8]', `W11: the Song rhythm seed of a kick on steps 1 and 9 with weak hats on all steps opens exactly steps ${JSON.stringify(openIdx)} (want [0,8])`)
const real = await F('seed'); check(real.length === 16 && real.filter(Boolean).length >= 1 && real[0], `W11: on the loaded song the seed is a sixteen-step bar with the downbeat open (${real.map((v) => v ? 1 : 0).join('')})`)
// W4 pad holds the wave only while held
await pg.evaluate(() => { document.querySelector('input[name=fxg][value=off]').checked = true; document.querySelector('input[name=fxg][value=off]').dispatchEvent(new Event('change', { bubbles: true })) }); await pg.waitForTimeout(250)
const idle = await sample(500); check(idle.every((x) => x[1] > 0.98), 'W4: with the gate Off the effect stays fully wet')
await pg.evaluate(() => window.PhosphorTest.hold.on('gate', 'ptr:gate', true)); await pg.waitForTimeout(150); const held = await sample(1500); const dip = held.filter((x) => x[1] < 0.1).length
await pg.evaluate(() => window.PhosphorTest.hold.on('gate', 'ptr:gate', false)); await pg.waitForTimeout(250); const after = await sample(500)
check(dip > 0.2 * held.length && after.every((x) => x[1] > 0.98), `W4: the Gate pad runs the wave while held (${dip} chops in ${held.length} samples) and the effect returns to fully wet on release`)
// W5: gate does nothing to an effect that is off
await F('on', 'crush', false); await pg.waitForTimeout(300); await pg.evaluate(() => window.PhosphorTest.hold.on('gate', 'ptr:gate', true)); await pg.waitForTimeout(200); const off = await sample(500); await pg.evaluate(() => window.PhosphorTest.hold.on('gate', 'ptr:gate', false))
check(off.every((x) => x[1] < 0.05), 'W5: the gate does nothing to an effect that is off (wet stays 0)')
// W6 ceiling
await F('on', 'crush', true); await pg.evaluate(() => { const r = document.querySelector('input[name=fxg][value=beat]'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) }); let pk = 0; for (let i = 0; i < 20; i++) { pk = Math.max(pk, await pg.evaluate(() => window.PhosphorTest.outPeak())); await pg.waitForTimeout(60) }
check(pk <= 0.51, `W6: output peak with Crush and the gate running is ${pk.toFixed(3)} (ceiling 0.5)`)
check(errs.length === 0, `W7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
