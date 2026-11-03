// Bench video: 7 frames in rem HTML on the render typography rules (resonance rules doc, dcaa96f9):
// one root size per target, the four-step ramp plus --fs-meta for references, sentence-case source,
// caps only via CSS on short mono labels. A trust-boundary strip on every frame lights the zone the frame
// is about (the throughline). Frame 2 is trust-boundary.svg itself, so README, page and video agree.
// Voice: voice/NN.mp3 if present, else macOS `say`. Writes out/, out/bench.mp4 and SCRIPT.md.
// Each frame is checked before encode: ramp sizes only, at most 45 words, 3 sizes (meta exempt), 7 body lines.
// The previous kit build is build.kit.cjs.
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
// Shared glass-box frame (vid/kit/glass-frame.html), used as written: style into the head, template into the body.
const GF = fs.readFileSync(__dirname + '/../kit/glass-frame.html', 'utf8');
const gfCss = GF.match(/<style>([\s\S]*?)<\/style>/)[1], gfHtml = GF.match(/<template[^>]*>([\s\S]*?)<\/template>/)[1];
const OUT = __dirname + '/out';
fs.mkdirSync(OUT, { recursive: true });
const PAUSE = 1.8;
const TOKENS = fs.readFileSync('/Users/zharris/arcs-v9/.claude/worktrees/fervent-burnell-79a4e3/src/ui-kit/recoil-report/_tokens.css', 'utf8');
const MONO = fs.readFileSync('/Users/zharris/arcs-v9/.claude/worktrees/ai-product-ownership-roadmap-78910c/public/fonts/jetbrains-mono-normal-100-800-latin-v1.woff2').toString('base64');
const SVG = 'data:image/svg+xml;base64,' + fs.readFileSync(__dirname + '/trust-boundary.svg').toString('base64');

const css = `${TOKENS}
@font-face{font-family:'JetBrains Mono';src:url(data:font/woff2;base64,${MONO})}
@font-face{font-family:JBM;src:url(data:font/woff2;base64,${MONO})}
html{font-size:40px}
:root{--fs-label:.8rem}
*{box-sizing:border-box}
body{margin:0;width:48rem;height:27rem;padding:2.15rem 2.4rem 1.35rem;background:var(--bg);color:var(--text);font-family:var(--ds-font-sans);
 display:grid;grid-template-columns:1fr 7rem;grid-template-rows:auto 1fr auto;column-gap:2rem;
 background-image:linear-gradient(#11222f 1px,transparent 1px),linear-gradient(90deg,#11222f 1px,transparent 1px);background-size:1.5rem 1.5rem}
p,h1,h2{margin:0;text-wrap:pretty}
.lbl{font:700 var(--fs-label)/1.2 var(--ds-font-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--text-secondary)}
header{grid-column:1/3}
header .lbl{color:var(--cyan)}
h1{font:600 var(--fs-display)/1.15 var(--ds-font-mono);letter-spacing:-.01em;margin-top:.4rem}
h2{font:500 var(--fs-headline)/1.25 var(--ds-font-sans);margin-top:.4rem}
.lede{font:400 var(--fs-body)/1.4 var(--ds-font-sans);color:var(--text)}
.tag{font:700 var(--fs-label)/1 var(--ds-font-mono);display:inline-block;vertical-align:baseline;letter-spacing:.14em;text-transform:uppercase;color:var(--green);border:2px solid var(--green);padding:.05rem .3rem;margin-left:.5rem;white-space:nowrap}
main{display:flex;flex-direction:column;justify-content:flex-start;padding-top:1.1rem;gap:.5rem;min-width:0}
.b{font:400 var(--fs-body)/1.4 var(--ds-font-sans)}
.row{display:grid;grid-template-columns:9.5rem 1fr;column-gap:.6rem;align-items:baseline;border-bottom:1px solid var(--border);padding:.2rem 0}
.row:last-child{border-bottom:0}
.k{font:400 var(--fs-body)/1.4 var(--ds-font-mono);color:var(--text-secondary)}
.code{font:400 var(--fs-body)/1.4 var(--ds-font-mono);color:var(--cyan);background:var(--elevated);border:1px solid var(--border);border-radius:.15rem;padding:.4rem .6rem}
.stamps{display:flex;align-items:center;gap:.3rem;flex-wrap:wrap}
.st{border:2px solid currentColor;padding:.2rem .35rem}
.ok{color:var(--green)}.lim{color:var(--gold)}.fail{color:var(--red)}.say{color:var(--cyan)}
aside{display:flex;flex-direction:column;gap:.3rem;justify-content:center}
.z{border:1.5px solid var(--border);padding:.45rem .5rem;color:var(--text-secondary)}
.z.on{border-color:var(--cyan);color:var(--cyan);background:var(--surface)}
.z.m{border-style:dashed}.z.m.on{border-color:var(--gold);color:var(--gold)}
.wall{border-top:2px dashed var(--cyan);margin:.1rem -.4rem}
footer{grid-column:1/3;display:flex;justify-content:space-between;align-items:end;gap:1rem}
.ref{font:400 var(--fs-meta,0.8125rem)/1.3 var(--ds-font-mono);color:var(--dimmed)}
.chip{border:1.5px solid var(--green);background:var(--surface);color:var(--text);padding:.35rem .6rem}
.chip::before{content:'';display:inline-block;width:.3rem;height:.3rem;border-radius:50%;background:var(--green);margin-right:.4rem;vertical-align:middle}
.crop{overflow:hidden;height:16.6rem}.crop img{display:block;width:63rem;margin-top:-5.1rem}.c1{width:33.6rem}.c2{width:29.6rem}.c2 img{margin-left:-33.4rem}
.hide{visibility:hidden}`;

