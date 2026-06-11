'use client'
import React from 'react'
import { font, text } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import type { FatedDecomposition } from '@/lib/mockCompass'

// FatedGrid — Card wrapping the FATED decomposition rows. Source: Brief.jsx.
export interface FatedGridProps {
  fated: Partial<FatedDecomposition>
}

export function FatedGrid({ fated }: FatedGridProps) {
  const FATED_ORDER: [string, string | undefined][] = [
    ['Facts', fated.facts], ['Assumptions', fated.assumptions],
    ['Tradeoffs', fated.tradeoffs], ['Emotions', fated.emotions], ['Direction', fated.direction],
  ]
  return (
    <Card>
      <Label style={{ marginBottom: '1rem' }}>FATED Decomposition</Label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {FATED_ORDER.map(([k, v]) => (
          <div key={k} style={{ display: 'grid', gridTemplateColumns: '92px 1fr', gap: '0.75rem', alignItems: 'baseline' }}>
            <span style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted }}>{k}</span>
            <span style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.secondary, lineHeight: 1.55 }}>{v}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
