// War-room SSOT → RecoilReport adapter (pure, no React, no I/O).
//
// Engagement SSOTs (runtime/recoil/generated/*.json, the 6-tab template
// scaffolded by /recoil-new) carry a different vocabulary from the
// RecoilReportData props that RecoilReportFromData renders. This maps one onto
// the other. The output uses the FLAT shape, which normalizeRecoilReport passes
// through unchanged, so `<RecoilReportFromData data={warroomToRecoilReport(ssot)} />`
// works without touching the screen.
//
// Field map (SSOT → prop). Anything without an honest source stays undefined;
// the adapter never invents copy.
//   page.header.title (else meta.doc_title, else meta.counterpart) → cover.title
//   page.header.sub                                                → cover.subtitle
//   'War Room' + opportunity.y_state                               → cover.badges
//   meta.date · meta.segments · opportunity.engagement_type        → cover.meta
//   meta.provenance.load_bearing_quote                             → loadBearingQuote.text
//   meta.counterpart · meta.date                                   → loadBearingQuote.attribution
//   insights[] {plane,title,text}                                  → signalThreads[]
//   beliefs[] {id,verdict,claim,evidence}                          → signalThreads[] (after insights)
//   page.blocks[tab=exante, type=receipt] fields                   → protocol[] (first)
//     Pre-committed move / Falsifier / Kill line; label "Ex-ante", or "Ex-ante (reconstructed)"
//     when the receipt's h2 says reconstructed/post-hoc (ADR-044: never pass as filed-before)
//   page.blocks[tab=forge, type=table, h2~/claim/] rows            → signalThreads[] (after beliefs)
//     columns found by name (claim / ruling / source|why|evidence); label "Forge · RULING";
//     GROUNDED green, INFERENCE gold, STRUCK red (struck claims stay visible, marked)
//   page.blocks[tab=forge, type=prose] p[]                         → forgeMethod string (Deeper Strata):
//     the substrates and ruling definitions behind the Forge threads, verbatim
//   kinematic_series {dt, series[]} (the War Game kinematics_table) → beliefKinematics (Deeper Strata):
//     per series "trajectory · D1 peak/term · D2 term · D3 term · grounded: quote", plus the n-point
//     caveat; derivatives from ../kinematics (same central difference as WarRoomReport + recoil_brief.py)
//   next_steps[] {owner,text}                                      → protocol[] (after; first one active)
//   page.blocks[tab=wargame, type=list] ("The gauntlet") items     → riskFlags[]
//     <strong>LENS:</strong> prefix → label; BAR=warning, Loki=caution, COURT=info, else by dot
//     list `intro` → gauntletIntro string (Deeper Strata), only when that list yielded a flag
//   page.blocks[tab=recoil, type=list, h2~/kairos/] items          → riskFlags[] (after the gauntlet)
//     Risk=warning, Kairos=info, Quiet signal=success; unlabeled items by dot (red/gold/green)
//     list `intro` → kairosIntro string (Deeper Strata), only when that list yielded a flag
//   page.blocks[tab=wargame, type=table] (ATG pre-mortem) rows     → scenarios.worst
//     ("assume dead": node, failure mode, handling; BOTTLENECK row → note)
//   page.blocks[tab=recoil, type=keyvalue] ("Receipt closed ...")  → callWalk[] (one step per close,
//     authored order; label = date in the h2 else meta.date; title = h2 after "Receipt closed";
//     body = Actual + Fork hit rows; peak never set: the SSOT does not rank closes)
//   page.blocks[tab=pre, type=prose, h2~/^true north/] p[]          → preCallTrueNorth string (Deeper Strata,
//     first of the pre-call strata); an h2 qualifier such as "(reconstructed post-hoc)" leads the text
//   page.blocks[tab=pre, type=keyvalue] rows {k,v}                 → preCallContext {k: v} (not a
//     RecoilReportData prop: RecoilReportFromData's Deeper Strata renders any extra key, verbatim)
//   page.blocks[tab=pre, type=list, h2~/intel/] items              → preCallIntel string[] (Deeper
//     Strata); "Lead-in: body" when the item has a bold lead-in, else the body alone (no invented keys)
//   page.blocks[tab=pre, type=list, h2~/question|landmine|moves/]:
//     items led by "Landmine..."                                   → riskFlags[] (after Kairos; caution,
//                                                                    warning when "unresolved"; label verbatim)
//     every other item                                             → preCallQuestions string[] (Deeper Strata,
//                                                                    same "Lead-in: body" format as Intel)
//   (no source)                                                    → scenarios.best, scenarios.base
//   (no source)                                                    → cover.actions = [] (explicit: hides
//                                                                    the screen's inert default buttons)
//
// Unfilled template placeholders ({{...}}) and bare TBD/TODO/PENDING are treated as absent.
//
// Audience air-gap: every SSOT node is tagged `audience: internal | both`.
// `{ audience: 'external' }` keeps only nodes explicitly tagged `both`;
// untagged nodes fail closed. The default 'internal' keeps everything.
//
// JSON arrays may arrive as TEXT strings (Prisma TEXT columns); every list
// read goes through parseList, which tolerates a stringified array.

