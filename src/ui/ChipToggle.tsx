'use client'
import React, { useState } from 'react'
import { font, signal, text } from './tokens'

// ChipToggle — depressed-into-surface well; selected lights a signal LED
export interface ChipToggleProps {
  label: string
  glyph?: React.ReactNode
  selected?: boolean
  onClick?: () => void
  accent?: string
  style?: React.CSSProperties
}

export function ChipToggle({ label, glyph = '▲', selected, onClick, accent = signal.green, style }: ChipToggleProps) {
  const [h, setH] = useState(false)
  return (
    <button type="button" onClick={onClick} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      position: 'relative', display: 'inline-flex', alignItems: 'center', gap: 6, overflow: 'hidden',
      padding: '8px 14px', fontSize: 12, borderRadius: 5, cursor: 'pointer', lineHeight: 1,
      fontFamily: font.mono, fontWeight: 600, letterSpacing: '0.04em',
      color: selected ? '#bdf2dc' : (h ? text.primary : text.dimmed),
      border: `1px solid ${selected ? accent + '55' : (h ? '#34435a' : '#232f3e')}`,
      background: selected ? 'linear-gradient(180deg, #0b1318, #0c1620)' : 'linear-gradient(180deg, #0c121a, #0e151e)',
      boxShadow: selected ? `inset 0 2px 5px rgba(0,0,0,.55), inset 0 -8px 12px -7px ${accent}40, inset 0 0 0 1px ${accent}14`
        : `inset 0 2px 4px rgba(0,0,0,.55), inset 0 -1px 0 rgba(255,255,255,${h ? '.05' : '.04'})`,
      transition: 'box-shadow .16s, border-color .16s, color .16s', ...style,
    }}>
      {selected && <span style={{ color: accent, fontSize: '1.05em', lineHeight: 1 }}>{glyph}</span>}{label}
    </button>
  )
}
