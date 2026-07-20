'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { QuoteBlock } from '../patterns/QuoteBlock'
import { Timeline } from '../patterns/Timeline'
import { SidelineList } from '../patterns/SidelineList'
import { ScenarioStack } from '../patterns/ScenarioStack'
import { AsideBox, type AsideVariant } from '../patterns/AsideBox'
import { ProcessSteps } from '../patterns/ProcessSteps'

export interface RecoilReportProps { data?: Partial<typeof RECOIL_SAMPLE> }

export const RECOIL_SAMPLE = {
  cover: {
    badges: ['Recoil Report', 'First Round · DS Analyst'],
    title: 'Jon Smyrl × Zach Harris — Figma DS Screen',
    subtitle: 'Post-call forensic analysis. Signal was strong; behavioral pattern repeated twice. NCI: 84.2 — recoverable. One fix owns the outcome.',
    meta: 'ARCS RECOIL · Jun 1, 2026 · 47 min call · Figma People Team',
    actions: ['Open Receipt', 'File to Prep Book'],
  },
}

export function RecoilReport({ data }: RecoilReportProps = {}) {
  const A = T.cyan
  const d = { ...RECOIL_SAMPLE, ...data }
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="r-quote" idx="01" label="Signal Quote" title="The Most Load-Bearing Moment" accent={A}>
        <QuoteBlock accent={A} attribution="Jon Smyrl · Jun 1, 2026 — response to stack walk">
          More succinct than I would have been able to communicate it.
        </QuoteBlock>
      </Sec>

      <Sec id="r-walk" idx="02" label="Call Walk" title="Chronological Signal Map" accent={A}>
        <Timeline accent={A} steps={[
          { label: 'Cold Open', title: 'Late Arrival — Rapport Recovery', body: 'Jon arrived 7 min late. Zach matched with the "plan-in-talker-buffer-time" riff. Clean entry — but self-planted the verbosity flag before Jon had a chance to form the concern.' },
          { label: 'Process Recap', title: 'CONSTRUCTIVE INTERFERENCE — Peak Signal', body: '"More succinct than I would have been able to communicate it." Clearest scoring signal on the call. Concision rewarded explicitly and immediately.', peak: true },
          { label: 'Stack Probe', title: 'Builder-Fit Peak', body: 'Stack named: Claude Code, Warp, Supabase RLS, Prisma, Next.js, Jest, Vercel. "Opinion earns a seat at the table" — Jon mirrored "pick the right tool for the problem."' },
          { label: 'Context-Mgmt', title: 'Builder-Credibility Peak — Call Closer', body: 'Stateful global world file, handoff files, decision-receipt logic applied to self-documentation. Jon: "I gotta drop… really enjoyed this." Offset both recoil zones.', peak: true },
        ]} />
      </Sec>

      <Sec id="r-signal" idx="03" label="Signal Assessment" title="Four-Thread Read" accent={A}>
        <SidelineList items={[
          { label: 'Coherence', accent: T.cyan, title: 'Signal is coherent, packaging is not', body: 'Every capability demonstrated on the call traces to the red thread. The problem: external signal (LinkedIn, positioning) doesn\'t convey this. The genome reads internally but doesn\'t project.' },
          { label: 'Recoil Zone 1', accent: T.red, title: 'Verbosity at the Panel of 2', body: 'Self-seeded the concern before the panel identified it. Jon is warmer and more patient than the next round will be. Fix: lead-with-the-point as a mechanical discipline, not a judgment call.', note: 'Two instances observed. Do not make it three.' },
          { label: 'Recoil Zone 2', accent: T.orange, title: 'Over-ran the runway twice', body: 'When the interviewer kept completing the sentence, the runway was already past. That is the behavioral tell — not verbosity per se, but not reading the signal to stop.' },
          { label: 'Recovery', accent: T.green, title: 'Context-management sequence closed cleanly', body: 'The builder-credibility sequence (stateful files, handoff logic, decision receipts) was the strongest signal of the call and directly offset both recoil zones. Jon dropped warmly.' },
        ]} />
      </Sec>

      <Sec id="r-scenarios" idx="04" label="Outcome Model" title="Three Paths Forward" accent={A}>
        <ScenarioStack scenarios={{
          best: { title: 'Founding Seat — DS Intelligence', body: 'Figma is building a design-intent intelligence function. You define what gets measured across their AI-native surface, which becomes the training signal for the next product. 18 months: influencing the roadmap, not just reporting on it.', note: 'Life-changing scope. The practitioner-analyst compound becomes a category advantage.' },
          base: { title: 'Strong Embedded DS Role', body: 'Real product influence, good comp, interesting technical problem. Developer workflow analytics is genuinely hard. Builder archetype fits. Solid career step.' },
          worst: { title: 'Adobe-Era Backfill', body: '"Own the DS roadmap" is aspirational. You\'re the third analyst supporting one PM\'s OKRs. Embedded means surrounded, not empowered.', note: 'Not a trap if you go in clear-eyed — exit in 18 months after building the portfolio piece.' },
        }} />
      </Sec>

      <Sec id="r-flags" idx="05" label="Risk Flags" title="What to Watch" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AsideBox variant="warning" label="Behavioral Pattern">Verbosity showed twice under open prompts. Panel of 2 will be less warm, harder clock. Lead-with-the-point is the #1 fix. Mechanical — not a judgment call.</AsideBox>
          <AsideBox variant="caution" label="External Signal Gap">LinkedIn headline is a list of competencies, not a statement of the genome. The underlying signal is extraordinary but doesn&apos;t project. Packaging underserves the signal.</AsideBox>
          <AsideBox variant="info" label="Godel Status">EXTERNAL_EVIDENCE_REQUIRED — real confirmation signal comes from recruiter feedback or homework invite. Grade the process, not the result.</AsideBox>
          <AsideBox variant="success" label="Validated">NCI 84.2 — strong and recoverable. The single fix (verbosity) is observable, mechanical, and within full control. No genome problem. No fit problem.</AsideBox>
        </div>
      </Sec>

      <Sec id="r-next" idx="06" label="Protocol" title="Recovery Protocol" accent={A}>
        <ProcessSteps accent={A} steps={[
          { label: 'Fix 01', title: 'Mechanical Verbosity Drill', body: 'Before the Panel of 2: answer every question in ≤2 sentences first. Pause. Offer to expand. Do not expand unless asked. Run this as a drill, not an intention.', active: true },
          { label: 'Fix 02', title: 'Lead With The Point', body: 'Open every answer with the conclusion. Put the mechanism and evidence behind it. Never earn the conclusion — state it first, then prove it.' },
          { label: 'Fix 03', title: 'Runway Read', body: 'When the interviewer interrupts or completes your sentence: that is the signal to stop. Not a politeness cue — a behavioral read. Treat it as a hard stop.' },
          { label: 'Confirm', title: 'Wait for the Signal', body: 'Homework invite or recruiter note within 5 business days is the confirmation signal. Absence of contact at 7 days is the Godel trigger — request a status update.' },
        ]} />
      </Sec>
    </div>
  )
}

