#!/usr/bin/env node
// phosphor_poly_check.mjs: the effect toggles are polyphonic, not mono. Any source (a pad press, a key, a latch,
// the sequencer, wobble) can hold an effect; it stays on until the LAST holder lets go. Latch an effect, hold others
// on top, release them, and the latched one keeps going. Stutter and Freeze share one loop: newest wins, the older
// one returns when it ends. Usage: node scripts/phosphor_poly_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const require = createRequire(import.meta.url + '/../../../package.json'.replace('file://', ''))
let chromium; try { ({ chromium } = require('playwright')) } catch { ({ chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')) }
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_poly_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), pg = await b.newPage({ viewport: { width: 1280, height: 900 } })
const errs = []; pg.on('pageerror', (e) => errs.push(String(e)))
await pg.goto(pathToFileURL(page).href + '?test=1&shutter=off'); await pg.waitForTimeout(1500)
await pg.evaluate(() => { const g = document.getElementById('glatch'); for (let e = g.parentElement; e; e = e.parentElement) if (e.tagName === 'DETAILS') e.open = true })
const on = () => pg.evaluate(() => window.PhosphorTest.glitch().on)
const stut = () => pg.evaluate(() => { const s = window.PhosphorTest.glitch().stut; return s ? s.kind : null })
const H = (fn, ...a) => pg.evaluate(([fn, a]) => window.PhosphorTest.hold[fn](...a), [fn, a])
// P1 latch two, hold a third on top, release it: the first two stay
await H('latch', true); await H('toggle', 'echo', 'latch'); await H('toggle', 'crush', 'latch')
let s = await on(); check(s.echo && s.crush, 'P1: latch Echo and Crush, both are on')
await H('on', 'sweep', 'key:x', true); s = await on(); check(s.echo && s.crush && s.sweep, 'P1: hold Sweep on top, all three are on')
await H('on', 'sweep', 'key:x', false); s = await on(); check(s.echo && s.crush && !s.sweep, 'P1: let go of Sweep, Echo and Crush keep going')
// P2 the same effect from two sources stays on until the last one lets go
await H('on', 'echo', 'ptr:echo', true); await H('on', 'echo', 'ptr:echo', false); s = await on(); check(s.echo, 'P2: hold Echo while it is latched, release the hold, it stays on')
await H('toggle', 'echo', 'latch'); s = await on(); check(!s.echo && s.crush, 'P2: unlatch Echo, only Echo goes off')
await H('toggle', 'crush', 'latch'); s = await on(); check(!s.crush, 'P2: unlatch Crush, nothing is left on')
// P3 two momentary sources for one effect
await H('on', 'tear', 'key:c', true); await H('on', 'tear', 'ptr:tear', true); await H('on', 'tear', 'key:c', false)
s = await on(); check(s.tear, 'P3: key and pad both hold Tear, release the key, Tear stays on'); await H('on', 'tear', 'ptr:tear', false); s = await on(); check(!s.tear, 'P3: release the pad, Tear goes off')
// P4 Stutter and Freeze: newest wins, the older returns
await H('on', 'stutter', 'key:z', true); check((await stut()) === 'stutter', 'P4: hold Stutter')
await H('on', 'freeze', 'key:x', true); check((await stut()) === 'freeze', 'P4: hold Freeze on top, Freeze takes the loop')
await H('on', 'freeze', 'key:x', false); check((await stut()) === 'stutter', 'P4: release Freeze, Stutter comes back')
await H('on', 'stutter', 'key:z', false); check((await stut()) === null, 'P4: release Stutter, the loop ends')
// P5 sequencer and a latched effect do not fight
await H('toggle', 'dist', 'latch'); await H('on', 'dist', 'seq', true); await H('on', 'dist', 'seq', false); s = await on(); check(s.dist, 'P5: the sequencer lets go of Distort, the latched Distort stays on'); await H('toggle', 'dist', 'latch')
// P6 real pointer: Latch button, then pads
await pg.evaluate(() => window.PhosphorTest.hold.latch(false))
const pad = (k) => pg.locator(`#gpads [data-g=${k}]`)
await pg.evaluate(() => document.getElementById('glatch').scrollIntoView({ block: 'center' }))
await pg.click('#glatch'); check((await pg.getAttribute('#glatch', 'aria-pressed')) === 'true', 'P6: the Latch button turns latch on')
await pad('echo').click(); await pad('crush').click(); s = await on()
check(s.echo && s.crush && (await pad('echo').getAttribute('aria-pressed')) === 'true' && (await pad('crush').getAttribute('aria-pressed')) === 'true', 'P6: tap Echo then Crush with a mouse, both stay on and both pads show pressed')
await pg.click('#glatch'); const bb = await pad('sweep').boundingBox(); await pg.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2); await pg.mouse.down()
s = await on(); check(s.echo && s.crush && s.sweep, 'P6: latch off, press and hold Sweep, all three are on')
await pg.mouse.up(); s = await on(); check(s.echo && s.crush && !s.sweep, 'P6: let go of Sweep, Echo and Crush keep going')
// P7 window blur lets go of what you are holding but not what you latched
await pg.click('#glatch'); await pad('tear').click(); await pg.click('#glatch'); await H('on', 'blocks', 'key:b', true)
await pg.evaluate(() => window.dispatchEvent(new Event('blur'))); s = await on(); check(s.tear && !s.blocks && s.echo, 'P7: blur lets go of a held Blocks, latched Tear and Echo stay')
// P8 leaving Perform clears everything
await pg.evaluate(() => { document.getElementById('perf').checked = true; document.getElementById('perf').dispatchEvent(new Event('change', { bubbles: true })) })
await pg.evaluate(() => { document.getElementById('perf').checked = false; document.getElementById('perf').dispatchEvent(new Event('change', { bubbles: true })) }); s = await on()
check(!s.echo && !s.crush && !s.tear, 'P8: turning Perform off clears every effect')
check(errs.length === 0, `P9: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