import { T } from '../tokens'
import { derivatives, kinematicsNote } from '../kinematics'
import type { RecoilReportData } from '../screens/RecoilReport'
import type { AsideVariant } from '../patterns/AsideBox'

export type WarroomAudience = 'internal' | 'external'

export interface WarroomRecoilReport {
  cover?: Partial<RecoilReportData['cover']>
  loadBearingQuote?: RecoilReportData['loadBearingQuote']
  callWalk?: RecoilReportData['callWalk']
  signalThreads?: RecoilReportData['signalThreads']
  scenarios?: Partial<RecoilReportData['scenarios']>
  riskFlags?: RecoilReportData['riskFlags']
  protocol?: RecoilReportData['protocol']
  /** Pre-Call Context rows, rendered by the screen's Deeper Strata section. */
  /** Pre-Call True North (the bearing), rendered by the screen's Deeper Strata section. */
  preCallTrueNorth?: string
  preCallContext?: Record<string, string>
  /** Pre-Call Intel items, rendered by the screen's Deeper Strata section. */
  preCallIntel?: string[]
  /** Pre-Call questions and scripted moves (landmines go to riskFlags). */
  preCallQuestions?: string[]
  /** Forge-tab method prose (substrates + ruling definitions), rendered by Deeper Strata. */
  forgeMethod?: string
  /** Belief trajectories with D1-D3 (the War Game kinematics table), rendered by Deeper Strata. */
  beliefKinematics?: Record<string, string>
  /** What the War Game gauntlet targets (its list intro), rendered by Deeper Strata. */
  gauntletIntro?: string
  /** How the recoil-tab Kairos watch-list was read (its intro), rendered by Deeper Strata. */
  kairosIntro?: string
}

type Rec = Record<string, unknown>

function isRecord(v: unknown): v is Rec {
  return typeof v === 'object' && v !== null && !Array.isArray(v)
}

function parseMaybeJson(v: unknown): unknown {
  if (typeof v !== 'string') return v
  const s = v.trim()
  if (!(s.startsWith('[') || s.startsWith('{'))) return v
  try {
    return JSON.parse(s)
  } catch {
    return v
  }
}

function parseList(v: unknown): unknown[] {
  const p = parseMaybeJson(v)
  return Array.isArray(p) ? p : []
}

function rec(v: unknown): Rec {
  const p = parseMaybeJson(v)
  return isRecord(p) ? p : {}
}

// Every named entity found in the SSOT corpus (the corpus unit test fails on any
// entity left undecoded, so a new one shows up there first).
const ENTITIES: Record<string, string> = {
  amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', middot: '\u00b7', times: '\u00d7',
  mdash: '\u2014', ndash: '\u2013', hellip: '\u2026',
  lsquo: '\u2018', rsquo: '\u2019', ldquo: '\u201c', rdquo: '\u201d',
  rarr: '\u2192', larr: '\u2190', uarr: '\u2191', darr: '\u2193',
  ntilde: '\u00f1', eacute: '\u00e9',
}

