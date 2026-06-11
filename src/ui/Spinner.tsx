'use client'
import React from 'react'
import { signal } from './tokens'

// Ported from compass-app atoms.jsx (Spinner). Reduced-motion safe via globals.css.

export interface SpinnerProps {
  size?: number
  width?: number
  color?: string
  style?: React.CSSProperties
}

export function Spinner({ size = 20, width, color = signal.cyan, style }: SpinnerProps) {
  const bw = width || (size >= 28 ? 3 : 2)
  return (
    <div
      data-spin
      style={{
        width: size, height: size, borderRadius: '50%',
        border: `${bw}px solid #1c2736`, borderTopColor: color,
        boxShadow: `0 0 7px -2px ${color}, inset 0 0 4px rgba(0,0,0,.6)`,
        animation: 'arcs-spin .8s linear infinite',
        ...style,
      }}
    />
  )
}
