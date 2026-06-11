'use client'
import React from 'react'
import { T } from '../tokens'

export interface SidelineItem {
  label?: string
  title: string
  body: string
  note?: string
  accent?: string
}

export interface SidelineListProps {
  items: SidelineItem[]
}

export function SidelineList({ items }: SidelineListProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {items.map((item, i) => (
        <div key={i} style={{ padding: '14px 18px', borderRadius: 8, background: T.surface, border: `1px solid ${T.border}`, borderLeft: `3px solid ${item.accent || T.cyan}` }}>
          {item.label && <div style={{ fontFamily: T.mono, fontSize: 9, color: item.accent || T.cyan, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 5 }}>{item.label}</div>}
          <div style={{ fontFamily: T.sans, fontSize: 15, fontWeight: 600, color: T.fg1, marginBottom: 6, letterSpacing: '-0.01em' }}>{item.title}</div>
          <p style={{ fontFamily: T.sans, fontSize: 14, color: T.fg2, lineHeight: 1.65 }}>{item.body}</p>
          {item.note && <div style={{ marginTop: 8, fontFamily: T.mono, fontSize: 11, color: item.accent || T.cyan, letterSpacing: '0.04em', opacity: 0.8 }}>{item.note}</div>}
        </div>
      ))}
    </div>
  )
}
