#!/usr/bin/env node
// phosphor_twin_check.mjs: checks T1 to T8 from _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md (Save as twin).
// Needs a local audio file you own: PHOSPHOR_FILES=/path/song.m4a[,/path/other.mp3]. Output files go to a temp folder
// that is deleted at the end; nothing is committed or uploaded. Usage: node scripts/phosphor_twin_check.mjs <page.html>
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const page = process.argv[2], files = (process.env.PHOSPHOR_FILES || '').split(',').filter(Boolean)
if (!page || !files.length) { console.error('usage: PHOSPHOR_FILES=song.m4a node scripts/phosphor_twin_check.mjs <page.html>'); process.exit(2) }
const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
let pw = null
for (const r of roots) { try { pw = createRequire(path.join(r, 'x.js'))('playwright'); break } catch {} }
if (!pw) { console.error('playwright not resolvable'); process.exit(2) }
const fails = []
const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg) }
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'phosphor-twin-'))
const url = pathToFileURL(path.resolve(page)).href
const b = await pw.chromium.launch()
const FR = [0.1, 0.3, 0.5, 0.7, 0.9]
const ready = (pg) => pg.waitForFunction(() => document.getElementById('status').textContent === '' && document.querySelectorAll('#chap button').length > 0, null, { timeout: 90000 })
const hashes = async (pg) => { const out = []; for (const f of FR) { await pg.evaluate((f) => { const s = document.getElementById('scrub'); s.value = Math.round(f * 1000); s.dispatchEvent(new Event('input', { bubbles: true })) }, f); out.push(await pg.evaluate(() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 2166136261; for (let i = 0; i < d.length; i += 7) h = Math.imul(h ^ d[i], 16777619) >>> 0; return h })) } return out }
const chapters = (pg) => pg.evaluate(() => [...document.querySelectorAll('#chap button')].map((x) => x.textContent).join(' '))
const tagsOf = (f) => { try { return JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format_tags', '-of', 'json', f]).toString()).format?.tags || {} } catch { return {} } }

for (const f of files) {
  const label = path.basename(f).slice(0, 18), songBytes = fs.statSync(f).size, tags = tagsOf(f)
  // T5: the demo state has the button disabled and nothing is saved or requested until Save is clicked
  const reqs = [], downloads = []
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1000 }, acceptDownloads: true }), pg = await ctx.newPage()
  pg.on('request', (r) => reqs.push(r.url())); pg.on('download', (d) => downloads.push(d))
  await pg.goto(url); await ready(pg)
  check(await pg.evaluate(() => document.getElementById('twinb').disabled), 'T5: with the demo signal Save as twin is disabled')
  await pg.setInputFiles('#file', f); await pg.waitForFunction(() => document.getElementById('src').textContent !== 'Demo signal' && document.getElementById('status').textContent === '', null, { timeout: 90000 })
  const origChap = await chapters(pg), origHash = await hashes(pg)
  check(downloads.length === 0 && reqs.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')), `T5 ${label}: loading a song writes nothing and requests nothing`)
  // T6: prefill from the file's own tags
  await pg.locator('#twinb').click()
  const form = await pg.evaluate(() => ({ title: document.getElementById('tt').value, credit: document.getElementById('tc').value, prov: document.getElementById('tprov').textContent }))
  const sunoTag = /suno/i.test(tags.comment || '')
  check(sunoTag ? form.credit === 'Made with Suno' : form.credit === '', `T6 ${label}: credit line prefill is "${form.credit}" (comment tag ${sunoTag ? 'says suno' : 'does not'})`)
  if (tags.artist) check(form.prov.includes(tags.artist), `T6 ${label}: the artist tag is read (${tags.artist})`)
  if (tags.title) check(form.title === tags.title, `T6 ${label}: the title tag prefills the title`)
  // Save the twin
  const [dl] = await Promise.all([pg.waitForEvent('download', { timeout: 60000 }), pg.locator('#tsave').click()])
  const twinPath = path.join(tmp, 'twin1.html'); await dl.saveAs(twinPath)
  const twinSize = fs.statSync(twinPath).size, pageSize = fs.statSync(page).size
  check(Math.abs(twinSize - (1.3334 * songBytes + pageSize)) / twinSize < 0.1, `T3 ${label}: twin is ${(twinSize / 1e6).toFixed(2)} MB for a ${(songBytes / 1e6).toFixed(2)} MB song (within 10 percent of 1.34 x song + page)`)
  // T7: attribution carried three ways
  const html = fs.readFileSync(twinPath, 'utf8')
  const ldm = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/), ld = ldm ? JSON.parse(ldm[1]) : null
  check(!!ld && ld['@type'] === 'MusicRecording' && ld.name === form.title, `T7 ${label}: JSON-LD MusicRecording carries the title`)
  check(/<meta name="description" content="[^"]*"/.test(html), `T7 ${label}: a description meta tag is present`)
  const foot1 = (html.match(/<p id="foot1">([\s\S]*?)<\/p>/) || [])[1] || ''
  check(form.credit ? foot1.includes(form.credit) && /This music is AI-generated/.test(foot1) === /suno/i.test(form.credit) : !/suno|AI-generated/i.test(foot1), `T7 ${label}: the visible credit in the footer matches the credit line`)
  // T1, T2: open the twin from disk
  const ctx2 = await b.newContext({ viewport: { width: 1280, height: 1000 }, acceptDownloads: true }), tp = await ctx2.newPage()
  const reqs2 = []; tp.on('request', (r) => reqs2.push(r.url()))
  const errs = []; tp.on('pageerror', (e) => errs.push(String(e)))
  await tp.goto(pathToFileURL(twinPath).href); await ready(tp)
  check((await chapters(tp)) === origChap, `T1 ${label}: the twin shows the same chapters (${origChap})`)
  const twHash = await hashes(tp)
  check(JSON.stringify(twHash) === JSON.stringify(origHash), `T2 ${label}: canvas pixels match the original page at five times`)
  check(reqs2.every((u) => u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')) && errs.length === 0, `T3 ${label}: the twin makes no network request and has no script errors`)
  // T4: saving from a twin does not double the audio
  await tp.locator('#twinb').click()
  const [dl2] = await Promise.all([tp.waitForEvent('download', { timeout: 60000 }), tp.locator('#tsave').click()])
  const p2 = path.join(tmp, 'twin2.html'); await dl2.saveAs(p2)
  check(Math.abs(fs.statSync(p2).size - twinSize) / twinSize < 0.01, `T4 ${label}: a twin saved from the twin is ${(fs.statSync(p2).size / 1e6).toFixed(2)} MB, the same size within 1 percent`)
  // T8: an edited or cleared credit changes what the twin carries
  await tp.locator('#twinb').click(); await tp.fill('#tc', ''); await tp.fill('#tt', 'Edited title')
  const [dl3] = await Promise.all([tp.waitForEvent('download', { timeout: 60000 }), tp.locator('#tsave').click()])
  const p3 = path.join(tmp, 'twin3.html'); await dl3.saveAs(p3)
  const h3 = fs.readFileSync(p3, 'utf8'), foot3 = (h3.match(/<p id="foot1">([\s\S]*?)<\/p>/) || [])[1] || ''
  check(/<title>Edited title twin<\/title>/.test(h3) && foot3.includes('Edited title') && !/suno|AI-generated/i.test(foot3), `T8 ${label}: an edited title and a cleared credit are what the new twin carries (no source claim left in the footer)`)
  await ctx.close(); await ctx2.close()
}
await b.close(); fs.rmSync(tmp, { recursive: true, force: true })
process.exit(fails.length ? 1 : 0)
