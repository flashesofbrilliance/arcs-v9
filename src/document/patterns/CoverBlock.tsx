'use client'
import React from 'react'
import { T } from '../tokens'
import { Pill } from '../primitives'

export interface CoverBlockProps {
  badges?: string[]
  title: React.ReactNode
  subtitle?: React.ReactNode
  meta?: React.ReactNode
  actions?: string[]
  accent?: string
}

export function CoverBlock({ badges = [], title, subtitle, meta, actions = [], accent = T.cyan }: CoverBlockProps) {
  return (
    <div style={{ padding: '36px 0 32px', borderBottom: `1px solid ${T.border}` }}>
      {badges.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          {badges.map((b, i) => <Pill key={i} accent={accent} solid={i === 0}>{b}</Pill>)}
        </div>
      )}
      <h1 style={{ fontFamily: T.sans, fontSize: 28, fontWeight: 600, color: T.fg1, letterSpacing: '-0.02em', lineHeight: 1.2, marginBottom: 12 }}>{title}</h1>
      {subtitle && <p style={{ fontFamily: T.sans, fontSize: 15, color: T.fg2, lineHeight: 1.7, marginBottom: 16, maxWidth: 640 }}>{subtitle}</p>}
      {meta && <div style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 16 }}>{meta}</div>}
      {actions.length > 0 && (
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {actions.map((a, i) => (
            <button key={i} style={{ height: 38, padding: '0 18px', borderRadius: 7, cursor: 'pointer', fontFamily: T.sans, fontSize: 13, fontWeight: 500,
              background: i === 0 ? accent : 'transparent', color: i === 0 ? T.bg : T.fg2, border: i === 0 ? 'none' : `1px solid ${T.border}` }}>
              {a}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
