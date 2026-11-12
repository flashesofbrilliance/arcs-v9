// Recoil anatomy (arc weld spec 4.1), pure data: one SSOT v2 record in, the page plan out.
//
// Both renders read this plan: the React screen (src/document/screens/WarRoomReport.tsx)
// and the single-file HTML (scripts/recoil_page.py, which carries a line-for-line Python
// twin of this file). tests/unit/recoil-anatomy.test.ts fails when the two plans differ
// on any committed SSOT fixture, so the renders cannot drift apart.
//
// Rules set by code (spec 4.3), never by hand:
//   fidelity  grade A/B SHARP, C DEGRADED, D/E/not scored GRAIN, Y PARADOX MOIRE
//             (mirrors x-fidelity in runtime/specs/recoil-ssot-v2.schema.json; the test checks it)
//   tone      red = a failed check, gold = a limit, green = proven, cyan = action,
//             steel = unknown, magenta = paradox
// Old six-tab SSOTs are v2 already, once adapted (scripts/recoil_ssot_v2.py keeps every v1
// key in place), so this reads both without a separate path.

export type Tone = 'cyan' | 'green' | 'gold' | 'red' | 'steel' | 'magenta'
export type Fidelity = 'SHARP' | 'DEGRADED' | 'GRAIN' | 'MOIRE'
export type GroupName = 'Decide' | 'Evidence' | 'System' | 'Method'
export interface Chip { tone: Tone; label: string }
export interface GlanceRow { key: string; text: string; href: string; chip?: Chip }
export interface Forecast { id: string; claim: string; before: string; after: string; moved: boolean; fidelity: Fidelity; chip: Chip }
export interface Fold {
  id: string
  title: string
  verdict: string
  chip: Chip
  /** next: opportunity + next steps · forecasts: beliefs · blocks: an SSOT tab · verb: a v2 verb pass · glass: method */
  kind: 'next' | 'forecasts' | 'blocks' | 'verb' | 'glass'
  /** kind 'blocks': indexes into page.blocks, in authored order */
  blocks?: number[]
  verb?: string
}
export interface Anatomy {
  header: { eyebrow: string; title: string; lede: string; ref: string; chips: Chip[]; nciGrain: boolean }
  glance: GlanceRow[]
  groups: { name: GroupName; note: string; folds: Fold[] }[]
  forecasts: Forecast[]
  /** The standing limit (kit 58 toast, gold): the Ex-Ante receipt's falsifier, kill line or stop-loss. */
  guard: { title: string; text: string } | null
  appendix: { id: string; title: string; verdict: string }
}

type Raw = Record<string, unknown>
const isRec = (v: unknown): v is Raw => typeof v === 'object' && v !== null && !Array.isArray(v)
const str = (v: unknown) => (typeof v === 'string' ? v : v == null ? '' : String(v))
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : [])
const rec = (v: unknown): Raw => (isRec(v) ? v : {})

export const FIDELITY_BY_GRADE: Record<string, Fidelity> = { A: 'SHARP', B: 'SHARP', C: 'DEGRADED', D: 'GRAIN', E: 'GRAIN', NS: 'GRAIN' }
export const FIDELITY_Y_OVERRIDE: Record<string, Fidelity> = { PARADOX: 'MOIRE' }
export function fidelity(letter?: string | null, y?: string | null): Fidelity {
  if (y && FIDELITY_Y_OVERRIDE[y]) return FIDELITY_Y_OVERRIDE[y]
  return FIDELITY_BY_GRADE[letter || 'NS'] ?? 'GRAIN'
}
const FID_TONE: Record<Fidelity, Tone> = { SHARP: 'green', DEGRADED: 'gold', GRAIN: 'steel', MOIRE: 'magenta' }

/** Grade chip: letter and basis set the tone; grain prints its sample size. */
export function gradeChip(g: unknown): Chip {
  const gr = rec(g)
  const letter = str(gr.letter) || 'NS'
  const f = fidelity(letter)
  const n = typeof gr.n === 'number' ? gr.n : 0
  const name = letter === 'NS' ? 'Not scored' : `Grade ${letter}`
  return { tone: FID_TONE[f], label: f === 'GRAIN' ? `${name} · n = ${n}` : name }
}

// Y chip takes its own state color: green proven, gold limit (YELLOW, FORK), red failed,
// magenta paradox, violet DELTA is not a meaning color so it reads steel with the others.
const Y_TONE: Record<string, Tone> = { GREEN: 'green', YELLOW: 'gold', FORK: 'gold', RED: 'red', PARADOX: 'magenta' }

