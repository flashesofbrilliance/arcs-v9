'use client'
import React from 'react'
import { font, signal, text } from './tokens'

// Swiss scaffolding label — optional cyan index + mono uppercase title.
// Ported from compass-app atoms.jsx (SectionLabel).

export interface SectionLabelProps {
  index?: string
  children: React.ReactNode
  color?: string
  style?: React.CSSProperties
}

export function SectionLabel({ index, children, color = text.muted, style }: SectionLabelProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, ...style }}>
      {index && (
        <span style={{ fontFamily: font.mono, ...font.tier.t1, color: signal.cyan }}>
          {index}
        </span>
      )}
      <span style={{ fontFamily: font.mono, ...font.tier.t2, textTransform: 'uppercase', color }}>
        {children}
      </span>
    </div>
  )
}
