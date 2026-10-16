#!/usr/bin/env node
// phosphor_pins_check.mjs: N1 to N11 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 25 and its addendum, timeline pins).
// Needs a synthetic 100 BPM break whose first beat is at 0.37 s (scripts/beat_truth_tracks.py writes break-100.wav): PHOSPHOR_FILES=/path/break-100.wav
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_pins_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(page).href, errs = [], reqs = []
const open = async (blocked) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); pg.on('request', (r) => reqs.push(r.url())); if (blocked) await pg.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('blocked', 'SecurityError') } })); await pg.goto(base + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200); await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 }); return pg }
let pg = await open(false); const P = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.pins[fn](...a), [fn, a])
const bpm = await pg.evaluate(() => window.PhosphorTest.bpm()), P0 = 60 / bpm
// N1
await pg.evaluate(() => window.PhosphorTest.seek(5.1)); const pin = await P('add', 'the drop', 'note', false)
const g0 = await pg.evaluate(() => window.PhosphorTest.grid0()); const k = Math.round((pin.at - g0) / P0)
check(Math.abs(pin.at - (g0 + k * P0)) < 0.002 && /^sha256:[0-9a-f]{64}$/.test(pin.sha) && pin.id === pin.sha.slice(-8) && pin.fp && pin.dna.length >= 2 && pin.rna.length >= 2 && pin.settings && pin.note === 'the drop', `N1: a pin at 5.1 s lands on the beat (${pin.at}), carries a SHA-256 key ${pin.id}, the song fingerprint, ${pin.dna.length} DNA codons and the settings`)
check(await pg.evaluate(async () => { const ok = await window.PhosphorTest.pins.verify(0); return ok }), 'N1: the key recomputes to the same value')
// N2 note never changes the picture or sound; fire counter stays zero
await P('cues', true); await P('resetFired'); await pg.evaluate((at) => { window.PhosphorTest.seek(at - 1.2) }, pin.at); await pg.click('#play'); await pg.waitForTimeout(2600)
check((await P('fired')).length === 0, 'N2: a note never fires anything when playback crosses it')
// N3 cue
await pg.click('#play'); await pg.evaluate(() => window.PhosphorTest.pins.clear()); await pg.evaluate(() => window.PhosphorTest.seek(5.0))
await pg.evaluate(() => { const r = document.getElementById('res'); r.value = 4; r.dispatchEvent(new Event('input', { bubbles: true })) }); const cue = await P('add', 'back to grain', 'cue', false)
await pg.evaluate(() => { const r = document.getElementById('res'); r.value = 9; r.dispatchEvent(new Event('input', { bubbles: true })) })
const run = async (label, setup, ms) => { await P('resetFired'); await pg.evaluate((at) => window.PhosphorTest.seek(at - 0.8), cue.at); await setup(); await pg.click('#play'); await pg.waitForTimeout(ms); const n = (await P('fired')).length; await pg.click('#play'); return n }
await P('arm', 0, false); await P('cues', true); check((await run('disarmed', async () => {}, 2200)) === 0, 'N3: a cue that is not ticked does not fire')
await P('arm', 0, true); await P('cues', false); check((await run('cues off', async () => {}, 2200)) === 0, 'N3: with Cues armed off nothing fires')
await P('cues', true); const fires = await run('armed', async () => {}, 2400); check(fires === 1, `N3: an armed cue fires once as playback crosses it (${fires})`)
const resNow = await pg.evaluate(() => +document.getElementById('res').value); check(resNow === 4, `N4: the cue put the look back (rung ${resNow}, saved 4) and left the level, steps and tempo alone`)
check((await pg.evaluate(() => window.PhosphorTest.molt.level())) === 4 && (await pg.evaluate(() => window.PhosphorTest.bpm())) === bpm, 'N4: level and tempo are unchanged')
check(/back to grain/.test(await pg.evaluate(() => document.getElementById('toast').textContent)), 'N11: the cue caption shows the pin\'s comment')
// seek across a cue does not fire
await P('resetFired'); await pg.evaluate((at) => { window.PhosphorTest.seek(at - 3) }, cue.at); await pg.click('#play'); await pg.evaluate((at) => window.PhosphorTest.seek(at + 0.5), cue.at); await pg.waitForTimeout(600); const seekFire = (await P('fired')).length; await pg.click('#play')
check(seekFire === 0, 'N3: jumping over a cue with a seek does not fire it')
// edited pin does not fire
const okAfter = await P('tamper', 0, 'edited text'); check(okAfter === false, 'N3: editing a pin makes its key stop matching'); await P('resetFired'); await pg.evaluate((at) => window.PhosphorTest.seek(at - 0.8), cue.at); await pg.click('#play'); await pg.waitForTimeout(2200); check((await P('fired')).length === 0, 'N3: a pin whose key no longer matches does not fire'); await pg.click('#play')
// N6 marks and keyboard list
await P('clear'); await pg.evaluate(() => window.PhosphorTest.seek(10)); const m1 = await P('add', 'ten seconds', 'note', false)
const left = await pg.evaluate(() => parseFloat(document.querySelector('#pinbar .pinmark').style.left)); const dur = await pg.evaluate(() => window.PhosphorTest.dur())
check(Math.abs(left - m1.at / dur * 100) < 0.1, `N6: the mark sits at ${left}% for ${m1.at} s of ${dur.toFixed(1)} s`)
await pg.focus('#pinlist button[data-pg="0"]'); await pg.keyboard.press('Enter'); await pg.waitForTimeout(150); check(Math.abs((await pg.evaluate(() => window.PhosphorTest.tnow())) - m1.at) < 0.2, 'N6: the list reaches a pin from the keyboard (Go)')
// N5 export and import with storage blocked
const text = await P('export'); check(/^Phosphor pins v1/.test(text) && /^fingerprint: /m.test(text) && /^pin: \{/m.test(text) && !/[—–]/.test(text), 'N5: the export has a header, the fingerprint and one line per pin, with no em-dashes'); await pg.context().close()
pg = await open(true); const Q = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.pins[fn](...a), [fn, a])
await pg.evaluate((t) => window.PhosphorTest.pins.import(t), text); const got = await Q('list'); check(got.length === 1 && got[0].note === 'ten seconds' && (await Q('verify', 0)) === true, 'N5: with storage blocked the pins come back from pasted text and their key verifies')
const tampered = text.replace('ten seconds', 'ten seconds EDITED'); await pg.evaluate(() => window.PhosphorTest.pins.clear()); await pg.evaluate((t) => window.PhosphorTest.pins.import(t), tampered); const t2 = await Q('list')
check(t2.length === 1 && t2[0].ok === false && /edited/.test(await pg.evaluate(() => document.getElementById('pinmsg').textContent)), 'N5: an edited pin is kept, flagged, and cannot fire')
// N9 and N10 anchors on a track with known beats: first beat 0.37 s, 100 BPM
await pg.evaluate(() => window.PhosphorTest.pins.clear()); await pg.evaluate(() => window.PhosphorTest.tap.set(95, 0.9)); const wrong = await pg.evaluate(() => [window.PhosphorTest.bpm(), window.PhosphorTest.grid0()])
await pg.evaluate(() => window.PhosphorTest.seek(0.37)); await pg.evaluate(() => document.getElementById('pinanchor').click()); await Q('add', 'beat one', 'note', true)
await pg.evaluate(() => window.PhosphorTest.seek(14.77)); await Q('add', 'beat 25', 'note', true); const unchanged = await pg.evaluate(() => [window.PhosphorTest.bpm(), window.PhosphorTest.grid0()])
check(unchanged[0] === wrong[0] && Math.abs(unchanged[1] - wrong[1]) < 1e-6, 'N10: anchors do nothing until Use anchors is pressed')
await pg.evaluate(() => { const i = document.getElementById('pinbeats'); i.value = 24 })
const used = await Q('use'); const P1 = 60 / used.bpm, off = (((used.grid0 - 0.37) % P1) + P1) % P1, offm = Math.min(off, P1 - off) * 1000
check(Math.abs(used.bpm - 100) < 0.3 && offm < 5, `N9: with the beat count given (24), two anchors bring a 5 percent wrong tempo to ${used.bpm} (true 100) and the grid ${offm.toFixed(1)} ms from a true beat`)
await pg.evaluate(() => { window.PhosphorTest.tap.set(98, 0.9); document.getElementById('pinbeats').value = '' }); const est = await Q('use'); const P2 = 60 / est.bpm, off2 = (((est.grid0 - 0.37) % P2) + P2) % P2
check(Math.abs(est.bpm - 100) < 0.3 && Math.min(off2, P2 - off2) * 1000 < 5, `N9: with no count and a 2 percent wrong tempo the estimate still lands on ${est.bpm}`)
// N8
check(reqs.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')) && errs.length === 0, `N8: no network request and no console error ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
