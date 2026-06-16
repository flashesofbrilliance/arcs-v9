// ARCS v9 design tokens — inline style constants
// Source of truth: WORLD.md palette + arcs-v9 page conventions
// Rule: inline styles only — no className, no Tailwind, no CSS modules
import type React from 'react'

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
  cyan:    '#00F0FF',  // True North, active bearing
  green:   '#00FF9D',  // Coherent / SHARP resolution
  gold:    '#FFD700',  // Court / LOCKED
  orange:  '#ff9d3c',  // Warning / macro-tag
  red:     '#FF4D6D',  // Alert / GRAIN resolution
  steel:   '#94a3b8',  // Default / neutral
  violet:  '#A78BFA',  // DELTA · conviction shift
  magenta: '#E879F9',  // PARADOX · curator
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
  // Six graded mono label tiers (Bierut fix II). As a tier rises: size up,
  // tracking down, weight holds — so the map legend stops reading like the
  // coastline. Color stays caller-controlled (it's semantic). Spread onto a
  // mono element: style={{ fontFamily: font.mono, ...font.tier.t3 }}.
  tier: {
    t1: { fontSize: '0.594rem', fontWeight: 700, letterSpacing: '0.16em' }, // 9.5px · section index
    t2: { fontSize: '0.625rem', fontWeight: 700, letterSpacing: '0.14em' }, // 10px  · section label
    t3: { fontSize: '0.656rem', fontWeight: 700, letterSpacing: '0.12em' }, // 10.5px · field label
    t4: { fontSize: '0.6875rem', fontWeight: 600, letterSpacing: '0.10em' }, // 11px · instrument value
    t5: { fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em' }, // 12px · signal callout
    t6: { fontSize: '0.8125rem', fontWeight: 700, letterSpacing: '0.06em' }, // 13px · section heading
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

// ─── Y-state → terrain weather reading ───────────────────────────────────────
// Mirrors the kit's Y_WEATHER (compass-app primitives.jsx). label = zone name,
// icon = glyph, color = signal tint. Used by WeatherBar / Result header.

export interface WeatherReading { label: string; icon: string; color: string }

// NOTE: must cover EVERY state ygate.ts can emit (GREEN YELLOW RED FORK SCRATCH
// DELTA PARADOX DRIFT LOCKED). An unmapped state is a bug — use getWeather(), which
// guards against the silent GREEN fallback (RED rendering as "Clarity Ridge" would
// invert its meaning — RED is the free-solo/ruin-exposure topology, WORLD.md).
export const yWeather: Record<string, WeatherReading> = {
  GREEN:   { label: 'CLARITY RIDGE',         icon: '▲', color: signal.green },
  YELLOW:  { label: 'PRESSURE BAND',         icon: '◈', color: signal.gold },
  RED:     { label: 'EXPOSED · RUIN EDGE',   icon: '✕', color: signal.red },
  FORK:    { label: 'FORK · PATH SELECTION', icon: '⊕', color: signal.cyan },
  SCRATCH: { label: 'FOG LAYER · ORIENT',    icon: '~', color: text.muted },
  DELTA:   { label: 'CONVICTION SHIFT',      icon: '△', color: signal.violet },
  PARADOX: { label: 'PARADOX · CURATOR',     icon: '∞', color: signal.magenta },
  DRIFT:   { label: 'DRIFT · SPIN CYCLE',    icon: '↻', color: signal.steel },
  LOCKED:  { label: 'KAIROS LOCK · LOCKED',  icon: '◆', color: signal.cyan },
}

// Resolve a y_state to its weather reading. Falls back to SCRATCH (fog/orient —
// the honest "unknown terrain" reading), and in dev warns loudly so a new ygate
// state can never silently masquerade as a different one.
export const getWeather = (yState: string | null | undefined): WeatherReading => {
  if (yState && yWeather[yState]) return yWeather[yState]
  if (process.env.NODE_ENV !== 'production') {
    console.warn(`[yWeather] unmapped y_state "${yState}" — add it to yWeather. Falling back to SCRATCH.`)
  }
  return yWeather.SCRATCH
}

// ─── Tributary type → color (canonical: Result.jsx tribColor) ────────────────

export const tribColor = (type: string): string =>
  type === 'meta' ? signal.cyan
  : type === 'challenge' ? signal.red
  : type === 'adjacent' ? signal.gold
  : signal.steel

// ─── Render resolution → earned-fidelity style (WORLD.md render scale) ────────

export const resStyle: Record<string, React.CSSProperties> = {
  SHARP:    { opacity: 1.0,  fontWeight: 500, letterSpacing: '0' },
  DEGRADED: { opacity: 0.85, fontWeight: 400, letterSpacing: '0.01em' },
  GRAIN:    { opacity: 0.70, fontWeight: 300, letterSpacing: '0.02em' },
  MOIRE:    { opacity: 0.60, fontWeight: 300, letterSpacing: '0.03em' },
}

// ─── NCI score → signal color ────────────────────────────────────────────────

export const nciColor = (s: number): string =>
  s >= 70 ? signal.green : s >= 45 ? signal.gold : signal.red

// glow tint for a signal color (used by instrument readouts)
export const signalGlow = (c: string): string =>
  c === signal.green ? 'rgba(0,255,157,.6)'
  : c === signal.gold ? 'rgba(255,215,0,.55)'
  : c === signal.red  ? 'rgba(255,77,109,.55)'
  : c === signal.cyan ? 'rgba(0,240,255,.55)'
  : 'rgba(160,180,210,.35)'

// ─── Canonical door_class vocabulary (F9) ────────────────────────────────────
// Live /api/compass emits ONE_WAY | TWO_WAY. The kit mock's legacy "REVERSIBLE"
// maps to TWO_WAY. Normalize at the API boundary so DoorBadge has one vocabulary.

export type DoorClass = 'ONE_WAY' | 'TWO_WAY'

export const normalizeDoorClass = (raw: string | null | undefined): DoorClass =>
  raw === 'ONE_WAY' ? 'ONE_WAY' : 'TWO_WAY'  // REVERSIBLE / null / TWO_WAY → TWO_WAY

export const doorMeta: Record<DoorClass, { label: string; color: string }> = {
  ONE_WAY: { label: 'ONE-WAY DOOR', color: signal.gold },   // irreversible · weigh hard
  TWO_WAY: { label: 'TWO-WAY DOOR', color: signal.green },  // reversible · move
}

// ── Responsive container grid ──────────────────────────────────────────────
// contentContainer: brief, receipt, history, dashboard, debrief
// formContainer:    prep (deliberately narrower — it's a form, not a document)
export function contentContainer(vw: number): React.CSSProperties {
  const maxWidth = vw >= 1440 ? 1280 : vw >= 1100 ? 1100 : vw >= 768 ? 960 : "100%"
  const px = vw >= 1440 ? "3rem" : vw >= 1100 ? "2.5rem" : vw >= 768 ? "2rem" : vw >= 481 ? "1.5rem" : "1rem"
  return { maxWidth, margin: "0 auto", paddingLeft: px, paddingRight: px }
}
export function formContainer(vw: number): React.CSSProperties {
  const maxWidth = vw >= 1100 ? 640 : vw >= 768 ? 580 : "100%"
  const px = vw >= 768 ? "2rem" : "1.5rem"
  return { maxWidth, margin: "0 auto", paddingLeft: px, paddingRight: px }
}
