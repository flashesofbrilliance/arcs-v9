#!/usr/bin/env node
// raw_capture_anim_check.mjs: the checks ADR-087 sets for an animated single-file instrument page.
// 1. REST INVARIANT: for each track, scrubbing to t = 1 leaves the full readout state equal to the static page,
//    and playing a track to its end lands on the same state.
// 2. TRANSPORT: play and pause work, a real control input halts playback, starting another track restores the first.
// 3. REDUCED MOTION: the page loads at rest, Play is hidden, stepping still works.
// 4. FRAME BUDGET (with --budget): at 4x CPU slowdown the heaviest path stays at or above 30 fps and the replay
//    wall time stays within 15 percent of its design duration.
// No console errors in any run. Exit 1 on any failure.
// Usage: node scripts/raw_capture_anim_check.mjs <page.html> [--budget]
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const file = process.argv[2], budget = process.argv.includes('--budget')
if (!file) { console.error('usage: raw_capture_anim_check.mjs <page.html> [--budget]'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable (set PLAYWRIGHT_ROOT)'); process.exit(2) }

const fails = []
const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const url = pathToFileURL(path.resolve(file)).href
const b = await pw.chromium.launch()
const errors = []

const snap = (pg) => pg.evaluate(() => JSON.stringify({ ev: document.getElementById('evo').textContent, clip: document.getElementById('clip').textContent, seen: document.getElementById('seen').textContent, real: document.getElementById('realpct').textContent, drift: document.getElementById('drift').textContent, y: document.getElementById('ylab').textContent, tag: document.getElementById('tag').textContent, sn: document.getElementById('snapro').textContent, arm: document.getElementById('armlab').textContent, plug: document.getElementById('plug').innerHTML, cells: [...document.querySelectorAll('#sheet rect')].map((r) => r.getAttribute('class')).join('|') }))

const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg = await ctx.newPage()
pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
await pg.goto(url); await pg.waitForTimeout(2100)
await pg.evaluate(() => document.querySelectorAll('details.alt').forEach((d) => (d.open = true)))
const base = await snap(pg)
const scrub = (id, v) => pg.evaluate(([id, v]) => { const i = document.querySelector('.tp[data-track="' + id + '"] input'); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
const btn = (id, a) => pg.locator('.tp[data-track="' + id + '"] [data-a=' + a + ']')

for (const id of ['develop', 'snap', 'ignite']) {
  await scrub(id, 0); const s0 = await snap(pg)
  await scrub(id, 1000); const s1 = await snap(pg)
  check(s1 === base, `rest invariant: ${id} at t=1 equals the static page`)
  if (id !== 'ignite') check(s0 !== base, `${id} at t=0 differs from the static page (the track does something)`)
}
await btn('develop', 'play').click(); await pg.waitForTimeout(700)
check((await btn('develop', 'play').textContent()) === 'Pause', 'play shows Pause while running')
await btn('develop', 'play').click()
check((await btn('develop', 'play').textContent()) === 'Play', 'pause returns the button to Play')
await btn('develop', 'play').click(); await pg.waitForTimeout(4700)
check((await snap(pg)) === base, 'playing develop to the end lands on the static page')
await btn('snap', 'play').click(); await pg.waitForTimeout(400)
await pg.evaluate(() => { const r = document.getElementById('capB'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) })
check((await btn('snap', 'play').textContent()) === 'Play', 'a real control input halts playback')
await pg.evaluate(() => { const r = document.getElementById('capA'); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })) })
await scrub('snap', 300); await btn('develop', 'play').click(); await pg.waitForTimeout(300)
check((await pg.evaluate(() => +document.querySelector('.tp[data-track=snap] input').value)) === 1000, 'starting another track restores the previous one to rest')
await ctx.close()

// ---- TAKE (ADR-087 rule 10): keyframes recorded from control edits, replayed with interpolation
{
  const c4 = await b.newContext({ viewport: { width: 1280, height: 900 } }), p4 = await c4.newPage()
  p4.on('pageerror', (e) => errors.push(String(e)))
  await p4.goto(url); await p4.waitForTimeout(2100)
  await p4.evaluate(() => document.querySelectorAll('details.alt').forEach((d) => (d.open = true)))
  const tScrub = (v) => p4.evaluate((v) => { const i = document.querySelector('.tp[data-track=take] input'); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })) }, v)
  const setC = (id, v) => p4.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
  const keys = () => p4.evaluate(() => document.querySelector('.tp[data-track=take] [data-k]').textContent)
  const evT = () => p4.evaluate(() => document.getElementById('evo').textContent)
  check((await keys()).startsWith('No keyframes'), 'take: starts empty')
  await setC('ev', 2.5)
  check((await keys()).startsWith('No keyframes'), 'take: editing with recording off writes no keyframe')
  await setC('ev', 1)
  await p4.locator('.tp[data-track=take] [data-a=rec]').click()
  check((await p4.locator('.tp[data-track=take] [data-a=rec]').getAttribute('aria-pressed')) === 'true', 'take: Record sets aria-pressed')
  check((await keys()).startsWith('1 keyframe'), 'take: recording captures a keyframe at the scrubber')
  await tScrub(500); await setC('ev', 3)
  await tScrub(1000); await setC('cb', 2)
  check((await keys()).startsWith('3 keyframes'), 'take: three keyframes after editing at 0, 50 and 100 percent')
  await tScrub(0); check((await evT()) === '+1.0 EV', 'take: scrubbing to the start restores the first keyframe')
  await tScrub(250); check((await evT()) === '+2.0 EV', 'take: scrubbing between keyframes interpolates (+2.0 EV at 25 percent)')
  await p4.locator('.tp[data-track=take] [data-a=play]').click(); await p4.waitForTimeout(6500)
  const endState = await p4.evaluate(() => ({ ev: document.getElementById('evo').textContent, cb: document.getElementById('cbo').textContent, rec: document.querySelector('.tp[data-track=take] [data-a=rec]').getAttribute('aria-pressed') }))
  check(endState.ev === '+3.0 EV' && endState.cb === '2 bit, 4 tones', 'take: replay ends on the last keyframe (+3.0 EV, 2 bit)')
  check(endState.rec === 'false', 'take: Play stops recording')
  await p4.reload(); await p4.waitForTimeout(2100)
  await p4.evaluate(() => document.querySelectorAll('details.alt').forEach((d) => (d.open = true)))
  check((await keys()).startsWith('3 keyframes'), 'take: keyframes persist across a reload (localStorage)')
  await tScrub(500); check((await evT()) === '+3.0 EV', 'take: a reloaded take replays')
  await p4.locator('.tp[data-track=take] [data-a=clear]').click()
  check((await keys()).startsWith('No keyframes'), 'take: Clear removes the keyframes')
  await c4.close()
}
const ctx2 = await b.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' }), pg2 = await ctx2.newPage()
await pg2.goto(url); await pg2.waitForTimeout(300)
check(await pg2.evaluate(() => document.getElementById('evo').textContent === '+1.0 EV'), 'reduced motion: the page loads at rest, no opening sweep')
check(await pg2.evaluate(() => [...document.querySelectorAll('.tp [data-a=play]')].every((x) => x.hidden)), 'reduced motion: Play is hidden')
await pg2.evaluate(() => { document.querySelectorAll('details.alt').forEach((d) => (d.open = true)); document.querySelector('.tp[data-track=snap] [data-a=back]').click() })
check((await pg2.evaluate(() => +document.querySelector('.tp[data-track=snap] input').value)) < 1000, 'reduced motion: stepping still works')
await ctx2.close()

