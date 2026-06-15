'use client'
import React from 'react'
import { font, signal, border, text, getWeather } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Label } from '@/ui/Label'
import { Card } from '@/ui/Card'
import { FatedGrid } from '@/molecules/FatedGrid'
import { TerrainPaths } from '@/molecules/TerrainPaths'
import { ConvictionSidebar } from '@/molecules/ConvictionSidebar'
import type { CompassResult } from '@/lib/mockCompass'

// Brief — Cartography Brief organism (two-column). PRESENTATIONAL: result via
// props, onBack callback. Source: compass-app/Brief.jsx.
export interface BriefProps {
  result: CompassResult
  onBack?: () => void
  onTributary?: (prompt: string) => void
  onNewQuestion?: () => void
}

export function Brief({ result, onBack, onTributary, onNewQuestion }: BriefProps) {
  const r = result.reasoning || {}
  const fated = r.fated || {}
  const weather = getWeather(result.y_state)

  // Two-column brief collapses to a single column on narrow viewports — the
  // fixed 280px sidebar otherwise overflows portrait phones. matchMedia (not a
  // CSS @media rule) keeps this within the inline-styles-only constraint.
  const [narrow, setNarrow] = React.useState(false)
  React.useEffect(() => {
    const mq = window.matchMedia('(max-width: 720px)')
    const sync = () => setNarrow(mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '2.5rem 1.5rem 4rem' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Wordmark section="Cartography Brief" />
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          <Button variant="ghost" size="sm" onClick={onBack}>← Ledger</Button>
          {onNewQuestion && <Button variant="ghost" size="sm" glyph="⊕" onClick={onNewQuestion}>New question</Button>}
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <Label style={{ marginBottom: '0.75rem', color: weather.color }}>{weather.icon} {weather.label} · {result.render_resolution}</Label>
        <h1 style={{ fontFamily: font.sans, fontSize: '1.5rem', fontWeight: 600, color: text.primary, margin: '0 0 0.75rem', lineHeight: 1.3, letterSpacing: '-0.01em' }}>{result.question}</h1>
        <p style={{ fontFamily: font.sans, fontSize: '1.0625rem', color: text.primary, margin: 0, lineHeight: 1.6, fontWeight: 500 }}>
          <span style={{ color: signal.cyan }}>True North · </span>{result.true_north}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: narrow ? '1fr' : '1fr 280px', gap: '1.25rem', alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <FatedGrid fated={fated} />
          <TerrainPaths paths={r.paths} />
          {r.court && (
            <Card>
              <Label style={{ marginBottom: '1rem' }}>Constitutional Court</Label>
              {r.court.map((c, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.5rem', fontSize: '0.82rem' }}>
                  <span style={{ fontFamily: font.mono, color: c.verdict === 'PASS' ? signal.green : c.verdict === 'TENSION' ? signal.gold : signal.red, fontWeight: 700, minWidth: 64 }}>{c.verdict}</span>
                  <span style={{ color: text.secondary }}><strong style={{ color: text.primary }}>{c.name}</strong> — {c.detail}</span>
                </div>
              ))}
              {r.court_verdict && <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: `1px solid ${border.subtle}`, fontSize: '0.82rem', color: text.dimmed, fontStyle: 'italic' }}>{r.court_verdict}</div>}
            </Card>
          )}
        </div>

        <ConvictionSidebar result={result} onTributary={onTributary} />
      </div>
    </div>
  )
}
