'use client'
import React from 'react'
import { useRouter } from 'next/navigation'
import { font, signal, text } from '@/ui/tokens'
import { signalGlow, nciColor, getWeather, normalizeDoorClass, doorMeta, tribColor } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { AuthControl } from '@/molecules/AuthControl'
import { Rule } from '@/ui/Rule'
import { SectionLabel } from '@/ui/SectionLabel'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { Badge } from '@/ui/Badge'
import { Gauge } from '@/ui/Gauge'
import { TrueNorthPanel } from '@/instrument/TrueNorthPanel'
import type { Tributary } from '@/lib/mockCompass'

// Home — marketing/entry organism. PRESENTATIONAL: takes onOpen callback only.
// Source: compass-app/Home.jsx (verbatim layout, window atoms → ES imports).

const HOME_STEPS = [
  { n: '01', title: 'Name the real fork', body: "Most people bring the symptom. ARCS asks for the actual decision — the fork, not the friction." },
  { n: '02', title: 'The question gets stress-tested', body: "What's actually at stake. What you might be missing. The strongest case against your instinct. Whether the ground is stable enough to move." },
  { n: '03', title: 'One direction. A specific next move.', body: "Not hedged, not vague — a clear call, graded by conviction. If the terrain doesn't support confidence, ARCS says so instead of pretending it does." },
  { n: '04', title: 'The full map', body: "Why this direction. What you're trading. What to watch. What's worth asking next." },
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
  tributaries?: Tributary[]
}

// ATG (Anticipatory Tributary Generator) preview — the same 3-prompt shape
// every real receipt produces. Shown compact here (one-line chips, not the
// full TributaryTile stack) so the demo card stays roughly the height of
// the left column instead of growing past it.
const DEMO_FALLBACK: HomeDemo = {
  decision: 'Should I take the Series A now or extend runway another 6 months and grow into a higher valuation?',
  trueNorth: 'Extend runway — the valuation delta at your current growth rate outweighs the optionality cost of 6 months.',
  nciScore: 74,
  coherence: 81,
  mode: 'COURT',
  doorClass: 'ONE_WAY',
  yState: 'GREEN',
  tributaries: [
    { type: 'meta', label: 'Meta', prompt: 'What would have to be true for taking the A now to be right regardless of valuation?' },
    { type: 'challenge', label: 'Challenge', prompt: 'If the next two months miss plan, what is your recovery line on the wait?' },
    { type: 'adjacent', label: 'Adjacent', prompt: 'Does a bridge note de-risk the wait without resetting the round terms?' },
  ],
}

export interface HomeProps {
  onOpen?: () => void
  onCalibrate?: () => void
  demo?: HomeDemo | null
  demoLabel?: string
  onBrief?: () => void
}

