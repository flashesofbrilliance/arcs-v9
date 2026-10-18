#!/usr/bin/env node
// phosphor_consent_check.mjs: the first-load consent splash on the hosted page (amendment 40). Usage: node scripts/phosphor_consent_check.mjs <page.html>
import { chromium, devices } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_consent_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch(), url = pathToFileURL(path.resolve(page)).href, errs = []
const mk = async (extra = {}, init) => { const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, ...extra }); if (init) await ctx.addInitScript(init); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); return pg }
const st = (pg) => pg.evaluate(() => { const c = document.getElementById('consent'), m = document.querySelector('main'); return { shown: !c.hidden, modal: c.getAttribute('aria-modal'), role: c.getAttribute('role'), inert: m.inert, focus: document.activeElement && document.activeElement.id, stored: (() => { try { return localStorage.getItem('phosphor.consent.v1') } catch (e) { return 'blocked' } })() } })
let pg = await mk(); await pg.goto(url); await pg.waitForTimeout(600); let s = await st(pg)
check(s.shown && s.role === 'dialog' && s.modal === 'true' && s.inert && s.focus === 'csgo', 'C1: the first load shows a modal dialog, the page behind it is inert and Start has focus')
const text = await pg.textContent('#consent')
check(/loud/i.test(text) && /flash/i.test(text) && /grown-up/i.test(text) && /stay on this device/i.test(text) && !/[—–]/.test(text), 'C2: it covers loud sound, flashing light, grown-ups first and where data stays, with no dashes')
await pg.keyboard.press('Escape'); await pg.keyboard.press('Tab'); await pg.keyboard.press('Tab'); s = await st(pg); const inside = await pg.evaluate(() => !!document.activeElement.closest('#consent'))
check(s.shown && inside, 'C3: Escape does not dismiss it and Tab stays inside it')
const h = await pg.evaluate(() => document.getElementById('csgo').getBoundingClientRect().height)
await pg.click('#csgo'); await pg.waitForTimeout(200); s = await st(pg)
check(h >= 56 && !s.shown && !s.inert && s.stored === '1', `C4: Start (${Math.round(h)} px tall) dismisses it, frees the page and remembers`)
await pg.reload(); await pg.waitForTimeout(600); s = await st(pg); check(!s.shown && !s.inert, 'C5: after Start it does not come back on the next load')
await pg.context().close()
pg = await mk({}, () => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } }) }); await pg.goto(url); await pg.waitForTimeout(600); s = await st(pg).catch(() => ({ shown: null }))
const shownBlocked = await pg.evaluate(() => !document.getElementById('consent').hidden); await pg.click('#csgo'); await pg.waitForTimeout(200)
check(shownBlocked && await pg.evaluate(() => document.getElementById('consent').hidden), 'C6: with storage blocked it shows every load and Start still works')
await pg.context().close()
pg = await mk(); await pg.goto(url + '?test=1'); await pg.waitForTimeout(600); check(!(await pg.evaluate(() => !document.getElementById('consent').hidden)), 'C7: test mode skips it so the other checks drive the page')
await pg.context().close()
pg = await mk({ ...devices['iPhone 13'] }); await pg.goto(url); await pg.waitForTimeout(600)
const ph = await pg.evaluate(() => { const r = document.getElementById('csgo').getBoundingClientRect(); return { fits: r.left >= 0 && r.right <= innerWidth, sideways: document.documentElement.scrollWidth > innerWidth } })
check(ph.fits && !ph.sideways, 'C8: on a phone the dialog and Start fit the width with no sideways scroll')
check(errs.length === 0, 'C9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
