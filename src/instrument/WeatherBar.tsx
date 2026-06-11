'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import type { WeatherReading } from '@/ui/tokens'

// WeatherBar — underlit-LED signal strip
export interface WeatherBarProps {
  weather: WeatherReading
  delta?: number | null
  resolution?: React.ReactNode
  style?: React.CSSProperties
}

export function WeatherBar({ weather, delta, resolution, style }: WeatherBarProps) {
  const c = weather.color
  return (
    <div style={{ position: 'relative', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '11px 16px', borderRadius: 6,
      border: `1px solid ${c}3d`,
      background: `linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${c}1c, #0a1418)`,
      boxShadow: `inset 0 1px 0 ${c}66, inset 0 -9px 14px -9px ${c}40, 0 0 11px ${c}24, 0 4px 12px rgba(0,0,0,.45)`, ...style }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: '48%', background: 'linear-gradient(rgba(255,255,255,.07), rgba(255,255,255,0))', pointerEvents: 'none' }} />
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ color: c, fontWeight: 700, fontSize: 15, textShadow: `0 0 7px ${c}b3` }}>{weather.icon}</span>
        <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: '0.12em', color: c, textTransform: 'uppercase', fontWeight: 700 }}>{weather.label}</span>
      </div>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 16, fontFamily: font.mono }}>
        {delta != null && <span style={{ fontSize: 12, fontWeight: 700, color: delta >= 0 ? signal.green : signal.red }}>{delta >= 0 ? '+' : ''}{delta} NCI</span>}
        <span style={{ fontSize: 10, color: text.dimmed, letterSpacing: '0.08em' }}>{resolution}</span>
      </div>
    </div>
  )
}