// SSOT strings are authored for the HTML war-room renderer: decode entities and
// strip inline tags so the React screen receives plain text.
function text(v: unknown): string | undefined {
  if (typeof v !== 'string') return undefined
  const out = v
    // Redaction spans (text colour == background) mask filler, not content.
    .replace(/<span[^>]*background:\s*([^;"]+);\s*color:\s*\1[^>]*>[\s\S]*?<\/span>/gi, '')
    .replace(/<[^>]*>/g, '')
    .replace(/&#(\d+);/g, (_, n: string) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n: string) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/&([a-z]+);/gi, (m, n: string) => ENTITIES[n.toLowerCase()] ?? m)
    .trim()
  // Unfilled template slots ({{...}}) and bare TBD/PENDING markers are absent, not content.
  return out.length && !out.includes('{{') && !/^(TBD|TODO|PENDING)\.?$/i.test(out) ? out : undefined
}

function join(parts: (string | undefined)[], sep = ' · '): string | undefined {
  const kept = parts.filter((p): p is string => !!p)
  return kept.length ? kept.join(sep) : undefined
}

function visible(node: unknown, audience: WarroomAudience): boolean {
  if (audience === 'internal') return true
  return isRecord(node) && node.audience === 'both'
}

const LENS_VARIANT: [RegExp, AsideVariant][] = [
  [/^BAR/i, 'warning'], [/LOKI/i, 'caution'], [/^COURT/i, 'info'],
  [/^RISK/i, 'warning'], [/^KAIROS/i, 'info'], [/^QUIET SIGNAL/i, 'success'],
]
const DOT_VARIANT: Record<string, AsideVariant> = { red: 'warning', r: 'warning', gold: 'caution', g: 'success', green: 'success' }

// List items lead with `<strong>LENS:</strong>` (some files use a coloured
// `<span>` instead); split that off as the label.
function splitLens(html: unknown): { label?: string; body?: string } {
  if (typeof html !== 'string') return {}
  const m = html.match(/^\s*<(strong|span)\b[^>]*>([^<]+?):?<\/\1>:?\s*([\s\S]*)$/)
  if (!m) return { body: text(html) }
  return { label: text(m[2])?.replace(/[\s:]+$/, ''), body: text(m[3].replace(/^\s*:\s*/, ''))?.replace(/^[\u2014\u2013-]\s*/, '') }
}

function wargameBlocks(root: Rec, audience: WarroomAudience): Rec[] {
  return parseList(rec(root.page).blocks).filter((b): b is Rec => isRecord(b) && b.tab === 'wargame' && visible(b, audience))
}

function flagsFromLists(blocks: Rec[], fallbackLabel: string): RecoilReportData['riskFlags'] {
  const flags: RecoilReportData['riskFlags'] = []
  for (const b of blocks) {
    if (b.type !== 'list') continue
    for (const item of parseList(b.items)) {
      if (!isRecord(item)) continue
      const { label, body } = splitLens(item.html)
      if (!body) continue
      const variant = (label ? LENS_VARIANT.find(([re]) => re.test(label))?.[1] : undefined) ?? DOT_VARIANT[String(item.dot)] ?? 'info'
      flags.push({ variant, label: label ?? fallbackLabel, body })
    }
  }
  return flags
}

const EX_ANTE_FIELDS = /^(pre-committed move|falsifier|kill line)$/i

function exAnteSteps(root: Rec, audience: WarroomAudience): RecoilReportData['protocol'] {
  const steps: RecoilReportData['protocol'] = []
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'exante' || b.type !== 'receipt' || !visible(b, audience)) continue
    const label = /reconstructed|post-hoc/i.test(text(b.h2) ?? '') ? 'Ex-ante (reconstructed)' : 'Ex-ante'
    for (const f of parseList(b.fields)) {
      if (!isRecord(f)) continue
      const title = text(f.label)
      const body = text(f.value)
      if (title && body && EX_ANTE_FIELDS.test(title)) steps.push({ label, title, body })
    }
  }
  return steps
}

function preCallTrueNorth(root: Rec, audience: WarroomAudience): string | undefined {
  const parts: string[] = []
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'pre' || b.type !== 'prose' || !visible(b, audience)) continue
    const h2 = text(b.h2) ?? ''
    if (!/^true north/i.test(h2)) continue
    const body = parseList(b.p).map(text).filter((x): x is string => !!x).join('\n\n')
    if (!body) continue
    // Keep the heading's own qualifier so a reconstructed bearing never reads as filed-before.
    const qualifier = h2.match(/\(([^)]+)\)/)?.[1]
    parts.push(qualifier ? `(${qualifier}) ${body}` : body)
  }
  return parts.length ? parts.join('\n\n') : undefined
}

