#!/usr/bin/env node
// phosphor_cue_check.mjs: Q1, Q3 to Q6 (amendment 58): the CDJ-style cue.
// Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_cue_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_cue_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForTimeout(1200); await pg.setInputFiles('#file', file)
await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 })
const T = (fn, a) => pg.evaluate(fn, a), bpm = await T(() => window.PhosphorTest.bpm()), bar = 4 * 60 / bpm
await T(() => window.PhosphorTest.seek(3.3)); await pg.waitForTimeout(200)
await T(() => window.PhosphorTest.cue.down()); await T(() => window.PhosphorTest.cue.up())
const c1 = await T(() => window.PhosphorTest.cue.t()), g0 = await T(() => window.PhosphorTest.tnow())
check(c1 !== null && Math.abs(c1 - 3.3) <= bar / 2 + 0.01 && Math.abs(g0 - c1) < 0.01, `Q1: pressing Cue while paused sets the cue at ${c1 && c1.toFixed(3)} s, within half a bar (${(bar / 2).toFixed(2)} s) of the playhead, and parks there`)
await T(() => window.PhosphorTest.cue.down()); await pg.waitForTimeout(900)
const hp = await T(() => ({ t: window.PhosphorTest.tnow(), playing: document.getElementById('play').textContent === 'Pause', prev: window.PhosphorTest.cue.prev() }))
check(hp.playing && hp.prev && hp.t > c1 + 0.3, `Q3: holding Cue at the cue plays from it (${hp.t.toFixed(2)} s after ${(0.9).toFixed(1)} s held)`)
await T(() => window.PhosphorTest.cue.up()); await pg.waitForTimeout(150)
const rp = await T(() => ({ t: window.PhosphorTest.tnow(), playing: document.getElementById('play').textContent === 'Pause' }))
check(!rp.playing && Math.abs(rp.t - c1) < 0.01, `Q4: letting go stops and returns to the cue (${rp.t.toFixed(3)} s)`)
await T((t) => window.PhosphorTest.seek(t), c1 + 5); await pg.waitForTimeout(100); await T(() => window.PhosphorTest.cue.down()); await T(() => window.PhosphorTest.cue.up())
const c2 = await T(() => window.PhosphorTest.cue.t())
check(c2 > c1 + 1, `Q5: moving away and pressing again sets a new cue (${c2.toFixed(3)} s)`)
check(errs.length === 0, 'Q6: no page errors' + (errs.length ? ': ' + errs[0] : ''))
await b.close(); process.exit(failed() ? 1 : 0)
