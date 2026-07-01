'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { text, signal, font } from './tokens'
import { Button } from './Button'
import { useToastDrawer } from './ToastDrawerContext'

export const FOOTER_H = 60

const legalLinkStyle: React.CSSProperties = {
  fontFamily: font.mono, fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase',
  color: text.dimmed, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0,
}

// Sticky bottom bar used on every public page. While the EyebrowToast covenant
// drawer is open, it fades through black to show only Trust/Privacy/Terms —
// same predictable position, regardless of which page's footer copy normally lives there.
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
  const [copied, setCopied] = useState(false)

  function copyAddr() {
    navigator.clipboard.writeText('zachharris.eth')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      style={{
        position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50,
        height: FOOTER_H,
        borderTop: `1px solid ${signal.gold}25`,
        background: open ? 'rgba(0,0,0,0.97)' : 'rgba(2,4,8,0.92)',
        backdropFilter: 'blur(12px)',
        transition: 'background 0.45s ease',
      }}
    >
      <div style={{ position: 'relative', maxWidth, margin: '0 auto', height: '100%', padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center' }}>
        {/* Normal content — fades out when drawer opens */}
        <div
          style={{
            position: 'absolute', inset: 0, padding: '0.75rem 1.5rem',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem',
            opacity: open ? 0 : 1,
            transition: 'opacity 0.3s ease',
            pointerEvents: open ? 'none' : 'auto',
          }}
        >
          <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed }}>
            {message}
          </span>
          <Button variant="gold" size="sm" onClick={() => router.push(ctaHref)}>
            {ctaLabel}&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
          </Button>
        </div>

        {/* Legal links — fade in when drawer opens */}
        <div
          style={{
            position: 'absolute', inset: 0, padding: '0.75rem 1.5rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem',
            opacity: open ? 1 : 0,
            transition: 'opacity 0.3s ease',
            pointerEvents: open ? 'auto' : 'none',
          }}
        >
          <button onClick={() => router.push('/trust')} style={legalLinkStyle}>Trust</button>
          <button onClick={() => router.push('/privacy')} style={legalLinkStyle}>Privacy</button>
          <button onClick={() => router.push('/terms')} style={legalLinkStyle}>Terms</button>
        </div>

      </div>

      {/* Support section - shows below footer when drawer opens */}
      {open && (
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            top: FOOTER_H,
            padding: '1rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              maxWidth: 280,
              textAlign: 'center',
            }}
          >
            <div style={{ fontFamily: font.mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: '0.1em', color: text.muted, marginBottom: '0.4rem' }}>
              Support The Project
            </div>
            <div style={{ fontFamily: font.mono, fontSize: 13, fontWeight: 700, color: text.primary, marginBottom: '0.5rem' }}>
              zachharris.eth
            </div>
            <button
              onClick={copyAddr}
              style={{
                fontFamily: font.mono,
                fontSize: 9,
                color: copied ? signal.green : text.secondary,
                background: 'rgba(0,240,255,0.05)',
                border: `0.5px solid ${signal.cyan}33`,
                borderRadius: 4,
                padding: '4px 9px',
                cursor: 'pointer',
                transition: 'color 0.15s',
              }}
            >
              {copied ? 'Copied ✓' : 'Copy address'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
