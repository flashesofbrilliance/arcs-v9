'use client'
import React from 'react'
import Link from 'next/link'
import { font, text, signal, border, surface } from '@/ui/tokens'

// The brief, shown locked on the free receipt: what it contains, never the
// content itself. Each row names a part the brief prompt actually writes
// (src/lib/briefPrompt.ts), so the page promises nothing the brief does not do.
// Brand promise: refuse to overclaim. No blurred fake text, no sample filler.

// One place for the price label until the paywall (PR 1950) exposes its own.
export const BRIEF_PRICE_LABEL = '$19'

const PARTS: { title: string; detail: string }[] = [
  { title: 'The blind spot', detail: 'The one thing you have most likely not considered, drawn from your own facts.' },
  { title: 'The tripwire', detail: 'The observable signal that would show this call is wrong, and the date by which you should see it.' },
  { title: 'The deciding question', detail: 'The single question that settles it, asked straight.' },
]

export function LockedBrief({ receiptId, hasBrief }: { receiptId: string; hasBrief: boolean }) {
  return (
    <section aria-labelledby="locked-brief" style={{ marginTop: '2.75rem', border: `1px solid ${border.subtle}`, borderTop: `2px solid ${signal.gold}`, borderRadius: 6, background: surface.panel, padding: 'clamp(1.1rem, 3.5vw, 1.75rem)' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', justifyContent: 'space-between', gap: '0.4rem 1rem', marginBottom: '0.6rem' }}>
        <h2 id="locked-brief" style={{ fontFamily: font.mono, ...font.tier.t6, textTransform: 'uppercase', color: signal.gold, margin: 0 }}>The brief</h2>
        <span style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: text.muted }}>{hasBrief ? 'Ready' : 'Written for this call'}</span>
      </div>
      <p style={{ fontFamily: font.sans, fontSize: '0.95rem', color: text.primary, lineHeight: 1.55, margin: '0 0 1.1rem', textWrap: 'pretty' }}>
        This receipt is where you stand. The brief is what you are not seeing yet.
      </p>

      <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {PARTS.map((p, i) => (
          <li key={p.title} style={{ display: 'grid', gridTemplateColumns: '1.75rem 1fr', alignItems: 'baseline', padding: '0.75rem 0', borderTop: `1px solid ${border.subtle}` }}>
            <span aria-hidden style={{ fontFamily: font.mono, ...font.tier.t4, color: signal.gold, fontVariantNumeric: 'tabular-nums' }}>{String(i + 1).padStart(2, '0')}</span>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontFamily: font.sans, fontSize: '0.95rem', fontWeight: 600, color: text.primary, lineHeight: 1.4 }}>{p.title}</div>
              <div style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.secondary, lineHeight: 1.5, marginTop: '0.15rem', textWrap: 'pretty' }}>{p.detail}</div>
            </div>
          </li>
        ))}
      </ol>

      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.6rem 1rem', marginTop: '1.1rem' }}>
        <Link
          href={`/brief/${receiptId}`}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', minHeight: 44, padding: '0 1.1rem', borderRadius: 4, background: signal.gold, color: surface.bg, fontFamily: font.mono, ...font.tier.t4, textTransform: 'uppercase', textDecoration: 'none', fontWeight: 700 }}
        >
          {hasBrief ? 'Open your brief →' : `Unlock the brief · ${BRIEF_PRICE_LABEL}`}
        </Link>
        {!hasBrief && <span style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.muted }}>One payment. Yours to keep and share.</span>}
      </div>
    </section>
  )
}