function forgeMethod(root: Rec, audience: WarroomAudience): string | undefined {
  const parts: string[] = []
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'forge' || b.type !== 'prose' || !visible(b, audience)) continue
    // Paragraph-level: a half-filled template paragraph ("{{sources}}") drops whole.
    parts.push(...parseList(b.p).map(text).filter((x): x is string => !!x))
  }
  return parts.length ? parts.join('\n\n') : undefined
}

function beliefKinematics(root: Rec, audience: WarroomAudience): Record<string, string> | undefined {
  const ks = rec(root.kinematic_series)
  const dt = typeof ks.dt === 'number' && ks.dt > 0 ? ks.dt : 1
  const out: Record<string, string> = {}
  let n = 0
  for (const x of parseList(ks.series)) {
    if (!isRecord(x) || !visible(x, audience)) continue
    const points = parseList(x.points).map(Number).filter((v) => Number.isFinite(v))
    const label = text(x.label) ?? text(x.key)
    if (!label || points.length === 0) continue
    const k = derivatives(points, dt)
    const quote = text(x.grounding_quote)
    let key = label
    for (let i = 2; key in out; i++) key = `${label} (${i})`
    out[key] = [
      points.join(' \u2192 '),
      `D1 peak/term ${k.d1Peak} / ${k.d1Term}`,
      `D2 term ${k.d2Term}`,
      `D3 term ${k.d3Term}`,
      ...(quote ? [`grounded: ${quote}`] : []),
    ].join(' \u00b7 ')
    n = Math.max(n, points.length)
  }
  if (!Object.keys(out).length) return undefined
  return { ...out, method: kinematicsNote(n) }
}

// A list intro frames that list's flags; scaffolds keep the template intro with
// unfilled items, so an intro is kept only when its own list produced a flag.
function listIntro(blocks: Rec[]): string | undefined {
  const intros = blocks
    .filter((b) => b.type === 'list' && flagsFromLists([b], 'x').length > 0)
    .map((b) => text(b.intro))
    .filter((x): x is string => !!x)
  return intros.length ? intros.join('\n\n') : undefined
}

function preCallContext(root: Rec, audience: WarroomAudience): Record<string, string> | undefined {
  const out: Record<string, string> = {}
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'pre' || b.type !== 'keyvalue' || !visible(b, audience)) continue
    for (const r of parseList(b.rows)) {
      if (!isRecord(r)) continue
      const k = text(r.k)
      const v = text(r.v)
      if (!k || !v) continue
      let key = k
      for (let i = 2; key in out; i++) key = `${k} (${i})` // keep every row, never overwrite
      out[key] = v
    }
  }
  return Object.keys(out).length ? out : undefined
}

function preCallLists(root: Rec, audience: WarroomAudience, h2: RegExp): Rec[] {
  return parseList(rec(root.page).blocks).filter(
    (b): b is Rec => isRecord(b) && b.tab === 'pre' && b.type === 'list' && h2.test(text(b.h2) ?? '') && visible(b, audience),
  )
}

