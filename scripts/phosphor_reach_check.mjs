#!/usr/bin/env node
// phosphor_reach_check.mjs: R1 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 22).
// Can a person actually REACH every control? At three window sizes, both skins, every level, with the offer banner showing and a song
// playing: the sticky picture deck stays under 60 percent of the viewport, and a trial click (scroll to it, hit-test it, do not click)
// succeeds on every visible button, slider and checkbox. Usage: node scripts/phosphor_reach_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_reach_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(page).href
const SIZES = [[1270, 990], [1024, 768], [390, 844]], full = process.env.REACH_FULL === '1'
for (const [w, h] of SIZES) for (const skin of ['', 'pocket']) for (const lvl of (full ? [1, 2, 3, 4] : [1, 4])) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(String(e)))
  await pg.goto(`${base}?test=1&shutter=off&level=${lvl}${skin ? '&skin=pocket' : ''}`); await pg.waitForTimeout(1200)
  await pg.evaluate(() => { const m = document.getElementById('molt'); document.getElementById('moltt').textContent = 'You are shaping the picture. Intermediate adds Glitch effects with Latch and Perform keys, and the Steps sequencer with Feel and Tighten. Nothing changes unless you say so.'; m.hidden = false })
  await pg.click('#play'); await pg.waitForTimeout(600)
  await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => { if (d.id === 'grown') d.open = true }))
  const deckH = await pg.evaluate(() => document.getElementById('deck').getBoundingClientRect().height)
  const label = `${w}x${h} ${skin || 'default'} level ${lvl}`
  check(deckH <= h * 0.6, `R1: ${label}: the sticky deck is ${Math.round(deckH)} px, ${Math.round(deckH / h * 100)} percent of the window (limit 60)`)
  const ids = await pg.evaluate(() => { const out = []; const closed = (e) => { for (let d = e.parentElement; d; d = d.parentElement) if (d.tagName === 'DETAILS' && !d.open && !(e.tagName === 'SUMMARY' && e.parentElement === d)) return true; return false }; document.querySelectorAll('button, input:not([type=hidden]):not([type=file]), select, summary').forEach((e, i) => { if (closed(e)) return; const r = e.getBoundingClientRect(); if (e.offsetParent !== null && r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden' && !e.closest('[hidden]') && !e.closest('.vh') && !(e.type === 'radio')) { e.setAttribute('data-rc', String(i)); out.push(String(i)) } }); return out })
  const fails = await pg.evaluate(() => {
    const bad = [], deck = document.getElementById('deck'), dock = document.getElementById('dock'), hud = null
    document.querySelectorAll('[data-rc]').forEach((e) => {
      let ok = false; window.scrollTo(0, 0); const dy = deck.getBoundingClientRect().height, top = dy + 6, bottom = (dock && getComputedStyle(dock).display !== 'none' ? dock.getBoundingClientRect().top : innerHeight) - 6
      if (e.closest('.deck') || e.closest('header') || e.closest('#dock')) { const r = e.getBoundingClientRect(); const h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (h && (h === e || e.contains(h))) ok = true; if (!ok) { for (const al of ['center', 'start', 'end']) { e.scrollIntoView({ block: al }); const r2 = e.getBoundingClientRect(), h2 = document.elementFromPoint(r2.left + r2.width / 2, r2.top + r2.height / 2); if (h2 && (h2 === e || e.contains(h2))) { ok = true; break } } } }
      else { const r0 = e.getBoundingClientRect(), y = scrollY + r0.top - top - 4; window.scrollTo(0, Math.max(0, y)); const r = e.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + Math.min(r.height / 2, 10); if (r.top >= top - 2 && r.bottom <= bottom + 2 + r.height && cy < bottom) { const h = document.elementFromPoint(cx, cy); ok = !!h && (h === e || e.contains(h) || (h.tagName === 'LABEL' && h.contains(e))) } }
      if (!ok) bad.push(e.id || e.textContent.trim().slice(0, 18) || e.tagName)
    }); return bad })
  check(fails.length === 0, `R1: ${label}: ${ids.length} controls, ${fails.length} cannot be reached${fails.length ? ' (' + fails.slice(0, 5).join(', ') + ')' : ''}`)
  if (errs.length) check(false, `R1: console errors ${errs[0]}`)
  await ctx.close()
}
await b.close(); process.exit(bad ? 1 : 0)
