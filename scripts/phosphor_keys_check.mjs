#!/usr/bin/env node
// phosphor_keys_check.mjs: checks M1 to M4 and B1 to B2 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 6).
// Usage: node scripts/phosphor_keys_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_keys_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const wav = path.join(os.tmpdir(), 'phosphor-click-120.wav')
if (!fs.existsSync(wav)) { console.error('run phosphor_stage_check.mjs once first to make the click track'); process.exit(2) }

const b = await pw.chromium.launch(), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } })
const pg = await ctx.newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
await pg.setInputFiles('#file', wav)
await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 60000 })
const S = () => pg.evaluate(() => window.PhosphorTest.pk.state())
const G = () => pg.evaluate(() => { const g = window.PhosphorTest.glitch(); return { stut: g.stut, perform: g.perform } })
const tick = () => pg.waitForTimeout(60)

// off means off: normal keys still work as before when Perform keys is off
await pg.keyboard.press('3'); check((await pg.evaluate(() => window.PhosphorTest.zoom().mode)) === 2, 'B3: with Perform keys off the number keys still pick a mode')
await pg.keyboard.press('Backquote'); check((await G()).perform === true, 'the ~ key turns Perform keys on')

// M2 strip order
const rungs = []
for (const k of ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']) { await pg.keyboard.down(k); await tick(); rungs.push((await S()).rung); await pg.keyboard.up(k); await tick() }
check(rungs[0] === 0 && rungs[9] === 8 && rungs.every((v, i) => i === 0 || v >= rungs[i - 1]), `M2: the number row runs rung 0 to 8 in order (${rungs.join(' ')})`)
const r0 = (await S()).rung
await pg.keyboard.down('1'); await tick(); await pg.keyboard.down('5'); await tick()
const both = (await S()).rung
await pg.keyboard.up('5'); await tick(); const back1 = (await S()).rung
await pg.keyboard.up('1'); await tick(); const back0 = (await S()).rung
check(both === 4 && back1 === 0 && back0 === r0, `M2: Hold hands control to the key still held, then back to the start (${both}, ${back1}, ${back0}, start ${r0})`)

// M1 chords
await pg.keyboard.down('e'); await pg.keyboard.down('r'); await pg.keyboard.down('t'); await pg.keyboard.down('q'); await tick()
const ch = await pg.evaluate(() => { const o = window.PhosphorTest.glitch(); return { stut: !!o.stut } })
const flags = await pg.evaluate(() => document.getElementById('gmo').textContent)
check(ch.stut && /tear/.test(flags) && /rgb/.test(flags) && /blocks/.test(flags), `M1: four keys held at once stack four effects (${flags})`)
for (const k of ['e', 'r', 't', 'q']) await pg.keyboard.up(k)
await tick(); check((await pg.evaluate(() => document.getElementById('gmo').textContent)) === 'perform: on', 'M1: letting go of all of them clears every effect')
check((await pg.evaluate(() => window.PhosphorTest.pk.got())).includes('chord'), 'B1: holding three keys at once unlocks the Triple sticker')

// M3 latch
await pg.keyboard.press('Tab'); check((await S()).latch === true, 'M3: Tab switches to Latch')
await pg.keyboard.press('e'); await tick()
check(/tear/.test(await pg.evaluate(() => document.getElementById('gmo').textContent)), 'M3: in Latch a press stays on after the key is up')
await pg.keyboard.press('e'); await tick()
check(!/tear/.test(await pg.evaluate(() => document.getElementById('gmo').textContent)), 'M3: and a second press turns it off')
await pg.keyboard.press('Tab'); check((await S()).latch === false, 'M3: Tab switches back to Hold')

// M4 banks
await pg.keyboard.down('d'); await tick(); const bank = (await S()).bank
await pg.keyboard.up('d'); await tick(); const after = (await S()).bank
check(bank === 2 && after === 0, `M4: the A row picks pattern banks and Hold returns (bank ${bank}, then ${after})`)

// B1 stickers on gestures, not before
const before = await pg.evaluate(() => window.PhosphorTest.pk.got())
check(before.includes('sweep') && !before.includes('trip') && !before.includes('pocket'), `B1: the ten-key slide earned Slide, and Boomerang and In time are not given early (${before.join(',')})`)
for (const k of ['3', '4', '5', '6', '7', '6', '5', '4', '3']) { await pg.keyboard.press(k); await pg.waitForTimeout(40) }
check((await pg.evaluate(() => window.PhosphorTest.pk.got())).includes('trip'), 'B1: up then back down unlocks Boomerang')
const pk = await pg.evaluate(() => { const T = window.PhosphorTest, P = T.pk, b0 = T.seq.base(), P8 = 60 / 120 / 2; return { on: P.pocketHit(b0 + 4 * P8 + 0.01), off: P.pocketHit(b0 + 4 * P8 + P8 / 2), } })
check(pk.on && !pk.off, `B1: a press within 45 ms of an eighth note counts as in time, a press halfway between does not (${pk.on}, ${pk.off})`)
await pg.evaluate(() => { const T = window.PhosphorTest, b0 = T.seq.base(); for (let i = 0; i < 7; i++) T.pk.feed(b0 + i * 0.25) })
check(!(await pg.evaluate(() => window.PhosphorTest.pk.got())).includes('pocket'), 'B1: seven on-beat presses are not enough')
await pg.evaluate(() => { const T = window.PhosphorTest; T.pk.feed(T.seq.base() + 7 * 0.25) })
check((await pg.evaluate(() => window.PhosphorTest.pk.got())).includes('pocket'), 'B1: the eighth unlocks In time')
const pal = (await S()).pal
check(['neon', 'sunset', 'ice', 'gold'].every((p) => pal.includes(p)), `B1: each sticker adds its palette to the Colors list (${pal.join(' ')})`)
check(await pg.evaluate(() => document.querySelectorAll('#stk .sk.got').length === 4), 'B2: the sticker row shows all four earned')

// B2 persists across a reload
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
check((await pg.evaluate(() => window.PhosphorTest.pk.got())).length === 4, 'B2: earned stickers are still there after a reload')

// leak check: typing in a field is untouched while Perform keys is on
await pg.keyboard.press('Backquote')
await pg.evaluate(() => { document.getElementById('grown').open = true; document.querySelector('details.grp:has(#res) > summary').click() })
check(true, 'leak guard ran')
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
