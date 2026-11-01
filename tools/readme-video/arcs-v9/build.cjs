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
// One root size per render target (16:9 at 1920x1080): 1rem = 54px, sized so body text stays legible on a phone-width player.
// Title-safe margins: 5 percent of each edge.
const css = `${tokens}
:root { --fs-meta: 0.8125rem; }
* { box-sizing: border-box; }
html { font-size: 54px; }
body { margin: 0; width: 1920px; height: 1080px; background: var(--bg); color: var(--text); font-family: var(--ds-font-sans);
  font-size: var(--fs-body); line-height: 1.5; padding: 54px 96px; display: flex; flex-direction: column; justify-content: center; }
h3 { font-family: var(--ds-font-mono); font-size: var(--fs-label); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--cyan); margin: 0 0 0.6rem; }
h1 { font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.15; margin: 0 0 0.5rem; text-wrap: balance; }
h2 { font-size: var(--fs-headline); font-weight: 500; line-height: 1.3; margin: 0 0 0.7rem; text-wrap: balance; }
.lede { font-family: var(--ds-font-display); font-size: var(--fs-headline); color: var(--text-secondary); margin: 0 0 0.8rem; }
p, li { margin: 0 0 0.3rem; text-wrap: pretty; }
ul { margin: 0; padding: 0; list-style: none; }
li { padding: 0.12rem 0; border-top: 1px solid var(--border); }
li:first-child { border-top: 0; }
.m { font-family: var(--ds-font-mono); color: var(--cyan); }
.lab { font-family: var(--ds-font-mono); text-transform: uppercase; letter-spacing: 0.06em; display: inline-block; width: 6.2rem; }
.score { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 0.4rem 0 0.2rem; }
.score > div { border-top: 1px solid var(--border); padding-top: 0.4rem; }
.score .n { display: block; font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.1; }
.score .t { display: block; color: var(--text-secondary); }
.g { color: var(--green); } .y { color: var(--gold); } .o { color: var(--orange); }
.ref { font-family: var(--ds-font-mono); font-size: var(--fs-meta); color: var(--dimmed); margin-top: 0.8rem; }
pre { font-family: var(--ds-font-mono); font-size: var(--fs-body); background: var(--elevated); border: 1px solid var(--border);
  border-radius: var(--ds-r-md); padding: 0.6rem 0.9rem; margin: 0 0 0.6rem; white-space: pre-wrap; }`;

const S = [
  { k: 'What it is', h: 'ARCS', b: `<p class="lede">Helps you think through one hard decision.</p><div class="score"><div><span class="n">17 of 17</span><span class="t"><span class="g">▲</span> tests pass</span></div><div><span class="n">1</span><span class="t">Claude call each</span></div><div><span class="n">6</span><span class="t">labels, set by code</span></div></div><p class="ref">▲ README, first screen · what happens when you ask</p>`,
    v: 'Arcs helps you think through one hard decision. You ask. It answers with one next step, and a label for how settled that answer is. And you can check it. Seventeen of seventeen tests pass on the code that sets the label. The final call stays yours.' },
  { k: 'Try it', h: 'Open the compass, no account needed', b: `<pre>app.arcs.care  →  Open the compass</pre><ul><li>Anonymous answers live only in your browser tab</li><li>Signed in, each run is saved as a receipt</li><li>Wider access by waitlist</li><li>Run it locally: Node and Postgres</li></ul><p class="ref">▲ README, try it · run it locally</p>`,
    v: 'Try it now. Open app dot arcs dot care, and choose open the compass. No account is needed. Anonymous answers live only in your browser tab, and are not stored. Sign in, and each run is saved as a receipt. To run it yourself, you need Node and a Postgres database.' },
  { k: 'How it works', h: 'One Claude call, a prompt that walks 6 steps', b: `<ul><li>Is this a real decision?</li><li>The strongest objections</li><li>Evidence and prior odds</li><li>A false premise, or overconfidence?</li><li>A confidence score, 0 to 100</li><li>One next step, up to 3 reasons</li></ul><p class="ref">▲ src/app/api/compass/route.ts</p>`,
    v: 'Behind each answer is one Claude call. Its prompt walks six steps. Is this a real decision? What are the strongest objections? What evidence bears on it? Is the premise false? Then an honest confidence score. And finally, one next step.' },
  { k: 'How settled is it', h: 'Code, not the model, sets the label', b: `<ul><li><span class="lab g">Green</span> No warning, confidence 65 or more</li><li><span class="lab y">Yellow</span> A caution, or under 65</li><li><span class="lab">Fork</span> 2 or more workable paths</li><li><span class="lab">Paradox</span> Exactly 2 paths, under 60</li><li><span class="lab">Delta</span> Blocking objection, ruin risk, or confidence moved</li><li><span class="lab">Scratch</span> You feel lost, or under 40 with no fork</li></ul><p class="ref">▲ src/lib/ygate.ts</p>`,
    v: 'Then plain code, not the model, labels how settled the answer is. Green, when it holds up. Yellow, when a caution fires. Fork, paradox, delta and scratch name the other ways it can be unsettled. The exact rules are on screen.' },
  { k: 'What is proven', h: 'What you can check', b: `<ul><li><span class="g">▲</span> 17 of 17 tests pass on the labeling code</li><li><span class="g">▲</span> The app is live</li><li><span class="g">▲</span> A reader with no memory rebuilt 17 of 19 parts of one incident, about 90%</li><li><span class="o">⚑</span> One incident, not the whole repo</li></ul><p class="ref">▲ tests/unit/ygate.test.ts · runtime/audit/</p>`,
    v: 'So what can you check? All seventeen tests on the labeling code pass. The app is live. And a reader with no memory rebuilt seventeen of nineteen parts of one incident, from the repo history alone. About ninety percent. One incident, not the whole repo.' },
  { k: 'Not built', h: 'Or not what it may sound like', b: `<ul><li>The canon describes 8 layers; the app runs 6</li><li>The Observatory replays this build’s own history, not your decisions</li><li><span class="m">operators/</span> is a reference library, not wired into the live compass</li></ul><p class="ref">▲ README, not built</p>`,
    v: 'Some things are not what they may sound like. The app runs six of the eight layers the canon describes. The Observatory replays the history of this build, not your decisions. The operators folder is a reference library, not wired in. And the final call stays yours.' },
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
