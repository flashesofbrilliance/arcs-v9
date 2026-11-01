// Blueprint walkthrough: 8 sheets snapped from kit.cjs, each layer revealed on its spoken
// sentence, the fact chip shown in the pause after the voice. Writes out/bp/ and
// out/walkthrough-blueprint.mp4; never touches build.cjs output.
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const K = require('./kit.cjs');
const { C, txt, box, arrow, line, hatch, stage, dim, callout, stamp } = K;
const OUT = __dirname + '/out/bp';
fs.mkdirSync(OUT, { recursive: true });
const PAUSE = 1.8; // the ma: seconds the chip holds after the voice ends

// Each layer appears at the start of sentence `at` of that card's narration.
const S = [
  { h: 'RFP answering engine', title: 'What it is', chip: { text: 'Clause behind it · or not covered' }, layers: [
    { at: 0, svg: box(120, 420, 480, 160) + txt(144, 462, 'Input', 'lbl', C.ink) + txt(144, 516, 'A question about an RFP', 'big')
      + arrow(600, 500, 716, 500) + box(720, 420, 300, 160) + txt(744, 462, 'Engine', 'lbl', C.ink) + txt(744, 524, 'Answers', 'big') },
    { at: 3, svg: line(330, 580, 330, 680, C.dim) + box(160, 680, 560, 110, C.dim, true) + txt(184, 722, 'Note', 'lbl', C.dim) + txt(184, 764, 'Fictional RFP, written for this sample', 'sub') },
    { at: 1, svg: line(1020, 500, 1100, 500) + line(1100, 340, 1100, 660) + arrow(1100, 340, 1196, 340) + arrow(1100, 660, 1196, 660)
      + K.fill(1200, 270, 600, 140, K.TINT.ok) + box(1200, 270, 600, 140, C.ok) + txt(1224, 312, 'Answer', 'lbl', C.ok) + txt(1224, 366, '+ the exact clause behind it', 'big')
      + box(1200, 590, 600, 140) + txt(1224, 632, 'Or', 'lbl', C.ink) + txt(1224, 686, 'A plain \u201cnot covered\u201d', 'big') },
    { at: 2, svg: dim(720, 1020, 640, 'Pure Python') + txt(870, 690, 'nothing to install', 'sub', C.dim, 'middle') },
  ] },
  { h: 'Rules first, model last', title: 'How it works', chip: { text: 'Model last · code checks it' }, layers: [
    { at: 1, svg: stage(120, 360, 360, 200, '01', 'Parse', ['Split into clauses'], 'by rules')
      + line(300, 560, 300, 690) + box(160, 690, 300, 100, C.ink, false, 1.5) 
      + `<text class="mono" x="184" y="754" style="fill:${C.dim}" text-decoration="line-through">§7.1</text>` + arrow(300, 746, 356, 746) + txt(372, 754, '§A1', 'mono') },
    { at: 2, svg: arrow(480, 460, 596, 460) + stage(600, 360, 360, 200, '02', 'Search', ['Find candidate', 'clauses']) + dim(120, 960, 300, 'No model') },
    { at: 3, svg: arrow(960, 460, 1076, 460) + stage(1080, 360, 360, 200, '03', 'Model', ['Pick clauses,', 'write one sentence'])
      + arrow(1440, 460, 1556, 460) + `<polygon points="1680,360 1800,460 1680,560 1560,460" fill="none" stroke="${C.ink}" stroke-width="2"/>`
      + txt(1680, 452, 'Code', 'lbl', C.ink, 'middle') + txt(1680, 482, 'check', 'lbl', C.ink, 'middle') + txt(1680, 610, 'before anyone sees it', 'lbl', C.dim, 'middle') },
  ] },
  { h: 'What is the bid deposit?', title: 'Through the MCP server', chip: { text: '$35,000 · amended value governs' }, layers: [
    { at: 0, svg: K.fill(120, 270, 1020, 520, C.panel) + box(120, 270, 1020, 520) + txt(144, 310, 'Claude MCP server · response', 'lbl', C.ink) + line(120, 330, 1140, 330, C.rule)
      + txt(144, 390, 'status', 'mono', C.dim) + txt(330, 390, 'answered', 'mono', C.ok) },
    { at: 1, svg: txt(144, 470, 'answer', 'mono', C.dim) + txt(330, 470, 'bid deposit is $35,000', 'mono')
      + txt(144, 550, 'cites', 'mono', C.dim) + txt(330, 550, 'RFP §7.1  +  Amendment §A1.2', 'mono')
      + txt(144, 630, 'notes', 'mono', C.dim) + txt(330, 630, 'the amended value governs', 'mono', C.part)
      + callout(700, 462, 1220, 380, '$35,000', C.ok) },
    { at: 2, svg: txt(144, 710, 'gate', 'mono', C.dim) + txt(330, 710, 'which check decided', 'mono') + callout(664, 702, 1220, 800, 'the gate field') },
  ] },
  { h: 'Six rules, enforced in code', title: 'Trust', chip: { text: '6 rules · in code' }, layers: [
    { at: 0, svg: line(120, 270, 1800, 270, C.rule) },
    ...[['Shows its source', 'Every answer points to the clause it came from.'], ['Numbers match', 'Amounts, dates and percentages match the text exactly.'],
        ['Latest wins', 'If an amendment changed it, you get the new value.'], ['\u201cNot covered\u201d counts', 'If the RFP doesn\u2019t say, it tells you so.'],
        ['Facts, not decisions', 'It won\u2019t write your bid or tell you whether to bid.'], ['No guessing', 'Without a model, you get the clauses, not a summary.']]
      .map(([a, b], i) => { const y = 290 + i * 96; return { at: i + 1, svg:
        box(120, y + 14, 60, 60, C.ink) + txt(150, y + 52, `0${i + 1}`, 'lbl', C.ink, 'middle')
        + txt(220, y + 56, a, 'big') + line(120, y + 92, 1800, y + 92, C.rule) }; }),
  ] },
  { h: 'A model that invents numbers', title: 'Injected fault', chip: { text: '8 / 8 faults caught' }, layers: [
    { at: 0, svg: box(120, 340, 360, 180, C.stale, true) + txt(144, 382, 'Mock model', 'lbl', C.stale) + txt(144, 440, 'misbehaves', 'big') + txt(144, 480, 'on purpose', 'sub', C.dim)
      + box(820, 340, 360, 180) + txt(844, 382, 'Check', 'lbl', C.ink) + txt(844, 440, 'Figures in the', 'big') + txt(844, 480, 'cited clause?', 'big') },
    { at: 1, svg: arrow(480, 400, 816, 400, C.stale) + arrow(480, 460, 816, 460, C.stale) + txt(530, 388, '$80,000', 'mono', C.stale) + txt(530, 448, '12%', 'mono', C.stale) },
    { at: 2, svg: line(1180, 380, 1256, 380, C.stale, 2) + stamp(1260, 340, 420, 80, 'Summary withheld', 'part') + line(1000, 520, 1000, 660) + arrow(1000, 660, 1256, 660)
      + box(1260, 600, 420, 120) + txt(1284, 642, 'Returned', 'lbl', C.ink) + txt(1284, 692, 'Clause text only', 'big') },
    { at: 3, svg: stamp(120, 600, 520, 120, '8 injected · 8 caught', 'ok') },
  ] },
  { h: 'What was actually run', title: 'Results, measured 2026-10-30', chip: { text: '11 correct · 12 withheld · 1 wrong', state: 'part' }, layers: [
    { at: 0, svg: box(120, 324, 1680, 456, C.rule, false, 1.5) },
    { at: 1, svg: txt(150, 390, 'Deterministic cases', 'big') + txt(900, 390, '5 / 5', 'mono') + stamp(1300, 354, 440, 52, 'Pass', 'ok') + line(120, 430, 1800, 430, C.rule)
      + txt(150, 496, 'Server vs. engine', 'big') + txt(900, 496, 'identical', 'mono') + stamp(1300, 460, 440, 52, 'Pass', 'ok') + line(120, 536, 1800, 536, C.rule) },
    { at: 2, svg: txt(150, 602, 'Real model, 24 questions', 'big') + txt(900, 602, '11 / 12 / 1', 'mono') + txt(1520, 602, 'correct / withheld / wrong', 'lbl', C.text, 'middle') + line(120, 643, 1800, 643, C.rule) },
    { at: 3, svg: hatch(120, 644, 1680, 106, C.part) + txt(150, 708, 'Target: 0 wrong', 'big') + txt(900, 708, 'run d67294d', 'mono') + stamp(1300, 672, 440, 52, 'Missed · 1 wrong', 'part') },
  ] },
  { h: 'What it does not do yet', title: 'Honest gaps', chip: { text: '5 gaps · stated', state: 'part' }, layers: [
    { at: 0, svg: box(120, 260, 1680, 540, C.rule, false, 1.5) + txt(150, 300, 'Plan · dashed = not built', 'lbl', C.dim) },
    ...[['No confidence score', 160, 330, 500], ['Keyword retrieval only', 700, 330, 500], ['Meaning not checked', 1240, 330, 540], ['Plain text, one numbering style', 160, 560, 700], ['Contract clause types, e.g. indemnity', 900, 560, 860]]
      .map(([s, x, y, w], i) => ({ at: i + 1, svg: box(x, y, w, 180, C.part, true) + txt(x + 28, y + 102, s, 'big') })),
  ] },
  { h: 'One command in Claude Code', title: 'Try it', chip: { text: '1 command · try it' }, layers: [
    { at: 0, svg: box(120, 280, 1100, 200) + txt(144, 320, 'Terminal', 'lbl', C.ink) + txt(144, 380, 'claude mcp add rfp-intelligence \\', 'mono')
      + txt(144, 420, '  -e MODEL_PROVIDER=mock -- python3 mcp/server.py', 'mono')
      + arrow(670, 480, 670, 576) + box(120, 580, 1100, 110) + txt(144, 620, 'Ask', 'lbl', C.ink) + txt(144, 664, 'Using rfp-intelligence, what is the bid deposit?', 'sub')
      + arrow(1220, 635, 1316, 635) + stamp(1320, 590, 480, 90, '$35,000 · cites both', 'ok') },
    { at: 1, svg: callout(1220, 380, 1340, 360, 'Setup and checks', C.dim) + txt(1340, 400, 'mcp/README.md', 'mono') },
  ] },
];

