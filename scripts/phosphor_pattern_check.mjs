#!/usr/bin/env node
// phosphor_pattern_check.mjs: the pattern text box (amendment 70, checks P1-P10 with the corrections recorded in amendment 71). Usage: node scripts/phosphor_pattern_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import fs from 'node:fs'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2]
if (!page) { console.log('usage: node scripts/phosphor_pattern_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch(), errs = [], reqs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }) })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); pg.on('request', (r) => { if (!/^(file|data|blob):/.test(r.url())) reqs.push(r.url()) }); pg.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()) })
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.click('details.grp:has(#seqg) > summary')
const on = (lane) => pg.evaluate((l) => [...document.querySelectorAll(`#seqg .sq[data-l="${l}"]`)].map((b, i) => (b.getAttribute('aria-pressed') === 'true' ? i + 1 : 0)).filter(Boolean), lane)
const apply = async (text, lane = 'stutter', seed) => { await pg.selectOption('#ptlane', lane); if (seed !== undefined) await pg.fill('#ptseed', String(seed)); await pg.fill('#pttxt', text); await pg.click('#ptgo'); return on(lane) }
const J = (a) => a.join(',')
// P1 grid
check(J(await apply('x x x x')) === '1,5,9,13', 'P1a: x x x x fills 1,5,9,13')
check(J(await apply('x*4')) === '1,5,9,13', 'P1b: x*4 fills 1,5,9,13')
check(J(await apply('[x x] x')) === '1,5,9', 'P1c: [x x] x fills 1,5,9 (corrected from the pre-registered 1,3,9, see amendment 71)')
check(J(await apply('x ~ x ~')) === '1,9', 'P1d: x ~ x ~ fills 1,9')
// P2 weights
check(J(await apply('x _ x')) === '1,11', 'P2a: x _ x fills 1,11 (2:1 over 16, rounded down)')
check(J(await apply('x!2 ~')) === J(await apply('x x ~')), 'P2b: x!2 ~ equals x x ~')
// P3 euclid
check(J(await apply('x(3,8)')) === '1,7,13', 'P3a: x(3,8) fills 1,7,13')
check(J(await apply('x(4,16)')) === '1,5,9,13', 'P3b: x(4,16) fills 1,5,9,13')
await apply('x x x x'); const before = await on('stutter'); await apply('x(9,8)'); check(J(await on('stutter')) === J(before) && /cannot be more/.test(await pg.textContent('#ptmsg')), 'P3c: k greater than n is refused and the lane is untouched')
// P4 alternation
check(J(await apply('<x ~>')) === '1', 'P4a: <x ~> fills step 1 on bar 1')
await pg.click('#ptnext'); const b2 = await on('stutter'); await pg.click('#ptnext'); const b3 = await on('stutter')
check(b2.length === 0 && J(b3) === '1', `P4b: Next bar gives nothing on bar 2 and step 1 on bar 3 (got [${J(b2)}] then [${J(b3)}])`)
// P5 determinism
const r1 = J(await apply('x*8?', 'stutter', 1)), runs = new Set(); for (let i = 0; i < 10; i++) runs.add(J(await apply('x*8?', 'stutter', 1)))
const others = new Set(); for (const s of [2, 3, 4, 5, 6]) others.add(J(await apply('x*8?', 'stutter', s)))
check(runs.size === 1 && runs.has(r1) && [...others].some((o) => o !== r1), `P5: x*8? repeats exactly for one seed (${r1}) and differs for another seed (${[...others].length} distinct of 5)`)
// P6 refusal
await apply('x . x'); const keep = await on('stutter'); let ok = true, why = []
for (const t of ['x $', 'x(', '[x', 'x*0', '', 'x'.repeat(201), 'x,y', 'x@3', 'x|y']) {
  await pg.fill('#pttxt', t); await pg.click('#ptgo'); const m = await pg.textContent('#ptmsg'); const now = await on('stutter')
  if (J(now) !== J(keep) || !/not changed/.test(m)) { ok = false; why.push(JSON.stringify(t.slice(0, 12))) }
}
check(ok, 'P6: bad input leaves the lane untouched with a message ' + why.join(' '))
// P7 containment
await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300)
const kidVis = await pg.evaluate(() => { const e = document.querySelector('.pat'), r = e.getBoundingClientRect(); return getComputedStyle(e).display !== 'none' && r.width > 0 })
check(!kidVis, 'P7a: the pattern box is not shown in Kid mode')
check(reqs.length === 0, 'P7b: no network request (' + reqs.slice(0, 2).join(' ') + ')')
// P8 recipe: the existing cells event carries the lane
await pg.evaluate(() => { document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown')) }); await pg.waitForTimeout(1700)
await pg.evaluate(() => { const g = document.getElementById('grown'); if (g) g.open = true; document.querySelector('#seqg').closest('details').open = true }); await apply('x ~ x ~'); await pg.waitForTimeout(700)
const rec = await pg.evaluate(() => { const ev = window.PhosphorTest.recipe.ev().filter((e) => e[2] === '@cells'); const c = ev.length ? ev[ev.length - 1][3] : null; return c && (c.stutter || (c.cells && c.cells.stutter) || c) })
check(JSON.stringify(rec).includes('1,0,0,0,0,0,0,0,1') || JSON.stringify(rec).includes('"stutter":[1,0,0,0,0,0,0,0,1'), 'P8: the recipe cells event carries the filled lane ' + JSON.stringify(rec).slice(0, 80))
// P9 size
const bytes = fs.statSync(page).size
check(bytes < 400000, `P9a: page ${bytes} bytes (cap 400,000)`)
const src = fs.readFileSync('_ARTIFACTS/phosphor-src/app.js', 'utf8'); const a0 = src.indexOf('function patParse'), a1 = src.indexOf('var PAT = {'), a2 = src.indexOf('seqBuild($("seqf"))')
check(a1 - a0 < 8000 && a0 > a2, `P9b: parser source ${a1 - a0} bytes (at most 8,000)`)
// P10 provenance
const log = fs.readFileSync('_PATTERNS/2026-10-23-phosphor-pattern-box-clean-room-log.md', 'utf8'), body = src.slice(a0, src.indexOf('(function () {', a1))
check(!/strudel|krill|pegjs|hap\b|queryArc|mini-?notation/i.test(body) && /2026-10-23/.test(log), 'P10: parser source has no Strudel identifier and the clean-room log is dated')
check(errs.length === 0, 'P11: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
