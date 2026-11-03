'use client'
import React, { useEffect, useState } from 'react'
import type { FieldSource } from './reading'
import { isGrain } from './reading'
import { alarmLine } from './alarm'
import { FidelityView } from './fidelity'
import { ClarityView } from './clarity'
import { CoherenceView } from './coherence'
import { readFidelity } from './fidelity.read'
import { readClarity } from './clarity.read'
import { readCoherence } from './coherence.read'
import { border, surface, text, signal } from '@/ui/tokens'

// Admin-only strip of the three gauges that read real data (conviction and consonance have no source yet, so they are not mounted), fixed above the field. No drag, grid or saved layout.
// One alarm line leads; tapping a gauge opens a drawer with the evidence behind its number.
const cell: React.CSSProperties = { flex: '1 1 150px', minWidth: 150, maxWidth: 220 }
const tap: React.CSSProperties = { all: 'unset', display: 'block', width: '100%', height: '100%', cursor: 'pointer', pointerEvents: 'auto', borderRadius: 8 }

export function HudWidgets({ field }: { field: FieldSource }) {
  const [open, setOpen] = useState<string | null>(null)
  const items = [
    { id: 'fidelity', title: 'Fidelity', reading: readFidelity(field), view: <FidelityView source={field} /> },
    { id: 'clarity', title: 'Clarity', reading: readClarity(field), view: <ClarityView source={field} /> },
    { id: 'coherence', title: 'Coherence', reading: readCoherence(field), view: <CoherenceView source={field} /> },
  ]
  const alarm = alarmLine(items)
  const sel = items.find((i) => i.id === open) ?? null

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(null) }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  return (
    <div role="group" aria-label="HUD gauges" style={{ position: 'fixed', zIndex: 1100, left: 8, right: 8, bottom: 44, display: 'flex', flexDirection: 'column', gap: 8, pointerEvents: 'none' }}>
      <div role="status" style={{ alignSelf: 'flex-start', padding: '4px 10px', fontSize: 12, color: text.primary, background: surface.panel, border: `1px solid ${alarm ? signal.gold : border.subtle}`, borderRadius: 6, pointerEvents: 'auto' }}>
        {alarm ?? 'All gauges sharp'}
      </div>
      {sel ? (
        <section aria-label={`${sel.title} evidence`} style={{ alignSelf: 'flex-start', maxWidth: 440, padding: 12, fontSize: 12, color: text.primary, background: surface.panel, border: `1px solid ${border.subtle}`, borderRadius: 8, pointerEvents: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
            <strong>{sel.title}</strong>
            <button type="button" onClick={() => setOpen(null)} aria-label="Close evidence" style={{ all: 'unset', cursor: 'pointer', color: text.muted }}>Close</button>
          </div>
          <dl style={{ margin: '8px 0 0', display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '2px 12px' }}>
            <dt style={{ color: text.muted }}>Value</dt><dd style={{ margin: 0 }}>{sel.reading.value === null ? 'No signal' : sel.reading.value.toFixed(3)}</dd>
            <dt style={{ color: text.muted }}>Sample</dt><dd style={{ margin: 0 }}>{sel.reading.threshold === null ? `n = ${sel.reading.n}, no threshold yet` : `n = ${sel.reading.n} of ${sel.reading.threshold}${isGrain(sel.reading) ? ' (GRAIN)' : ''}`}</dd>
            <dt style={{ color: text.muted }}>Source</dt><dd style={{ margin: 0 }}>{sel.reading.source}</dd>
            <dt style={{ color: text.muted }}>As of</dt><dd style={{ margin: 0 }}>{sel.reading.asOf ?? 'unknown'}</dd>
          </dl>
        </section>
      ) : null}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {items.map((i) => (
          <div key={i.id} style={cell}>
            <button type="button" aria-expanded={open === i.id} aria-label={`${i.title} evidence`} onClick={() => setOpen(open === i.id ? null : i.id)} style={tap}>{i.view}</button>
          </div>
        ))}
      </div>
    </div>
  )
}
