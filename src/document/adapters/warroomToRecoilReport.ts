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
//   next_steps[] {owner,text}                                      → protocol[]
//   page.blocks[tab=wargame, type=list] ("The gauntlet") items     → riskFlags[]
//     <strong>LENS:</strong> prefix → label; BAR=warning, Loki=caution, COURT=info, else by dot
//   page.blocks[tab=recoil, type=list, h2~/kairos/] items          → riskFlags[] (after the gauntlet)
//     Risk=warning, Kairos=info, Quiet signal=success; unlabeled items by dot (red/gold/green)
//   page.blocks[tab=wargame, type=table] (ATG pre-mortem) rows     → scenarios.worst
//     ("assume dead": node, failure mode, handling; BOTTLENECK row → note)
//   page.blocks[tab=recoil, type=keyvalue] ("Receipt closed ...")  → callWalk[] (one step per close,
//     authored order; label = date in the h2 else meta.date; title = h2 after "Receipt closed";
//     body = Actual + Fork hit rows; peak never set: the SSOT does not rank closes)
//   (no source)                                                    → cover.actions,
//                                                                    scenarios.best, scenarios.base
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

const ENTITIES: Record<string, string> = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', middot: '·', mdash: '\u2014', ndash: '–', rarr: '→', times: '×' }

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
  return { label: text(m[2]), body: text(m[3]) }
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

  const protocol: RecoilReportData['protocol'] = []
  for (const s of parseList(root.next_steps)) {
    if (!isRecord(s) || !visible(s, audience)) continue
    const body = text(s.text)
    if (!body) continue
    const n = String(protocol.length + 1).padStart(2, '0')
    protocol.push({ label: `Next ${n}`, title: text(s.owner) ?? `Step ${n}`, body, ...(protocol.length === 0 ? { active: true } : {}) })
  }

  const callWalk = callWalkFromCloses(root, audience, date)
  const wargame = wargameBlocks(root, audience)
  // The recoil tab's post-call watch-list (Kairos, quiet signals, risks).
  const kairos = parseList(rec(root.page).blocks).filter(
    (b): b is Rec => isRecord(b) && b.tab === 'recoil' && b.type === 'list' && /kairos/i.test(text(b.h2) ?? '') && visible(b, audience),
  )
  const riskFlags = [...flagsFromLists(wargame, 'Gauntlet'), ...flagsFromLists(kairos, 'Recoil read')]
  const worst = worstFromPremortem(wargame)

  return {
    ...(Object.keys(cover).length ? { cover } : {}),
    ...(loadBearingQuote ? { loadBearingQuote } : {}),
    ...(callWalk.length ? { callWalk } : {}),
    ...(threads.length ? { signalThreads: threads } : {}),
    ...(protocol.length ? { protocol } : {}),
    ...(riskFlags.length ? { riskFlags } : {}),
    ...(worst ? { scenarios: { worst } } : {}),
  }
}
