'use client'
import React from 'react'
import type { FieldSource } from './reading'
import { FidelityView } from './fidelity'
import { ConvictionView } from './conviction'
import { ClarityView } from './clarity'
import { CoherenceView } from './coherence'
import { ConsonanceView } from './consonance'

// Admin-only strip of the five gauges, fixed above the field. No drag, grid or saved layout:
// three of the five can only print No signal or GRAIN today, so the controls wait for real readings.
const cell: React.CSSProperties = { flex: '1 1 150px', minWidth: 150, maxWidth: 220 }

export function HudWidgets({ field }: { field: FieldSource }) {
  return (
    <div role="group" aria-label="HUD gauges" style={{ position: 'fixed', zIndex: 1100, left: 8, right: 8, bottom: 44, display: 'flex', flexWrap: 'wrap', gap: 8, pointerEvents: 'none' }}>
      <div style={cell}><FidelityView source={field} /></div>
      <div style={cell}><ConvictionView source={field} /></div>
      <div style={cell}><ClarityView source={field} /></div>
      <div style={cell}><CoherenceView source={field} /></div>
      <div style={cell}><ConsonanceView source={null} /></div>
    </div>
  )
}
