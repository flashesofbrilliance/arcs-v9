'use client'
import React, { useState } from 'react'
import { font, text } from './tokens'

// Field — instrument input module (bezel + recessed screen + cyan focus)
export interface FieldProps {
  label?: string
  as?: 'input' | 'textarea' | 'select'
  value?: string
  onChange?: React.ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  placeholder?: string
  rows?: number
  children?: React.ReactNode
  style?: React.CSSProperties
  fieldStyle?: React.CSSProperties
}

export function Field({ label, as = 'input', value, onChange, placeholder, rows, children, style, fieldStyle }: FieldProps) {
  const [f, setF] = useState(false)
  const isSelect = as === 'select'
  const glow = f && !isSelect // horizon (select) gets a clean focus line, no glow
  const well: React.CSSProperties = {
    width: '100%', boxSizing: 'border-box', color: text.primary, fontSize: 14, padding: '10px 12px', outline: 'none', fontFamily: font.sans,
    borderRadius: 5, border: `1px solid ${f ? (isSelect ? '#3a4a5e' : '#00F0FF66') : '#1c2736'}`,
    background: 'linear-gradient(180deg, #090d12, #0c1219)',
    boxShadow: glow ? 'inset 0 2px 5px rgba(0,0,0,.55), inset 0 -9px 14px -9px rgba(0,240,255,.34), 0 0 0 1px #00F0FF3a'
                    : 'inset 0 2px 5px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)',
    transition: 'box-shadow .16s, border-color .16s',
    resize: as === 'textarea' ? 'vertical' : undefined, lineHeight: as === 'textarea' ? 1.6 : undefined,
    ...fieldStyle,
  }
  const onFocus = () => setF(true)
  const onBlur = () => setF(false)
  return (
    <div style={{ position: 'relative', borderRadius: 6, padding: '12px 14px 13px', overflow: 'hidden',
      border: '1px solid #2a3647',
      background: 'linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)',
      boxShadow: 'inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)', ...style }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: '34%', background: 'linear-gradient(rgba(255,255,255,.05), rgba(255,255,255,0))', pointerEvents: 'none' }} />
      {label && <span style={{ position: 'relative', display: 'block', fontFamily: font.mono, fontSize: 11, color: text.secondary, textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700, marginBottom: 8 }}>{label}</span>}
      {as === 'textarea'
        ? <textarea rows={rows || 3} value={value} onChange={onChange as React.ChangeEventHandler<HTMLTextAreaElement>} placeholder={placeholder} onFocus={onFocus} onBlur={onBlur} style={well} />
        : as === 'select'
        ? <select value={value} onChange={onChange as React.ChangeEventHandler<HTMLSelectElement>} onFocus={onFocus} onBlur={onBlur} style={well}>{children}</select>
        : <input type="text" value={value} onChange={onChange as React.ChangeEventHandler<HTMLInputElement>} placeholder={placeholder} onFocus={onFocus} onBlur={onBlur} style={well} />}
    </div>
  )
}
