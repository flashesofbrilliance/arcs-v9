#!/usr/bin/env node
// phosphor_guard_check.mjs: G1 to G3 from _PATTERNS/2026-10-15-kid-play-surface-pattern.md. Flash rate, loudness, no push features.
// Usage: node scripts/phosphor_guard_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'

const page = process.argv[2]
if (!page) { console.error('usage: phosphor_guard_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }

// a loud full-scale 220 Hz square, 12 s, 22.05 kHz, for the loudness check; and the quieter click track for the picture scenarios
function wavOf(name, f) { const sr = 22050, n = sr * 12, b = Buffer.alloc(44 + n * 2); b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40); for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(Math.max(-1, Math.min(1, f(i / sr))) * 32767), 44 + i * 2); const p = path.join(os.tmpdir(), name); fs.writeFileSync(p, b); return p }
const loud = wavOf('phosphor-loud.wav', (t) => (Math.sin(2 * Math.PI * 220 * t) >= 0 ? 1 : -1))
const click = wavOf('phosphor-guard-click.wav', (t) => { const k = (t - 0.3) % 0.5; return (t >= 0.3 ? Math.exp(-k * 18) * Math.sin(2 * Math.PI * (60 + 90 * Math.exp(-k * 30)) * k) * 0.9 : 0) + 0.3 * Math.sin(2 * Math.PI * 880 * t) * (Math.floor(t * 4) % 2) })

const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = [], reqs = []
async function open(file) {
  const pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
  await pg.addInitScript(() => document.addEventListener('DOMContentLoaded', () => { const g = document.getElementById('grown'); if (g) g.open = true }))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0)
  if (process.env.SHUTTER !== 'off') await pg.evaluate(() => window.PhosphorTest.shutter && window.PhosphorTest.shutter(true))
  await pg.setInputFiles('#file', file); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 60000 })
  return pg
}
let SW = 0.1, LIM = 3 // read from the page's motion tokens (--mo-lum-swing, --mo-flash-max) once it is open
// G1 ---------------------------------------------------------------
const pg = await open(click)
{ const mo = await pg.evaluate(() => window.PhosphorTest.mo); SW = mo.swing; LIM = mo.flash }
const sampler = `(ms) => new Promise((res) => { const cv = document.getElementById('cv'), s = document.createElement('canvas'); s.width = 32; s.height = 16; const g = s.getContext('2d', { willReadFrequently: true }), out = [], t0 = performance.now(); const fc = document.createElement('canvas'); fc.width = 96; fc.height = 54; const fg = fc.getContext('2d', { willReadFrequently: true }); let prevF = null; window.__jit = [];
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4) };
  (function tick() { const now = performance.now(); g.drawImage(cv, 0, 0, 32, 16); const d = g.getImageData(0, 0, 32, 16).data; let sum = 0; const reg = new Array(16).fill(0); for (let y = 0; y < 16; y++) for (let x = 0; x < 32; x++) { const i = (y * 32 + x) * 4, L = 0.2126 * lin(d[i]) + 0.7152 * lin(d[i + 1]) + 0.0722 * lin(d[i + 2]); sum += L; reg[(y >> 2) * 4 + (x >> 3)] += L / 32 } fg.drawImage(cv, 0, 0, 96, 54); const fd = fg.getImageData(0, 0, 96, 54).data, cur = new Float32Array(96 * 54); for (let i = 0; i < cur.length; i++) cur[i] = (0.2126 * fd[i * 4] + 0.7152 * fd[i * 4 + 1] + 0.0722 * fd[i * 4 + 2]) / 255; if (prevF) { let dsum = 0; for (let i = 0; i < cur.length; i++) dsum += Math.abs(cur[i] - prevF[i]); window.__jit.push(dsum / cur.length) } prevF = cur; out.push([now - t0, sum / 512, reg]); if (now - t0 < ms) requestAnimationFrame(tick); else res(out) })() })`
