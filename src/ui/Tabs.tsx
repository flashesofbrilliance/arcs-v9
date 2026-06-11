'use client'
import React, { useState } from 'react'
import { font, signal, text } from './tokens'
import { Card } from './Card'

// Tabs — glass tab strip + carded panel (mirrors the Card sensibilities)
export interface TabItem {
  value: string
  label: string
  glyph?: React.ReactNode
  content?: React.ReactNode
}

export interface TabsProps {
  items: TabItem[]
  value?: string
  onChange?: (value: string) => void
  accent?: string
  style?: React.CSSProperties
}

export function Tabs({ items, value, onChange, accent = signal.cyan, style }: TabsProps) {
  const [internal, setInternal] = useState(items[0] && items[0].value)
  const active = value !== undefined ? value : internal
  const set = onChange || setInternal
  const cur = items.find(i => i.value === active) || items[0]
  return (
    <div style={style}>
      <div role="tablist" style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
        {items.map(it => {
          const on = it.value === active
          return (
            <button key={it.value} type="button" role="tab" aria-selected={on} onClick={() => set(it.value)} style={{
              display: 'inline-flex', alignItems: 'center', gap: 7, padding: '8px 15px', borderRadius: 10, cursor: 'pointer',
              fontFamily: font.mono, fontSize: 11, fontWeight: 700, letterSpacing: '0.085em', textTransform: 'uppercase', whiteSpace: 'nowrap',
              color: on ? '#eafcff' : text.dimmed,
              border: `1px solid ${on ? accent + '55' : '#243042'}`,
              background: on
                ? `linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${accent}1f, #0a1620)`
                : 'linear-gradient(180deg, #0c121a, #0e151e)',
              boxShadow: on
                ? `inset 0 1px 0 ${accent}73, inset 0 -8px 13px -9px ${accent}55, 0 0 11px ${accent}24, 0 4px 12px rgba(0,0,0,.42)`
                : 'inset 0 1px 0 rgba(255,255,255,.04), inset 0 2px 4px rgba(0,0,0,.5)',
              transform: on ? 'translateY(-1px)' : 'none', transition: 'color .16s, border-color .16s, box-shadow .16s, transform .12s',
            }}>
              {it.glyph && <span style={{ fontSize: '1.05em', color: on ? accent : text.muted }}>{it.glyph}</span>}{it.label}
            </button>
          )
        })}
      </div>
      <Card accent={accent}>{cur && cur.content}</Card>
    </div>
  )
}
