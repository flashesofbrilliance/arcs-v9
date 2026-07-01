'use client'
import React from 'react'
import { border } from './tokens'

// Hairline divider. Ported from compass-app atoms.jsx (Rule).

export function Rule({ style }: { style?: React.CSSProperties }) {
  return <div style={{ height: 1, background: 'rgba(255,255,255,0.06)', ...style }} />
}
