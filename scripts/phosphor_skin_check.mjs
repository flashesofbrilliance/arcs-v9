#!/usr/bin/env node
// phosphor_skin_check.mjs: checks P1 to P3 and P5 from _PATTERNS/2026-10-15-sequencer-5d-prereg.md (Amendment 3, Pocket skin).
// P4 is the other check scripts run with PHOSPHOR_SKIN=pocket. Uses the page's test hook (?test=1). No files needed.
// Usage: node scripts/phosphor_skin_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_skin_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const b = await pw.chromium.launch(), errors = [], reqs = []
const url = pathToFileURL(path.resolve(page)).href
const open = async (q, w = 1280) => { const ctx = await b.newContext({ viewport: { width: w, height: 1000 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => reqs.push(r.url())); await pg.goto(url + q); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 30000 }); return { ctx, pg } }
// P1
{
  const { ctx, pg } = await open('?test=1')
  const has = () => pg.evaluate(() => ({ strip: !!document.getElementById('ledstrip'), dock: !!document.getElementById('dock'), skin: document.documentElement.getAttribute('data-skin') }))
  let s = await has(); check(!s.strip && s.dock && !s.skin, 'P1: the default page has the native dock but no strip and no skin attribute')
  await pg.locator('#skinb').click(); s = await has(); check(s.strip && s.dock && s.skin === 'pocket', 'P1: switching on creates the strip and the dock and sets the skin')
  await pg.locator('#skinb').click(); s = await has(); check(!s.strip && s.dock && !s.skin, 'P1: switching off removes the strip and the skin and keeps the dock')
  await ctx.close()
}
// P2, P3
{
  const { ctx, pg } = await open('?skin=pocket&test=1')
  const seek = (f) => pg.evaluate((f) => { const s = document.getElementById('scrub'); s.value = Math.round(f * 1000); s.dispatchEvent(new Event('input', { bubbles: true })) }, f)
  const samples = []
  await pg.locator('#play').click(); await pg.waitForTimeout(150)
  for (const f of [0.02, 0.1, 0.2, 0.3, 0.45, 0.55, 0.65, 0.8, 0.95]) { await seek(f); await pg.waitForTimeout(160); { const ls = []; for (let k = 0; k < 8; k++) { ls.push((await pg.evaluate(() => window.PhosphorTest.meter())).level); await pg.waitForTimeout(16) } const a = await pg.evaluate(() => window.PhosphorTest.meter()); ls.push(a.level); a.lo = Math.min(...ls); a.hi = Math.max(...ls); samples.push(a) } }
  check(samples.every((m) => m.strip >= Math.round(m.lo * m.stripN) - 1 && m.strip <= Math.round(m.hi * m.stripN) + 1), `P2: the top strip lights the dots the level calls for, within 1 of the level range, while playing (${samples.map((m) => m.strip + '/' + m.stripN).join(' ')})`)
  const hi = samples.reduce((a, m) => (m.level > a.level ? m : a)), lo = samples.reduce((a, m) => (m.level < a.level ? m : a))
  check(Math.max(...samples.map((m) => m.strip)) > Math.min(...samples.map((m) => m.strip)) , `P2: a loud frame lights more dots than a quiet one (${Math.max(...samples.map((m) => m.strip))} against ${Math.min(...samples.map((m) => m.strip))} on the strip)`)
  for (const w of [1280, 790]) {
    await pg.setViewportSize({ width: w, height: 1000 }); await pg.waitForTimeout(250)
    const e = await pg.evaluate(() => { const r = (s) => { const el = document.querySelector(s); return el ? Math.round(el.getBoundingClientRect().right) : null }; return { hero: r('.hero'), alts: r('.alts'), foot: r('footer'), read: r('.read'), sheet: r('.sheet') } })
    check(Math.abs(e.alts - e.hero) <= 2 && Math.abs(e.foot - e.hero) <= 2 && Math.abs(e.sheet - e.hero) <= 2, `P3: at ${w}px the blocks end at the same right edge in the Pocket skin (hero ${e.hero}, details ${e.alts}, footer ${e.foot}, ladder ${e.sheet})`)
  }
  await ctx.close()
}
check(errors.length === 0, `P5: no console errors${errors.length ? ': ' + errors[0] : ''}`)
check(reqs.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')), 'P5: no network requests')
await b.close(); process.exit(fails.length ? 1 : 0)
