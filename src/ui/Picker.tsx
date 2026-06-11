'use client'
import React, { useState } from 'react'
import { font, text } from './tokens'

// Picker — instrument dropdown (matches the Observatory control grammar)
export interface PickerOption {
  value: string
  label: string
}

export interface PickerProps {
  label?: string
  value: string
  options: PickerOption[]
  onChange: (value: string) => void
  style?: React.CSSProperties
}

export function Picker({ label, value, options, onChange, style }: PickerProps) {
  const [open, setOpen] = useState(false)
  const [h, setH] = useState(false)
  const ref = React.useRef<HTMLDivElement>(null)
  React.useEffect(() => {
    if (!open) return
    const close = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])
  const current = options.find(o => o.value === value) || options[0]
  return (
    <div ref={ref} style={{ position: 'relative', borderRadius: 6, padding: '12px 14px 13px',
      border: '1px solid #2a3647',
      background: 'linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)',
      boxShadow: 'inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)', ...style }}>
      {label && <span style={{ display: 'block', fontFamily: font.mono, fontSize: 11, color: text.secondary, textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700, marginBottom: 8 }}>{label}</span>}
      <button type="button" onClick={() => setOpen(o => !o)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, width: '100%', padding: '10px 12px', borderRadius: 5, cursor: 'pointer',
          border: `1px solid ${open ? '#00F0FF66' : (h ? '#34435a' : '#1c2736')}`, color: text.primary, fontFamily: font.sans, fontSize: 14,
          background: 'linear-gradient(180deg, #090d12, #0c1219)',
          boxShadow: 'inset 0 2px 5px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)', transition: 'border-color .16s' }}>
        <span>{current.label}</span>
        <span style={{ color: text.dimmed, fontSize: 10, transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }}>▾</span>
      </button>
      {open && (
        <div style={{ position: 'absolute', left: 14, right: 14, top: 'calc(100% - 4px)', zIndex: 30, padding: 4, borderRadius: 8, overflow: 'hidden',
          border: '1px solid #00F0FF44', background: 'linear-gradient(180deg, #0e151e, #0a0f16)', boxShadow: '0 16px 34px -14px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.05)' }}>
          {options.map(o => {
            const sel = o.value === value
            return (
              <button key={o.value} type="button" onClick={() => { onChange(o.value); setOpen(false) }}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', padding: '8px 10px', borderRadius: 5, cursor: 'pointer',
                  border: '1px solid transparent', textAlign: 'left', fontFamily: font.sans, fontSize: 13.5,
                  color: sel ? '#b9e8f4' : text.primary, background: sel ? 'linear-gradient(180deg, #00F0FF1c, #00F0FF08)' : 'transparent' }}
                onMouseEnter={e => { if (!sel) e.currentTarget.style.background = 'rgba(255,255,255,.04)' }}
                onMouseLeave={e => { if (!sel) e.currentTarget.style.background = 'transparent' }}>
                {o.label}{sel && <span style={{ color: '#00F0FF', fontSize: 10 }}>●</span>}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
