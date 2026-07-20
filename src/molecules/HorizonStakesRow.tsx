'use client'
import React from 'react'
import { font, text } from '@/ui/tokens'
import { Picker } from '@/ui/Picker'
import { SegmentedSlider } from '@/ui/SegmentedSlider'

// HorizonStakesRow — Picker (Horizon) + SegmentedSlider (Stakes) in a bezel.
// Source: Compass.jsx. Stateful form molecule: takes value + onChange props.

const HORIZON_OPTS = [
  { value: 'TODAY', label: 'Today' },
  { value: 'THIS_WEEK', label: 'This week' },
  { value: 'THIS_QUARTER', label: 'This quarter' },
  { value: 'ONE_TO_THREE_YEARS', label: '1 to 3 years' },
]

const STAKE_OPTS = [
  { value: 'LOW', label: 'Low', accent: 'green' as const },
  { value: 'MEDIUM', label: 'Medium', accent: 'gold' as const },
  { value: 'HIGH', label: 'High', accent: 'red' as const },
]

export interface HorizonStakesRowProps {
  horizon: string
  stakes: string
  onHorizonChange: (value: string) => void
  onStakesChange: (value: string) => void
}

export function HorizonStakesRow({ horizon, stakes, onHorizonChange, onStakesChange }: HorizonStakesRowProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Horizon — thin picker on top */}
      <Picker label="Horizon" value={horizon} onChange={onHorizonChange} options={HORIZON_OPTS} style={{ padding: '8px 10px' }} />

      {/* Stakes — full-width bezel below */}
      <div style={{ position: 'relative', borderRadius: 6, padding: '12px 14px 13px',
        border: '1px solid #2a3647',
        background: 'linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)' }}>
        <span style={{ display: 'block', fontFamily: font.mono, fontSize: 11, color: text.secondary, textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700, marginBottom: 8 }}>Stakes</span>
        <SegmentedSlider options={STAKE_OPTS} value={stakes} onChange={onStakesChange} />
      </div>
    </div>
  )
}
