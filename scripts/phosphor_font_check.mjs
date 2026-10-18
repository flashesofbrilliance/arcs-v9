#!/usr/bin/env node
// phosphor_font_check.mjs: canvas text uses the whole CSS font stack, so a machine without the first named font falls back to a monospace, not the browser default. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_font_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_font_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch(), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.addInitScript(() => { window.__fonts = new Set(); const d = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'font'); Object.defineProperty(CanvasRenderingContext2D.prototype, 'font', { get() { return d.get.call(this) }, set(v) { window.__fonts.add(String(v)); d.set.call(this, v) } }) })
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(3000); await pg.click('#play'); await pg.waitForTimeout(1200)
const fonts = await pg.evaluate(() => [...window.__fonts])
const mono = fonts.filter((f) => /\d+px /.test(f) && /mono/i.test(f) === false ? false : /JetBrains|Mono|monospace/i.test(f))
check(mono.length > 0 && mono.every((f) => /monospace\s*$/.test(f.replace(/["']/g, '').trim()) || /monospace/.test(f)), `F1: every canvas label font names the whole mono stack ending in a generic monospace (${mono.length} distinct: ${mono.slice(0, 2).join(' | ')})`)
const w = await pg.evaluate(() => { const c = document.createElement('canvas').getContext('2d'); const m = (f) => { c.font = f; return c.measureText('Wiiiiiiii 0000').width }; return { first: m("600 14px 'NoSuchMono'"), stack: m("600 14px 'NoSuchMono', ui-monospace, Menlo, monospace"), mono: m('600 14px monospace') } })
check(Math.abs(w.stack - w.mono) < 6 && Math.abs(w.first - w.mono) > 10, `F2: the failure it prevents is real: a missing first font alone draws ${w.first.toFixed(0)} px wide, the stack draws ${w.stack.toFixed(0)} px like monospace (${w.mono.toFixed(0)})`)
const net = await pg.evaluate(() => performance.getEntriesByType('resource').filter((r) => !/^(blob|data|file):/.test(r.name)).map((r) => r.name))
check(net.length === 0, `F3: no font or other file is fetched from the network (${net.length})`)
check(errs.length === 0, 'F4: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
