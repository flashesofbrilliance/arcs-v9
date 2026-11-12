'use client'
import React from 'react'
import { T } from '../tokens'
import { derivatives, kinematicsNote } from '../kinematics'
import { anatomy, type Anatomy, type Chip, type Fold, type Fidelity, type Tone } from '../recoil/anatomy'

// ─── War-room render path: the recoil component set (arc weld spec 4.1) ──────
// The page plan (header, glance, fold groups, appendix) comes from ../recoil/anatomy, the same
// plan scripts/recoil_page.py renders as single-file HTML (tests/unit/recoil-anatomy.test.ts
// keeps the two equal). This file only draws it: kit look (56 fold, 57 ledger row, 59 claim
// check, 28 chip, 37 fidelity grain) in inline styles from ../tokens.
// The 6-tab war-room SSOTs (recoil-new / recoil-prep / recoil-close; e.g.
// runtime/recoil/generated/2026-09-14-schriner.json) carry meta / opportunity
// / beliefs / kinematic_series / insights / next_steps / page.blocks — not the
// cover / callWalk / signalThreads shape the 6-section report expects. Forcing
// them through an adapter would be lossy (beliefs are not a call walk), so
// RecoilReportFromData branches here instead. Block renderers mirror
// render_block in scripts/recoil_page.py; keep the two in step when a block type is added.
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
export const WARROOM_RENDERED_KEYS = ['page', 'beliefs', 'kinematic_series', 'insights', 'next_steps', 'opportunity', 'schema', 'call', 'verbs']

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

// ─── atoms ────────────────────────────────────────────────────────────────
const TONE: Record<Tone, string> = { cyan: T.cyan, green: T.green, gold: T.gold, red: T.red, magenta: T.magenta, steel: T.steel }
const MONO: React.CSSProperties = { fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }
const P: React.CSSProperties = { fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.6, margin: 0 }
const REF: React.CSSProperties = { fontFamily: T.mono, fontSize: T.fsLabel, letterSpacing: '0.04em', color: T.fg3, lineHeight: 1.5, margin: 0 }
const SUB: React.CSSProperties = { fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, letterSpacing: '0.02em', color: T.fg1, margin: 0, breakAfter: 'avoid' }

/** Kit 28 chip. Steel (unknown) is the plain chip: no fill. */
function ChipEl({ c }: { c: Chip }) {
  const col = TONE[c.tone]
  const plain = c.tone === 'steel'
  return (
    <span style={{ ...MONO, display: 'inline-flex', alignItems: 'center', padding: '3px 10px', borderRadius: 999, whiteSpace: 'nowrap',
      color: col, border: `1px solid ${plain ? T.border : col}`, background: plain ? 'transparent' : `${col}12` }}>{c.label}</span>
  )
}

// Kit 37: fidelity is weight, tracking and a grain overlay, never dimmed text (WORLD.md render scale).
const GRAIN_BG = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E")`
const FID: Record<Fidelity, React.CSSProperties> = {
  SHARP: { fontWeight: 500 },
  DEGRADED: { fontWeight: 400, letterSpacing: '0.01em' },
  GRAIN: { fontWeight: 300, letterSpacing: '0.02em', backgroundImage: GRAIN_BG },
  MOIRE: { fontWeight: 300, letterSpacing: '0.03em', backgroundImage: GRAIN_BG, backgroundColor: `${T.magenta}12` },
}
const FID_VALUE: Record<Fidelity, string> = { SHARP: T.green, DEGRADED: T.gold, GRAIN: T.fg2, MOIRE: T.magenta }

// ─── molecules ────────────────────────────────────────────────────────────
const BOX: React.CSSProperties = { background: T.surface, border: `1px solid ${T.border}`, borderRadius: 6, overflow: 'hidden', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }

