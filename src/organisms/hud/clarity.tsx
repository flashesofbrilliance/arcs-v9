'use client'
import React from 'react'
import { WidgetFace } from './WidgetFace'
import { readClarity } from './clarity.read'
import type { FieldSource } from './reading'

export { readClarity }

// Clarity widget view. Imports only its own read, the shared face, and tokens/atoms.
export function ClarityView({ source }: { source: FieldSource | null | undefined }) {
  return <WidgetFace title="Clarity" reading={readClarity(source)} fmt={(v) => `${Math.round(v * 100)}%`} />
}
