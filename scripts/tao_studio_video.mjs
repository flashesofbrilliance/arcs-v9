#!/usr/bin/env node
/**
 * tao_studio_video.mjs: render the Tao print studio to a frame-exact video, in any of four shapes, with the audio joined in.
 *
 *   node scripts/tao_studio_video.mjs --out out.mp4 [--preset tag|street|fancy|brain|invader|silk] [--recipe <file or inline json>]
 *        [--audio song.mp3] [--ratio 16:9|4:3|1:1|9:16] [--short 720|1080] [--fps 30] [--seconds N] [--start S]
 *        [--drive tagmap|sweep|off|recipe] [--square] [--lossless] [--keep-frames DIR] [--force]
 *
 * How: opens _ARTIFACTS/tao-print-studio.html in stage-only mode (`?stage=1`, the viewport is the video size), loads the recipe and the audio, then for frame i sets the
 * time to start + i/fps, waits for the paint, captures the stage and streams the frame to ffmpeg. Quality is forced to Full, so the rough, spray and wall filters are on;
 * a full-grit frame can take most of a second. A second ffmpeg pass joins the ORIGINAL audio file (the live key effects are not in the sound; the key presses are in the picture).
 * With no --audio the page's built-in demo signal is used. Local only: any network request is blocked and counted; it refuses to overwrite an existing --out without --force;
 * temporary files live in a temp folder that is removed at the end. Needs Playwright (repo node_modules or global) and ffmpeg and ffprobe on PATH. No new dependencies.
 * Prints one JSON summary. See _PATTERNS/2026-10-18-studio-offline-renderer-prereg.md (once on main) for the checks.
 */
import { spawn, execFileSync } from 'node:child_process'
import { createRequire } from 'node:module'
import { existsSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync, mkdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const argv = process.argv.slice(2)
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d }
const flag = (k) => argv.includes('--' + k)
const out = opt('out'); if (!out) { console.error('usage: tao_studio_video.mjs --out out.mp4 [--preset p] [--recipe r] [--audio a] [--ratio 16:9] [--short 720] [--fps 30] [--seconds N] [--start S] [--drive d] [--square] [--lossless] [--keep-frames DIR] [--force]'); process.exit(2) }
const OUT = resolve(out)
if (existsSync(OUT) && !flag('force')) { console.error('refusing to overwrite ' + OUT + ' (pass --force)'); process.exit(2) }
const RATIOS = { '16:9': 16 / 9, '4:3': 4 / 3, '1:1': 1, '9:16': 9 / 16 }
const ratio = opt('ratio', '16:9'); if (!RATIOS[ratio]) { console.error('--ratio must be one of ' + Object.keys(RATIOS).join(', ')); process.exit(2) }
const short = +opt('short', 720), fps = +opt('fps', 30), start = +opt('start', 0), a = RATIOS[ratio]
const W = a >= 1 ? Math.round(short * a / 2) * 2 : short, H = a >= 1 ? short : Math.round(short / a / 2) * 2
const preset = opt('preset', null), audio = opt('audio', null), driveMode = opt('drive', opt('recipe') ? 'recipe' : 'tagmap'), keep = opt('keep-frames', null)
const here = dirname(fileURLToPath(import.meta.url)), studio = pathToFileURL(resolve(here, '..', '_ARTIFACTS', 'tao-print-studio.html')).href + '?stage=1'
if (audio && !existsSync(resolve(audio))) { console.error('audio file not found: ' + audio); process.exit(2) }
let recipe = null; if (opt('recipe')) { const r = opt('recipe'); recipe = JSON.parse(existsSync(r) ? readFileSync(r, 'utf8') : r) }

