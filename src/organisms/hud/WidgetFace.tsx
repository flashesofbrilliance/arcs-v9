'use client'
import React from 'react'
import { Gauge } from '@/ui/Gauge'
import { signal, text } from '@/ui/tokens'
import { isGrain, type Reading } from './reading'

// Shared face for the five widgets: Reading in, Gauge out. Honesty rule: a reading below its
// threshold renders GRAIN and prints n; a reading with no source prints "No signal".
// Text stays full opacity; fog is shown with the grain overlay, never by dimming words.
const GRAIN_BG = 'repeating-linear-gradient(45deg, rgba(148,163,184,.14) 0 1px, transparent 1px 3px), repeating-linear-gradient(-45deg, rgba(148,163,184,.10) 0 1px, transparent 1px 4px)'

export function WidgetFace({ title, reading, fmt, noSignalWhy }: { title: string; reading: Reading; fmt: (v: number) => string; noSignalWhy?: string }) {
  const none = reading.threshold === null
  const grain = isGrain(reading)
  const value = none ? 'No signal' : grain ? 'GRAIN' : fmt(reading.value as number)
  const sub = none
    ? (noSignalWhy ?? 'no source yet')
    : grain
      ? `n = ${reading.n} of ${reading.threshold}`
      : `n = ${reading.n}`
  return (
    <Gauge
      label={title}
      value={value}
      sub={sub}
      valueSize={none || grain ? 20 : 28}
      color={grain ? text.secondary : signal.cyan}
      accent={grain ? undefined : signal.cyan}
      minWidth={0}
      style={{ height: '100%', backgroundImage: grain ? `${GRAIN_BG}, linear-gradient(165deg, #131b23, #0a1016)` : undefined }}
    >
      <div style={{ position: 'relative', fontSize: 11, color: text.muted, marginTop: 2 }}>{reading.source}{reading.asOf ? ` · ${reading.asOf}` : ''}</div>
    </Gauge>
  )
}
