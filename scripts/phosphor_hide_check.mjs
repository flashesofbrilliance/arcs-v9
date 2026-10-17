// phosphor_hide_check.mjs: the player can be hidden to a bump and brought back (artifact comment 2026-10-16). Usage: node scripts/phosphor_hide_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_hide_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href, errs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, hasTouch: true }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const st = () => pg.evaluate(() => { const d = document.getElementById('dock'), r = d.getBoundingClientRect(), bu = document.getElementById('dkbump').getBoundingClientRect(); return { attr: document.documentElement.getAttribute('data-dock'), inert: d.inert, dockVis: getComputedStyle(d).visibility, dockTop: Math.round(r.top), bumpShown: getComputedStyle(document.getElementById('dkbump')).display !== 'none', bumpH: Math.round(bu.height), pad: getComputedStyle(document.body).paddingBottom, ih: innerHeight } })
let s = await st(); check(s.attr === null && s.dockVis === 'visible' && !s.bumpShown, 'H1: the player starts shown and the bump is not')
await pg.click('#dkhide'); await pg.waitForTimeout(400); s = await st()
check(s.attr === 'hidden' && s.dockVis === 'hidden' && s.inert && s.bumpShown && s.bumpH >= 44, `H2: Hide slides the player away and shows a bump (${s.bumpH} px tall, dock inert ${s.inert})`)
check(parseInt(s.pad) <= 90, `H3: the page padding shrinks with the player (${s.pad})`)
await pg.keyboard.press('Space'); await pg.waitForTimeout(400); const playing = await pg.evaluate(() => document.getElementById('play').textContent)
check(/Pause/i.test(playing) || await pg.evaluate(() => window.PhosphorTest && window.PhosphorTest.playing ? window.PhosphorTest.playing() : false), `H4: Space still plays while the player is hidden (Play button reads "${playing}")`)
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); s = await st()
check(s.attr === 'hidden', 'H5: the hidden choice is remembered after a reload')
await pg.click('#dkbump'); await pg.waitForTimeout(400); s = await st()
check(s.attr === null && s.dockVis === 'visible' && !s.inert && !s.bumpShown, 'H6: the bump brings the player back')
const bb = await pg.locator('#dock').boundingBox(); await pg.mouse.move(bb.x + bb.width / 2, bb.y + 4); await pg.mouse.down(); await pg.mouse.move(bb.x + bb.width / 2, bb.y + 120, { steps: 8 }); await pg.mouse.up(); await pg.waitForTimeout(400); s = await st()
check(s.attr === 'hidden', 'H7: dragging the player down hides it')
// H8 to H13: the bump moves, tucks and is remembered. Done with real touch events (CDP) because a fixed, undraggable bump on a phone was the bug (Zach, 2026-10-17).
const bump = () => pg.evaluate(() => { const e = document.getElementById('dkbump'), r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height, tuck: e.getAttribute('data-tuck'), hidden: document.documentElement.getAttribute('data-dock') } })
const cdp = await ctx.newCDPSession(pg), tch = (type, x, y) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y, id: 1 }] })
const drag = async (from, to) => { await tch('touchStart', from[0], from[1]); for (let k = 1; k <= 8; k++) { await tch('touchMove', from[0] + (to[0] - from[0]) * k / 8, from[1] + (to[1] - from[1]) * k / 8); await pg.waitForTimeout(16) } await tch('touchEnd'); await pg.waitForTimeout(150) }
await pg.waitForTimeout(300); let u = await bump()
await drag([u.x, u.y], [300, 400]); let v = await bump()
check(Math.abs(v.x - 300) < 6 && Math.abs(v.y - 400) < 6 && v.hidden === 'hidden' && !v.tuck, `H8: dragging the bump by touch moves it (${Math.round(u.x)},${Math.round(u.y)} to ${Math.round(v.x)},${Math.round(v.y)}) and leaves the player hidden`)
await drag([v.x, v.y], [1275, 450]); v = await bump()
check(v.tuck === 'r' && v.w <= 28 && v.hidden === 'hidden', `H9: dropping it on the right edge tucks it into a slim tab (${Math.round(v.w)} px wide)`)
await tch('touchStart', v.x, v.y); await tch('touchEnd'); await pg.waitForTimeout(200); v = await bump()
check(!v.tuck && v.hidden === 'hidden', 'H10: tapping the tab brings the bump back out and keeps the player hidden')
await drag([v.x, v.y], [200, 500]); await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); v = await bump()
check(Math.abs(v.x - 200) < 6 && Math.abs(v.y - 500) < 6 && v.hidden === 'hidden', `H11: the bump position is remembered after a reload (${Math.round(v.x)},${Math.round(v.y)})`)
await tch('touchStart', v.x, v.y); await tch('touchEnd'); await pg.waitForTimeout(400); s = await st()
check(s.attr === null, 'H12: a tap on the bump brings the player back')
await pg.click('#dkhide'); await pg.waitForTimeout(300); await pg.focus('#dkbump'); await pg.keyboard.press('Enter'); await pg.waitForTimeout(300); s = await st()
check(s.attr === null, 'H13: Enter on the focused bump also brings the player back')
check(errs.length === 0, 'H14: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
