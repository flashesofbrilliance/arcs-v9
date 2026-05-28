// ARCS v9 design tokens — inline style constants
// Source of truth: WORLD.md palette + arcs-v9 page conventions
// Rule: inline styles only — no className, no Tailwind, no CSS modules

// ─── Surface / background hierarchy ──────────────────────────────────────────

export const surface = {
  bg:       '#020408',  // Page background
  panel:    '#0d1117',  // Cards, modules, panels
  elevated: '#111827',  // Inputs, hover states
} as const

// ─── Border ───────────────────────────────────────────────────────────────────

export const border = {
  subtle:  '#1e293b',                       // Dividers, card strokes
  active:  'rgba(122, 210, 255, 0.38)',     // Selected / active
  locked:  'rgba(255, 210, 120, 0.28)',     // Court / locked
} as const

// ─── Text ─────────────────────────────────────────────────────────────────────

export const text = {
  primary:   '#e2e8f0',  // Primary readable
  secondary: '#94a3b8',  // Secondary / supporting
  muted:     '#475569',  // Muted / labels
  dimmed:    '#64748b',  // Dimmed / metadata
} as const

// ─── Signal colors — mode state and Y-gate rendering ─────────────────────────

export const signal = {
  cyan:   '#00F0FF',  // True North, active bearing
  green:  '#00FF9D',  // Coherent / SHARP resolution
  gold:   '#FFD700',  // Court / LOCKED
  red:    '#FF4D6D',  // Alert / GRAIN resolution
  steel:  '#94a3b8',  // Default / neutral
} as const

// ─── Typography ───────────────────────────────────────────────────────────────

export const font = {
  sans: "'Inter', system-ui, -apple-system, sans-serif",
  mono: "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace",
  size: {
    xs:   '0.625rem',  // 10px
    sm:   '0.75rem',   // 12px
    md:   '0.875rem',  // 14px
    base: '1rem',      // 16px
    lg:   '1.125rem',  // 18px
    xl:   '1.25rem',   // 20px
  },
  weight: {
    normal: 400,
    medium: 500,
    bold:   700,
  },
  tracking: {
    base:   '0em',
    wide:   '0.04em',
    wider:  '0.08em',
    widest: '0.14em',
  },
} as const

// ─── Radius ───────────────────────────────────────────────────────────────────

export const radius = {
  xs:   '3px',
  sm:   '6px',
  md:   '10px',
  lg:   '16px',
  pill: '999px',
} as const

// ─── Spacing — 4px base ───────────────────────────────────────────────────────

export const space = {
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
} as const

// ─── Y-gate render resolution colors ──────────────────────────────────────────
// Maps Y state → signal color for consistent treatment across components

export const yGateColor: Record<string, string> = {
  GREEN:    signal.green,
  YELLOW:   signal.gold,
  FORK:     signal.gold,
  SCRATCH:  signal.steel,
  DELTA:    signal.steel,
  DRIFT:    signal.steel,
  PARADOX:  signal.red,
  RED:      signal.red,
}
