#!/usr/bin/env node
// phosphor_bars_check.mjs: B1 to B7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 29, the next eight bars).
// Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_bars_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_bars_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href, errs = []
const mk = async (extra = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 }, ...extra }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200); await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 }); await pg.evaluate(() => document.getElementById('bars').scrollIntoView({ block: 'center' })); await pg.waitForTimeout(300); return pg }
let pg = await mk(); const T = (fn) => pg.evaluate(fn)
await pg.evaluate(() => window.PhosphorTest.seek(3.3)); await pg.waitForTimeout(300); await T(() => window.PhosphorTest.bars.render())
const bpm = await T(() => window.PhosphorTest.bpm()), tm = await T(() => window.PhosphorTest.bars.times()), bl = 4 * 60 / bpm, now = 3.3
check(tm.length === 8 && tm.every((x, i) => i === 0 || Math.abs(x - tm[i - 1] - bl) < 0.001) && tm[0] > now && tm[0] <= now + bl + 0.001, `B1: eight tiles one bar apart (${(bl).toFixed(3)} s at ${bpm} BPM), the first at ${tm[0].toFixed(2)} s after the playhead ${now}`)
// B2 distinct images
const hashes = await T(() => [...document.querySelectorAll('#bars canvas')].map((c) => { const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i += 37) { h ^= d[i]; h = Math.imul(h, 16777619) >>> 0 } return h }))
check(new Set(hashes).size >= 3, `B2: ${new Set(hashes).size} different pictures among the eight tiles`)
// B3 click seeks
await pg.evaluate(() => document.querySelector('#bars [data-b="3"]').click()); await pg.waitForTimeout(250); const at = await T(() => window.PhosphorTest.tnow()); check(Math.abs(at - tm[3]) < 0.05, `B3: clicking the fourth tile jumps to ${at.toFixed(2)} s (bar at ${tm[3].toFixed(2)} s)`)
// B4 pin mark
await pg.evaluate((t) => window.PhosphorTest.seek(t), tm[2] + 0.2); await pg.waitForTimeout(200); await pg.evaluate(() => window.PhosphorTest.pins.add('mark me', 'note', false)); await pg.evaluate(() => window.PhosphorTest.seek(3.3)); await pg.waitForTimeout(300); await T(() => window.PhosphorTest.bars.render())
const caps = await T(() => [...document.querySelectorAll('#bars figcaption')].map((c) => c.textContent)); check(caps.filter((c) => /pin/.test(c)).length === 1, `B4: exactly one tile shows the pin mark (${caps.map((c) => (/pin/.test(c) ? 'pin' : '-')).join(' ')})`)
// B6 main picture unchanged by the preview
const mainHash = () => T(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i += 53) { h ^= d[i]; h = Math.imul(h, 16777619) >>> 0 } return h })
await pg.evaluate(() => window.PhosphorTest.seek(5)); await pg.waitForTimeout(250); const h0 = await mainHash(); await T(() => window.PhosphorTest.bars.render()); await T(() => window.PhosphorTest.bars.play(true)); await pg.waitForTimeout(700); await T(() => window.PhosphorTest.bars.play(false)); await pg.evaluate(() => window.PhosphorTest.seek(5)); await pg.waitForTimeout(250); const h1 = await mainHash()
check(h0 === h1, 'B6: the main picture at 5 s is identical before and after the preview ran')
// B5 stop motion
await T(() => window.PhosphorTest.bars.show(0)); await T(() => window.PhosphorTest.bars.play(true)); const seq = []; const t0 = Date.now(); while (Date.now() - t0 < 2300) { seq.push(await T(() => window.PhosphorTest.bars.index())); await pg.waitForTimeout(40) } await T(() => window.PhosphorTest.bars.play(false))
const steps = []; seq.forEach((v, i) => { if (i === 0 || v !== seq[i - 1]) steps.push(v) }); const inOrder = steps.every((v, i) => i === 0 || v === (steps[i - 1] + 1) % 8), pose = await T(() => window.PhosphorTest.mo.pose)
check(steps.length >= 4 && inOrder && steps.length - 1 <= 2.3 * (pose / 2) + 1, `B5: Play preview stepped ${steps.length - 1} times in 2.3 s in order (${steps.join(',')}); never faster than ${pose / 2} frames a second`)
const stopped = await T(() => window.PhosphorTest.bars.playing()); check(stopped === false, 'B5: Stop preview stops it')
// reduced motion
await pg.context().close(); pg = await mk({ reducedMotion: 'reduce' }); check(await T(() => document.getElementById('barplay').hidden), 'B5: with reduced motion the Play preview button is hidden and nothing advances by itself')
// B7 cost: a full refresh (look change) and the one-tile update when the playhead crosses a bar
await pg.evaluate(() => window.PhosphorTest.seek(3)); await pg.waitForTimeout(250)
const cost = await T(() => { const full = [], inc = []; for (let i = 0; i < 9; i++) { let t = performance.now(); window.PhosphorTest.bars.render(true); full.push(performance.now() - t) } const bl = 4 * 60 / window.PhosphorTest.bpm(); for (let i = 0; i < 9; i++) { window.PhosphorTest.seek(window.PhosphorTest.tnow() + bl); let t = performance.now(); window.PhosphorTest.bars.render(); inc.push(performance.now() - t) } const m = (a) => a.sort((x, y) => x - y)[a.length >> 1]; return [m(full), m(inc)] })
check(cost[0] < 30 && cost[1] < 5, `B7: a full refresh takes ${cost[0].toFixed(1)} ms (on a look change, limit 30) and the update at a bar line takes ${cost[1].toFixed(1)} ms (limit 5)`)
check(errs.length === 0, `B7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(failed() ? 1 : 0)
