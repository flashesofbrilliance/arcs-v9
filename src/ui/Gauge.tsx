'use client'
import React from 'react'
import { font, text } from './tokens'

// Instrument readout: raised glass bezel around a recessed optical "screen".
// The signature ARCS hardware tile (NCI / Coherence / Satoshi). Pass `accent`
// for a signal-tinted bezel; `children` to fill the body (e.g. macro-tag pills).
export interface GaugeProps {
  label: string
  value?: React.ReactNode
  sub?: React.ReactNode
  color?: string
  glow?: string
  accent?: string
  valueSize?: number
  flex?: React.CSSProperties['flex']
  minWidth?: number
  children?: React.ReactNode
  style?: React.CSSProperties
}

export function Gauge({
  label,
  value,
  sub,
  color = '#cdd7e3',
  glow = 'rgba(160,180,210,.35)',
  accent,
  valueSize = 33,
  flex = 1,
  minWidth = 120,
  children,
  style,
}: GaugeProps) {
  const bezel: React.CSSProperties = accent
    ? {
        border: `1px solid ${accent}40`,
        boxShadow: `inset 0 1px 0 ${accent}73, inset 0 -2px 6px rgba(0,0,0,.55), 0 0 14px ${accent}2e, 0 5px 14px rgba(0,0,0,.5)`,
      }
    : {
        border: '1px solid #2a3647',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), inset 0 0 0 1px rgba(255,255,255,.02), 0 5px 14px rgba(0,0,0,.5)',
      }
  return (
    <div style={{ position: 'relative', flex, minWidth, padding: '15px 16px 14px', borderRadius: 6, overflow: 'hidden',
      background: 'linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)',
      ...bezel, ...style }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: '40%', background: 'linear-gradient(rgba(255,255,255,.06), rgba(255,255,255,0))', pointerEvents: 'none' }} />
      <div style={{ position: 'relative', fontFamily: font.mono, fontSize: 10, color: accent || text.muted, letterSpacing: '.1em', textTransform: 'uppercase', fontWeight: 700 }}>{label}</div>
      {value !== undefined && value !== null && (
        <div style={{ position: 'relative', marginTop: 4, borderRadius: 8, padding: '4px 2px',
          boxShadow: 'inset 0 2px 5px rgba(0,0,0,.6), inset 0 -1px 0 rgba(255,255,255,.05)' }}>
          <div style={{ position: 'relative', fontSize: valueSize, fontWeight: 700, lineHeight: 1, color, textShadow: `0 0 16px ${glow}` }}>{value}</div>
        </div>
      )}
      {sub && <div style={{ position: 'relative', fontSize: 11, color: text.muted, marginTop: 4 }}>{sub}</div>}
      {children}
    </div>
  )
}
