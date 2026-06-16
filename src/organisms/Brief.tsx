'use client'
import React from 'react'
import { font, signal, border, text, getWeather, nciColor } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Label } from '@/ui/Label'
import { Card } from '@/ui/Card'
import { FatedGrid } from '@/molecules/FatedGrid'
import { TerrainPaths } from '@/molecules/TerrainPaths'
import { TributariesStack } from '@/molecules/TributariesStack'
import type { CompassResult } from '@/lib/mockCompass'

export interface BriefProps {
  result: CompassResult
  onBack?: () => void
  onTributary?: (prompt: string) => void
  onNewQuestion?: () => void
  // AI situation framing — rendered just above the Tributaries block.
  situationFraming?: string
}

export function Brief({ result, onBack, onTributary, onNewQuestion, situationFraming }: BriefProps) {
  const r = result.reasoning || {}
  const fated = r.fated || {}
  const weather = getWeather(result.y_state)

  const [narrow, setNarrow] = React.useState(false)
  React.useEffect(() => {
    const mq = window.matchMedia('(max-width: 720px)')
    const sync = () => setNarrow(mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  const nc = nciColor(result.nci_score)

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '2.5rem 1.5rem 4rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Wordmark section="Cartography Brief" />
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          <Button variant="ghost" size="sm" onClick={onBack}>← Ledger</Button>
          {onNewQuestion && <Button variant="ghost" size="sm" glyph="⊕" onClick={onNewQuestion}>New question</Button>}
        </div>
      </div>

      {/* Status line — fog fidelity */}
      <Label style={{ marginBottom: '1rem', color: weather.color }}>{weather.icon} {weather.label} · {result.render_resolution}</Label>

      {/* Decision — the question, at the top (mirrors the receipt pattern) */}
      <div style={{ marginBottom: '1.25rem', padding: '1rem 1.25rem', background: 'rgba(13,17,23,0.6)', border: `0.5px solid ${border.subtle}`, borderRadius: 6 }}>
        <div style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.12em', color: text.dimmed, textTransform: 'uppercase', marginBottom: '0.4rem' }}>Decision</div>
        <div style={{ fontFamily: font.sans, fontSize: '0.9rem', color: text.secondary, lineHeight: 1.6 }}>{result.question}</div>
      </div>

      {/* True North */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.14em', color: signal.cyan, textTransform: 'uppercase', marginBottom: '0.5rem' }}>True North</div>
        <div style={{ fontFamily: font.sans, fontSize: 'clamp(1.1rem, 2.5vw, 1.5rem)', fontWeight: 600, color: text.primary, lineHeight: 1.35 }}>{result.true_north}</div>
      </div>

      {/* Conviction — full-width, right below True North */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '1rem 1.25rem', background: 'rgba(13,17,23,0.6)', border: `0.5px solid ${border.subtle}`, borderRadius: 6, marginBottom: '1.25rem', flexWrap: narrow ? 'wrap' : 'nowrap' }}>
        <div style={{ flexShrink: 0 }}>
          <div style={{ fontFamily: font.mono, fontSize: '0.55rem', letterSpacing: '0.12em', color: text.dimmed, textTransform: 'uppercase', marginBottom: '0.2rem' }}>Conviction</div>
          <div style={{ fontFamily: font.sans, fontSize: '2.25rem', fontWeight: 700, color: nc, lineHeight: 1, textShadow: `0 0 12px ${nc}55` }}>{result.nci_score}</div>
          <div style={{ fontFamily: font.mono, fontSize: '0.55rem', color: text.dimmed, marginTop: '0.2rem', letterSpacing: '0.06em' }}>/ 100</div>
        </div>
        {!narrow && <div style={{ width: '0.5px', height: 44, background: border.subtle, flexShrink: 0 }} />}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          {([
            ['Mode', result.decision_mode],
            ['Door', result.door_class?.replace(/_/g, ' ')],
            ['Coherence', result.coherence_pct != null ? `${result.coherence_pct}%` : '—'],
            ...(r.advisors?.bayesian_risk_pct != null ? [['Bayesian risk', `${r.advisors.bayesian_risk_pct}%`]] : []),
          ] as [string, string][]).map(([k, v]) => (
            <div key={k}>
              <div style={{ fontFamily: font.mono, fontSize: '0.55rem', letterSpacing: '0.1em', color: text.muted, textTransform: 'uppercase', marginBottom: '0.2rem' }}>{k}</div>
              <div style={{ fontFamily: font.mono, fontSize: '0.75rem', color: text.secondary }}>{v}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Terrain Paths — single column, directly under Conviction */}
      {r.paths?.length ? (
        <div style={{ marginBottom: '1.25rem' }}>
          <TerrainPaths paths={r.paths} />
        </div>
      ) : null}

      {/* Two-col: FATED + Constitutional Court entries */}
      {(Object.keys(fated).length > 0 || r.court) ? (
        <div style={{ display: 'grid', gridTemplateColumns: narrow ? '1fr' : (Object.keys(fated).length > 0 && r.court ? '1fr 1fr' : '1fr'), gap: '1.25rem', marginBottom: '1.25rem' }}>
          {Object.keys(fated).length > 0 ? <FatedGrid fated={fated} /> : null}
          {r.court ? (
            <Card>
              <Label style={{ marginBottom: '1rem' }}>Constitutional Court</Label>
              {r.court.map((c, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.5rem', fontSize: '0.82rem' }}>
                  <span style={{ fontFamily: font.mono, color: c.verdict === 'PASS' ? signal.green : c.verdict === 'TENSION' ? signal.gold : signal.red, fontWeight: 700, minWidth: 64 }}>{c.verdict}</span>
                  <span style={{ color: text.secondary }}><strong style={{ color: text.primary }}>{c.name}</strong> — {c.detail}</span>
                </div>
              ))}
            </Card>
          ) : null}
        </div>
      ) : null}

      {/* Court Verdict — single-column card, same atom as Decision box */}
      {r.court_verdict && (
        <div style={{ marginBottom: '1.25rem', padding: '1rem 1.25rem', background: 'rgba(13,17,23,0.6)', border: `0.5px solid ${border.subtle}`, borderRadius: 6 }}>
          <div style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.12em', color: text.dimmed, textTransform: 'uppercase', marginBottom: '0.4rem' }}>Court Verdict</div>
          <div style={{ fontFamily: font.sans, fontSize: '0.9rem', color: text.secondary, lineHeight: 1.6 }}>{r.court_verdict}</div>
        </div>
      )}

      {/* Situation Framing — above the tributaries block */}
      {situationFraming && (
        <Card style={{ marginBottom: '1.25rem' }}>
          <Label style={{ marginBottom: '0.75rem' }}>Situation Framing</Label>
          <p style={{ fontFamily: font.sans, fontSize: '0.9rem', color: text.secondary, lineHeight: 1.7, margin: 0, whiteSpace: 'pre-wrap' }}>{situationFraming}</p>
        </Card>
      )}

      {/* Where to Navigate Next — tributaries as full-width interactive card */}
      {result.tributaries && result.tributaries.length > 0 && (
        <Card style={{ marginBottom: '1.25rem' }}>
          <TributariesStack tributaries={result.tributaries} onTributary={onTributary} />
        </Card>
      )}
    </div>
  )
}
