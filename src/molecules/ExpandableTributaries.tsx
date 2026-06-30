'use client'
import React, { useState } from 'react'
import { font, text, signal, tribColor } from '@/ui/tokens'
import type { Tributary } from '@/lib/mockCompass'

export interface ExpandableTributariesProps {
  tributaries: Tributary[]
  onTributary?: (prompt: string) => void
}

export function ExpandableTributaries({ tributaries, onTributary }: ExpandableTributariesProps) {
  const [open, setOpen] = useState(false)

  if (!tributaries.length) return null

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
            return (
              <div
                key={i}
                style={{
                  paddingLeft: '1rem',
                  borderLeft: `1.5px solid ${color}3a`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem',
                }}
              >
                <button
                  onClick={() => {
                    onTributary?.(t.prompt)
                    setOpen(false)
                  }}
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
                      color: text.secondary,
                      lineHeight: 1.5,
                      transition: 'color .12s',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLDivElement).style.color = text.primary
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLDivElement).style.color = text.secondary
                    }}
                  >
                    {t.prompt}
                  </div>
                </button>
              </div>
            )
          })}

          {/* Collapse button */}
          <button
            onClick={() => setOpen(false)}
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
