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
    <div style={{ fontFamily: font.mono, fontSize: '0.65rem', letterSpacing: '0.12em', textTransform: 'uppercase', color: color || text.muted, fontWeight: 700, ...style }}>
      {children}
    </div>
  )
}
