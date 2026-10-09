'use client'
import React from 'react'
import { surface, text, signal, font } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Rule } from '@/ui/Rule'
import { ButtonLink } from '@/ui/Button'

// DeadEnd: the branded "nothing here" surface. Used by the app 404 and by any
// receipt/brief page whose record could not be loaded, so a bad or expired link
// always offers a way back instead of a lone red sentence.
export interface DeadEndProps {
  section?: string
  title: string
  body: string
}

export function DeadEnd({ section, title, body }: DeadEndProps) {
  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 620, margin: '0 auto', padding: '2rem 1.5rem 6rem' }}>
        <div style={{ paddingBottom: '1rem' }}>
          <Wordmark section={section} />
        </div>
        <Rule style={{ marginBottom: '2.5rem' }} />
        <div style={{ fontFamily: font.mono, fontSize: '0.6875rem', letterSpacing: '0.14em', textTransform: 'uppercase', color: signal.gold, marginBottom: '0.75rem' }}>
          Terrain unknown
        </div>
        <h1 style={{ fontFamily: font.sans, fontSize: '1.6rem', fontWeight: 600, color: text.primary, margin: '0 0 0.75rem', lineHeight: 1.2, letterSpacing: '-0.01em' }}>
          {title}
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: '0.95rem', color: text.secondary, margin: '0 0 2rem', lineHeight: 1.6 }}>
          {body}
        </p>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <ButtonLink variant="primary" size="md" glyph="⊕" href="/dashboard">Open the compass</ButtonLink>
          <ButtonLink variant="ghost" size="md" href="/history">Your ledger</ButtonLink>
          <ButtonLink variant="ghost" size="md" href="/">Home</ButtonLink>
        </div>
      </div>
    </main>
  )
}
