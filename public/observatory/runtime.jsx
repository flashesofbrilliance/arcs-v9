// ARCS Observatory — STATIC RUNTIME (code only; carries NO data).
//
// Data is hot-swappable at runtime: payloads live in data.<slug>.json and are
// listed in datasets.json. index.html fetches a payload, calls hydrateObservatory(p),
// then mounts <App>. Swapping datasets re-hydrates window + remounts <App> — no reload,
// no rebuild, no redeploy.
//
// This file is hand-maintained code. scripts/build_observatory.py refreshes the JSON
// payloads ONLY; it never rewrites this runtime. Token maps + helpers are the verbatim
// contract every view file (timeline/deck/views/tweaks-panel) reads off `window`.

const C = { cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", orange: "#ff9d3c", red: "#FF4D6D", steel: "#94a3b8" };
const ALT = {
  L5: { name: "EXECUTIVE",   accent: C.green },
  L4: { name: "STRATEGIC",   accent: C.cyan },
  L3: { name: "OPERATIONAL", accent: C.gold },
  L2: { name: "TACTICAL",    accent: C.orange },
  L1: { name: "SURGICAL",    accent: C.red },
};
const GRADE = { A: C.green, B: C.cyan, C: C.gold, D: C.orange, F: C.red };
const SEV = { RUIN: C.red, HIGH: C.orange, MED: C.gold };
const STATUS = { AVERTED: C.green, MITIGATED: C.gold, OPEN: C.red };
const TYPE_COLOR = { genesis: C.green, canon: C.green, kairos: C.gold, milestone: C.cyan, feat: C.cyan, security: C.red, fix: C.orange };

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// span — set by hydrateObservatory from the active payload. leftPct reads the live
// `let` bindings so positions recompute when a dataset is swapped in.
let SPAN_START = Date.parse("2026-05-27"), SPAN_DAYS = 11;
const leftPct = (d) => Math.round(((Date.parse(d) - SPAN_START) / 86400000 / SPAN_DAYS) * 1000) / 10;

function groupKeys(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  const day = `${DOW[d.getDay()]} · ${MON[d.getMonth()]} ${d.getDate()}`;
  const monday = new Date(d); monday.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  const week = `Week of ${MON[monday.getMonth()]} ${monday.getDate()}`;
  const month = `${["January","February","March","April","May","June","July","August","September","October","November","December"][d.getMonth()]} ${d.getFullYear()}`;
  return { day, week, month };
}
function matchQ(x, q) {
  if (!q || !q.trim()) return true;
  const s = q.trim().toLowerCase();
  const hay = [x.label, x.risk, x.type, x.alt, x.status, x.sev, x.sha, x.desc, x.note, x.lab, x.grade, x.how, x.kind,
    x.alt && ALT[x.alt] && ALT[x.alt].name].filter(Boolean).join(" ").toLowerCase();
  return hay.includes(s);
}
function stepIndices(focus) {
  const LEDGER = window.LEDGER || [];
  return (!focus || focus === "all") ? LEDGER.map((_, i) => i) : LEDGER.map((x, i) => (x.alt === focus ? i : -1)).filter(i => i >= 0);
}

// ── hydrateObservatory(payload) — install a (swapped) dataset onto window ────────
// MUST run before <App> mounts. Recomputes LEDGER + repo link from the payload and
// republishes the full global contract the view files read.
function hydrateObservatory(p) {
  p = p || {};
  const slug = p.repo || "flashesofbrilliance/arcs-v9";
  const REPO = "https://github.com/" + slug + "/commit/";
  SPAN_START = Date.parse(p.span_start || "2026-05-27");
  SPAN_DAYS = p.span_days || 11;
  const EVENTS = p.events || [];
  const RISKS = p.risks || [];
  const LAYERS = p.layers || [];
  const REDACTED_OPEN_RISKS = p.redacted_open_risks || 0;
  const LEDGER = [...EVENTS.map(e => ({ ...e, kind: "event" })), ...RISKS.map(r => ({ ...r, kind: "risk" }))]
    .map(x => ({ ...x, left: leftPct(x.date) }))
    .sort((a, b) => Date.parse(a.date) - Date.parse(b.date) || (a.kind === "event" ? -1 : 1));
  Object.assign(window, {
    C, REPO, ALT, GRADE, SEV, STATUS, TYPE_COLOR,
    EVENTS, RISKS, LAYERS, LEDGER,
    leftPct, groupKeys, matchQ, stepIndices,
    REDACTED_OPEN_RISKS, SPAN_START, SPAN_DAYS,
    OBS_DATASET: { repo: slug, label: p.label, generated_at: p.generated_at, head_sha: p.head_sha, attribution: p.attribution },
  });
  return window.OBS_DATASET;
}
window.hydrateObservatory = hydrateObservatory;
