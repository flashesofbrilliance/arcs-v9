'use client'
import React from 'react'
import { WidgetFace } from './WidgetFace'
import { readFidelity } from './fidelity.read'
import type { FieldSource } from './reading'

export { readFidelity }

// Fidelity widget view. Imports only its own read, the shared face, and tokens/atoms.
export function FidelityView({ source }: { source: FieldSource | null | undefined }) {
  return <WidgetFace title="Fidelity" reading={readFidelity(source)} fmt={(v) => `${Math.round(v * 100)}%`} />
}
