'use client'
import React from 'react'
import { font, text, signal, border, getWeather, resStyle, nciColor, doorLabel, tribColor } from '@/ui/tokens'
import { FatedGrid } from '@/molecules/FatedGrid'
import { TerrainPaths } from '@/molecules/TerrainPaths'
import { AHMED_ORDER, SUBJECT_LABEL, OPEN_QUESTION_PROMPT, horizonLabel } from '@/lib/vocabulary'
import type { FatedDecomposition, TerrainPath, Tributary } from '@/lib/mockCompass'

// The Ahmed order, one layout for receipt and brief:
// Decision -> True North -> Reasons -> Open questions -> Next moves -> Evidence (folded).
// Labels come from src/lib/vocabulary.ts only. Spec: runtime/specs/ahmed-order-vocabulary.md
//
// Earned fidelity (WORLD.md): the order is structure, never resolution. True North
// and its reasons render at the receipt's own resolution; a fogged receipt is never
// sharpened to fit the layout.

export interface AhmedOrderData {
  decision: string
  trueNorth: string
  yState: string
  renderResolution?: string | null
  mode?: string | null
  doorClass?: string | null
  stakes?: string | null
  horizon?: string | null
  reasons: string[]
  questions: Tributary[]
  paths: TerrainPath[]
  fated?: Partial<FatedDecomposition> | null
  courtVerdict?: string | null
  nciScore?: number | null
  coherencePct?: number | null
  macroTags?: string[]
  version?: number | null
  createdAt?: string | null
}

// WORLD.md Y state -> render resolution, used only when a receipt never stored one.
const Y_TO_RESOLUTION: Record<string, string> = {
  GREEN: 'SHARP', LOCKED: 'SHARP', YELLOW: 'DEGRADED', FORK: 'DEGRADED',
  SCRATCH: 'GRAIN', DELTA: 'GRAIN', DRIFT: 'GRAIN', RED: 'GRAIN', PARADOX: 'MOIRE',
}
export const resolutionFor = (yState: string, stored?: string | null): string =>
  (stored && resStyle[stored] ? stored : Y_TO_RESOLUTION[yState]) ?? 'GRAIN'

const MEASURE = 680 // px: the one body measure for reading text in this layout

const sectionGap: React.CSSProperties = { marginTop: '2.75rem' }

function SlotHeading({ children, color = text.muted, id }: { children: React.ReactNode; color?: string; id?: string }) {
  return (
    <h2 id={id} style={{ fontFamily: font.mono, ...font.tier.t6, textTransform: 'uppercase', color, margin: '0 0 0.9rem' }}>
      {children}
    </h2>
  )
}

const titleCase = (s: string) => s.charAt(0) + s.slice(1).toLowerCase()

