'use client'
import React from 'react'
import { font, text } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import type { FatedDecomposition } from '@/lib/mockCompass'

// Each FATED axis has a dedicated signal color for scannability.
const FATED_COLORS: Record<string, string> = {
  Facts:       '#00F0FF', // cyan
  Assumptions: '#FFD700', // gold
  Tradeoffs:   '#FF4D6D', // red
  Emotions:    '#00FF9D', // green
  Direction:   '#94A3B8', // steel
}

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
        {FATED_ORDER.map(([k, v]) => {
          const color = FATED_COLORS[k] ?? text.muted
          return (
            <div key={k} style={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: '0.75rem', alignItems: 'baseline' }}>
              <span style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.1em', textTransform: 'uppercase', color, textShadow: `0 0 8px ${color}44` }}>{k}</span>
              <span style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.secondary, lineHeight: 1.55 }}>{v}</span>
            </div>
          )
        })}
      </div>
    </Card>
  )
}