// ─── Dynamic variant — real per-call data, not the static Jon Smyrl sample ───
// Produced by the /recoil-report skill from a Granola transcript run through
// both Recoil Protocol passes (runtime/specs/recoil-modes-v1.md). Same six
// canonical sections/patterns as RecoilReport above, just data-driven.

export interface RecoilReportData {
  cover: {
    badges: [string, string]
    title: string
    subtitle: string
    meta: string
    actions: [string, string]
  }
  loadBearingQuote: { text: string; attribution: string }
  callWalk: { label: string; title: string; body: string; peak?: boolean }[]
  signalThreads: { label: string; accent: string; title: string; body: string; note?: string }[]
  scenarios: {
    best: { title: string; body: string; note?: string }
    base: { title: string; body: string; note?: string }
    worst: { title: string; body: string; note?: string }
  }
  riskFlags: { variant: 'warning' | 'caution' | 'info' | 'success'; label: string; body: string }[]
  protocol: { label: string; title: string; body: string; active?: boolean }[]
}

// ─── Raw input normalization ──────────────────────────────────────────────
// The /recoil-report skill (runtime/specs/recoil-modes-v1.md) has produced
// reports in more than one JSON shape over time — the flat CoverBlockProps
// shape above (demo.json, jeben-louisville), and a richer meta+cover shape
// with segment/probability/severity fields (labella, masopust, daniel,
// christopher, precall notes — the shape recoil-modes-v1.md actually
// documents). Rather than migrate historical report files or fork the
// render path, normalize any raw shape onto RecoilReportData here, once,
// so CoverBlock/Timeline/SidelineList/ScenarioStack/AsideBox/ProcessSteps
// (shared with Receipt/Brief/PrepDoc — do not change their prop contracts)
// always receive what they expect.