const voice = fs.readFileSync(__dirname + '/voice/SCRIPT.md', 'utf8');
const sentences = n => voice.split(/^## /m).find(s => s.startsWith(n)).split('\n').slice(1).join(' ').trim().split(/(?<=[.!?]["”]?)\s+/);
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const parts = [], spans = []; let t0card = 0;
  for (let i = 0; i < S.length; i++) {
    const n = String(i + 1).padStart(2, '0'), sh = S[i], audio = `${__dirname}/voice/${n}.mp3`;
    const sents = sentences(n), D = dur(audio);
    const words = sents.map(s => s.split(/\s+/).length), W = words.reduce((a, c) => a + c, 0);
    const start = sents.map((_, k) => (words.slice(0, k).reduce((a, c) => a + c, 0) / W) * D);
    const ats = [...new Set([0, ...sh.layers.map(l => l.at)])].sort((a, c) => a - c);
    const list = [];
    fs.writeFileSync(`${OUT}/${n}.ats.json`, JSON.stringify(ats));
    for (let k = 0; k < ats.length; k++) {
      const png = `${OUT}/${n}-${k}.png`;
      await pg.setContent(K.page(sh, i + 1, S.length, ats[k], false)); await pg.waitForTimeout(150);
      await pg.screenshot({ path: png });
      const t0 = start[ats[k]] || 0, t1 = k + 1 < ats.length ? start[ats[k + 1]] : D;
      list.push(`file '${png}'\nduration ${(t1 - t0).toFixed(3)}`);
    }
    const chipPng = `${OUT}/${n}-chip.png`;
    await pg.setContent(K.page(sh, i + 1, S.length, 99, true)); await pg.waitForTimeout(150);
    if (process.env.DUMP) { fs.mkdirSync(__dirname + '/out/gate', { recursive: true }); fs.writeFileSync(`${__dirname}/out/gate/bp-${n}.html`, K.page(sh, i + 1, S.length, 99, true)); }
    await pg.screenshot({ path: chipPng });
    list.push(`file '${chipPng}'\nduration ${PAUSE}\nfile '${chipPng}'`);
    fs.writeFileSync(`${OUT}/${n}.txt`, list.join('\n'));
    if (process.env.STILLS) continue; // stills only: no encode
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${OUT}/${n}.txt`, '-i', audio,
      '-af', `apad=whole_dur=${(D + PAUSE).toFixed(3)}`, '-fps_mode', 'cfr', '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', (D + PAUSE).toFixed(3), `${OUT}/${n}.mp4`]);
    for (const [a, c] of K.voiceSpans(audio, D)) spans.push([+(t0card + a).toFixed(3), +(t0card + c).toFixed(3)]);
    t0card += D + PAUSE;
    parts.push(`file '${OUT}/${n}.mp4'`);
  }
  await b.close();
  if (process.env.STILLS) return console.log('stills only', OUT);
  fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', `${__dirname}/out/walkthrough-blueprint.mp4`]);
  fs.writeFileSync(`${__dirname}/out/walkthrough-blueprint.spans.json`, JSON.stringify({ source: 'walkthrough-blueprint.mp4', unit: 's', spans }, null, 1));
  console.log('ok', `${__dirname}/out/walkthrough-blueprint.mp4`);
})();