// A lead-in that is already a sentence ("Genuine fan.") runs straight into its body.
function leadIn(label: string | undefined, body: string): string {
  return label ? `${label}${/[.!?]$/.test(label) ? ' ' : ': '}${body}` : body
}

function preCallIntel(root: Rec, audience: WarroomAudience): string[] | undefined {
  const out: string[] = []
  for (const b of preCallLists(root, audience, /intel/i)) {
    for (const item of parseList(b.items)) {
      if (!isRecord(item)) continue
      const { label, body } = splitLens(item.html)
      if (body) out.push(leadIn(label, body))
    }
  }
  return out.length ? out : undefined
}

function preCallQuestions(root: Rec, audience: WarroomAudience): { questions: string[]; landmines: RecoilReportData['riskFlags'] } {
  const questions: string[] = []
  const landmines: RecoilReportData['riskFlags'] = []
  for (const b of preCallLists(root, audience, /question|landmine|moves/i)) {
    for (const item of parseList(b.items)) {
      if (!isRecord(item)) continue
      const { label, body } = splitLens(item.html)
      if (!body) continue
      if (label && /^landmine/i.test(label)) {
        landmines.push({ variant: /unresolved/i.test(label) ? 'warning' : 'caution', label, body })
      } else {
        questions.push(leadIn(label, body))
      }
    }
  }
  return { questions, landmines }
}

// Each "Receipt closed" block is one call scored against its ex-ante; in
// multi-call SSOTs they are appended in call order, which is the walk.
function callWalkFromCloses(root: Rec, audience: WarroomAudience, fallbackDate?: string): RecoilReportData['callWalk'] {
  const steps: RecoilReportData['callWalk'] = []
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'recoil' || b.type !== 'keyvalue' || !visible(b, audience)) continue
    const h2 = text(b.h2)
    if (!h2 || !/^receipt closed/i.test(h2)) continue
    const rows = new Map<string, string>()
    for (const r of parseList(b.rows)) {
      if (!isRecord(r)) continue
      const k = text(r.k)
      const v = text(r.v)
      if (k && v) rows.set(k.toLowerCase(), v)
    }
    const actual = [...rows].find(([k]) => k.startsWith('actual'))?.[1]
    const fork = rows.get('fork hit')
    const body = join([actual, fork ? `Fork hit: ${fork}` : undefined], ' ')
    if (!body) continue
    const rest = h2.replace(/^receipt closed\s*[·:,-]?\s*/i, '')
    const date = rest.match(/\((\d{4}-\d{2}-\d{2})\)/)?.[1] ?? (steps.length === 0 ? fallbackDate : undefined)
    const title = rest.replace(/\s*\(\d{4}-\d{2}-\d{2}\)\s*/, '').trim()
    steps.push({
      label: date ?? `Close ${steps.length + 1}`,
      title: title ? title[0].toUpperCase() + title.slice(1) : 'Receipt closed',
      body,
    })
  }
  return steps
}

// The pre-mortem assumes the engagement is dead and walks the critical path:
// that is a worst-case scenario, and the only scenario the war room records.
function worstFromPremortem(blocks: Rec[]): RecoilReportData['scenarios']['worst'] | undefined {
  const table = blocks.find((b) => b.type === 'table' && /pre-?mortem/i.test(text(b.h2) ?? ''))
  if (!table) return undefined
  const cols = parseList(table.columns).map((c) => text(c) ?? '')
  const col = (re: RegExp) => cols.findIndex((c) => re.test(c))
  const iFail = col(/failure/i)
  const iHandle = col(/handling|gate/i)
  const lines: string[] = []
  let bottleneck: string | undefined
  for (const row of parseList(table.rows)) {
    const cells = parseList(row)
    const node = text(cells[0])?.replace(/\s*·?\s*BOTTLENECK.*$/i, '')
    if (!node) continue
    const fail = iFail >= 0 ? text(cells[iFail]) : undefined
    const handle = iHandle >= 0 ? text(cells[iHandle]) : undefined
    if (!fail && !handle) continue // a bare node number is not a scenario
    if (/BOTTLENECK/i.test(cells.map((c) => (typeof c === 'string' ? c : '')).join(' '))) bottleneck ??= node
    lines.push(join([node, fail ? `dies if: ${fail}` : undefined, handle ? `move: ${handle}` : undefined], ', ') ?? node)
  }
  if (!lines.length) return undefined
  return {
    title: text(table.h2) ?? 'Pre-mortem',
    body: lines.join(' / '),
    ...(bottleneck ? { note: `Bottleneck: ${bottleneck}` } : {}),
  }
}

