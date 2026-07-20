'use client'
import React from 'react'
import { font, signal } from '@/ui/tokens'

// TrueNorthPanel — underlit cyan-glass conclusion surface
export interface TrueNorthPanelProps {
  heading: React.ReactNode
  children: React.ReactNode
  footnotes?: React.ReactNode
  style?: React.CSSProperties
}

export function TrueNorthPanel({ heading, children, footnotes, style }: TrueNorthPanelProps) {
  return (
    <div style={{ position: 'relative', overflow: 'hidden', padding: '1.25rem 1.5rem', borderRadius: 6,
      border: `1px solid ${signal.cyan}42`,
      background: 'linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.14)), linear-gradient(165deg, rgba(8,58,66,.42), rgba(10,22,32,.42))',
      backdropFilter: 'blur(14px)', WebkitBackdropFilter: 'blur(14px)',
      boxShadow: 'inset 0 1px 0 rgba(120,245,255,.4), inset 0 -11px 17px -11px rgba(0,240,255,.26), 0 0 10px rgba(0,240,255,.12), 0 5px 16px rgba(0,0,0,.5)', ...style }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: '42%', background: 'linear-gradient(rgba(255,255,255,.07), rgba(255,255,255,0))', pointerEvents: 'none' }} />
      <div style={{ position: 'relative', fontFamily: font.mono, fontSize: 10, color: signal.cyan, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 10, fontWeight: 700, textShadow: `0 0 8px ${signal.cyan}66` }}>{heading}</div>
      <p style={{ position: 'relative', fontFamily: font.sans, fontSize: '1.0625rem', lineHeight: 1.6, color: '#eafcff', margin: 0, fontWeight: 500 }}>{children}</p>
      {footnotes}
    </div>
  )
}
