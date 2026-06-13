'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Rule } from '@/ui/Rule'
import { SectionLabel } from '@/ui/SectionLabel'
import { Field } from '@/ui/Field'
import { TributaryTile } from '@/instrument/TributaryTile'
import { HorizonStakesRow } from '@/molecules/HorizonStakesRow'
import { PipelineTakeover } from '@/molecules/PipelineTakeover'
import { AuthControl } from '@/molecules/AuthControl'

// CompassForm — Question Compass organism. PRESENTATIONAL: controlled inputs via
// value/onChange, work via onSubmit, progress via running/step. Parent owns the
// pipeline (no fetch/api here). Source: compass-app/Compass.jsx.

const EXAMPLES = [
  'Should I take the Series A now or extend runway six months?',
  'Do I make the leverage hire this quarter or wait?',
]

export interface CompassFormProps {
  question: string
  horizon: string
  stakes: string
  running?: boolean
  step?: number
  onQuestionChange: (value: string) => void
  onHorizonChange: (value: string) => void
  onStakesChange: (value: string) => void
  onCalibrate?: () => void
  onSubmit: () => void
  onHistory?: () => void
}

export function CompassForm({
  question, horizon, stakes, running, step = 0,
  onQuestionChange, onHorizonChange, onStakesChange, onCalibrate, onSubmit, onHistory,
}: CompassFormProps) {
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim() || running) return
    onSubmit()
  }
  return (
    <div style={{ maxWidth: 620, margin: '0 auto', padding: '2rem 1.5rem 4rem', containerType: 'inline-size' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark section="Question Compass" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <Button variant="ghost" size="sm" onClick={onHistory}>History</Button>
          <AuthControl next="/history" />
        </div>
      </div>
      <Rule style={{ marginBottom: '2rem' }} />

      <SectionLabel index="01" style={{ marginBottom: '0.9rem' }}>State the decision</SectionLabel>
      <h1 style={{ fontFamily: font.sans, fontSize: '5.4cqw', whiteSpace: 'nowrap', fontWeight: 600, color: text.primary, margin: '0 0 1.5rem', lineHeight: 1.12, letterSpacing: '-0.02em' }}>
        What are you really trying to decide?
      </h1>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <Field as="textarea" rows={3} label="Decision" value={question} onChange={e => onQuestionChange(e.target.value)}
            placeholder="Type the real fork — not the symptom." />
          <HorizonStakesRow horizon={horizon} stakes={stakes} onHorizonChange={onHorizonChange} onStakesChange={onStakesChange} />
        </div>

        {/* Bierut fix III — one bindu per screen. Get True North is the single
            primary action; calibration collapses to a quiet modifier beneath it,
            so the ready user never has to choose which button to press. */}
        <Button type="submit" variant="primary" size="lg" glyph={running ? '~' : '⊕'} disabled={running || !question.trim()} style={{ width: '100%', marginTop: '1.5rem' }}>
          {running ? 'Running L0–L5 pipeline…' : <>Get True North&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></>}
        </Button>

        {!running && (
          <button type="button" onClick={onCalibrate}
            style={{ display: 'block', margin: '0.85rem auto 0', background: 'none', border: 'none', cursor: 'pointer', fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: text.dimmed }}>
            ◈ &nbsp;Sharpen the read — stakes, confidence &amp; context
          </button>
        )}

        {running && <PipelineTakeover current={step} />}
      </form>

      {!question && (
        <div style={{ marginTop: '2rem' }}>
          <SectionLabel style={{ marginBottom: '0.75rem' }}>Or start from an example</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {EXAMPLES.map(ex => (
              <TributaryTile key={ex} label="Example" glyph="⊕" color={signal.cyan} onClick={() => onQuestionChange(ex)}>{ex}</TributaryTile>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
