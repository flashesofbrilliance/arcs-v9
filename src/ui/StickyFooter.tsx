'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { text, signal, font } from './tokens'
import { Button } from './Button'

export const FOOTER_H = 60   // CTA bar height (dismissible)
export const LEGAL_H  = 30   // Legal bar height (always visible)

const legalLinkStyle: React.CSSProperties = {
  fontFamily: font.mono, fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase',
  color: text.dimmed, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0,
}

export function StickyFooter({
  message,
  ctaLabel = 'Inquire directly',
  ctaHref = '/advisory',
  maxWidth = 960,
}: {
  message: string
  ctaLabel?: string
  ctaHref?: string
  maxWidth?: number
}) {
  const router = useRouter()
  const [dismissed, setDismissed] = useState(false)

  return (
    <>
      {/* CTA bar — dismissible via X, sits above the legal bar */}
      {!dismissed && (
        <div
          style={{
            position: 'fixed', bottom: `calc(${LEGAL_H}px + env(safe-area-inset-bottom))`, left: 0, right: 0, zIndex: 50,
            height: FOOTER_H,
            borderTop: `1px solid ${signal.gold}25`,
            background: 'rgba(2,4,8,0.92)',
            backdropFilter: 'blur(12px)',
          }}
        >
          {/* Message + CTA — constrained to maxWidth */}
          <div
            style={{
              maxWidth, margin: '0 auto', height: '100%', padding: '0.75rem 1.5rem',
              display: 'flex', alignItems: 'center', gap: '1rem',
            }}
          >
            <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed, flex: 1 }}>
              {message}
            </span>
            <Button variant="gold" size="sm" onClick={() => router.push(ctaHref)}>
              {ctaLabel}&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
            </Button>
          </div>

          {/* X — absolute at right:0, matches breadcrumb X position */}
          <button
            onClick={() => setDismissed(true)}
            aria-label="Dismiss"
            style={{
              position: 'absolute', right: 0, top: 0, bottom: 0,
              minWidth: 44, padding: '0 12px',
              background: 'none', border: 'none', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <span style={{ fontFamily: font.mono, fontSize: 10, color: `${signal.gold}44`, lineHeight: 1 }}>✕</span>
          </button>
        </div>
      )}

      {/* Legal bar — always visible at the very bottom, above iOS home indicator */}
      <div
        style={{
          position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
          height: `calc(${LEGAL_H}px + env(safe-area-inset-bottom))`,
          paddingBottom: 'env(safe-area-inset-bottom)',
          borderTop: `1px solid rgba(255,255,255,0.05)`,
          background: 'rgba(2,4,8,0.92)',
          backdropFilter: 'blur(12px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem',
        }}
      >
        <button onClick={() => router.push('/trust')} style={legalLinkStyle}>Trust</button>
        <button onClick={() => router.push('/privacy')} style={legalLinkStyle}>Privacy</button>
        <button onClick={() => router.push('/terms')} style={legalLinkStyle}>Terms</button>
      </div>
    </>
  )
}
