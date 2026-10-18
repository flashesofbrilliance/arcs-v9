#!/usr/bin/env node
// phosphor_kidcap_check.mjs: Kid mode shows at most 24 controls at rest (amendment 51); the grown-up controls come back in Parent mode; a preset button taps back to Plain. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_kidcap_check.mjs <page.html>
import { chromium, devices } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_kidcap_check.mjs <page.html>'); process.exit(2) }
import { check, failed } from './lib/phosphor_check_lib.mjs'
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?shutter=off', errs = []
const count = (pg) => pg.evaluate(() => { const vis = (e) => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[inert]') && !e.closest('[aria-hidden=true]') }; const l = [...document.querySelectorAll('button, input:not([type=radio]):not([type=checkbox]), input[type=radio]:checked, input[type=checkbox], select, summary, textarea, a[href]')].filter(vis); return { n: l.length, ids: l.map((e) => e.id).filter(Boolean) } })
for (const [name, extra] of [['desktop', { viewport: { width: 1270, height: 990 } }], ['phone', { ...devices['iPhone 13'] }]]) {
  const ctx = await b.newContext(extra); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} }); const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e)))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
  await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300); const kid = await count(pg)
  check(kid.n <= 24, `K1-${name}: Kid mode at rest shows ${kid.n} controls (at most 24)`)
  const gone = ['skinb', 'zin', 'zout', 'fsb', 'dkhide'].filter((id) => kid.ids.includes(id))
  check(gone.length === 0, `K2-${name}: the moved controls are not in Kid mode (still there: ${gone.join(',') || 'none'})`)
  await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700); const par = await count(pg)
  const back = ['skinb', 'zin', 'zout', 'fsb', 'dkhide'].filter((id) => !par.ids.includes(id))
  check(back.length === 0 && par.n > kid.n, `K3-${name}: every moved control is back in Parent mode (missing: ${back.join(',') || 'none'}; ${par.n} controls)`)
  if (name === 'desktop') {
    await pg.evaluate(() => document.getElementById('mdKid').click()); await pg.waitForTimeout(300)
    const sig = () => pg.evaluate(() => [document.getElementById('palsel').value, document.getElementById('res').value, document.getElementById('rloop').checked].join('|'))
    const s0 = await sig(); await pg.evaluate(() => document.querySelector('[data-pre=party]').click()); const s1 = await sig(); await pg.evaluate(() => document.querySelector('[data-pre=party]').click()); const s2 = await sig()
    const pressed = await pg.evaluate(() => document.querySelector('[data-pre=party]').getAttribute('aria-pressed'))
    check(s1 !== s0 && s2 === s0 && pressed === 'false', `K4: tapping a preset again returns to Plain (${s0} to ${s1} to ${s2}; pressed ${pressed})`)
  }
  await ctx.close()
}
check(errs.length === 0, 'K5: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
