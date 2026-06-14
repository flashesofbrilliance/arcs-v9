'use client'
import React from 'react'
import { font, signal, text, nciColor, signalGlow } from '@/ui/tokens'
import { Gauge } from '@/ui/Gauge'
import type { CompassResult } from '@/lib/mockCompass'

// InstrumentCluster — Gauge ×4 (NCI · Coherence · Satoshi · Macro). Source: Result.jsx.
export interface InstrumentClusterProps {
  result: CompassResult
}

export function InstrumentCluster({ result }: InstrumentClusterProps) {
  const c = nciColor(result.nci_score)
  return (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
      <Gauge label="Conviction" value={result.nci_score} sub="/ 100" color={c} glow={signalGlow(c)} minWidth={120} />
      {result.coherence_pct !== undefined && (
        <Gauge label="Coherence" minWidth={120} value={<>{result.coherence_pct}<span style={{ fontSize: 16, color: text.muted }}>%</span></>} />
      )}
      {result.is_satoshi && (
        <Gauge label="Satoshi" accent={signal.gold} minWidth={140} valueSize={24} color={signal.gold} glow={signalGlow(signal.gold)} value="★ Peak" />
      )}
      {result.macro_tags?.length > 0 && (
        <Gauge label="Macro Tags" flex={2} minWidth={160}>
          <div style={{ position: 'relative', display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 8 }}>
            {result.macro_tags.map(t => (
              <span key={t} style={{ fontSize: 11, padding: '3px 9px', borderRadius: 999, color: '#cfd9e6', fontWeight: 600, fontFamily: font.mono,
                background: 'linear-gradient(180deg, #1a2330, #121922)', boxShadow: 'inset 0 1px 0 rgba(255,255,255,.1), inset 0 -2px 4px rgba(0,0,0,.5)' }}>{t}</span>
            ))}
          </div>
        </Gauge>
      )}
    </div>
  )
}
