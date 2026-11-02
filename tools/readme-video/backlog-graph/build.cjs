// Backlog graph, glass box: an animated explainer that follows one real row up the five layers.
// Every motion is a state change the tools really make (SOURCE.md); nothing moves for show.
//
//   node tools/readme-video/backlog-graph/build.cjs            page only (out/video.html)
//   node tools/readme-video/backlog-graph/build.cjs --render   page + silent MP4 (out/animatic.mp4) + stills
//
// Card time: with voice/NN.mp3 present, each card holds its take plus 0.8 s (rule R8); without, an estimate at
// 2.7 words per second plus the pad, which is what the silent animatic uses. No API key or voice id is read here.
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const DIR = __dirname;
const ROOT = path.resolve(DIR, '../../..');
const OUT = path.join(DIR, 'out');
const TODAY = '2026-11-02';
const HERO = 'doc-gate-false-positive-cleanup';
const PAD = 0.8;

const CARDS = [
  { k: 'cold open', h: '438 rows. What do I do next?',
    b: `<p class="lede">One file, one row per line and no order yet.</p>`,
    v: 'Four hundred thirty eight rows in one backlog. What do I do next?' },
  { k: '1 · Source', h: 'One row, one line of JSON',
    b: `<pre class="code" id="row"><span class="dim">_QUEUE/induced-backlog.jsonl, line 99</span>
{"id": "doc-gate-false-positive-cleanup",
 "jtbd": "Clean the existing false positives the 4 doc gates
          report … so a blocking switch would not red every PR.",
 "state": "OPEN",
 "depends_on": ["doc-gates-advisory-ci"],
 "fates": ["landed", "withdrawn"]}</pre>`,
    v: 'Each row is one line of JSON: a job, a state, what it waits on. Follow this one. Its job: clear false alarms from four doc gates so they can block.' },
  { k: '2 · Gates', h: 'A shape check, not a merit check',
    b: `<pre class="code" id="tcopy"><span class="dim">test copy</span>
 "state": "<span id="st">OPEN</span>",</pre>
<pre class="term" id="term"><span class="dim">$ backlog_status_check.py --check --file test-copy.jsonl</span>
<span class="red l1">FAIL  line 99 doc-gate-false-positive-cleanup:
      RUNNING requires &grave;claimed_by&grave;</span>
<span class="red l2">FAIL  line 99 doc-gate-false-positive-cleanup:
      RUNNING requires &grave;claimed_at&grave;</span>
<span class="red l3">exit 1</span></pre>`,
    v: 'First, a shape check. On a test copy, I marked it running with no name. The gate refused, and said why. Shape, not merit.' },
  { k: '3 · Graph build', h: 'Edges, then waves',
    b: `<div class="chain" id="chain">
<div class="node n0"><span class="g green">▲</span> doc-gates-advisory-ci<em>done</em></div>
<div class="node n1 hero">doc-gate-false-positive-cleanup<em>wave 0</em></div>
<div class="node n2">doc-gates-blocking<em>wave 1</em></div>
</div><p class="ref" id="edgeref">edges: depends_on + unblocks, inverted · scripts/backlog_graph.py</p>`,
    v: 'Then the graph. Edges come from depends on. Finished rows drop out. The rest sort into waves by their longest chain. This row’s one dependency is done, so it sits in wave zero. One row waits on it.' },
  { k: '4 · Outputs', h: 'Ready now: 11 rows',
    b: `<div class="card" id="out">
<div class="crow"><span class="g green">▲</span> <b>doc-gate-false-positive-cleanup</b></div>
<div class="grid"><span class="lab">wave</span><span>0</span><span class="lab">trigger</span><span>RIPE</span>
<span class="lab">tool fit</span><span class="green">HAVE</span><span class="lab">tier cue</span><span>2</span></div>
<div class="tools">scripts/integrity_gate.py · scripts/integrity_gate_selftest.py · canon_propagation_check.py</div>
</div><p class="ref" id="outref">no model calls · same file in, same order out</p>`,
    v: 'Eleven rows can start now. This is one. Its tools all resolve in the repo, so it is marked have. No model was called. The same file gives the same order.' },
  { k: '5 · Fate', h: 'The script stops here',
    b: `<pre class="code" id="claim"><span class="dim">test copy</span>
 "state": "<span id="st2">OPEN</span>",
 "claimed_by": "<span id="cb"></span>",
 "claimed_at": "<span id="ca"></span>"</pre>
<pre class="term" id="term2"><span class="dim">gate, same test copy:</span> <span class="green l1">exit 0</span></pre>
<p class="serif" id="decide">The script orders. A person decides.</p>
<p class="ref" id="tref">~ shown on a test copy; the real row is still OPEN and unclaimed</p>`,
    v: 'Here the script stops. It orders. A person decides. A claim writes a name and a time, and the gate passes. Landed or withdrawn is a person’s call.' },
  { k: 'the thin spot', h: 'Most rows have no edge yet',
    b: `<div class="stats" id="stats"><div><span class="big">224 of 320</span><span class="lab">active rows in wave 0</span></div>
<div class="s2"><span class="big gold">178</span><span class="lab">with no edge at all</span></div></div>
<pre class="code" id="fix"><span class="dim">the fix lives in the rows, not the script</span>
 "depends_on": ["…"]</pre>`,
    v: 'Now the thin spot. Two hundred twenty four of three hundred twenty active rows sit in wave zero, and one hundred seventy eight have no edge at all. So the order there is ranking, not dependency. The fix is in the rows: write depends on.' },
  { k: 'glass box', h: 'backlog_graph.py',
    b: `<ul class="close" id="close">
<li><span class="g green">▲</span> Deterministic, no model calls</li>
<li><span class="g green">▲</span> Gates check shape, not merit</li>
<li><span class="g green">▲</span> A person decides every fate</li>
<li><span class="g gold">~</span> Shallow graph: 178 rows with no edge, named</li></ul>
<p class="ref">python3 scripts/backlog_graph.py --today ${TODAY}</p>`,
    v: 'No model calls. Gates on shape. A person on every fate. And it names its own thin spot.' },
];

