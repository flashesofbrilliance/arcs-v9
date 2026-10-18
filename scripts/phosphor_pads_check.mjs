#!/usr/bin/env node
// phosphor_pads_check.mjs: the pad block (amendment 47). 16 pads, banks A to D, each pad plays one slice. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_pads_check.mjs <page.html>
import { chromium, devices } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_pads_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off', errs = []
const open = async (extra = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 }, ...extra }); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); return pg }
const log = (pg) => pg.evaluate(() => window.PhosphorTest.pads.log())
let pg = await open()
// P1 Kid mode: the Pads button is there, opens a tray of 16 pads and 4 banks
await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300)
const btnVis = await pg.evaluate(() => getComputedStyle(document.getElementById('dkpad')).display !== 'none'); await pg.click('#dkpad'); await pg.waitForTimeout(200)
const dims = await pg.evaluate(() => [...document.querySelectorAll('#pbk .btn')].map((e) => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] }))
check(btnVis && dims.length === 16 && (await pg.locator('#pbkb .btn').count()) === 4 && dims.every(([w, h]) => w >= 56 && h >= 56), `P1: in Kid mode the Pads button opens 16 pads (all at least 56 by 56 px, smallest ${Math.min(...dims.map((d) => d[0]))} by ${Math.min(...dims.map((d) => d[1]))}) and 4 banks`)
// P2 first press with no slices chops the song into 16 and plays pad 1
await pg.evaluate(() => document.querySelector('[data-pk="0"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true }))); await pg.waitForTimeout(300)
const l1 = await log(pg), nsl = await pg.evaluate(() => window.PhosphorTest.slices().length)
check(nsl === 16 && l1.length === 1 && l1[0][0] === 0 && l1[0][1] === 0 && /chopped/i.test(await pg.textContent('#padmsg')), `P2: the first press chops the song into ${nsl} equal parts, plays pad 1, and says so`)
// P3 pad n plays slice n: compare each against the slice list
const sl = await pg.evaluate(() => window.PhosphorTest.slices().map((s) => [+s.t0.toFixed(3), +s.t1.toFixed(3)]))
for (let i = 0; i < 16; i++) await pg.evaluate((i) => document.querySelector(`[data-pk="${i}"]`).dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true })), i)
const l2 = (await log(pg)).slice(1); const okMap = l2.length === 16 && l2.every((e, i) => e[1] === i && e[2] === sl[i][0] && e[3] === sl[i][1])
check(okMap, 'P3: pads 1 to 16 play slices 1 to 16 from the right start and end times')
// P4 banks: with 40 slices, bank B pad 1 is slice 17 and bank C pad 9 is empty
await pg.evaluate(() => { document.getElementById('clearsl').click(); document.getElementById('zfit').click(); document.getElementById('asb').click() }); await pg.waitForTimeout(400); await pg.evaluate(() => { window.PhosphorTest.slices().length = 40 })
const n2 = await pg.evaluate(() => window.PhosphorTest.slices().length), sl2 = await pg.evaluate(() => window.PhosphorTest.slices().map((s) => [+s.t0.toFixed(3), +s.t1.toFixed(3)]))
await pg.click('#pbkb [data-bk="1"]'); await pg.waitForTimeout(100); const before = (await log(pg)).length
await pg.evaluate(() => document.querySelector('[data-pk="0"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true }))); const lb = (await log(pg)).slice(before)
await pg.click('#pbkb [data-bk="3"]'); await pg.waitForTimeout(100); const empty = await pg.getAttribute('[data-pk="15"]', 'aria-disabled'); const b4 = (await log(pg)).length
await pg.evaluate(() => document.querySelector('[data-pk="15"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true }))); const after = (await log(pg)).length
check(n2 > 20 && lb.length === 1 && lb[0][0] === 1 && lb[0][2] === sl2[16][0] && after === b4 && (n2 <= 48 ? empty === 'true' : true), `P4: with ${n2} slices bank B pad 1 plays slice 17 (${lb[0] && lb[0][2]} against ${sl2[16][0]}), and an empty pad stays silent and marked`)
// P5 keys: closed tray ignores them, open tray plays them
await pg.click('#pbkb [data-bk="0"]'); await pg.click('#dkpad'); await pg.waitForTimeout(100); const c0 = (await log(pg)).length
await pg.keyboard.press('KeyQ'); await pg.waitForTimeout(100); const closedN = (await log(pg)).length
await pg.click('#dkpad'); await pg.waitForTimeout(100)
const keys = ['Digit1', 'Digit2', 'Digit3', 'Digit4', 'KeyQ', 'KeyW', 'KeyE', 'KeyR', 'KeyA', 'KeyS', 'KeyD', 'KeyF', 'KeyZ', 'KeyX', 'KeyC', 'KeyV']
for (const k of keys) await pg.keyboard.press(k)
const lk = (await log(pg)).slice(closedN)
check(closedN === c0 && lk.length === 16 && lk.every((e, i) => e[1] === i), `P5: with the tray closed the Q key plays no pad; with it open the 16 keys 1234 QWER ASDF ZXCV play pads 1 to 16 in order (${lk.length})`)
// P6 a fast burst of all 16 keys within one frame loses none
const b6 = (await log(pg)).length; await pg.evaluate((keys) => { for (const k of keys) window.dispatchEvent(new KeyboardEvent('keydown', { code: k, bubbles: true, cancelable: true })) }, keys); const burst = (await log(pg)).length - b6
check(burst === 16, `P6: a burst of all 16 key presses in one tick plays all 16 (${burst})`)
// P7 typing in a text box does not trigger pads
await pg.evaluate(() => { const t = document.createElement('input'); t.type = 'text'; t.id = 'tmpbox'; t.style.cssText = 'position:fixed;top:0;left:0;z-index:99'; document.body.appendChild(t); t.focus() }); const b7 = (await log(pg)).length, f7 = await pg.evaluate(() => document.activeElement.id); await pg.keyboard.type('qwer 1234'); const a7 = (await log(pg)).length; check(a7 === b7 && f7 === 'tmpbox', `P7: typing in a text box plays no pads (focus ${f7}, ${b7} to ${a7})`)
// P7b only one tray is open at a time: Mix closes Pads and Pads closes Mix
await pg.evaluate(() => { document.getElementById('tmpbox').remove(); document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown')) }); await pg.waitForTimeout(1700)
const openState = () => pg.evaluate(() => [!document.getElementById('padtray').hidden, !document.getElementById('fxtray').hidden])
const s0 = await openState(); await pg.evaluate(() => document.getElementById('dkfx').click()); const s1 = await openState(); await pg.evaluate(() => document.getElementById('dkpad').click()); const s2 = await openState()
check(s0[0] && !s0[1] && !s1[0] && s1[1] && s2[0] && !s2[1], `P7b: only one tray is open at a time (pads ${s0}, then Mix ${s1}, then pads ${s2})`)
await pg.context().close()
// P8 touch on a phone
pg = await open({ ...devices['iPhone 13'] }); await pg.evaluate(() => document.getElementById('dkpad').click()); await pg.waitForTimeout(300)
const box = await pg.locator('[data-pk="5"]').boundingBox(); await pg.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2); await pg.waitForTimeout(300)
const l8 = await log(pg), ph = await pg.evaluate(() => { const r = document.getElementById('padtray').getBoundingClientRect(); return { fits: r.left >= 0 && r.right <= innerWidth, side: document.documentElement.scrollWidth > innerWidth, minH: Math.min(...[...document.querySelectorAll('#pbk .btn')].map((e) => e.getBoundingClientRect().height)) } })
check(l8.length === 1 && l8[0][1] === 5 && ph.fits && !ph.side && ph.minH >= 56, `P8: on a phone a finger tap on pad 6 plays slice 6, the tray fits the width with no sideways scroll, pads are at least ${Math.round(ph.minH)} px tall`)
check(errs.length === 0, 'P9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
