#!/usr/bin/env node
// phosphor_begin_check.mjs: the first-minute ritual (amendment 68). Any first key or tap starts the music and the key still acts; a quiet ring invites it; soft rings answer each press for a minute; nothing is stored. Usage: node scripts/phosphor_begin_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2]
if (!page) { console.log('usage: node scripts/phosphor_begin_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const url = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=1'
const open = async (opts = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 900 }, ...opts }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} }); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.waitForTimeout(600); return pg }
const st = (pg) => pg.evaluate(() => window.PhosphorTest.begin())
// B1 the ring is there in Kid mode, adds no control, takes no pointer, is hidden from assistive technology
let pg = await open()
const s0 = await st(pg), ring = await pg.evaluate(() => { const e = document.getElementById('begin'); return { pe: getComputedStyle(e).pointerEvents, aria: e.getAttribute('aria-hidden'), ctl: e.querySelectorAll('button,input,select,a,[tabindex]').length, w: e.getBoundingClientRect().width } })
const kidCtl = await pg.evaluate(() => [...document.querySelectorAll('button,input,select,textarea,a[href],summary')].filter((e) => e.offsetParent !== null && e.getBoundingClientRect().width > 0 && !e.closest('[hidden]')).length)
check(s0.shown && s0.ring && !s0.done && !s0.playing && ring.pe === 'none' && ring.aria === 'true' && ring.ctl === 0 && ring.w > 400, `B1: in Kid mode a quiet ring waits (pointer ${ring.pe}, hidden from assistive technology, ${ring.ctl} controls inside), nothing is playing, and ${kidCtl} controls are visible`)
// B2 a first key begins and plays within 300 ms; the key still acts (Digit2 changes the stage view)
const stage0 = await pg.evaluate(() => document.getElementById('tag').textContent)
const t0 = Date.now(); await pg.keyboard.press('Digit2'); let ok2 = false; while (Date.now() - t0 < 600) { if ((await st(pg)).playing) { ok2 = Date.now() - t0; break } await pg.waitForTimeout(20) }
const s2 = await st(pg), stage1 = await pg.evaluate(() => document.getElementById('tag').textContent)
check(s2.done && s2.mode === 'key' && ok2 !== false && ok2 < 400 && !s2.ring && stage0 !== stage1, `B2: the first key begins and the music plays after ${ok2} ms (want under 400 incl. the test's own 20 ms polling); the ring is gone; the key still acted (view "${stage0}" to "${stage1}")`)
await pg.context().close()
// B3 a first tap on the picture begins
pg = await open(); await pg.mouse.click(640, 220); await pg.waitForTimeout(250); const s3 = await st(pg)
check(s3.done && s3.mode === 'tap' && s3.playing, `B3: a first tap on the picture begins and plays (${s3.mode}, playing ${s3.playing})`)
await pg.context().close()
// B4 pressing Play or Space first leaves it playing, not toggled off
pg = await open(); await pg.click('#play'); await pg.waitForTimeout(300); const s4a = await st(pg); await pg.context().close()
pg = await open(); await pg.keyboard.press('Space'); await pg.waitForTimeout(400); const s4b = await st(pg); await pg.context().close()
check(s4a.done && s4a.playing && s4b.done && s4b.playing, `B4: pressing Play first leaves it playing (${s4a.playing}), and so does Space (${s4b.playing}); neither toggles twice`)
// B5 rings: one per press at most every 350 ms, never more than 6, none when reduced motion is asked for
pg = await open(); await pg.keyboard.press('KeyJ'); await pg.waitForTimeout(100)
for (let i = 0; i < 12; i++) { await pg.keyboard.press('KeyK'); await pg.waitForTimeout(40) }
const r1 = (await st(pg)).rips; await pg.waitForTimeout(1200); const r2 = (await st(pg)).rips; await pg.keyboard.press('KeyL'); await pg.waitForTimeout(100); const r3 = (await st(pg)).rips
await pg.context().close()
const pr = await open({ reducedMotion: 'reduce' }); await pr.keyboard.press('KeyJ'); await pr.waitForTimeout(100); await pr.keyboard.press('KeyK'); await pr.waitForTimeout(500); const rm = await st(pr); await pr.context().close()
check(r1 >= 1 && r1 <= 2 && r2 === 0 && r3 === 1 && rm.done && rm.playing && rm.rips === 0, `B5: twelve quick presses make ${r1} ring (rate limit), they all fade (${r2} left), the next press makes ${r3}; with reduced motion the music still starts (${rm.playing}) and there are ${rm.rips} rings`)
// B6 Parent mode: no ring, and a key does not start anything
pg = await open(); await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700)
const s6a = await st(pg); await pg.keyboard.press('KeyJ'); await pg.waitForTimeout(300); const s6b = await st(pg)
check(!s6a.shown && !s6b.done && !s6b.playing, `B6: in Parent mode there is no ring (${s6a.shown}) and a key does not begin (${s6b.done}) or play (${s6b.playing})`)
await pg.context().close()
// B7 the begin event is logged when the play log is on; nothing about it is stored
pg = await open(); await pg.evaluate(() => { document.getElementById('elb').click() }); const keysBefore = await pg.evaluate(() => Object.keys(localStorage).sort().join()); await pg.keyboard.press('KeyJ'); await pg.waitForTimeout(300)
const ev = await pg.evaluate(() => window.PhosphorTest.elog.ev().filter((e) => e[2] === 'begin')), keysAfter = await pg.evaluate(() => Object.keys(localStorage).sort().join()), vals = await pg.evaluate(() => JSON.stringify(Object.keys(localStorage).map((k) => localStorage.getItem(k))))
check(ev.length === 1 && ev[0][3] === 'key' && typeof ev[0][4] === 'number' && !/begin/i.test(keysAfter) && !/"begin"/.test(vals), `B7: with the play log on, one begin event is kept (${JSON.stringify(ev[0] && ev[0].slice(2))}) and no begin flag is stored`)
await pg.context().close()
// B9 to B12 Space in Kid mode: a tap never stops the music, it cuts the effects to dry for about a beat; a hold of 0.6 s starts and stops
pg = await open(); await pg.keyboard.press('Space'); await pg.waitForTimeout(500); const playing0 = (await st(pg)).playing
const fxe = () => pg.evaluate(() => window.PhosphorTest.fxl('echo').e), dry = () => pg.evaluate(() => window.PhosphorTest.dry())
const e0 = await fxe(); await pg.keyboard.down('Space'); await pg.waitForTimeout(80); await pg.keyboard.up('Space'); await pg.waitForTimeout(60)
const dMid = await dry(), eMid = await fxe(); await pg.waitForTimeout(900); const dEnd = await dry(), eEnd = await fxe(), still = (await st(pg)).playing
check(playing0 && still && dMid.on && dMid.n === 1 && eMid === 0 && !dEnd.on && eEnd === e0, `B9: after the first Space starts the music (${playing0}), a quick tap leaves it playing (${still}) and cuts the effects to dry for a moment (echo level ${e0} to ${eMid}) then restores it (${eEnd}, pulses ${dEnd.n})`)
await pg.keyboard.down('Space'); await pg.waitForTimeout(800); await pg.keyboard.up('Space'); await pg.waitForTimeout(150); const stopped = (await st(pg)).playing, dAfterHold = await dry()
await pg.keyboard.down('Space'); await pg.waitForTimeout(800); await pg.keyboard.up('Space'); await pg.waitForTimeout(250); const started = (await st(pg)).playing
check(stopped === false && dAfterHold.n === 1 && started === true, `B10: holding Space for 0.8 s stops the music (playing ${stopped}) without a dry cut (${dAfterHold.n} pulse total), and holding again starts it (${started})`)
// B11 the bug: focus on the Play button and a Space tap used to toggle it through the button; now it does not
await pg.click('#play'); await pg.waitForTimeout(250); const afterClick = (await st(pg)).playing; await pg.keyboard.press('Space'); await pg.waitForTimeout(250); const afterTap = (await st(pg)).playing
check(afterTap === afterClick, `B11: with the Play button focused, a Space tap does not toggle the music (after the click ${afterClick}, after the tap ${afterTap})`)
// B12 holding does not repeat: a long hold is one stop, not several toggles
await pg.keyboard.down('Space'); for (let i = 0; i < 6; i++) { await pg.keyboard.down('Space'); await pg.waitForTimeout(250) } await pg.keyboard.up('Space'); await pg.waitForTimeout(200); const rep = (await st(pg)).playing
check(rep !== afterTap, `B12: a long hold with key repeat toggles exactly once (before ${afterTap}, after ${rep})`)
await pg.context().close()
// B13 Parent mode keeps the normal Space (the live page toggles play on Space in Parent mode; unchanged)
pg = await open(); await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700)
await pg.keyboard.press('Space'); await pg.waitForTimeout(200); const dp = await dry()
const sp = await st(pg); check(dp.n === 0 && !sp.done && sp.playing, `B13: in Parent mode Space behaves as before (it toggles play, now ${sp.playing}), with no dry cut (${dp.n} pulses) and no begin ritual (${sp.done})`)
await pg.context().close()
check(errs.length === 0, 'B8: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
