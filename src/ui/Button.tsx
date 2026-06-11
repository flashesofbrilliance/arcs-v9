'use client'
import React from 'react'

// Cards × Badges fusion: semi-opaque dark-glass body + subtle emboss bevel; the
// gate color lives only in the accents (rim, glyph, label tint, a whisper of
// bloom). No saturated fills. Optional leading `glyph`.
// hover border (bdH) runs hotter than rest — same hue, more saturation/brightness

type Accent = { ink: string; bd: string; bdH: string; sig: string; bloom: string; bloomH: string }

const BTN_ACCENT: Record<string, Accent> = {
  primary:        { ink: '#b9e8f4', bd: '#00F0FF3a', bdH: '#00F0FF99', sig: '#00F0FF', bloom: '#00F0FF12', bloomH: '#00F0FF2b' },
  'outline-cyan': { ink: '#b9e8f4', bd: '#00F0FF3a', bdH: '#00F0FF99', sig: '#00F0FF', bloom: '#00F0FF12', bloomH: '#00F0FF2b' },
  green:          { ink: '#bdf2dc', bd: '#00FF9D3a', bdH: '#00FF9D99', sig: '#00FF9D', bloom: '#00FF9D12', bloomH: '#00FF9D2b' },
  gold:           { ink: '#f0e4ba', bd: '#FFD7003a', bdH: '#FFD70099', sig: '#FFD700', bloom: '#FFD70010', bloomH: '#FFD70026' },
  danger:         { ink: '#f6c9d2', bd: '#FF4D6D3a', bdH: '#FF4D6D99', sig: '#FF6B85', bloom: '#FF4D6D12', bloomH: '#FF4D6D2b' },
  ghost:          { ink: '#cbd5e1', bd: '#2a3647',   bdH: '#566b86',   sig: '#94a3b8', bloom: 'transparent', bloomH: 'rgba(0,0,0,.01)' },
}

const GLASS_BODY = 'linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #141c24, #0b1117)'

export type ButtonVariant = 'primary' | 'outline-cyan' | 'green' | 'gold' | 'danger' | 'ghost'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: 'sm' | 'md' | 'lg'
  glyph?: React.ReactNode
}

export function Button({ variant = 'primary', size = 'md', glyph, disabled, children, style, ...rest }: ButtonProps) {
  const [h, setH] = React.useState(false)
  const [p, setP] = React.useState(false)
  const a = BTN_ACCENT[variant] || BTN_ACCENT.primary
  const sz: React.CSSProperties =
    size === 'lg' ? { fontSize: 12, padding: '13px 23px', borderRadius: 6 }
    : size === 'sm' ? { fontSize: 10, padding: '7px 12px', borderRadius: 4 }
    : { fontSize: 11, padding: '10px 16px', borderRadius: 5 }
  const base = `inset 0 1px 0 rgba(255,255,255,.09), inset 0 -2px 7px rgba(0,0,0,.5), 0 0 14px ${a.bloom}, 0 4px 12px rgba(0,0,0,.4)`
  const hover = `inset 0 1px 0 rgba(255,255,255,.12), inset 0 -2px 7px rgba(0,0,0,.45), 0 0 20px ${a.bloomH}, 0 6px 16px rgba(0,0,0,.5)`
  const press = `inset 0 2px 6px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.05), 0 0 10px ${a.bloom}`
  const lit = !disabled && (h || p)
  return (
    <button
      disabled={disabled}
      onMouseEnter={() => setH(true)}
      onMouseLeave={() => { setH(false); setP(false) }}
      onMouseDown={() => setP(true)}
      onMouseUp={() => setP(false)}
      style={{
        position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5em',
        fontFamily: "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace", fontWeight: 600, letterSpacing: '0.085em', textTransform: 'uppercase', lineHeight: 1, whiteSpace: 'nowrap',
        color: a.ink, border: `1px solid ${lit ? a.bdH : a.bd}`, background: GLASS_BODY,
        boxShadow: disabled ? base : p ? press : h ? hover : base,
        transform: disabled ? 'none' : p ? 'translateY(1px)' : h ? 'translateY(-1px)' : 'none',
        cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.42 : 1, filter: disabled ? 'saturate(.55)' : 'none',
        transition: 'box-shadow .16s, transform .09s, border-color .16s, filter .16s', WebkitFontSmoothing: 'antialiased',
        ...sz, ...style,
      }}
      {...rest}
    >
      {glyph && <span style={{ fontSize: '1.05em', lineHeight: 1, color: a.sig }}>{glyph}</span>}
      {children}
    </button>
  )
}