function take(i) {
  for (const ext of ['mp3', 'm4a', 'wav', 'aiff']) {
    const f = path.join(DIR, 'voice', `${String(i + 1).padStart(2, '0')}.${ext}`);
    if (fs.existsSync(f)) return { f, d: +execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString() };
  }
  return null;
}

// Real data, read fresh: the graph's nodes and the file's states. Ids leave the build only for the three named rows.
function data() {
  const g = JSON.parse(execFileSync('python3', [path.join(ROOT, 'scripts/backlog_graph.py'), '--today', TODAY, '--json'], { cwd: ROOT, maxBuffer: 64 << 20 }));
  const named = new Set([HERO, 'doc-gates-blocking']);
  const nodes = g.nodes.map((n) => ({ w: n.wave, r: n.ready_now ? 1 : 0, iso: (!n.deps.length && !n.descendants) ? 1 : 0,
    id: named.has(n.id) ? n.id : '' }));
  const rows = fs.readFileSync(path.join(ROOT, '_QUEUE/induced-backlog.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter((r) => r.id);
  const term = rows.filter((r) => ['DONE', 'COMPOSTED', 'SUPERSEDED'].includes(r.state)).length;
  return { rows: rows.length, active: g.active, waves: g.critical_path_waves, terminal: term, nodes };
}

const WPS = 2.7;
const cards = CARDS.map((c, i) => {
  const t = take(i);
  const words = c.v.split(/\s+/).length;
  return { ...c, dur: +(((t ? t.d : words / WPS)) + PAD).toFixed(2), take: t && path.relative(DIR, t.f) };
});

fs.mkdirSync(OUT, { recursive: true });
const tpl = fs.readFileSync(path.join(DIR, 'video.tpl.html'), 'utf8');
const tokens = fs.readFileSync(path.join(ROOT, 'src/ui-kit/recoil-report/_tokens.css'), 'utf8');
const html = tpl.replace('/*__TOKENS__*/', tokens).replace('/*__DATA__*/null', JSON.stringify({ cards, ...data() }));
fs.writeFileSync(path.join(OUT, 'video.html'), html);
const total = cards.reduce((s, c) => s + c.dur, 0);
console.log(`wrote out/video.html: ${cards.length} cards, ${total.toFixed(1)} s (${cards.every((c) => c.take) ? 'takes' : 'estimated at ' + WPS + ' wps'})`);

if (process.argv.includes('--render')) {
  execFileSync('node', [path.join(ROOT, 'scripts/html_video_render.mjs'), path.join(OUT, 'video.html'), path.join(OUT, 'animatic.mp4'),
    '--w', '1920', '--h', '1080', '--fps', '30', '--poster', '40'], { cwd: ROOT, stdio: 'inherit' });
  // Voiced cut: each take followed by the pad as silence (R8), concatenated, then muxed under the picture.
  if (cards.every((c) => c.take)) {
    const inputs = cards.flatMap((c) => ['-i', path.join(DIR, c.take)]);
    const chain = cards.map((c, i) => `[${i}:a]aresample=44100,apad=pad_dur=${PAD},atrim=0:${c.dur}[a${i}]`).join(';');
    const cat = cards.map((_, i) => `[a${i}]`).join('') + `concat=n=${cards.length}:v=0:a=1[aout]`;
    const wav = path.join(OUT, 'narration.wav');
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', `${chain};${cat}`, '-map', '[aout]', wav]);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(OUT, 'animatic.mp4'), '-i', wav, '-map', '0:v', '-map', '1:a',
      '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', path.join(OUT, 'backlog-graph-glassbox.mp4')]);
    console.log('wrote out/backlog-graph-glassbox.mp4 (voiced)');
  }
}
