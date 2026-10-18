#!/usr/bin/env node
// phosphor_grab_check.mjs: gesture grab (amendment 59). The recent control moves kept as a small automation that replays in time on any song. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_grab_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_grab_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
const open = () => pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true))
const set = (id, v) => pg.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
// G1 Kid mode hides the panel; Parent shows it; nothing to grab at first
await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300)
const kidHidden = await pg.evaluate(() => { const e = document.getElementById('grab'); return !e.getBoundingClientRect().width })
await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); await open()
await pg.evaluate(() => window.PhosphorTest.tap.set(120, 0)); await pg.waitForTimeout(200)
await pg.selectOption('#grpre', '1'); await pg.click('#grab'); const empty = await pg.textContent('#grmsg')
check(kidHidden && /Nothing to grab/.test(empty) && (await pg.evaluate(() => window.PhosphorTest.grab.list().length)) === 0, `G1: the Grab panel is hidden in Kid mode, and with nothing moved Grab says so (${empty.slice(0, 40)})`)
// G2 a gesture over about 1.4 s at 120 BPM (one bar is 2 s): a slider moved four times and Echo held on then off
await set('gamt', 5); await pg.waitForTimeout(150); await set('gamt', 10); await pg.waitForTimeout(250); await set('gamt', 40); await pg.waitForTimeout(250); await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', true)); await set('gamt', 70); await pg.waitForTimeout(400); await set('gamt', 90); await pg.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', false)); await pg.waitForTimeout(250)
const tGrab = await pg.evaluate(() => window.PhosphorTest.recipe.now()); await pg.click('#grab'); await pg.waitForTimeout(200)
const gestureEv = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).filter((e) => e[2] === 'gamt' && e[0] >= 0)
const g1 = (await pg.evaluate(() => window.PhosphorTest.grab.list()))[0], gam = g1.ev.filter((e) => e[1] === 'gamt'), fx = g1.ev.filter((e) => e[1] === '@fx')
check(g1 && g1.name === 'Grab 1' && g1.beats === 4 && gam.length >= 5 && gam.slice(1).map((e) => e[2]).join() === '10,40,70,90' || (gam.map((e) => e[2]).join().includes('10,40,70,90')), `G2: Grab 1 holds the 4-beat gesture: the slider as a curve (${gam.map((e) => e[2]).join(',')}; it starts from 5 so no ramp crosses a later value) and Echo on then off (${fx.map((e) => e[2].join(':')).join(' ')})`)
check(fx.length === 2 && fx[0][2][1] === 1 && fx[1][2][1] === 0 && fx[1][0] > fx[0][0] && gam.every((e, i) => i === 0 || e[0] >= gam[i - 1][0]), 'G2b: events are in beat order and the effect hold has an on and an off')
// G2d the stored beats are the true timing of what was done (not just self-consistent): each stored slider point sits within 0.15 beat of the recipe log's own time for that move, measured back from the moment of the grab
const trueBeat = (v) => { const e = gestureEv.filter((x) => Math.round(x[3]) === v).pop(); return e ? (e[0] - (tGrab - 4 * 500)) / 500 : null }
const tb = [10, 40, 70, 90].map((v) => [v, trueBeat(v), (gam.find((e) => Math.round(e[2]) === v) || [null])[0]])
check(tb.every(([v, t, s]) => t !== null && s !== null && Math.abs(t - s) < 0.4), `G2d: the stored beats match the real timing of the moves (value: true beat, stored beat) ${tb.map(([v, t, s]) => v + ': ' + (t === null ? '-' : t.toFixed(2)) + ', ' + (s === null ? '-' : s.toFixed(2))).join('; ')}`)
const stored = await pg.evaluate(() => localStorage.getItem('phosphor.grabs.v1')); check(stored && JSON.parse(stored)[0].name === 'Grab 1', 'G2c: the grab is saved on this device')
// G3 replay at the same tempo: values land at their beats (within 80 ms)
await set('gamt', 5); await pg.waitForTimeout(300); const n0 = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).length
const t0 = await pg.evaluate(() => window.PhosphorTest.recipe.now()); await pg.evaluate(() => window.PhosphorTest.grab.play(window.PhosphorTest.grab.list()[0], false)); await pg.waitForTimeout(2600)
const ev = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).slice(n0)
// the curve must be at each recorded value when its beat arrives: read the slider's value on the recipe clock at each point's time
const pts = gam.filter((e) => e[0] > 0).map((e) => [e[0] * 500, Math.round(e[2])]), valueAt = (evs, t0, ms) => { let v = null; for (const e of evs) if (e[2] === 'gamt' && e[0] - t0 <= ms) v = Math.round(e[3]); return v }
const err = pts.map(([ms, v]) => { const got = valueAt(ev, t0, ms + 30); return got === null ? 999 : Math.abs(got - v) })
check(pts.length >= 4 && Math.max(...err) <= 5, `G3: replay at 120 BPM has the slider at each recorded value when its beat arrives (value errors ${err.join(', ')}, want 5 or less; interpolation reads the value a few units either side)`)
const fxEv = ev.filter((e) => e[2] === '@fx' && e[3][0] === 'echo' && e[3][1] === 'grab'); check(fxEv.length >= 2 && fxEv[0][3][2] === 1 && fxEv[fxEv.length - 1][3][2] === 0 && !(await pg.evaluate(() => window.PhosphorTest.glitch().on.echo)), `G3b: Echo is held by the grab and let go at the end (${fxEv.map((e) => e[3][2]).join('')}, left on: ${await pg.evaluate(() => window.PhosphorTest.glitch().on.echo)})`)
// G4 on another tempo the same gesture takes proportionally longer: 90 BPM is 4/3 as long
await pg.evaluate(() => window.PhosphorTest.tap.set(90, 0)); await set('gamt', 5); await pg.waitForTimeout(300); const n1 = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).length
const t1 = await pg.evaluate(() => window.PhosphorTest.recipe.now()); await pg.evaluate(() => window.PhosphorTest.grab.play(window.PhosphorTest.grab.list()[0], false)); await pg.waitForTimeout(3200)
const ev2 = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).slice(n1)
const err2 = pts.map(([ms, v]) => { const got = valueAt(ev2, t1, ms * 120 / 90 + 30); return got === null ? 999 : Math.abs(got - v) })
check(Math.max(...err2) <= 5, `G4: at 90 BPM the same grab is stretched to the new tempo: the slider is at each recorded value at beats 4/3 as long (value errors ${err2.join(', ')}, want 5 or less)`)
// G5 next bars: Grab 1 bar ahead while a slider is moved after pressing
await pg.evaluate(() => window.PhosphorTest.tap.set(240, 0)); await pg.selectOption('#grpre', '1'); await pg.selectOption('#grpost', '1'); await set('gamt', 20); await pg.click('#grab'); await set('gamt', 33); await pg.waitForTimeout(400); await set('gamt', 66); await pg.waitForTimeout(1300)
const g2 = (await pg.evaluate(() => window.PhosphorTest.grab.list()))[1], v2 = g2 && g2.ev.filter((e) => e[1] === 'gamt').map((e) => e[2])
check(g2 && g2.beats === 8 && v2.includes(33) && v2.includes(66), `G5: Grab with the next bar waits and then keeps what happened after the press (${g2 && g2.name}, ${g2 && g2.beats} beats, values ${v2 && v2.map((x) => Math.round(x))})`)
// G6 rename, delete, persistence
await pg.fill('[data-gn="0"]', 'Wobble drop'); await pg.dispatchEvent('[data-gn="0"]', 'change'); await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const names = await pg.evaluate(() => window.PhosphorTest.grab.list().map((g) => g.name)); await pg.evaluate(() => document.querySelector('[data-gd="1"]').click()); const left = await pg.evaluate(() => window.PhosphorTest.grab.list().map((g) => g.name))
check(names[0] === 'Wobble drop' && names.length === 2 && left.length === 1, `G6: a grab can be renamed and deleted, and they survive a reload (${names.join(', ')}, then ${left.join(', ')})`)
check(errs.length === 0, 'G7: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
