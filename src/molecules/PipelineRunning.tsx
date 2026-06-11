'use client'
import React from 'react'
import { font, signal } from '@/ui/tokens'
import { Spinner } from '@/ui/Spinner'
import { StepProgress } from '@/ui/StepProgress'

// PipelineRunning — Spinner + Label + StepProgress. Source: Compass.jsx.
export interface PipelineRunningProps {
  current?: number
  style?: React.CSSProperties
}

export function PipelineRunning({ current = 3, style }: PipelineRunningProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', ...style }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Spinner size={18} />
        <span style={{ fontFamily: font.mono, fontSize: 11, letterSpacing: '0.08em', color: signal.cyan }}>RUNNING L0–L5…</span>
      </div>
      <StepProgress current={current} />
    </div>
  )
}
