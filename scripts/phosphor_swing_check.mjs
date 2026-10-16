#!/usr/bin/env node
// phosphor_swing_check.mjs: W1 to W7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 19).
// Usage: node scripts/phosphor_swing_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_swing_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg = await ctx.newPage()
const errs = []; pg.on('pageerror', (e) => errs.push(String(e)))
const url = pathToFileURL(page).href + '?test=1&shutter=off'
await pg.goto(url); await pg.waitForTimeout(1500)
const G = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.groove[fn](...a), [fn, a])
const times = () => pg.evaluate(() => { const g = window.PhosphorTest.groove, o = []; for (let j = 0; j < 8; j++) o.push(g.fire(j)); return { o, st: g.step(), base: g.base() } })
await G('swing', 50); let r = await times()
check(r.o.every((f, j) => Math.abs(f - (r.base + j * r.st)) < 1e-4), 'W1: Feel 50 leaves every step time unchanged (0.1 ms)')
await G('swing', 67); r = await times()
check(r.o.every((f, j) => Math.abs(f - (r.base + j * r.st + (j % 2 ? r.st / 3 : 0))) < 5e-4), `W2: Feel 67 puts odd steps one third of a step late (step ${(r.st * 1000).toFixed(1)} ms), even steps unchanged`)
// W3: the highlighted column follows the swung time
const col = (t) => pg.evaluate((t) => { const g = window.PhosphorTest.groove; g.head(t); return g.col() }, t)
const e0 = r.base + 1 * r.st, late = e0 + r.st / 3
check((await col(e0 + 0.001)) === 0 && (await col(late + 0.001)) === 1, 'W3: the odd step lights up late (still on step 0 at its straight time, on step 1 at its swung time)')
// W4: tighten
await G('swing', 50); await G('tighten', 0)
const wait0 = await pg.evaluate(() => window.PhosphorTest.groove.wait(0.123)); check(wait0 === 0, 'W4: Tighten 0 waits 0 ms')
await G('tighten', 100)
const ws = await pg.evaluate(() => { const g = window.PhosphorTest.groove, st = g.step(), base = g.base(), out = []; for (let k = 0; k < 40; k++) { const t = 0.05 + k * 0.0377, w = g.wait(t); out.push({ t, w, land: t + w, onGrid: Math.abs(((t + w - base) / st) - Math.round((t + w - base) / st)) < 0.002, st }) } return out })
check(ws.every((x) => x.w >= 0 && x.w <= x.st + 1e-6 && x.onGrid), `W4: Tighten 100 lands every press on a grid time, never earlier, waits at most one step (${(ws[0].st * 1000).toFixed(0)} ms)`)
await G('tighten', 50); const w50 = await pg.evaluate(() => { const g = window.PhosphorTest.groove; return [g.wait(0.0501), (() => { g.tighten(100); return g.wait(0.0501) })()] })
check(Math.abs(w50[0] - w50[1] / 2) < 2e-3, 'W4: Tighten 50 waits half as long as Tighten 100')
// W4b: a real key press under Tighten 100 starts late, a quick tap that ends before the wait starts nothing
await pg.evaluate(() => { const T = window.PhosphorTest; T.groove.tighten(100); T.groove.swing(50); T.notes.on(true) }); await pg.waitForTimeout(100)
await pg.evaluate(() => document.getElementById('notesb').getAttribute('aria-pressed') === 'true' || document.getElementById('notesb').click())
await pg.evaluate(() => document.body.focus())
const wantWait = await pg.evaluate(() => window.PhosphorTest.groove.wait(window.PhosphorTest.tnow()))
await pg.keyboard.down('Digit1'); const v0 = await G('voices'); await pg.waitForTimeout(Math.max(250, 1000 * 0.15)); const v1 = await G('voices'); await pg.keyboard.up('Digit1')
check(wantWait === 0 || (v0 === 0 && v1 === 1), `W4: a real key press under Tighten 100 starts after its wait (${(wantWait * 1000).toFixed(0)} ms): ${v0} voices at once, ${v1} after`)
await G('voices'); await pg.waitForTimeout(400)
await pg.keyboard.down('Digit2'); await pg.keyboard.up('Digit2'); await pg.waitForTimeout(400); check((await G('voices')) === 0, 'W4: a tap released before its wait leaves no stuck note')
// W5: a swung stutter step fires at its swung time and ends after the gate
await G('swing', 67)
const w5 = await pg.evaluate(() => { const T = window.PhosphorTest, g = T.groove, st = g.step(); T.seq.clear(); T.seq.set('tear', 1, 1); T.seq.gate(0.5); const f = g.fire(1), a = T.seq.active; return [a(f - 0.005).tear === true, a(f + 0.002).tear === true, a(f + st * 0.5 + 0.01).tear === true, a(g.base() + st + 0.001).tear === true] })
check(!w5[0] && w5[1] && !w5[2] && !w5[3], 'W5: Tear on step 2 at 67 percent is off before its swung time, on at it, off after the gate, and off at the straight time')
// W6: reload keeps it
await G('swing', 58); await G('tighten', 30); await pg.evaluate(() => document.body.dispatchEvent(new Event('change', { bubbles: true }))); await pg.waitForTimeout(700)
await pg.reload(); await pg.waitForTimeout(1800)
const keep = await pg.evaluate(() => [document.getElementById('swo').textContent, document.getElementById('tz').value])
check(keep[0] === '58 percent' && keep[1] === '30', `W6: Feel and Tighten survive a reload (${keep.join(', ')})`)
check(errs.length === 0, `W6: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
