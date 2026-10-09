'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec, Pill } from '../primitives'
import { AsideBox } from '../patterns/AsideBox'
import { derivatives, kinematicsNote } from '../kinematics'

// ─── War-room render path ─────────────────────────────────────────────────
// The 6-tab war-room SSOTs (recoil-new / recoil-prep / recoil-close; e.g.
// runtime/recoil/generated/2026-09-14-schriner.json) carry meta / opportunity
// / beliefs / kinematic_series / insights / next_steps / page.blocks — not the
// cover / callWalk / signalThreads shape the 6-section report expects. Forcing
// them through an adapter would be lossy (beliefs are not a call walk), so
// RecoilReportFromData branches here instead. Block renderers mirror
// scripts/recoil_brief.py `_render_block` (the canonical HTML renderer behind
// /warroom/[slug]); keep the two in step when a block type is added.
//
// Internal only: /recoil is admin-gated (src/lib/admin.ts), so every audience
// renders. meta.gate (passcodes) is never rendered.

type Raw = Record<string, unknown>
const isRec = (v: unknown): v is Raw => typeof v === 'object' && v !== null && !Array.isArray(v)
const s = (v: unknown) => (typeof v === 'string' ? v : v == null ? '' : String(v))
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : [])

export function isWarRoomShape(raw: Raw): boolean {
  return isRec(raw.page) && Array.isArray(raw.page.blocks)
}

/** Top-level keys this view renders; DeepStrata skips them. meta stays as substrate (gate stripped). */
export const WARROOM_RENDERED_KEYS = ['page', 'beliefs', 'kinematic_series', 'insights', 'next_steps', 'opportunity']

// Block strings are authored HTML fragments (<strong>, <br>, &#183; entities)
// from committed repo files. Allowlist the inline tags they use; drop every
// other tag and every attribute (href kept on <a>, http(s) only).
const ALLOWED = new Set(['strong', 'b', 'em', 'i', 'br', 'code', 'a', 'span', 'u', 'sub', 'sup'])
function clean(html: string): string {
  return html
    .replace(/<(script|style|iframe|object)[\s\S]*?<\/\1\s*>/gi, '')
    .replace(/<\/?([a-zA-Z0-9]+)([^>]*)>/g, (m, tag: string, attrs: string) => {
      const t = tag.toLowerCase()
      if (!ALLOWED.has(t)) return ''
      if (m.startsWith('</')) return `</${t}>`
      if (t === 'a') {
        const href = /href\s*=\s*"(https?:\/\/[^"]*)"/i.exec(attrs)?.[1]
        return href ? `<a href="${href}" target="_blank" rel="noopener noreferrer" style="color:${T.cyan}">` : '<a>'
      }
      return `<${t}>`
    })
}
function H({ html, style }: { html: unknown; style?: React.CSSProperties }) {
  return <span style={style} dangerouslySetInnerHTML={{ __html: clean(s(html)) }} />
}

