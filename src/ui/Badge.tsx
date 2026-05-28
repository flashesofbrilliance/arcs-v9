'use client'
import React from 'react'
import { font, radius, signal } from './tokens'

// Register controls visual weight:
//   cockpit    — prominent, sm text, used in dashboard instrument panels
//   governance — bold, mono, bordered pill; used in ADR/receipt headers
//   light      — quiet, xs text, minimal border; default for metadata labels

export type Register = 'cockpit' | 'governance' | 'light'

export interface BadgeProps {
  label: string
  color?: string
  register?: Register
  style?: React.CSSProperties
}

export function Badge({ label, color = signal.steel, register = 'light', style }: BadgeProps) {
  const base: React.CSSProperties = {
    display:     'inline-flex',
    alignItems:  'center',
    whiteSpace:  'nowrap',
    lineHeight:  1.4,
    fontFamily:  font.mono,
    fontWeight:  font.weight.medium,
  }

  const variant: React.CSSProperties =
    register === 'governance'
      ? {
          fontSize:      font.size.sm,
          letterSpacing: font.tracking.widest,
          padding:       '3px 12px',
          borderRadius:  radius.md,
          background:    `${color}18`,
          border:        `1px solid ${color}50`,
          color,
        }
      : register === 'cockpit'
      ? {
          fontSize:      font.size.sm,
          letterSpacing: font.tracking.wider,
          padding:       '2px 10px',
          borderRadius:  radius.sm,
          background:    `${color}20`,
          border:        `1px solid ${color}60`,
          color,
        }
      : /* light */ {
          fontSize:      font.size.xs,
          letterSpacing: font.tracking.wide,
          padding:       '1px 8px',
          borderRadius:  radius.sm,
          background:    'transparent',
          border:        `1px solid ${color}40`,
          color,
          opacity:       0.85,
        }

  return <span style={{ ...base, ...variant, ...style }}>{label}</span>
}
