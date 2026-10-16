#!/usr/bin/env node
// phosphor_genome_check.mjs: G1 to G7 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Amendment 20, genome ribbon).
// Usage: node scripts/phosphor_genome_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const { chromium } = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const page = process.argv[2]; if (!page) { console.log('usage: phosphor_genome_check.mjs <page.html>'); process.exit(2) }
let bad = 0; const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), pg = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage()
const errs = [], reqs = []; pg.on('pageerror', (e) => errs.push(String(e))); pg.on('request', (r) => reqs.push(r.url()))
await pg.goto(pathToFileURL(page).href + '?test=1&shutter=off'); await pg.waitForTimeout(2000)
const T = (expr, arg) => pg.evaluate(expr, arg)
const keysBefore = await T(() => Object.keys(localStorage).sort().join(','))
// G1
const d1 = await T(() => window.PhosphorTest.genome.dna()), n = await T(() => window.PhosphorTest.genome.n()), P = await T(() => window.PhosphorTest.genome.period())
check(!!d1 && d1.length === n && n > 10, `G1: the song has ${n} codons, one per beat (${(P * 1000).toFixed(0)} ms)`)
await pg.evaluate(() => window.PhosphorTest.tap.set(120, 0)); const d2 = await T(() => window.PhosphorTest.genome.dna()); await pg.evaluate(() => window.PhosphorTest.tap.set(120, 0)); const d3 = await T(() => window.PhosphorTest.genome.dna())
check(JSON.stringify(d2) === JSON.stringify(d3), 'G1: the same song at the same grid gives the same DNA twice')
// G2
const used = [0, 1, 2].map((p) => new Set(d2.map((c) => c[p])).size); check(used.every((u) => u >= 3), `G2: each DNA base position uses at least three letters (${used.join(', ')})`)
// G3: loud and quiet beats differ in the low-weight base
const lowSpread = await T(() => { const g = window.PhosphorTest, d = g.genome.dna(), P = g.genome.period(); const L = d.map((c, i) => [i, 'ACGT'.indexOf(c[0])]); return [Math.min(...L.map((x) => x[1])), Math.max(...L.map((x) => x[1]))] })
check(lowSpread[0] === 0 && lowSpread[1] === 3, 'G3: the quietest beat reads A and the loudest low-heavy beat reads T in the first base')
// G4: only the matching base changes
const R = async () => { await T(() => window.PhosphorTest.seek(2)); await T(() => window.PhosphorTest.genome.draw()); return T(() => window.PhosphorTest.genome.now().rna) }
await T(() => window.PhosphorTest.glitch && window.PhosphorTest.fx.on('crush', false)); const r0 = await R()
await T(() => { document.getElementById('res').value = 1; document.getElementById('res').dispatchEvent(new Event('input', { bubbles: true })) }); const r1 = await R()
check(r1[0] !== r0[0] && r1[1] === r0[1] && r1[2] === r0[2], `G4: lowering the rung changes only the first base (${r0} to ${r1})`)
await T(() => { document.getElementById('pal').value = 1; document.getElementById('pal').dispatchEvent(new Event('input', { bubbles: true })) }); const r2 = await R()
check(r2[1] !== r1[1] && r2[0] === r1[0] && r2[2] === r1[2], `G4: lowering bit depth changes only the second base (${r1} to ${r2})`)
await T(() => window.PhosphorTest.fx.on('echo', true)); await T(() => window.PhosphorTest.fx.on('tear', true)); const r3 = await R()
check(r3[2] !== r2[2] && r3[0] === r2[0] && r3[1] === r2[1], `G4: switching effects on changes only the third base (${r2} to ${r3})`)
await T(() => { window.PhosphorTest.fx.on('echo', false); window.PhosphorTest.fx.on('tear', false) })
// G5: history kept
await T(() => { window.PhosphorTest.fx.on('crush', false); window.PhosphorTest.seek(2); window.PhosphorTest.genome.draw() })
const i0 = await T(() => window.PhosphorTest.genome.now().i), hist = await T(() => window.PhosphorTest.genome.rna()[window.PhosphorTest.genome.now().i])
await T(() => { const T = window.PhosphorTest; T.seek(2 + 3 * T.genome.period()); T.genome.draw() }); await pg.waitForTimeout(150)
await T(() => { const T = window.PhosphorTest; T.fx.on('crush', true); T.fx.on('echo', true); T.genome.draw() })
const hist2 = await T((i) => window.PhosphorTest.genome.rna()[i], i0), later = await T(() => window.PhosphorTest.genome.now().rna)
check(hist && hist2 === hist && later !== hist, `G5: the codon at beat ${i0} stays ${hist} after the filters change (now ${later})`); await T(() => { window.PhosphorTest.fx.on('crush', false); window.PhosphorTest.fx.on('echo', false) })
// G6: 64 codons translate
const tr = await T(() => { const W = window.PhosphorTest.genome.words, o = []; for (let a = 0; a < 4; a++) for (let b = 0; b < 4; b++) for (let c = 0; c < 4; c++) { const w = W([a, b, c], [a, b, c]); o.push(w.sound + '|' + w.look) } return o })
check(tr.length === 64 && tr.every((s) => s.split('|').every((x) => x.length > 4)) && !tr.some((s) => /[—–]/.test(s)) && new Set(tr).size === 64, 'G6: all 64 codons translate to distinct, non-empty text without em-dashes')
const banned = /(happy|sad|depress|anxi|calming|heal|therap|mood|treat)/i; check(!tr.some((s) => banned.test(s)), 'G6: no word reads as an emotional or medical claim')
// recipe
const rec = await T(() => window.PhosphorTest.genome.recipe()); check(/^Phosphor recipe/.test(rec) && /DNA \(song/.test(rec) && /RNA \(look/.test(rec) && /settings: \{/.test(rec) && !/[—–]/.test(rec), 'G6: the recipe lists song, DNA, RNA, the look and the settings, with no em-dashes')
// G7
const keysAfter = await T(() => Object.keys(localStorage).sort().join(',')); const ms = await T(() => window.PhosphorTest.genome.ms()); const med = ms.slice().sort((a, z) => a - z)[ms.length >> 1] || 0
check(keysAfter.split(',').filter((k) => /genome|rna|dna/i.test(k)).length === 0, 'G7: the ribbon adds no localStorage key of its own')
check(reqs.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')), 'G7: no network requests')
check(med < 1.5, `G7: median ribbon draw ${med.toFixed(2)} ms (want under 1.5)`)
check(errs.length === 0, `G7: no console errors ${errs.slice(0, 2).join('; ')}`)
await b.close(); process.exit(bad ? 1 : 0)
