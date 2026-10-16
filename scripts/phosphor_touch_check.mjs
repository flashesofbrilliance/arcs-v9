#!/usr/bin/env node
// phosphor_touch_check.mjs: R2 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 27, the touch-first slice).
// On an emulated iPhone 13, iPad Mini and a 360 px touch phone: pads and tabs at least 56 px tall with at least 6 px between them, sequencer steps at least 56 by 56 px
// in lane view, tap targets at least 44 px, picker labels at least 48 px tall, no sideways scroll, a lane chip works from the keyboard, and the desktop layout is
// unchanged from a baseline page. Usage: node scripts/phosphor_touch_check.mjs <page.html> [baseline.html]
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium, devices } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], baseline = process.argv[3]; if (!page) { console.log('usage: phosphor_touch_check.mjs <page.html> [baseline.html]'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch(), errs = [], url = (f) => pathToFileURL(path.resolve(f)).href + '?test=1&shutter=off&level=4'
const grp = async (pg, name) => { await pg.evaluate((name) => { document.querySelector('#grown').open = true; document.querySelectorAll('details.grp').forEach((d) => (d.open = d.querySelector('summary').textContent === name)) }, name); await pg.waitForTimeout(350) }
const prep = async (pg) => { await pg.goto(url(page)); await pg.waitForTimeout(1200); await pg.evaluate(() => { const n = document.getElementById('notesb'); if (n.getAttribute('aria-pressed') !== 'true') n.click() }) }
const DEVS = [['iPhone 13', devices['iPhone 13']], ['iPad Mini', devices['iPad Mini']], ['360 touch phone', { ...devices['iPhone 13'], viewport: { width: 360, height: 740 }, screen: { width: 360, height: 740 } }]]
for (const [name, dev] of DEVS) {
  const ctx = await b.newContext({ ...dev }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await prep(pg); await grp(pg, 'Zoom'); const padsR = await pg.evaluate(() => [...document.querySelectorAll('#pads .pad, #pads .ph')].filter((e) => e.offsetParent && e.getBoundingClientRect().width > 0).map((e) => { const x = e.getBoundingClientRect(); return [x.left, x.top, x.right, x.bottom, x.width, x.height] })); await grp(pg, 'Steps')
  const r = await pg.evaluate(() => {
    const vis = (s) => [...document.querySelectorAll(s)].filter((e) => e.offsetParent && e.getBoundingClientRect().width > 0).map((e) => e.getBoundingClientRect())
    const dims = (rs) => ({ n: rs.length, minW: Math.round(Math.min(...rs.map((x) => x.width))), minH: Math.round(Math.min(...rs.map((x) => x.height))) })
    const gapMin = (rs) => { let g = 1e9; for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) { const a = rs[i], c = rs[j], dx = Math.max(c.left - a.right, a.left - c.right), dy = Math.max(c.top - a.bottom, a.top - c.bottom); const d = Math.max(dx, dy); if (d >= 0 && d < g && (Math.abs(a.top - c.top) < 4 || Math.abs(a.left - c.left) < 4)) g = d } return Math.round(g) }
    const steps = vis('#seqg .sq'), tabs = vis('#seqg .sqtabs .btn')
    const closed = (e) => { for (let d = e.parentElement; d; d = d.parentElement) if (d.tagName === 'DETAILS' && !d.open && !(e.tagName === 'SUMMARY' && e.parentElement === d)) return true; return false }
    const taps = [...document.querySelectorAll('button, summary, select, input[type=range], .seg label')].filter((e) => e.offsetParent && !closed(e) && !e.closest('.vh') && !e.closest('.pinbar') && e.getBoundingClientRect().width > 0 && !e.closest('#seqf'))
    const small = taps.filter((e) => { const x = e.getBoundingClientRect(); return x.height < 44 || (x.width < 44 && !(e.tagName === 'INPUT')) }).map((e) => (e.id || e.className || e.tagName) + ':' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)).slice(0, 6)
    const labels = vis('.seg label')
    return { steps: dims(steps), tabs: dims(tabs), laneMode: document.getElementById('seqg').classList.contains('lane'), stepsShown: steps.length, small, labelMinH: dims(labels).minH, pageScroll: document.documentElement.scrollWidth > innerWidth, seqScroll: document.getElementById('seqg').scrollWidth > document.getElementById('seqg').clientWidth + 1 }
  })
  const pr = padsR.map((x) => ({ left: x[0], top: x[1], right: x[2], bottom: x[3], width: x[4], height: x[5] })); let pg2 = 1e9; for (let i = 0; i < pr.length; i++) for (let j = i + 1; j < pr.length; j++) { const a = pr[i], c = pr[j], dx = Math.max(c.left - a.right, a.left - c.right), dy = Math.max(c.top - a.bottom, a.top - c.bottom), d = Math.max(dx, dy); if (d >= 0 && d < pg2 && (Math.abs(a.top - c.top) < 4 || Math.abs(a.left - c.left) < 4)) pg2 = d }
  const pMinH = Math.round(Math.min(...pr.map((x) => x.height))), pMinW = Math.round(Math.min(...pr.map((x) => x.width)))
  check(pr.length >= 20 && pMinH >= 56 && Math.round(pg2) >= 6, `R2 ${name}: ${pr.length} pads and tabs are at least 56 px tall (${pMinW} by ${pMinH}) with ${Math.round(pg2)} px between them`)
  check(r.laneMode && r.stepsShown === 16 && r.steps.minW >= 56 && r.steps.minH >= 56, `R2 ${name}: the sequencer shows one lane (${r.stepsShown} steps) as large buttons (${r.steps.minW} by ${r.steps.minH})`)
  check(r.small.length === 0, `R2 ${name}: every tap target is at least 44 px${r.small.length ? ' (small: ' + r.small.join(', ') + ')' : ''}`)
  check(r.labelMinH >= 48, `R2 ${name}: picker labels are at least 48 px tall (${r.labelMinH})`)
  check(!r.pageScroll && !r.seqScroll, `R2 ${name}: neither the page nor the sequencer scrolls sideways`)
  // keyboard lane chip: focus a different tab, press Enter, the selected row changes
  await pg.focus('#seqg .sqtabs .btn[data-lane="crush"]'); await pg.keyboard.press('Enter'); const lane = await pg.evaluate(() => document.querySelector('#seqg .sqrow.sqsel').getAttribute('data-row'))
  check(lane === 'crush', `R2 ${name}: a lane chip works from the keyboard (selected ${lane})`)
  await ctx.close()
}
// desktop unchanged: compare the sequencer step rectangles with the baseline page, fine pointer, 1270 wide
if (baseline) {
  const rects = async (f) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); await pg.goto(url(f)); await pg.waitForTimeout(1200); await pg.evaluate(() => { document.querySelector('#grown').open = true; document.querySelectorAll('details.grp').forEach((d) => (d.open = d.querySelector('summary').textContent === 'Steps')) }); await pg.waitForTimeout(300); const r = await pg.evaluate(() => [...document.querySelectorAll('#seqg .sq')].map((e) => { const x = e.getBoundingClientRect(); return [Math.round(x.width), Math.round(x.height)] })); const lane = await pg.evaluate(() => document.getElementById('seqg').classList.contains('lane')); await ctx.close(); return { r, lane } }
  const A = await rects(page), B0 = await rects(baseline)
  check(!A.lane && JSON.stringify(A.r) === JSON.stringify(B0.r) && A.r.length === 176, `R2 desktop: the sequencer is not in lane view and its ${A.r.length} step sizes match the baseline page`)
}
check(errs.length === 0, `R2: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
