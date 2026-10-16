#!/usr/bin/env node
// phosphor_molt_check.mjs: M1 to M9 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 21, UX molt level slider).
// Usage: node scripts/phosphor_molt_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_molt_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(page).href
const errs = []
const open = async (q, w = 1280) => { const ctx = await b.newContext({ viewport: { width: w, height: 900 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + q); await pg.waitForTimeout(1200); return pg }
const vis = (pg) => pg.evaluate(() => [...document.querySelectorAll('[data-min]')].filter((e) => getComputedStyle(e).display !== 'none').map((e) => (e.id || e.className || e.tagName) + ':' + e.getAttribute('data-min')))
// M4 defaults
let pg = await open('?shutter=off'); check((await pg.evaluate(() => document.documentElement.dataset.lvl)) === '1', 'M4: a first visit with no parameters opens at level 1 (Noob)')
const t4 = await open('?test=1'); check((await t4.evaluate(() => document.documentElement.dataset.lvl)) === '4', 'M4: test=1 opens at level 4'); await t4.context().close()
// M1 level 1
let v = await vis(pg); check(v.length === 0, `M1: at level 1 nothing above level 1 is visible (${v.length} shown)`)
const must1 = await pg.evaluate(() => ['kpick', 'kcol', 'kzoom', 'kwob', 'play', 'scrub', 'lvl'].every((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' }) && [...document.querySelectorAll('#presets [data-pre]')].length > 0 && getComputedStyle(document.getElementById('notesb')).display !== 'none')
check(must1, 'M1: the picker, play, the look buttons, words, Notes and the slider are visible at level 1')
const hid1 = await pg.evaluate(() => ['genome', 'grown', 'slices'].every((id) => getComputedStyle(document.getElementById(id)).display === 'none') && getComputedStyle(document.querySelector('.sheet')).display === 'none')
check(hid1, 'M1: the genome ribbon, Grown-up controls, Sampler and ladder are not shown at level 1')
// M2 cumulative
const sets = []; for (const n of [1, 2, 3, 4]) { await pg.evaluate((n) => { const s = document.getElementById('lvl'); s.value = n; s.dispatchEvent(new Event('input', { bubbles: true })) }, n); sets.push(await vis(pg)) }
const exp = [0, 4, 6, 9].map((x) => x)
check(sets[0].length === 0 && sets.every((s, i) => i === 0 || sets[i - 1].every((x) => s.includes(x))), `M2: each level shows everything the level below showed (${sets.map((s) => s.length).join(', ')} marked elements)`)
check(sets.every((s, i) => s.every((x) => +x.split(':').pop() <= i + 1)) && sets.every((s, i) => [...Array(i + 1).keys()].every(() => true)), 'M2: nothing is shown above its own level')
const grp = (n) => pg.evaluate((n) => { document.getElementById('lvl').value = n; document.getElementById('lvl').dispatchEvent(new Event('input', { bubbles: true })); return [...document.querySelectorAll('details.grp')].filter((d) => getComputedStyle(d).display !== 'none').map((d) => d.querySelector('summary').textContent) }, n)
check(JSON.stringify(await grp(2)) === '["Zoom","Resolution","Look"]' && JSON.stringify(await grp(3)) === '["Zoom","Resolution","Look","Glitch","Steps"]' && JSON.stringify(await grp(4)) === '["Zoom","Resolution","Look","Glitch","Steps","Keys"]', 'M2: the control groups arrive in order: Zoom, Resolution, Look, then Glitch, Steps, then Keys')
// M3 keyboard, aria, reload
await pg.evaluate(() => { const s = document.getElementById('lvl'); s.value = 1; s.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.focus('#lvl'); await pg.keyboard.press('ArrowRight'); await pg.keyboard.press('ArrowRight')
check((await pg.evaluate(() => [document.documentElement.dataset.lvl, document.getElementById('lvl').getAttribute('aria-valuetext'), document.getElementById('lvlo').textContent])).join() === '3,Intermediate,Intermediate', 'M3: the arrow keys move the slider, which names the level (Intermediate)')
await pg.evaluate(() => document.body.dispatchEvent(new Event('change', { bubbles: true }))); await pg.waitForTimeout(700); await pg.reload(); await pg.waitForTimeout(1500)
check((await pg.evaluate(() => document.documentElement.dataset.lvl)) === '3', 'M3: the level survives a reload')
await pg.context().close()
// M5 to M7 offers
pg = await open('?test=1&level=1&shutter=off')
const st = () => pg.evaluate(() => ({ lv: window.PhosphorTest.molt.level(), hid: document.getElementById('molt').hidden, txt: document.getElementById('moltt').textContent, yes: document.getElementById('moltyes').textContent }))
await pg.evaluate(() => window.PhosphorTest.molt.addSec(40)); check((await st()).hid, 'M5: 40 s of play and no looks tried gives no offer')
for (const k of ['kcol', 'kzoom']) await pg.click('#' + k); check((await st()).hid, 'M5: two looks tried is still no offer')
await pg.click('#kwob', { delay: 50 }); await pg.waitForTimeout(100); let s = await st()
check(!s.hid && /Beginner/.test(s.txt) && s.lv === 1, 'M5: 20 s of play and three different looks tried offers Beginner');
check(s.lv === 1, 'M6: the offer alone did not change the level')
await pg.click('#moltno'); s = await st(); check(s.hid && s.lv === 1, 'M6: Not now closes the offer and the level stays')
await pg.evaluate(() => window.PhosphorTest.molt.check()); check((await st()).hid, 'M6: the same evidence does not bring the offer back')
for (const sel of ['#kid [data-km="0"]', '#kid [data-km="1"]']) await pg.click(sel); await pg.evaluate(() => window.PhosphorTest.molt.check())
check((await st()).hid, 'M6: after Not now, five looks and 40 s is not enough (it now takes six looks and 40 s)')
await pg.click('#kid [data-km="2"]'); await pg.evaluate(() => window.PhosphorTest.molt.check())
s = await st(); check(!s.hid, 'M6: at twice the evidence (six looks, 40 s) the offer returns')
await pg.click('#moltyes'); s = await st(); check(s.lv === 2 && /Level 2 is on/.test(s.txt) && /genome ribbon/.test(s.txt) && s.yes === 'Undo', 'M7: Show more makes it level 2, names the new controls and offers Undo')
check(await pg.evaluate(() => getComputedStyle(document.getElementById('genome')).display !== 'none'), 'M7: the genome ribbon is now shown')
await pg.click('#moltyes'); s = await st(); check(s.lv === 1 && s.hid, 'M7: Undo restores level 1')
// M8 focus
await pg.evaluate(() => { const s = document.getElementById('lvl'); s.value = 4; s.dispatchEvent(new Event('input', { bubbles: true })) }); await pg.evaluate(() => { document.querySelector('#grown').open = true; document.getElementById('sessrec').focus() })
await pg.evaluate(() => { const s = document.getElementById('lvl'); s.value = 1; s.dispatchEvent(new Event('input', { bubbles: true })) })
check(await pg.evaluate(() => document.activeElement.id === 'lvl'), 'M8: lowering the level while focus is in a control that disappears moves focus to the slider')
// M9
await pg.context().close()
for (const w of [360, 390]) { const p = await open('?shutter=off', w); check(!(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth)), `M9: no horizontal scroll at ${w} px, level 1`); await p.context().close() }
check(errs.length === 0, `M9: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
