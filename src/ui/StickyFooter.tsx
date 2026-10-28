'use client'

import React, { useState } from 'react'
import { usePathname } from 'next/navigation'
import { text, signal, font } from './tokens'
import { CloseButton } from './CloseButton'
import { ButtonLink } from './Button'
import Link from 'next/link'
import { useToastDrawer } from './ToastDrawerContext'

export const FOOTER_H = 60

const legalLinkStyle: React.CSSProperties = {
  fontFamily: font.mono, fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase',
  color: text.dimmed, textDecoration: 'underline',
}

// Fixed offer bar: the sprint CTA, faded while the data drawer is open, gone once dismissed.
// Trust, Privacy and Terms live in the in-flow SiteFooter at the end of every page.
export function SiteFooter() {
  const pathname = usePathname()
  if (pathname === '/hud') return null
  return (
    <footer
      style={{
        display: 'flex', justifyContent: 'center', gap: '1.5rem',
        padding: `1.5rem 1.5rem calc(${FOOTER_H}px + 1.5rem + env(safe-area-inset-bottom))`,
        borderTop: '1px solid rgba(255,255,255,0.05)',
      }}
    >
      <Link href="/trust" style={legalLinkStyle}>Trust</Link>
      <Link href="/privacy" style={legalLinkStyle}>Privacy</Link>
      <Link href="/terms" style={legalLinkStyle}>Terms</Link>
    </footer>
  )
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
  const { open } = useToastDrawer()
  const [dismissed, setDismissed] = useState(false)
  const pathname = usePathname()

  // Full-screen instruments (arcs.care/hud) carry no page chrome; a dismissed offer leaves no bar.
  if (pathname === '/hud' || dismissed) return null
  return (
    <div
      style={{
        position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
        height: `calc(${FOOTER_H}px + env(safe-area-inset-bottom))`,
        paddingBottom: 'env(safe-area-inset-bottom)',
        borderTop: `1px solid ${signal.gold}25`,
        background: open ? 'rgba(0,0,0,0.97)' : 'rgba(2,4,8,0.92)',
        backdropFilter: 'blur(12px)',
        transition: 'background 0.45s ease',
      }}
    >
      {/* CTA content — fades out when drawer opens or when dismissed */}
      {(
        <div
          style={{
            position: 'absolute', inset: 0, paddingBottom: 'env(safe-area-inset-bottom)',
            padding: '0 max(1.5rem, 52px) 0 1.5rem', maxWidth, margin: '0 auto',
            display: 'flex', alignItems: 'center', gap: '1rem',
            opacity: open ? 0 : 1,
            // visibility (not just opacity) so a faded layer leaves the tab order
            visibility: open ? 'hidden' : 'visible',
            transition: 'opacity 0.3s ease, visibility 0.3s',
            pointerEvents: open ? 'none' : 'auto',
          }}
        >
          <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed, flex: 1 }}>
            {message}
          </span>
          <ButtonLink variant="gold" size="sm" href={ctaHref}>
            {ctaLabel}&nbsp;<span aria-hidden="true" style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
          </ButtonLink>
        </div>
      )}

      {/* Dismiss: same right-edge axis as the data-notice X. The CTA row
          reserves that 48px lane (paddingRight below) so the two never overlap. */}
      {(
        <CloseButton
          label="Dismiss sprint offer"
          accent={signal.gold}
          onClick={() => setDismissed(true)}
          style={{ position: 'absolute', right: 'max(4px, env(safe-area-inset-right))', top: '50%', transform: 'translateY(-50%)', marginTop: 'calc(env(safe-area-inset-bottom) / -2)' }}
        />
      )}
    </div>
  )
}