/** Kit 57 ledger: key on the left, body on the right; rows never split in print. */
function Ledger({ rows }: { rows: { k: React.ReactNode; body: React.ReactNode }[] }) {
  if (!rows.length) return null
  return (
    <div style={BOX}>
      {rows.map((r, i) => (
        <div key={i} style={{ display: 'grid', gridTemplateColumns: 'minmax(8rem, 22%) minmax(0, 1fr)', gap: '4px 16px', padding: '12px 16px',
          borderTop: i ? `1px solid ${T.border}` : 'none', breakInside: 'avoid' }}>
          <div style={{ fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, letterSpacing: '0.02em', lineHeight: 1.5, color: T.fg2 }}>{r.k}</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 0, fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.6 }}>{r.body}</div>
        </div>
      ))}
    </div>
  )
}

/** Kit 33 LED, for list rows: green on, red alert, otherwise off. */
function Led({ dot, children }: { dot: string; children: React.ReactNode }) {
  const c = dot === 'g' ? T.green : dot === 'r' ? T.red : T.border
  return (
    <span style={{ display: 'inline-flex', alignItems: 'baseline', gap: 8 }}>
      <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: '50%', background: c, flexShrink: 0 }} />{children}
    </span>
  )
}

const TH: React.CSSProperties = { fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, letterSpacing: '0.02em', color: T.fg2, textAlign: 'left', padding: '8px 10px', borderBottom: `1px solid ${T.border}`, verticalAlign: 'bottom' }
const TD: React.CSSProperties = { fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.55, padding: 10, borderBottom: `1px solid ${T.border}`, verticalAlign: 'top' }
function Table({ head, rows }: { head: unknown[]; rows: unknown[][] }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead><tr>{head.map((h, i) => <th key={i} style={TH}><H html={h} /></th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i} style={{ breakInside: 'avoid' }}>{r.map((c, j) => <td key={j} style={TD}><H html={c} /></td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

// D1-D3 by central difference, the same as _grad in scripts/recoil_brief.py.
interface Series { key: string; label: string; color: string; points: number[]; quote: string }
// A series color snaps to the nearest palette signal color (SSOTs carry ad hoc hexes);
// the same rule as palette_color in scripts/recoil_page.py.
const PALETTE = [T.cyan, T.green, T.gold, T.red, T.purple, T.magenta, T.orange]
function paletteColor(c: string): string {
  const m = /^#?([0-9a-f]{6})$/i.exec(c.trim())
  if (!m) return T.cyan
  const rgb = [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16))
  const d = (h: string) => [0, 2, 4].reduce((n, i, k) => n + (parseInt(h.slice(1 + i, 3 + i), 16) - rgb[k]) ** 2, 0)
  return PALETTE.reduce((a, b) => (d(b) < d(a) ? b : a))
}
function readSeries(raw: Raw): { dt: number; series: Series[] } {
  const ks = isRec(raw.kinematic_series) ? raw.kinematic_series : {}
  const dt = typeof ks.dt === 'number' && ks.dt > 0 ? ks.dt : 1
  const series = arr(ks.series).filter(isRec).map((x) => ({
    key: s(x.key), label: s(x.label), color: paletteColor(s(x.color)),
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, breakInside: 'avoid' }}>
      <svg viewBox={`0 0 ${W} ${Hh}`} style={{ width: '100%', height: 'auto', display: 'block' }} role="img" aria-label="Belief trajectory">
        {[0, 0.5, 1].map((g) => (
          <g key={g}>
            <line x1={pad} x2={W - pad} y1={yAt(g)} y2={yAt(g)} stroke={T.border} strokeWidth={1} />
            <text x={4} y={yAt(g) + 3} fill={T.fg3} fontSize={T.fsLabel} fontFamily="monospace">{g}</text>
          </g>
        ))}
        {series.map((x) => (
          <polyline key={x.key} fill="none" stroke={x.color} strokeWidth={2} points={x.points.map((v, i) => `${xAt(i)},${yAt(v)}`).join(' ')} />
        ))}
      </svg>
      <Ledger rows={series.map((x) => ({ k: <span><span aria-hidden="true" style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 3, marginRight: 8, background: x.color }} />{x.label}</span>, body: x.quote ? <span>&ldquo;{x.quote}&rdquo;</span> : null }))} />
    </div>
  )
}

// Kit 59 claim check for the Forge table: green grounded (proven), red struck (failed), plain inference.
const RULING: Record<string, { tone: Tone; value: string }> = {
  GROUNDED: { tone: 'green', value: T.green }, STRUCK: { tone: 'red', value: T.red }, INFERENCE: { tone: 'steel', value: T.fg2 },
}
function ForgeClaims({ rows, ri }: { rows: unknown[][]; ri: number }) {
  return (
    <div style={BOX}>
      {rows.map((r, i) => {
        const raw = s(r[ri]).replace(/<[^>]*>/g, '')
        const word = Object.keys(RULING).find((k) => raw.toUpperCase().includes(k)) ?? ''
        const rl = RULING[word] ?? RULING.INFERENCE
        const label = word ? word[0] + word.slice(1).toLowerCase() : raw
        return (
          <div key={i} style={{ ...(word === 'INFERENCE' ? FID.GRAIN : {}), display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto minmax(0, 1.25fr)', gap: '8px 16px', alignItems: 'start',
            padding: 16, borderTop: i ? `1px solid ${T.border}` : 'none', breakInside: 'avoid', fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.55 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0 }}>
              <H html={r[0]} />
            </div>
            <ChipEl c={{ tone: rl.tone, label }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0 }}>
              <span style={{ fontFamily: T.mono, fontSize: T.fsHeadline, fontWeight: 700, lineHeight: 1.2, color: rl.value }}>{label}</span>
              {r.filter((_, j) => j !== 0 && j !== ri).map((c, j) => <span key={j} style={{ color: T.fg2 }}><H html={c} /></span>)}
            </div>
          </div>
        )
      })}
    </div>
  )
}

