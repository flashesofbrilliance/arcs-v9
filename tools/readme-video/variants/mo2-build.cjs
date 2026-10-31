// Making-of v2 (compound engineering): 8 sheets on kit.cjs. Throughline = the six-link chain strip,
// current links lit. Renders stills (STILLS=1 implied) to out/mo2/; fluid-build.cjs mo2 encodes.
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const fs = require('fs');
const K = require('./kit.cjs');
const { C, TINT, txt, box, fill, arrow, line, hatch, stamp } = K;
const OUT = __dirname + '/out/mo2';
fs.mkdirSync(OUT, { recursive: true });

const LINKS = ['Correction', 'Rule', 'Check', 'Judge', 'Tooling', 'Backlog row'];
const chain = lit => LINKS.map((s, i) => { const x = 120 + i * 270, on = lit.includes(i);
  return (on ? fill(x, 244, 250, 52, TINT.ink) : '') + box(x, 244, 250, 52, on ? C.ink : C.rule, false, on ? 2 : 1.5)
    + txt(x + 18, 278, s, 'lbl', on ? C.ink : C.dim) + (i < 5 ? line(x + 250, 270, x + 270, 270, C.rule, 1.5) : ''); }).join('');
const ref = (x, y, glyph, s, color) => txt(x, y, `${glyph} ${s}`, 'ref', color);

const S = [
  { h: 'What compounds', title: 'Compound engineering', chip: { text: 'Each fix leaves a tool' }, lit: [], layers: [
    { at: 1, svg: ['A rule', 'A check', 'A reviewer', 'A tool', 'A task'].map((s, i) => box(120 + i * 330, 360, 300, 120) + txt(144 + i * 330, 434, s, 'big')).join('') },
    { at: 2, svg: fill(120, 560, 1620, 160, TINT.ok) + box(120, 560, 1620, 160, C.ok) + txt(150, 606, 'Compound engineering', 'lbl', C.ok)
      + txt(150, 670, 'Each piece of work makes the next one cheaper', 'big') },
  ] },
  { h: 'One chain from today', title: 'The chain', chip: { text: 'Correction, rule, check, judge, tool, task' }, lit: [0, 1, 2, 3, 4, 5], layers: [
    { at: 1, svg: box(120, 482, 500, 140) + txt(150, 526, 'Start', 'lbl', C.ink) + txt(150, 584, 'A line of copy sounded wrong', 'sub') },
    // rows indent into a chevron around the arrow line (y 552): the arrow pushes the field, middle row leads
    { at: 2, svg: arrow(620, 552, 836, 552) + ['Written rule', 'Script check', 'Render reviewer', 'Shared tooling', 'Backlog task'].map((s, i) => {
      const x = 720 + (2 - Math.abs(i - 2)) * 60;
      return box(x, 330 + i * 92, 640, 76) + txt(x + 30, 378 + i * 92, s, 'big'); }).join('') },
  ] },
  { h: 'One wording fix', title: 'Correction to check', chip: { text: 'One wording fix, one standing check' }, lit: [0, 1, 2], layers: [
    { at: 1, svg: `<text class="big" x="150" y="420" style="fill:${C.dim}" text-decoration="line-through">No answer without a real source</text>`
      + arrow(150, 460, 150, 516) + txt(150, 570, 'Shows its source', 'big', C.ink) },
    { at: 2, svg: arrow(760, 500, 916, 500) + box(920, 340, 760, 130) + txt(950, 384, 'Rule', 'lbl', C.ink) + txt(950, 440, 'Video rules and typography', 'sub') + box(920, 530, 760, 130) + txt(950, 574, 'Check R11', 'lbl', C.ink) + txt(950, 630, 'Punctuation lint on every script', 'sub')
      + ref(920, 712, '▲', 'PR 1877, merged', C.ok) },
  ] },
  { h: 'A reviewer, then a tool', title: 'Judge and tooling', chip: { text: 'Blocked twice, then fixed' }, lit: [3, 4], layers: [
    { at: 1, svg: box(120, 330, 560, 150) + txt(150, 374, 'Brand line producer', 'lbl', C.ink) + txt(150, 434, 'Checks every frame', 'big') + ref(150, 520, '▲', 'PR 1875, merged', C.ok) },
    { at: 2, svg: stamp(760, 330, 420, 64, 'Blocked: margins, type', 'stale') + stamp(760, 414, 420, 64, 'Blocked: density', 'stale') + stamp(1240, 372, 300, 64, 'Fixed', 'ok') },
    { at: 3, svg: box(120, 600, 420, 130) + txt(150, 644, 'mix.sh', 'lbl', C.ink) + txt(150, 700, 'Splice and voice ride', 'sub')
      + arrow(540, 640, 756, 620) + arrow(540, 690, 756, 710) + box(760, 590, 420, 60) + txt(790, 630, 'Walkthrough', 'sub') + box(760, 680, 420, 60) + txt(790, 720, 'Making-of', 'sub')
      + ref(120, 790, '~', 'scratch folder, not in the repo', C.part) },
  ] },
  { h: 'The backlog graph', title: 'Backlog row', chip: { text: 'About 400 rows, 13 waves', state: 'ink' }, lit: [5], layers: [
    { at: 1, svg: box(120, 330, 660, 400) + txt(150, 374, 'A row', 'lbl', C.ink)
      + ['route', 'gates', 'trigger', 'depends on'].map((s, i) => txt(150, 440 + i * 70, s, 'mono', C.dim)).join('') },
    { at: 2, svg: Array.from({ length: 13 }, (_, i) => line(860 + i * 70, 340, 860 + i * 70, 720, i === 0 ? C.ok : C.rule, i === 0 ? 3 : 1.5)).join('')
      + txt(860, 330, 'Waves', 'lbl', C.dim)
      + fill(900, 560, 760, 130, TINT.ink) + box(900, 560, 760, 130) + txt(930, 604, 'Ready', 'lbl', C.ok) + txt(930, 656, 'arcs-mini-adopt-design-md-motion', 'mono')
      + ref(860, 860, '▲', 'backlog graph: 394 rows, 13 waves, 2026-10-30', C.dim) },
  ] },
  { h: 'What broke', title: 'Seams', chip: { text: 'Timing in the tool, density by hand', state: 'part' }, lit: [], layers: [
    { at: 1, svg: `<text class="big" x="150" y="400" style="fill:${C.dim}">Reveals on estimates</text>` + arrow(780, 390, 856, 390, C.ok) + txt(880, 400, 'Snapped to the voice', 'big', C.ok) },
    { at: 2, svg: `<text class="big" x="150" y="520" style="fill:${C.dim}">Frames too dense</text>` + arrow(780, 510, 856, 510, C.part) + txt(880, 520, 'Trimmed to 45 words by hand', 'big', C.part) },
    { at: 3, svg: stamp(150, 600, 640, 80, 'Timing: fixed in the tool', 'ok') },
    { at: 4, svg: stamp(150, 710, 640, 80, 'Density: trimmed by hand', 'part') },
  ] },
  { h: 'Not built yet', title: 'Gaps', chip: { text: '3 gaps, stated', state: 'part' }, lit: [], layers: [
    ...[['Type size and density checks', 'judged, not yet scripted'], ['Backlog rows with no tool', 'the graph cannot find one'], ['Music tool', 'not in the repository yet']]
      .map(([a, b], i) => ({ at: i + 1, svg: hatch(120, 320 + i * 170, 1560, 140, C.part) + box(120, 320 + i * 170, 1560, 140, C.part, true)
        + txt(150, 380 + i * 170, a, 'big') + txt(150, 424 + i * 170, b, 'sub', C.dim) })),
  ] },
  { h: 'Try it', title: 'Next session', chip: { text: 'Run /backlog-graph' }, lit: [5], layers: [
    { at: 0, svg: box(120, 340, 700, 140) + txt(150, 384, 'Terminal', 'lbl', C.ink) + txt(150, 440, '/backlog-graph', 'mono') },
    { at: 1, svg: arrow(820, 410, 916, 410) + box(920, 340, 760, 140, C.ok) + fill(920, 340, 760, 140, TINT.ok) + txt(950, 384, 'Ready now', 'lbl', C.ok)
      + txt(950, 440, 'Start from the top row', 'big') },
  ] },
];