const ZONES = ['Code', 'Model', 'Check', 'Outcome'];
const strip = cur => `<aside><p class="lbl">Trust boundary</p>` + ZONES.map((z, i) =>
  `<p class="lbl z${i === 1 ? ' m' : ''}${cur.includes(i) ? ' on' : ''}">${z}</p>${i === 1 ? '<div class="wall"></div>' : ''}`).join('') + `</aside>`;
const row = (k, v, c = 'ok') => `<div class="row"><span class="k">${k}</span><span class="b ${c}">${v}</span></div>`;
const caught = (k, v) => `<div class="row"><span class="k">${k}</span><span class="b lim">${v}<span class="tag">caught</span></span></div>`;

// Each body item: [sentence index it appears on, html]. Order is screen order.
const S = [
  { title: 'The model proposes. Code checks.', h1: true, zone: [0, 1, 2, 3], chip: '5 of 5 mock cases pass · 8 of 8 faults caught',
    v: ["This engine answers questions about a short, fictional R F P and its amendment, written just for this sample.", "A model helps write the answers, but it never gets the last word. The code does.", "And a bench of test cases and injected faults checks that those safeguards actually hold."], zs: [[0,1,2,3],[1,2],[2,3]],
    body: [[1, '<p class="b">A model helps.</p>'], [1, '<p class="b say">Code has the last word.</p>'], [2, '<p class="b">The bench tests it.</p>']] },
  { title: 'Where the model stops', lede: 'Code finds. The model proposes.', zone: [0, 1], chip: 'One diagram · README, page, video', ref: '▲ source/rfp/answer.py',
    v: ["First, the code parses the R F P and finds the clauses that might answer the question.", "For four fixed questions, it skips the model entirely, and just quotes the governing text.", "Otherwise, the model proposes an answer: it picks the clauses, and writes one sentence."], zs: [[0],[0],[1]],
    body: [[0, `<div class="crop c1"><img src="${SVG}" alt="Code and model half of the trust boundary diagram"></div>`]] },
  { title: 'What code checks', lede: 'Every cited clause, every figure.', zone: [2, 3], chip: 'Answered or held back', ref: '▲ source/rfp/answer.py',
    v: ["Then the code checks that answer. Every cited clause has to exist, and every figure has to appear in them.", "If it passes, you get the answer, with citations.", "If it fails, the model's sentence is held back."], zs: [[2],[3],[3]],
    body: [[0, `<div class="crop c2"><img src="${SVG}" alt="Check half of the trust boundary diagram"></div>`]] },
  { title: 'Eight cases, one command', lede: 'Mock run.', zone: [3], chip: 'MCP = direct call', ref: '▲ mcp/eval_via_mcp.py',
    v: ["Eight test cases run through the M C P server.", "With the mock model, which is a stand-in for testing the plumbing and the safety checks, not real answers, all five of five pass.", "The other three traps need a real model, so the mock skips them. The real-model run is a separate result.", "And the server returns exactly what the engine returns when you call it directly."], zs: [[0],[1,2],[3],[0,3]],
    body: [[0, '<p class="code">python3 mcp/eval_via_mcp.py --provider mock<br>&nbsp;&nbsp;--compare-direct</p>'],
      [1, '<div class="stamps">' + [1, 2, 3, 4, 5].map(n => `<span class="lbl st ok">S${n}</span>`).join('') + '</div>'],
      [2, '<div class="stamps">' + [6, 7, 8].map(n => `<span class="lbl st lim">S${n}</span>`).join('') + '</div>'],
      [2, '<p class="lbl" style="color:var(--dimmed);text-transform:none;letter-spacing:.04em">real model d67294d: 11 right, 12 withheld, 1 wrong</p>']] },
  { title: 'Faults the check catches', lede: 'Faults injected on purpose.', zone: [1, 2], chip: '3 of 3 caught', ref: '▲ source/rfp/provider.py, MOCK_FAULT',
    v: ["Here's the fun part, the mock model can also fail on purpose!", "Say it invents a figure? The check names it, and holds the sentence back.", "Change a single dollar figure, and the check catches that too.", "And if it cites a clause that doesn't exist? No answer. At all."], zs: [[1],[2],[2],[3]],
    body: [[1, caught('invent', 'Verbatim failed: $80,000, 12%')], [2, caught('wrong_figure', 'Verbatim failed: $30,000')], [3, caught('fake_citation', 'No valid citation, no answer')]] },
  { title: 'Faults that fail safe', lede: 'Code withholds, never guesses.', zone: [2, 3], chip: '8 of 8 caught', ref: '▲ source/rfp/answer.py',
    v: ["Ask it to draft a whole proposal, or hand down a bid verdict? That's withheld.", "If the model times out, returns garbage, or flat-out refuses, the engine fails safe, with no answer.", "Eight faults in. Eight caught."], zs: [[2],[3],[2,3]],
    body: [[0, caught('draft', 'Withheld: scope')], [0, caught('verdict', 'Withheld: person decides')],
      [1, caught('timeout', 'Clauses shown')], [1, caught('garbage', 'Unparseable')], [1, caught('refuse', 'Not addressed')]] },
  { title: 'A second bench', lede: 'Registered, run once.', zone: [2], chip: '0 confident-wrong in 800', ref: '▲ provenance results, 2026-10-18',
    v: ["I used the same discipline on a provenance search engine.", "I wrote the rules down first, and then ran it exactly once.", "A shingle index missed edited quotes, so I cut it.", "A quick pre-check, a Bloom filter, dropped thirty-seven true files, so I cut that too.", "Hash checks caught every tampered file, so they stayed."], zs: [[0],[0],[2],[2],[2,3]],
    body: [[2, row('shingle index', 'Cut: 85.0% edited recall', 'fail')], [3, row('Bloom filter', 'Cut: 37 misses in 600', 'fail')], [4, row('hash check', 'Kept: 100 of 100 caught')]] },
  { title: 'A claim you can rerun', lede: 'Cut what fails. Keep what passes.', zone: [0, 1, 2, 3], chip: 'Two layers cut · one check kept',
    v: ["A bench turns a claim into something you can rerun.", "It tells you what to cut, and what to keep.", "On that bench, two layers were cut, and one check was kept."], zs: [[0,1,2,3],[2],[3]],
    body: [[0, '<p class="b say">Rerun it yourself: one command.</p>']] },
];