export function AhmedOrder({ data, onQuestion, after }: {
  data: AhmedOrderData
  /** Follow an open question into a new compass run. */
  onQuestion?: (prompt: string) => void
  /** Slot for surface-specific content between Next moves and Evidence. */
  after?: React.ReactNode
}) {
  const res = resolutionFor(data.yState, data.renderResolution)
  const rs = resStyle[res]
  const weather = getWeather(data.yState)
  const horizon = horizonLabel(data.horizon)
  const fated = data.fated && Object.values(data.fated).some((v) => typeof v === 'string' && v.trim()) ? data.fated : null
  const facts: [string, string][] = [
    ['Mode', data.mode ? titleCase(data.mode) : ''],
    ['Door', data.doorClass ? titleCase(doorLabel(data.doorClass)) : ''],
    ['Stakes', data.stakes ? titleCase(data.stakes) : ''],
    ['Horizon', horizon ?? ''],
  ].filter(([, v]) => v) as [string, string][]

  return (
    <div>
      {/* Subject: the decision (a call, a bet or a choice) */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ fontFamily: font.mono, ...font.tier.t2, textTransform: 'uppercase', color: text.dimmed, marginBottom: '0.4rem' }}>{SUBJECT_LABEL}</div>
        <p style={{ fontFamily: font.sans, fontSize: '0.95rem', color: text.secondary, lineHeight: 1.6, margin: 0, textWrap: 'pretty' }}>{data.decision}</p>
      </div>

      {/* 1 · True North, at the resolution it earned */}
      <section aria-labelledby="slot-verdict">
        <SlotHeading id="slot-verdict" color={signal.cyan}>{AHMED_ORDER.verdict.label}</SlotHeading>
        <p style={{ fontFamily: font.sans, fontSize: 'clamp(1.15rem, 2.6vw, 1.55rem)', lineHeight: 1.35, color: text.primary, margin: 0, textWrap: 'pretty', ...rs, fontWeight: Math.max(Number(rs.fontWeight ?? 400), 400) + 100 }}>
          {data.trueNorth}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '0.4rem 1.25rem', marginTop: '0.9rem' }}>
          <span style={{ fontFamily: font.mono, ...font.tier.t4, textTransform: 'uppercase', color: weather.color, whiteSpace: 'nowrap' }}>
            {weather.icon} {weather.label} · {res === 'SHARP' ? 'sharp' : `rendered ${res.toLowerCase()}`}
          </span>
          {facts.map(([k, v]) => (
            <span key={k} style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.muted, whiteSpace: 'nowrap' }}>
              {k} <span style={{ color: text.secondary }}>{v}</span>
            </span>
          ))}
        </div>
      </section>

      {/* 2 · Reasons */}
      <section aria-labelledby="slot-reasons" style={sectionGap}>
        <SlotHeading id="slot-reasons">{AHMED_ORDER.reasons.label}</SlotHeading>
        {data.reasons.length > 0 ? (
          <ol style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.8rem', maxWidth: MEASURE, opacity: rs.opacity }}>
            {data.reasons.map((r, i) => (
              <li key={i} style={{ display: 'grid', gridTemplateColumns: '1.75rem 1fr', alignItems: 'baseline' }}>
                <span style={{ fontFamily: font.mono, ...font.tier.t4, color: signal.cyan, fontVariantNumeric: 'tabular-nums' }}>{String(i + 1).padStart(2, '0')}</span>
                <span style={{ fontFamily: font.sans, fontSize: '0.925rem', color: text.secondary, lineHeight: 1.6, textWrap: 'pretty' }}>{r}</span>
              </li>
            ))}
          </ol>
        ) : <Empty>No reasons were recorded with this receipt.</Empty>}
      </section>

      {/* 3 · Open questions: asked by the compass, answered only by the one deciding */}
      <section aria-labelledby="slot-questions" style={sectionGap}>
        <SlotHeading id="slot-questions">{AHMED_ORDER.questions.label}</SlotHeading>
        {data.questions.length > 0 ? (
          <>
            <ol style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1.1rem', maxWidth: MEASURE }}>
              {data.questions.map((q, i) => (
                <li key={i} style={{ borderTop: `1px solid ${border.subtle}`, paddingTop: '0.85rem' }}>
                  <div style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: tribColor(q.type), marginBottom: '0.35rem' }}>{q.label}</div>
                  <p style={{ fontFamily: font.sans, fontSize: '0.925rem', color: text.secondary, lineHeight: 1.6, margin: 0, textWrap: 'pretty' }}>{q.prompt}</p>
                  {onQuestion && (
                    <button type="button" onClick={() => onQuestion(q.prompt)} style={{ marginTop: '0.55rem', background: 'none', border: 'none', padding: '0.25rem 0', cursor: 'pointer', fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: signal.cyan, textUnderlineOffset: 3 }}>
                      Run this question →
                    </button>
                  )}
                </li>
              ))}
            </ol>
            <p style={{ fontFamily: "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif", fontStyle: 'italic', fontSize: '1rem', color: text.secondary, margin: '1.25rem 0 0', maxWidth: MEASURE }}>
              {OPEN_QUESTION_PROMPT}
            </p>
          </>
        ) : <Empty>No open questions were recorded with this receipt.</Empty>}
      </section>

      {/* 4 · Next moves */}
      <section aria-labelledby="slot-tasks" style={sectionGap}>
        <SlotHeading id="slot-tasks">{AHMED_ORDER.tasks.label}{horizon ? ` · ${horizon}` : ''}</SlotHeading>
        {data.paths.length > 0 ? <div style={{ maxWidth: MEASURE }}><TerrainPaths paths={data.paths} bare /></div> : <Empty>No moves were recorded with this receipt.</Empty>}
      </section>

      {after}

      {/* 5 · Evidence, behind the fold */}
      <details style={{ ...sectionGap, borderTop: `1px solid ${border.subtle}`, paddingTop: '1rem' }}>
        <summary style={{ cursor: 'pointer', fontFamily: font.mono, ...font.tier.t6, textTransform: 'uppercase', color: text.muted }}>
          {AHMED_ORDER.evidence.label}
        </summary>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '1.25rem' }}>
          <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.9rem 1.5rem', margin: 0 }}>
            {data.nciScore != null && <Stat k="NCI (decision coherence)" v={`${data.nciScore} / 100`} color={nciColor(data.nciScore)} />}
            {data.coherencePct != null && <Stat k="Question coherence" v={`${data.coherencePct}%`} />}
            {data.macroTags && data.macroTags.length > 0 && <Stat k="Checks run" v={data.macroTags.join(' · ')} />}
            {data.version != null && <Stat k="Lineage depth" v={String(data.version)} />}
            {data.createdAt && <Stat k="Recorded" v={new Date(data.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })} />}
          </dl>
          {data.courtVerdict && (
            <div>
              <div style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: signal.gold, marginBottom: '0.35rem' }}>Court verdict</div>
              <p style={{ fontFamily: font.sans, fontSize: '0.9rem', color: text.secondary, lineHeight: 1.6, margin: 0, maxWidth: MEASURE }}>{data.courtVerdict}</p>
            </div>
          )}
          {fated && <FatedGrid fated={fated} />}
        </div>
      </details>
    </div>
  )
}

function Stat({ k, v, color = text.primary }: { k: string; v: string; color?: string }) {
  return (
    <div style={{ minWidth: 0 }}>
      <dt style={{ fontFamily: font.mono, ...font.tier.t2, textTransform: 'uppercase', color: text.dimmed, marginBottom: '0.25rem' }}>{k}</dt>
      <dd style={{ fontFamily: font.mono, ...font.tier.t5, color, margin: 0, fontVariantNumeric: 'tabular-nums' }}>{v}</dd>
    </div>
  )
}

function Empty({ children }: { children: React.ReactNode }) {
  return <p style={{ fontFamily: font.sans, fontSize: '0.875rem', color: text.muted, margin: 0 }}>{children}</p>
}
