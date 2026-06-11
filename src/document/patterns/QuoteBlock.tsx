'use client'
import React from 'react'
import { T } from '../tokens'

export interface QuoteBlockProps {
  children: React.ReactNode
  attribution?: string
  accent?: string
}

export function QuoteBlock({ children, attribution, accent = T.cyan }: QuoteBlockProps) {
  return (
    <div style={{ padding: '16px 20px', borderRadius: 8, background: T.surface, borderLeft: `4px solid ${accent}` }}>
      <blockquote style={{ fontFamily: T.sans, fontSize: 16, fontWeight: 500, color: T.fg1, lineHeight: 1.7, fontStyle: 'italic' }}>&quot;{children}&quot;</blockquote>
      {attribution && <div style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4, marginTop: 10, letterSpacing: '0.06em' }}>— {attribution}</div>}
    </div>
  )
}
