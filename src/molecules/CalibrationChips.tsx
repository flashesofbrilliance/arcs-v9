'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { SectionLabel } from '@/ui/SectionLabel'
import { ChipToggle } from '@/ui/ChipToggle'

// CalibrationChips — SectionLabel + ChipToggle ×6 (max 2 selected).
// Source: Compass.jsx. Stateful form molecule: takes value + onChange props.

const PROTECTION = ['Cash', 'Time', 'Reputation', 'Relationship', 'Health', 'Optionality']

export interface CalibrationChipsProps {
  selected: string[]
  onToggle: (chip: string) => void
}

export function CalibrationChips({ selected, onToggle }: CalibrationChipsProps) {
  return (
    <div>
      <SectionLabel index="02" color={signal.gold} style={{ marginBottom: '0.75rem' }}>Calibrate · optional</SectionLabel>
      <div style={{ fontFamily: font.mono, fontSize: 10, color: text.muted, letterSpacing: '0.06em', marginBottom: '0.6rem' }}>What can&apos;t you afford to lose? · pick up to 2</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
        {PROTECTION.map(c => (
          <ChipToggle key={c} label={c} selected={selected.includes(c)} onClick={() => onToggle(c)} style={{ width: '100%', justifyContent: 'center' }} />
        ))}
      </div>
    </div>
  )
}
