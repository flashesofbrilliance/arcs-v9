#!/usr/bin/env node
// phosphor_dock_check.mjs: D1 to D7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 32, one sticky player). D8 is the older suites.
// Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_dock_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium, devices } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_dock_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href, errs = []
const open = async (q, extra = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 900 }, ...extra }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + q); await pg.waitForTimeout(1000); return pg }
let pg = await open('?test=1&shutter=off&level=4')
// D1
const d1 = await pg.evaluate(() => { const d = document.getElementById('dock'), r = d && d.getBoundingClientRect(), cs = d && getComputedStyle(d); const has = (id) => !!d && d.contains(document.getElementById(id)); return { n: document.querySelectorAll('#dock').length, fixed: cs && cs.position === 'fixed', bottom: r && Math.round(innerHeight - r.bottom), ids: ['play', 'dtitle', 'clock', 'scrub', 'kpick'].every(has), tp: !!document.getElementById('tp'), bigPlay: !!document.querySelector('.deck #play') } })
check(d1.n === 1 && d1.fixed && d1.bottom <= 20 && d1.ids && !d1.tp && !d1.bigPlay, `D1: one fixed dock at the bottom (${d1.bottom} px up) holding Play, title, time, scrubber and Add song; the old transport row is gone`)
// D2 add song opens a picker and loads
const [fc] = await Promise.all([pg.waitForEvent('filechooser', { timeout: 5000 }).catch(() => null), pg.click('#kpick')]); check(!!fc, 'D2: Add song opens a file picker')
if (fc) await fc.setFiles(file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 }); await pg.waitForTimeout(400)
const t2 = await pg.evaluate(() => [document.getElementById('dtitle').textContent, document.getElementById('clock').textContent]); check(/break-100/.test(t2[0]) && /\/ 0:24/.test(t2[1]), `D2: loading updated the title (${t2[0]}) and the time (${t2[1]})`)
// D3 the level meter lives at the top (Pocket strip), not in the player
await pg.click('#play'); await pg.waitForTimeout(600); const hasM = await pg.evaluate(() => !!document.getElementById('dmeter')); await pg.click('#play')
check(!hasM, 'D3: the player carries no level meter of its own')
// D4 scrubber follows and seeks
await pg.evaluate(() => window.PhosphorTest.seek(2)); await pg.click('#play'); await pg.waitForTimeout(500); const s0 = +(await pg.inputValue('#scrub')); await pg.waitForTimeout(1500); const s1 = +(await pg.inputValue('#scrub')); await pg.click('#play')
check(s1 > s0 + 30, `D4: the scrubber moved with playback (${s0} to ${s1} of 1000)`)
await pg.evaluate(() => { const s = document.getElementById('scrub'); s.value = 500; s.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.waitForTimeout(250); const at = await pg.evaluate(() => window.PhosphorTest.tnow()); check(Math.abs(at - 12) < 1, `D4: dragging the scrubber to the middle seeks there (${at.toFixed(1)} s of 24)`)
// D5 room under the page
const room = await pg.evaluate(() => ({ pad: parseFloat(getComputedStyle(document.body).paddingBottom), dock: document.getElementById('dock').offsetHeight })); check(room.pad >= room.dock, `D5: the page keeps ${Math.round(room.pad)} px of room at the bottom for a ${room.dock} px dock`)
await pg.context().close()
// D6 phone
pg = await open('?shutter=off', { ...devices['iPhone 13'] }); const ph = await pg.evaluate(() => { const g = (id) => { const r = document.getElementById(id).getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] }; return { play: g('play'), up: g('kpick'), scrub: g('scrub'), scroll: document.documentElement.scrollWidth > innerWidth } })
check(ph.play[1] >= 48 && ph.up[1] >= 48 && ph.scrub[1] >= 44 && !ph.scroll, `D6: on a phone Play is ${ph.play.join('x')}, Add song ${ph.up.join('x')}, the scrubber ${ph.scrub.join('x')}, and nothing scrolls sideways`)
await pg.context().close()
const p360 = await open('?shutter=off', { ...devices['iPhone 13'], viewport: { width: 360, height: 740 }, screen: { width: 360, height: 740 } }); check(!(await p360.evaluate(() => document.documentElement.scrollWidth > innerWidth)), 'D6: no sideways scroll at 360 px'); await p360.context().close()
// D7 pocket skin look on the same dock
pg = await open('?shutter=off&skin=pocket'); const d7 = await pg.evaluate(() => ({ n: document.querySelectorAll('#dock').length, bg: getComputedStyle(document.getElementById('dock')).backgroundImage, strip: !!document.getElementById('ledstrip') })); check(d7.n === 1 && /svg|gradient/.test(d7.bg) && d7.strip, 'D7: with the Pocket skin there is still exactly one dock, with the Pocket look, and the LED strip')
check(errs.length === 0, `D7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(failed() ? 1 : 0)