const P: React.CSSProperties = { fontFamily: T.sans, fontSize: 13.5, color: T.fg2, lineHeight: 1.7, margin: '0 0 10px' }
const H2: React.CSSProperties = { fontFamily: T.sans, fontSize: 15, fontWeight: 600, color: T.fg1, margin: '0 0 10px' }
const card = (accent?: string): React.CSSProperties => ({
  border: `1px solid ${accent ? `${accent}55` : T.border}`, borderRadius: 8, background: T.surface, padding: '16px 18px',
})
const TH: React.CSSProperties = { fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', color: T.fg3, textTransform: 'uppercase', textAlign: 'left', padding: '8px 10px', borderBottom: `1px solid ${T.border}`, verticalAlign: 'bottom' }
const TD: React.CSSProperties = { fontFamily: T.sans, fontSize: 12.5, color: T.fg1, lineHeight: 1.55, padding: '9px 10px', borderBottom: `1px solid ${T.border}`, verticalAlign: 'top' }
const DOT: Record<string, string> = { g: T.green, c: T.cyan, r: T.red, y: T.gold, o: T.orange }

function Table({ head, rows }: { head: unknown[]; rows: unknown[][] }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead><tr>{head.map((h, i) => <th key={i} style={TH}><H html={h} /></th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j} style={TD}><H html={c} /></td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

function Card({ h2, accent, children }: { h2?: unknown; accent?: string; children: React.ReactNode }) {
  return (
    <div style={card(accent)}>
      {s(h2) && <h3 style={{ ...H2, color: accent ?? T.fg1 }}><H html={h2} /></h3>}
      {children}
    </div>
  )
}
const Intro = ({ v }: { v: unknown }) => (s(v) ? <p style={P}><H html={v} /></p> : null)

// D1-D3 by central difference — same as recoil_brief.py `_grad` (np.gradient, edge_order=1).

interface Series { key: string; label: string; color: string; points: number[]; quote: string }
function readSeries(raw: Raw): { dt: number; series: Series[] } {
  const ks = isRec(raw.kinematic_series) ? raw.kinematic_series : {}
  const dt = typeof ks.dt === 'number' && ks.dt > 0 ? ks.dt : 1
  const series = arr(ks.series).filter(isRec).map((x) => ({
    key: s(x.key), label: s(x.label), color: s(x.color) || T.cyan,
    points: arr(x.points).map(Number).filter((n) => Number.isFinite(n)),
    quote: s(x.grounding_quote),
  })).filter((x) => x.points.length > 0)
  return { dt, series }
}

function Chart({ series }: { series: Series[] }) {
  if (!series.length) return null
  const W = 600, Hh = 180, pad = 24
  const n = Math.max(...series.map((x) => x.points.length))
  const xAt = (i: number) => pad + (n > 1 ? (i / (n - 1)) * (W - 2 * pad) : 0)
  const yAt = (v: number) => Hh - pad - Math.max(0, Math.min(1, v)) * (Hh - 2 * pad)
  return (
    <div style={{ margin: '10px 0' }}>
      <svg viewBox={`0 0 ${W} ${Hh}`} style={{ width: '100%', height: 'auto', display: 'block' }} role="img" aria-label="Belief trajectory">
        {[0, 0.5, 1].map((g) => (
          <g key={g}>
            <line x1={pad} x2={W - pad} y1={yAt(g)} y2={yAt(g)} stroke={T.border} strokeWidth={1} />
            <text x={4} y={yAt(g) + 3} fill={T.fg4} fontSize={9} fontFamily="monospace">{g}</text>
          </g>
        ))}
        {series.map((x) => (
          <polyline key={x.key} fill="none" stroke={x.color} strokeWidth={2} points={x.points.map((v, i) => `${xAt(i)},${yAt(v)}`).join(' ')} />
        ))}
      </svg>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
        {series.map((x) => (
          <div key={x.key} style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: x.color, flexShrink: 0 }} />
            <span style={{ fontFamily: T.sans, fontSize: 12, color: T.fg2, lineHeight: 1.5 }}>
              {x.label}{x.quote && <em style={{ color: T.fg3 }}> · &ldquo;{x.quote}&rdquo;</em>}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Block({ b, raw }: { b: Raw; raw: Raw }) {
  const t = s(b.type)
  switch (t) {
    case 'sec_label':
      return <div style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.14em', color: T.fg3, textTransform: 'uppercase' }}><H html={b.text} /></div>
    case 'prose':
    case 'pilot':
      return <Card h2={b.h2} accent={t === 'pilot' ? T.green : undefined}>{arr(b.p).map((p, i) => <p key={i} style={P}><H html={p} /></p>)}</Card>
    case 'list':
      return (
        <Card h2={b.h2}>
          <Intro v={b.intro} />
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {arr(b.items).filter(isRec).map((it, i) => (
              <li key={i} style={{ display: 'flex', gap: 10, alignItems: 'baseline' }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: DOT[s(it.dot)] ?? T.fg4, flexShrink: 0, transform: 'translateY(-1px)' }} />
                <H html={it.html ?? it.text} style={{ ...P, margin: 0 }} />
              </li>
            ))}
          </ul>
        </Card>
      )
    case 'receipt':
    case 'keyvalue': {
      const rows = t === 'receipt'
        ? arr(b.fields).filter(isRec).map((f) => [f.label, f.value])
        : arr(b.rows).filter(isRec).map((r) => [r.k, r.v])
      return (
        <Card h2={b.h2} accent={t === 'receipt' ? T.gold : undefined}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {rows.map(([k, v], i) => (
              <div key={i}>
                <div style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', color: T.fg3, textTransform: 'uppercase', marginBottom: 3 }}><H html={k} /></div>
                <H html={v} style={{ ...P, margin: 0, color: T.fg1, display: 'block' }} />
              </div>
            ))}
          </div>
        </Card>
      )
    }
    case 'table':
      return (
        <Card h2={b.h2}>
          <Intro v={b.intro} />
          <Table head={arr(b.columns)} rows={arr(b.rows).map(arr)} />
          {s(b.note) && <p style={{ ...P, fontSize: 11, color: T.fg3, marginTop: 10 }}><H html={b.note} /></p>}
        </Card>
      )
    case 'rosetta':
      return (
        <Card h2={b.h2}>
          <Table head={[s(b.left) || 'Your world', s(b.right) || 'This engine']} rows={arr(b.rows).map(arr)} />
        </Card>
      )
    case 'provenance': {
      const meta = isRec(raw.meta) ? raw.meta : {}
      const prov = isRec(meta.provenance) ? meta.provenance : {}
      return (
        <Card h2="Source & provenance" accent={T.gold}>
          <p style={P}>Captured: <H html={prov.captured} /></p>
          {s(prov.load_bearing_quote) && (
            <div style={{ borderLeft: `2px solid ${T.gold}`, paddingLeft: 12, fontFamily: T.sans, fontSize: 15, fontStyle: 'italic', color: T.fg1, lineHeight: 1.5 }}>
              &ldquo;<H html={prov.load_bearing_quote} />&rdquo;
            </div>
          )}
        </Card>
      )
    }
    case 'worked_example':
      return (
        <Card h2={b.h2}>
          <Intro v={b.intro} />
          <Chart series={readSeries(raw).series} />
          <Intro v={b.close} />
        </Card>
      )
    case 'insights':
      return (
        <Card h2={b.h2}>
          <Intro v={b.intro} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {arr(raw.insights).filter(isRec).map((it, i) => (
              <div key={i} style={{ borderLeft: `2px solid ${[T.cyan, T.gold, T.green, T.purple][i % 4]}`, paddingLeft: 12 }}>
                <div style={{ fontFamily: T.mono, fontSize: 11, color: T.fg4, letterSpacing: '0.12em', textTransform: 'uppercase' }}>{s(it.plane)}</div>
                <div style={{ ...H2, fontSize: 14, margin: '2px 0 4px' }}><H html={it.title} /></div>
                <H html={it.text} style={{ ...P, margin: 0, display: 'block' }} />
              </div>
            ))}
          </div>
        </Card>
      )
    case 'belief_log': {
      const rows = arr(raw.beliefs).filter(isRec).map((be) => {
        const c = arr(be.confidence)
        return [be.id, be.claim, be.inference, `${c[0] ?? '--'} → ${c[1] ?? '--'}`, be.conviction, be.verdict]
      })
      return <Card h2={b.h2}><Table head={['id', 'claim', 'inf', 'conf', 'conviction', 'verdict']} rows={rows} /></Card>
    }
    case 'kinematics_table': {
      const { dt, series } = readSeries(raw)
      const rows = series.map((x) => {
        const k = derivatives(x.points, dt)
        return [x.label, `${k.d1Peak} / ${k.d1Term}`, String(k.d2Term), String(k.d3Term)]
      })
      const n = series[0]?.points.length ?? 0
      return (
        <Card h2={b.h2}>
          <Table head={['signal', 'D1 peak/term', 'D2 term', 'D3 term']} rows={rows} />
          <p style={{ ...P, fontSize: 11, color: T.fg3, marginTop: 10 }}>
            {kinematicsNote(n)}
          </p>
        </Card>
      )
    }
    case 'foot':
    case 'stamp':
      return <p style={{ ...P, fontFamily: t === 'stamp' ? T.mono : T.sans, fontSize: t === 'stamp' ? 10.5 : 13, color: T.fg3 }}><H html={b.text} /></p>
    default:
      return (
        <AsideBox variant="caution" label={`Unrendered block · ${t || 'untyped'}`}>
          No renderer for this block type yet; it is kept in the SSOT. Add it here and in scripts/recoil_brief.py.
        </AsideBox>
      )
  }
}

function Cover({ raw }: { raw: Raw }) {
  const meta = isRec(raw.meta) ? raw.meta : {}
  const opp = isRec(raw.opportunity) ? raw.opportunity : {}
  const page = isRec(raw.page) ? raw.page : {}
  const hd = isRec(page.header) ? page.header : {}
  const chips: [string, string][] = []
  if (s(opp.y_state)) chips.push([`Y · ${s(opp.y_state)}`, T.gold])
  if (s(opp.topology)) chips.push([s(opp.topology), T.steel])
  if (typeof opp.nci_prior === 'number' || typeof opp.nci_post === 'number') chips.push([`NCI ${opp.nci_prior ?? '--'} → ${opp.nci_post ?? '--'}`, T.cyan])
  if (typeof opp.req_reality === 'number') chips.push([`req reality ${opp.req_reality}`, T.steel])
  return (
    <div style={{ border: `1px solid ${T.border}`, borderRadius: 10, background: T.surface, padding: '22px 22px 18px', marginBottom: 8 }}>
      <div style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.14em', color: T.cyan, textTransform: 'uppercase', marginBottom: 8 }}>
        <H html={hd.eyebrow || 'War Room'} />
      </div>
      <h1 style={{ fontFamily: T.sans, fontSize: 24, fontWeight: 600, color: T.fg1, lineHeight: 1.25, margin: '0 0 6px' }}>
        <H html={hd.title || `${s(meta.counterpart)} · ${s(meta.date)}`} />
      </h1>
      {s(hd.sub) && <p style={{ ...P, margin: '0 0 12px' }}><H html={hd.sub} /></p>}
      {chips.length > 0 && <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>{chips.map(([c, a]) => <Pill key={c} accent={a}>{c}</Pill>)}</div>}
      <div style={{ fontFamily: T.mono, fontSize: 11, color: T.fg4, letterSpacing: '0.06em' }}>
        ARCS WAR ROOM · {s(meta.report_id)} · {s(meta.counterpart)}{typeof meta.segments === 'number' ? ` · ${meta.segments} segments` : ''}
      </div>
    </div>
  )
}

export function WarRoomReport({ raw }: { raw: Raw }) {
  const page = isRec(raw.page) ? raw.page : {}
  const blocks = arr(page.blocks).filter(isRec)
  const tabs = arr(page.tabs).filter(isRec).map((t) => ({ id: s(t.id), label: s(t.label) }))
  // Tab order from page.tabs; blocks with no/unknown tab land in a trailing group in authored order.
  const known = new Set(tabs.map((t) => t.id))
  const groups = tabs.map((t) => ({ ...t, blocks: blocks.filter((b) => s(b.tab) === t.id) }))
  const loose = blocks.filter((b) => !known.has(s(b.tab)))
  if (loose.length) groups.push({ id: 'brief', label: tabs.length ? 'Unfiled' : 'Brief', blocks: loose })
  const opp = isRec(raw.opportunity) ? raw.opportunity : {}
  const nextSteps = arr(raw.next_steps).filter(isRec)

  return (
    <div>
      <Cover raw={raw} />
      {groups.filter((g) => g.blocks.length).map((g, i) => (
        <Sec key={g.id} id={`w-${g.id}`} idx={String(i + 1).padStart(2, '0')} label={g.label} title={g.label} accent={T.cyan}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {g.blocks.map((b, j) => <Block key={j} b={b} raw={raw} />)}
          </div>
        </Sec>
      ))}
      {(s(opp.note) || nextSteps.length > 0) && (
        <Sec id="w-next" idx={String(groups.filter((g) => g.blocks.length).length + 1).padStart(2, '0')} label="Next Steps" title="Opportunity & Next Steps" accent={T.green}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {s(opp.note) && <Card h2="Opportunity note"><p style={{ ...P, whiteSpace: 'pre-wrap' }}><H html={opp.note} /></p></Card>}
            {nextSteps.length > 0 && (
              <Card h2="Next steps">
                <Table head={['owner', 'step']} rows={nextSteps.map((n) => [n.owner, n.text])} />
              </Card>
            )}
          </div>
        </Sec>
      )}
    </div>
  )
}

/** meta minus gate passcodes, for the DeepStrata substrate. */
export function stripGate(raw: Raw): Raw {
  if (!isRec(raw.meta)) return raw
  const { gate: _gate, ...meta } = raw.meta
  void _gate
  return { ...raw, meta }
}
