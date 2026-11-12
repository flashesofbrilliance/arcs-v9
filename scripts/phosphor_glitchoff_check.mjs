#!/usr/bin/env node
// phosphor_glitchoff_check.mjs: O1 to O8 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (amendment 31, the Glitch master switch).
// Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_glitchoff_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const { chromium, devices } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2], file = (process.env.PHOSPHOR_FILES || '').split(',')[0]
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_glitchoff_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), base = pathToFileURL(path.resolve(page)).href, errs = []
const open = async (q, extra = {}) => { const ctx = await b.newContext({ viewport: { width: 1270, height: 990 }, ...extra }), pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + q); await pg.waitForTimeout(1000); await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.getElementById('src').textContent !== 'Demo signal', null, { timeout: 60000 }); return pg }
let pg = await open('?test=1&shutter=off&level=4'); const KINDS = ['stutter', 'freeze', 'tear', 'rgb', 'blocks', 'crush', 'dist', 'gate']
const state = () => pg.evaluate(() => { const g = window.PhosphorTest.glitch(); return { stut: g.stut ? g.stut.kind : null, on: g.on } })
const anyOn = (s) => !!s.stut || ['tear', 'rgb', 'blocks', 'crush', 'dist', 'gate'].some((k) => s.on[k])
await pg.click('#play'); await pg.waitForTimeout(500)
// some running first, then off
for (const k of ['tear', 'crush', 'rgb']) await pg.evaluate((k) => window.PhosphorTest.hold.on(k, 'latch', true), k); await pg.evaluate(() => window.PhosphorTest.hold.on('stutter', 'latch', true)); await pg.waitForTimeout(200)
const before = await state(); check(before.on.tear && before.on.crush && before.on.rgb && before.stut === 'stutter', 'O2: before the switch, Tear, Crush, Split and Stutter are running')
await pg.click('#glitchsw'); await pg.waitForTimeout(250); const after = await state(), who = await pg.evaluate(() => Object.keys(window.PhosphorTest.hold.who()).filter((k) => ['stutter', 'freeze', 'tear', 'rgb', 'blocks', 'crush', 'dist', 'gate'].includes(k)))
check(!after.on.tear && !after.on.crush && !after.on.rgb && after.stut === null && who.length === 0 && (await pg.getAttribute('#glitchsw', 'aria-pressed')) === 'false', `O2: turning Glitch off released them all and cleared their holders (${who.length} held)`)
// O1 every kind blocked
const blocked = []; for (const k of KINDS) { await pg.evaluate((k) => window.PhosphorTest.hold.on(k, 'key:x', true), k); await pg.waitForTimeout(80); const s = await state(); if (anyOn(s)) blocked.push(k); await pg.evaluate((k) => window.PhosphorTest.hold.on(k, 'key:x', false), k) }
check(blocked.length === 0, `O1: with Glitch off none of the eight kinds can start from a held source${blocked.length ? ' (started: ' + blocked.join(', ') + ')' : ''}`)
const wetNow = await pg.evaluate(() => window.PhosphorTest.fx.wet('crush')); check(!wetNow || wetNow.wet < 0.02, 'O1: the Crush effect stage stayed dry')
// O4 other effects still work
await pg.evaluate(() => { for (const k of ['echo', 'room', 'shim', 'sweep']) window.PhosphorTest.hold.on(k, 'latch', true) }); await pg.waitForTimeout(150); const fx = await pg.evaluate(() => window.PhosphorTest.glitch().on); check(fx.echo && fx.room && fx.shim && fx.sweep, 'O4: Echo, Room, Shimmer and Sweep still work with Glitch off'); await pg.evaluate(() => { for (const k of ['echo', 'room', 'shim', 'sweep']) window.PhosphorTest.hold.on(k, 'latch', false) })
// O5 wobble
await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(150); const kb = await pg.locator('#kwob').boundingBox(); await pg.mouse.move(kb.x + kb.width / 2, kb.y + kb.height / 2); await pg.mouse.down(); await pg.waitForTimeout(200); const wob = await state(); await pg.mouse.up()
check(!wob.on.rgb && !wob.on.blocks, 'O5: the Kid Wobble button does nothing while Glitch is off')
// O6 sequencer lane
await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); await pg.evaluate(() => { const T = window.PhosphorTest; T.seq.clear(); for (let i = 0; i < 16; i++) T.seq.set('tear', i, 1); T.seq.on(true) }); await pg.waitForTimeout(900); const sq = await state(); check(!sq.on.tear, 'O6: a full Tear lane in the sequencer does nothing while Glitch is off')
// O3 / O6 back on: sequencer works, latched ones do not return
await pg.click('#glitchsw'); for (let i = 0; i < 16 && !(await state()).on.tear; i++) await pg.waitForTimeout(500); // up to 8 s: the sequencer ticks on animation frames, which starve under load (2026-10-18: 1 in 5 failed at 3 s on a loaded machine with nothing latched back) const back = await state(); check(back.on.tear === true && !back.on.crush && !back.on.rgb && back.stut === null, 'O3: with Glitch back on the sequenced Tear works again and the old latched Crush, Split and Stutter did not come back'); await pg.evaluate(() => window.PhosphorTest.seq.on(false))
// O7 reload
await pg.click('#glitchsw'); await pg.waitForTimeout(600); await pg.reload(); await pg.waitForTimeout(1500); check((await pg.getAttribute('#glitchsw', 'aria-pressed')) === 'false' && /off/.test(await pg.textContent('#glitchsw')), 'O7: the Glitch off choice survives a reload')
await pg.context().close()
// O8 phone
pg = await open('?shutter=off', { ...devices['iPhone 13'] }); const sz = await pg.evaluate(() => { const r = document.getElementById('glitchsw').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), document.documentElement.scrollWidth > innerWidth] })
check(sz[1] >= 48 && sz[0] >= 48 && !sz[2], `O8: on a phone the switch is ${sz[0]} by ${sz[1]} px and the header does not scroll sideways`)
check(errs.length === 0, `O8: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(failed() ? 1 : 0)
