'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Button } from '@/ui/Button'

// CompassError — Bierut fix IV. A raw "Failed to fetch" is a stack-trace surfaced
// to someone who just committed their real fork. The failure state should be the
// most designed thing in the product, speaking in the same cartographic voice as
// the rest — and it should reassure: the fork is held, nothing was lost.

export interface CompassErrorProps {
  message?: string | null   // raw error kept, but demoted to dimmed metadata
  onRetry?: () => void
}

export function CompassError({ message, onRetry }: CompassErrorProps) {
  return (
    <Card accent={signal.gold}>
      <div style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: signal.gold, marginBottom: '0.65rem' }}>
        ◈ &nbsp;Compass offline · L0 signal lost
      </div>
      <p style={{ fontFamily: font.sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.6, margin: '0 0 1rem' }}>
        The terrain dropped out before activation. Your fork is held — nothing was lost.
      </p>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', flexWrap: 'wrap' }}>
        {onRetry && (
          <Button variant="gold" size="sm" glyph="↻" onClick={onRetry}>Re-run the compass</Button>
        )}
        {message && (
          <span style={{ fontFamily: font.mono, fontSize: '0.625rem', letterSpacing: '0.04em', color: text.muted }}>
            {message}
          </span>
        )}
      </div>
    </Card>
  )
}
