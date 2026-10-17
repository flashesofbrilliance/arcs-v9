// phosphor_hide_check.mjs: the player can be hidden to a bump and brought back (artifact comment 2026-10-16). Usage: node scripts/phosphor_hide_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_hide_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href, errs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
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
const bu = await pg.locator('#dkbump').boundingBox(); await pg.mouse.move(bu.x + bu.width / 2, bu.y + 20); await pg.mouse.down(); await pg.mouse.move(bu.x + bu.width / 2, bu.y - 80, { steps: 8 }); await pg.mouse.up(); await pg.waitForTimeout(400); s = await st()
check(s.attr === null, 'H8: dragging the bump up brings it back')
check(errs.length === 0, 'H9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