const page = (s, n, upto, chip) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}${gfCss}</style></head><body>${gfHtml.replace('{{LABEL}}', `${String(n).padStart(2, '0')} / ${String(S.length).padStart(2, '0')}`)}
<header><p class="lbl">Bench · ${String(n).padStart(2, '0')} / ${String(S.length).padStart(2, '0')}</p>${s.h1 ? `<h1>${s.title}</h1>` : `<h2>${s.title}</h2>`}</header>
<main>${s.lede ? `<p class="lede">${s.lede}</p>` : ''}${s.body.map(([at, h]) => at <= upto ? h : `<div class="hide">${h}</div>`).join('')}</main>${strip(chip || upto >= 99 ? s.zone : s.zs[Math.min(upto, s.zs.length - 1)])}
<footer><p class="ref">${s.ref || ''}</p><p class="lbl chip${chip ? '' : ' hide'}">${s.chip}</p></footer></body></html>`;

// Density and ramp check on the settled frame (rules 1 and 3); throws so a bad frame never encodes.
const check = async (pg, name) => {
  const r = await pg.evaluate(() => {
    const root = parseFloat(getComputedStyle(document.documentElement).fontSize);
    const meta = 0.8125 * root, body = 0.925 * root;
    const ramp = [0.8, 0.925, 1.15, 0.8125].map(x => x * root).concat(Math.min(Math.max(1.5 * root, innerWidth * 0.04), 2.4 * root));
    const sizes = new Set(), bad = [], tops = new Set(); let words = 0;
    for (const el of document.querySelectorAll('body *')) {
      if (el.closest('.hide') || el.closest('.gf')) continue; // frame chrome is not card content
      const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').trim();
      if (!own) continue;
      const fs = parseFloat(getComputedStyle(el).fontSize);
      if (!ramp.some(x => Math.abs(x - fs) < 0.5)) bad.push(el.tagName + ' ' + fs);
      if (!(el.classList.contains('ref') && Math.abs(fs - meta) < 0.5)) sizes.add(Math.round(fs));
      words += own.split(/\s+/).length;
      // count the element's own text lines (a Range), so an inline stamp beside the text does not add a line
      if (Math.abs(fs - body) < 0.5) for (const rc of [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).flatMap(n => { const rg = document.createRange(); rg.selectNodeContents(n); return [...rg.getClientRects()]; })) for (let y = rc.top; y < rc.bottom - 1; y += fs * 1.4) tops.add(Math.round(y / 8));
    }
    for (const r of document.querySelectorAll('.row')) { const [k, v] = r.children; const kr = document.createRange(); kr.selectNodeContents(k); if (kr.getBoundingClientRect().right > v.getBoundingClientRect().left - 4) bad.push('overlap ' + k.textContent); }
    // adjacent 8px buckets are one line (key and value text can straddle a bucket edge by 1px)
    const t = [...tops].sort((a, b) => a - b), lines = t.filter((y, i) => i === 0 || y - t[i - 1] > 1).length;
    return { words, sizes: sizes.size, bodyLines: lines, bad };
  });
  const fails = [r.bad.length && 'off-ramp ' + r.bad.join(','), r.words > 45 && r.words + ' words', r.sizes > 3 && r.sizes + ' sizes', r.bodyLines > 7 && r.bodyLines + ' body lines'].filter(Boolean);
  if (fails.length) throw new Error(`${name}: ${fails.join('; ')}`);
  return r;
};

const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

// Fluid timing (Zach approved, card 04 reference vid/fluid-card.cjs): 650 ms fade in and out per sheet,
// 240 ms dissolves between reveals, picture leads voice 0.4 s and holds 0.6 s after, reveals on their
// sentences, sheet length snapped up to whole music bars (161.5 BPM). Writes bench.spans.json for mix.sh.
const LEAD = 0.4, TAIL = 0.6, CHIP = 1.8, BAR = 60 / 161.5 * 4, SHUTTER = 0.65, QUICK = 0.24, GAP = 0.25;
const run = a => execFileSync('ffmpeg', ['-hide_banner', '-y', '-loglevel', 'error', ...a]);

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 }, reducedMotion: 'reduce', colorScheme: 'dark' });
  const parts = [], report = [], spans = []; let T0 = 0;
  fs.writeFileSync(__dirname + '/SCRIPT.md', '# Bench video script\n\n' + S.map((s, i) => `## ${i + 1}. ${s.title}\n\n${s.v.join(' ')}\n`).join('\n'));
  fs.mkdirSync(__dirname + '/voice', { recursive: true });
  fs.writeFileSync(__dirname + '/voice/SCRIPT.md', S.map((s, i) => `## ${i + 1}\n\n${s.v.join(' ')}\n`).join('\n'));
  for (const f of fs.readdirSync(OUT)) if (/^\d\d-.*\.(png|aiff|wav)$/.test(f)) fs.unlinkSync(`${OUT}/${f}`);
  for (let i = 0; i < S.length; i++) {
    const n = String(i + 1).padStart(2, '0'), s = S[i];
    // Voice: a real take wins (starts by word share); else one `say` take per sentence, so starts are exact.
    let audio = `${__dirname}/voice/${n}.mp3`, starts, sent;
    if (fs.existsSync(audio)) {
      const D = dur(audio), w = s.v.map(x => x.split(/\s+/).length), W = w.reduce((a, c) => a + c, 0);
      const log = execFileSync('sh', ['-c', `ffmpeg -hide_banner -i "${audio}" -af silencedetect=n=-38dB:d=0.18 -f null - 2>&1`]).toString();
      const ends = [...log.matchAll(/silence_end: ([0-9.]+)/g)].map(m => +m[1]).filter(t => t < D - 0.3);
      starts = s.v.map((_, k) => { const est = w.slice(0, k).reduce((a, c) => a + c, 0) / W * D; if (!k || !ends.length) return est;
        const near = ends.reduce((b, t) => Math.abs(t - est) < Math.abs(b - est) ? t : b); return Math.abs(near - est) < 1.5 ? near : est; });
      sent = s.v.map((_, k) => [starts[k], k + 1 < s.v.length ? starts[k + 1] - 0.1 : D]);
    } else {
      const takes = s.v.map((v, k) => { const f = `${OUT}/${n}-s${k}.aiff`; execFileSync('say', ['-v', 'Samantha', '-r', '175', '-o', f, v]); return f; });
      starts = []; sent = []; let t = 0;
      for (const f of takes) { const d = dur(f); starts.push(t); sent.push([t, t + d]); t += d + GAP; }
      audio = `${OUT}/${n}.wav`;
      const fc = takes.map((_, k) => `[${k}:a]aresample=48000,apad=pad_dur=${k + 1 < takes.length ? GAP : 0}[a${k}];`).join('') + takes.map((_, k) => `[a${k}]`).join('') + `concat=n=${takes.length}:v=0:a=1[a]`;
      run([...takes.flatMap(f => ['-i', f]), '-filter_complex', fc, '-map', '[a]', audio]);
    }
    const D = dur(audio);
    const ats = s.v.map((_, k) => k); // one state per sentence: the rail and reveals move with the voice
    const imgs = [];
    for (let k = 0; k < ats.length; k++) {
      const png = `${OUT}/${n}-${k}.png`;
      await pg.setContent(page(s, i + 1, ats[k], false)); await pg.waitForTimeout(200);
      await check(pg, `${n}-${k}`);
      await pg.screenshot({ path: png }); imgs.push(png);
    }
    const chipPng = `${OUT}/${n}-chip.png`;
    await pg.setContent(page(s, i + 1, 99, true)); await pg.waitForTimeout(200);
    report.push(`${n}-chip ${JSON.stringify(await check(pg, `${n}-chip`))}`);
    await pg.screenshot({ path: chipPng }); imgs.push(chipPng);
    // Timeline: state k lands as its sentence starts; the chip after voice + TAIL; total in whole bars.
    const tChip = LEAD + D + TAIL, TOTAL = Math.ceil((tChip + CHIP) / BAR) * BAR;
    const at = [...ats.map((a, k) => k === 0 ? 0 : LEAD + starts[a] - QUICK), tChip];
    const len = imgs.map((_, k) => (k + 1 < at.length ? at[k + 1] : TOTAL) - at[k] + QUICK);
    let fc = '', prev = '[0:v]';
    for (let k = 1; k < imgs.length; k++) {
      const d = k === imgs.length - 1 ? SHUTTER * 0.6 : QUICK;
      fc += `${prev}[${k}:v]xfade=transition=fade:duration=${d.toFixed(3)}:offset=${at[k].toFixed(3)}[v${k}];`; prev = `[v${k}]`;
    }
    fc += `${prev}fade=t=in:d=${SHUTTER}:color=black,fade=t=out:st=${(TOTAL - SHUTTER).toFixed(3)}:d=${SHUTTER},fps=30,format=yuv420p[v];` +
      `[${imgs.length}:a]aresample=48000,adelay=${Math.round(LEAD * 1000)}:all=1,apad=whole_dur=${TOTAL.toFixed(3)}[a]`;
    run([...imgs.flatMap((f, k) => ['-loop', '1', '-t', len[k].toFixed(3), '-i', f]), '-i', audio, '-filter_complex', fc,
      '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', TOTAL.toFixed(3), `${OUT}/${n}.mp4`]);
    sent.forEach(([a, c]) => spans.push([+(T0 + LEAD + a).toFixed(3), +(T0 + LEAD + c).toFixed(3)]));
    T0 += dur(`${OUT}/${n}.mp4`);
    parts.push(`file '${OUT}/${n}.mp4'`);
  }
  await b.close();
  fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
  run(['-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', `${OUT}/bench.mp4`]);
  fs.writeFileSync(`${OUT}/bench.spans.json`, JSON.stringify({ source: 'bench.mp4', unit: 's', spans }, null, 1));
  console.log(report.join('\n'));
  console.log('ok', `${OUT}/bench.mp4`, 'spans', spans.length, 'total', T0.toFixed(2));
})();
