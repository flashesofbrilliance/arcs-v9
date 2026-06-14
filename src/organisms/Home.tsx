'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { signalGlow, nciColor, getWeather, normalizeDoorClass, doorMeta } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Rule } from '@/ui/Rule'
import { SectionLabel } from '@/ui/SectionLabel'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { Badge } from '@/ui/Badge'
import { Gauge } from '@/ui/Gauge'
import { TrueNorthPanel } from '@/instrument/TrueNorthPanel'

// Home — marketing/entry organism. PRESENTATIONAL: takes onOpen callback only.
// Source: compass-app/Home.jsx (verbatim layout, window atoms → ES imports).

const HOME_STEPS = [
  { n: '01', title: 'State the decision', body: "Type what you're actually trying to decide — not the symptom, the real fork. Set horizon and stakes." },
  { n: '02', title: 'Compass runs L0–L5', body: 'Six pipeline layers in parallel: activation, adversarial challenge, Bayesian validation, immune check, NCI scoring, synthesis.' },
  { n: '03', title: 'Receive True North', body: 'One actionable sentence. Conviction grade. Render resolution calibrated to how certain the terrain actually is.' },
  { n: '04', title: 'Cartography brief', body: 'Situation framing, FATED decomposition, terrain paths, and tributaries — the full map of where you stand.' },
]

// Demo receipt for the landing's "Example · Decision Receipt" card. When a real
// recent receipt is passed it overrides the static sample; otherwise the sample
// keeps the landing rendering even on an empty DB.
export interface HomeDemo {
  decision: string
  trueNorth: string
  nciScore: number
  coherence?: number | null
  mode?: string | null
  doorClass?: string | null
  yState?: string | null
}

const DEMO_FALLBACK: HomeDemo = {
  decision: 'Should I take the Series A now or extend runway another 6 months and grow into a higher valuation?',
  trueNorth: 'Extend runway — the valuation delta at your current growth rate outweighs the optionality cost of 6 months.',
  nciScore: 74,
  coherence: 81,
  mode: 'COURT',
  doorClass: 'ONE_WAY',
  yState: 'GREEN',
}

export interface HomeProps {
  onOpen?: () => void
  demo?: HomeDemo | null
  demoLabel?: string
  onBrief?: () => void
}

export function Home({ onOpen, demo, demoLabel, onBrief }: HomeProps) {
  const d = demo ?? DEMO_FALLBACK
  const w = getWeather(d.yState)
  const door = doorMeta[normalizeDoorClass(d.doorClass)]
  const gaugeC = nciColor(d.nciScore)
  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: '2rem 1.5rem 3.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark />
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button variant="ghost" size="sm" onClick={onOpen}>Calibrate</Button>
          <Button variant="outline-cyan" size="sm" glyph="⊕" onClick={onOpen}>Open compass</Button>
        </div>
      </div>
      <Rule style={{ marginBottom: '3rem' }} />

      <div style={{ marginBottom: '3rem' }}>
        <SectionLabel style={{ marginBottom: '1.25rem' }}>Navigate to clarity · Render through the fog</SectionLabel>
        <h1 style={{ fontFamily: font.sans, fontSize: 'clamp(2.25rem, 5.5vw, 3.25rem)', fontWeight: 600, lineHeight: 1.08, color: text.primary, margin: '0 0 1.5rem', letterSpacing: '-0.025em' }}>
          What are you really<br />trying to decide?
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: '1.0625rem', color: text.secondary, lineHeight: 1.7, maxWidth: 480, margin: '0 0 2rem' }}>
          ARCS is a boardroom-grade decision intelligence layer. It maps the terrain, grades conviction, and renders clarity at the fidelity the data actually deserves.
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Button size="lg" glyph="⊕" onClick={onOpen}>Run the compass&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></Button>
          <Button variant="ghost" size="lg" onClick={() => { const el = typeof document !== 'undefined' ? document.getElementById('how') : null; if (el) window.scrollTo({ top: el.offsetTop - 24, behavior: 'smooth' }) }}>How it works</Button>
        </div>
      </div>

      {/* Bierut fix V — the featured Receipt is the conversion asset (output
          before input); the cyan underlit accent makes it read as an artifact,
          not documentation. */}
      <Card accent={signal.cyan} style={{ marginBottom: '3rem', padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <Label>{demoLabel ?? (demo ? 'Recent · Decision Receipt' : 'Example · Decision Receipt')}</Label>
          <Badge label={`${w.icon} ${w.label}`} color={w.color} register="light" />
        </div>
        <div style={{ fontFamily: font.sans, fontSize: '0.9375rem', color: text.primary, marginBottom: '1.25rem', lineHeight: 1.5 }}>
          {d.decision}
        </div>
        <TrueNorthPanel heading={`True North${d.mode ? ' · ' + d.mode : ''} · ${door.label}`} style={{ padding: '1rem 1.25rem', marginBottom: '1rem' }}>
          {d.trueNorth}
        </TrueNorthPanel>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <Gauge label="Conviction" value={String(d.nciScore)} sub="/ 100" color={gaugeC} glow={signalGlow(gaugeC)} flex="0 0 auto" minWidth={96} valueSize={26} style={{ padding: '10px 14px' }} />
          {d.coherence != null && (
            <Gauge label="Coherence" value={<>{d.coherence}<span style={{ fontSize: 15, color: text.muted }}>%</span></>} flex="0 0 auto" minWidth={96} valueSize={26} style={{ padding: '10px 14px' }} />
          )}
          <Badge label={door.label} color={door.color} register="governance" />
          {d.mode && <Badge label={d.mode} color={signal.gold} register="light" />}
        </div>
        {onBrief && (
          <div style={{ marginTop: '1.25rem' }}>
            <Button variant="outline-cyan" size="sm" glyph="◆" onClick={onBrief}>View the full brief&nbsp;→</Button>
          </div>
        )}
      </Card>

      <div id="how" style={{ marginBottom: '3rem' }}>
        <SectionLabel style={{ marginBottom: '1.5rem' }}>How it works</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {HOME_STEPS.map((step, i) => (
            <div key={step.n}>
              {i > 0 && <Rule />}
              <div style={{ display: 'grid', gridTemplateColumns: '44px 1fr', gap: '1.25rem', alignItems: 'baseline', padding: '1.1rem 0' }}>
                <div style={{ fontFamily: font.mono, fontSize: '0.75rem', color: signal.cyan, fontWeight: 700, letterSpacing: '0.1em' }}>{step.n}</div>
                <div>
                  <div style={{ fontFamily: font.sans, fontSize: '0.95rem', fontWeight: 600, color: text.primary, marginBottom: '0.3rem' }}>{step.title}</div>
                  <div style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.dimmed, lineHeight: 1.65 }}>{step.body}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Rule style={{ marginBottom: '1.5rem' }} />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <span style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed }}>Render through the fog to earned clarity.</span>
        <Button variant="outline-cyan" size="sm" glyph="⊕" onClick={onOpen}>Open compass</Button>
      </div>
    </div>
  )
}
