// Live page editor walkthrough: HTML cards -> Playwright PNGs, narration takes (or macOS `say` as a free draft), ffmpeg.
// Source: src/ui-kit/tabbed-brief/README.md, section "Tuning by hand (internal only)" (PR 2136). The video may say only what it says.
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
h1 { font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.3; margin: 0 0 0.5rem; text-wrap: balance; }
h2 { font-size: var(--fs-headline); font-weight: 500; line-height: 1.3; margin: 0 0 0.7rem; text-wrap: balance; }
.lede { font-family: var(--ds-font-display); font-size: var(--fs-headline); line-height: 1.5; color: var(--text-secondary); margin: 0 0 0.8rem; }
p, li { margin: 0 0 0.3rem; text-wrap: pretty; }
ul { margin: 0; padding: 0; list-style: none; }
li { padding: 0.12rem 0; border-top: 1px solid var(--border); }
li:first-child { border-top: 0; }
.m { font-family: var(--ds-font-mono); color: var(--cyan); }
.lab { font-family: var(--ds-font-mono); text-transform: uppercase; letter-spacing: 0.06em; display: inline-block; width: 7.6rem; }
.score { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 0.4rem 0 0.2rem; }
.score > div { border-top: 1px solid var(--border); padding-top: 0.4rem; }
.score .n { display: block; font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.1; }
.score .t { display: block; color: var(--text-secondary); }
.g { color: var(--green); } .y { color: var(--gold); } .o { color: var(--orange); }
.ref { font-family: var(--ds-font-mono); font-size: var(--fs-meta); color: var(--dimmed); margin-top: 0.8rem; }
pre { font-family: var(--ds-font-mono); font-size: var(--fs-body); background: var(--elevated); border: 1px solid var(--border);
  border-radius: var(--ds-r-md); padding: 0.6rem 0.9rem; margin: 0 0 0.6rem; white-space: pre-wrap; }`;

const S = [
  { k: 'What it is', h: 'Edit the page, change the source', b: `<p class="lede">Edit a rendered page; the change goes to its source.</p><ul><li><span class="m">Route 1</span> the builder: every slider, text by data field</li><li><span class="m">Route 2</span> the bookmarklet: any page, text only</li><li><span class="o">⚑</span> A built page is never edited by hand</li></ul><p class="ref">▲ tabbed-brief/README.md · Tuning by hand</p>`,
    v: 'A live page editor. Move the sliders and edit the text on the page itself. A built page is never edited by hand, so the change goes to its source. Two ways in: the builder, or the bookmarklet.' },
  { k: 'Route 1, the builder', h: 'Build an internal copy, then open it', b: `<pre>python3 scripts/tabbed_brief_build.py DATA.json \\
  --tune /some/scratch/name.html
python3 -m http.server --directory /some/scratch
# then open name.html with ?tune&amp;edit</pre><ul><li><span class="o">⚑</span> Refuses any path under <span class="m">public/</span></li><li>The same two flags work on every page builder</li></ul><p class="ref">▲ README, route 1 · scripts/page_tune.py</p>`,
    v: 'Route one. Run the page’s builder with the tune flag. It writes an internal copy, and refuses the public folder. Serve that folder, then open the copy with tune and edit in the address. The same two flags work on every page builder.' },
  { k: 'Route 1, the builder', h: 'Edit, copy, hand it back', b: `<ul><li>Double-click text to edit it</li><li>Sliders: line height, section rhythm, card gap, letter-spacing, body size, breakpoints, wrapping</li><li>Copy edits · Copy JSON · Copy CSS · Drop breadcrumb, then Export versions</li></ul><pre>python3 scripts/tabbed_brief_build.py DATA.json \\
  --apply FILE</pre><p class="ref">▲ README, route 1 · if any part is refused, nothing is written</p>`,
    v: 'Double-click text to edit it. Move the sliders. Then copy what changed: the edits, the JSON patch, the CSS line, or a breadcrumb’s versions. Save it to a file, and run the same builder with apply. It validates, then rebuilds. If any part is refused, nothing is written.' },
  { k: 'Where it lands', h: 'Each part goes back where it is written', b: `<ul><li style="display: grid; grid-template-columns: 4.4rem 1fr; padding: 0.3rem 0;"><span class="lab" style="width: auto;">Text</span><span>to the first source that holds it</span></li><li style="display: grid; grid-template-columns: 4.4rem 1fr; padding: 0.3rem 0;"><span class="lab" style="width: auto;">Style</span><span>tokens and wrapping to the place the builder names, usually a tuned block</span></li><li><span class="o">⚑</span> No tuner tokens on the page: token changes are refused</li><li><span class="o">⚑</span> Text the builder computes is in no source: refused and named</li></ul><p class="ref">▲ README, the builder table · scripts/page_tune.py</p>`,
    v: 'Where does each change land? Text goes back to the first source that holds it. Tokens and wrapping go to the place the builder names, usually a tuned block; a page with no tuner tokens refuses them. Computed text is in no source, so it is refused, and named.' },
  { k: 'Route 2, the bookmarklet', h: 'Any page, text only', b: `<pre>python3 scripts/tune_serve.py
# open http://127.0.0.1:8799/ and drag “ARCS tune”
python3 scripts/tune_serve.py --apply URL edits.json</pre><ul><li>Click it on any page</li><li><span class="o">⚑</span> A built file: it refuses and names the script</li><li><span class="o">⚑</span> JS-side breakpoints do not follow the slider; CSS <span class="m">@media</span> rules do</li></ul><p class="ref">▲ README, route 2 · scripts/tune_serve.py</p>`,
    v: 'Route two. Run tune serve, open its local page, and drag the bookmarklet to your bookmarks bar. Click it on any page; the page never carries the tuner. Copy your edits, then apply them by URL. Built by a script? It refuses, and names the script.' },
  { k: 'The guards', h: 'What stops a bad write', b: `<ul><li><span class="o">⚑</span> Old text must be found exactly once in the source, or nothing is written</li><li><span class="o">⚑</span> <span class="m">page_gate.py --counterpart</span> fails any page that still carries the tuner</li><li><span class="o">⚑</span> A moved container width is reported “set in source by hand”; it is not written</li></ul><p class="ref">▲ README, guards</p>`,
    v: 'What stops a bad write? Old text must be found exactly once in the source, or nothing is written. The page gate, in counterpart mode, fails any page that still carries the tuner. And a moved container width is reported, set in source by hand. It is not written.' },
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
  // Tail: the last card's frame holds 1.7 s more and fades to black, so the close lands instead of cutting off.
  const lastPng = `${OUT}/${String(S.length).padStart(2, '0')}.png`;
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-loop', '1', '-i', lastPng, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
    '-vf', 'fade=t=out:st=0.2:d=1.5', '-c:v', 'libx264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', '1.7', `${OUT}/tail.mp4`]);
  parts.push(`file '${OUT}/tail.mp4'`);
  fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', `${OUT}/walkthrough.mp4`]);
  console.log('ok', `${OUT}/walkthrough.mp4`);
})();
