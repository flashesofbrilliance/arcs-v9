#!/usr/bin/env node
// phosphor_zoomrow_check.mjs: the Zoom in / Zoom out buttons under the strip work, and the frame's own zoom buttons do not move the strip. Found by the static review (two elements shared the ids zin and zout, so the strip buttons were dead).
// Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_zoomrow_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_zoomrow_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch(), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
await pg.evaluate(() => { let e = document.getElementById('zoomrow'); while (e) { if (e.tagName === 'DETAILS') e.open = true; e = e.parentElement } })
const span = () => pg.evaluate(() => { const v = window.PhosphorTest.view(); return (v.b || window.PhosphorTest.dur()) - v.a })
const ids = await pg.evaluate(() => [...document.querySelectorAll('[id]')].map((e) => e.id)), dup = ids.filter((x, i) => ids.indexOf(x) !== i)
check(dup.length === 0, 'Z1: no id appears twice on the page ' + dup.join(','))
const s0 = await span(); await pg.locator('#zoomrow button').nth(1).click(); await pg.waitForTimeout(150); const s1 = await span()
check(s1 < s0 * 0.7, `Z2: the strip's Zoom in narrows the view (${s0.toFixed(1)} s to ${s1.toFixed(1)} s)`)
await pg.locator('#zoomrow button').nth(0).click(); await pg.waitForTimeout(150); const s2 = await span()
check(s2 > s1 * 1.5, `Z3: the strip's Zoom out widens it again (${s1.toFixed(1)} s to ${s2.toFixed(1)} s)`)
await pg.evaluate(() => document.getElementById('zin').click()); await pg.waitForTimeout(150); const s3 = await span()
check(Math.abs(s3 - s2) < 0.01, `Z4: the frame's own zoom button leaves the strip view alone (${s2.toFixed(1)} s, ${s3.toFixed(1)} s)`)
check(errs.length === 0, 'Z5: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
