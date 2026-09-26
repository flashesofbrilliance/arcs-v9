'use client'
import React, { useCallback, useEffect, useState } from 'react'
import { font, text, signal, border } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { Button } from '@/ui/Button'

// TribunePanel — ADR-020 step 6. Reads /api/tribune for a persisted receipt and renders the
// three phases at earned fidelity: SIMPLE = one line per phase, RICH = + bullets and board,
// DEEP = full LAB output. Proactive stays silent below threshold and says so in one line.
// Annotates, never mutates: nothing here writes to the Receipt except the baton hand-off
// (server-side, ADR-020 additive column).

type Phase = 'anterior' | 'proactive' | 'posterior'
type Board = Record<string, { vote: 'green' | 'red'; objection?: string }>
interface Content {
  phase: Phase
  one_line: string
  bullets?: string[]
  coalition_readiness: number
  board?: Board
  lab?: { loki: string; advisors: string; bayesian: string; posterior_probability?: number }
  detail?: Record<string, unknown>
}
interface Row { phase: Phase; risk_tier?: string | null; drift_state?: string | null; nci_delta?: number | null; court_invoked?: boolean; content: Content }

const PHASE_META: Record<Phase, { label: string; verb: string; hint: string }> = {
  anterior: { label: 'Anterior', verb: 'Run pre-mortem', hint: 'before the needle moves' },
  proactive: { label: 'Proactive', verb: 'Observe', hint: 'silent unless a threshold fires' },
  posterior: { label: 'Posterior', verb: 'Debrief', hint: 'after an outcome is logged' },
}
const PHASES: Phase[] = ['anterior', 'proactive', 'posterior']

export function TribunePanel({ receiptId }: { receiptId: string }) {
  const [rows, setRows] = useState<Record<string, Row>>({})
  const [silent, setSilent] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState<Phase | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [authed, setAuthed] = useState(true)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/tribune?receipt_id=${encodeURIComponent(receiptId)}`)
      .then(async (r) => ({ status: r.status, data: await r.json().catch(() => ({})) }))
      .then(({ status, data }) => {
        if (cancelled) return
        if (status === 401) { setAuthed(false); return }
        if (status !== 200) return
        const next: Record<string, Row> = {}
        for (const t of (data.tribunes ?? []) as Row[]) next[t.phase] = t
        setRows(next)
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [receiptId])

  const run = useCallback(async (phase: Phase) => {
    setBusy(phase); setErr(null)
    try {
      const r = await fetch('/api/tribune', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ receipt_id: receiptId, phase }),
      })
      const data = await r.json().catch(() => ({}))
      if (r.status === 401) { setAuthed(false); return }
      if (!r.ok) { setErr(data.error ?? `Tribune ${phase} failed`); return }
      if (data.silent) {
        setSilent((s) => ({ ...s, [phase]: `Silent. No threshold fired (risk ${data.risk_tier ?? '?'}, NCI Δ ${data.nci_delta ?? 'n/a'}).` }))
        return
      }
      setRows((prev) => ({ ...prev, [phase]: { phase, risk_tier: data.risk_tier, drift_state: data.drift_state, nci_delta: data.nci_delta, court_invoked: data.court_invoked, content: data.content } }))
    } catch {
      setErr('Tribune unavailable')
    } finally {
      setBusy(null)
    }
  }, [receiptId])

  if (!authed) return null // Tribune is an owner surface; anonymous readers see nothing, by design

  return (
    <Card padding="compact" style={{ padding: '1rem 1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
        <Label style={{ marginBottom: 0 }}>Tribune</Label>
        <span style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.08em', color: text.dimmed, textTransform: 'uppercase' }}>annotates · never decides</span>
      </div>
      <div style={{ height: 1, background: border.subtle, margin: '0.75rem 0' }} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
        {PHASES.map((phase) => {
          const row = rows[phase]
          const meta = PHASE_META[phase]
          return (
            <div key={phase}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                <span style={{ fontFamily: font.mono, fontSize: '0.62rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: row ? signal.cyan : text.muted }}>
                  {meta.label}
                  {row?.court_invoked && <span style={{ color: signal.red, marginLeft: 8 }}>COURT</span>}
                </span>
                <Button variant="ghost" size="sm" disabled={busy !== null} onClick={() => run(phase)}>
                  {busy === phase ? '…' : row ? 'Re-run' : meta.verb}
                </Button>
              </div>
              {row ? (
                <PhaseBody row={row} />
              ) : (
                <div style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed, lineHeight: 1.5, marginTop: '0.25rem' }}>
                  {silent[phase] ?? meta.hint}
                </div>
              )}
            </div>
          )
        })}
      </div>
      {err && <div style={{ fontFamily: font.mono, fontSize: '0.65rem', color: signal.red, marginTop: '0.75rem' }}>{err}</div>}
    </Card>
  )
}

function PhaseBody({ row }: { row: Row }) {
  const c = row.content
  const readiness = Math.round((c.coalition_readiness ?? 0) * 100)
  const reds = c.board ? Object.entries(c.board).filter(([, v]) => v.vote === 'red') : []
  return (
    <div style={{ marginTop: '0.35rem' }}>
      <div style={{ fontFamily: font.sans, fontSize: '0.88rem', color: text.primary, lineHeight: 1.5 }}>{c.one_line}</div>
      <div style={{ fontFamily: font.mono, fontSize: '0.62rem', color: text.muted, marginTop: '0.3rem', letterSpacing: '0.06em' }}>
        BOARD {readiness}% GREEN{row.risk_tier ? ` · RISK ${row.risk_tier.toUpperCase()}` : ''}{row.nci_delta != null ? ` · NCI Δ ${row.nci_delta > 0 ? '+' : ''}${row.nci_delta}` : ''}{row.drift_state ? ` · DRIFT ${row.drift_state}` : ''}
      </div>
      {c.bullets && c.bullets.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.5rem' }}>
          {c.bullets.map((b, i) => (
            <div key={i} style={{ display: 'flex', gap: '0.6rem', fontFamily: font.sans, fontSize: '0.8rem', color: text.secondary, lineHeight: 1.5 }}>
              <span style={{ color: signal.cyan, fontFamily: font.mono, fontSize: '0.65rem', marginTop: '0.15rem' }}>·</span><span>{b}</span>
            </div>
          ))}
        </div>
      )}
      {reds.length > 0 && (
        <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {reds.map(([role, v]) => (
            <div key={role} style={{ fontFamily: font.mono, fontSize: '0.65rem', color: text.secondary }}>
              <span style={{ color: signal.red, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{role}</span>{v.objection ? `. ${v.objection}` : ''}
            </div>
          ))}
        </div>
      )}
      {c.lab && (c.lab.loki || c.lab.advisors || c.lab.bayesian) && (
        <div style={{ marginTop: '0.6rem', borderLeft: `1px solid ${border.subtle}`, paddingLeft: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {(['loki', 'advisors', 'bayesian'] as const).map((k) => c.lab?.[k] ? (
            <div key={k} style={{ fontFamily: font.sans, fontSize: '0.78rem', color: text.secondary, lineHeight: 1.5 }}>
              <span style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: text.muted, marginRight: 8 }}>{k}</span>{c.lab[k]}
            </div>
          ) : null)}
          {typeof c.lab.posterior_probability === 'number' && (
            <div style={{ fontFamily: font.mono, fontSize: '0.62rem', color: text.muted }}>P(holds) {Math.round(c.lab.posterior_probability * 100)}%</div>
          )}
        </div>
      )}
    </div>
  )
}
