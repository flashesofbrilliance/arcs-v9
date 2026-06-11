'use client'
import React from 'react'
import { signal } from './tokens'

// Ported from compass-app atoms.jsx (ProgressBar). Reduced-motion safe via globals.css.

export interface ProgressBarProps {
  value?: number
  height?: number
  indeterminate?: boolean
  color?: string
  style?: React.CSSProperties
}

export function ProgressBar({ value = 0, height = 6, indeterminate, color = signal.cyan, style }: ProgressBarProps) {
  return (
    <div
      style={{
        width: '100%', height, borderRadius: 999, overflow: 'hidden', position: 'relative',
        background: 'linear-gradient(180deg, #090d12, #0c1219)',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)',
        ...style,
      }}
    >
      {indeterminate ? (
        <div
          data-indet
          style={{
            position: 'absolute', top: 0, bottom: 0, width: '34%', borderRadius: 999,
            background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
            boxShadow: `0 0 9px -1px ${color}`,
            animation: 'arcs-indet 1.35s cubic-bezier(0.4,0,0.2,1) infinite',
          }}
        />
      ) : (
        <div
          style={{
            height: '100%', width: `${Math.max(0, Math.min(100, value))}%`, borderRadius: 999, position: 'relative',
            background: `linear-gradient(90deg, #1ec3d4, ${color})`,
            boxShadow: `0 0 8px -1px ${color}, inset 0 1px 0 rgba(255,255,255,.35)`,
            transition: 'width .3s ease',
          }}
        >
          <div
            data-shimmer
            style={{
              position: 'absolute', inset: 0, borderRadius: 999,
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,.4), transparent)',
              transform: 'translateX(-100%)',
              animation: 'arcs-shimmer 1.6s ease-in-out infinite',
            }}
          />
        </div>
      )}
    </div>
  )
}
