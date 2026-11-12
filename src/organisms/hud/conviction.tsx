'use client'
import React from 'react'
import { WidgetFace } from './WidgetFace'
import { readConviction } from './conviction.read'
import type { FieldSource } from './reading'

export { readConviction }

// Conviction widget view. Imports only its own read, the shared face, and tokens/atoms.
export function ConvictionView({ source }: { source: FieldSource | null | undefined }) {
  return <WidgetFace title="Conviction" reading={readConviction(source)} fmt={(v) => String(v)} noSignalWhy="needs receipts tagged real" />
}
