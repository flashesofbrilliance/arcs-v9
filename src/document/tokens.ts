// ARCS Document UIKit — local tokens (reader-view aesthetic)
//
// Ported faithfully from ui_kits/documents/patterns.jsx's local `const T`.
// This is a DISTINCT token set from src/ui/tokens.ts — do NOT remap onto the
// app tokens. The doc kit has its own fg3/fg4/shell values for the reader view.

export const T = {
  bg: '#020408', surface: '#0d1117', elevated: '#111827', shell: '#060a0f',
  border: '#1e293b', borderHi: 'rgba(205,225,240,0.12)',
  fg1: '#e2e8f0', fg2: '#94a3b8', fg3: '#8593a6', fg4: '#5e6975',
  cyan: '#00F0FF', green: '#00FF9D', gold: '#FFD700',
  orange: '#ff9d3c', red: '#FF4D6D', steel: '#94a3b8', purple: '#a78bfa',
  sans: "'Inter',system-ui,sans-serif",
  mono: "'JetBrains Mono','IBM Plex Mono',monospace",
} as const

export const DIM = (c: string) => `${c}16`
export const BDR = (c: string) => `${c}35`
export const GLOW = (c: string) => `${c}55`
