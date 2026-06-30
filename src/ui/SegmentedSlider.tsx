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
  return (
    <div style={{
      position: 'relative', display: 'grid',
      gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))`,
      padding: 4, borderRadius: 6,
      background: 'linear-gradient(180deg, #090d12, #0c1219)',
      boxShadow: 'inset 0 2px 6px rgba(0,0,0,.7), inset 0 -1px 0 rgba(255,255,255,.04)',
      ...style,
    }}>
      {/* Sliding thumb */}
      <div style={{
        position: 'absolute', top: 4, bottom: 4, left: 4,
        width: `calc((100% - 8px) / ${options.length})`,
        borderRadius: 4,
        transform: `translateX(${idx * 100}%)`,
        transition: 'transform .22s cubic-bezier(.4,0,.2,1), border-color .18s, box-shadow .18s',
        border: `1px solid ${a.bd}`,
        background: 'linear-gradient(180deg, #131c28, #0f1822)',
        boxShadow: `inset 0 1px 3px rgba(0,0,0,.4), inset 0 -5px 10px -6px ${a.bloom2}, 0 1px 0 rgba(255,255,255,.05)`,
      }} />
      {options.map((o, i) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          style={{
            position: 'relative', zIndex: 1,
            minWidth: 0, background: 'transparent', border: 'none',
            padding: '8px 2px', cursor: 'pointer',
            fontFamily: font.mono, fontWeight: 700,
            fontSize: 10, letterSpacing: '0.03em',
            textAlign: 'center',
            color: i === idx ? a.ink : text.dimmed,
            transition: 'color .16s',
            whiteSpace: 'nowrap',
          }}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}