function flashesOf(series) {
  const pts = []; let dir = 0, ext = series[0][1], extT = series[0][0]
  for (const [t, v] of series.slice(1)) {
    if (dir === 0) { if (Math.abs(v - ext) >= SW) { dir = v > ext ? 1 : -1; pts.push(t); ext = v; extT = t } }
    else if (dir === 1) { if (v > ext) { ext = v; extT = t } else if (ext - v >= SW) { pts.push(extT); dir = -1; ext = v; extT = t } }
    else { if (v < ext) { ext = v; extT = t } else if (v - ext >= SW) { pts.push(extT); dir = 1; ext = v; extT = t } }
  }
  let w = 0; for (let i = 0; i < pts.length; i++) w = Math.max(w, Math.floor(pts.filter((p) => p >= pts[i] && p < pts[i] + 1000).length / 2)); return { worst: w, changes: pts.length }
}
function flashes(series) {
  // the whole frame, and each of 16 regions: a region that flashes counts, because local flicker is what a small high-contrast area does
  const whole = flashesOf(series.map((s) => [s[0], s[1]])); let regWorst = 0, regChanges = 0, regAt = -1
  for (let r = 0; r < 16; r++) { const f = flashesOf(series.map((s) => [s[0], s[2][r]])); if (f.worst > regWorst) { regWorst = f.worst; regAt = r } regChanges += f.changes }
  const vs = series.map((x) => x[1]); return { worst: Math.max(whole.worst, regWorst), whole: whole.worst, region: regWorst, regionAt: regAt, changes: whole.changes + regChanges, lo: Math.min(...vs), hi: Math.max(...vs), n: series.length }
}
await pg.click('#play'); await pg.waitForTimeout(400)
const scen = {
  'Scope': async () => {}, 'Bars': async () => { await pg.click('#kid [data-km="1"]') }, 'Rainbow': async () => { await pg.click('#kid [data-km="3"]') }, 'Sun': async () => { await pg.click('#kid [data-km="4"]') },
  'Blocks': async () => { await pg.click('#kid [data-km="0"]'); await pg.evaluate(() => window.PhosphorTest.on('blocks')) },
  'Split': async () => { await pg.evaluate(() => { window.PhosphorTest.off('blocks'); window.PhosphorTest.on('rgb') }) },
  'Tear': async () => { await pg.evaluate(() => { window.PhosphorTest.off('rgb'); window.PhosphorTest.on('tear') }) },
  'Stutter': async () => { await pg.evaluate(() => { window.PhosphorTest.off('tear'); window.PhosphorTest.on('stutter') }) },
  'All together': async () => { await pg.evaluate(() => { ['rgb', 'blocks', 'tear'].forEach((k) => window.PhosphorTest.on(k)) }) },
  'Sequencer, every lane, short gate': async () => { await pg.evaluate(() => { const T = window.PhosphorTest, S = T.seq; ['stutter', 'freeze', 'tear', 'rgb', 'blocks'].forEach((l) => { for (let i = 0; i < 16; i++) S.set(l, i, 1) }); S.gate(0.25); S.bars(1); S.on(true) }) },
}
const results = {}
for (const [name, setup] of Object.entries(scen)) {
  await setup(); await pg.waitForTimeout(300)
  const series = await pg.evaluate(`(${sampler})(3000)`); results[name] = flashes(series)
}
// 1-bit tones and mashed keys
await pg.evaluate(() => { window.PhosphorTest.seq.on(false); window.PhosphorTest.seq.clear(); ['rgb', 'blocks', 'tear', 'stutter'].forEach((k) => window.PhosphorTest.off(k)) })
await pg.evaluate(() => { const p = document.getElementById('pal'); p.value = 1; p.dispatchEvent(new Event('input')) })
results['1-bit tones'] = flashes(await pg.evaluate(`(${sampler})(3000)`))
async function carrier(pg) {
  const ensure = async () => { await pg.evaluate(() => { const p = document.getElementById('play'); if (p.textContent === 'Play') p.click() }); await pg.waitForTimeout(150) }
  // carrier scenarios (Zach, 2026-10-16): bright views with every effect, and violent random tweaking of the controls. Run on a REAL song that keeps playing (an earlier version ran on a click track that had already ended, so every picture was frozen and the effects looked safe).
  const setView = async (m) => { await pg.evaluate((m) => document.querySelector(`#kid [data-km="${m}"]`).click(), m) }
  await pg.evaluate(() => { window.PhosphorTest.seq.on(false); window.PhosphorTest.seq.clear(); ['rgb', 'blocks', 'tear', 'stutter', 'crush', 'dist'].forEach((k) => window.PhosphorTest.off(k)) })
  for (const [view, vname, pal] of [[4, 'Sun', 'orig'], [3, 'Rainbow in heat', 'heat'], [3, 'Rainbow in mono', 'mono']]) {
    await setView(view); await pg.evaluate((p) => { const s = document.getElementById('palsel'); s.value = p; s.dispatchEvent(new Event('change', { bubbles: true })) }, pal); await pg.waitForTimeout(500)
    { await ensure(); const sv = await pg.evaluate(`(${sampler})(1800)`); const fl = flashes(sv); fl.jit = await pg.evaluate(() => window.__jit.reduce((a, b) => a + b, 0) / Math.max(1, window.__jit.length)); results[`${vname} with no effect (jitter baseline)`] = fl }
    for (const fx of ['tear', 'blocks', 'rgb', 'stutter']) { await pg.evaluate((k) => window.PhosphorTest.on(k), fx); await pg.waitForTimeout(250); { await ensure(); const sv = await pg.evaluate(`(${sampler})(2200)`); const fl = flashes(sv); fl.jit = await pg.evaluate(() => window.__jit.reduce((a, b) => a + b, 0) / Math.max(1, window.__jit.length)); results[`${vname} with ${fx}`] = fl; } await pg.evaluate((k) => window.PhosphorTest.off(k), fx) }
    await pg.evaluate(() => { const g = document.getElementById('gamt'); g.value = 100; g.dispatchEvent(new Event('input', { bubbles: true })); ['tear', 'blocks', 'rgb'].forEach((k) => window.PhosphorTest.on(k)) }); await pg.waitForTimeout(250)
    { await ensure(); const sv = await pg.evaluate(`(${sampler})(2200)`); const fl = flashes(sv); fl.jit = await pg.evaluate(() => window.__jit.reduce((a, b) => a + b, 0) / Math.max(1, window.__jit.length)); results[`${vname} with Tear, Blocks and Split at full Amount`] = fl }
    await pg.evaluate(() => { ['tear', 'blocks', 'rgb'].forEach((k) => window.PhosphorTest.off(k)); const g = document.getElementById('gamt'); g.value = 60; g.dispatchEvent(new Event('input', { bubbles: true })) })
  }
  { // violent random tweaking: a seeded stream of 15 control changes a second for three seconds, on a bright picture
    let seed = 20261016; const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296
    await setView(4); await pg.evaluate(() => { const s = document.getElementById('palsel'); s.value = 'orig'; s.dispatchEvent(new Event('change', { bubbles: true })) })
    const tweak = (async () => { for (let i = 0; i < 45; i++) { const r = Math.floor(rnd() * 6)
      await pg.evaluate(([r, x]) => { const E = (id, v, ev) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event(ev || 'input', { bubbles: true })) }
        if (r === 0) document.querySelector(`#kid [data-km="${Math.floor(x * 5)}"]`).click()
        else if (r === 1) { const s = document.getElementById('palsel'); s.selectedIndex = Math.floor(x * s.options.length); s.dispatchEvent(new Event('change', { bubbles: true })) }
        else if (r === 2) E('res', 1 + Math.floor(x * 9))
        else if (r === 3) { const c = document.getElementById('inv'); c.checked = !c.checked; c.dispatchEvent(new Event('change', { bubbles: true })) }
        else if (r === 4) { const k = ['tear', 'blocks', 'rgb', 'crush', 'dist', 'stutter'][Math.floor(x * 6)]; window.PhosphorTest.on(k); setTimeout(() => window.PhosphorTest.off(k), 80) }
        else document.getElementById('kzoom').click() }, [r, rnd()]); await pg.waitForTimeout(60) } })()
    await ensure(); const vs = await pg.evaluate(`(${sampler})(3200)`); await tweak; results['Violent random tweaking (15 changes a second)'] = flashes(vs)
    await pg.evaluate(() => { const c = document.getElementById('inv'); if (c.checked) c.click() })
  }

}
const realSong = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)[0]
if (realSong) { const cp = await open(realSong); await cp.evaluate(() => { const s = document.getElementById('scrub'); s.value = 300; s.dispatchEvent(new Event('input')) }); await cp.click('#play'); await cp.waitForTimeout(600); await carrier(cp) }
// positive controls: these flip the whole picture, so a working detector must see them
await pg.click('body', { position: { x: 5, y: 5 } })
const invMash = (async () => { for (let i = 0; i < 28; i++) { await pg.keyboard.press('i'); await pg.waitForTimeout(70) } })()
const iseries = await pg.evaluate(`(${sampler})(2200)`); await invMash; results['Mashing the I (invert) key'] = flashes(iseries)
await pg.evaluate(() => { const c = document.getElementById('inv'); if (c.checked) c.click() })
await pg.click('body', { position: { x: 5, y: 5 } })
const palMash = (async () => { for (let i = 0; i < 28; i++) { await pg.keyboard.press('ArrowRight'); await pg.waitForTimeout(70) } })()
const pseries = await pg.evaluate(`(${sampler})(2200)`); await palMash; results['Mashing the arrow keys (palettes)'] = flashes(pseries)
await pg.keyboard.press('Backquote')
const mash = (async () => { const keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '1', '5', '0', 'a', 's']; for (let i = 0; i < 40; i++) { await pg.keyboard.press(keys[i % keys.length]); await pg.waitForTimeout(70) } })()
const mseries = await pg.evaluate(`(${sampler})(3200)`); await mash; results['Mashed keys'] = flashes(mseries)
// N8: mashing the Notes strip (twelve keys) at about 14 per second, with the picture mirroring the sound
await pg.keyboard.press('Backquote'); await pg.evaluate(() => { document.getElementById('notesb').click() })
await pg.click('body', { position: { x: 5, y: 5 } })
const noteMash = (async () => { const ks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']; for (let i = 0; i < 44; i++) { await pg.keyboard.down(ks[i % 12]); await pg.waitForTimeout(35); await pg.keyboard.up(ks[i % 12]); await pg.waitForTimeout(35) } })()
const nseries = await pg.evaluate(`(${sampler})(3200)`); await noteMash; results['Mashing the Notes strip (1 to =)'] = flashes(nseries)
await pg.evaluate(() => { document.getElementById('notesb').click() })
for (const [name, r] of Object.entries(results)) check(r.worst <= LIM, `G1: ${name}: at most ${r.worst} flashes in any second (limit ${LIM}; jitter ${r.jit === undefined ? '' : r.jit.toFixed(4)}; whole frame ${r.whole}, worst of 16 regions ${r.region}${r.regionAt >= 0 ? ' (region ' + r.regionAt + ')' : ''}; luminance ${r.lo.toFixed(2)} to ${r.hi.toFixed(2)} over ${r.n} frames)`)

// G2 ---------------------------------------------------------------
const lp = await open(loud)
await lp.evaluate(() => { document.getElementById('play').click() }); await lp.waitForTimeout(900)
let peak = -1; for (let i = 0; i < 20; i++) { peak = Math.max(peak, await lp.evaluate(() => window.PhosphorTest.outPeak())); await lp.waitForTimeout(40) }
check(peak >= 0 && peak <= 0.5, `G2: a full-scale signal leaves the speakers no louder than 0.5 of full scale in kid mode (peak ${peak < 0 ? 'not measurable: no output bus' : peak.toFixed(3)})`)
await lp.evaluate(() => { window.PhosphorTest.fx.on('dist', true); window.PhosphorTest.fx.on('crush', true) }); await lp.waitForTimeout(300)
let peakFx = -1; for (let i = 0; i < 20; i++) { peakFx = Math.max(peakFx, await lp.evaluate(() => window.PhosphorTest.outPeak())); await lp.waitForTimeout(40) }
check(peakFx >= 0 && peakFx <= 0.5, `G2: with Distort and Crush on, a full-scale signal still leaves no louder than 0.5 (peak ${peakFx.toFixed(3)})`)
await lp.evaluate(() => { window.PhosphorTest.fx.on('dist', false); window.PhosphorTest.fx.on('crush', false) }); await lp.waitForTimeout(300)
await lp.evaluate(() => { const c = document.getElementById('fullvol'); c.checked = true; c.dispatchEvent(new Event('change')) }); await lp.waitForTimeout(300)
let peakFull = -1; for (let i = 0; i < 20; i++) { peakFull = Math.max(peakFull, await lp.evaluate(() => window.PhosphorTest.outPeak())); await lp.waitForTimeout(40) }
check(peakFull > peak + 0.2, `G2: the Grown-up checkbox turns the limit off (peak ${peak.toFixed(3)} then ${peakFull.toFixed(3)})`)
// G2 on real music with effects (found 2026-10-15: dense music and effects overshot the ceiling with 2x oversampling in the soft clip; tones and squares did not show it)
if ((process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)[0]) {
  const mp = await open(process.env.PHOSPHOR_FILES.split(',')[0])
  await mp.evaluate(() => { document.getElementById('play').click() }); await mp.waitForTimeout(800)
  await mp.evaluate(() => { ['crush', 'dist', 'echo', 'room', 'shim'].forEach((k) => window.PhosphorTest.on(k)) })
  let pm = 0; for (let i = 0; i < 120; i++) { pm = Math.max(pm, await mp.evaluate(() => window.PhosphorTest.outPeak())); await mp.waitForTimeout(50) }
  check(pm <= 0.5, `G2: a real song with Crush, Distort, Echo, Room and Shimmer on peaks at ${pm.toFixed(3)} (ceiling 0.5)`)
}
// G3 ---------------------------------------------------------------
const src = fs.readFileSync(page, 'utf8')
const bad = ['Notification.', 'serviceWorker', 'PushManager', 'leaderboard', 'streak', 'countdown', 'XMLHttpRequest', 'fetch('].filter((w) => src.includes(w))
check(bad.length === 0, `G3: no push or tracking API and no points words in the page${bad.length ? ' (found ' + bad.join(', ') + ')' : ''}`)
check(reqs.length === 0, `G3: no network requests (${reqs.length})`)
check(errors.length === 0, `no console or script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close()
if (fails.length) { console.log(`\n${fails.length} failed`); process.exit(1) }
