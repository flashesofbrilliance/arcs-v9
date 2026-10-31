// Fluid timing for a whole video (the card 04 sample, approved, rolled out). Reads the PNG states that
// bp-build.cjs / mo-build.cjs render with STILLS=1, writes the VOICE-ONLY video and its spans sidecar;
// mix.sh adds the music ride and the song. Usage: node fluid-build.cjs bp|mo
const { execFileSync } = require('child_process');
const fs = require('fs');
const K = require('./kit.cjs');
const SET = process.argv[2] || 'bp';
const V = __dirname;
const CFG = { bp: { dir: `${V}/out/bp`, voice: `${V}/voice`, script: `${V}/voice/SCRIPT.md`, name: 'walkthrough-fluid' },
              mo2: { dir: `${V}/out/mo2`, voice: `${V}/makingof/voice-v2`, script: `${V}/makingof/SCRIPT-v2.md`, name: 'makingof-v2-fluid' },
              cap: { dir: `${V}/out/cap`, voice: `${V}/capture/voice`, script: `${V}/capture/SCRIPT.md`, name: 'capture-a3' },
              rc: { dir: `${V}/out/rc`, voice: `${V}/recut/voice`, script: `${V}/recut/SCRIPT.md`, name: 'walkthrough-recut' },
              mo: { dir: `${V}/out/mo`, voice: `${V}/makingof/voice`, script: `${V}/makingof/SCRIPT.md`, name: 'makingof-fluid' } }[SET];
const OUT = `${V}/out/fluid/${SET}`;
fs.mkdirSync(OUT, { recursive: true });
const LEAD = 0.4, TAIL = 0.6, CHIP = 1.8, BAR = 60 / 161.5 * 4, SHUTTER = 0.65, QUICK = 0.24;
const run = (...a) => execFileSync('ffmpeg', ['-hide_banner', '-y', '-loglevel', 'error', ...a]);
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const script = fs.readFileSync(CFG.script, 'utf8');
const sentencesOf = n => script.split(/^## /m).find(s => s.startsWith(n)).split('\n\n')[1].split('\n')
  .filter(l => l.trim() && !l.startsWith('Chip:')).join(' ').trim().split(/(?<=[.!?]["”]?)\s+/);

const parts = [], spans = []; let t0 = 0;
const NCARDS = script.split(/^## /m).length - 1;
for (let i = 1; i <= NCARDS; i++) {
  const n = String(i).padStart(2, '0'), audio = `${CFG.voice}/${n}.mp3`, D = dur(audio);
  // sentence starts: word-share estimate snapped to the nearest measured pause end
  const sents = sentencesOf(n), take = K.voiceSpans(audio, D), ends = take.slice(1).map(s => s[0]);
  const words = sents.map(s => s.split(/\s+/).length), W = words.reduce((a, c) => a + c, 0);
  const starts = sents.map((_, k) => { if (!k) return 0;
    const est = words.slice(0, k).reduce((a, c) => a + c, 0) / W * D;
    const near = ends.reduce((b, t) => Math.abs(t - est) < Math.abs(b - est) ? t : b, ends[0] ?? est);
    return Math.abs(near - est) < 1.5 ? near : est; });
  // states: bp-build writes NN.ats.json (state k -> sentence); making-of states follow sentence order
  const atsFile = `${CFG.dir}/${n}.ats.json`;
  const pngs = fs.readdirSync(CFG.dir).filter(f => new RegExp(`^${n}-\\d+\\.png$`).test(f)).sort((a, b) => parseInt(a.split('-')[1]) - parseInt(b.split('-')[1]));
  const ats = fs.existsSync(atsFile) ? JSON.parse(fs.readFileSync(atsFile)) : pngs.map((_, k) => k);
  const at = ats.map((s, k) => k === 0 ? 0 : LEAD + starts[Math.min(s, starts.length - 1)] - QUICK);
  const tChip = LEAD + D + TAIL, TOTAL = Math.ceil((tChip + CHIP) / BAR) * BAR;
  const imgs = [...pngs.map(f => `${CFG.dir}/${f}`), `${CFG.dir}/${n}-chip.png`]; at.push(tChip);
  const inputs = []; imgs.forEach((f, k) => inputs.push('-loop', '1', '-t', ((k + 1 < at.length ? at[k + 1] : TOTAL) - at[k] + QUICK).toFixed(3), '-i', f));
  let fc = '', prev = '[0:v]';
  for (let k = 1; k < imgs.length; k++) { const d = k === imgs.length - 1 ? SHUTTER * 0.6 : QUICK;
    fc += `${prev}[${k}:v]xfade=transition=fade:duration=${d.toFixed(3)}:offset=${at[k].toFixed(3)}[v${k}];`; prev = `[v${k}]`; }
  fc += `${prev}fade=t=in:d=${SHUTTER},fade=t=out:st=${(TOTAL - SHUTTER).toFixed(3)}:d=${SHUTTER},format=yuv420p[v];`;
  fc += `[${imgs.length}:a]adelay=${LEAD * 1000}|${LEAD * 1000},apad=whole_dur=${TOTAL.toFixed(3)},aresample=48000[a]`;
  run(...inputs, '-i', audio, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', TOTAL.toFixed(3), `${OUT}/${n}.mp4`);
  for (const [a, b] of take) spans.push([+(t0 + LEAD + a).toFixed(3), +(t0 + LEAD + b).toFixed(3)]);
  parts.push(`file '${OUT}/${n}.mp4'`); t0 += TOTAL;
  console.log(n, 'bars', Math.round(TOTAL / BAR), 'starts', starts.map(t => t.toFixed(2)).join(','));
}
fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
const final = `${V}/out/${CFG.name}.mp4`;
run('-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', final);
fs.writeFileSync(final.replace(/\.mp4$/, '.spans.json'), JSON.stringify({ source: `${CFG.name}.mp4`, unit: 's', spans }, null, 1));
console.log('ok', final, 'total', t0.toFixed(2));
