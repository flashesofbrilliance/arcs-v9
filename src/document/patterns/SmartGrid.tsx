'use client'
import React from 'react'
import { T } from '../tokens'

export interface SmartGridItem {
  label?: string
  title: string
  body: string
  color?: string
}

export interface SmartGridProps {
  items: SmartGridItem[]
  cols?: number
}

export function SmartGrid({ items, cols = 2 }: SmartGridProps) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols},1fr)`, gap: 10 }}>
      {items.map((item, i) => (
        <div key={i} style={{ padding: '16px 18px', borderRadius: 10, background: T.surface, border: `1px solid ${T.border}` }}>
          {item.label && <div style={{ fontFamily: T.mono, fontSize: 9, color: item.color || T.fg4, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 5 }}>{item.label}</div>}
          <div style={{ fontFamily: T.sans, fontSize: 14, fontWeight: 600, color: T.fg1, marginBottom: 6 }}>{item.title}</div>
          <p style={{ fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.6 }}>{item.body}</p>
        </div>
      ))}
    </div>
  )
}
