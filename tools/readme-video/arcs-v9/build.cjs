// arcs-v9 README walkthrough: HTML cards -> Playwright PNGs, narration takes (or macOS `say` as a free draft), ffmpeg.
// Source: README.md at the repo root (approved by Zach 2026-11-01, PR 1924). The video may say only what it says.
// Type comes from the kit tokens (src/ui-kit/recoil-report/_tokens.css), inlined verbatim; sizes are ramp tokens only.
const path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || path.join(ROOT, 'node_modules/playwright'));
const { execFileSync } = require('child_process');
const fs = require('fs');
const OUT = __dirname + '/out';
fs.mkdirSync(OUT, { recursive: true });

const tokens = fs.readFileSync(path.join(ROOT, 'src/ui-kit/recoil-report/_tokens.css'), 'utf8');
// One root size per render target (16:9 at 1920x1080): 1rem = 40px, so every ramp step scales with the frame.
// Title-safe margins: 5 percent of each edge.
const css = `${tokens}
:root { --fs-meta: 0.8125rem; }
* { box-sizing: border-box; }
html { font-size: 40px; }
body { margin: 0; width: 1920px; height: 1080px; background: var(--bg); color: var(--text); font-family: var(--ds-font-sans);
  font-size: var(--fs-body); line-height: 1.5; padding: 54px 96px; display: flex; flex-direction: column; justify-content: center; }
h3 { font-family: var(--ds-font-mono); font-size: var(--fs-label); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--cyan); margin: 0 0 0.6rem; }
h1 { font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.15; margin: 0 0 0.5rem; text-wrap: balance; }
h2 { font-size: var(--fs-headline); font-weight: 500; line-height: 1.3; margin: 0 0 0.7rem; text-wrap: balance; }
.lede { font-family: var(--ds-font-display); font-size: var(--fs-headline); color: var(--text-secondary); margin: 0 0 0.8rem; }
p, li { margin: 0 0 0.3rem; text-wrap: pretty; }
ul { margin: 0; padding: 0; list-style: none; }
li { padding: 0.25rem 0; border-top: 1px solid var(--border); }
li:first-child { border-top: 0; }
.m { font-family: var(--ds-font-mono); color: var(--cyan); }
.lab { font-family: var(--ds-font-mono); text-transform: uppercase; letter-spacing: 0.06em; display: inline-block; width: 6.2rem; }
.g { color: var(--green); } .y { color: var(--gold); } .o { color: var(--orange); }
.ref { font-family: var(--ds-font-mono); font-size: var(--fs-meta); color: var(--dimmed); margin-top: 0.8rem; }
pre { font-family: var(--ds-font-mono); font-size: var(--fs-body); background: var(--elevated); border: 1px solid var(--border);
  border-radius: var(--ds-r-md); padding: 0.6rem 0.9rem; margin: 0 0 0.6rem; white-space: pre-wrap; }`;

