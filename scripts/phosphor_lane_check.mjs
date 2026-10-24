#!/usr/bin/env node
// phosphor_lane_check.mjs: flying faders, first slice (amendment 61). One automation lane: Record, Play, Touch, Latch, Clear. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_lane_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_lane_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
const set = (id, v) => pg.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
const T = (f) => pg.evaluate(f), st = () => T(() => window.PhosphorTest.lane.st()), val = () => T(() => +document.getElementById('gamt').value)
await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300)
const kidHidden = await T(() => !document.getElementById('lanerow').getBoundingClientRect().width)
await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700)
await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true))
check(kidHidden && !!(await T(() => document.getElementById('lanerow').getBoundingClientRect().width)), 'F1: the Lane row is hidden in Kid mode and shown in Parent mode')
await T(() => window.PhosphorTest.tap.set(120, 0)); await T(() => window.PhosphorTest.lane.set('gamt', 'rec'))
await pg.click('#play'); await pg.waitForTimeout(500)
// F2 record: values set at known moments land on their true beat
const marks = []
for (const v of [20, 50, 80, 30]) { await set('gamt', v); const ev = (await T(() => window.PhosphorTest.recipe.ev())).filter((e) => e[2] === 'gamt').pop(); marks.push([v, await pg.evaluate((t) => window.PhosphorTest.tmap.beat(t), ev[1])]); await pg.waitForTimeout(700) }
const pts = (await st()).pts
const err = marks.map(([v, bt]) => { const p = pts.find((q) => Math.round(q[1]) === v); return p ? Math.abs(p[0] - bt) : 999 })
check(pts.length === 4 && Math.max(...err) < 0.3, `F2: Record keeps each move at its true beat (errors ${err.map((x) => x.toFixed(2)).join(', ')}; ${pts.length} points)`)
// F3 play: stop, restart, lane moves the slider through the points
await pg.click('#play'); await pg.waitForTimeout(300); await T(() => window.PhosphorTest.lane.set('gamt', 'play')); await set('gamt', 5)
await T(() => window.PhosphorTest.seek(0)); await pg.click('#play'); const seen = []
for (let i = 0; i < 40; i++) { await pg.waitForTimeout(100); seen.push([await T(() => window.PhosphorTest.tmap.beat(window.PhosphorTest.recipe.ev().length ? 0 : 0)), await val()]) }
const vals = seen.map((s) => s[1]), want = (await st()).pts.map((p) => Math.round(p[1]))
check(want.slice(0, 3).every((w) => vals.some((v) => Math.abs(v - w) <= 6)), `F3: Play moves the slider on its own through the recorded values (saw ${[...new Set(vals.map(Math.round))].join(',')} for lane ${want.join(',')})`)
const steps = vals.slice(1).map((v, i) => Math.abs(v - vals[i])); check(Math.max(...steps) <= 25, `F3b: no jumps while playing (largest step between 100 ms reads ${Math.max(...steps).toFixed(1)})`)
// F4 touch: a hand holds the slider away from the lane, then lets go: it glides back
await T(() => window.PhosphorTest.lane.set('gamt', 'touch'))
const hand = (type) => pg.evaluate((type) => { const e = document.getElementById('gamt'); e.dispatchEvent(new PointerEvent(type, { bubbles: true })); if (type === 'pointerup') e.dispatchEvent(new Event('change', { bubbles: true })) }, type)
await hand('pointerdown'); await set('gamt', 90); await pg.waitForTimeout(300)
const held = await st(); const heldV = await val(); await pg.waitForTimeout(600); const heldV2 = await val()
await hand('pointerup'); const after = []; for (let i = 0; i < 14; i++) { await pg.waitForTimeout(80); after.push(await val()) }
const jump = Math.max(...after.map((v, i) => Math.abs(v - (i ? after[i - 1] : heldV2)))), moved = Math.abs(after[after.length - 1] - heldV2)
check(held.held && heldV === 90 && heldV2 === 90 && !(await st()).held && moved > 10 && jump <= 30, `F4: Touch lets the hand override (held at ${heldV}, ${heldV2}) and glides back after release (moved ${moved.toFixed(0)}, largest step ${jump.toFixed(1)})`)
// F5 latch keeps writing after release
await T(() => window.PhosphorTest.lane.set('gamt', 'latch')); const n0 = (await st()).pts.length
await hand('pointerdown'); await set('gamt', 60); await hand('pointerup'); await pg.waitForTimeout(100)
const l1 = await st(); await set('gamt', 77); await pg.waitForTimeout(300); const l2 = await st()
check(l1.latched && l2.pts.some((p) => Math.round(p[1]) === 77), 'F5: Latch keeps writing after the hand lets go')
// F6 clear
await pg.click('#lnclr'); check((await st()).pts.length === 0, 'F6: Clear empties the lane')
check(errs.length === 0, 'F7: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
