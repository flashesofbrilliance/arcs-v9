'use client'
import React from 'react'
import { tribColor } from '@/ui/tokens'
import { SectionLabel } from '@/ui/SectionLabel'
import { TributaryTile } from '@/instrument/TributaryTile'
import type { Tributary } from '@/lib/mockCompass'

// TributariesStack — SectionLabel + TributaryTile ×3. Source: Result.jsx.
// Canonical: uses tribColor() from tokens (meta=cyan, challenge=red, adjacent=gold).
export interface TributariesStackProps {
  tributaries: Tributary[]
  onTributary?: (prompt: string) => void
}

export function TributariesStack({ tributaries, onTributary }: TributariesStackProps) {
  return (
    <div>
      <SectionLabel style={{ marginBottom: '0.6rem' }}>Tributaries · where to navigate next</SectionLabel>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {tributaries.map((t, i) => (
          <TributaryTile key={i} label={t.label} color={tribColor(t.type)} glyph={t.type === 'meta' ? '↳' : undefined} onClick={() => onTributary?.(t.prompt)}>{t.prompt}</TributaryTile>
        ))}
      </div>
    </div>
  )
}
