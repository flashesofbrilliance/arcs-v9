'use client'
import React from 'react'
import { font, signal } from './tokens'

// Register controls visual treatment:
//   state      — kit default: Y-gate weather DNA; signal-tinted glass capsule with bloom + emboss
//   governance — bold, mono, bordered pill; used in ADR/receipt headers
//   light      — quiet, xs text, minimal border; default for metadata labels
//   cockpit    — alias preserved for legacy callers; renders the 'state' treatment

export type Register = 'state' | 'governance' | 'light' | 'cockpit'

export interface BadgeProps {
  label: string
  glyph?: React.ReactNode
  color?: string
  register?: Register
  style?: React.CSSProperties
}

export function Badge({ label, glyph, color = signal.steel, register = 'state', style }: BadgeProps) {
  const common: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    fontFamily: font.mono,
    fontWeight: 700,
    whiteSpace: 'nowrap',
    lineHeight: 1,
    textTransform: 'uppercase',
    color,
  }

  const v: React.CSSProperties =
    register === 'governance'
      ? { fontSize: 11, letterSpacing: '0.12em', padding: '4px 11px', borderRadius: 7, background: `${color}1f`, border: `1px solid ${color}55` }
      : register === 'light'
      ? { fontSize: 10, fontWeight: 500, letterSpacing: '0.06em', padding: '2px 9px', borderRadius: 6, background: 'transparent', border: `1px solid ${color}40`, opacity: 0.92 }
      : /* state (also: cockpit alias) */
        { fontSize: 11, letterSpacing: '0.11em', padding: '6px 12px', borderRadius: 8, background: `linear-gradient(165deg, ${color}2e, ${color}0f)`, border: `1px solid ${color}45`, boxShadow: `inset 0 1px 0 rgba(255,255,255,.05), 0 0 8px ${color}26` }

  return (
    <span style={{ ...common, ...v, ...style }}>
      {glyph && <span style={{ fontSize: '1.05em', lineHeight: 1 }}>{glyph}</span>}
      {label}
    </span>
  )
}