export type RecoilReportRaw = Record<string, unknown>

const COLOR_ALIAS: Record<string, string> = { green: T.green, gold: T.gold, red: T.red, cyan: T.cyan, orange: T.orange, purple: T.purple }
const SEVERITY_TO_VARIANT: Record<string, AsideVariant> = { HIGH: 'warning', MED: 'caution', LOW: 'info' }

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null
}
function str(v: unknown, fallback = ''): string {
  return typeof v === 'string' ? v : fallback
}
function join(parts: (string | null | undefined | false)[], sep = ' · '): string {
  return parts.filter((p): p is string => typeof p === 'string' && p.length > 0).join(sep)
}

function normalizeCover(raw: RecoilReportRaw): RecoilReportData['cover'] {
  const rc = isRecord(raw.cover) ? raw.cover : {}
  const rm = isRecord(raw.meta) ? raw.meta : {}
  if (typeof rc.title === 'string') {
    // Already flat shape — pass through.
    return {
      badges: (Array.isArray(rc.badges) ? rc.badges : ['Recoil Report', '']) as [string, string],
      title: rc.title,
      subtitle: str(rc.subtitle),
      meta: str(rc.meta),
      actions: (Array.isArray(rc.actions) ? rc.actions : ['Open Receipt', 'File to Prep Book']) as [string, string],
    }
  }
  // Richer shape: meta.callTitle + cover.{yGate,conviction,stability,nci,headline,subline}
  const badges = [str(rc.yGate), str(rc.conviction)].filter(Boolean)
  return {
    badges: (badges.length ? badges : ['Recoil Report', '']) as [string, string],
    title: str(rm.callTitle, 'Recoil Report'),
    subtitle: join([str(rc.headline) || null, str(rc.subline) || null], ' '),
    meta: join([
      'ARCS RECOIL',
      str(rm.callDate) || null,
      str(rm.callTime) || null,
      typeof rm.durationMinutes === 'number' ? `${rm.durationMinutes} min` : null,
      typeof rc.nci === 'number' ? `NCI ${rc.nci}` : null,
      str(rc.stability) || null,
    ]),
    actions: ['Open Receipt', 'File to Prep Book'],
  }
}

function normalizeCallWalk(raw: RecoilReportRaw): RecoilReportData['callWalk'] {
  const list = Array.isArray(raw.callWalk) ? raw.callWalk : []
  return list.filter(isRecord).map((step): RecoilReportData['callWalk'][number] => {
    if (typeof step.title === 'string' && typeof step.body === 'string') {
      return step as unknown as RecoilReportData['callWalk'][number] // already flat shape
    }
    const divergence = str(step.divergenceFlag)
    return {
      label: join([str(step.time) || null, str(step.direction) || null]),
      title: str(step.label, `Segment ${step.segment ?? ''}`.trim()),
      body: join([str(step.summary) || null, divergence ? `Divergence: ${divergence}` : null], '\n\n'),
      peak: divergence.startsWith('HIGH'),
    }
  })
}

