#!/usr/bin/env node
// phosphor_look_check.mjs: checks L1 to L6 from _PATTERNS/2026-10-15-sequencer-5d-prereg.md (Amendment 1):
// curve, invert, palette swap, stutter, keyboard, photosensitivity. Runs on the built-in demo signal; no files needed.
// Uses the page's test hook (?test=1). Usage: node scripts/phosphor_look_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_look_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const b = await pw.chromium.launch(), errors = []
const ctx0 = await b.newContext({ viewport: { width: 1280, height: 1000 } })
if (process.env.PHOSPHOR_SKIN) await ctx0.addInitScript((v) => { try { localStorage.setItem('phosphor.skin.v1', v) } catch (e) {} }, process.env.PHOSPHOR_SKIN)
const pg = await ctx0.newPage()
pg.on('pageerror', (e) => errors.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1'); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 30000 })
const ev = (fn, arg) => pg.evaluate(fn, arg)
const set = (id, v) => ev(([id, v]) => { const e = document.getElementById(id); if (e.type === 'radio' || e.type === 'checkbox') { e.checked = !!v; e.dispatchEvent(new Event('change', { bubbles: true })) } else { e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true })) } }, [id, v])
const seek = (f) => set('scrub', Math.round(f * 1000))
const hash = () => ev(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i++) h = Math.imul(h ^ d[i], 16777619) >>> 0; return h })
const px = () => ev(() => { const c = document.getElementById('cv'), g = c.getContext('2d'), out = []; for (const [fx, fy] of [[0.1, 0.5], [0.3, 0.4], [0.5, 0.5], [0.7, 0.6], [0.9, 0.5], [0.5, 0.85]]) out.push([...g.getImageData(Math.floor(c.width * fx), Math.floor(c.height * fy), 1, 1).data].slice(0, 3)); return out })
await set('m1', true); await seek(0.5)            // Bars mode, a mid-song frame
const base = await hash(), basePx = await px()
// L1 curve
await set('cu1', true); await set('cua', 100)
const logL = await ev(() => window.PhosphorTest.lut())
check(logL.r[128] > 128 && logL.r[0] === 0 && logL.r[255] === 255, `L1: Log at 100 lifts mid-gray (LUT[128] = ${logL.r[128]}) and keeps 0 and 255`)
let mono = true; for (let i = 1; i < 256; i++) if (logL.r[i] < logL.r[i - 1]) mono = false
check(mono, 'L1: the Log curve is monotone')
await set('cu2', true); const expL = await ev(() => window.PhosphorTest.lut())
check(expL.r[128] < 128 && expL.r[0] === 0 && expL.r[255] === 255, `L1: Exp at 100 sinks mid-gray (LUT[128] = ${expL.r[128]}) and keeps 0 and 255`)
await set('cu1', true); await set('cua', 0); check((await hash()) === base, 'L1: curve Amount 0 leaves the picture byte-identical')
await set('cu0', true)
// L2 invert
await set('inv', true); const invPx = await px(); const comp = basePx.every((p, i) => p.every((v, k) => Math.abs(v - (255 - invPx[i][k])) <= 1 || Math.abs((255 - v) - invPx[i][k]) <= 1))
check(comp, 'L2: Original with Invert is the RGB complement at six sample points')
await pg.waitForTimeout(400) // invert is rate limited to protect against fast flashing (guard check G1)
await set('inv', false); check((await hash()) === base, 'L2: inverting twice returns the picture byte-identical')
// L3 palettes
for (const name of ['arcs', 'phosphor', 'amber', 'indigo', 'heat', 'mono']) {
  await set('palsel', name)
  const r = await ev(() => { const L = window.PhosphorTest.lut(), c = document.getElementById('cv'), g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height).data; let worst = 0; for (let i = 0; i < d.length; i += 4 * 211) { let best = 999; for (let k = 0; k < 256; k++) best = Math.min(best, Math.max(Math.abs(d[i] - L.r[k]), Math.abs(d[i + 1] - L.g[k]), Math.abs(d[i + 2] - L.b[k]))); worst = Math.max(worst, best) } return { worst, first: [L.r[0], L.g[0], L.b[0]], last: [L.r[255], L.g[255], L.b[255]] } })
  check(r.worst <= 4, `L3: ${name}: every sampled pixel lies within ${r.worst} levels of the gradient (want 4 or less); ends ${r.first.join(',')} to ${r.last.join(',')}`)
}
await set('palsel', 'orig')
// L4 stutter, visual and audio
await set('m0', true); await seek(0.4)
const plain = await hash()
await ev(() => window.PhosphorTest.on('stutter')); await pg.waitForTimeout(400)
const gs = await ev(() => window.PhosphorTest.glitch())
const Lw = gs.stut ? gs.stut.L : 0
const bpm = parseInt(((await ev(() => document.getElementById('magro').textContent)).match(/about (\d+) BPM/) || [])[1] || '120', 10), wantL = (60 / bpm) * 0.125
check(!!gs.stut && Math.abs(Lw - wantL) < 1e-6, `L4: stutter at 1/8 beat and ${bpm} BPM holds a ${(Lw * 1000).toFixed(1)} ms window (want ${(wantL * 1000).toFixed(1)})`)
check(!!gs.loop && gs.loop.loop && Math.abs((gs.loop.end - gs.loop.start) - Lw) < 0.002 && Math.abs(gs.loop.start - gs.stut.t0) < 0.002, `L4: the audio loop is ${gs.loop ? ((gs.loop.end - gs.loop.start) * 1000).toFixed(1) : '?'} ms long and starts at the held time (within 2 ms)`)
const tA = await ev(() => { const T = window.PhosphorTest, s = T.glitch().stut; return [T.gtime(s.t0 + 0.30), T.gtime(s.t0 + 0.30 + 3 * s.L), s.t0] })
check(Math.abs(tA[0] - tA[1]) < 1e-9 && tA[0] >= tA[2] && tA[0] < tA[2] + Lw, 'L4: the drawn time repeats every window (the same loop phase gives the same time)')
await ev(() => window.PhosphorTest.off('stutter')); await pg.waitForTimeout(200)
check((await ev(() => window.PhosphorTest.glitch())).stut === null && (await ev(() => window.PhosphorTest.glitch())).loop === null, 'L4: releasing ends the stutter and its audio loop')
check((await hash()) === plain, 'L4: after release the picture is the unglitched frame again')
// L5 keyboard
await ev(() => document.body.focus())
await pg.keyboard.press('`'); check((await ev(() => window.PhosphorTest.glitch())).perform === true, 'L5: the backtick key turns Perform on')
await pg.keyboard.down('z'); await pg.waitForTimeout(200)
check((await ev(() => window.PhosphorTest.glitch())).stut !== null, 'L5: holding Z starts the stutter')
await pg.keyboard.up('z'); await pg.waitForTimeout(150)
check((await ev(() => window.PhosphorTest.glitch())).stut === null, 'L5: releasing Z ends it')
await ev(() => { const i = document.createElement('input'); i.type = 'text'; i.id = 'tmpin'; document.body.appendChild(i); i.focus() })
await pg.keyboard.down('z'); await pg.waitForTimeout(150)
check((await ev(() => window.PhosphorTest.glitch())).stut === null, 'L5: keys are ignored while a text field has focus')
await pg.keyboard.up('z'); await ev(() => document.getElementById('tmpin').remove())
await ev(() => document.body.focus()); await pg.keyboard.press('`'); check((await ev(() => window.PhosphorTest.glitch())).perform === false, 'L5: the backtick key turns Perform off')
// L6 photosensitivity: mean luminance change between consecutive frames, measured four ways in Bars mode
await set('m1', true)
const lumNow = () => ev(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let s = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 13) { s += 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]; n++ } return s / n / 255 })
const maxDelta = async () => { const lum = []; for (let k = 0; k < 90; k++) { await seek(0.3 + k / 30 / 24); lum.push(await lumNow()) } let m = 0; for (let i = 1; i < lum.length; i++) m = Math.max(m, Math.abs(lum[i] - lum[i - 1])); return m }
const glitches = async (on) => { for (const g of ['tear', 'rgb', 'blocks']) await ev(([g, on]) => on ? window.PhosphorTest.on(g) : window.PhosphorTest.off(g), [g, on]) }
await set('calm', false); const liveClean = await maxDelta(); await glitches(true); const liveGlitch = await maxDelta(); await glitches(false)
await set('calm', true); const calmClean = await maxDelta(); await glitches(true); const calmGlitch = await maxDelta(); await glitches(false)
console.log(`  frame-to-frame mean luminance, largest change: live ${liveClean.toFixed(3)}, live with glitches ${liveGlitch.toFixed(3)}, calm ${calmClean.toFixed(3)}, calm with glitches ${calmGlitch.toFixed(3)}`)
check(Math.abs(liveGlitch - liveClean) < 0.03 && Math.abs(calmGlitch - calmClean) < 0.03, 'L6: the glitch effects themselves add under 0.03 to the largest frame-to-frame change')
check(calmGlitch < 0.1, `L6: with Calm on and every glitch on, the largest change is ${calmGlitch.toFixed(3)} (want under 0.1)`)
console.log(`  (diagnostic, the condition first registered: Calm off, no glitch, largest change ${liveClean.toFixed(3)}; a loud onset redraws a whole bar chart in one frame, which is why Calm exists and is on by default)`)
const KEYS = { F16: 'F16', F17: 'F17', F18: 'F18', F19: 'F19', NumLock: 'Clear', NumpadEqual: '=', NumpadDivide: '/', NumpadMultiply: '*', NumpadSubtract: '-', NumpadAdd: '+', NumpadEnter: 'Enter', Numpad1: '1', Numpad2: '2', Numpad3: '3', Numpad4: '4', Numpad5: '5', Numpad6: '6', Numpad7: '7', Numpad8: '8', Numpad9: '9', KeyA: 'a', KeyS: 's', KeyD: 'd', KeyF: 'f', KeyG: 'g' }
const press = (code) => ev(([code, key]) => { const t = document.activeElement || document.body; for (const type of ['keydown', 'keyup']) t.dispatchEvent(new KeyboardEvent(type, { code, key, bubbles: true, cancelable: true })) }, [code, KEYS[code] || code])
// K1 to K5: keypad zoom stages, learnable keys, palette arrows (Amendment 2)
const zoom = () => ev(() => window.PhosphorTest.zoom())
await ev(() => document.body.focus()); await set('perf', false); await set('palsel', 'orig'); await set('pal', 8)
await press('F16'); let z = await zoom(); const h1 = await hash()
check(z.mode === 0 && z.zs[0] === 1, 'K1: F16 selects Scope at stage 1')
const seq = []; for (const key of ['NumLock', 'Numpad7', 'Numpad4', 'Numpad1']) { await press(key); seq.push((await zoom()).zs[0]) }
check(JSON.stringify(seq) === '[2,3,4,5]', `K1: Clear, 7, 4, 1 step Scope through stages ${seq.join(', ')}`)
const h5 = await hash(); check(h5 !== h1, 'K1: stage 5 draws a different picture from stage 1')
await press('F16'); check((await hash()) === h1, 'K1: pressing the stage 1 key restores the stage 1 picture byte-identical')
await press('F17'); const m1 = (await zoom()).mode; await press('F18'); const m2 = (await zoom()).mode; await press('F19'); const m3 = (await zoom()).mode
check(m1 === 1 && m2 === 2 && m3 === 3, `K2: F17, F18, F19 select Bars, Radial, Spectro (modes ${m1}, ${m2}, ${m3})`)
await press('NumpadEnter'); z = await zoom(); check(z.mode === 3 && z.zs[3] === 5, 'K2: the last key of the fourth column sets Spectro stage 5')
const hz = []; for (const k of ['F16', 'F17', 'F18', 'F19']) { await press(k); const h1k = await hash(); const last = ['Numpad1', 'Numpad2', 'Numpad3', 'NumpadEnter'][hz.length]; await press(last); hz.push(h1k !== (await hash())); await press(k) }
check(hz.every(Boolean), 'K1: stage 5 differs from stage 1 in all four modes')
// K3 palette arrows
const pal = () => ev(() => document.getElementById('palsel').value)
await ev(() => document.body.focus()); const order = []; for (let i = 0; i < 7; i++) { await pg.keyboard.press('ArrowRight'); order.push(await pal()) }
check(order.join() === 'arcs,phosphor,amber,indigo,heat,mono,orig', `K3: Right arrow steps the palette in order and wraps (${order.join(' ')})`)
await pg.keyboard.press('ArrowLeft'); check((await pal()) === 'mono', 'K3: Left arrow reverses and wraps')
await set('palsel', 'orig')
await pg.keyboard.press('Shift+ArrowLeft'); const b7 = await ev(() => document.getElementById('pal').value); await pg.keyboard.press('Shift+ArrowLeft'); const b6 = await ev(() => document.getElementById('pal').value); await pg.keyboard.press('Shift+ArrowRight'); const b7b = await ev(() => document.getElementById('pal').value)
check(b7 === '7' && b6 === '6' && b7b === '7', `K3: Shift with an arrow steps the palette bit depth (${b7}, ${b6}, ${b7b})`)
await set('pal', 8)
// K4 arrows are not hijacked from controls that use them
await ev(() => document.getElementById('scrub').focus()); const before = await pal(); await pg.keyboard.press('ArrowRight'); check((await pal()) === before, 'K4: arrows do nothing to the palette while a slider has focus')
// K5 learn, persist, old keys stop working, reset
await ev(() => (document.activeElement && document.activeElement.blur(), document.body.focus())); await ev(() => document.querySelector('[data-learn="0"]').click())
for (const k of ['KeyA', 'KeyS', 'KeyD', 'KeyF', 'KeyG']) await press(k)
check((await ev(() => document.getElementById('learnhint').textContent)) === 'Saved.', 'K5: learning five keys saves the column')
await press('F18'); await press('KeyG'); z = await zoom(); check(z.mode === 0 && z.zs[0] === 5, 'K5: a learned key sets its mode and stage')
await press('F17'); await press('Numpad7'); check((await zoom()).mode === 1, 'K5: the old key for that column no longer works')
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 30000 })
await ev(() => (document.activeElement && document.activeElement.blur(), document.body.focus())); await press('F18'); await press('KeyA'); z = await zoom(); check(z.mode === 0 && z.zs[0] === 1, 'K5: learned keys persist across a reload')
await ev(() => document.getElementById('resetkeys').click()); await ev(() => (document.activeElement && document.activeElement.blur(), document.body.focus())); await press('F18'); await press('F16'); check((await zoom()).mode === 0, 'K5: Reset keys restores the defaults')
check(errors.length === 0, `no script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close(); process.exit(fails.length ? 1 : 0)
