'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { track } from '@vercel/analytics'
import { text, signal, font } from './tokens'
import { Button } from './Button'
import { useToastDrawer } from './ToastDrawerContext'

export const FOOTER_H = 60

const legalLinkStyle: React.CSSProperties = {
  fontFamily: font.mono, fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase',
  color: text.dimmed, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0,
}

// Single fixed bar. Two layers share the same space:
//   · CTA layer  — fades out when drawer opens or CTA is dismissed
//   · Legal layer — fades in when drawer opens; becomes permanent when CTA is dismissed
// On dismiss the CTA layer is removed and the legal layer is locked visible.
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
  const { open } = useToastDrawer()
  const router = useRouter()
  const [dismissed, setDismissed] = useState(false)

  // Legal links are visible when the drawer is open OR the CTA has been dismissed
  const showLegal = dismissed || open

  return (
    <div
      style={{
        position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
        height: `calc(${FOOTER_H}px + env(safe-area-inset-bottom))`,
        paddingBottom: 'env(safe-area-inset-bottom)',
        borderTop: dismissed ? `1px solid rgba(255,255,255,0.05)` : `1px solid ${signal.gold}25`,
        background: (!dismissed && open) ? 'rgba(0,0,0,0.97)' : 'rgba(2,4,8,0.92)',
        backdropFilter: 'blur(12px)',
        transition: 'background 0.45s ease',
      }}
    >
      {/* CTA content — fades out when drawer opens or when dismissed */}
      {!dismissed && (
        <div
          style={{
            position: 'absolute', inset: 0, paddingBottom: 'env(safe-area-inset-bottom)',
            padding: '0 1.5rem', maxWidth, margin: '0 auto',
            display: 'flex', alignItems: 'center', gap: '1rem',
            opacity: open ? 0 : 1,
            transition: 'opacity 0.3s ease',
            pointerEvents: open ? 'none' : 'auto',
          }}
        >
          <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed, flex: 1 }}>
            {message}
          </span>
          <Button variant="gold" size="sm" onClick={() => { track('footer_inquiry_click'); router.push(ctaHref) }}>
            {ctaLabel}&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
          </Button>
        </div>
      )}

      {/* Legal links — fade in when drawer opens; locked visible once dismissed */}
      <div
        style={{
          position: 'absolute', inset: 0, paddingBottom: 'env(safe-area-inset-bottom)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem',
          opacity: showLegal ? 1 : 0,
          transition: dismissed ? 'none' : 'opacity 0.3s ease',
          pointerEvents: showLegal ? 'auto' : 'none',
        }}
      >
        <button onClick={() => router.push('/trust')} style={legalLinkStyle}>Trust</button>
        <button onClick={() => router.push('/privacy')} style={legalLinkStyle}>Privacy</button>
        <button onClick={() => router.push('/terms')} style={legalLinkStyle}>Terms</button>
      </div>

      {/* X — absolute at right:0, same axis as breadcrumb X; only shown while CTA is up */}
      {!dismissed && (
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
      )}
    </div>
  )
}