const S = [
  { k: 'What it is', h: 'ARCS', b: `<p class="lede">Helps you think through one hard decision.</p><ul><li>One next step, the reasons, 3 follow-up questions</li><li>A label for how settled the answer is</li><li>It does not decide for you: the final call stays yours</li></ul><p class="ref">▲ README, first screen</p>`,
    v: 'Arcs helps you think through one hard decision. You type the question. It gives back one next step, the reasons for it, three follow-up questions, and a label for how settled the answer is. It does not make the decision for you. The final call stays yours.' },
  { k: 'How it works', h: 'One Claude call, a prompt that walks 6 steps', b: `<ul><li>Is this a real decision?</li><li>The strongest objections</li><li>Evidence and prior odds</li><li>A false premise, or overconfidence?</li><li>A confidence score, 0 to 100</li><li>One next step, up to 3 reasons</li></ul><p class="ref">▲ src/app/api/compass/route.ts, the PIPELINE block</p>`,
    v: 'Each question gets one Claude call, with a prompt that walks six steps. Is this a real decision, and what are the strongest objections? What evidence bears on it? Is it built on a false premise? An honest confidence score, from zero to one hundred. Then one next step, and up to three reasons.' },
  { k: 'How settled is it', h: 'Code, not the model, sets the label', b: `<ul><li><span class="lab g">Green</span> No warning, confidence 65 or more</li><li><span class="lab y">Yellow</span> A caution, or under 65</li><li><span class="lab">Fork</span> 2 or more workable paths</li><li><span class="lab">Paradox</span> Exactly 2 paths, under 60</li><li><span class="lab">Delta</span> Blocking objection, ruin risk, or confidence moved</li><li><span class="lab">Scratch</span> You feel lost, or under 40 with no fork</li></ul><p class="ref">▲ src/lib/ygate.ts</p>`,
    v: 'Plain code, not the model, then labels how settled the answer is. Green means no warning fired, and confidence is sixty five or more. Yellow means a caution, or confidence under sixty five. Fork means two or more workable paths. Paradox means exactly two paths, with confidence under sixty. The table has the rest.' },
  { k: 'What is proven', h: 'What you can check', b: `<ul><li><span class="g">▲</span> 17 of 17 tests pass on the labeling code</li><li><span class="g">▲</span> The app is live</li><li><span class="g">▲</span> A reader with no memory rebuilt 17 of 19 parts of one incident, about 90%</li><li><span class="o">⚑</span> One incident, not the whole repo</li><li><span class="g">▲</span> This README was read cold, claim by claim</li></ul><p class="ref">▲ tests/unit/ygate.test.ts · runtime/audit/ · arcs.care</p>`,
    v: 'Here is what you can check. All seventeen tests on the labeling code pass. The app is live. A reader with no memory rebuilt seventeen of nineteen parts of one incident from the repo history alone, about ninety percent. That is one incident, not the whole repo. And this read me was itself read cold, and checked claim by claim.' },
  { k: 'Not built', h: 'Or not what it may sound like', b: `<ul><li>The canon describes 8 layers; the app runs 6</li><li>The Observatory replays this build’s own history, not your decisions</li><li><span class="m">operators/</span> is a reference library, not wired into the live compass</li><li>The Python CLI needs your own scan files</li></ul><p class="ref">▲ README, not built · Python CLI</p>`,
    v: 'Some things are not what they may sound like. The canon describes eight layers, and the app runs six. The Observatory is a demo that replays a fixed dataset about this build, not your decisions. The operators folder is a reference library, not wired into the live compass. And the Python command line needs your own scan files.' },
  { k: 'Try it', h: 'Open the compass', b: `<pre>app.arcs.care  →  Open the compass</pre><ul><li>No account needed. Anonymous answers live only in your browser tab</li><li>Signed in, each run is saved as a receipt</li><li>Wider access by waitlist</li><li>Locally: Node 22.6 or later, Postgres, <span class="m">npm run dev</span></li></ul><p class="ref">▲ README, try it and run it locally</p>`,
    v: 'Open app dot arcs dot care, and choose open the compass. No account is needed. Anonymous answers live only in your browser tab, and are not stored. If you are signed in, each run is saved as a receipt. Wider access opens in stages, through a waitlist. To run it locally, you need Node and a Postgres database.' },
];

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const parts = [];
  for (let i = 0; i < S.length; i++) {
    const s = S[i], n = String(i + 1).padStart(2, '0');
    const head = i === 0 ? `<h1>${s.h}</h1>` : `<h2>${s.h}</h2>`;  // display H1 on the title frame only
    const html = `<html lang="en"><head><meta charset="utf-8"><style>${css}</style></head><body><h3>${s.k}</h3>${head}${s.b}</body></html>`;
    fs.writeFileSync(`${OUT}/${n}.html`, html);
    await pg.setContent(html);
    await pg.screenshot({ path: `${OUT}/${n}.png` });
    // Zach's own takes in voice/NN.<ext> win; otherwise fall back to `say` (a free draft, never the shipped voice).
    const own = ['m4a', 'wav', 'mp3', 'aiff'].map(e => `${__dirname}/voice/${n}.${e}`).find(f => fs.existsSync(f));
    if (!own) execFileSync('say', ['-v', 'Samantha', '-r', '175', '-o', `${OUT}/${n}.aiff`, s.v]);
    // Card time = take + 0.8 s pad, exactly (rule R8; never -shortest on a looped still).
    const take = own || `${OUT}/${n}.aiff`;
    const dur = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', take]).toString()) + 0.8;
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-loop', '1', '-i', `${OUT}/${n}.png`, '-i', take,
      '-af', 'apad=pad_dur=0.8', '-c:v', 'libx264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', dur.toFixed(3), `${OUT}/${n}.mp4`]);
    parts.push(`file '${OUT}/${n}.mp4'`);
  }
  await b.close();
  fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', `${OUT}/walkthrough.mp4`]);
  console.log('ok', `${OUT}/walkthrough.mp4`);
})();
