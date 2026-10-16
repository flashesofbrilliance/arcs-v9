#!/usr/bin/env node
// beat_eval.mjs: score the page's beat detection against known truth (made by beat_truth_tracks.py).
// For each track: detected BPM against truth (exact within 1 percent, octave and ratio errors named), and the grid phase error
// (grid origin against the true first beat, wrapped to half a beat, in milliseconds).
// Usage: node scripts/beat_eval.mjs <page.html> <truth-dir> [out.json]
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'

const [pagePath, dir, outp] = process.argv.slice(2)
if (!pagePath || !dir) { console.error('usage: beat_eval.mjs <page.html> <truth-dir> [out.json]'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
const truth = JSON.parse(fs.readFileSync(path.join(dir, 'truth.json'), 'utf8'))
const b = await pw.chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] })
const pg = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage()
await pg.goto(pathToFileURL(path.resolve(pagePath)).href + '?test=1'); await pg.waitForFunction(() => document.getElementById('status').textContent === '')
const rows = []
for (const t of truth) {
  const prev = await pg.evaluate(() => document.getElementById('src').textContent)
  await pg.setInputFiles('#file', path.join(dir, t.name + '.wav'))
  await pg.waitForFunction((p) => document.getElementById('src').textContent !== p && document.getElementById('status').textContent === '', prev, { timeout: 120000 })
  const r = await pg.evaluate(() => ({ bpm: window.PhosphorTest.bpm(), g0: window.PhosphorTest.seq.base(), conf: window.PhosphorTest.fx.bpmInfo ? window.PhosphorTest.fx.bpmInfo() : null }))
  const ratio = r.bpm ? r.bpm / t.bpm : 0
  const kind = !r.bpm ? 'none' : Math.abs(ratio - 1) < 0.015 ? 'ok' : Math.abs(ratio - 2) < 0.03 ? 'double' : Math.abs(ratio - 0.5) < 0.015 ? 'half' : Math.abs(ratio - 1.5) < 0.03 ? 'x1.5' : Math.abs(ratio - 2 / 3) < 0.02 ? 'x2/3' : Math.abs(ratio - 4 / 3) < 0.03 ? 'x4/3' : Math.abs(ratio - 0.75) < 0.02 ? 'x3/4' : 'other'
  const P = 60 / t.bpm; let d = ((r.g0 - t.t0) % P + P) % P; if (d > P / 2) d -= P; const phaseMs = r.bpm ? Math.round(d * 1000) : null
  rows.push({ name: t.name, pattern: t.pattern, truth: t.bpm, got: r.bpm, kind, phaseMs, conf: r.conf })
  console.log(`${t.name.padEnd(14)} truth ${String(t.bpm).padStart(3)}  got ${String(r.bpm || '-').padStart(4)}  ${kind.padEnd(7)} phase ${phaseMs === null ? '-' : (phaseMs + ' ms').padStart(7)}`)
}
const ok = rows.filter((r) => r.kind === 'ok').length, ph = rows.filter((r) => r.kind === 'ok' && Math.abs(r.phaseMs) <= 25).length
console.log(`\ntempo right: ${ok} of ${rows.length}; of those, grid within 25 ms of the true beat: ${ph}`)
const byKind = {}; rows.forEach((r) => { byKind[r.kind] = (byKind[r.kind] || 0) + 1 }); console.log('by outcome:', JSON.stringify(byKind))
const byPat = {}; rows.forEach((r) => { (byPat[r.pattern] = byPat[r.pattern] || { n: 0, ok: 0 }); byPat[r.pattern].n++; if (r.kind === 'ok') byPat[r.pattern].ok++ }); console.log('right by pattern:', JSON.stringify(byPat))
if (outp) fs.writeFileSync(outp, JSON.stringify(rows, null, 1))
await b.close()
