#!/usr/bin/env node
// phosphor_waypoint_check.mjs: S1 to S7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 23, waypoints and storage fallback).
// Usage: node scripts/phosphor_waypoint_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_waypoint_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(page).href, errs = []
const BLOCK = () => { const bad = () => { throw new DOMException('blocked', 'SecurityError') }; Object.defineProperty(window, 'localStorage', { get: bad }) }
const open = async (q, blocked) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); if (blocked) await pg.addInitScript(BLOCK); await pg.goto(base + q); await pg.waitForTimeout(1500); return pg }
const snap = (pg) => pg.evaluate(() => { const T = window.PhosphorTest; return { lvl: T.molt.level(), mode: T.zoom().mode, pal: document.getElementById('palsel').value, swing: document.getElementById('swo').textContent, t: +T.tnow().toFixed(1), cells: T.sig().cells, res: +document.getElementById('res').value } })
// S1
let pg = await open('?test=1&shutter=off&level=4'); check(await pg.evaluate(() => document.getElementById('svchip').hidden), 'S1: with storage working the "Not saved here" chip is hidden'); await pg.context().close()
pg = await open('?test=1&shutter=off&level=4', true)
check(!(await pg.evaluate(() => document.getElementById('svchip').hidden)) && !(await pg.evaluate(() => window.PhosphorTest.wp.store())), 'S1: with storage throwing the chip is shown')
await pg.click('#play'); await pg.waitForTimeout(500); check(await pg.evaluate(() => window.PhosphorTest.tnow() > 0.2), 'S1: the page still plays with storage blocked')
await pg.click('#svchip'); check(!(await pg.evaluate(() => document.getElementById('wp').hidden)), 'S1: the chip opens the waypoint panel')
// S2 round trip on a fresh blocked page
await pg.evaluate(() => { const T = window.PhosphorTest; T.groove.swing(58); T.seek(7.3); T.seq.set('tear', 3, 1); T.mode.set(1); T.zoom() })
await pg.evaluate(() => { const r = document.getElementById('res'); r.value = 4; r.dispatchEvent(new Event('input', { bubbles: true })) })
await pg.click('#wpcopy'); const text = await pg.evaluate(() => document.getElementById('wpbox').value), a = await snap(pg)
check(/^Phosphor waypoint v1/.test(text) && /fingerprint: [0-9a-f]{8}/.test(text) && /^at: 7\.\d+ s of /m.test(text) && /^settings: \{/m.test(text) && !/[—–]/.test(text), 'S2: the waypoint text has a header, position, fingerprint and settings, with no em-dashes')
await pg.context().close()
pg = await open('?test=1&shutter=off&level=1', true)
await pg.evaluate((t) => window.PhosphorTest.wp.apply(t), text); await pg.waitForTimeout(300); const c = await snap(pg)
check(c.lvl === 1 && c.swing === a.swing && c.res === a.res && c.cells === a.cells && Math.abs(c.t - a.t) < 0.3, `S2: a fresh page with storage blocked comes back to level ${c.lvl}, ${c.swing}, rung ${c.res}, ${c.cells} step(s), ${c.t} s (was ${a.lvl}, ${a.swing}, ${a.res}, ${a.cells}, ${a.t})`)
// S3 Zach's own recipe
const ZACH = `Phosphor recipe
song: Kintsugi Acid.mp3, 138.7 BPM, feel 50 percent
DNA (song, beats 82 to 89): ATA CCG GAA CCG CTA GGA TCA GGA
RNA (look, same beats): UUA UUA UUA UUC UUA UUA UUA UUA
this beat sounds warm, soft, busy and looks crystal, full, rippling
look: Sun, palette heat, resolution rung 9 of 9, 8 bit, effects rgb
settings: {"mode":4,"zs":[5,2,2,2,2],"pal":"heat","curve":"log","amt":0.37,"bits":8,"wood":false,"crt":true,"calm":true,"res":9,"chs":true,"rl":{"on":true,"bars":1,"dir":"pp"},"seq":{"quant":"beat","gate":0.5,"bars":1,"cells":{"stutter":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"freeze":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"tear":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"rgb":[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],"blocks":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"jog":[1,0,0,0,2,0,0,0,3,0,0,0,2,0,0,0],"detail":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"crush":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"dist":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"echo":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"sweep":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}},"click":false,"bpm":100,"lvl":2,"swing":50,"tz":0}`
await pg.evaluate((t) => window.PhosphorTest.wp.apply(t), ZACH); await pg.waitForTimeout(300)
const z = await pg.evaluate(() => { const T = window.PhosphorTest; return { lvl: T.molt.level(), mode: T.zoom().mode, pal: document.getElementById('palsel').value, crt: document.getElementById('crt').checked, steps: T.sig().cells, res: +document.getElementById('res').value, msg: T.wp.msg() } })
check(z.lvl === 4 && z.mode === 4 && z.pal === 'heat' && z.crt === true && z.steps === 12 && z.res === 9, `S3: Zach's pasted recipe (saved level 2, now read as Parent) applies: level ${z.lvl}, mode ${z.mode}, palette ${z.pal}, CRT ${z.crt}, ${z.steps} steps, rung ${z.res}`)
check(/Waypoint applied/.test(z.msg) && !/Moved to/.test(z.msg), 'S5: an older recipe with no fingerprint restores the settings and does not move the place')
// S4 invalid
const before = await snap(pg)
for (const junk of ['hello', '', 'Phosphor recipe\nnothing here', 'Phosphor recipe\nsettings: {not json']) { const r = await pg.evaluate((t) => window.PhosphorTest.wp.apply(t), junk); if (r !== false) check(false, `S4: junk "${junk.slice(0, 12)}" was accepted`) }
check(JSON.stringify(await snap(pg)) === JSON.stringify(before) && /Nothing changed/.test(await pg.evaluate(() => window.PhosphorTest.wp.msg())), 'S4: text that is not a waypoint changes nothing and says so')
await pg.evaluate(() => window.PhosphorTest.wp.apply('Phosphor recipe\nsettings: {"mode":99,"res":50,"lvl":9,"swing":200,"bits":99,"zs":[9,9,9,9],"tz":-5}'))
const o = await snap(pg); check(o.lvl <= 4 && o.res >= 1 && o.res <= 9 && o.mode >= 0 && o.mode <= 4, `S4: out-of-range values are ignored field by field (level ${o.lvl}, rung ${o.res}, mode ${o.mode})`)
// S5 mismatch
await pg.evaluate(() => { window.PhosphorTest.seek(2) }); await pg.waitForTimeout(100); const fpNow = await pg.evaluate(() => window.PhosphorTest.wp.fp())
await pg.evaluate((fp) => window.PhosphorTest.wp.apply('Phosphor waypoint v1\nat: 9.00 s of 24.0\nfingerprint: 00000000\nsettings: {"mode":1}'), fpNow); await pg.waitForTimeout(150)
const t5 = await pg.evaluate(() => [window.PhosphorTest.tnow(), window.PhosphorTest.wp.msg()]); check(Math.abs(t5[0] - 2) < 0.3 && /different song/.test(t5[1]), `S5: a waypoint from a different song restores settings but leaves the place (${t5[0].toFixed(1)} s)`)
await pg.evaluate((fp) => window.PhosphorTest.wp.apply(`Phosphor waypoint v1\nat: 9.00 s of 24.0\nfingerprint: ${fp}\nsettings: {"mode":1}`), fpNow); await pg.waitForTimeout(150)
check(Math.abs((await pg.evaluate(() => window.PhosphorTest.tnow())) - 9) < 0.3, 'S5: the same song (matching fingerprint) moves to the saved place')
// S6 typing in the box
await pg.click('#svchip'); await pg.focus('#wpbox'); const lv0 = await snap(pg); await pg.keyboard.type('f i 1 2 3 4 ` z x c'); const fs = await pg.evaluate(() => [document.getElementById('wpbox').value, window.PhosphorTest.fs()])
check(fs[0].includes('f i 1 2 3 4') && fs[1] === false && (await snap(pg)).mode === lv0.mode, 'S6: typing in the box never triggers a play key')
// S7
const keys = await pg.evaluate(() => 'ok'); check(errs.length === 0, `S7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
