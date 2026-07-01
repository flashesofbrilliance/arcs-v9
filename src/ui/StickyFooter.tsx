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
            position: 'fixed', bottom: LEGAL_H, left: 0, right: 0, zIndex: 50,
            height: FOOTER_H,
            borderTop: `1px solid ${signal.gold}25`,
            background: 'rgba(2,4,8,0.92)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <div
            style={{
              maxWidth, margin: '0 auto', height: '100%', padding: '0.75rem 1.5rem',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem',
            }}
          >
            <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed }}>
              {message}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
              <Button variant="gold" size="sm" onClick={() => router.push(ctaHref)}>
                {ctaLabel}&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
              </Button>
              <button
                onClick={() => setDismissed(true)}
                aria-label="Dismiss"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  width: 24, height: 24, background: 'none', border: 'none', cursor: 'pointer', padding: 0, flexShrink: 0,
                }}
              >
                <span style={{ fontFamily: font.mono, fontSize: 11, color: `${text.dimmed}99`, lineHeight: 1 }}>✕</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Legal bar — always visible at the very bottom */}
      <div
        style={{
          position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
          height: LEGAL_H,
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
