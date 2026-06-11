'use client'
import React from 'react'
import { font, signal, text } from './tokens'

// Stepped L0–L5 pipeline indicator. Ported from compass-app atoms.jsx (StepProgress).
// Reduced-motion safe via globals.css.

export interface StepProgressProps {
  labels?: string[]
  current?: number
  style?: React.CSSProperties
}

export function StepProgress({ labels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'], current = 0, style }: StepProgressProps) {
  return (
    <div style={style}>
      <div style={{ display: 'flex', gap: 5 }}>
        {labels.map((_, i) => {
          const done = i < current
          const now = i === current
          return (
            <div
              key={i}
              data-pulse={now ? '' : undefined}
              style={{
                flex: 1, height: 6, borderRadius: 3,
                background: done
                  ? `linear-gradient(90deg, #1ec3d4, ${signal.cyan})`
                  : now
                  ? `linear-gradient(90deg, #0a4a52, ${signal.cyan})`
                  : 'linear-gradient(180deg, #0a0f15, #0d141c)',
                boxShadow: done
                  ? `0 0 7px -2px ${signal.cyan}, inset 0 1px 0 rgba(255,255,255,.3)`
                  : 'inset 0 1px 2px rgba(0,0,0,.6)',
                animation: now ? 'arcs-pulse 1.1s ease-in-out infinite' : 'none',
              }}
            />
          )
        })}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: font.mono, fontSize: 8.5, color: text.muted, letterSpacing: '0.06em', marginTop: 7 }}>
        {labels.map((l, i) => (
          <span key={l} style={{ color: i === current ? signal.cyan : text.muted }}>{l}</span>
        ))}
      </div>
    </div>
  )
}
