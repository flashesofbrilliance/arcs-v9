'use client'
import React from 'react'
import { T } from '../tokens'

export interface TwoColumnPanel {
  heading?: string
  body?: string
  items?: string[]
  note?: string
}

export interface TwoColumnProps {
  left: TwoColumnPanel
  right: TwoColumnPanel
  accent?: string
}

export function TwoColumn({ left, right, accent = T.cyan }: TwoColumnProps) {
  const panel = (p: TwoColumnPanel, dark: boolean) => (
    <div style={{ flex: 1, padding: '18px 20px', borderRadius: 10, background: dark ? '#070b10' : T.surface, border: `1px solid ${T.border}` }}>
      {p.heading && <div style={{ fontFamily: T.sans, fontSize: 14, fontWeight: 600, color: T.fg1, marginBottom: 10 }}>{p.heading}</div>}
      {p.body && <p style={{ fontFamily: T.sans, fontSize: 14, color: T.fg2, lineHeight: 1.65, marginBottom: p.items ? 10 : 0 }}>{p.body}</p>}
      {p.items && <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 7 }}>
        {p.items.map((it, i) => (
          <li key={i} style={{ fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.6, display: 'flex', gap: 8 }}>
            <span style={{ color: T.fg4, flexShrink: 0 }}>—</span>
            <span dangerouslySetInnerHTML={{ __html: it }} />
          </li>
        ))}
      </ul>}
      {p.note && <div style={{ marginTop: 12, padding: '9px 12px', borderRadius: 6, background: `${accent}0d`, border: `1px solid ${accent}22`, fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.6 }}>{p.note}</div>}
    </div>
  )
  return <div style={{ display: 'flex', gap: 12 }}>{panel(left, true)}{panel(right, false)}</div>
}
