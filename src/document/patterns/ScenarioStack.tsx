'use client'
import React, { useState } from 'react'
import { T, DIM, BDR } from '../tokens'
import { Pill } from '../primitives'

export interface Scenario {
  title?: string
  body: string
  note?: string
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
  const [active, setActive] = useState<SKey>('best')
  const s = scenarios[active]
  const cfg = SCFG[active]
  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        {Object.values(SCFG).map(c => (
          <button key={c.key} onClick={() => setActive(c.key)} style={{ height: 30, padding: '0 14px', borderRadius: 7, cursor: 'pointer', fontFamily: T.mono, fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase',
            background: active === c.key ? DIM(c.color) : 'transparent', color: active === c.key ? c.color : T.fg4, border: `1px solid ${active === c.key ? BDR(c.color) : T.border}`, transition: 'all .14s' }}>
            {c.label}
          </button>
        ))}
      </div>
      <div key={active} className="fadein" style={{ padding: '18px 20px', borderRadius: 10, background: T.surface, border: `1px solid ${BDR(cfg.color)}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <Pill accent={cfg.color}>{cfg.label}</Pill>
          {s.title && <span style={{ fontFamily: T.sans, fontSize: 15, fontWeight: 600, color: T.fg1 }}>{s.title}</span>}
        </div>
        <p style={{ fontFamily: T.sans, fontSize: 14, color: T.fg2, lineHeight: 1.7 }}>{s.body}</p>
        {s.note && <div style={{ marginTop: 10, padding: '7px 11px', borderRadius: 5, background: DIM(cfg.color), fontFamily: T.mono, fontSize: 11, color: cfg.color, letterSpacing: '0.04em', lineHeight: 1.5 }}>{s.note}</div>}
      </div>
    </div>
  )
}
