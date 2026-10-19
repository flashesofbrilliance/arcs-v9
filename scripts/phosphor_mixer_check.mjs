#!/usr/bin/env node
// phosphor_mixer_check.mjs: X1 to X10 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 24, two-deck mixer).
// Needs two local audio files: PHOSPHOR_FILES=/path/a.wav,/path/b.wav (A is loaded as the song, B into Deck B).
// Usage: PHOSPHOR_FILES=a.wav,b.wav node scripts/phosphor_mixer_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], files = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)
if (!page || files.length < 2) { console.log('usage: PHOSPHOR_FILES=a.wav,b.wav node scripts/phosphor_mixer_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(page).href, errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
const M = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.mix[fn](...a), [fn, a])
// X1 defaults and level gating
const p1 = await b.newContext({ viewport: { width: 1270, height: 990 } }).then((c) => c.newPage()); await p1.goto(base + '?shutter=off&level=1'); await p1.waitForTimeout(800)
check(await p1.evaluate(() => getComputedStyle(document.getElementById('mixer')).display === 'none'), 'X1: the mixer is hidden in Kid mode'); await p1.context().close()
await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200)
await pg.setInputFiles('#file', files[0]); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 })
const g0 = await M('gains'); check(g0.a === 1 && g0.b === 0, 'X1: the defaults are crossfader on A, A gain 1, B gain 0')
check(await pg.evaluate(() => getComputedStyle(document.getElementById('mixer')).display !== 'none'), 'X1: the mixer is shown at level 4')
// X2 gain math
let ok = true, worst = 0; for (let i = 0; i <= 20; i++) { const xf = -1 + i / 10, g = await M('math', xf, 'smooth'); worst = Math.max(worst, Math.abs(g.a * g.a + g.b * g.b - 1)) } 
const e1 = await M('math', -1, 'smooth'), e2 = await M('math', 1, 'smooth'), s0 = await M('math', 0, 'sharp'), s1 = await M('math', -1, 'sharp'), s2 = await M('math', 1, 'sharp')
check(worst < 0.01 && e1.a === 1 && Math.abs(e1.b) < 1e-9 && Math.abs(e2.a) < 1e-9 && e2.b === 1, `X2: Smooth keeps A squared plus B squared at 1 (worst ${worst.toExponential(1)}) with exact end points`)
check(s0.a === 1 && s0.b === 1 && s1.a === 1 && s1.b === 0 && s2.a === 0 && s2.b === 1, 'X2: Sharp has both at 1 in the middle and one at 0 at each end')
// X4 load B
await pg.setInputFiles('#dbfile', files[1]); await pg.waitForFunction(() => window.PhosphorTest.mix.b().nf > 0, null, { timeout: 60000 }); await pg.waitForTimeout(500)
const B = await M('b'), bpmA = await pg.evaluate(() => window.PhosphorTest.bpm())
const ratio = B.bpm / (+process.env.B_TRUE || B.bpm)
check(B.nf > 100 && B.dna > 5 && B.dna === Math.max(1, Math.ceil((B.dur - (B.grid0 % (60 / B.bpm))) / (60 / B.bpm))), `X4: Deck B ${B.name} read: ${B.bpm} BPM, ${B.dna} codons for ${B.dur.toFixed(1)} s`)
if (process.env.B_TRUE) check([1, 2, 0.5].some((m) => Math.abs(ratio * m - 1) < 0.03), `X4: B's tempo ${B.bpm} is within 3 percent of ${process.env.B_TRUE} (or a half or double)`)
check((await pg.evaluate(() => window.PhosphorTest.bpm())) === bpmA, 'X4: loading B did not change Deck A\'s tempo')
// X5 sync
const sy = await pg.evaluate(() => { const r = window.PhosphorTest.mix.sync(); const A = window.PhosphorTest.bpm(), Bb = window.PhosphorTest.mix.b(); return { A, eff: Bb.bpm * Bb.rate * Bb.mult, rate: Bb.rate, m: Bb.mult } })
check(Math.abs(sy.eff / sy.A - 1) < 0.001, `X5: after Sync B's effective tempo ${sy.eff.toFixed(2)} equals A's ${sy.A.toFixed(2)} (rate ${(sy.rate * 100).toFixed(1)} percent, x${sy.m})`)
check(/pitch/.test(await pg.evaluate(() => document.getElementById('mxmsg').textContent)) || Math.abs(sy.rate - 1) > 0.2, 'X5: the message says what Sync does to pitch, or flags a ratio beyond 20 percent')
// X3 audibility and X6 align: play both
await pg.evaluate(() => { document.getElementById('play').click() }); await pg.waitForTimeout(500)
await M('play', 0); await pg.waitForTimeout(600)
const rms = () => pg.evaluate(() => { const d = window.PhosphorTest.fx.bufs(); let s = 0; for (const v of d) s += v * v; return Math.sqrt(s / d.length) })
const avg = async (n = 6) => { let s = 0; for (let i = 0; i < n; i++) { s += await rms(); await pg.waitForTimeout(60) } return s / n }
await M('set', -1, 1, 1); await pg.waitForTimeout(250); const rA = await avg(); await M('set', 1, 1, 1); await pg.waitForTimeout(250); const rB = await avg(); await M('set', 0, 0, 0); await pg.waitForTimeout(300); const r0 = await avg()
check(rA > 0.01 && rB > 0.01 && r0 < 0.002, `X3: output is audible from A alone (${rA.toFixed(3)}), B alone (${rB.toFixed(3)}), and silent with both levels at 0 (${r0.toFixed(4)})`)
await M('set', 0, 1, 1); await pg.evaluate(() => window.PhosphorTest.mix.align()); await pg.waitForTimeout(500)
const ph = []; for (let i = 0; i < 3; i++) { ph.push(await M('phase')); await pg.waitForTimeout(700) }
check(ph.every((x) => x !== null && x < 15), `X6: after Align the beats are within 15 ms at three moments (${ph.map((x) => x.toFixed(1)).join(', ')} ms)`)
// X10 ceiling with both full
await M('set', 0, 1, 1); let pk = 0; for (let i = 0; i < 12; i++) { pk = Math.max(pk, await M('ceiling')); await pg.waitForTimeout(80) }
check(pk <= 0.51, `X10: two decks at full level stay under the output ceiling (peak ${pk.toFixed(3)})`)
// X7 transport
await M('stop'); const h1 = (await M('b')).pos; await pg.waitForTimeout(400); const h2 = (await M('b')).pos; check(Math.abs(h1 - h2) < 0.001 && !(await M('b')).playing, 'X7: Pause holds the position')
await M('play', 3); await pg.waitForTimeout(1000); const q1 = await M('b'); await pg.waitForTimeout(1000); const q2 = await M('b'); const adv = (q2.pos - q1.pos) / 1.0
check(Math.abs(adv - q2.rate) < 0.08 * q2.rate, `X7: Play advances B at its rate (${adv.toFixed(3)} s per second, rate ${q2.rate.toFixed(3)})`)
await M('stop'); const n0 = (await M('b')).pos; await M('nudge', 10); const n1 = (await M('b')).pos; check(Math.abs(n1 - n0 - 0.01) < 0.002, `X7: Nudge moves B by 10 ms (${((n1 - n0) * 1000).toFixed(1)} ms)`)
await pg.click('#dbcue'); const cu = await M('b'); check(!cu.playing && cu.pos >= 0 && cu.pos < 60 / cu.bpm, 'X7: Cue returns B to its first beat and holds')
// X8 picture follow
await pg.evaluate(() => { window.PhosphorTest.mix.stop(); document.getElementById('play').textContent === 'Pause' && document.getElementById('play').click() }); await pg.waitForTimeout(300)
await pg.evaluate(() => window.PhosphorTest.seek(5)); const hash = () => pg.evaluate(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i += 53) { h ^= d[i]; h = Math.imul(h, 16777619) >>> 0 } return h })
await M('follow', 'A'); const hA = await hash(); await pg.evaluate(() => { window.PhosphorTest.mix.stop(); }); await M('play', 4); await pg.waitForTimeout(300); await M('stop'); await M('follow', 'B'); await pg.waitForTimeout(200); const hB = await hash(); await M('follow', 'A'); await pg.waitForTimeout(200); const hA2 = await hash()
check(hA !== hB && hA === hA2, 'X8: following B changes the picture and following A again restores the exact original')
check(errs.length === 0, `X9: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(failed() ? 1 : 0)