const RULING_ACCENT: Record<string, string> = { GROUNDED: T.green, INFERENCE: T.gold, STRUCK: T.red }

function forgeClaims(root: Rec, audience: WarroomAudience): RecoilReportData['signalThreads'] {
  const threads: RecoilReportData['signalThreads'] = []
  for (const b of parseList(rec(root.page).blocks)) {
    if (!isRecord(b) || b.tab !== 'forge' || b.type !== 'table' || !/claim/i.test(text(b.h2) ?? '') || !visible(b, audience)) continue
    const cols = parseList(b.columns).map((c) => text(c) ?? '')
    const col = (re: RegExp) => cols.findIndex((c) => re.test(c))
    const iClaim = col(/claim/i)
    const iRuling = col(/ruling/i)
    const iSource = col(/source|why|evidence/i)
    if (iClaim < 0 || iRuling < 0) continue
    for (const row of parseList(b.rows)) {
      const cells = parseList(row)
      const claim = text(cells[iClaim])
      const rulingText = text(cells[iRuling])
      if (!claim || !rulingText) continue
      // Some rulings carry commentary ("INFERENCE: a question about fit ..."): the
      // leading word is the ruling, the rest is kept verbatim as the note.
      const m = rulingText.match(/^([A-Za-z-]+)[\s:;,.-]*([\s\S]*)$/)
      const ruling = (m?.[1] ?? rulingText).toUpperCase()
      const comment = m?.[2]?.replace(/^\(([\s\S]*)\)$/, '$1').trim()
      threads.push({
        label: `Forge \u00b7 ${ruling}`,
        accent: RULING_ACCENT[ruling] ?? T.cyan,
        title: claim,
        body: (iSource >= 0 ? text(cells[iSource]) : undefined) ?? '',
        ...(comment ? { note: comment } : {}),
      })
    }
  }
  return threads
}

const VERDICT_ACCENT: Record<string, string> = { CONFIRMED: T.green, FALSIFIED: T.red, OPEN: T.gold }