function normalizeSignalThreads(raw: RecoilReportRaw): RecoilReportData['signalThreads'] {
  const list = Array.isArray(raw.signalThreads) ? raw.signalThreads : []
  return list.filter(isRecord).map((item): RecoilReportData['signalThreads'][number] => {
    if (typeof item.title === 'string' && typeof item.body === 'string') {
      return item as unknown as RecoilReportData['signalThreads'][number] // already flat shape
    }
    const color = str(item.color)
    return {
      label: str(item.strength),
      title: str(item.label),
      body: str(item.description),
      accent: COLOR_ALIAS[color] ?? (color || T.cyan),
    }
  })
}

function normalizeScenarios(raw: RecoilReportRaw): RecoilReportData['scenarios'] {
  const s = raw.scenarios
  if (isRecord(s) && isRecord(s.best) && isRecord(s.base) && isRecord(s.worst)) {
    return s as unknown as RecoilReportData['scenarios'] // already flat shape
  }
  const list = Array.isArray(s) ? s.filter(isRecord) : []
  const empty: RecoilReportData['scenarios']['best'] = { title: '—', body: 'No scenario data.' }
  if (list.length === 0) return { best: empty, base: empty, worst: empty }
  // Preserve authored order (already probability-ranked, highest first, per
  // recoil-modes-v1.md scenario generation) into the fixed 3-slot tab UI.
  // Any 4th+ scenario is folded into the worst slot's note as a footnote —
  // ScenarioStack (shared with Receipt/Brief/PrepDoc) only supports 3 tabs.
  const toScenario = (item: Record<string, unknown> | undefined): RecoilReportData['scenarios']['best'] => {
    if (!item) return empty
    const prob = typeof item.probability === 'number' ? `${item.probability}%` : null
    return {
      title: str(item.label, str(item.id)),
      body: join([str(item.description, str(item.conditions)) || null, str(item.trigger) ? `Trigger: ${item.trigger}` : null], '\n\n'),
      note: join([prob ? `Probability: ${prob}` : null, str(item.watch) || null], ' — ') || undefined,
    }
  }
  const extra = list.slice(3).map((item) => `${str(item.label, str(item.id))}${typeof item.probability === 'number' ? ` (${item.probability}%)` : ''}`)
  const worst = toScenario(list[2])
  return {
    best: toScenario(list[0]),
    base: toScenario(list[1]),
    worst: extra.length ? { ...worst, note: join([worst.note, `Also: ${extra.join('; ')}`], ' — ') } : worst,
  }
}

function normalizeRiskFlags(raw: RecoilReportRaw): RecoilReportData['riskFlags'] {
  const list = Array.isArray(raw.riskFlags) ? raw.riskFlags : []
  return list.filter(isRecord).map((f) => {
    if (typeof f.variant === 'string' && typeof f.body === 'string') {
      return f as unknown as RecoilReportData['riskFlags'][number] // already flat shape
    }
    return {
      variant: SEVERITY_TO_VARIANT[str(f.severity)] ?? 'info',
      label: str(f.label),
      body: join([str(f.description) || null, str(f.action) ? `Action: ${f.action}` : null], '\n\n'),
    }
  })
}

function normalizeProtocol(raw: RecoilReportRaw): RecoilReportData['protocol'] {
  const p = raw.protocol
  if (Array.isArray(p)) return p as RecoilReportData['protocol'] // already flat shape
  if (!isRecord(p)) return []
  const steps: RecoilReportData['protocol'] = []
  const passes = Array.isArray(p.passes) ? p.passes.filter(isRecord) : []
  for (const pass of passes) {
    steps.push({
      label: str(pass.direction, str(pass.name)),
      title: str(pass.name),
      body: str(pass.keyFinding, str(pass.prePrepNote)),
    })
  }
  const actions = Array.isArray(p.immediateActions) ? p.immediateActions : []
  actions.forEach((action, i) => {
    if (typeof action !== 'string') return
    steps.push({ label: 'NEXT ACTION', title: `Action ${i + 1}`, body: action, active: i === 0 })
  })
  return steps
}

