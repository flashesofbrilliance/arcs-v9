#!/usr/bin/env node
// phosphor_director.mjs: a performance director for _ARTIFACTS/phosphor.html. See amendment 14 in _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md.
// It drives the real page through its test hooks and the same controls a hand would use, records picture and sound, and checks each take.
// Local only: it reads songs from a folder you name and writes demos to a folder you name. Nothing is uploaded or committed.
//   node scripts/phosphor_director.mjs pick  <page.html> <songs-dir> <out-dir>         choose five Suno-tagged songs and write picks.json
//   node scripts/phosphor_director.mjs take  <page.html> <out-dir> <index 0-4> [secs]    perform and record one demo from picks.json
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import fs from 'node:fs'

const [cmd, pagePath, a3, a4, a5] = process.argv.slice(2)
if (!cmd || !pagePath) { console.error('usage: see the header of this file'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const url = pathToFileURL(path.resolve(pagePath)).href + '?test=1'
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function openPage(b, w = 1280, h = 800) {
  const pg = await (await b.newContext({ viewport: { width: w, height: h } })).newPage(); const errors = [], reqs = []
  pg.on('pageerror', (e) => errors.push(String(e))); pg.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) }); pg.on('request', (r) => { if (!/^(file|blob|data):/.test(r.url())) reqs.push(r.url()) })
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
  return { pg, errors, reqs }
}
async function load(pg, file) {
  const prev = await pg.evaluate(() => document.getElementById('src').textContent)
  await pg.setInputFiles('#file', file)
  await pg.waitForFunction((p) => document.getElementById('src').textContent !== p && document.getElementById('status').textContent === '', prev, { timeout: 120000 })
}

