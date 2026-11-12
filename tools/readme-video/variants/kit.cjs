// Blueprint storyboard kit: atoms and molecules that every sheet snaps together.
// Tokens follow arcs-v9 DESIGN.md (the repo SSOT). Color is state: cyan bearing/linework,
// green passed (c-ok), gold partial/not run (c-part), red caught/refused (c-stale).
const fs = require('fs');
const F = '/Users/zharris/arcs-v9/.claude/worktrees/ai-product-ownership-roadmap-78910c/public/fonts/';
const b64 = f => fs.readFileSync(F + f).toString('base64');

const C = { ground: '#020408', panel: '#0d1117', rule: '#1e293b', ink: '#00F0FF', text: '#e2e8f0', dim: '#94a3b8',
  ok: '#00FF9D', part: '#FFD700', stale: '#FF4D6D' };
const TINT = { ok: 'rgba(0,255,157,.07)', part: 'rgba(255,215,0,.07)', stale: 'rgba(255,77,109,.07)', ink: 'rgba(0,240,255,.07)' };

const GF = fs.readFileSync(__dirname + '/kit/glass-frame.html', 'utf8');
const gfCss = GF.match(/<style>([\s\S]*?)<\/style>/)[1], gfHtml = GF.match(/<template[^>]*>([\s\S]*?)<\/template>/)[1];
const glassFrame = label => gfHtml.replace('{{LABEL}}', label);
const css = gfCss + `
@font-face{font-family:Inter;src:url(data:font/woff2;base64,${b64('inter-normal-100-900-latin-v1.woff2')})}
@font-face{font-family:JBM;src:url(data:font/woff2;base64,${b64('jetbrains-mono-normal-100-800-latin-v1.woff2')})}
*{box-sizing:border-box}
body{margin:0;width:1920px;height:1080px;background:${C.ground};color:${C.text};font-family:Inter,sans-serif;position:relative;overflow:hidden;
 background-image:linear-gradient(#11222f 1px,transparent 1px),linear-gradient(90deg,#11222f 1px,transparent 1px),
 linear-gradient(#0b1620 1px,transparent 1px),linear-gradient(90deg,#0b1620 1px,transparent 1px);
 background-size:200px 200px,200px 200px,40px 40px,40px 40px;background-position:-1px -1px}
:root{--fs-label:.8rem;--fs-body:.925rem;--fs-head:1.15rem;--fs-display:clamp(1.5rem,4vw,2.4rem);--fs-meta:.8125rem}
html{font-size:calc(100vw / 64)} /* the frame scale: one root per render target, 30px at 1920 wide */
.eb{position:absolute;left:120px;top:92px;font-family:JBM;font-size:var(--fs-label);font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:${C.ink}}
.h{position:absolute;left:120px;top:128px;margin:0;color:#fff}
h1.h{font-family:JBM;font-weight:700;font-size:var(--fs-display);letter-spacing:-0.01em}
h2.h{font-family:Inter;font-weight:500;font-size:var(--fs-head);letter-spacing:-0.02em}
svg{position:absolute;left:0;top:0}
.lbl{font-family:JBM;font-size:var(--fs-label);letter-spacing:.12em;text-transform:uppercase;font-weight:700}
.big{font-family:Inter;font-weight:500;font-size:var(--fs-head)}
.sub{font-family:Inter;font-size:var(--fs-body)}
.mono{font-family:JBM;font-size:var(--fs-body)}
.ref{font-family:JBM;font-size:var(--fs-meta)}
.tb{position:absolute;right:96px;bottom:54px;display:grid;grid-template-columns:auto auto;border-left:1.5px solid ${C.rule};border-top:1.5px solid ${C.rule};font-family:JBM;font-size:var(--fs-label);letter-spacing:.12em;text-transform:uppercase;background:${C.ground}}
.tb div{padding:14px 22px;border-right:1.5px solid ${C.rule};border-bottom:1.5px solid ${C.rule};color:${C.dim}}
.tb b{display:block;color:${C.text};font-weight:500;font-size:var(--fs-body);letter-spacing:0;margin-top:6px;text-transform:none;font-family:Inter}
.chip{position:absolute;left:120px;bottom:96px;display:flex;align-items:center;gap:16px;padding:18px 28px;border-radius:3px;font-family:JBM;font-size:var(--fs-body);font-weight:700;letter-spacing:0;color:${C.text};background:${C.panel}}
.chip i{width:14px;height:14px;border-radius:50%}
`;

// ── atoms ──
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const txt = (x, y, s, cls, color = C.text, anchor = 'start', extra = '') =>
  `<text class="${cls}" x="${x}" y="${y}" text-anchor="${anchor}" style="fill:${color}" ${extra}>${esc(s)}</text>`;
