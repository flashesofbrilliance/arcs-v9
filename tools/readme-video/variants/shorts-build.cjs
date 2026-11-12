// Stills for the 60 s capture (cap) and the 90 s walkthrough re-cut (rc), on kit.cjs with the glass frame.
// Usage: node shorts-build.cjs cap|rc  ->  out/<set>/NN-k.png, NN-chip.png, NN.ats.json; then fluid-build.cjs <set>.
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const fs = require('fs');
const K = require('./kit.cjs');
const { C, TINT, txt, box, fill, arrow, hatch, stamp } = K;
const SET = process.argv[2];
const OUT = `${__dirname}/out/${SET}`;
fs.mkdirSync(OUT, { recursive: true });
const term = (lines) => fill(120, 300, 1680, 480, C.panel) + box(120, 300, 1680, 480, C.rule, false, 1.5)
  + txt(150, 344, 'Terminal · real model run, row A3', 'lbl', C.dim) + lines.join('');
const L = (y, s, color = C.text) => txt(150, y, s, 'mono', color);
const Q = L(420, '> The deposit is roughly $30,000, right?');
const R = [L(500, 'model: "No. Amendment No. 1 ... increases the bid deposit from $20,000', C.ok), L(544, 'to $35,000, so the amended deposit is $35,000, not roughly $30,000."', C.ok)];
const G = [L(624, "gate:  verbatim FAILED: ['$30,000'] not in any cited clause", C.part), L(668, 'shown: withheld, cited clauses A1.2 and 7.1 instead', C.part)];
const nums = y => box(120, y, 520, 150, C.ok) + fill(120, y, 520, 150, TINT.ok) + txt(150, y + 62, '11 correct', 'big', C.ok)
  + box(700, y, 520, 150, C.part) + fill(700, y, 520, 150, TINT.part) + txt(730, y + 62, '12 withheld', 'big', C.part)
  + box(1280, y, 520, 150, C.stale) + fill(1280, y, 520, 150, TINT.stale) + txt(1310, y + 62, '1 wrong', 'big', C.stale);
const SRC = 'Run d67294d, 2026-10-30, 24 pre-registered questions';

const SETS = {
  cap: { script: 'capture/SCRIPT.md', sheets: [
    { h: 'One real question', title: 'Live run', chip: { text: 'A leading question' }, layers: [
      { at: 0, svg: term([]) }, { at: 1, svg: Q }] },
    { h: 'The model was right', title: 'Live run', chip: { text: 'The model was right' }, layers: [
      { at: 0, svg: term([Q]) }, { at: 1, svg: R.join('') }] },
    { h: 'The check withheld it', title: 'Live run', chip: { text: 'Withheld · safe but strict', state: 'part' }, layers: [
      { at: 0, svg: term([Q, ...R]) + G[0] }, { at: 1, svg: G[1] }, { at: 2, svg: stamp(1360, 700, 400, 56, 'Safe but strict', 'part') }] },
    { h: 'The whole run', title: 'Results', chip: { text: '11 correct · 12 withheld · 1 wrong', state: 'part' }, layers: [
      { at: 0, svg: nums(380) + txt(120, 620, SRC, 'ref', C.dim) + stamp(120, 680, 520, 64, 'Target: 0 wrong. Missed.', 'part') }] },
  ] },
  rc: { script: 'recut/SCRIPT.md', sheets: [
    { h: 'Rules first, model last', title: 'How it works', chip: { text: 'Rules first, model last' }, layers: [
      { at: 0, svg: box(120, 360, 400, 160) + txt(150, 404, '01 Rules', 'lbl', C.ink) + txt(150, 470, 'Find the clauses', 'big') },
      { at: 1, svg: arrow(520, 440, 636, 440) + box(640, 360, 560, 160, C.ink) + fill(640, 360, 560, 160, TINT.ink) + txt(670, 404, '02 Checks', 'lbl', C.ink) + txt(670, 470, 'Six checks in code', 'big') },
      { at: 2, svg: arrow(1200, 440, 1316, 440) + box(1320, 360, 480, 160) + txt(1350, 404, '03 Model', 'lbl', C.ink) + txt(1350, 470, 'Writes last', 'big') }] },
    { h: 'What it promises', title: 'Trust', chip: { text: 'Facts, not decisions' }, layers: [
      ...[['Shows its source', 0], ['Figures match the text exactly', 0], ['Latest amendment wins', 1], ['Facts, not decisions', 2]]
        .map(([s, at], i) => ({ at, svg: box(120, 320 + i * 120, 1000, 96) + txt(150, 380 + i * 120, s, 'big') }))] },
    { h: 'A real model run', title: 'Results', chip: { text: '11 correct · 12 withheld · 1 wrong', state: 'part' }, layers: [
      { at: 1, svg: nums(340) + txt(120, 540, SRC, 'ref', C.dim) },
      { at: 2, svg: box(120, 600, 1680, 120, C.stale) + txt(150, 650, 'The 1 wrong', 'lbl', C.stale) + txt(150, 700, 'Gave the amended $35,000, but also named the old $20,000', 'sub') }] },
    { h: 'What it does not do', title: 'Honest gaps', chip: { text: 'Figures checked · meaning not', state: 'part' }, layers: [
      { at: 0, svg: hatch(120, 340, 1680, 140, C.part) + box(120, 340, 1680, 140, C.part, true) + txt(150, 424, 'Meaning not checked', 'big') },
      { at: 1, svg: hatch(120, 520, 1680, 140, C.part) + box(120, 520, 1680, 140, C.part, true) + txt(150, 586, 'Strict: 3 right answers withheld', 'big') + txt(150, 630, 'A3, A5 quoted the wrong number to correct it; I1 tripped on a clause number', 'sub', C.dim) }] },
    { h: 'Where it breaks', title: 'Your contracts', chip: { text: 'Clause types · not yet', state: 'part' }, layers: [
      { at: 1, svg: hatch(120, 380, 1680, 160, C.part) + box(120, 380, 1680, 160, C.part, true) + txt(150, 446, 'Clause types it has not seen', 'big') + txt(150, 496, 'For example, indemnity', 'sub', C.dim) }] },
  ] },
}[SET];

const script = fs.readFileSync(`${__dirname}/${SETS.script}`, 'utf8');
const nSent = n => script.split(/^## /m).find(s => s.startsWith(n)).split('\n\n')[1].trim().split(/(?<=[.!?]["”]?)\s+/).length;
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (let i = 0; i < SETS.sheets.length; i++) {
    const n = String(i + 1).padStart(2, '0'), sh = SETS.sheets[i], max = nSent(n) - 1;
    sh.layers.forEach(l => { if (l.at > max) throw new Error(`${n}: layer at ${l.at} but only ${max + 1} sentences`); });
    const ats = [...new Set([0, ...sh.layers.map(l => l.at)])].sort((a, c) => a - c);
    fs.writeFileSync(`${OUT}/${n}.ats.json`, JSON.stringify(ats));
    for (let k = 0; k < ats.length; k++) {
      await pg.setContent(K.page(sh, i + 1, SETS.sheets.length, ats[k], false)); await pg.waitForTimeout(150);
      await pg.screenshot({ path: `${OUT}/${n}-${k}.png` });
    }
    await pg.setContent(K.page(sh, i + 1, SETS.sheets.length, 99, true)); await pg.waitForTimeout(150);
    await pg.screenshot({ path: `${OUT}/${n}-chip.png` });
  }
  await b.close(); console.log('stills', OUT);
})();
