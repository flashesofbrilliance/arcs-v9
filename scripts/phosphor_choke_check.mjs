#!/usr/bin/env node
// phosphor_choke_check.mjs: pad mute and choke groups (amendment 67). Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_choke_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_choke_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const url = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'
const open = async () => { const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true)); await pg.click('#dkpad'); await pg.waitForTimeout(200); return pg }
const ev = (pg, f, a) => pg.evaluate(f, a)
const down = (pg, k) => pg.evaluate((k) => document.querySelector(`[data-pk="${k}"]`).dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true })), k)
const up = (pg, k) => pg.evaluate((k) => document.querySelector(`[data-pk="${k}"]`).dispatchEvent(new PointerEvent('pointerup', { bubbles: true, cancelable: true })), k)
const live = (pg) => pg.evaluate(() => window.PhosphorTest.pads.live().sort((a, c) => a - c))
const logN = (pg) => pg.evaluate(() => window.PhosphorTest.pads.log().length)
let pg = await open()
await down(pg, 5); await up(pg, 5); await pg.waitForTimeout(200) // chops the song into 16 parts
await pg.evaluate(() => document.getElementById('padedit').click())
const pick = async (k, sel) => { await down(pg, k); await pg.waitForTimeout(60); await pg.evaluate((s) => document.querySelector(s).click(), sel) }
await pick(0, '#padgm [data-g="1"]'); await pick(1, '#padgm [data-g="1"]'); await pick(2, '#padgm [data-g="2"]'); await pick(3, '#padpick [data-fx="echo"]'); await pick(3, '#padgm [data-g="1"]'); await pick(4, '#padmute')
const labels = await pg.evaluate(() => [0, 1, 2, 3, 4].map((k) => document.querySelector(`[data-pk="${k}"] small`).textContent))
await pg.reload(); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true)); await pg.click('#dkpad'); await pg.waitForTimeout(200)
const labels2 = await pg.evaluate(() => [0, 1, 2, 3, 4].map((k) => document.querySelector(`[data-pk="${k}"] small`).textContent))
check(labels.join() === labels2.join() && labels2[0].includes('G1') && labels2[2].includes('G2') && labels2[3].includes('Echo') && labels2[3].includes('G1') && labels2[4].includes('off'), `M1: group and mute choices show on the pads and survive a reload (${labels2.join(' | ')})`)
await down(pg, 5); await up(pg, 5); await pg.waitForTimeout(200)
// M2 a muted pad adds no voice and no log entry, and says so
const n0 = await logN(pg), v0 = await pg.evaluate(() => window.PhosphorTest.pads.live().length); await down(pg, 4); await pg.waitForTimeout(150)
check((await logN(pg)) === n0 && (await live(pg)).length === v0 && /muted/.test(await pg.textContent('#padmsg')), `M2: a muted pad adds no voice and no log entry, and says it is muted (${await pg.textContent('#padmsg')})`)
// M3 choke inside a group, other group untouched
await down(pg, 0); await pg.waitForTimeout(80); await down(pg, 1); await pg.waitForTimeout(80); const a1 = await live(pg); await down(pg, 2); await pg.waitForTimeout(60); const a2 = await live(pg); await down(pg, 0); await pg.waitForTimeout(60); const a3 = await live(pg)
check(a1.includes(1) && !a1.includes(0), `M3a: hitting pad 2 (group 1) cuts pad 1 of its group (live ${a1.join(',')})`)
check(a2.includes(1) && a2.includes(2) && a3.includes(0) && a3.includes(2) && !a3.includes(1), `M3b: pad 3 (group 2) is not cut by group 1, and hitting pad 1 again cuts pad 2 (live now ${a3.join(',')})`)
// M4 an effect pad in the group is released by a slice hit of the group
await down(pg, 3); await pg.waitForTimeout(150); const on = (await pg.evaluate(() => window.PhosphorTest.glitch().on)).echo; await down(pg, 1); await pg.waitForTimeout(150); const off = (await pg.evaluate(() => window.PhosphorTest.glitch().on)).echo
check(on === true && off === false, `M4: Echo held on a group pad (${on}) is released when another pad of the group is hit (${off})`)
await up(pg, 3)
// M5 the render applies the cuts
const render = (text) => pg.evaluate(async (t) => { const o = await window.PhosphorTest.recipe.render(t); return { n: o.l.length, l: Array.from(o.l.filter((_, i) => i % 3 === 0)) } }, text)
await down(pg, 0); await pg.waitForTimeout(120); await down(pg, 1); await pg.waitForTimeout(900)
const text = await pg.evaluate(() => window.PhosphorTest.recipe.exp()), rA = await render(text)
await pg.evaluate(() => { const m = JSON.parse(localStorage.getItem('phosphor.padgm.v1')); m.grp = {}; localStorage.setItem('phosphor.padgm.v1', JSON.stringify(m)) })
const rB = await render(text); let d = 0, e = 0; const n = Math.min(rA.l.length, rB.l.length); for (let i = 0; i < n; i++) { d += (rA.l[i] - rB.l[i]) ** 2; e += rB.l[i] ** 2 + 1e-12 }
check(Math.sqrt(d / e) > 0.05, `M5: the render of the same two hits differs with and without the group (relative difference ${Math.sqrt(d / e).toFixed(3)}, want over 0.05)`)
check(errs.length === 0, 'M7: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
