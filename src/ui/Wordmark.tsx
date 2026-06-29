'use client'
import React from 'react'
import Link from 'next/link'
import { font, signal, text, border } from './tokens'

export interface WordmarkProps {
  section?: string
}

// The mark + section label double as a "home" affordance everywhere they
// appear (compass, brief, history, etc.) — clicking either returns to "/".
export function Wordmark({ section }: WordmarkProps) {
  return (
    <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
      {/* Bierut fix I — the mark reads as a proper noun, not a UI label: ARCS
          heavier + wider-tracked; FIELD OS drops to a lighter cut + dimmer ink. */}
      <span style={{ fontFamily: font.mono, fontSize: '0.65rem', textTransform: 'uppercase', whiteSpace: 'nowrap', display: 'inline-flex', alignItems: 'baseline', gap: '0.45em' }}>
        <span style={{ color: signal.cyan, fontWeight: 800, letterSpacing: '0.22em' }}>ARCS</span>
        <span style={{ color: text.dimmed, fontWeight: 400, letterSpacing: '0.14em' }}>FIELD OS</span>
      </span>
      {section && (
        <>
          <span style={{ width: 1, height: 12, background: border.subtle }} />
          <span style={{ fontFamily: font.mono, fontSize: '0.65rem', letterSpacing: '0.12em', color: text.muted, textTransform: 'uppercase' }}>{section}</span>
        </>
      )}
    </Link>
  )
}
