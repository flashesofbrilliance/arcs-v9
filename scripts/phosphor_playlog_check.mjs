#!/usr/bin/env node
// phosphor_playlog_check.mjs: the opt-in play log (amendment 42). Local only, control ids and values, never names. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_playlog_check.mjs <page.html>
import { chromium } from 'playwright'
import { copyFileSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_playlog_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const secret = path.join(mkdtempSync(path.join(tmpdir(), 'plog-')), 'my-secret-lullaby-title.wav'); copyFileSync('/private/tmp/claude-501/fx/' + file, secret)
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4', errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); let pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
const ready = async () => { await pg.waitForFunction(() => document.getElementById('status').textContent === '') }
const stored = () => pg.evaluate(() => localStorage.getItem('phosphor.playlog.v1'))
const openGrown = () => pg.evaluate(() => { let e = document.getElementById('elb'); while (e) { if (e.tagName === 'DETAILS') e.open = true; e = e.parentElement } })
await pg.goto(url); await ready(); await pg.setInputFiles('input[type=file]', secret); await pg.waitForTimeout(2500)
await pg.click('#play'); await pg.waitForTimeout(400); await pg.evaluate(() => { const e = document.getElementById('scrub'); e.value = 300; e.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.keyboard.press('KeyZ'); await pg.waitForTimeout(6000)
check(!(await stored()) && (await pg.evaluate(() => window.PhosphorTest.elog.ev().length)) === 0, 'L1: off by default: playing, scrubbing and pressing keys records nothing in memory or storage')
await openGrown(); await pg.click('#elb'); await pg.waitForTimeout(100)
check(await pg.evaluate(() => window.PhosphorTest.elog.on()) && /Play log: on/.test(await pg.textContent('#elb')) && await pg.getAttribute('#elb', 'aria-pressed') === 'true', 'L2: the grown-up switch turns it on and says so')
await pg.evaluate(() => document.querySelector('[data-gp=robot]').click()); await pg.evaluate(() => { const e = document.getElementById('scrub'); for (const v of [100, 200, 400]) { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) } }); await pg.keyboard.press('KeyX'); await pg.click('#play'); await pg.waitForTimeout(200); await pg.click('#play'); await pg.waitForTimeout(300)
const ev = await pg.evaluate(() => window.PhosphorTest.elog.ev()); const kinds = new Set(ev.map((e) => e[2]))
check(['start', 'tap', 'set', 'key', 'play', 'stop'].every((k) => kinds.has(k)), `L3: it records starts, taps, slider moves, keys and play and stop (${[...kinds].join(', ')})`)
const sets = ev.filter((e) => e[2] === 'set' && e[3] === 'scrub'); if (process.env.PL_DEBUG) console.log(JSON.stringify(sets))
check(sets.length === 1 && sets[0][4] === 400, 'L4: a quick run of slider moves is one event with the last value, not a flood')
await pg.evaluate(() => window.PhosphorTest.seek(1)); await pg.waitForTimeout(100)
const dump = await stored(); check(!!dump && !/secret|lullaby|\.wav/i.test(dump), 'L5: the stored log holds no song or file name (the file was called my-secret-lullaby-title.wav)')
await pg.evaluate(() => window.PhosphorTest.elog.seed([[1000, null, 'start', null, null], [3500, null, 'play', null, null], [4000, null, 'tap', 'gp=robot', null], [5000, 2.0, 'set', 'mv_echo', 40], [6000, 3.0, 'set', 'mv_echo', 50], [7000, null, 'tap', 'pad', null], [9000000, null, 'start', null, null], [9001000, null, 'key', 'KeyZ', null], [9002000, null, 'err', 'boom', null], [9003000, null, 'tap', 'szin', null]]))
const sm = await pg.evaluate(() => window.PhosphorTest.elog.summary())
check(sm.sessions === 2 && sm.events === 10 && sm.medianFirstSoundSec === 2.5 && sm.presetTaps === 1 && sm.sliderMoves === 2 && sm.errors === 1 && sm.stoppedAt[0] === 'pad' && sm.stoppedAt[1] === 'szin' && sm.top[0] === 'mv_echo x2', `L6: the summary reads back 2 sessions, first sound after ${sm.medianFirstSoundSec} s (want 2.5), 1 preset, 2 slider moves, 1 error, where each stopped, top control ${sm.top[0]}`)
await pg.evaluate(() => { document.getElementById('elb').scrollIntoView() }); const shown = await pg.textContent('#elsum'); check(/2 session/.test(shown) && /First sound after 2.5 s/.test(shown) && !/[—–]/.test(shown), 'L7: the grown-up panel shows the summary in plain words')
await pg.evaluate(() => window.dispatchEvent(new Event('pagehide'))); await pg.reload(); await ready(); const again = await pg.evaluate(() => ({ on: window.PhosphorTest.elog.on(), n: window.PhosphorTest.elog.ev().length }))
check(again.on && again.n >= 10, `L8: the log and the switch survive a reload (${again.n} events, on ${again.on})`)
await openGrown(); await pg.click('#elclr'); await pg.waitForTimeout(100); const cleared = await pg.evaluate(() => window.PhosphorTest.elog.ev().length); const st2 = JSON.parse(await stored())
check(cleared === 0 && st2.ev.length === 0, 'L9: Clear log empties memory and storage')
await pg.evaluate(() => window.PhosphorTest.elog.seed(Array.from({ length: 3100 }, (_, i) => [1000 + i, null, 'tap', 'x', null]))); await pg.evaluate(() => document.querySelector('#play').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }))); const cap = await pg.evaluate(() => window.PhosphorTest.elog.ev().length)
check(cap <= 3000, `L10: the log is capped (3100 seeded, ${cap} kept)`)
await pg.context().close(); const ctx2 = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx2.addInitScript(() => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } }) }); pg = await ctx2.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(url); await pg.waitForTimeout(1500)
await pg.evaluate(() => { let e = document.getElementById('elb'); while (e) { if (e.tagName === 'DETAILS') e.open = true; e = e.parentElement } }); await pg.click('#elb'); await pg.click('#elclr'); await pg.waitForTimeout(100)
check(errs.length === 0, 'L11: with storage blocked it still runs without errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