if (cmd === 'pick') {
  const dir = a3, out = a4; fs.mkdirSync(out, { recursive: true })
  const cand = []
  for (const f of fs.readdirSync(dir)) {
    if (!/\.(mp3|m4a)$/i.test(f) || /kid|child|chorus/i.test(f)) continue
    let j; try { j = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:format_tags', '-of', 'json', path.join(dir, f)], { encoding: 'utf8' })) } catch { continue }
    const tags = j.format.tags || {}, low = Object.fromEntries(Object.entries(tags).map(([k, v]) => [k.toLowerCase(), v])), dur = +j.format.duration
    if (/suno/i.test(low.comment || '') && dur >= 100 && dur <= 270) cand.push({ file: path.join(dir, f), name: f, dur })
  }
  cand.sort((x, y) => x.name.localeCompare(y.name)); const only = process.env.ONLY ? process.env.ONLY.split('|') : null, use = only ? cand.filter((c) => only.includes(c.name)) : cand.slice(0, 20)
  console.log(`${cand.length} Suno-tagged songs between 1:40 and 4:30; analyzing ${use.length}`)
  const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const { pg } = await openPage(b)
  const rows = []
  for (const c of use) {
    try { await load(pg, c.file); const r = await pg.evaluate(() => ({ bpm: window.PhosphorTest.bpm(), dur: window.PhosphorTest.dur(), chaps: window.PhosphorTest.chaps() })); rows.push({ ...c, ...r }); console.log(`${c.name}  bpm ${r.bpm || 'none'}  ${r.dur.toFixed(0)} s  ${r.chaps.length} chapters`) } catch (e) { console.log('skipped', c.name, String(e).slice(0, 80)) }
  }
  await b.close()
  // spread across tempos: sort by bpm (none counts as 0), take five evenly spaced, make sure they are distinct files
  const s = (only ? rows.slice().sort((x, y) => only.indexOf(x.name) - only.indexOf(y.name)) : rows.slice().sort((x, y) => (x.bpm || 0) - (y.bpm || 0))), picks = []
  if (only) s.forEach((r) => picks.push(r)); else for (let i = 0; i < 5 && s.length; i++) { const k = Math.min(s.length - 1, Math.round(i * (s.length - 1) / 4)); const row = s[k]; if (!picks.some((p) => p.file === row.file)) picks.push(row) }
  for (const r of s) { if (picks.length >= 5) break; if (!picks.some((p) => p.file === r.file)) picks.push(r) }
  fs.writeFileSync(path.join(out, 'picks.json'), JSON.stringify(picks.slice(0, 5), null, 2)); console.log('\npicked:'); picks.slice(0, 5).forEach((p, i) => console.log(i, p.name, p.bpm || 'no tempo', p.dur.toFixed(0) + ' s'))
  process.exit(0)
}

// ------------------------------- take -------------------------------
const out = a3, idx = +a4, SECS = +(a5 || 75)
const picks = JSON.parse(fs.readFileSync(path.join(out, 'picks.json'), 'utf8')), song = picks[idx]
if (!song) { console.error('no such pick'); process.exit(2) }
const bpm0 = song.bpm || 0, style = process.env.STYLE || (!bpm0 || bpm0 < 92 ? 'moon' : bpm0 < 118 ? 'mid' : bpm0 <= 140 ? 'club' : 'fast')
const beat = 60 / (bpm0 || 90), bar = 4 * beat
const used = new Set()
const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const { pg, errors, reqs } = await openPage(b)
await load(pg, song.file)
const E = (f, ...a) => pg.evaluate(f, ...a)
const A = {
  mode: (n) => { used.add('view modes'); return E((n) => document.querySelector(`#kid [data-km="${n}"]`).click(), n) },
  pal: (p) => { used.add('colors'); return E((p) => { const s = document.getElementById('palsel'); s.value = p; s.dispatchEvent(new Event('change', { bubbles: true })) }, p) },
  res: (v) => { used.add('resolution develop'); return E((v) => { const r = document.getElementById('res'); r.value = v; r.dispatchEvent(new Event('input', { bubbles: true })) }, v) },
  zoom: () => { used.add('zoom stages'); return E(() => document.getElementById('kzoom').click()) },
  fx: (k, on) => { used.add(k === 'stutter' || k === 'freeze' ? 'stutter or freeze' : k); return E(([k, on]) => on ? window.PhosphorTest.on(k) : window.PhosphorTest.off(k), [k, on]) },
  seq: (lane, steps, v = 1) => { used.add('step lanes'); return E(([l, s, v]) => s.forEach((i) => window.PhosphorTest.seq.set(l, i, v)), [lane, steps, v]) },
  seqClear: () => E(() => window.PhosphorTest.seq.clear()),
  seqOn: (on) => E((on) => window.PhosphorTest.seq.on(on), on),
  snap: (q, g) => E(([q, g]) => { window.PhosphorTest.seq.quant(q); window.PhosphorTest.seq.gate(g) }, [q, g]),
  loop: (on, bars, dir) => { used.add('resolution loop'); return E(([o, b2, d]) => window.PhosphorTest.loop(o, b2, d), [on, bars, dir]) },
  gate: (m, thr, div) => { used.add('gate'); return E(([m, t, d]) => window.PhosphorTest.fx.gate(m, t, d), [m, thr, div]) },
  preset: (n) => { used.add('presets'); return E((n) => window.PhosphorTest.preset(n), n) },
  tempo: (bpm, origin) => { used.add('tempo tools'); return E(([b2, o]) => window.PhosphorTest.tap.set(b2, o), [bpm, origin]) },
  notesOn: (on) => E((on) => window.PhosphorTest.notes.on(on), on),
  amount: (v) => E((v) => { const g = document.getElementById('gamt'); g.value = v; g.dispatchEvent(new Event('input', { bubbles: true })) }, v),
}
async function note(key, holdSec) { used.add('notes'); await pg.keyboard.down(key); await sleep(holdSec * 1000); await pg.keyboard.up(key) }
const songT = () => E(() => window.PhosphorTest.tnow())

// start: a chapter start that leaves room for the take, nearest a quarter of the way in
const want = song.dur * 0.25, room = song.dur - SECS - 3
let start = 0; for (const c of song.chaps) if (c <= room && Math.abs(c - want) < Math.abs(start - want)) start = c
await E((t) => { const s = document.getElementById('scrub'); s.value = Math.round(t / window.PhosphorTest.dur() * 1000); s.dispatchEvent(new Event('input')) }, start)
await sleep(300); start = await songT()
await E(() => { document.getElementById('fsb').click() }); await sleep(400)   // a larger picture for the capture

// scores: each is [seconds into the take, label, action]
const sc = []
const at = (t, label, fn) => sc.push([t, label, fn])
const develop = (t0, from, step) => { for (let r = from, t = t0; r <= 9; r++, t += step) at(t, 'res ' + r, () => A.res(r)) }
if (style === 'sparse') {
  // post-minimal for fast songs: a thin line, long gaps, one effect at a time, a single precise drop, decay at the end
  at(0, 'plain, phosphor green, coarse', async () => { await A.preset('plain'); await A.pal('phosphor'); await A.mode(0); await A.res(2) }); develop(2, 3, 5)
  at(14, 'one echo on one beat', async () => { await A.fx('echo', true); await sleep(beat * 1000); await A.fx('echo', false) })
  at(26, 'ring, indigo', async () => { await A.mode(2); await A.pal('indigo') })
  at(32, 'one sparse lane', async () => { await A.tempo(bpm0 || 120, 0); await A.seqClear(); await A.seq('stutter', [12]); await A.snap('onset', 0.25); await A.seqOn(true) })
  at(44, 'lane off, room', async () => { await A.seqOn(false); await A.fx('room', true) }); at(50, 'room off', () => A.fx('room', false))
  at(54, 'sweep closes slowly', () => A.fx('sweep', true))
  at(61, process.env.GOLD ? 'the drop: sweep cut, the gold chime' : 'the drop: sweep cut, one distort hit', async () => { await A.fx('sweep', false); if (process.env.GOLD) { used.add('gold chime'); await E(() => window.PhosphorTest.fx.gold.play()) } else { await A.fx('dist', true); await sleep(beat * 1000); await A.fx('dist', false) } })
  at(65, 'resolution loop, one bar', () => A.loop(true, 1, 'down')); at(70, 'loop off, decay', async () => { await A.loop(false, 1, 'up'); await A.res(5) }); at(73, 'decay', () => A.res(3))
} else if (style === 'moon') {
  at(0, 'sleepy preset, amber', async () => { await A.preset('sleepy'); await A.pal('amber'); await A.res(3) }); develop(3, 4, 4)
  at(8, 'room', () => A.fx('room', true)); at(15, 'room off', () => A.fx('room', false))
  at(20, 'notes on', () => A.notesOn(true)); at(21, 'motif', async () => { await note('1', 0.9); await sleep(500); await note('3', 0.9); await sleep(500); await note('5', 1.6) }); at(27, 'notes off', () => A.notesOn(false))
  at(30, 'radial, indigo', async () => { await A.mode(2); await A.pal('indigo') })
  at(38, 'echo', () => A.fx('echo', true)); at(40, 'echo off', () => A.fx('echo', false))
  at(46, 'sweep closes', () => A.fx('sweep', true)); at(55, 'sweep opens', () => A.fx('sweep', false))
  at(58, 'a single stutter', async () => { await A.tempo(bpm0 || 72, 0); await A.seq('stutter', [0]); await A.snap('beat', 0.25); await A.seqOn(true) }); at(66, 'stutter off', () => A.seqOn(false))
  at(62, 'zoom in', () => A.zoom()); at(68, 'fade', () => A.res(6)); at(72, 'fade', () => A.res(4))
} else if (style === 'mid') {
  at(0, 'rain preset, phosphor', async () => { await A.preset('rain'); await A.pal('phosphor'); await A.res(4) }); develop(2, 5, 2.5)
  at(12, 'room', () => A.fx('room', true)); at(22, 'room off', () => A.fx('room', false))
  at(24, 'bars, loop on the beat', async () => { await A.mode(1); await A.loop(true, 2, 'pp') })
  at(34, 'shimmer', () => A.fx('shim', true)); at(42, 'shimmer off', () => A.fx('shim', false))
  at(44, 'crush on loud hits', async () => { await A.gate('level', -22); await A.fx('crush', true) }); at(50, 'crush off', async () => { await A.fx('crush', false); await A.gate('off') })
  at(52, 'ring, indigo', async () => { await A.mode(2); await A.pal('indigo'); await A.loop(false, 2, 'up') })
  at(56, 'sweep', () => A.fx('sweep', true)); at(60, 'sweep cut, one distort hit', async () => { await A.fx('sweep', false); await A.fx('dist', true); await sleep(beat * 1000); await A.fx('dist', false) })
  at(64, 'notes', async () => { await A.notesOn(true); await note('2', 0.7); await sleep(300); await note('4', 0.7); await sleep(300); await note('6', 1.4); await A.notesOn(false) })
  at(70, 'fade', () => A.res(6))
} else if (style === 'club') {
  at(0, 'robot preset, arcs', async () => { await A.preset('robot'); await A.pal('arcs'); await A.res(5) }); develop(2, 6, 3)
  at(8, 'sparse lanes', async () => { await A.seqClear(); await A.seq('stutter', [12]); await A.seq('echo', [6]); await A.snap('onset', 0.25); await A.seqOn(true) })
  at(16, 'resolution loop', () => A.loop(true, 2, 'up'))
  at(24, 'build: sweep closes', () => A.fx('sweep', true))
  at(32, 'drop: cut and one distort hit', async () => { await A.fx('sweep', false); await A.fx('dist', true); await sleep(beat * 1000); await A.fx('dist', false); await A.mode(2) })
  at(36, 'more lanes', async () => { await A.seq('blocks', [4, 12]) })
  at(42, 'beat cut crush', async () => { await A.gate('beat', undefined, 4); await A.fx('crush', true) }); at(47, 'crush off', async () => { await A.fx('crush', false); await A.gate('off') })
  at(52, 'shimmer', () => A.fx('shim', true)); at(58, 'shimmer off', () => A.fx('shim', false))
  at(60, 'room, heat', async () => { await A.fx('room', true); await A.pal('heat') }); at(66, 'room off', () => A.fx('room', false))
  at(68, 'lanes off, fade', async () => { await A.seqOn(false); await A.loop(false, 2, 'up'); await A.res(6) })
} else {
  at(0, 'rainbow, heat', async () => { await A.mode(3); await A.pal('heat'); await A.res(5) }); develop(2, 6, 2.5)
  at(8, 'sparse lanes', async () => { await A.seqClear(); await A.seq('rgb', [0, 10]); await A.seq('tear', [6]); await A.snap('beat', 0.25); await A.seqOn(true) })
  at(16, 'resolution loop', () => A.loop(true, 1, 'pp'))
  for (const t of [24, 40, 56]) at(t, 'a one-beat stutter roll', async () => { await A.fx('stutter', true); await sleep(beat * 1000); await A.fx('stutter', false) })
  at(30, 'echo out', async () => { await A.fx('echo', true); await sleep(beat * 2000); await A.fx('echo', false) })
  at(44, 'beat cut distort', async () => { await A.gate('beat', undefined, 4); await A.fx('dist', true) }); at(48, 'off', async () => { await A.fx('dist', false); await A.gate('off') })
  at(50, 'room and shimmer', async () => { await A.fx('room', true); await A.fx('shim', true) }); at(58, 'off', async () => { await A.fx('room', false); await A.fx('shim', false) })
  at(62, 'radial, phosphor', async () => { await A.mode(2); await A.pal('phosphor') }); at(68, 'fade', async () => { await A.seqOn(false); await A.loop(false, 1, 'up'); await A.res(6) })
}
sc.sort((x, y) => x[0] - y[0])

// instruments: luminance sampler, output peak tracker, recorder
await E(() => {
  window.__lum = []; window.__pk = 0; const cv = document.getElementById('cv'), s = document.createElement('canvas'); s.width = 32; s.height = 18; const g = s.getContext('2d', { willReadFrequently: true }), t0 = performance.now();
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4) };
  (function tick() { g.drawImage(cv, 0, 0, 32, 18); const d = g.getImageData(0, 0, 32, 18).data; let sum = 0; for (let i = 0; i < d.length; i += 4) sum += 0.2126 * lin(d[i]) + 0.7152 * lin(d[i + 1]) + 0.0722 * lin(d[i + 2]); window.__lum.push([performance.now() - t0, sum / (d.length / 4)]); requestAnimationFrame(tick) })()
  setInterval(() => { window.__pk = Math.max(window.__pk, window.PhosphorTest.outPeak()) }, 40)
})
await E(() => window.PhosphorTest.rec.start())
await E(() => document.getElementById('play').click()); await sleep(250)
const t0 = Date.now(), log = []
const base = await songT()
for (const [t, label, fn] of sc) {
  if (t > SECS) break
  while ((await songT()) - base < t) await sleep(15)
  try { await fn() } catch (e) { log.push('error at ' + label + ': ' + String(e).slice(0, 100)) }
  log.push(`${t.toFixed(0).padStart(3)} s  ${label}`)
}
while ((await songT()) - base < SECS) await sleep(50)
await E(() => document.getElementById('play').click()); await sleep(300)
const b64 = await E(() => window.PhosphorTest.rec.stop()), lum = await E(() => window.__lum), pk = await E(() => window.__pk)
const slug = song.name.replace(/\.[^.]+$/, '').replace(/[^A-Za-z0-9]+/g, '-').replace(/^-+|-+$/g, '').toLowerCase()
const base2 = path.join(out, `demo-${idx + 1}-${slug}${process.env.SUFFIX || ''}`); fs.writeFileSync(base2 + '.webm', Buffer.from(b64, 'base64'))
let mp4 = false; try { execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', base2 + '.webm', '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '27', '-c:a', 'aac', '-b:a', '128k', base2 + '.mp4']); mp4 = true } catch (e) { console.log('ffmpeg failed', String(e).slice(0, 120)) }
// flashes: pairs of 10 percent swings in any second
function flashes(series) { const pts = []; let dir = 0, ext = series[0][1], extT = series[0][0]; for (const [t, v] of series.slice(1)) { if (dir === 0) { if (Math.abs(v - ext) >= 0.1) { dir = v > ext ? 1 : -1; pts.push(t); ext = v; extT = t } } else if (dir === 1) { if (v > ext) { ext = v; extT = t } else if (ext - v >= 0.1) { pts.push(extT); dir = -1; ext = v; extT = t } } else { if (v < ext) { ext = v; extT = t } else if (v - ext >= 0.1) { pts.push(extT); dir = 1; ext = v; extT = t } } } let w = 0; for (let i = 0; i < pts.length; i++) w = Math.max(w, Math.floor(pts.filter((p) => p >= pts[i] && p < pts[i] + 1000).length / 2)); return w }
const fps = lum.length / (lum[lum.length - 1][0] / 1000)
const allFamilies = ['view modes', 'colors', 'resolution develop', 'resolution loop', 'step lanes', 'stutter or freeze', 'crush', 'dist', 'echo', 'room', 'shim', 'sweep', 'gate', 'notes', 'tempo tools', 'zoom stages', 'presets']
const report = { song: song.name, style, bpm: bpm0 || null, startInSong: +start.toFixed(1), seconds: SECS, peak: +pk.toFixed(3), peakOk: pk <= 0.5, worstFlashesPerSecond: flashes(lum), flashesOk: flashes(lum) <= 3, networkRequests: reqs.length, pageErrors: errors.length, sampledFps: +fps.toFixed(1), featuresUsed: [...used].sort(), featuresNotUsed: allFamilies.filter((f) => !used.has(f)), mp4, log }
fs.writeFileSync(base2 + '.json', JSON.stringify(report, null, 2))
console.log(JSON.stringify({ ...report, log: undefined }, null, 1)); console.log(log.join('\n'))
await b.close()
if (!report.peakOk || !report.flashesOk || report.networkRequests || report.pageErrors) { console.log('\nTAKE REJECTED by the guard'); process.exit(1) }