if (budget) {
  const ctx3 = await b.newContext({ viewport: { width: 1280, height: 900 } }), pg3 = await ctx3.newPage()
  await pg3.addInitScript(() => { window.__frames = 0; const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = (cb) => raf((t) => { window.__frames++; cb(t) }) })
  await pg3.goto(url); await pg3.waitForTimeout(2200)
  const cdp = await ctx3.newCDPSession(pg3); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 })
  await pg3.evaluate(() => { const m = document.getElementById('mR'); m.checked = true; m.dispatchEvent(new Event('change', { bubbles: true })); const n = document.getElementById('np'); n.value = 8; n.dispatchEvent(new Event('input', { bubbles: true })); window.__frames = 0 })
  const t0 = Date.now(); await pg3.locator('.tp[data-track=develop] [data-a=play]').click()
  await pg3.waitForFunction(() => +document.querySelector('.tp[data-track=develop] input').value >= 1000, null, { timeout: 30000 })
  const wall = Date.now() - t0, fps = (await pg3.evaluate(() => window.__frames)) / (wall / 1000)
  check(fps >= 30, `frame budget: ${fps.toFixed(1)} fps on the re-cut path at 4x CPU slowdown (want >= 30)`)
  check(Math.abs(wall - 4200) / 4200 <= 0.15, `frame budget: replay took ${wall} ms against 4200 ms (within 15 percent)`)
  await ctx3.close()
}
check(errors.length === 0, `no console errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
process.exit(fails.length ? 1 : 0)
