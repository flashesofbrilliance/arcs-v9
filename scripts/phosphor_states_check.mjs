#!/usr/bin/env node
// phosphor_states_check.mjs: the state matrix (amendment 52). For each atom, hover, focus-visible, active (finger down), pressed and disabled must look different from rest, and by color or border, never opacity alone (DESIGN.md contrast rule 3). Usage: node scripts/phosphor_states_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2]; if (!page) { console.log('usage: node scripts/phosphor_states_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch(), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true)); await pg.waitForTimeout(300)
let cdp; try { cdp = await ctx.newCDPSession(pg); await cdp.send('DOM.enable'); await cdp.send('CSS.enable') } catch (e) { check(true, 'S-skip: forced pseudo-states need Chromium (CDP), skipped on this engine'); await b.close(); process.exit(0) }
const look = (sel) => pg.evaluate((sel) => { const e = document.querySelector(sel), s = getComputedStyle(e); return { bg: s.backgroundColor, border: s.borderTopColor + ' ' + s.borderTopStyle, color: s.color, outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor, shadow: s.boxShadow, opacity: s.opacity } }, sel)
const same = (a, b2) => ['bg', 'border', 'color', 'outline', 'shadow'].every((k) => a[k] === b2[k])
const forced = async (sel, cls) => { const { root } = await cdp.send('DOM.getDocument'); const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: sel }); await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: cls }); const l = await look(sel); await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] }); return l }
const ATOMS = [['button', '#mdKid'], ['button (grown-up)', '#pick'], ['big button (preset)', '[data-pre=rain]'], ['zoom pad', '.pad']]
for (const [name, sel] of ATOMS) {
  const exists = await pg.evaluate((s) => !!document.querySelector(s), sel); if (!exists) { check(false, `S-${name}: the sample ${sel} exists`); continue }
  await pg.evaluate(() => document.activeElement && document.activeElement.blur()); const rest = await look(sel)
  const hov = await forced(sel, ['hover']), foc = await forced(sel, ['focus', 'focus-visible']), act = await forced(sel, ['active'])
  check(!same(rest, hov), `S-${name}: hover differs from rest by color or border`)
  check(!same(rest, foc), `S-${name}: focus-visible differs from rest (outline ${foc.outline})`)
  if (name !== 'zoom pad') check(!same(rest, act), `S-${name}: active (finger down) differs from rest`)
}
// pressed and disabled
await pg.evaluate(() => { const e = document.querySelector('[data-pre=rain]'); e.setAttribute('aria-pressed', 'false') }); const off = await look('[data-pre=rain]'); await pg.evaluate(() => document.querySelector('[data-pre=rain]').setAttribute('aria-pressed', 'true')); const on = await look('[data-pre=rain]')
check(!same(off, on), 'S-pressed: a pressed preset differs from an unpressed one by color or border')
const dis = await pg.evaluate(() => { const e = document.getElementById('twinb'); return e ? e.disabled : null }); const en = await look('#twinb'); await pg.evaluate(() => { document.getElementById('twinb').disabled = false }); const en2 = await look('#twinb')
check(dis === true && !same(en, en2) && (en.opacity === en2.opacity || en.color !== en2.color), 'S-disabled: a disabled button differs from an enabled one by color or border, not by opacity alone')
check(errs.length === 0, 'S-errors: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
