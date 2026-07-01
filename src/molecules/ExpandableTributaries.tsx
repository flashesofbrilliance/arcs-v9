'use client'
import React, { useState } from 'react'
import { track } from '@vercel/analytics'
import { font, text, signal, border, tribColor } from '@/ui/tokens'
import { Field } from '@/ui/Field'
import { Button } from '@/ui/Button'
import type { Tributary } from '@/lib/mockCompass'

export interface PlgContext {
  receiptId: string
  sessionId?: string | null
}

export interface ExpandableTributariesProps {
  tributaries: Tributary[]
  onTributary?: (prompt: string) => void
  // PLG hook: when authed===false and plgContext is set, clicking a tributary
  // shows an inline magic-link signup instead of navigating to dashboard.
  authed?: boolean | null
  plgContext?: PlgContext
}

export function ExpandableTributaries({ tributaries, onTributary, authed, plgContext }: ExpandableTributariesProps) {
  const [open, setOpen] = useState(false)
  // PLG state — set when an unauthed viewer clicks a tributary
  const [pendingTrib, setPendingTrib] = useState<Tributary | null>(null)
  const [email, setEmail] = useState('')
  const [plgStatus, setPlgStatus] = useState<'idle' | 'sending' | 'sent'>('idle')

  // If auth resolves to confirmed-true while the PLG form is showing (slow session
  // check + fast click), navigate the user rather than leaving the form open.
  React.useEffect(() => {
    if (authed === true && pendingTrib) {
      onTributary?.(pendingTrib.prompt)
      setPendingTrib(null)
      setOpen(false)
    }
  }, [authed]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!tributaries.length) return null

  function handleTribClick(t: Tributary) {
    // Only confirmed-authed users bypass the PLG gate; null (still checking)
    // and false both show the signup form — the effect above handles the
    // edge case where null later resolves to true.
    if (authed === true || !plgContext) {
      onTributary?.(t.prompt)
      setOpen(false)
      return
    }
    // Unauthed (or still-checking) viewer → capture intent, show signup
    setPendingTrib(t)
    setPlgStatus('idle')
    setEmail('')
    track('brief_tributary_plg_intent', { tributaryType: t.type, receiptId: plgContext.receiptId })
  }

  async function handlePlgSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || !pendingTrib || !plgContext || plgStatus !== 'idle') return
    setPlgStatus('sending')
    const q = encodeURIComponent(pendingTrib.prompt)
    const parent = encodeURIComponent(plgContext.receiptId)
    const sid = plgContext.sessionId ? `&sid=${encodeURIComponent(plgContext.sessionId)}` : ''
    const callbackUrl = `/dashboard?q=${q}&parent=${parent}${sid}`
    const { signIn } = await import('next-auth/react')
    await signIn('resend', { email, callbackUrl, redirect: false })
    track('brief_tributary_plg_signup', { tributaryType: pendingTrib.type, receiptId: plgContext.receiptId })
    setPlgStatus('sent')
  }

  return (
    <div>
      {/* Collapsed state — button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          style={{
            fontFamily: font.mono,
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            padding: '8px 14px',
            borderRadius: 5,
            border: `0.5px solid ${signal.cyan}55`,
            background: `${signal.cyan}08`,
            color: signal.cyan,
            cursor: 'pointer',
            transition: 'all .12s',
          }}
          onMouseEnter={(e) => {
            const el = e.currentTarget
            el.style.background = `${signal.cyan}14`
            el.style.borderColor = `${signal.cyan}88`
          }}
          onMouseLeave={(e) => {
            const el = e.currentTarget
            el.style.background = `${signal.cyan}08`
            el.style.borderColor = `${signal.cyan}55`
          }}
        >
          ↳ {tributaries.length} follow-up{tributaries.length !== 1 ? 's' : ''}
        </button>
      )}

      {/* Expanded state — nested threads */}
      {open && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {tributaries.map((t, i) => {
            const color = tribColor(t.type)
            const isPending = pendingTrib?.prompt === t.prompt
            return (
              <div
                key={i}
                style={{
                  paddingLeft: '1rem',
                  borderLeft: `1.5px solid ${isPending ? color : `${color}3a`}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem',
                  transition: 'border-color .15s',
                }}
              >
                <button
                  onClick={() => handleTribClick(t)}
                  style={{
                    textAlign: 'left',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.3rem',
                  }}
                >
                  <div
                    style={{
                      fontFamily: font.mono,
                      fontSize: '0.6rem',
                      fontWeight: 700,
                      letterSpacing: '0.1em',
                      textTransform: 'uppercase',
                      color: color,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                    }}
                  >
                    <span style={{ opacity: 0.6 }}>·</span> {t.label}
                  </div>
                  <div
                    style={{
                      fontFamily: font.sans,
                      fontSize: '0.9rem',
                      color: isPending ? text.primary : text.secondary,
                      lineHeight: 1.5,
                      transition: 'color .12s',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLDivElement).style.color = text.primary
                    }}
                    onMouseLeave={(e) => {
                      if (!isPending) (e.currentTarget as HTMLDivElement).style.color = text.secondary
                    }}
                  >
                    {t.prompt}
                  </div>
                </button>

                {/* PLG inline signup — appears under the selected tributary */}
                {isPending && (
                  <div
                    style={{
                      marginTop: '0.5rem',
                      padding: '1rem 1.125rem',
                      background: '#0a1520',
                      border: `0.5px solid ${border.subtle}`,
                      borderRadius: 6,
                    }}
                  >
                    {plgStatus === 'sent' ? (
                      <div style={{ paddingLeft: '0.75rem', borderLeft: `2px solid ${signal.cyan}` }}>
                        <div style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted, marginBottom: '0.3rem' }}>Link sent</div>
                        <div style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.primary, lineHeight: 1.5 }}>
                          Check your email — sent to <span style={{ color: signal.cyan }}>{email}</span>
                        </div>
                        <div style={{ fontFamily: font.sans, fontSize: '0.78rem', color: text.muted, marginTop: '0.4rem', lineHeight: 1.5 }}>
                          Click the link and your compass will open with this question ready to run.
                        </div>
                      </div>
                    ) : (
                      <form onSubmit={handlePlgSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <div style={{ fontFamily: font.sans, fontSize: '0.82rem', color: text.secondary, lineHeight: 1.55 }}>
                          Run this in your own compass. One magic link — no password.
                        </div>
                        <Field
                          label="Email"
                          type="email"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="you@example.com"
                        />
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <Button
                            type="submit"
                            variant="primary"
                            size="sm"
                            glyph={plgStatus === 'sending' ? '~' : '→'}
                            disabled={plgStatus === 'sending' || !email.trim()}
                          >
                            {plgStatus === 'sending' ? 'Sending…' : 'Send link'}
                          </Button>
                          <button
                            type="button"
                            onClick={() => setPendingTrib(null)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: font.mono, fontSize: '0.6rem', color: text.muted, letterSpacing: '0.05em', textTransform: 'uppercase', transition: 'color .12s', padding: 0 }}
                            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = text.secondary }}
                            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = text.muted }}
                          >
                            cancel
                          </button>
                        </div>
                      </form>
                    )}
                  </div>
                )}
              </div>
            )
          })}

          {/* Collapse button */}
          <button
            onClick={() => { setOpen(false); setPendingTrib(null) }}
            style={{
              fontFamily: font.mono,
              fontSize: '0.6rem',
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              padding: '0',
              border: 'none',
              background: 'none',
              color: text.muted,
              cursor: 'pointer',
              marginTop: '0.25rem',
              transition: 'color .12s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.color = text.secondary
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.color = text.muted
            }}
          >
            ↑ collapse
          </button>
        </div>
      )}
    </div>
  )
}