function normalizeRecoilReport(raw: RecoilReportRaw): RecoilReportData {
  return {
    cover: normalizeCover(raw),
    loadBearingQuote: isRecord(raw.loadBearingQuote)
      ? { text: str(raw.loadBearingQuote.text), attribution: str(raw.loadBearingQuote.attribution) }
      : { text: '', attribution: '' },
    callWalk: normalizeCallWalk(raw),
    signalThreads: normalizeSignalThreads(raw),
    scenarios: normalizeScenarios(raw),
    riskFlags: normalizeRiskFlags(raw),
    protocol: normalizeProtocol(raw),
  }
}

// ─── Deeper Strata — archaeology of the full ledger ───────────────────────
// The six canonical sections render the briefing surface; everything else in
// a report file (recapitulation, diamondCutPass, nonverbalOverlay, readOrder,
// statedVsRevealed, meta, …) is ledger strata that previously never reached
// the page. This section excavates them in AUTHORITY order — the anachronistic
// tread mandated by readOrder: current truth first, provenance beneath,
// substrate last. Depth maps onto the WORLD.md render scale: the top stratum
// renders SHARP (superionic — structure + flow), deeper strata degrade toward
// GRAIN, because depth is provenance, not truth. Amber preserves; it does not
// update.

const STRATA_CANONICAL = new Set([
  'reportId', 'notice', 'cover', 'loadBearingQuote', 'callWalk',
  'signalThreads', 'scenarios', 'riskFlags', 'protocol', 'receiptLifecycle',
])
const STRATA_AUTHORITY = ['recapitulation', 'diamondCutPass', 'nonverbalOverlay', 'statedVsRevealed', 'readOrder']
const STRATA_SUBSTRATE = 'meta'
const AMBER = ['#FFD700', '#EAC14A', '#D0A93C', '#B69130', '#9C7A26', '#82651E']
const STRATA_FIDELITY = [
  { opacity: 1, weight: 500, tracking: '0em' },       // S0 — superionic, current truth
  { opacity: 0.95, weight: 400, tracking: '0.002em' },
  { opacity: 0.88, weight: 400, tracking: '0.006em' },
  { opacity: 0.82, weight: 400, tracking: '0.01em' },
  { opacity: 0.76, weight: 300, tracking: '0.015em' },
  { opacity: 0.7, weight: 300, tracking: '0.02em' },  // deepest — grain
]

function strataLabel(k: string): string {
  return k.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/[_-]+/g, ' ').trim().toUpperCase()
}

function StrataValue({ v, depth, amber }: { v: unknown; depth: number; amber: string }) {
  if (v == null) return null
  if (typeof v !== 'object') {
    return (
      <p style={{ fontFamily: T.sans, fontSize: 12.5, color: T.fg3, lineHeight: 1.7, margin: '3px 0', whiteSpace: 'pre-wrap' }}>
        {String(v)}
      </p>
    )
  }
  if (Array.isArray(v)) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {v.map((item, i) => (
          <div key={i} style={{ borderLeft: `1px solid ${amber}30`, paddingLeft: 10 }}>
            <StrataValue v={item} depth={depth + 1} amber={amber} />
          </div>
        ))}
      </div>
    )
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {Object.entries(v as Record<string, unknown>).map(([k, item]) => (
        <div key={k}>
          <div style={{ fontFamily: T.mono, fontSize: 9, fontWeight: 700, color: `${amber}CC`, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 3 }}>
            {strataLabel(k)}
          </div>
          <div style={{ paddingLeft: depth < 3 ? 10 : 6, borderLeft: `1px solid ${amber}22` }}>
            <StrataValue v={item} depth={depth + 1} amber={amber} />
          </div>
        </div>
      ))}
    </div>
  )
}