function loadPlaywright() {
  const req = createRequire(import.meta.url)
  for (const base of [process.cwd(), execFileSync('npm', ['root', '-g'], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim()]) { try { return req(req.resolve('playwright', { paths: [base] })) } catch {} }
  console.error('Playwright not found (repo node_modules or global).'); process.exit(3)
}
const { chromium } = loadPlaywright()
const tmp = mkdtempSync(join(tmpdir(), 'tao-video-')), t0 = Date.now(), blocked = []
let browser
try {
  browser = await chromium.launch()
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
  await ctx.route('**/*', (r) => { const u = r.request().url(); if (/^(file|data|blob):/.test(u)) return r.continue(); blocked.push(u); return r.abort() })
  const page = await ctx.newPage(), errs = []; page.on('pageerror', (e) => errs.push(e.message))
  if (recipe) await page.addInitScript((c) => { try { localStorage.setItem('tao-print-studio', JSON.stringify(c)) } catch (e) {} }, recipe)
  await page.goto(studio); await page.waitForFunction(() => window.TaoDrive && TaoDrive.ready() && window.TaoRT); await page.waitForTimeout(500)
  const sel = (id, v) => page.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('change', { bubbles: true })) }, [id, v])
  if (preset) { if (!(await page.evaluate((p) => !!document.getElementById('p-' + p), preset))) { console.error('unknown preset: ' + preset); process.exit(2) } await page.evaluate((p) => document.getElementById('p-' + p).click(), preset); await page.waitForTimeout(600) }
  if (!recipe || !recipe.layout) await sel('layout', flag('square') ? 'square' : 'fit')
  await sel('frame', 'auto')
  if (audio) { await page.setInputFiles('#drive-file', resolve(audio)); await page.waitForFunction((n) => { const f = TaoDrive.frame(); return f && f.name !== 'Demo signal' && TaoDrive.ready() }, null, { timeout: 120000 }); await page.waitForTimeout(400) }
  if (driveMode === 'tagmap') await page.evaluate(() => document.getElementById('drive-tagmap').click())
  else if (driveMode === 'sweep') await page.evaluate(() => document.getElementById('drive-sweep').click())
  else if (driveMode === 'off') await page.evaluate(() => { const e = document.getElementById('drive-on'); e.checked = false; e.dispatchEvent(new Event('change', { bubbles: true })) })
  await page.evaluate(() => TaoRT.forceFull()); await page.waitForTimeout(300)
  const dur = await page.evaluate(() => TaoDrive.dur()), seconds = Math.min(+opt('seconds', dur - start), 900), frames = Math.max(1, Math.round(seconds * fps))
  if (start + seconds > dur + 1e-6 && !flag('loop')) { /* allow wrap: the studio clip loops */ }
  // audio source for the mux: the original file, or the page's demo signal written as a WAV
  let audioPath = audio ? resolve(audio) : join(tmp, 'demo.wav')
  if (!audio) { const b64 = await page.evaluate(() => TaoDrive.wavBase64()); writeFileSync(audioPath, Buffer.from(b64, 'base64')) }
  const vOut = join(tmp, 'video.mp4'), codec = execFileSync('ffmpeg', ['-hide_banner', '-encoders']).toString().includes('libx264') ? 'libx264' : 'mpeg4'
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', codec, ...(codec === 'libx264' ? ['-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p'] : ['-q:v', '2']), vOut], { stdio: ['pipe', 'inherit', 'inherit'] })
  const done = new Promise((res, rej) => { ff.on('exit', (c) => (c === 0 ? res() : rej(new Error('ffmpeg video pass exited ' + c)))); ff.on('error', rej) })
  if (keep) mkdirSync(resolve(keep), { recursive: true })
  const tf = Date.now(), shotOpts = keep || flag('lossless') ? { type: 'png' } : { type: 'jpeg', quality: 92 }
  for (let i = 0; i < frames; i++) {
    const t = (start + i / fps) % dur
    await page.evaluate((t) => window.seek(t), t)
    for (let k = 0; k < 100; k++) { const idle = await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(window.TaoRT.idle()))))); if (idle) break; await page.waitForTimeout(50) }
    const buf = await page.screenshot(shotOpts)
    if (keep) writeFileSync(join(resolve(keep), 'f' + String(i).padStart(5, '0') + '.png'), buf)
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r))
  }
  ff.stdin.end(); await done
  const tm = Date.now()
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', vOut, '-ss', String(start), '-t', String(seconds), '-i', audioPath, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', OUT])
  const size = statSync(OUT).size
  console.log(JSON.stringify({ out: OUT, ratio, size: W + 'x' + H, fps, frames, seconds: +seconds.toFixed(3), encoder: codec, audio: audio ? resolve(audio) : 'demo signal', drive: driveMode, preset: preset || null, bytes: size, seconds_per_frame: +(((tm - tf) / 1000) / frames).toFixed(3), render_seconds: +((Date.now() - t0) / 1000).toFixed(1), network_blocked: blocked.length, page_errors: errs }))
} finally {
  if (browser) await browser.close()
  rmSync(tmp, { recursive: true, force: true })
}
