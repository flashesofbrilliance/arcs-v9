'use client'
import React from 'react'
import Link from 'next/link'
import { font, signal, text, border } from './tokens'

export interface WordmarkProps {
  section?: string
}

// Logomark — a nested infinity/orbit knot, vector not raster so it stays
// crisp at the ~14-18px size it actually renders at next to the wordmark.
// Two concentric loops echo the "many strands, one path" reference image
// without the noise — a photo of light-trails turns to mud at this scale.
function ArcsMark() {
  return (
    <svg width="18" height="13" viewBox="0 0 24 16" fill="none" aria-hidden="true" style={{ flexShrink: 0 }}>
      <path
        d="M12 8 C12 3.5 5 3.5 5 8 C5 12.5 12 12.5 12 8 C12 3.5 19 3.5 19 8 C19 12.5 12 12.5 12 8"
        stroke={signal.cyan}
        strokeWidth={1.1}
        strokeLinecap="round"
        opacity={0.95}
      />
      <path
        d="M12 8 C12 5.2 8 5.2 8 8 C8 10.8 12 10.8 12 8 C12 5.2 16 5.2 16 8 C16 10.8 12 10.8 12 8"
        stroke={signal.cyan}
        strokeWidth={0.7}
        strokeLinecap="round"
        opacity={0.5}
      />
    </svg>
  )
}

// The mark + section label double as a "home" affordance everywhere they
// appear (compass, brief, history, etc.) — clicking either returns to "/".
export function Wordmark({ section }: WordmarkProps) {
  return (
    <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
      {/* Bierut fix I — the mark reads as a proper noun, not a UI label: ARCS
          heavier + wider-tracked; FIELD OS drops to a lighter cut + dimmer ink. */}
      <span style={{ fontFamily: font.mono, fontSize: '0.65rem', textTransform: 'uppercase', whiteSpace: 'nowrap', display: 'inline-flex', alignItems: 'baseline', gap: '0.45em' }}>
        <ArcsMark />
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
