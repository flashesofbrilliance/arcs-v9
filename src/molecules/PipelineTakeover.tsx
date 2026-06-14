'use client'
import React from 'react'
import { SequenceLoader } from '@/molecules/SequenceLoader'

// PipelineTakeover — Bierut fix VI. The L0–L5 run owns the full viewport while
// the compass thinks, with each layer's progress bar actually filling as the
// engine advances (via SequenceLoader). A search result becomes a verdict.

const LAYERS = [
  { id: 'L0', name: 'ACTIVATION' },
  { id: 'L1', name: 'ADVERSARIAL' },
  { id: 'L2', name: 'BAYESIAN' },
  { id: 'L3', name: 'IMMUNE' },
  { id: 'L4', name: 'NCI' },
  { id: 'L5', name: 'SYNTHESIS' },
]

export function PipelineTakeover() {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: 'fixed', inset: 0, zIndex: 50,
        background: 'radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem',
      }}
    >
      <SequenceLoader title="Running L0–L5 pipeline…" stages={LAYERS} footer="Rendering through the fog…" />
    </div>
  )
}