// ─── text ─────────────────────────────────────────────────────────────────
const NAMED: Record<string, string> = {
  amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', middot: '·', times: '×',
  mdash: '—', ndash: '–', hellip: '…', rarr: '→', larr: '←', ldquo: '“', rdquo: '”',
  lsquo: '‘', rsquo: '’', le: '≤', ge: '≥', ne: '≠', asymp: '≈', deg: '°',
}
/** HTML fragment to plain text: tags dropped, entities decoded, whitespace collapsed. */
export function plain(html: unknown): string {
  return str(html)
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]*>/g, '')
    .replace(/&#x([0-9a-f]+);/gi, (_, h: string) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d: string) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&([a-z]+);/gi, (m, n: string) => NAMED[n.toLowerCase()] ?? m)
    .replace(/\s+/g, ' ')
    .trim()
}
const MAX = 120
/** The first sentence, cut at a word to MAX characters. */
export function firstSentence(text: string): string {
  const t = text.trim()
  const m = /^(.+?[.?!])(\s|$)/.exec(t)
  return clip(m ? m[1] : t)
}
/** Cut at a word to MAX characters. */
export function clip(text: string): string {
  let s = text.trim()
  if (s.length > MAX) {
    const cut = s.slice(0, MAX - 1)
    const sp = cut.lastIndexOf(' ')
    s = `${(sp > 40 ? cut.slice(0, sp) : cut).replace(/[\s,;:.·-]+$/, '')}…`
  }
  return s
}
/** A step its author marked finished. */
const CLOSED = /^\s*(DONE|RESOLVED|CLOSED|SUPERSEDED|DROPPED)\b/
export const isOpenStep = (st: Raw) => !CLOSED.test(plain(st.text))
/** Owner and step, without the author's NEXT marker. */
const stepText = (st: Raw) => `${plain(st.owner)}: ${plain(st.text).replace(/^NEXT\b:?\s*/, '')}`
const sentence = (t: string) => (t && !/[.?!]$/.test(t) ? `${t}.` : t)
const PLACEHOLDER = /\{\{[^}]*\}\}|^\s*(TBD|TODO|PENDING)\s*$/i
const real = (v: unknown) => { const p = plain(v); return p && !PLACEHOLDER.test(p) ? p : '' }

/** The first real text a block carries, in the order a reader meets it. */
function blockText(b: Raw): string {
  const t = str(b.type)
  const cands: unknown[] = []
  if (t === 'receipt') for (const f of arr(b.fields)) if (isRec(f)) cands.push(`${plain(f.label)}: ${plain(f.value)}`)
  if (t === 'keyvalue') for (const r of arr(b.rows)) if (isRec(r)) cands.push(`${plain(r.k)}: ${plain(r.v)}`)
  cands.push(b.intro)
  for (const p of arr(b.p)) cands.push(p)
  for (const it of arr(b.items)) if (isRec(it)) cands.push(it.html ?? it.text)
  for (const c of cands) { const p = real(c); if (p && !/:\s*$/.test(p)) return p }
  return ''
}

// ─── method tabs ──────────────────────────────────────────────────────────
// Lifecycle order (PR 2145): Pre-Call, Ex-Ante, Forge, Recoil, War Game, Defensibility.
export const METHOD_RANK: Record<string, number> = { pre: 1, exante: 2, forge: 3, recoil: 4, wargame: 5, defense: 6 }

/** Forge claim table rulings, counted. */
function forgeRulings(blocks: Raw[]): Record<string, number> | null {
  for (const b of blocks) {
    if (str(b.type) !== 'table') continue
    const cols = arr(b.columns).map((c) => plain(c).toLowerCase())
    const ci = cols.findIndex((c) => c.includes('ruling'))
    if (ci < 0) continue
    const out: Record<string, number> = {}
    for (const r of arr(b.rows)) {
      const v = plain(arr(r)[ci]).toUpperCase()
      const k = ['GROUNDED', 'INFERENCE', 'STRUCK'].find((x) => v.includes(x)) ?? 'OTHER'
      out[k] = (out[k] ?? 0) + 1
    }
    return out
  }
  return null
}

function tabFold(id: string, label: string, tab: Raw, idx: number[], blocks: Raw[], fc: Forecast[]): Fold {
  const own = idx.map((i) => blocks[i])
  let verdict = real(tab.verdict)
  let chip: Chip = isRec(tab.grade) ? gradeChip(tab.grade) : { tone: 'steel', label: 'Not graded' }
  if (id === 'forge') {
    const r = forgeRulings(own)
    if (r) {
      const parts = [['GROUNDED', 'grounded'], ['INFERENCE', 'inference'], ['STRUCK', 'struck']]
        .filter(([k]) => r[k]).map(([k, w]) => `${r[k]} ${w}`)
      if (!verdict) verdict = `Claims on the call: ${parts.join(', ')}`
      if (!isRec(tab.grade)) chip = r.STRUCK ? { tone: 'red', label: `${r.STRUCK} struck` } : { tone: 'green', label: 'None struck' }
    }
  }
  if (id === 'recoil' && !verdict && fc.length) {
    const moved = fc.filter((f) => f.moved).length
    verdict = `${moved} of ${fc.length} beliefs moved on the call`
  }
  if (!verdict) for (const b of own) { const t = blockText(b); if (t) { verdict = t; break } }
  return { id: `f-${id}`, title: label, verdict: firstSentence(verdict || label), chip, kind: 'blocks', blocks: idx }
}

