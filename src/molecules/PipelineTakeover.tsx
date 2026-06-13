'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'

// PipelineTakeover — Bierut fix VI. The L0–L5 run is the most momentum-building
// moment in the product: proof that six layers of intelligence ran on the user's
// behalf. Promoted from a strip buried below the form to a full-viewport takeover
// that owns the screen while the compass runs. A search result becomes a verdict.

const LAYERS: [string, string][] = [
  ['L0', 'ACTIVATION'],
  ['L1', 'ADVERSARIAL'],
  ['L2', 'BAYESIAN'],
  ['L3', 'IMMUNE'],
  ['L4', 'NCI'],
  ['L5', 'SYNTHESIS'],
]

export interface PipelineTakeoverProps {
  current?: number // 0–5, the active layer index
}

export function PipelineTakeover({ current = 0 }: PipelineTakeoverProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: 'fixed', inset: 0, zIndex: 50,
        background: 'radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: '2rem', gap: '2.25rem',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
        <Wordmark />
        <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: signal.cyan }}>
          Running L0–L5 pipeline…
        </span>
      </div>

      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {LAYERS.map(([id, name], i) => {
          const done = i < current
          const active = i === current
          const lit = i <= current
          const c = lit ? signal.cyan : text.muted
          return (
            <div key={id} style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
              <span style={{ fontFamily: font.mono, fontSize: '0.85rem', width: 16, textAlign: 'center', color: c, textShadow: lit ? `0 0 10px ${signal.cyan}88` : 'none' }}>
                {lit ? '▸' : '·'}
              </span>
              <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', color: lit ? text.primary : text.muted, minWidth: 26 }}>{id}</span>
              <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', color: lit ? text.secondary : text.muted }}>{name}</span>
              <div style={{ flex: 1, height: 1, background: '#141e2e' }} />
              {active && <span style={{ fontFamily: font.mono, fontSize: '0.625rem', letterSpacing: '0.08em', color: signal.cyan }}>◂ active</span>}
              {done && <span style={{ fontFamily: font.mono, fontSize: '0.7rem', color: signal.green }}>✓</span>}
            </div>
          )
        })}
      </div>

      <span style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed, fontStyle: 'italic' }}>
        Rendering through the fog…
      </span>
    </div>
  )
}
