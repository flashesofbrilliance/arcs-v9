'use client'
import React from 'react'
import { T } from '../tokens'

export interface ProcessStep {
  label?: string
  title: string
  body: string
  active?: boolean
}

export interface ProcessStepsProps {
  steps: ProcessStep[]
  accent?: string
}

export function ProcessSteps({ steps, accent = T.cyan }: ProcessStepsProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {steps.map((step, i) => (
        <div key={i} style={{ display: 'flex', gap: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
            <div style={{ width: 32, height: 32, borderRadius: '50%', background: step.active ? accent : T.surface, border: `1px solid ${step.active ? accent : T.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.mono, fontSize: 11, fontWeight: 700, color: step.active ? T.bg : T.fg3 }}>{i + 1}</div>
            {i < steps.length - 1 && <div style={{ width: 1, flex: 1, minHeight: 14, background: `linear-gradient(180deg,${step.active ? accent + '70' : T.border},${T.border})`, margin: '3px 0' }} />}
          </div>
          <div style={{ flex: 1, paddingBottom: 18 }}>
            {step.label && <div style={{ fontFamily: T.mono, fontSize: 9, color: step.active ? accent : T.fg4, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 3 }}>{step.label}</div>}
            <div style={{ fontFamily: T.sans, fontSize: 14, fontWeight: 600, color: step.active ? T.fg1 : T.fg2, marginBottom: 4 }}>{step.title}</div>
            <p style={{ fontFamily: T.sans, fontSize: 13, color: T.fg3, lineHeight: 1.65 }}>{step.body}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
