'use client'
import React from 'react'
import { WidgetFace } from './WidgetFace'
import { readConsonance, type ConsonanceSource } from './consonance.read'

export { readConsonance }

// Consonance widget view. Source is the closed-receipt cohort; none is wired yet, so it prints n = 0 of 30.
export function ConsonanceView({ source }: { source: ConsonanceSource | null | undefined }) {
  return <WidgetFace title="Consonance" reading={readConsonance(source)} fmt={(v) => `${Math.round(v * 100)} pts`} />
}
