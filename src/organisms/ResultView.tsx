'use client'
import React from 'react'
import { font, signal, border, text, getWeather, resStyle, contentContainer } from '@/ui/tokens'
import { useVw } from '@/ui/useVw'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Rule } from '@/ui/Rule'
import { Label } from '@/ui/Label'
import { Tabs } from '@/ui/Tabs'
import { WeatherBar } from '@/instrument/WeatherBar'
import { TrueNorthPanel } from '@/instrument/TrueNorthPanel'
import { InstrumentCluster } from '@/molecules/InstrumentCluster'
import { TributariesStack } from '@/molecules/TributariesStack'
import type { CompassResult } from '@/lib/mockCompass'

// ResultView — Receipt organism. PRESENTATIONAL: result via props, actions via
// callbacks. showReasoning is local view state (not data). Source: Result.jsx.
export interface ResultViewProps {
  result: CompassResult
  onReset?: () => void
  onBrief?: () => void
  onTributary?: (prompt: string) => void
  onHistory?: () => void
}

export function ResultView({ result, onReset, onBrief, onTributary, onHistory }: ResultViewProps) {
  const vw = useVw()
  const [showReasoning, setShowReasoning] = React.useState(false)
  const weather = getWeather(result.y_state)
  const rs = resStyle[result.render_resolution] || resStyle.SHARP
  const r = result.reasoning || {}
  const verdictColor = (v: string) => v === 'PASS' ? signal.green : v === 'TENSION' ? signal.gold : signal.red

  return (
    <div style={{ ...contentContainer(vw), paddingTop: '2rem', paddingBottom: '4rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark section="Receipt" />
        <div style={{ display: "flex", gap: "0.25rem" }}>
          {onHistory && <Button variant="ghost" size="sm" onClick={onHistory}>← Ledger</Button>}
          <Button variant="ghost" size="sm" glyph="⊕" onClick={onReset}>New question</Button>
        </div>
      </div>
      <Rule style={{ marginBottom: '1.5rem' }} />

      <div style={{ fontFamily: font.sans, fontSize: '0.9rem', color: text.secondary, lineHeight: 1.5, marginBottom: '1.5rem', paddingLeft: '0.85rem', borderLeft: `2px solid ${signal.cyan}55` }}>
        {result.question}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
        <WeatherBar weather={weather} delta={result.nci_delta} resolution={result.render_resolution} />

        <TrueNorthPanel heading={`True North · ${result.decision_mode} · ${result.door_class}`}
          footnotes={result.why?.length > 0 && (
            <ul style={{ position: 'relative', margin: '0.85rem 0 0', paddingLeft: '1.25rem', lineHeight: 1.7, color: '#bfeef5', fontSize: '0.875rem', ...rs }}>
              {result.why.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          )}>
          {result.true_north}
        </TrueNorthPanel>

        <InstrumentCluster result={result} />

        <Button variant="outline-cyan" glyph="⊕" onClick={onBrief} style={{ width: '100%' }}>Open Cartography Brief&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></Button>

        {result.tributaries?.length > 0 && (
          <div style={{ marginTop: '0.5rem' }}>
            <TributariesStack tributaries={result.tributaries} onTributary={onTributary} />
          </div>
        )}

        {r.court && (
          <>
            <Button variant="ghost" onClick={() => setShowReasoning(v => !v)} style={{ width: '100%', justifyContent: 'space-between' }}>
              <span>{showReasoning ? 'Hide reasoning · L0–L5' : 'Show full reasoning · L0–L5'}</span>
              <span style={{ display: 'inline-block', transition: 'transform .2s ease', transform: showReasoning ? 'rotate(90deg)' : 'none', fontSize: '0.85em', lineHeight: 1 }}>▶</span>
            </Button>
            {showReasoning && (
              <div style={{ ...rs }}>
                <Tabs accent={signal.cyan} items={[
                  { value: 'court', label: 'Court', glyph: '◆', content: (
                    <>
                      <Label style={{ marginBottom: '0.75rem' }}>Constitutional Court</Label>
                      {r.court.map((c, i) => (
                        <div key={i} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                          <span style={{ fontFamily: font.mono, color: verdictColor(c.verdict), fontWeight: 700, minWidth: 64 }}>{c.verdict}</span>
                          <span style={{ color: text.secondary }}><strong style={{ color: text.primary }}>{c.name}</strong> — {c.detail}</span>
                        </div>
                      ))}
                      {r.court_verdict && <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: `1px solid ${border.subtle}`, fontSize: '0.8rem', color: text.dimmed, fontStyle: 'italic' }}>{r.court_verdict}</div>}
                    </>
                  ) },
                  ...(r.advisors ? [{ value: 'advisors', label: 'Advisors', glyph: '⊕', content: (
                    <>
                      <Label style={{ marginBottom: '0.5rem' }}>Advisors</Label>
                      <div style={{ fontSize: '0.8rem', color: text.secondary, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <div><span style={{ color: signal.red, fontWeight: 600 }}>Loki: </span>{r.advisors.loki_challenge}</div>
                        <div><span style={{ color: signal.green, fontWeight: 600 }}>Counter: </span>{r.advisors.loki_counter}</div>
                        <div><span style={{ color: text.muted }}>Bayesian risk: </span><span style={{ color: signal.gold, fontWeight: 600 }}>{r.advisors.bayesian_risk_pct}%</span> — {r.advisors.bayesian_rationale}</div>
                      </div>
                    </>
                  ) }] : []),
                ]} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
