#!/usr/bin/env node
// phosphor_mix_check.mjs: the effect tray, per-effect level held between min and max limits (amendment 38). Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_mix_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_mix_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href, errs = []
const open = async () => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); await pg.click('#play'); await pg.waitForTimeout(500); return pg }
const parent = (pg) => pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))).then(() => pg.waitForTimeout(1700))
const set = (pg, id, v) => pg.evaluate(([i, x]) => { const e = document.getElementById(i); e.value = x; e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
const mix = (pg, k) => pg.evaluate((k) => window.PhosphorTest.fxl(k), k)
const hold = (pg, k, on) => pg.evaluate(([k, on]) => window.PhosphorTest.hold.on(k, 'latch', on), [k, on])
let pg = await open()
// T1 Kid mode hides Mix; Parent shows it, opens the tray with nine rows
await pg.evaluate(() => document.getElementById("mdKid").click()); await pg.waitForTimeout(300)
const kidHidden = await pg.evaluate(() => getComputedStyle(document.getElementById('dkfx')).display === 'none')
await parent(pg); await pg.click('#dkfx'); await pg.waitForTimeout(200)
const rows = await pg.locator('#fxtray .fxr').count(), vis = await pg.locator('#fxtray').isVisible()
check(kidHidden && vis && rows === 9 && await pg.getAttribute('#dkfx', 'aria-expanded') === 'true', `T1: Mix is hidden in Kid mode, opens a tray of ${rows} effect rows in Parent mode`)
// T2 level scales Echo's send
await hold(pg, 'echo', true); await pg.waitForTimeout(500); const full = await mix(pg, 'echo')
await set(pg, 'mv_echo', 50); await pg.waitForTimeout(500); const half = await mix(pg, 'echo')
check(Math.abs(full.g - 0.7) < 0.03 && Math.abs(half.g - 0.35) < 0.03, `T2: Echo send follows its level (${full.g.toFixed(2)} at 100, ${half.g.toFixed(2)} at 50)`)
// T3 limits: max 40 clamps the level and the slider; min 20 raises the floor
await set(pg, 'mh_echo', 40); await pg.waitForTimeout(500); const cap = await mix(pg, 'echo'), mx = await pg.evaluate(() => document.getElementById('mv_echo').max)
check(cap.e <= 0.4001 && Math.abs(cap.g - 0.28) < 0.03 && mx === '40', `T3: max 40 caps the level at ${cap.e} (send ${cap.g.toFixed(2)}) and the slider stops at ${mx}`)
await set(pg, 'ml_echo', 20); await set(pg, 'mv_echo', 0); const floor = await mix(pg, 'echo')
check(Math.abs(floor.e - 0.2) < 0.001, `T3b: min 20 holds the level at ${floor.e} even when the slider is pulled to 0`)
await set(pg, 'ml_echo', 60); const cross = await pg.evaluate(() => [document.getElementById('ml_echo').value, document.getElementById('mh_echo').value])
check(+cross[0] <= +cross[1], `T3c: min can not cross max (min ${cross[0]}, max ${cross[1]})`)
await hold(pg, 'echo', false)
// T4 presets obey the limits: Echo max 0 silences Space echo's echo
await set(pg, 'ml_echo', 0); await set(pg, 'mh_echo', 0)
await pg.evaluate(() => { let e = document.getElementById('gpre'); while (e) { if (e.tagName === 'DETAILS') e.open = true; e = e.parentElement } })
await pg.evaluate(() => document.querySelector('[data-gp=space]').click()); await pg.waitForTimeout(500); const sp = await mix(pg, 'echo'), sh = await mix(pg, 'shim')
check(sp.g < 0.02 && sh.g > 0.5, `T4: with Echo capped at 0 the Space echo preset starts no echo (${sp.g.toFixed(3)}) but still plays Shimmer (${sh.g.toFixed(2)})`)
await pg.evaluate(() => document.querySelector('[data-gp=clean]').click())
// T5 MIDI stays inside the limits: touch the level slider, turn a knob to max and min
await set(pg, 'mh_room', 70); await set(pg, 'ml_room', 30)
await pg.evaluate(() => document.getElementById('mv_room').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })))
await pg.evaluate(() => window.PhosphorTest.midi(0xB0, 30, 127)); const top = await mix(pg, 'room'); await pg.evaluate(() => window.PhosphorTest.midi(0xB0, 30, 0)); const bot = await mix(pg, 'room')
check(Math.abs(top.e - 0.7) < 0.011 && Math.abs(bot.e - 0.3) < 0.011, `T5: a MIDI knob sweeps only between the limits (${bot.e} to ${top.e})`)
// T6 Crush wet follows its level; Sweep cutoff moves with its level
await hold(pg, 'crush', true); await set(pg, 'mv_crush', 40); await pg.waitForTimeout(500); const cr = await mix(pg, 'crush'); await hold(pg, 'crush', false)
check(Math.abs(cr.g - 0.4) < 0.05, `T6: Crush wet follows its level (${cr.g.toFixed(2)} at 40)`)
await hold(pg, 'sweep', true); await set(pg, 'mv_sweep', 100); await pg.waitForTimeout(2500); const sw1 = await mix(pg, 'sweep'); await set(pg, 'mv_sweep', 20); await pg.waitForTimeout(2500); const sw2 = await mix(pg, 'sweep'); await hold(pg, 'sweep', false)
check(sw1.g < 600 && sw2.g > 3 * sw1.g, `T6b: Sweep closes the filter less at a lower level (${Math.round(sw1.g)} Hz at 100, ${Math.round(sw2.g)} Hz at 20)`)
// T7 remembered: limits survive a reload
await set(pg, 'mh_dist', 55); await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); const re = await pg.evaluate(() => document.getElementById('mh_dist').value)
check(re === '55', `T7: the limits are remembered after a reload (Distort max ${re})`)
// T8 picture: at a fixed playhead, Tear at level 0 draws a different frame than Tear at 100, and the same level draws the same frame twice
await pg.context().close(); pg = await open(); await parent(pg)
await pg.evaluate(() => { const e = document.getElementById('gs2'); e.checked = true; e.dispatchEvent(new Event('change', { bubbles: true })) })
await pg.click('#play'); await pg.waitForTimeout(300)
await hold(pg, 'tear', true); await hold(pg, 'rgb', true); await hold(pg, 'blocks', true)
for (const k of ['rgb', 'blocks']) await set(pg, 'mh_' + k, 0)
const shot = async () => { await pg.evaluate(() => window.PhosphorTest.seek(2.0)); await pg.waitForTimeout(250); return pg.evaluate(() => { const c = document.querySelector('.frame canvas'); return Array.from(c.getContext('2d').getImageData(0, 0, c.width, c.height).data.filter((_, i) => i % 16 === 0)) }) }
const diff = (a, b2) => { let n = 0; for (let i = 0; i < a.length; i++) if (Math.abs(a[i] - b2[i]) > 24) n++; return n / a.length }
await set(pg, 'mh_tear', 0); const A = await shot(), A2 = await shot(); await set(pg, 'mh_tear', 100); const B = await shot()
check(diff(A, A2) < 0.001 && diff(A, B) > 0.003, `T8: at a fixed playhead the same level draws the same frame (${diff(A, A2).toFixed(4)}) and Tear 0 against Tear 100 differ (${diff(A, B).toFixed(4)})`)
check(errs.length === 0, 'T9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