const box = (x, y, w, h, color = C.ink, dash = false, sw = 2) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="${color}" stroke-width="${sw}"${dash ? ' stroke-dasharray="14 10"' : ''}/>`;
const fill = (x, y, w, h, tint) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${tint}"/>`;
const arrow = (x1, y1, x2, y2, color = C.ink) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="2" marker-end="url(#ar-${color.slice(1)})"/>`;
const line = (x1, y1, x2, y2, color = C.ink, sw = 1.5, dash = false) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}"${dash ? ' stroke-dasharray="6 8"' : ''}/>`;
const hatch = (x, y, w, h, color) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#hatch-${color.slice(1)})"/>`;

// ── molecules ──
// Stage: numbered box with a label, a headline and an optional sub line.
const stage = (x, y, w, h, n, label, lines, sub) =>
  box(x, y, w, h) + txt(x + 24, y + 38, `${n} ${label}`, 'lbl', C.ink) +
  lines.map((l, i) => txt(x + 24, y + 100 + i * 42, l, 'big')).join('') + (sub ? txt(x + 24, y + 100 + lines.length * 42 + 4, sub, 'sub', C.dim) : '');
// Dimension line: a span with end ticks and a label above.
const dim = (x1, x2, y, label, color = C.ink) =>
  line(x1, y, x2, y, color, 2) + line(x1, y - 14, x1, y + 14, color, 2) + line(x2, y - 14, x2, y + 14, color, 2) +
  txt((x1 + x2) / 2, y - 20, label, 'lbl', color, 'middle');
// Callout: dot on the part, leader line, label at the end.
const callout = (px, py, lx, ly, label, color = C.ink) =>
  `<circle cx="${px}" cy="${py}" r="6" fill="${color}"/>` + line(px, py, lx - 14, ly - 8, color, 1.5) + txt(lx, ly, label, 'lbl', color);
// Stamp: tinted, bordered verdict block.
const stamp = (x, y, w, h, s, state) => fill(x, y, w, h, TINT[state]) + box(x, y, w, h, C[state], false, 2) + txt(x + w / 2, y + h / 2 + 11, s, 'lbl', C[state], 'middle');

const defs = `<defs>${[C.ink, C.ok, C.part, C.stale, C.dim].map(c =>
  `<marker id="ar-${c.slice(1)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="${c}"/></marker>
   <pattern id="hatch-${c.slice(1)}" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="16" stroke="${c}" stroke-opacity=".2" stroke-width="3"/></pattern>`).join('')}</defs>`;

// ── template: one sheet, with layers revealed up to `upto` and the chip when `withChip` ──
function page(sheet, n, total, upto, withChip) {
  const layers = sheet.layers.filter(l => l.at <= upto).map(l => l.svg).join('');
  const st = sheet.chip.state || 'ok';
  const chip = withChip ? `<div class="chip" style="border:1.5px solid ${C[st]};background:linear-gradient(${TINT[st]},${TINT[st]}),${C.panel}"><i style="background:${C[st]}"></i>${esc(sheet.chip.text)}</div>` : '';
  return `<html><head><style>${css}</style></head><body>${glassFrame(`${String(n).padStart(2, '0')} / ${String(total).padStart(2, '0')}`)}
<svg width="1920" height="1080" viewBox="0 0 1920 1080">${defs}${layers}</svg>
<div class="eb">${esc(sheet.title)}</div>${n === 1 ? `<h1 class="h">${esc(sheet.h)}</h1>` : `<h2 class="h">${esc(sheet.h)}</h2>`}${chip}</body></html>`;
}


// Voice spans for the music ride: [start, end] seconds of speech in one take, from silencedetect.
function voiceSpans(audio, dur) {
  const log = require('child_process').execFileSync('sh', ['-c', `ffmpeg -hide_banner -i "${audio}" -af silencedetect=n=-38dB:d=0.18 -f null - 2>&1`]).toString();
  const gaps = [...log.matchAll(/silence_start: ([0-9.]+)[\s\S]*?silence_end: ([0-9.]+)/g)].map(m => [+m[1], +m[2]]);
  const out = []; let s0 = 0;
  for (const [a, b] of gaps) { if (a > s0 + 0.05) out.push([s0, a]); s0 = b; }
  if (s0 < dur - 0.05) out.push([s0, dur]);
  return out;
}

module.exports = { glassFrame, voiceSpans, C, TINT, txt, box, fill, arrow, line, hatch, stage, dim, callout, stamp, page };
