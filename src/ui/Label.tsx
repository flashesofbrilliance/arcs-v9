'use client'
import React from 'react'
import { font, text } from './tokens'

export interface LabelProps {
  children: React.ReactNode
  color?: string
  style?: React.CSSProperties
}

export function Label({ children, color, style }: LabelProps) {
  return (
    <div style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: color || text.muted, ...style }}>
      {children}
    </div>
  )
}
