// Fluid-timing sample for one card (default 04): reveals on measured sentence starts, cross-dissolves,
// picture leads voice 0.4 s and holds 0.6 s after, card length snapped to music bars, music rides
// 55:45 in gaps and 70:30 under speech. Reads the PNG states bp-build.cjs already rendered.
// Usage: node fluid-card.cjs [NN]  ->  out/fluid/NN.mp4
const { execFileSync } = require('child_process');
const fs = require('fs');
const N = process.argv[2] || '04';
const V = __dirname, BP = `${V}/out/bp`, OUT = `${V}/out/fluid`;
fs.mkdirSync(OUT, { recursive: true });
const MUSIC = '/Users/zharris/Downloads/Ephemeral Beauty (1).mp3';
const LEAD = 0.4, TAIL = 0.6, CHIP = 1.8, BAR = 60 / 161.5 * 4; // 1.486 s
const SHUTTER = 0.65, QUICK = 0.24, RAMP_A = 0.3, RAMP_R = 0.6;
const run = (...a) => execFileSync('ffmpeg', ['-hide_banner', '-y', '-loglevel', 'error', ...a]);
const sh = (...a) => execFileSync('ffmpeg', ['-hide_banner', ...a], { stdio: ['ignore', 'pipe', 'pipe'] });
const audio = `${V}/voice/${N}.mp3`;
const D = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio]).toString());

// 1. Sentence starts: word-share estimate, snapped to the nearest measured pause end.
const script = fs.readFileSync(`${V}/voice/SCRIPT.md`, 'utf8');
const sents = script.split(/^## /m).find(s => s.startsWith(N)).split('\n').slice(1).join(' ').trim().split(/(?<=[.!?]["\u201d]?)\s+/);
const log = execFileSync('sh', ['-c', `ffmpeg -hide_banner -i "${audio}" -af silencedetect=n=-38dB:d=0.18 -f null - 2>&1`]).toString();
const ends = [...log.matchAll(/silence_end: ([0-9.]+)/g)].map(m => +m[1]).filter(t => t < D - 0.3);
const words = sents.map(s => s.split(/\s+/).length), W = words.reduce((a, c) => a + c, 0);
const starts = [0];
for (let k = 1; k < sents.length; k++) {
  const est = words.slice(0, k).reduce((a, c) => a + c, 0) / W * D;
  const near = ends.reduce((b, t) => Math.abs(t - est) < Math.abs(b - est) ? t : b, ends[0] ?? est);
  starts.push(Math.abs(near - est) < 1.5 ? near : est);
}
// speech spans for the music ride: from each pause end to the next pause start
const gaps = [...log.matchAll(/silence_start: ([0-9.]+)[\s\S]*?silence_end: ([0-9.]+)/g)].map(m => [+m[1], +m[2]]);

// 2. Timeline. Picture at 0, voice at LEAD, chip after voice + TAIL, total snapped up to whole bars.
const states = fs.readdirSync(BP).filter(f => new RegExp(`^${N}-\\d+\\.png$`).test(f)).sort((a, b) => parseInt(a.split('-')[1]) - parseInt(b.split('-')[1]));
// bp-build maps state k to the k-th distinct `at`; for card 04 that is sentence k.
const tState = states.map((_, k) => k === 0 ? 0 : LEAD + starts[Math.min(k, starts.length - 1)] - QUICK);
const tChip = LEAD + D + TAIL;
const TOTAL = Math.ceil((tChip + CHIP) / BAR) * BAR;
const imgs = [...states.map(f => `${BP}/${f}`), `${BP}/${N}-chip.png`];
const at = [...tState, tChip];

// 3. Video: each still looped for its span, chained with xfade.
const inputs = [], spans = imgs.map((_, i) => (i + 1 < at.length ? at[i + 1] : TOTAL) - at[i] + QUICK);
imgs.forEach((f, i) => inputs.push('-loop', '1', '-t', spans[i].toFixed(3), '-i', f));
let fc = '', prev = '[0:v]';
for (let i = 1; i < imgs.length; i++) {
  const d = i === imgs.length - 1 ? SHUTTER * 0.6 : QUICK; // the chip arrives a touch slower
  fc += `${prev}[${i}:v]xfade=transition=fade:duration=${d.toFixed(3)}:offset=${(at[i]).toFixed(3)}[v${i}];`;
  prev = `[v${i}]`;
}
fc += `${prev}fade=t=in:d=${SHUTTER}:color=black,fade=t=out:st=${(TOTAL - SHUTTER).toFixed(3)}:d=${SHUTTER},format=yuv420p[v];`;

// 4. Audio: voice delayed by LEAD; music at 55:45 under the voice level, ducked to 70:30 while speaking.
const vol = log.match(/./) && execFileSync('sh', ['-c', `ffmpeg -hide_banner -i "${audio}" -af ebur128 -f null - 2>&1 | awk '/^ +I:/{v=$2} END{print v}'`]).toString().trim();
const gapLUFS = (+vol - 20 * Math.log10(55 / 45)).toFixed(1);
const duckDB = (20 * Math.log10(70 / 30) - 20 * Math.log10(55 / 45)); // ~5.6 dB
const speech = []; let s0 = 0;
for (const [a, b] of gaps) { if (a > s0) speech.push([s0, a]); s0 = b; }
if (s0 < D) speech.push([s0, D]);
// piecewise gain: 1 in gaps, g under speech, linear ramps (attack RAMP_A before, release RAMP_R after)
const g = Math.pow(10, -duckDB / 20).toFixed(4);
const seg = speech.map(([a, b]) => { a += LEAD; b += LEAD;
  return `if(between(t,${(a - RAMP_A).toFixed(3)},${a.toFixed(3)}),1-(1-${g})*(t-${(a - RAMP_A).toFixed(3)})/${RAMP_A},` +
         `if(between(t,${a.toFixed(3)},${b.toFixed(3)}),${g},` +
         `if(between(t,${b.toFixed(3)},${(b + RAMP_R).toFixed(3)}),${g}+(1-${g})*(t-${b.toFixed(3)})/${RAMP_R},`; });
const expr = seg.join('') + '1' + ')))'.repeat(seg.length);
fc += `[${imgs.length}:a]adelay=${Math.round(LEAD * 1000)}|${Math.round(LEAD * 1000)},apad=whole_dur=${TOTAL.toFixed(3)},aresample=48000[vo];`;
fc += `[${imgs.length + 1}:a]aresample=48000,loudnorm=I=${gapLUFS}:TP=-6:LRA=11,atrim=0:${TOTAL.toFixed(3)},volume='${expr}':eval=frame,` +
      `afade=t=in:d=${SHUTTER},afade=t=out:st=${(TOTAL - 1.2).toFixed(3)}:d=1.2[bed];[vo][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]`;
run(...inputs, '-i', audio, '-i', MUSIC, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-t', TOTAL.toFixed(3), `${OUT}/${N}.mp4`);
fs.writeFileSync(`${OUT}/${N}.spans.json`, JSON.stringify({ source: `${N}.mp4`, unit: 's', spans: speech.map(([a, b]) => [+(a + LEAD).toFixed(3), +(b + LEAD).toFixed(3)]) }, null, 1));
console.log(JSON.stringify({ card: N, starts: starts.map(t => +t.toFixed(2)), total: +TOTAL.toFixed(2), bars: Math.round(TOTAL / BAR), voiceLUFS: +vol, gapLUFS: +gapLUFS, duckDB: +duckDB.toFixed(1) }));
