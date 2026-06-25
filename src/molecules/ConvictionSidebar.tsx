'use client'
import React from 'react'
import { font, border, text, nciColor } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { TributariesStack } from '@/molecules/TributariesStack'
import type { CompassResult } from '@/lib/mockCompass'

// ConvictionSidebar — Card (Conviction readout) + interactive TributariesStack.
export interface ConvictionSidebarProps {
  result: CompassResult
  onTributary?: (prompt: string) => void
}

export function ConvictionSidebar({ result, onTributary }: ConvictionSidebarProps) {
  const r = result.reasoning || {}
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', position: 'sticky', top: '1rem' }}>
      <Card padding="compact" style={{ padding: '1rem 1.25rem' }}>
        <Label style={{ marginBottom: '0.75rem' }}>Conviction</Label>
        <div style={{ fontFamily: font.sans, fontSize: '2.5rem', fontWeight: 700, color: nciColor(result.nci_score), lineHeight: 1 }}>{result.nci_score}</div>
        <div style={{ fontFamily: font.mono, fontSize: '0.65rem', color: text.muted, marginTop: '0.35rem', letterSpacing: '0.08em' }}>CONVICTION / 100 · COHERENCE {result.coherence_pct}%</div>
        <div style={{ height: 1, background: border.subtle, margin: '1rem 0' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {([
            ['Mode', result.decision_mode],
            ['Door', result.door_class],
            // Hide entirely rather than show "—%" — an uncalculated risk reads
            // as confusing, not as "zero risk" or "not applicable."
            ...(typeof r.advisors?.bayesian_risk_pct === 'number' ? [['Bayesian risk', `${r.advisors.bayesian_risk_pct}%`]] : []),
          ] as [string, string][]).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontFamily: font.mono, fontSize: '0.7rem' }}>
              <span style={{ color: text.muted, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k}</span>
              <span style={{ color: text.secondary }}>{v}</span>
            </div>
          ))}
        </div>
      </Card>

      {result.tributaries && result.tributaries.length > 0 && (
        <Card padding="compact" style={{ padding: '1rem 1.25rem' }}>
          <TributariesStack tributaries={result.tributaries} onTributary={onTributary} />
        </Card>
      )}
    </div>
  )
}