export function Home({ onOpen, onCalibrate, demo, demoLabel, onBrief }: HomeProps) {
  const router = useRouter()
  const d = demo ?? DEMO_FALLBACK
  const w = getWeather(d.yState)
  const door = doorMeta[normalizeDoorClass(d.doorClass)]
  const gaugeC = nciColor(d.nciScore)
  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '2rem 1.5rem 5.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <Button variant="ghost" size="sm" onClick={() => router.push('/history')}>History</Button>
          <AuthControl next="/history" showWaitlist />
        </div>
      </div>
      <Rule style={{ marginBottom: '3rem' }} />

      {/* Split-screen (direction #3) — pitch and proof side by side, so a
          visitor never scrolls past one without the other. Collapses to a
          single column via auto-fit, no separate mobile breakpoint needed. */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '2.5rem', alignItems: 'stretch', marginBottom: '3rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', paddingTop: '1.25rem', paddingBottom: '1.25rem' }}>
          <SectionLabel style={{ marginBottom: '0.85rem' }}>Navigate to clarity · Make the decision visible</SectionLabel>
          <h1 style={{ fontFamily: font.sans, fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', fontWeight: 600, lineHeight: 1.1, color: text.primary, margin: '0 0 1.25rem', letterSpacing: '-0.025em' }}>
            What are you really<br />trying to decide?
          </h1>
          <p style={{ fontFamily: font.sans, fontSize: '1rem', color: text.secondary, lineHeight: 1.85, margin: '0 0 1.75rem' }}>
            Critical decisions are too important to tackle alone. When you&rsquo;re too close to the problem a fresh perspective helps. ARCS gives you a clear line of sight to the horizon line and orients you in the right direction.
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <Button size="lg" glyph="⊕" onClick={onOpen}>Open the compass&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></Button>
          </div>
        </div>

        {/* Outer box stays neutral (no colored outline/glow, matching the
            compass/receipt pages) — only the True North panel itself glows,
            same as everywhere else it appears. */}
        <Card style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
            <Label>{demoLabel ?? (demo ? 'Recent · what ARCS produces' : 'Example receipt — what ARCS produces')}</Label>
            <Badge label={`${w.icon} ${w.label}`} color={w.color} register="light" />
          </div>
          <div
            title={d.decision}
            style={{ fontFamily: font.sans, fontSize: '0.875rem', color: text.primary, marginBottom: '1rem', lineHeight: 1.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
          >
            {d.decision}
          </div>
          <TrueNorthPanel
            heading={`True North${d.mode ? ' · ' + d.mode : ''} · ${door.label}`}
            style={{ padding: '0.9rem 1.1rem', marginBottom: '0.9rem' }}
          >
            {d.trueNorth}
          </TrueNorthPanel>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'stretch', gap: '0.6rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
              <Gauge label="Conviction" value={`${d.nciScore}%`} color={gaugeC} glow={signalGlow(gaugeC)} flex="0 0 auto" minWidth={88} valueSize={22} style={{ padding: '8px 12px' }} />
              {d.coherence != null && (
                <Gauge label="Coherence" value={`${d.coherence}%`} flex="0 0 auto" minWidth={88} valueSize={22} style={{ padding: '8px 12px' }} />
              )}
            </div>
            {/* space-between + stretch: door-class pill's bottom lands flush
                with the bottom of the (taller) Coherence gauge, instead of
                both badges clinging to the top of the row. */}
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              {d.mode ? <Badge label={d.mode} color={signal.gold} register="light" /> : <span />}
              <Badge label={door.label} color={door.color} register="governance" />
            </div>
          </div>

          {d.tributaries && d.tributaries.length > 0 && (
            <div style={{ marginTop: '0.9rem' }}>
              <SectionLabel style={{ marginBottom: '0.5rem' }}>Tributaries · where to navigate next</SectionLabel>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.6rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  {d.tributaries.map((t, i) => {
                    const c = tribColor(t.type)
                    return (
                      <button
                        key={i}
                        onClick={() => { if (typeof window !== 'undefined') window.location.href = `/dashboard?q=${encodeURIComponent(t.prompt)}` }}
                        style={{
                          fontFamily: font.mono, fontSize: '0.6875rem', letterSpacing: '0.04em', fontWeight: 600, textTransform: 'uppercase',
                          color: c, background: 'transparent', border: `1px solid ${c}40`, borderRadius: 5, padding: '5px 10px', cursor: 'pointer',
                        }}
                      >
                        {t.label}
                      </button>
                    )
                  })}
                </div>

                {onBrief && (
                  <Button variant="outline-cyan" size="sm" onClick={onBrief} style={{ flexShrink: 0 }}>View brief&nbsp;→</Button>
                )}
              </div>
            </div>
          )}

          {/* Tributaries absent (no demo override provided one) — button keeps
              its own row, same right-aligned position as before. */}
          {onBrief && !(d.tributaries && d.tributaries.length > 0) && (
            <div style={{ marginTop: '1.1rem', display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="outline-cyan" size="sm" onClick={onBrief}>View the full brief&nbsp;→</Button>
            </div>
          )}
        </Card>
      </div>

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

      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50, borderTop: `1px solid ${signal.gold}25`, background: 'rgba(2,4,8,0.92)', backdropFilter: 'blur(12px)' }}>
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <span style={{ fontFamily: font.sans, fontSize: '0.75rem', lineHeight: 1.4, color: text.dimmed, maxWidth: 420 }}>
          Interested in ARCS powered sprints by Mañana?
        </span>
        <Button
          variant="gold"
          size="sm"
          onClick={() => { if (typeof window !== 'undefined') window.location.href = '/waitlist?view=advisory' }}
        >
          Inquire directly&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
        </Button>
      </div>
      </div>
    </div>
  )
}