function DeepStrata({ raw }: { raw: RecoilReportRaw }) {
  const [open, setOpen] = React.useState(0) // FOCUS mode: only the top stratum open; -1 = all closed
  const strata: { name: string; value: unknown; tag: string }[] = []
  for (const k of STRATA_AUTHORITY) {
    if (raw[k] != null) strata.push({ name: k, value: raw[k], tag: k === 'recapitulation' ? 'CURRENT TRUTH' : 'PROVENANCE' })
  }
  for (const k of Object.keys(raw)) {
    if (!STRATA_CANONICAL.has(k) && k !== STRATA_SUBSTRATE && !STRATA_AUTHORITY.includes(k) && raw[k] != null) {
      strata.push({ name: k, value: raw[k], tag: 'PROVENANCE' })
    }
  }
  if (raw[STRATA_SUBSTRATE] != null) strata.push({ name: STRATA_SUBSTRATE, value: raw[STRATA_SUBSTRATE], tag: 'SUBSTRATE' })
  if (strata.length === 0) return null

  return (
    <Sec id="r-strata" idx="07" label="Deeper Strata" title="Archaeology of the Ledger" accent={T.gold}>
      <div style={{ marginBottom: 14 }}>
        <AsideBox variant="info" label="Dig Protocol">
          Anachronistic tread — the top stratum is current truth; deeper strata are preserved provenance, superseded
          beliefs left in place and marked, never overwritten. Depth renders at earned fidelity: sharp at the surface,
          grain at the substrate. Amber preserves; it does not update.
        </AsideBox>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {strata.map((s, i) => {
          const amber = AMBER[Math.min(i, AMBER.length - 1)]
          const fid = STRATA_FIDELITY[Math.min(i, STRATA_FIDELITY.length - 1)]
          const crystal = s.tag === 'CURRENT TRUTH'
          const isOpen = open === i
          const bytes = JSON.stringify(s.value).length
          return (
            <div key={s.name} style={{
              border: crystal ? '1px solid rgba(0,240,255,0.30)' : `1px solid ${amber}30`,
              borderRadius: 8,
              background: crystal ? 'rgba(0,240,255,0.02)' : `${amber}08`,
              boxShadow: crystal ? '0 0 20px rgba(0,240,255,0.07), inset 0 0 30px rgba(255,215,0,0.03)' : 'none',
              opacity: fid.opacity,
            }}>
              <button
                onClick={() => setOpen(isOpen ? -1 : i)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 10, width: '100%', textAlign: 'left',
                  padding: '10px 14px', background: 'transparent', border: 'none', cursor: 'pointer',
                }}
              >
                <span style={{
                  fontFamily: T.mono, fontSize: 9, fontWeight: 700, letterSpacing: '0.1em',
                  color: crystal ? T.cyan : amber, border: `1px solid ${crystal ? 'rgba(0,240,255,0.35)' : `${amber}40`}`,
                  borderRadius: 4, padding: '2px 6px', flexShrink: 0,
                }}>S{i}</span>
                <span style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', color: crystal ? T.fg1 : T.fg2, textTransform: 'uppercase' }}>
                  {strataLabel(s.name)}
                </span>
                <span style={{ fontFamily: T.mono, fontSize: 9, color: crystal ? T.cyan : `${amber}AA`, letterSpacing: '0.12em', flexShrink: 0 }}>
                  {s.tag}
                </span>
                <span style={{ flex: 1 }} />
                <span style={{ fontFamily: T.mono, fontSize: 9, color: T.fg4, flexShrink: 0 }}>
                  {(bytes / 1024).toFixed(1)} KB
                </span>
                <span style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4, flexShrink: 0 }}>{isOpen ? '▾' : '▸'}</span>
              </button>
              {isOpen && (
                <div style={{
                  padding: '4px 14px 14px', borderTop: `1px solid ${crystal ? 'rgba(0,240,255,0.15)' : `${amber}1E`}`,
                  fontWeight: fid.weight, letterSpacing: fid.tracking,
                }}>
                  <StrataValue v={s.value} depth={0} amber={crystal ? '#7FE8F0' : amber} />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </Sec>
  )
}

// ─── Receipt lifecycle — the meeting object (ex-ante open → ex-post close) ──
// Prototype (2026-07-20) of product surface #2's core object: a meeting is an
// ARCS receipt that OPENS on a hypothesis before contact and CLOSES on the
// revealed reality, where the stated-vs-revealed diff IS the belief update.
// Renders only when a report carries a `receiptLifecycle` key — existing
// reports have none, so this is a zero-regression addition. When state=OPEN
// the revealed/belief cells render PENDING; they're filled in post-call and
// the state flips to CLOSED. See memory: recoil-as-second-product-surface.
interface LifecycleDiffRow { expecting: string; revealed?: string | null; beliefUpdate?: string | null }
interface Lifecycle {
  state: 'OPEN' | 'CLOSED'
  opened?: string
  closed?: string
  hypothesis: string
  statedPreference: string
  agenda?: string[]
  diff: LifecycleDiffRow[]
  closeNote?: string
}

function readLifecycle(raw: RecoilReportRaw): Lifecycle | null {
  const lc = raw.receiptLifecycle
  if (!isRecord(lc)) return null
  const diff = (Array.isArray(lc.diff) ? lc.diff : []).filter(isRecord).map((r) => ({
    expecting: str(r.expecting),
    revealed: typeof r.revealed === 'string' ? r.revealed : null,
    beliefUpdate: typeof r.beliefUpdate === 'string' ? r.beliefUpdate : null,
  }))
  return {
    state: lc.state === 'CLOSED' ? 'CLOSED' : 'OPEN',
    opened: str(lc.opened) || undefined,
    closed: str(lc.closed) || undefined,
    hypothesis: str(lc.hypothesis),
    statedPreference: str(lc.statedPreference),
    agenda: (Array.isArray(lc.agenda) ? lc.agenda.filter((a): a is string => typeof a === 'string') : undefined),
    diff,
    closeNote: str(lc.closeNote) || undefined,
  }
}

function ReceiptLifecycle({ lc }: { lc: Lifecycle }) {
  const open = lc.state === 'OPEN'
  const stateColor = open ? T.cyan : T.green
  const label = (t: string) => (
    <div style={{ fontFamily: T.mono, fontSize: 9, fontWeight: 700, color: T.fg4, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 4 }}>{t}</div>
  )
  return (
    <Sec id="r-lifecycle" idx="00" label="Receipt Lifecycle" title="Meeting Object — Ex-Ante Open / Ex-Post Close" accent={stateColor}>
      {/* state chip + timestamps */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
        <span style={{ fontFamily: T.mono, fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', color: stateColor, border: `1px solid ${stateColor}55`, borderRadius: 4, padding: '3px 8px' }}>
          RECEIPT · {lc.state}
        </span>
        {lc.opened && <span style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4 }}>opened {lc.opened}</span>}
        {lc.closed && <span style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4 }}>closed {lc.closed}</span>}
      </div>

      {/* ex-ante — the frozen bearing */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 16 }}>
        <div style={{ borderLeft: `2px solid ${T.cyan}`, paddingLeft: 12 }}>
          {label('Hypothesis · ex-ante bearing')}
          <p style={{ fontFamily: T.sans, fontSize: 13.5, color: T.fg1, lineHeight: 1.65, margin: 0, whiteSpace: 'pre-wrap' }}>{lc.hypothesis}</p>
        </div>
        <div style={{ borderLeft: `2px solid ${T.gold}`, paddingLeft: 12 }}>
          {label('Stated preference · desired outcome')}
          <p style={{ fontFamily: T.sans, fontSize: 13.5, color: T.fg1, lineHeight: 1.65, margin: 0, whiteSpace: 'pre-wrap' }}>{lc.statedPreference}</p>
        </div>
        {lc.agenda && lc.agenda.length > 0 && (
          <div style={{ borderLeft: `2px solid ${T.steel}`, paddingLeft: 12 }}>
            {label('Agenda · what gets tested in the room')}
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              {lc.agenda.map((a, i) => (
                <li key={i} style={{ fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.6 }}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* the diff — stated/expected vs revealed = belief update */}
      {label('Stated-vs-revealed diff · the close')}
      <div style={{ border: `1px solid ${T.border}`, borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', background: T.shell, borderBottom: `1px solid ${T.border}` }}>
          {['Expecting to see', 'Revealed', 'Δ Belief'].map((h) => (
            <div key={h} style={{ fontFamily: T.mono, fontSize: 9.5, fontWeight: 700, letterSpacing: '0.1em', color: T.fg3, textTransform: 'uppercase', padding: '8px 12px' }}>{h}</div>
          ))}
        </div>
        {lc.diff.map((row, i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', borderBottom: i < lc.diff.length - 1 ? `1px solid ${T.border}` : 'none' }}>
            <div style={{ fontFamily: T.sans, fontSize: 12.5, color: T.fg1, lineHeight: 1.55, padding: '10px 12px', borderRight: `1px solid ${T.border}` }}>{row.expecting}</div>
            <div style={{ fontFamily: T.sans, fontSize: 12.5, lineHeight: 1.55, padding: '10px 12px', borderRight: `1px solid ${T.border}`, color: row.revealed ? T.fg1 : T.fg4, fontStyle: row.revealed ? 'normal' : 'italic' }}>
              {row.revealed ?? 'PENDING · fill post-call'}
            </div>
            <div style={{ fontFamily: T.sans, fontSize: 12.5, lineHeight: 1.55, padding: '10px 12px', color: row.beliefUpdate ? T.green : T.fg4, fontStyle: row.beliefUpdate ? 'normal' : 'italic' }}>
              {row.beliefUpdate ?? '—'}
            </div>
          </div>
        ))}
      </div>

      {lc.closeNote && (
        <div style={{ marginTop: 14 }}>
          <AsideBox variant={open ? 'info' : 'success'} label={open ? 'To close' : 'Closed'}>{lc.closeNote}</AsideBox>
        </div>
      )}
    </Sec>
  )
}

export function RecoilReportFromData({ data: raw }: { data: RecoilReportRaw }) {
  const A = T.cyan
  const d = normalizeRecoilReport(raw)
  const lifecycle = readLifecycle(raw)
  const notice = str(raw.notice)
  const significance = isRecord(raw.loadBearingQuote) ? str(raw.loadBearingQuote.significance) : ''
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      {notice && (
        <div style={{ margin: '16px 0' }}>
          <AsideBox variant="warning" label="Notice">{notice}</AsideBox>
        </div>
      )}

      {lifecycle && <ReceiptLifecycle lc={lifecycle} />}

      <Sec id="r-quote" idx="01" label="Signal Quote" title="The Most Load-Bearing Moment" accent={A}>
        <QuoteBlock accent={A} attribution={d.loadBearingQuote.attribution}>
          {d.loadBearingQuote.text}
        </QuoteBlock>
        {significance && (
          <p style={{ fontFamily: T.sans, fontSize: 13, color: T.fg3, lineHeight: 1.65, marginTop: 10 }}>{significance}</p>
        )}
      </Sec>

      <Sec id="r-walk" idx="02" label="Call Walk" title="Chronological Signal Map" accent={A}>
        <Timeline accent={A} steps={d.callWalk} />
      </Sec>

      <Sec id="r-signal" idx="03" label="Signal Assessment" title="Four-Thread Read" accent={A}>
        <SidelineList items={d.signalThreads} />
      </Sec>

      <Sec id="r-scenarios" idx="04" label="Outcome Model" title="Three Paths Forward" accent={A}>
        <ScenarioStack scenarios={d.scenarios} />
      </Sec>

      <Sec id="r-flags" idx="05" label="Risk Flags" title="What to Watch" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {d.riskFlags.map((f, i) => (
            <AsideBox key={i} variant={f.variant} label={f.label}>{f.body}</AsideBox>
          ))}
        </div>
      </Sec>

      <Sec id="r-next" idx="06" label="Protocol" title="Recovery Protocol" accent={A}>
        <ProcessSteps accent={A} steps={d.protocol} />
      </Sec>

      <DeepStrata raw={raw} />
    </div>
  )
}
