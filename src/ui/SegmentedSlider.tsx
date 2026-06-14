'use client'
import React from 'react'
import { font, text } from './tokens'

// Sliding segmented control — thumb slides, signal follows position
type SegAccent = { bd: string; bloom: string; bloom2: string; ink: string }

const SEG_ACCENT: Record<string, SegAccent> = {
  green: { bd: '#00FF9D55', bloom: '#00FF9D1c', bloom2: '#00FF9D33', ink: '#bdf2dc' },
  gold:  { bd: '#FFD70055', bloom: '#FFD70016', bloom2: '#FFD7002b', ink: '#f0e4ba' },
  red:   { bd: '#FF4D6D55', bloom: '#FF4D6D1c', bloom2: '#FF4D6D33', ink: '#f6c9d2' },
  cyan:  { bd: '#00F0FF55', bloom: '#00F0FF1c', bloom2: '#00F0FF2b', ink: '#b9e8f4' },
}

export interface SegmentedOption {
  value: string
  label: string
  accent?: 'green' | 'gold' | 'red' | 'cyan'
}

export interface SegmentedSliderProps {
  options: SegmentedOption[]
  value: string
  onChange: (value: string) => void
  style?: React.CSSProperties
}

export function SegmentedSlider({ options, value, onChange, style }: SegmentedSliderProps) {
  const idx = Math.max(0, options.findIndex(o => o.value === value))
  const a = SEG_ACCENT[options[idx]?.accent ?? 'cyan'] || SEG_ACCENT.cyan
  // Fit the label to its cell: 1cqi = 1% of the control's width, each cell is
  // (100/n)% wide, and a mono glyph advances ~0.62em. So this coefficient sizes
  // the longest label to just fill its cell — then clamp caps it at 12px and
  // floors it so it never overflows the segment (was a hard 12px → clipped text).
  const maxLen = Math.max(1, ...options.map(o => o.label.length))
  const fitCqi = ((100 / options.length) / (maxLen * 0.62)).toFixed(2)
  return (
    <div style={{ position: 'relative', display: 'grid', gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))`, padding: 5, borderRadius: 6, containerType: 'inline-size',
      background: 'linear-gradient(180deg, #090d12, #0c1219)',
      boxShadow: 'inset 0 2px 6px rgba(0,0,0,.7), inset 0 -1px 0 rgba(255,255,255,.04)', ...style }}>
      <div style={{ position: 'absolute', top: 5, bottom: 5, left: 5, width: `calc((100% - 10px) / ${options.length})`, borderRadius: 4,
        transform: `translateX(${idx * 100}%)`, transition: 'transform .24s cubic-bezier(.4,0,.2,1), border-color .2s, box-shadow .2s',
        border: `1px solid ${a.bd}`,
        background: 'linear-gradient(180deg, #0d141c, #0f1822)',
        boxShadow: `inset 0 2px 4px rgba(0,0,0,.5), inset 0 -7px 11px -7px ${a.bloom2}, inset 0 0 0 1px rgba(255,255,255,.03)` }} />
      {options.map((o, i) => (
        <button key={o.value} type="button" onClick={() => onChange(o.value)} style={{ position: 'relative', zIndex: 1, minWidth: 0, background: 'transparent', border: 'none', padding: '9px 4px', cursor: 'pointer', whiteSpace: 'nowrap',
          fontFamily: font.mono, fontWeight: 700, fontSize: `clamp(8px, ${fitCqi}cqi, 12px)`, letterSpacing: '0.02em', color: i === idx ? a.ink : text.dimmed, transition: 'color .18s' }}>{o.label}</button>
      ))}
    </div>
  )
}
