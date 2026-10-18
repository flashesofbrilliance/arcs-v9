// phosphor_eject_check.mjs: Eject lock and the wide display (artifact comment 2026-10-16). Usage: node scripts/phosphor_eject_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_eject_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch(), errs = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const w = await pg.evaluate(() => { const r = (s) => Math.round(document.querySelector(s).getBoundingClientRect().width); return { dock: r('#dock'), frame: r('#frame'), tag: getComputedStyle(document.getElementById('tag')).display } })
check(w.tag === 'none', 'E2: the mode readout at the top left is gone')
const hold = async (sel, ms) => { const bb = await pg.locator(sel).boundingBox(); await pg.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await pg.mouse.down(); await pg.waitForTimeout(ms); await pg.mouse.up() }
await hold('#eject', 1200); check(!(await pg.evaluate(() => window.__ejectLock())), 'E3: a 1.2 second press does not lock')
await hold('#eject', 3300)
const on = await pg.evaluate(() => ({ lock: window.__ejectLock(), lvl: document.documentElement.getAttribute('data-lvl'), fs: document.getElementById('frame').classList.contains('fs'), exitShown: getComputedStyle(document.getElementById('hexit')).display, hej: !document.getElementById('hej').hidden }))
check(on.lock && on.lvl === '1' && on.fs && on.exitShown === 'none' && on.hej, `E4: holding 3 seconds locks Kid mode full screen and hides Exit (${JSON.stringify(on)})`)
await pg.keyboard.press('Escape'); await pg.dblclick('#cv').catch(() => {}); check(await pg.evaluate(() => window.__ejectLock() && document.getElementById('frame').classList.contains('fs')), 'E5: Escape and double click do not leave the lock')
await hold('#hej', 1000); check(await pg.evaluate(() => window.__ejectLock()), 'E6: a short press on the full screen Eject does not unlock')
await hold('#hej', 3300)
const off = await pg.evaluate(() => ({ lock: window.__ejectLock(), fs: document.getElementById('frame').classList.contains('fs') }))
check(!off.lock && !off.fs, 'E7: holding 3 seconds again unlocks and leaves full screen')
// E9 holding Escape for 3 seconds enters the lock; a short Escape does not
await pg.keyboard.down('Escape'); await pg.waitForTimeout(1000); await pg.keyboard.up('Escape')
check(!(await pg.evaluate(() => window.__ejectLock())), 'E9: a 1 second Escape does not lock')
await pg.keyboard.down('Escape'); await pg.waitForTimeout(3300); await pg.keyboard.up('Escape')
check(await pg.evaluate(() => window.__ejectLock() && document.getElementById('frame').classList.contains('fs')), 'E9: holding Escape for 3 seconds enters the locked full screen')
await hold('#hej', 3300)
check(!(await pg.evaluate(() => window.__ejectLock())), 'E9: and Eject held for 3 seconds leaves it')
check(errs.length === 0, 'E8: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
