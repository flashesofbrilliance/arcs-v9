#!/usr/bin/env node
// phosphor_mode_check.mjs: K1 to K8 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 28, Kid and Parent). Replaces the old four-level molt check.
// Usage: node scripts/phosphor_mode_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium, devices } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_mode_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch(), base = pathToFileURL(path.resolve(page)).href, errs = []
const open = async (q, opts = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 }, ...opts }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} }); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + q); await pg.waitForTimeout(1000); return pg }
const lvl = (pg) => pg.evaluate(() => document.documentElement.dataset.lvl)
const shown = (pg) => pg.evaluate(() => [...document.querySelectorAll('[data-min]')].filter((e) => getComputedStyle(e).display !== 'none').length)
// K1
let pg = await open('?shutter=off')
check((await lvl(pg)) === '1' && (await shown(pg)) === 0 && (await pg.getAttribute('#mdKid', 'aria-pressed')) === 'true', 'K1: a first visit opens in Kid with no Parent element showing')
check(await pg.evaluate(() => ['kpick', 'kcol', 'kzoom', 'kwob', 'play', 'scrub', 'mdKid', 'mdParent'].every((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' }) && getComputedStyle(document.getElementById('notesb')).display !== 'none'), 'K1: the picker, play, the look buttons, Notes and the switch are visible in Kid')
// K2 a tap does not open Parent
const bb = await pg.locator('#mdParent').boundingBox(); await pg.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await pg.mouse.down(); await pg.waitForTimeout(200); await pg.mouse.up(); await pg.waitForTimeout(1500)
check((await lvl(pg)) === '1', 'K2: a quick tap on Parent does not open Parent')
await pg.click('#mdParent', { delay: 300 }); await pg.waitForTimeout(1700); check((await lvl(pg)) === '1', 'K2: a click that is released at 0.3 seconds does not open Parent')
// K3 pointer hold
await pg.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await pg.mouse.down(); await pg.waitForTimeout(700); const mid = await lvl(pg); const holdAttr = await pg.getAttribute('#mdParent', 'data-hold'); await pg.waitForTimeout(1000); await pg.mouse.up()
check(mid === '1' && holdAttr !== null && (await lvl(pg)) === '4' && (await shown(pg)) > 5, `K3: holding Parent for 1.5 seconds with a pointer opens it (still Kid at 0.7 s, then Parent; ${await shown(pg)} Parent elements showing)`)
// K5 reload keeps it
await pg.waitForTimeout(700); await pg.reload(); await pg.waitForTimeout(1200); check((await lvl(pg)) === '4', 'K5: the mode survives a reload')
// K6 focus
await pg.evaluate(() => { document.querySelector('#grown').open = true; const el = document.getElementById('sessrec'); el && el.focus() })
await pg.click('#mdKid'); check((await lvl(pg)) === '1' && (await pg.evaluate(() => document.activeElement.id)) === 'mdKid', 'K4: one tap returns to Kid, and K6: focus inside a Parent control moves to the Kid button')
// K4 keyboard hold
await pg.focus('#mdParent'); await pg.keyboard.down('Enter'); await pg.waitForTimeout(600); const kmid = await lvl(pg); await pg.waitForTimeout(1100); await pg.keyboard.up('Enter')
check(kmid === '1' && (await lvl(pg)) === '4', 'K4: holding Enter on the focused Parent button for 1.5 seconds also opens it')
await pg.focus('#mdKid'); await pg.keyboard.press('Enter'); check((await lvl(pg)) === '1', 'K4: Enter on Kid returns at once')
// K7 no banner
check(await pg.evaluate(() => !document.getElementById('molt') && !document.getElementById('lvl') && !document.getElementById('moltyes')), 'K7: no offer banner, counters or level slider remain')
await pg.context().close()
// url param
pg = await open('?level=4&shutter=off'); check((await lvl(pg)) === '4', 'K3: ?level=4 opens Parent for a grown-up who prefers an address'); await pg.context().close()
// K8 touch
pg = await open('?shutter=off', { ...devices['iPhone 13'] }); const sz = await pg.evaluate(() => ['mdKid', 'mdParent'].map((id) => { const r = document.getElementById(id).getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] })); const hs = await pg.evaluate(() => document.documentElement.scrollWidth > innerWidth)
check(sz.every(([w, h]) => h >= 48 && w >= 48) && !hs, `K8: on a phone both buttons are at least 48 px (${sz.map((s) => s.join('x')).join(', ')}) and the header does not scroll sideways`)
check(errs.length === 0, `K7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(failed() ? 1 : 0)