export function warroomToRecoilReport(ssot: unknown, opts: { audience?: WarroomAudience } = {}): WarroomRecoilReport {
  const audience = opts.audience ?? 'internal'
  const root = rec(ssot)
  const meta = rec(root.meta)
  const provenance = rec(meta.provenance)
  const opportunity = visible(root.opportunity, audience) ? rec(root.opportunity) : {}
  // Untagged nodes (page.header usually is) count as internal: fail closed.
  const rawHeader = rec(root.page).header
  const header = visible(rawHeader, audience) ? rec(rawHeader) : {}

  const counterpart = text(meta.counterpart)
  const date = text(meta.date)

  const title = text(header.title) ?? (audience === 'internal' ? text(meta.doc_title) ?? counterpart : undefined)
  const yState = text(opportunity.y_state)
  const segments = typeof meta.segments === 'number' ? `${meta.segments} segments` : undefined
  const cover: WarroomRecoilReport['cover'] = {
    // No SSOT field is a call to action; an empty list hides the screen's
    // default buttons, which would otherwise render and link nowhere.
    actions: [],
    ...(title ? { title } : {}),
    ...(text(header.sub) ? { subtitle: text(header.sub) } : {}),
    ...(yState ? { badges: ['War Room', yState] as [string, string] } : {}),
    ...(join([date, segments, text(opportunity.engagement_type)]) ? { meta: join([date, segments, text(opportunity.engagement_type)]) } : {}),
  }

  // The provenance block carries its own audience tag; an internal quote must
  // not cross the air-gap.
  const quote = visible(provenance, audience) ? text(provenance.load_bearing_quote) : undefined
  const loadBearingQuote = quote ? { text: quote, attribution: join([counterpart, date]) ?? '' } : undefined

  const threads: RecoilReportData['signalThreads'] = []
  for (const i of parseList(root.insights)) {
    if (!isRecord(i) || !visible(i, audience)) continue
    const t = text(i.title)
    const body = text(i.text)
    if (!t || !body) continue
    threads.push({ label: text(i.plane) ?? 'Insight', accent: T.cyan, title: t, body })
  }
  for (const b of parseList(root.beliefs)) {
    if (!isRecord(b) || !visible(b, audience)) continue
    const claim = text(b.claim)
    if (!claim) continue
    const verdict = text(b.verdict)
    threads.push({
      label: join([text(b.id), verdict]) ?? 'Belief',
      accent: (verdict && VERDICT_ACCENT[verdict.toUpperCase()]) ?? T.cyan,
      title: claim,
      body: text(b.evidence) ?? '',
      ...(text(b.inference) ? { note: `Inference: ${text(b.inference)}` } : {}),
    })
  }

  // Ex-ante commitments were filed before the call, so they lead; next_steps
  // are post-call and hold the active step.
  threads.push(...forgeClaims(root, audience))

  const protocol: RecoilReportData['protocol'] = exAnteSteps(root, audience)
  let n = 0
  for (const s of parseList(root.next_steps)) {
    if (!isRecord(s) || !visible(s, audience)) continue
    const body = text(s.text)
    if (!body) continue
    const id = String(++n).padStart(2, '0')
    protocol.push({ label: `Next ${id}`, title: text(s.owner) ?? `Step ${id}`, body, ...(n === 1 ? { active: true } : {}) })
  }

  const callWalk = callWalkFromCloses(root, audience, date)
  const trueNorth = preCallTrueNorth(root, audience)
  const context = preCallContext(root, audience)
  const intel = preCallIntel(root, audience)
  const { questions, landmines } = preCallQuestions(root, audience)
  const method = forgeMethod(root, audience)
  const kinematics = beliefKinematics(root, audience)
  const gIntro = listIntro(wargameBlocks(root, audience))
  const wargame = wargameBlocks(root, audience)
  // The recoil tab's post-call watch-list (Kairos, quiet signals, risks).
  const kairos = parseList(rec(root.page).blocks).filter(
    (b): b is Rec => isRecord(b) && b.tab === 'recoil' && b.type === 'list' && /kairos/i.test(text(b.h2) ?? '') && visible(b, audience),
  )
  const riskFlags = [...flagsFromLists(wargame, 'Gauntlet'), ...flagsFromLists(kairos, 'Recoil read'), ...landmines]
  const kIntro = listIntro(kairos)
  const worst = worstFromPremortem(wargame)

  return {
    cover,
    ...(loadBearingQuote ? { loadBearingQuote } : {}),
    ...(callWalk.length ? { callWalk } : {}),
    ...(threads.length ? { signalThreads: threads } : {}),
    ...(protocol.length ? { protocol } : {}),
    ...(riskFlags.length ? { riskFlags } : {}),
    ...(worst ? { scenarios: { worst } } : {}),
    ...(trueNorth ? { preCallTrueNorth: trueNorth } : {}),
    ...(context ? { preCallContext: context } : {}),
    ...(intel ? { preCallIntel: intel } : {}),
    ...(questions.length ? { preCallQuestions: questions } : {}),
    ...(method ? { forgeMethod: method } : {}),
    ...(kinematics ? { beliefKinematics: kinematics } : {}),
    ...(gIntro ? { gauntletIntro: gIntro } : {}),
    ...(kIntro ? { kairosIntro: kIntro } : {}),
  }
}
