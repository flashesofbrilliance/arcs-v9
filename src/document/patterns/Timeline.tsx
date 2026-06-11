'use client'
import React from 'react'
import { T } from '../tokens'

export interface TimelineStep {
  label?: string
  title: string
  body: string
  peak?: boolean
}

export interface TimelineProps {
  steps: TimelineStep[]
  accent?: string
}

export function Timeline({ steps, accent = T.cyan }: TimelineProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {steps.map((step, i) => (
        <div key={i} style={{ display: 'flex', gap: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
            <div style={{ width: 34, height: 34, borderRadius: '50%', background: step.peak ? accent : T.surface, border: `1px solid ${step.peak ? accent : T.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.mono, fontSize: 11, fontWeight: 700, color: step.peak ? T.bg : T.fg3, flexShrink: 0 }}>
              {String(i + 1).padStart(2, '0')}
            </div>
            {i < steps.length - 1 && <div style={{ width: 1, flex: 1, minHeight: 18, background: `linear-gradient(180deg,${step.peak ? accent + '80' : T.border},${T.border})`, margin: '3px 0' }} />}
          </div>
          <div style={{ flex: 1, paddingBottom: 20 }}>
            {step.label && <div style={{ fontFamily: T.mono, fontSize: 9, color: step.peak ? accent : T.fg4, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>{step.label}</div>}
            <div style={{ fontFamily: T.sans, fontSize: 14, fontWeight: 600, color: step.peak ? T.fg1 : T.fg2, marginBottom: 5 }}>{step.title}</div>
            <p style={{ fontFamily: T.sans, fontSize: 13, color: T.fg3, lineHeight: 1.65 }}>{step.body}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
