'use client'
import React from 'react'
import { font, signal, text, formContainer } from '@/ui/tokens'
import { useVw } from '@/ui/useVw'
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
  'What have I built that is mine to carry anywhere? And where can I break it into pieces, spread it, and grow it into the next thing?',
  'Which of my skills and relationships travel with me? Where is the highest-leverage place to replant them?',
]

// The meta-tributary beneath the portable-capital opener: the deeper fork the
// literal question already implies. Same verbs (atomize, germinate), opposite
// polarity. Rendered as a real meta-tributary, not a third example, because it
// is the tributary[0] the compass would surface anyway.
const META_TRIBUTARY = 'Am I using AI to compound what is mine, or am I dissolving into it?'

export interface CompassFormProps {
  question: string
  horizon: string
  stakes: string
  running?: boolean
  onQuestionChange: (value: string) => void
  onHorizonChange: (value: string) => void
  onStakesChange: (value: string) => void
  onCalibrate?: () => void
  onSubmit: () => void
  onHistory?: () => void
  error?: React.ReactNode   // failure notice, rendered under the action so the form never jumps
}

export function CompassForm({
  question, horizon, stakes, running,
  onQuestionChange, onHorizonChange, onStakesChange, onCalibrate, onSubmit, onHistory, error,
}: CompassFormProps) {
  const vw = useVw()
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim() || running) return
    onSubmit()
  }
  return (
    <div style={{ ...formContainer(vw), paddingTop: '2rem', paddingBottom: '6rem', containerType: 'inline-size' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark section="Question Compass" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <Button variant="ghost" size="sm" onClick={onHistory}>History</Button>
          <AuthControl next="/history" />
        </div>
      </div>
      <Rule style={{ marginBottom: '2rem' }} />

      <SectionLabel index="01" style={{ marginBottom: '0.9rem' }}>Name what you&apos;re actually deciding</SectionLabel>
      <h1 style={{ fontFamily: font.sans, fontSize: 'clamp(1.5rem, 1.1rem + 2.2cqw, 2.1rem)', textWrap: 'balance', fontWeight: 600, color: text.primary, margin: '0 0 1.5rem', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
        What are you really trying to decide?
      </h1>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <Field as="textarea" rows={3} label="Decision" value={question} onChange={e => onQuestionChange(e.target.value)}
            placeholder="What have I built that is mine to carry anywhere? Where should I plant it to grow next?" />
          <HorizonStakesRow horizon={horizon} stakes={stakes} onHorizonChange={onHorizonChange} onStakesChange={onStakesChange} />
        </div>

        {/* Bierut fix III — one bindu per screen. Get True North is the single
            primary action; calibration collapses to a quiet modifier beneath it,
            so the ready user never has to choose which button to press. */}
        <Button type="submit" variant="primary" size="lg" glyph={running ? '~' : '⊕'} disabled={running || !question.trim()} style={{ width: '100%', marginTop: '1.5rem', opacity: running || question.trim() ? undefined : 0.75 }}>
          {running ? 'Reading the terrain…' : <>Get True North&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></>}
        </Button>

        {!running && (
          <button type="button"
            aria-disabled={!question.trim()}
            onClick={() => { if (question.trim()) onCalibrate?.() }}
            style={{ display: 'block', margin: '0.85rem auto 0', padding: '0.75rem 0.5rem', background: 'none', border: 'none', cursor: question.trim() ? 'pointer' : 'default', fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: question.trim() ? text.dimmed : text.muted }}>
            Add context: stakes, confidence, and what you already know
          </button>
        )}

        {error && <div style={{ marginTop: '1.25rem' }}>{error}</div>}

        {running && <PipelineTakeover />}
      </form>

      {!question && (
        <div style={{ marginTop: '2rem' }}>
          <SectionLabel style={{ marginBottom: '0.75rem' }}>Point at what compounds, not what you fear losing. Try one:</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {EXAMPLES.map(ex => (
              <TributaryTile key={ex} label="Example" glyph="⊕" color={signal.cyan} onClick={() => onQuestionChange(ex)}>{ex}</TributaryTile>
            ))}
            <TributaryTile label="Meta" glyph="◆" color={signal.gold} onClick={() => onQuestionChange(META_TRIBUTARY)}>{META_TRIBUTARY}</TributaryTile>
          </div>
        </div>
      )}
    </div>
  )
}
