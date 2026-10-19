#!/usr/bin/env node
// phosphor_measure.mjs: measure the page as a person meets it (visible controls, font sizes, radii, tap targets, inline styles, duplicate ids) per mode, viewport and open tray. Read only; prints JSON. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_measure.mjs <page.html> [out.json]
import { chromium, devices } from 'playwright'
import { writeFileSync } from 'node:fs'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const page = process.argv[2], out = process.argv[3], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_measure.mjs <page.html> [out.json]'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?shutter=off'
const probe = () => {
  const vis = (e) => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[inert]') && !e.closest('[aria-hidden=true]') }
  const ctl = [...document.querySelectorAll('button, input:not([type=radio]):not([type=checkbox]), input[type=radio]:checked, input[type=checkbox], select, summary, textarea, a[href], [role=button]')].filter(vis).filter((e) => !(e.type === 'radio' && !e.checked))
  const all = [...document.querySelectorAll('body *')].filter(vis), sizes = {}, radii = {}, gaps = {}
  all.forEach((e) => { const s = getComputedStyle(e); const own = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()); if (own) sizes[s.fontSize] = (sizes[s.fontSize] || 0) + 1; if (s.borderRadius !== '0px') radii[s.borderRadius] = (radii[s.borderRadius] || 0) + 1; if (s.gap && s.gap !== 'normal') gaps[s.gap] = (gaps[s.gap] || 0) + 1 })
  const small = ctl.filter((e) => { const r = e.getBoundingClientRect(); return (r.height < 44 || r.width < 44) && !['radio', 'checkbox'].includes(e.type) }).map((e) => (e.id || e.className || e.tagName) + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height))
  const ids = [...document.querySelectorAll('[id]')].map((e) => e.id), dup = ids.filter((x, i) => ids.indexOf(x) !== i)
  return { controls: ctl.length, byTag: ctl.reduce((m, e) => { const k = e.tagName.toLowerCase() + (e.type ? ':' + e.type : ''); m[k] = (m[k] || 0) + 1; return m }, {}), fontSizes: sizes, radii, gaps, smallTargets: small.length, smallSample: small.slice(0, 8), inlineStyleVisible: all.filter((e) => e.getAttribute('style')).length, duplicateIds: [...new Set(dup)] }
}
const res = {}
for (const [vp, extra] of [['desktop', { viewport: { width: 1270, height: 990 } }], ['phone', { ...devices['iPhone 13'] }]]) {
  const ctx = await b.newContext(extra); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
  const pg = await ctx.newPage(); await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500)
  for (const mode of ['kid', 'parent']) {
    if (mode === 'kid') await pg.evaluate(() => document.getElementById('mdKid').click()); else { await pg.evaluate(() => document.getElementById('mdParent').dispatchEvent(new PointerEvent('pointerdown'))); await pg.waitForTimeout(1700) }
    await pg.waitForTimeout(300); res[`${vp}/${mode}/base`] = await pg.evaluate(probe)
    await pg.evaluate(() => document.getElementById('dkpad').click()); await pg.waitForTimeout(200); res[`${vp}/${mode}/pads`] = await pg.evaluate(probe); await pg.evaluate(() => document.getElementById('dkpad').click())
    if (mode === 'parent') { await pg.evaluate(() => document.getElementById('dkfx').click()); await pg.waitForTimeout(200); res[`${vp}/parent/mix`] = await pg.evaluate(probe); await pg.evaluate(() => document.getElementById('dkfx').click()); await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true)); await pg.waitForTimeout(300); res[`${vp}/parent/all-open`] = await pg.evaluate(probe) }
  }
  await ctx.close()
}
const tpl = (await import('node:fs')).readFileSync(path.resolve('_ARTIFACTS/phosphor-src/page.tpl'), 'utf8'), css = (await import('node:fs')).readFileSync(path.resolve('_ARTIFACTS/phosphor-src/style.css'), 'utf8')
res.source = { inlineStyleAttrsInTemplate: (tpl.match(/ style="/g) || []).length, distinctFontSizeDeclarations: [...new Set((css.match(/font-size:\s*[^;]+/g) || []).map((s) => s.replace(/\s+/g, ' ')))].length, distinctRadiusDeclarations: [...new Set((css.match(/border-radius:\s*[^;]+/g) || []).map((s) => s.replace(/\s+/g, ' ')))].length, cssBytes: css.length }
if (out) writeFileSync(out, JSON.stringify(res, null, 1)); await b.close()
for (const [k, v] of Object.entries(res)) { if (k === 'source') { console.log('source', JSON.stringify(v)); continue } console.log(k.padEnd(22), 'controls', String(v.controls).padStart(3), '| sizes', Object.keys(v.fontSizes).length, '| radii', Object.keys(v.radii).length, '| small', v.smallTargets, '| inline', v.inlineStyleVisible, '| dupIds', v.duplicateIds.length) }
