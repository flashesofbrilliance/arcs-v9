#!/usr/bin/env node
// phosphor_slice_check.mjs: checks S1 to S4 from _PATTERNS/2026-10-15-sequencer-5d-prereg.md.
// S1 magnetic snap against an independent reference, S2 click-free cuts, S3 coherence separates true neighbors,
// S4 the greedy arrangement recovers the original order. Needs local songs: PHOSPHOR_FILES=a.m4a,b.mp3.
// Uses the page's test hook (?test=1). Usage: node scripts/phosphor_slice_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const page = process.argv[2], files = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)
if (!page || !files.length) { console.error('usage: PHOSPHOR_FILES=song.m4a node scripts/phosphor_slice_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = [], check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const b = await pw.chromium.launch(), url = pathToFileURL(path.resolve(page)).href + '?test=1', errors = []
for (const f of files) {
  const label = path.basename(f).slice(0, 18)
  const pg = await (await b.newContext({ viewport: { width: 1280, height: 1000 } })).newPage()
  pg.on('pageerror', (e) => errors.push(String(e)))
  await pg.goto(url); await pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 30000 })
  await pg.setInputFiles('#file', f); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 })
  const R = await pg.evaluate(() => {
    const T = window.PhosphorTest, M = T.magnets(), DUR = T.dur(), SR = T.sr(), out = {}
    out.counts = M.reduce((a, m) => (a[m.k] = (a[m.k] || 0) + 1, a), {})
    // S1: compare snap against an independent reference
    const W = { chapter: 1.0, onset: 0.8, valley: 0.6, grid: 0.5, edge: 0.5 }; let seed = 12345; const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296
    let mism = 0, inside = 0, outside = 0, outOk = 0, bypassOk = 0, n = 0, clean = 0, snapped = 0
    for (const radius of [0.06, 0.12, 0.2]) for (let k = 0; k < 150; k++) {
      const x = rnd() * DUR; let best = null, bs = 0
      for (const m of M) { const d = Math.abs(m.t - x); if (d > radius) continue; const sc = W[m.k] * (1 - d / radius); if (sc > bs) { bs = sc; best = m } }
      const r = T.snap(x, radius, false, -1); n++
      if (best) { inside++; if (!r.magnet || r.magnet.t !== best.t || Math.abs(r.t - best.t) > 0.0051) mism++; else { snapped++; const v = Math.abs(T.pcm(Math.round(r.t * SR)) || 0); if (v < 0.01) clean++ } }
      else { outside++; if (!r.magnet && Math.abs(r.t - x) < 1e-9) outOk++ }
      const bp = T.snap(x, radius, true, -1); if (!bp.magnet && Math.abs(bp.t - x) < 1e-9) bypassOk++
    }
    out.s1 = { n, inside, outside, mism, outOk, bypassOk }; out.s2 = { snapped, clean }
    // S3, S4: 12 slices cut at the strongest onsets, spaced DUR/14 apart
    const on = M.filter((m) => m.k === 'onset').sort((a, b) => b.s - a.s), cuts = []
    for (const m of on) { if (cuts.every((c) => Math.abs(c - m.t) >= DUR / 14)) cuts.push(m.t); if (cuts.length >= 13) break }
    cuts.sort((a, b) => a - b)
    const sl = []; for (let i = 0; i + 1 < cuts.length; i++) sl.push(T.makeSlice(cuts[i], cuts[i + 1]))
    out.nslices = sl.length
    const N = sl.length, C = []; for (let i = 0; i < N; i++) { C[i] = []; for (let j = 0; j < N; j++) C[i][j] = i === j ? null : T.coherence(sl[i], sl[j]) }
    const non = []; for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) if (i !== j && j !== i + 1) non.push(C[i][j]); non.sort((a, b) => a - b)
    const med = non[non.length >> 1]; let above = 0, pairs = 0, tsum = 0; for (let i = 0; i + 1 < N; i++) { pairs++; tsum += C[i][i + 1]; if (C[i][i + 1] > med) above++ }
    out.s3 = { pairs, above, med: +med.toFixed(3), meanTrue: +(tsum / pairs).toFixed(3), meanOther: +(non.reduce((a, v) => a + v, 0) / non.length).toFixed(3) }
    const arr = T.arrange(sl), ord = arr.order; let rec = 0; for (let i = 0; i + 1 < ord.length; i++) if (ord[i + 1] === ord[i] + 1) rec++
    out.s4 = { recovered: rec, total: N - 1, random: +(1 / (N - 1) * 1).toFixed(3), score: +arr.score.toFixed(3), order: ord.map((i) => i + 1).join(' ') }
    return out
  })
  console.log(`  ${label}: magnets ${JSON.stringify(R.counts)}; ${R.nslices} slices`)
  check(R.s1.mism === 0, `S1 ${label}: snap matched the independent reference on ${R.s1.inside} inside-radius samples (${R.s1.mism} mismatches)`)
  check(R.s1.outOk === R.s1.outside, `S1 ${label}: outside every radius the edge stayed put (${R.s1.outOk} of ${R.s1.outside})`)
  check(R.s1.bypassOk === R.s1.n, `S1 ${label}: bypass left the edge unchanged (${R.s1.bypassOk} of ${R.s1.n})`)
  check(R.s2.snapped > 0 && R.s2.clean / R.s2.snapped >= 0.9, `S2 ${label}: ${R.s2.clean} of ${R.s2.snapped} snapped edges have a sample under 0.01 (want 90 percent)`)
  const f3 = R.s3.above / R.s3.pairs
  check(f3 >= 0.8, `S3 ${label}: ${R.s3.above} of ${R.s3.pairs} true neighbor pairs beat the median non-neighbor coherence (${f3.toFixed(2)}; want 0.80, kill under 0.60); mean true ${R.s3.meanTrue} vs other ${R.s3.meanOther}`)
  const f4 = R.s4.recovered / R.s4.total
  check(f4 >= 0.4, `S4 ${label}: the arrangement recovered ${R.s4.recovered} of ${R.s4.total} true adjacent pairs (${f4.toFixed(2)}; want 0.40, kill under 0.25; random about ${R.s4.random}); order ${R.s4.order}, flow ${R.s4.score}`)
}
check(errors.length === 0, `no script errors${errors.length ? ': ' + errors[0] : ''}`)
await b.close(); process.exit(fails.length ? 1 : 0)
