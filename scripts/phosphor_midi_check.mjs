// phosphor_midi_check.mjs: MIDI in (opt-in). Synthetic messages through PhosphorTest.midi, no device needed. Usage: node scripts/phosphor_midi_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_midi_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch(), errs = []
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const midi = (a, b2, c) => pg.evaluate(([x, y, z]) => window.PhosphorTest.midi(x, y, z), [a, b2, c])
check(await pg.evaluate(() => !!document.getElementById('midib') && typeof window.PhosphorTest.midi === 'function'), 'M1: the MIDI button and the test hook exist')
// M2: a note-on presses the same key a keyboard would (counted on the document)
await pg.evaluate(() => { window.__k = []; document.addEventListener('keydown', (e) => window.__k.push('d' + e.code), true); document.addEventListener('keyup', (e) => window.__k.push('u' + e.code), true) })
await midi(0x90, 60, 100); await midi(0x80, 60, 0); const k = await pg.evaluate(() => window.__k)
check(k.length === 2 && k[0][0] === 'd' && k[1] === 'u' + k[0].slice(1), `M2: note-on is a key down, note-off a key up (${k.join(',')})`)
await midi(0x90, 61, 0); const k2 = await pg.evaluate(() => window.__k.slice(2))
check(k2.length === 1 && k2[0][0] === 'u', 'M3: note-on with velocity 0 counts as note-off')
// M4: touch a slider, then turn a knob: linked; later CC moves the slider across its range
const id = await pg.evaluate(() => { const r = document.querySelector('input[type=range][id]'); return r.id })
const box = await pg.locator('#' + id).boundingBox(); await pg.evaluate((i) => document.getElementById(i).scrollIntoView(), id)
await pg.evaluate((i) => document.getElementById(i).dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })), id)
await midi(0xB0, 21, 0); const lo = await pg.evaluate((i) => +document.getElementById(i).value, id)
await midi(0xB0, 21, 127); const hi = await pg.evaluate((i) => { const e = document.getElementById(i); return [+e.value, +e.max, +e.min] }, id)
check(hi[0] === hi[1] && lo === hi[2], `M4: CC 21 is linked to #${id}: 0 gives min (${lo}), 127 gives max (${hi[0]})`)
await midi(0xB0, 21, 64); const mid = await pg.evaluate((i) => +document.getElementById(i).value, id)
check(mid > hi[2] && mid < hi[1], `M5: a middle CC value lands between min and max (${mid})`)
await pg.evaluate(() => localStorage.getItem('phosphor.midi.v1')).then((v) => check(!!v && JSON.parse(v)['21'] === id, 'M6: the link is remembered locally'))
await midi(0xB0, 99, 50); check(true, 'M7: an unlinked CC is ignored without error')
await pg.evaluate(() => { Object.defineProperty(navigator, 'requestMIDIAccess', { value: undefined, configurable: true }); document.getElementById('midib').click() }); await pg.waitForTimeout(100)
check(await pg.evaluate(() => /Chrome or Edge/.test(document.getElementById('midih').textContent)), 'M8: with no Web MIDI the button says so')
check(errs.length === 0, 'M9: no page errors ' + errs.join('|'))
await b.close(); process.exit(bad ? 1 : 0)