/** Kit 58 toast, gold: the standing limit set before the call. Fixed on screen, in the flow in print. */
function Guard({ g }: { g: NonNullable<Anatomy['guard']> }) {
  const [shown, setShown] = React.useState(true)
  React.useEffect(() => {
    const esc = (e: KeyboardEvent) => { if (e.key === 'Escape') setShown(false) }
    document.addEventListener('keydown', esc)
    return () => document.removeEventListener('keydown', esc)
  }, [])
  if (!shown) return null
  return (
    <div role="status" data-toast="" style={{ position: 'fixed', right: 20, bottom: 20, zIndex: 50, width: 'min(380px, calc(100vw - 32px))', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto',
      alignItems: 'center', gap: '4px 12px', padding: '12px 12px 16px 16px', background: T.elevated, border: `1px solid ${T.gold}`, borderRadius: 6 }}>
      <span style={{ ...MONO, color: T.gold }}>{g.title}</span>
      <button type="button" aria-label="Dismiss" onClick={() => setShown(false)} data-print="hide"
        style={{ width: 44, height: 44, margin: '-8px -4px -8px 0', border: 0, background: 'transparent', color: T.fg2, cursor: 'pointer', fontSize: T.fsBody }}>&#215;</button>
      <p style={{ ...P, gridColumn: '1 / -1' }}>{g.text}</p>
      <span style={{ ...REF, gridColumn: '1 / -1', color: T.fg2 }}>Set before the call, in the Ex-Ante receipt</span>
    </div>
  )
}

