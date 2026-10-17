// phosphor_glitchpre_check.mjs: Glitch presets (Zach 2026-10-17: decision fatigue, "what does this sound like"). Usage: node scripts/phosphor_glitchpre_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_glitchpre_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.evaluate(() => { document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown')) }); await pg.waitForTimeout(1700)
await pg.evaluate(() => { let e = document.getElementById('gpre'); while (e) { if (e.tagName === 'DETAILS') e.open = true; e = e.parentElement } })
const WANT = { water: ['room', 'sweep'], robot: ['crush', 'shim'], tv: ['tear', 'rgb', 'crush'], space: ['echo', 'shim', 'room'], heavy: ['dist', 'blocks'], clean: [] }
const ALL = ['tear', 'rgb', 'blocks', 'crush', 'dist', 'echo', 'room', 'shim', 'sweep']
const on = () => pg.evaluate((A) => { const g = window.PhosphorTest.glitch().on; return A.filter((k) => g[k]).sort() }, ALL)
const click = (k) => pg.click(`[data-gp=${k}]`)
check(await pg.locator('#gpre button').count() === 6 && (await on()).length === 0, 'G1: six presets exist and nothing is on at the start')
const bads = []
for (const k of Object.keys(WANT)) { await click(k); await pg.waitForTimeout(150); const got = await on(); if (JSON.stringify(got) !== JSON.stringify([...WANT[k]].sort())) bads.push(`${k}: ${got}`) ; if (k !== 'clean') { await click(k); await pg.waitForTimeout(100); if ((await on()).length) bads.push(k + ' did not turn off') } }
check(bads.length === 0, 'G2: each preset turns on exactly its effects, and a second tap turns them off ' + bads.join(' | '))
await click('water'); await pg.waitForTimeout(100); await click('heavy'); await pg.waitForTimeout(150)
check(JSON.stringify(await on()) === JSON.stringify(['blocks', 'dist']), 'G3: choosing another preset replaces the first (no leftovers)')
check(await pg.getAttribute('[data-gp=heavy]', 'aria-pressed') === 'true' && await pg.getAttribute('[data-gp=water]', 'aria-pressed') === 'false' && /gritty/i.test(await pg.textContent('#gphint')), 'G4: the chosen preset is pressed and the hint says what it sounds like')
await click('clean'); await pg.waitForTimeout(150); check((await on()).length === 0 && !/gritty/.test(await pg.textContent('#gphint')), 'G5: Clean turns the preset effects off')
await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', true)); await click('heavy'); await pg.waitForTimeout(100); await click('clean'); await pg.waitForTimeout(100)
check((await on()).join() === 'echo', 'G6: Clean leaves an effect you latched by hand')
await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', false))
await pg.evaluate(() => document.getElementById('glitchsw').click()); await click('heavy'); await pg.waitForTimeout(150)
check((await on()).length === 0 && /Glitch is off/.test(await pg.textContent('#gphint')), 'G7: with Glitch off a glitch preset starts nothing and the hint says why')
await click('water'); await pg.waitForTimeout(150)
check((await on()).join() === 'room,sweep' && !/Glitch is off/.test(await pg.textContent('#gphint')), 'G7b: with Glitch off a sound-only preset still plays (room and sweep are not glitch)')
const sz = await pg.evaluate(() => [...document.querySelectorAll('#gpre button')].map((e) => Math.round(e.getBoundingClientRect().height)))
check(sz.every((h) => h >= 40), `G8: preset buttons are at least 40 px tall (${sz.join(',')})`)
check(errs.length === 0, 'G9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
