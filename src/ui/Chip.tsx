import React from 'react'
import { font, signal } from './tokens'

// Chip — static tag/category pill. Distinct from ChipToggle (interactive selector):
// Chip has no click state, no hover, no selection — it's a label, not a control.
// Use for macro_tags, decision_mode/door_class readouts, weather/mode badges.
//
// filled=false (default): tinted glass — color-tinted background + border, color text.
// filled=true: solid fill — color background, dark (#020408) text. Use for the single
// "primary" chip in a row (e.g. the active Y-state) to draw the eye before the rest.

export interface ChipProps {
  label: string
  color?: string
  filled?: boolean
  style?: React.CSSProperties
}

export function Chip({ label, color = signal.steel, filled = false, style }: ChipProps) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        height: 22,
        padding: '0 10px',
        borderRadius: 4,
        fontFamily: font.mono,
        fontSize: 10,
        fontWeight: 700,
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        lineHeight: 1,
        whiteSpace: 'nowrap',
        color: filled ? '#020408' : color,
        background: filled ? color : `${color}16`,
        border: filled ? 'none' : `1px solid ${color}35`,
        ...style,
      }}
    >
      {label}
    </span>
  )
}
