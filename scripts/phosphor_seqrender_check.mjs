#!/usr/bin/env node
// phosphor_seqrender_check.mjs: the sequencer in the offline render (amendment 62). The pattern cells are recorded in the recipe and the render fires them on the song clock. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_seqrender_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_seqrender_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true))
await pg.evaluate(() => window.PhosphorTest.tap.set(120, 0))
// S1 pressing pattern cells is recorded as one cells action in the recipe
await pg.evaluate(() => { for (let i = 0; i < 16; i++) document.querySelector('.sq[data-l="crush"][data-i="' + i + '"]').click() }); await pg.waitForTimeout(500)
const cellsEv = (await pg.evaluate(() => window.PhosphorTest.recipe.ev())).filter((e) => e[2] === '@cells')
check(cellsEv.length === 1 && cellsEv[0][3].crush.every((v) => v === 1), `S1: the pattern cells are recorded in the recipe as one action (${cellsEv.length} action, crush lane ${cellsEv[0] && cellsEv[0][3].crush.reduce((a, c) => a + c, 0)} of 16 steps on)`)
await pg.evaluate(() => { const e = document.getElementById('sqon'); e.checked = true; e.dispatchEvent(new Event('change', { bubbles: true })) })
await pg.evaluate(() => window.PhosphorTest.seek(0)); await pg.click('#play'); await pg.waitForTimeout(2200); await pg.click('#play'); await pg.waitForTimeout(300)
const text = await pg.evaluate(() => window.PhosphorTest.recipe.exp()), head = text.split('\n')[0], rec = JSON.parse(text.split('\n').slice(1).join('\n'))
const without = head + '\n' + JSON.stringify({ base: rec.base, events: rec.events.map((e) => e[2] === '@cells' ? [e[0], e[1], e[2], Object.fromEntries(Object.entries(e[3]).map(([k, v]) => [k, v.map(() => 0)]))] : e) })
const diff = await pg.evaluate(async ([a, c]) => { const x = await window.PhosphorTest.recipe.render(a), y = await window.PhosphorTest.recipe.render(c); let s = 0, e = 0; const n = Math.min(x.l.length, y.l.length); for (let i = 0; i < n; i++) { s += (x.l[i] - y.l[i]) ** 2; e += x.l[i] ** 2 + 1e-12 } return { rel: Math.sqrt(s / e), n } }, [text, without])
check(diff.rel > 0.2, `S2: the render with the pattern differs clearly from the same render with every cell empty (relative difference ${diff.rel.toFixed(3)}, want over 0.2)`)
// S3 deterministic
const h = await pg.evaluate(async (a) => { const x = await window.PhosphorTest.recipe.render(a), y = await window.PhosphorTest.recipe.render(a); let d = 0; for (let i = 0; i < x.l.length; i++) d += Math.abs(x.l[i] - y.l[i]); return d }, text)
check(h === 0, `S3: two renders with the pattern are identical (total difference ${h})`)
check(errs.length === 0, 'S4: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
