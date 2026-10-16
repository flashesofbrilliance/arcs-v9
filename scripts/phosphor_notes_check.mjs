#!/usr/bin/env node
// phosphor_notes_check.mjs: N1 to N7 and N9 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 11). N8 (flash rate while mashing the strip) lives in phosphor_guard_check.mjs.
// Usage: node scripts/phosphor_notes_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_notes_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const E = (f, ...a) => pg.evaluate(f, ...a)
const peak = async (n = 14) => { let m = 0; for (let i = 0; i < n; i++) { m = Math.max(m, await E(() => window.PhosphorTest.outPeak())); await pg.waitForTimeout(40) } return m }

// N5 off means unchanged
await pg.keyboard.press('3'); check((await E(() => window.PhosphorTest.zoom().mode)) === 2, 'N5: with Notes off the number key 3 still picks a mode')
// N1 toggle
check(await E(() => document.getElementById('nkeys').hidden), 'N1: the twelve keys are hidden until Notes is on')
await pg.click('#notesb')
check(await E(() => !document.getElementById('nkeys').hidden && document.querySelectorAll('#nkeys .nk').length === 12), 'N1: Notes shows twelve keys')
// N2 pentatonic
const f = await E(() => { const T = window.PhosphorTest.notes; return Array.from({ length: 12 }, (_, i) => T.freq(i)) })
const octOk = [0, 1, 2, 3, 4, 5, 6].every((i) => Math.abs(f[i + 5] / f[i] - 2) < 1e-9)
const semis = f.slice(0, 5).map((v) => Math.round(12 * Math.log2(v / f[0])))
check(octOk && semis.join() === '0,2,4,7,9', `N2: pentatonic, and key i+5 is exactly an octave above key i (semitones ${semis.join(' ')}; C4 ${f[0].toFixed(2)} Hz, D6 ${f[11].toFixed(2)} Hz)`)
// N3 sound
await pg.keyboard.down('1'); const held = await peak(); await pg.keyboard.up('1'); await pg.waitForTimeout(1000); const after = await peak()
check(held > 0.01 && held <= 0.5 && after < 0.01, `N3: holding 1 makes sound under the 0.5 ceiling and it dies after release (held ${held.toFixed(3)}, after ${after.toFixed(4)})`)
// N7 mirror
await pg.keyboard.down('5'); await pg.waitForTimeout(300)
check(await E(() => window.PhosphorTest.notes.mirror()), 'N7: with no song the picture mirrors the sound'); await pg.keyboard.up('5')
// N4 cap
for (const k of ['1', '2', '3', '4', '5', '6']) await pg.keyboard.down(k)
const v6 = await E(() => window.PhosphorTest.notes.voices())
for (const k of ['1', '2', '3', '4', '5', '6']) await pg.keyboard.up(k)
await pg.waitForTimeout(500)
check(v6 === 4 && (await E(() => window.PhosphorTest.notes.voices())) === 0, `N4: six keys at once play at most four voices (${v6}) and every voice is released afterwards`)
// N4b = minus and equals
await pg.keyboard.down('-'); await pg.keyboard.down('='); const v2 = await E(() => window.PhosphorTest.notes.voices()); await pg.keyboard.up('-'); await pg.keyboard.up('=')
check(v2 === 2, `N2: the minus and equals keys are the last two notes (${v2} voices)`)
// N6 pointer
await E(() => { const i = document.querySelector('.inst').getBoundingClientRect(); window.scrollTo(0, i.bottom + window.scrollY - innerHeight + 4) }); await pg.waitForTimeout(250)
const box = await pg.locator('#nkeys .nk').nth(7).boundingBox()
await pg.mouse.move(box.x + box.width / 2, box.y + box.height / 2); await pg.mouse.down(); await pg.waitForTimeout(150)
const hit = await E(() => { const r = document.querySelectorAll('#nkeys .nk')[7].getBoundingClientRect(), el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return el && !!el.closest('#nkeys') })
const vp = await E(() => window.PhosphorTest.notes.voices()); await pg.mouse.up(); await pg.waitForTimeout(400)
check(hit && vp === 1 && (await E(() => window.PhosphorTest.notes.voices())) === 0, `N6: an on-screen key plays by pointer and releases (${vp} voice)`)
// toggle off releases and restores behavior
await pg.keyboard.down('2'); await pg.click('#notesb'); await pg.waitForTimeout(100)
check((await E(() => window.PhosphorTest.notes.voices())) === 0 && (await E(() => document.getElementById('nkeys').hidden)), 'N1: turning Notes off stops every voice and hides the keys'); await pg.keyboard.up('2')
check(reqs.length === 0, `N9: no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
