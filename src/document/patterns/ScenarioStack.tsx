'use client'
import React, { useState } from 'react'
import { T, DIM, BDR } from '../tokens'
import { Pill } from '../primitives'

export interface Scenario {
  title?: string
  body: string
  note?: string
  /** Placeholder with no source data; the stack opens on the first scenario without it. */
  empty?: boolean
}

export interface ScenarioStackProps {
  scenarios: { best: Scenario; base: Scenario; worst: Scenario }
}

type SKey = 'best' | 'base' | 'worst'

const SCFG: Record<SKey, { label: string; color: string; key: SKey }> = {
  best: { label: 'Best Case', color: T.green, key: 'best' },
  base: { label: 'Base Case', color: T.gold, key: 'base' },
  worst: { label: 'Worst Case', color: T.red, key: 'worst' },
}

export function ScenarioStack({ scenarios }: ScenarioStackProps) {
  const first = (['best', 'base', 'worst'] as SKey[]).find(k => !scenarios[k].empty) ?? 'best'
  const [active, setActive] = useState<SKey>(first)
  const s = scenarios[active]
  const cfg = SCFG[active]
  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        {Object.values(SCFG).map(c => (
          <button key={c.key} onClick={() => setActive(c.key)} style={{ height: 30, padding: '0 14px', borderRadius: 7, cursor: 'pointer', fontFamily: T.mono, fontSize: T.fsLabel, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase',
            background: active === c.key ? DIM(c.color) : 'transparent', color: active === c.key ? c.color : T.fg3, border: `1px solid ${active === c.key ? BDR(c.color) : T.border}`, transition: 'all .14s' }}>
            {c.label}
          </button>
        ))}
      </div>
      <div key={active} style={{ breakInside: 'avoid', animation: 'fade .2s ease-out', padding: '18px 20px', borderRadius: 10, background: T.surface, border: `1px solid ${BDR(cfg.color)}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <Pill accent={cfg.color}>{cfg.label}</Pill>
          {s.title && <span style={{ fontFamily: T.sans, fontSize: T.fsBody, fontWeight: 600, color: T.fg1 }}>{s.title}</span>}
        </div>
        <p style={{ fontFamily: T.sans, fontSize: T.fsBody, color: T.fg2, lineHeight: 1.7 }}>{s.body}</p>
        {s.note && <div style={{ marginTop: 10, padding: '7px 11px', borderRadius: 5, background: DIM(cfg.color), fontFamily: T.mono, fontSize: T.fsLabel, color: cfg.color, letterSpacing: '0.04em', lineHeight: 1.5 }}>{s.note}</div>}
      </div>
    </div>
  )
}