function forecasts(raw: Raw): Forecast[] {
  return arr(raw.beliefs).filter(isRec).map((b) => {
    const c = arr(b.confidence)
    const num = (v: unknown) => (typeof v === 'number' ? v : null)
    const a = num(c[0]), z = num(c.length > 1 ? c[1] : c[0])
    const f = fidelity(isRec(b.grade) ? str(b.grade.letter) : null)
    return {
      id: str(b.id), claim: plain(b.claim),
      before: a == null ? 'not held' : String(a), after: z == null ? '--' : String(z),
      moved: a != null && z != null && a !== z, fidelity: f, chip: gradeChip(b.grade),
    }
  })
}

// ─── the plan ─────────────────────────────────────────────────────────────
export function anatomy(raw: Raw): Anatomy {
  const meta = rec(raw.meta)
  const opp = rec(raw.opportunity)
  const page = rec(raw.page)
  const hd = rec(page.header)
  const blocks = arr(page.blocks).map(rec)
  const fc = forecasts(raw)

  // header
  const y = str(opp.y_state).trim().toUpperCase()
  const chips: Chip[] = []
  if (y) chips.push({ tone: Y_TONE[y] ?? 'steel', label: `Y · ${y}` })
  // Both zero is the template default, not a score (Schriner 2026-09-14 carries 0 and 0 on a YELLOW call).
  const zero = (v: unknown) => v === 0 || v == null
  const scored = (typeof opp.nci_prior === 'number' || typeof opp.nci_post === 'number') && !(zero(opp.nci_prior) && zero(opp.nci_post))
  chips.push(scored
    ? { tone: 'steel', label: `NCI ${opp.nci_prior ?? '--'} → ${opp.nci_post ?? '--'}` }
    : { tone: 'steel', label: 'NCI · not scored · n = 0' })
  const ref = [str(meta.date), str(meta.counterpart), str(meta.report_id)].filter(Boolean).join(' · ')
  const lede = [sentence(real(hd.sub)), 'NCI is the Net Coherence Index.'].filter(Boolean).join(' ')
  const header = {
    eyebrow: plain(hd.eyebrow) || 'Recoil',
    title: plain(hd.title) || [str(meta.counterpart), str(meta.date)].filter(Boolean).join(' · '),
    lede, ref, chips, nciGrain: !scored,
  }

  // tabs into folds; blocks with no known tab go to one Unfiled fold
  const tabs = arr(page.tabs).filter(isRec).map((t) => ({ id: str(t.id), label: plain(t.label), tab: t }))
  const known = new Set(tabs.map((t) => t.id))
  const byTab = (id: string) => blocks.map((b, i) => ({ b, i })).filter((x) => str(x.b.tab) === id).map((x) => x.i)
  const loose = blocks.map((b, i) => ({ b, i })).filter((x) => !known.has(str(x.b.tab))).map((x) => x.i)
  const tabFolds = tabs
    .map((t) => ({ ...t, idx: byTab(t.id) }))
    .filter((t) => t.idx.length)
    .map((t) => ({ t, both: t.idx.every((i) => str(blocks[i].audience) === 'both'), fold: tabFold(t.id, t.label, t.tab, t.idx, blocks, fc) }))

  const evidence: Fold[] = []
  const verbs = rec(raw.verbs)
  for (const v of ['analyze', 'assess', 'evaluate', 'synthesize', 'recapitulate']) {
    const p = rec(verbs[v])
    if (!str(p.verdict)) continue
    evidence.push({ id: `f-verb-${v}`, title: v[0].toUpperCase() + v.slice(1), verdict: firstSentence(plain(p.verdict)), chip: gradeChip(p.grade), kind: 'verb', verb: v })
  }
  evidence.push(...tabFolds.filter((x) => x.both && !(x.t.id in METHOD_RANK)).map((x) => x.fold))
  evidence.push(...tabFolds.filter((x) => x.t.id in METHOD_RANK).sort((a, b) => METHOD_RANK[a.t.id] - METHOD_RANK[b.t.id]).map((x) => x.fold))
  const system = tabFolds.filter((x) => !x.both && !(x.t.id in METHOD_RANK)).map((x) => x.fold)
  if (loose.length) system.push(tabFold('unfiled', tabs.length ? 'Unfiled' : 'Brief', {}, loose, blocks, fc))

  // Decide: where it stands, then the forecasts
  const decide: Fold[] = []
  const steps = arr(raw.next_steps).filter(isRec)
  const openSteps = steps.filter(isOpenStep)
  if (real(opp.note) || steps.length) {
    const s0 = openSteps.find((x) => /^\s*NEXT\b/.test(plain(x.text))) ?? openSteps[0]
    decide.push({
      id: 'f-next', title: 'Where it stands',
      verdict: firstSentence(s0 ? stepText(s0) : real(opp.note)),
      chip: { tone: 'cyan', label: steps.length ? `${openSteps.length} open of ${steps.length}` : 'Note' },
      kind: 'next',
    })
  }
  if (fc.length) {
    const graded = fc.filter((f) => f.fidelity !== 'GRAIN').length
    decide.push({
      id: 'f-forecasts', title: 'Forecasts',
      verdict: `${fc.filter((f) => f.moved).length} of ${fc.length} beliefs moved; ${graded ? `${graded} graded` : 'none graded, so all render grain'}`,
      chip: graded ? { tone: 'steel', label: `${graded} of ${fc.length} graded` } : { tone: 'steel', label: `Not scored · n = 0` },
      kind: 'forecasts',
    })
  }

  const mig = rec(raw.migration)
  const from = str(mig.from) || (str(raw.schema) ? 'v2' : 'six-tab.v1')
  const method: Fold[] = [{
    id: 'f-glass', title: 'Glass box',
    verdict: `Rendered by code from ${str(meta.report_id) || 'this SSOT'} (${from}); fidelity and color set from grade and Y state`,
    chip: { tone: 'steel', label: 'How it was made' }, kind: 'glass',
  }]

  const groups = ([
    { name: 'Decide', note: 'what to do next', folds: decide },
    { name: 'Evidence', note: 'what the decision rests on, method in lifecycle order', folds: evidence },
    { name: 'System', note: 'what else this record holds', folds: system },
    { name: 'Method', note: 'how this page was made', folds: method },
  ] as Anatomy['groups']).filter((g) => g.folds.length)

  // glance: next move first, at most five rows
  const glance: GlanceRow[] = []
  const all = groups.flatMap((g) => g.folds)
  const href = (id: string) => (all.some((f) => f.id === id) ? `#${id}` : '')
  // The step its author marked NEXT leads; otherwise the first open one.
  const n0 = openSteps.find((x) => /^\s*NEXT\b/.test(plain(x.text))) ?? openSteps[0]
  if (n0) glance.push({ key: 'Next move', text: clip(stepText(n0)), href: '#f-next', chip: { tone: 'cyan', label: plain(n0.owner) || 'Owner' } })
  else glance.push({ key: 'Next move', text: 'No open next step in this record.', href: '', chip: { tone: 'steel', label: 'None on record' } })
  const quote = real(rec(meta.provenance).load_bearing_quote)
  const firstEv = evidence[0]
  if (quote) glance.push({ key: 'Signal', text: clip(quote), href: '#f-strata' })
  else if (firstEv) glance.push({ key: 'Signal', text: firstEv.verdict, href: `#${firstEv.id}` })
  if (openSteps.length) {
    const owners: Record<string, number> = {}
    for (const s of openSteps) { const o = plain(s.owner) || 'Unowned'; owners[o] = (owners[o] ?? 0) + 1 }
    glance.push({ key: 'Owed', text: Object.entries(owners).map(([o, n]) => `${o} owes ${n}`).join(', '), href: '#f-next' })
  }
  if (fc.length) glance.push({ key: 'Forecasts', text: decide[decide.length - 1].verdict, href: '#f-forecasts', chip: decide[decide.length - 1].chip })
  const pre = all.find((f) => f.id === 'f-pre')
  glance.push(pre
    ? { key: 'Pre-call', text: pre.verdict, href: href('f-pre') }
    : { key: 'Pre-call', text: 'No pre-call tab in this record.', href: '', chip: { tone: 'steel', label: 'None on record' } })

  let guard: Anatomy['guard'] = null
  for (const b of blocks) {
    if (str(b.tab) !== 'exante' || str(b.type) !== 'receipt') continue
    const f = arr(b.fields).filter(isRec).find((x) => /falsifier|kill|stop.?loss/i.test(plain(x.label)) && real(x.value))
    if (f) { guard = { title: plain(f.label), text: real(f.value) }; break }
  }

  return {
    header, glance: glance.slice(0, 5), groups, forecasts: fc, guard,
    appendix: { id: 'f-strata', title: 'Deeper Strata', verdict: 'Provenance and every key the folds above do not render, verbatim' },
  }
}
