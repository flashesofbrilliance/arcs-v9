'use client'
import React from 'react'
import { font, signal, text, border } from './tokens'

export interface WordmarkProps {
  section?: string
}

export function Wordmark({ section }: WordmarkProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <span style={{ fontFamily: font.mono, fontSize: '0.65rem', letterSpacing: '0.15em', color: signal.cyan, textTransform: 'uppercase', fontWeight: 700, whiteSpace: 'nowrap' }}>
        ARCS <span style={{ color: text.secondary, fontWeight: 500 }}>FIELD OS</span>
      </span>
      {section && (
        <>
          <span style={{ width: 1, height: 12, background: border.subtle }} />
          <span style={{ fontFamily: font.mono, fontSize: '0.65rem', letterSpacing: '0.12em', color: text.muted, textTransform: 'uppercase' }}>{section}</span>
        </>
      )}
    </div>
  )
}
