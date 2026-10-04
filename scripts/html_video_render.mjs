#!/usr/bin/env node
/**
 * html_video_render.mjs: render an HTML animation to MP4, frame by frame.
 *
 * The page must expose `window.DURATION` (seconds) and `window.seek(t)`, where every frame is a pure
 * function of t. Stepping time explicitly (instead of recording a live animation) makes the render
 * exact at any frame rate and repeatable at any aspect ratio.
 *
 *   node scripts/html_video_render.mjs <page.html> <out.mp4> [--w 1280 --h 720 --fps 30 --poster 3.0]
 *
 * Needs Playwright (repo node_modules or global) and ffmpeg on PATH. No new dependencies.
 * Writes <out.mp4> (H.264, yuv420p, faststart) and, with --poster <t>, <out>-poster.jpg.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const [page, out] = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
if (!page || !out) { console.error('usage: html_video_render.mjs <page.html> <out.mp4> [--w --h --fps --poster]'); process.exit(2); }
const W = +opt('w', 1280), H = +opt('h', 720), FPS = +opt('fps', 30), POSTER = opt('poster', null);

function loadPlaywright() {
  const req = createRequire(import.meta.url);
  for (const base of [process.cwd(), execFileSync('npm', ['root', '-g']).toString().trim()]) {
    try { return req(req.resolve('playwright', { paths: [base] })); } catch {}
    try { return req(req.resolve('@playwright/test', { paths: [base] })); } catch {}
  }
  throw new Error('playwright not found (repo or global)');
}
const { chromium } = loadPlaywright();
const exe = process.env.PW_EXEC || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const browser = await chromium.launch({ executablePath: exe }).catch(() => chromium.launch());
const p = await browser.newPage({ viewport: { width: W, height: H } });
await p.goto(pathToFileURL(resolve(page)).href, { waitUntil: 'load' });
await p.evaluate(() => document.fonts.ready);
const duration = await p.evaluate(() => window.DURATION);
const frames = Math.round(duration * FPS);
const dir = mkdtempSync(join(tmpdir(), 'htmlvid-'));
for (let f = 0; f < frames; f++) {
  await p.evaluate((t) => window.seek(t), f / FPS);
  await p.screenshot({ path: join(dir, `${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
}
if (POSTER !== null) {
  await p.evaluate((t) => window.seek(t), +POSTER);
  await p.screenshot({ path: out.replace(/\.mp4$/, '-poster.jpg'), type: 'jpeg', quality: 88 });
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(dir, '%05d.jpg'),
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
rmSync(dir, { recursive: true, force: true });
console.log(`rendered ${out}: ${W}x${H}, ${frames} frames, ${duration}s @ ${FPS}fps`);
