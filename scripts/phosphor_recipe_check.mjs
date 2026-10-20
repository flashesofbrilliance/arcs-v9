#!/usr/bin/env node
// phosphor_recipe_check.mjs: the recipe log (amendment 55). Every control change is an event; replaying the events reproduces the controls at any moment, whatever changed them. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_recipe_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_recipe_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
const R = (fn, ...a) => pg.evaluate(([fn, a]) => { const r = window.PhosphorTest.recipe[fn](...a); return r }, [fn, a])
const eq0 = 0; const eq = (a, b2) => { const ks = new Set([...Object.keys(a), ...Object.keys(b2)]); const d = []; for (const k of ks) if (a[k] !== b2[k]) d.push(k + ':' + a[k] + '/' + b2[k]); return d }
// R1 each move of one slider is its own event, in order (no coalescing)
const e0 = (await R('ev')).length
for (const v of [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) await pg.evaluate((v) => { const e = document.getElementById('gamt'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) }, v)
const ev1 = (await R('ev')).slice(e0).filter((e) => e[2] === 'gamt')
check(ev1.length === 10 && ev1.map((e) => e[3]).join() === '10,20,30,40,50,60,70,80,90,100', `R1: ten moves of one slider are ten events in order (${ev1.length})`)
// R2 media time is recorded while playing and null while stopped
await pg.click('#play'); await pg.waitForTimeout(600); await pg.evaluate(() => { const e = document.getElementById('amt') || document.getElementById('gamt'); e.value = 33; e.dispatchEvent(new Event('input', { bubbles: true })) }); const last = (await R('ev')).slice(-1)[0]; await pg.click('#play')
check(typeof last[1] === 'number' && last[1] > 0 && ev1[0][1] === null, `R2: an event made while playing carries the song time (${last[1]} s), one made while stopped carries none`)
// R3 replay equals the controls at sampled moments, with changes from a mix of sources
const rnd = (() => { let s = 12345; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296 })()
const ids = await pg.evaluate(() => [...document.querySelectorAll('input[type=range][id]')].filter((e) => !e.closest('#fxtray .fxl') && e.id.indexOf('mh_') && e.id.indexOf('ml_') && e.id !== 'scrub' && e.id !== 'zpan').map((e) => e.id))
const samples = []
for (let round = 0; round < 6; round++) {
  for (let k = 0; k < 8; k++) { const id = ids[Math.floor(rnd() * ids.length)]; await pg.evaluate(([id, f]) => { const e = document.getElementById(id); const lo = +e.min || 0, hi = +e.max || 100; e.value = lo + f * (hi - lo); e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, rnd()]) }
  if (round === 1) await pg.evaluate(() => document.querySelector('[data-gp=tv]').click())          // a preset
  if (round === 2) await pg.evaluate(() => window.PhosphorTest.midi(0xB0, 7, 99))                    // MIDI (needs a link, harmless if none)
  if (round === 3) await pg.evaluate(() => { const r = document.querySelector('input[name=fxg][value=beat]'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) })
  if (round === 4) await pg.evaluate(() => { const e = document.getElementById('perf'); e.checked = !e.checked; e.dispatchEvent(new Event('change', { bubbles: true })) })
  await pg.waitForTimeout(350)
  samples.push(await pg.evaluate(() => ({ t: window.PhosphorTest.recipe.now(), dom: window.PhosphorTest.recipe.scan() })))
}
let worst = []; for (const sm of samples) { const d = eq(await R('state', sm.t), sm.dom); if (d.length > worst.length) worst = d }
check(worst.length === 0, `R3: replaying the events to each of ${samples.length} sampled moments reproduces every control exactly (worst mismatch ${worst.length} ${worst.slice(0, 3).join(' ')})`)
// R4 a change made by code alone (no input event) is caught by the reconcile, not by an event
const before = await pg.evaluate(() => { const e = document.getElementById('fxdep'); e.value = 12; return window.PhosphorTest.recipe.state(1e12).fxdep })
const n0 = (await R('ev')).length; await pg.waitForTimeout(500); if (process.env.RC_DEBUG) console.log('events during wait', (await R('ev')).slice(n0).map((e) => e[2]).join(',')); const st = await R('state', 1e12), live = await R('scan')
check(before !== 12 && st.fxdep === 12 && eq(st, live).length === 0, `R4: a value set by code with no event is not in the recipe at once (${before}) and is there within half a second (${st.fxdep}), and the whole recipe equals the page`)
// R4b with the event path switched off (the page's input and change listeners for the recipe are dropped), the 200 ms reconcile alone still catches a code-made change
const ctx2 = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx2.addInitScript(() => { const orig = EventTarget.prototype.addEventListener; EventTarget.prototype.addEventListener = function (t, f, o) { if (f && f.name === 'recSync' && (t === 'input' || t === 'change')) return; return orig.call(this, t, f, o) } })
const pg2 = await ctx2.newPage(); pg2.on('pageerror', (e) => errs.push(String(e))); await pg2.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg2.waitForTimeout(1500)
const r2 = await pg2.evaluate(async () => { const e = document.getElementById('fxdep'); e.value = 12; const at = window.PhosphorTest.recipe.state(1e12).fxdep; await new Promise((r) => setTimeout(r, 600)); return { at, later: window.PhosphorTest.recipe.state(1e12).fxdep } })
check(r2.at !== 12 && r2.later === 12, `R4b: with the event listeners dropped the reconcile alone captures a code-made change (${r2.at} at once, ${r2.later} after 0.6 s)`)
await ctx2.close()
// R5 memory only, no text
const keys = await pg.evaluate(() => Object.keys(localStorage)); const dump = JSON.stringify(await R('ev'))
check(!keys.some((k) => /rec/i.test(k)) && !/lullaby|secret/i.test(dump), 'R5: nothing from the recipe log is written to storage')
// R7 to R11: actions
const acts = async () => (await R('ev')).filter((e) => e[2][0] === '@')
const a0 = (await acts()).length
await pg.evaluate(() => { document.getElementById('dkpad').click() }); await pg.evaluate(() => document.querySelector('[data-pk="3"]').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true }))); await pg.keyboard.press('KeyE'); await pg.evaluate(() => { document.getElementById('dkpad').click(); const p = document.getElementById('perf'); if (!p.checked) { p.checked = true; p.dispatchEvent(new Event('change', { bubbles: true })) } }); await pg.keyboard.press('Digit5')
await pg.evaluate(() => window.PhosphorTest.seek(2.5)); await pg.evaluate(() => window.PhosphorTest.tap.set(97, 0.2))
const na = (await acts()).slice(a0), names = na.map((e) => e[2])
check(names.includes('@pad') && names.includes('@key') && names.includes('@seek') && names.includes('@tempo') && na.filter((e) => e[2] === '@pad').map((e) => e[3]).join() === '0:3,0:6' && na.find((e) => e[2] === '@tempo')[3][0] === 97, `R7: pads (a tap and a key), a Perform key, seek and tempo are recorded as actions in order (${names.join(' ')})`)
await pg.click('#play'); await pg.waitForTimeout(300); await pg.click('#play'); const pl = (await acts()).map((e) => e[2])
check(pl.includes('@play') && pl.includes('@stop'), 'R8: play and stop are recorded')
const songs = (await acts()).filter((e) => e[2] === '@song')
check(songs.length >= 1 && /^[0-9a-f]{8}\|\d+$/.test(songs[songs.length - 1][3]), `R9: the loaded song is recorded as a content fingerprint and length only (${songs.length && songs[songs.length - 1][3]})`)
const st1 = await R('state', 1e12); const txt = await pg.evaluate(() => window.PhosphorTest.recipe.exp()); const back = await pg.evaluate((t) => window.PhosphorTest.recipe.imp(t), txt)
check(/^Phosphor recipe v1\n/.test(txt) && back && back.events.length === (await R('ev')).length && JSON.stringify(back.base) === JSON.stringify(await pg.evaluate(() => window.PhosphorTest.recipe.exp().length ? JSON.parse(window.PhosphorTest.recipe.exp().split('\n').slice(1).join('\n')).base : null)) && !/lullaby|secret|\.wav/i.test(txt), `R10: the recipe exports to text and reads back with every event (${back && back.events.length}), and the text holds no file name`)
const bad = await pg.evaluate(() => [window.PhosphorTest.recipe.imp(''), window.PhosphorTest.recipe.imp('nope'), window.PhosphorTest.recipe.imp('Phosphor recipe v1\n{"base":1}'), window.PhosphorTest.recipe.imp('Phosphor recipe v1\n{"base":{},"events":[["x"]]}')])
check(bad.every((x) => x === null), 'R11: text that is not a recipe, or has malformed events, is refused (nothing is applied)')
check(errs.length === 0, 'R6: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