const script = fs.readFileSync(__dirname + '/makingof/SCRIPT-v2.md', 'utf8');
const nSent = n => script.split(/^## /m).find(s => s.startsWith(n)).split('\n\n')[1].trim().split(/(?<=[.!?]["”]?)\s+/).length;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (let i = 0; i < S.length; i++) {
    const n = String(i + 1).padStart(2, '0'), sh = { ...S[i] };
    sh.layers = [{ at: 0, svg: chain(sh.lit) }, ...sh.layers];
    const max = nSent(n) - 1; sh.layers.forEach(l => { if (l.at > max) throw new Error(`${n}: layer at ${l.at} but only ${max + 1} sentences`); });
    const ats = [...new Set([0, ...sh.layers.map(l => l.at)])].sort((a, c) => a - c);
    fs.writeFileSync(`${OUT}/${n}.ats.json`, JSON.stringify(ats));
    for (let k = 0; k < ats.length; k++) {
      await pg.setContent(K.page(sh, i + 1, S.length, ats[k], false)); await pg.waitForTimeout(150);
      await pg.screenshot({ path: `${OUT}/${n}-${k}.png` });
    }
    const html = K.page(sh, i + 1, S.length, 99, true);
    await pg.setContent(html); await pg.waitForTimeout(150); await pg.screenshot({ path: `${OUT}/${n}-chip.png` });
    fs.mkdirSync(__dirname + '/out/gate2', { recursive: true }); fs.writeFileSync(`${__dirname}/out/gate2/mo2-${n}.html`, html);
  }
  await b.close();
  console.log('stills', OUT);
})();
