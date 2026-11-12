'use client'
import React from 'react'
import { WidgetFace } from './WidgetFace'
import { readCoherence } from './coherence.read'
import type { FieldSource } from './reading'

export { readCoherence }

// Coherence widget view. Imports only its own read, the shared face, and tokens/atoms.
export function CoherenceView({ source }: { source: FieldSource | null | undefined }) {
  return <WidgetFace title="Coherence" reading={readCoherence(source)} fmt={(v) => `${Math.round(v * 100)}%`} />
}
