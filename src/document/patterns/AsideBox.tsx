'use client'
import React from 'react'
import { T } from '../tokens'

export type AsideVariant = 'info' | 'caution' | 'success' | 'warning'

export interface AsideBoxProps {
  variant?: AsideVariant
  label?: string
  children: React.ReactNode
}

const ASIDE: Record<AsideVariant, { color: string; bg: string; label: string }> = {
  info: { color: '#7AD2FF', bg: 'rgba(122,210,255,0.08)', label: 'INFO' },
  caution: { color: T.gold, bg: 'rgba(255,215,0,0.08)', label: 'CAUTION' },
  success: { color: T.green, bg: 'rgba(0,255,157,0.08)', label: 'VALIDATED' },
  warning: { color: T.red, bg: 'rgba(255,77,109,0.08)', label: 'WARNING' },
}

export function AsideBox({ variant = 'info', label, children }: AsideBoxProps) {
  const c = ASIDE[variant]
  return (
    <div style={{ padding: '11px 15px', borderRadius: 8, background: c.bg, border: `1px solid ${c.color}28` }}>
      <div style={{ fontFamily: T.mono, fontSize: 9, color: c.color, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 6 }}>{label || c.label}</div>
      <p style={{ fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.65 }}>{children}</p>
    </div>
  )
}