// ─── block bodies (an SSOT tab inside its fold) ────────────────────────────
const norm = (t: unknown) => s(t).replace(/<[^>]*>/g, '').replace(/&#183;|&middot;/g, '·').replace(/^\s*\d+\s*[·.:-]\s*/, '').trim().toLowerCase()
const LEAD = /^\s*<(strong|b)>([\s\S]*?)<\/\1>\s*:?\s*/

function Block({ b, raw, foldTitle, next }: { b: Raw; raw: Raw; foldTitle: string; next?: Raw }) {
  const t = s(b.type)
  const h2 = s(b.h2) ? <h3 style={SUB}><H html={b.h2} /></h3> : null
  const intro = s(b.intro) ? <p style={P}><H html={b.intro} /></p> : null
  switch (t) {
    case 'sec_label':
      // The fold title already names the section: never print a section label twice.
      if ([foldTitle.toLowerCase(), norm(next?.h2)].includes(norm(b.text))) return null
      return <h3 style={SUB}><H html={b.text} /></h3>
    case 'prose':
    case 'pilot':
      return <>{h2}{arr(b.p).map((p, i) => <p key={i} style={P}><H html={p} /></p>)}</>
    case 'list':
      if (s(b.tab) === 'pre' && /intel/i.test(s(b.h2))) {
        // Kit 62 attributed notes: who the counterpart is, as gathered before the call.
        return (
          <div style={{ background: T.elevated, border: `1px solid ${T.border}`, borderRadius: 6, padding: 16, display: 'flex', flexDirection: 'column', gap: 12, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', justifyContent: 'space-between', gap: '4px 12px' }}>
              <h3 style={{ ...MONO, color: T.fg1, margin: 0 }}><H html={b.h2} /></h3>
              <span style={{ ...REF, color: T.fg2 }}>Gathered before the call</span>
            </div>
            {intro}
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {arr(b.items).filter(isRec).map((it, i) => {
                const html = s(it.html ?? it.text)
                const m = LEAD.exec(html)
                return (
                  <li key={i} style={{ ...P, color: T.fg2, breakInside: 'avoid' }}>
                    {m ? <><strong style={{ color: T.fg1, fontWeight: 600 }}><H html={m[2]} /></strong> <H html={html.slice(m[0].length)} /></> : <H html={html} />}
                  </li>
                )
              })}
            </ul>
          </div>
        )
      }
      return (
        <>{h2}{intro}
          <Ledger rows={arr(b.items).filter(isRec).map((it) => {
            const html = s(it.html ?? it.text)
            const m = LEAD.exec(html)
            const key = m ? m[2].replace(/<[^>]*>/g, '').replace(/:$/, '') : ''
            return { k: <Led dot={s(it.dot)}><H html={key || 'Note'} /></Led>, body: <H html={m ? html.slice(m[0].length) : html} /> }
          })} />
        </>
      )
    case 'receipt':
    case 'keyvalue': {
      const rows = t === 'receipt'
        ? arr(b.fields).filter(isRec).map((f) => [f.label, f.value])
        : arr(b.rows).filter(isRec).map((r) => [r.k, r.v])
      return <>{h2}<Ledger rows={rows.map(([k, v]) => ({ k: <H html={k} />, body: <H html={v} /> }))} /></>
    }
    case 'table': {
      const cols = arr(b.columns).map((c) => s(c).replace(/<[^>]*>/g, '').toLowerCase())
      const ri = cols.findIndex((c) => c.includes('ruling'))
      if (s(b.tab) === 'forge' && ri >= 0) return <>{h2}{intro}<ForgeClaims rows={arr(b.rows).map(arr)} ri={ri} /></>
      return <>{h2}{intro}<Table head={arr(b.columns)} rows={arr(b.rows).map(arr)} />{s(b.note) && <p style={REF}><H html={b.note} /></p>}</>
    }
    case 'rosetta':
      return <>{h2}<Table head={[s(b.left) || 'Your world', s(b.right) || 'This engine']} rows={arr(b.rows).map(arr)} /></>
    case 'provenance': {
      const prov = isRec(raw.meta) && isRec(raw.meta.provenance) ? raw.meta.provenance : {}
      return (
        <>
          <h3 style={SUB}>Source and provenance</h3>
          <Ledger rows={[
            { k: 'Captured', body: <H html={prov.captured} /> },
            ...(s(prov.load_bearing_quote) ? [{ k: 'Load-bearing quote', body: <span>&ldquo;<H html={prov.load_bearing_quote} />&rdquo;</span> }] : []),
          ]} />
        </>
      )
    }
    case 'worked_example':
      return <>{h2}{intro}<Chart series={readSeries(raw).series} />{s(b.close) && <p style={P}><H html={b.close} /></p>}</>
    case 'insights':
      return (
        <>{h2}{intro}
          <Ledger rows={arr(raw.insights).filter(isRec).map((it) => ({ k: s(it.plane), body: <span><strong><H html={it.title} /></strong> <H html={it.text} /></span> }))} />
        </>
      )
    case 'belief_log':
      return <>{h2}<p style={REF}>The belief log is shown once, in the <a href="#f-forecasts" style={{ color: T.cyan }}>Forecasts</a> fold under Decide.</p></>
    case 'kinematics_table': {
      const { dt, series } = readSeries(raw)
      const rows = series.map((x) => {
        const k = derivatives(x.points, dt)
        return [x.label, `${k.d1Peak} / ${k.d1Term}`, String(k.d2Term), String(k.d3Term)]
      })
      return <>{h2}<Table head={['signal', 'D1 peak/term', 'D2 term', 'D3 term']} rows={rows} /><p style={REF}>{kinematicsNote(series[0]?.points.length ?? 0)}</p></>
    }
    case 'foot':
    case 'stamp':
      return <p style={REF}><H html={b.text} /></p>
    default:
      return <p style={REF}>Unrendered block · {t || 'untyped'}. Kept in the SSOT; add a renderer here and in scripts/recoil_page.py.</p>
  }
}

// ─── organisms ────────────────────────────────────────────────────────────
function Header({ h }: { h: Anatomy['header'] }) {
  return (
    <header style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <p style={{ ...MONO, letterSpacing: '0.14em', color: T.fg3, margin: 0 }}>{h.eyebrow}</p>
      <h1 style={{ fontFamily: T.sans, fontSize: T.fsDisplay, fontWeight: 600, color: T.fg1, lineHeight: 1.2, margin: 0 }}>{h.title}</h1>
      <p style={REF}>{h.ref}</p>
      <p style={{ fontFamily: T.sans, fontSize: T.fsHeadline, lineHeight: 1.5, color: T.fg2, margin: 0 }}>{h.lede}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {h.chips.map((c, i) => <span key={c.label} style={i === 1 && h.nciGrain ? FID.GRAIN : undefined}><ChipEl c={c} /></span>)}
      </div>
    </header>
  )
}

function Glance({ rows }: { rows: Anatomy['glance'] }) {
  const [status, setStatus] = React.useState('Nothing is sent from this page.')
  const copy = (text: string) => {
    try { void navigator.clipboard.writeText(text).then(() => setStatus('Copied. Nothing is sent from this page.')) } catch { setStatus('Copy was blocked here; select the text and copy it.') }
  }
  return (
    <section aria-labelledby="w-glance" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <h2 id="w-glance" style={{ ...MONO, letterSpacing: '0.14em', color: T.fg3, margin: 0 }}>At a glance</h2>
      <Ledger rows={rows.map((g, i) => ({
        k: g.key,
        body: (
          <>
            {g.chip && <div><ChipEl c={g.chip} /></div>}
            <span>{g.text}{g.href && <> <a href={g.href} style={{ color: T.cyan }}>Open</a></>}</span>
            {i === 0 && g.key === 'Next move' && g.href && (
              <div data-print="hide" style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                <button type="button" onClick={() => copy(g.text)} style={{ ...MONO, color: T.fg1, background: T.elevated, border: `1px solid ${T.border}`, borderRadius: 6, padding: '8px 14px', cursor: 'pointer' }}>Copy</button>
                <span aria-live="polite" style={REF}>{status}</span>
              </div>
            )}
          </>
        ),
      }))} />
    </section>
  )
}

/** Kit 56 fold: closed on screen, its summary states the verdict and carries a grade chip. */
function FoldEl({ f, children }: { f: Pick<Fold, 'id' | 'title' | 'verdict' | 'chip'>; children: React.ReactNode }) {
  return (
    <details id={f.id} data-fold="" style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 6, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>
      <summary style={{ listStyle: 'none', cursor: 'pointer', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '8px 16px', padding: 16, breakAfter: 'avoid' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0, flex: '1 1 20rem' }}>
          <h2 style={{ ...MONO, letterSpacing: '0.14em', color: T.fg2, margin: 0 }}>{f.title}</h2>
          <span style={{ fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.5 }}>{f.verdict}</span>
        </div>
        <ChipEl c={f.chip} />
      </summary>
      <div style={{ padding: '16px 16px 20px', borderTop: `1px solid ${T.border}`, display: 'flex', flexDirection: 'column', gap: 12 }}>{children}</div>
    </details>
  )
}

function Forecasts({ a }: { a: Anatomy }) {
  return (
    <>
      <p style={REF}>Confidence before and after the call, 0 to 1. A forecast with no grade is not scored, so it renders grain with its sample size.</p>
      <div style={BOX}>
        {a.forecasts.map((f, i) => (
          // Kit 59 claim check: what was held, the grade, the record.
          <div key={f.id} style={{ ...FID[f.fidelity], display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto minmax(7rem, auto)', gap: '8px 16px', alignItems: 'start',
            padding: 16, borderTop: i ? `1px solid ${T.border}` : 'none', breakInside: 'avoid', fontFamily: T.sans, fontSize: T.fsBody, color: T.fg1, lineHeight: 1.55 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 0 }}>
              <span style={{ fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, color: T.fg2 }}>{f.id}</span>
              <span>{f.claim}</span>
            </div>
            <ChipEl c={f.chip} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <span style={{ fontFamily: T.mono, fontSize: T.fsHeadline, lineHeight: 1.2, fontVariantNumeric: 'tabular-nums', color: FID_VALUE[f.fidelity], fontWeight: f.fidelity === 'SHARP' ? 700 : 300 }}>{f.before} → {f.after}</span>
              <span style={{ color: T.fg2 }}>{f.moved ? 'Moved on the call' : 'Held'}</span>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}

function FoldBody({ f, a, raw }: { f: Fold; a: Anatomy; raw: Raw }) {
  if (f.kind === 'blocks') {
    const blocks = arr(isRec(raw.page) ? raw.page.blocks : []).map((b) => (isRec(b) ? b : {}))
    const own = (f.blocks ?? []).map((i) => blocks[i])
    return <>{own.map((b, j) => <Block key={j} b={b} raw={raw} foldTitle={f.title} next={own[j + 1]} />)}</>
  }
  if (f.kind === 'next') {
    const opp = isRec(raw.opportunity) ? raw.opportunity : {}
    const facts = ([['engagement_type', 'Engagement'], ['topology', 'Topology'], ['req_reality', 'Req reality (0 to 3)']] as const)
      .filter(([k]) => s(opp[k]))
      .map(([k, label]) => ({ k: label, body: <><H html={opp[k]} />{s(opp[`${k}_basis`]) && <span style={REF}><H html={opp[`${k}_basis`]} /></span>}</> }))
    const steps = arr(raw.next_steps).filter(isRec)
    return (
      <>
        {s(opp.note) && <p style={{ ...P, whiteSpace: 'pre-wrap' }}><H html={opp.note} /></p>}
        <Ledger rows={facts} />
        {steps.length > 0 && <><h3 style={SUB}>Next steps</h3><Ledger rows={steps.map((n) => ({ k: s(n.owner) || 'Unowned', body: <H html={n.text} /> }))} /></>}
      </>
    )
  }
  if (f.kind === 'forecasts') return <Forecasts a={a} />
  if (f.kind === 'verb') {
    const vp = isRec(raw.verbs) && isRec(raw.verbs[f.verb ?? '']) ? (raw.verbs[f.verb ?? ''] as Raw) : {}
    const cites = arr(vp.cites).map(s).join(', ')
    return <>{arr(vp.body).map((x, i) => <p key={i} style={P}><H html={x} /></p>)}{cites && <p style={REF}>Cites {cites}</p>}</>
  }
  // glass box
  const meta = isRec(raw.meta) ? raw.meta : {}
  const mig = isRec(raw.migration) ? raw.migration : {}
  return (
    <Ledger rows={[
      { k: 'Source', body: `runtime/recoil/generated/${s(meta.report_id)}.json, shape ${s(mig.from) || (s(raw.schema) ? 'v2' : 'six-tab.v1')}` },
      { k: 'Plan', body: 'src/document/recoil/anatomy.ts, the twin of plan() in scripts/recoil_page.py; a unit test fails if they differ' },
      { k: 'Fidelity', body: 'A SHARP, B SHARP, C DEGRADED, D GRAIN, E GRAIN, NS GRAIN; Y PARADOX overrides to MOIRE' },
      { k: 'Color', body: 'red a failed check, gold a limit, green proven, cyan an action, plain chip unknown, magenta paradox' },
    ]} />
  )
}

/** Appendix: every key the folds do not render, verbatim (meta without passcodes). */
function Strata({ raw }: { raw: Raw }) {
  const skip = new Set([...WARROOM_RENDERED_KEYS, 'meta'])
  const meta = isRec(raw.meta) ? raw.meta : {}
  const items: [string, unknown][] = [['meta', meta], ...Object.entries(raw).filter(([k, v]) => !skip.has(k) && v != null)]
  const pre: React.CSSProperties = { ...REF, color: T.fg2, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }
  return (
    <>
      <p style={REF}>Verbatim, except that template text written with an em-dash shows a comma (house style, em-dashes 0).</p>
      {items.map(([k, v]) => (
        <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <h3 style={SUB}>{k}</h3>
          <pre style={pre}>{(typeof v === 'string' ? v : JSON.stringify(v, null, 1)).replace(/\s*\u2014\s*/g, ', ')}</pre>
        </div>
      ))}
    </>
  )
}

// Print (inline styles cannot reach ::details-content): every fold opens, rows stay whole
// (breakInside on each row above), chrome carrying data-print="hide" is dropped.
const PRINT_CSS = '@media print { details[data-fold]::details-content { content-visibility: visible; display: contents } [data-toast] { position: static !important; width: auto !important } }'

export function WarRoomReport({ raw }: { raw: Raw }) {
  const a = React.useMemo(() => anatomy(raw), [raw])
  const root = React.useRef<HTMLDivElement>(null)
  const setAll = (open: boolean) => root.current?.querySelectorAll('details[data-fold]').forEach((d) => { (d as HTMLDetailsElement).open = open })
  React.useEffect(() => {
    const openHash = () => { const el = location.hash && document.getElementById(location.hash.slice(1)); if (el && el.tagName === 'DETAILS') (el as HTMLDetailsElement).open = true }
    const all = () => setAll(true)
    openHash()
    window.addEventListener('hashchange', openHash)
    window.addEventListener('beforeprint', all)
    return () => { window.removeEventListener('hashchange', openHash); window.removeEventListener('beforeprint', all) }
  }, [])
  const nfold = a.groups.reduce((n, g) => n + g.folds.length, 0)
  const btn: React.CSSProperties = { ...MONO, color: T.fg1, background: T.elevated, border: `1px solid ${T.border}`, borderRadius: 6, padding: '8px 14px', cursor: 'pointer' }
  return (
    <div ref={root} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <style>{PRINT_CSS}</style>
      <Header h={a.header} />
      <Glance rows={a.glance} />
      <div data-print="hide" style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <p style={{ ...P, color: T.fg2 }}>{nfold} folds in {a.groups.length} groups, then the Deeper Strata. Each summary states its verdict.</p>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="button" style={btn} onClick={() => setAll(true)}>Open all</button>
          <button type="button" style={btn} onClick={() => setAll(false)}>Close all</button>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {a.groups.map((g, gi) => (
          <React.Fragment key={g.name}>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '4px 12px', margin: gi ? '16px 0 4px' : '0 0 4px', breakAfter: 'avoid' }}>
              <span style={{ ...MONO, letterSpacing: '0.14em', color: T.fg1 }}>{g.name}</span>
              <span style={{ ...P, color: T.fg2 }}>{g.note}</span>
            </div>
            {g.folds.map((f) => <FoldEl key={f.id} f={f}><FoldBody f={f} a={a} raw={raw} /></FoldEl>)}
          </React.Fragment>
        ))}
      </div>
      <FoldEl f={{ ...a.appendix, chip: { tone: 'steel', label: 'Provenance' } }}><Strata raw={raw} /></FoldEl>
      {a.guard && <Guard g={a.guard} />}
      <div aria-hidden="true" style={{ height: a.guard ? 120 : 0 }} />
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
