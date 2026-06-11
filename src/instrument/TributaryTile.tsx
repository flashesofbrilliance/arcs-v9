'use client'
import React, { useState } from 'react'
import { font, text } from '@/ui/tokens'

// TributaryTile — glass tile, lifts to full opacity + underlit on hover
export interface TributaryTileProps {
  label: string
  color: string
  glyph?: React.ReactNode
  onClick?: () => void
  children?: React.ReactNode
}

export function TributaryTile({ label, glyph, color, children, onClick }: TributaryTileProps) {
  const [h, setH] = useState(false)
  return (
    <button onClick={onClick} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      position: 'relative', overflow: 'hidden', width: '100%', boxSizing: 'border-box', padding: '12px 16px', borderRadius: 5, textAlign: 'left', cursor: 'pointer',
      display: 'flex', flexDirection: 'column', gap: 4, opacity: h ? 1 : 0.82,
      border: `1px solid ${color}${h ? '55' : '2e'}`,
      background: 'linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0b1117)',
      boxShadow: h ? `inset 0 1px 0 rgba(255,255,255,.08), inset 0 -8px 14px -8px ${color}40, 0 0 12px ${color}1e, 0 5px 14px rgba(0,0,0,.42)` : 'inset 0 1px 0 rgba(255,255,255,.05), 0 2px 7px rgba(0,0,0,.35)',
      transform: h ? 'translateY(-1px)' : 'none', transition: 'all .16s',
    }}>
      <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, color, display: 'flex', alignItems: 'center', gap: 6 }}>{glyph && <span>{glyph}</span>}{label}</span>
      <span style={{ fontFamily: font.sans, fontSize: 13, color: text.secondary, lineHeight: 1.5 }}>{children}</span>
    </button>
  )
}
