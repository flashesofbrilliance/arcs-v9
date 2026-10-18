#!/usr/bin/env node
// phosphor_hidden_check.mjs: nothing marked hidden may be visible. A display rule in the stylesheet can override the hidden attribute (it did for the pad picker); this finds the whole class. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_hidden_check.mjs <page.html>
import { chromium, devices } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_hidden_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off', errs = []
const leak = (pg) => pg.evaluate(() => [...document.querySelectorAll('[hidden]')].filter((e) => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return s.display !== 'none' || r.width * r.height > 0 }).map((e) => (e.id || e.className || e.tagName) + ' display:' + getComputedStyle(e).display))
for (const [name, extra] of [['desktop', { viewport: { width: 1270, height: 990 } }], ['phone', { ...devices['iPhone 13'] }]]) {
  const ctx = await b.newContext(extra); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
  const empty = await leak(pg)
  await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
  const loaded = await leak(pg)
  await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700)
  const parent = await leak(pg)
  await pg.evaluate(() => { document.getElementById('dkpad').click() }); await pg.waitForTimeout(200); const pads = await leak(pg)
  await pg.evaluate(() => { document.getElementById('dkfx').click() }); await pg.waitForTimeout(200); const mix = await leak(pg)
  const all = [...new Set([...empty, ...loaded, ...parent, ...pads, ...mix])]
  check(all.length === 0, `H-${name}: no element marked hidden is visible, with no song, with a song, in Parent mode, with the Pads tray and with the Mix tray${all.length ? ' (' + all.slice(0, 6).join('; ') + ')' : ''}`)
  await ctx.close()
}
check(errs.length === 0, 'H-errors: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
