'use client'
import React, { useEffect, useState } from 'react'
import { grammarChips, type GrammarFidelity, type GrammarMode, type GrammarTone } from './grammarChipTokens'

// GrammarChip: the claim chip grammar (runtime/specs/grammar-chips.json) as a self-contained JSX atom.
// Same look as src/ui-kit/grammar-chips/chips.html. Works with no theme (ARCS world, dark or light),
// or skinned by any MUI-shaped theme object (duck-typed; this file does not import MUI).

export type GrammarSkin = Partial<Record<GrammarTone | 'panel' | 'border' | 'text' | 'textSecondary', string>>

// The subset of an MUI theme this reads. Pass `useTheme()` from @mui/material straight in.
export interface MuiThemeLike {
  palette?: {
    mode?: 'light' | 'dark'
    info?: { main?: string }; success?: { main?: string }; warning?: { main?: string }
    error?: { main?: string }; secondary?: { main?: string }
    text?: { primary?: string; secondary?: string }
    background?: { paper?: string }
    divider?: string
  }
}

// Map an MUI theme onto the grammar. Same mapping as applySkin() in chips.html.
export function skinFromMuiTheme(theme: MuiThemeLike): GrammarSkin {
  const p = theme.palette ?? {}
  return {
    say: p.info?.main, show: p.success?.main, limit: p.warning?.main, fail: p.error?.main, shift: p.secondary?.main,
    neutral: p.text?.secondary, panel: p.background?.paper, border: p.divider, text: p.text?.primary, textSecondary: p.text?.secondary,
  }
}

function useSystemMode(): GrammarMode {
  const [mode, setMode] = useState<GrammarMode>('dark')
  useEffect(() => {
    const q = window.matchMedia('(prefers-color-scheme: light)')
    const on = () => setMode(q.matches ? 'light' : 'dark')
    on(); q.addEventListener('change', on)
    return () => q.removeEventListener('change', on)
  }, [])
  return mode
}

const pct = (hex: string, p: string) => `color-mix(in srgb, ${hex} ${p}, transparent)`

export interface GrammarChipProps {
  tone: GrammarTone
  children?: React.ReactNode
  fidelity?: GrammarFidelity
  mode?: GrammarMode | 'auto'
  skin?: GrammarSkin
  muiTheme?: MuiThemeLike
  // 'hud' = hairline, tone corner ticks, no glow (default); 'field' = recessed well, underlit; 'pocket' = the dj.arcs.care Pocket skin
  material?: 'hud' | 'field' | 'pocket'
  // a status light that breathes (glow radius, not opacity; stops under reduced motion)
  live?: boolean
  style?: React.CSSProperties
}

export function GrammarChip({ tone, children, fidelity = 'sharp', mode = 'auto', skin, muiTheme, material = 'hud', live, style }: GrammarChipProps) {
  const system = useSystemMode()
  const m: GrammarMode = mode === 'auto' ? (muiTheme?.palette?.mode ?? system) : mode
  const base = grammarChips.modes[m]
  const s: GrammarSkin = { ...(muiTheme ? skinFromMuiTheme(muiTheme) : {}), ...skin }
  const t = grammarChips.tones[tone]
  const c = s[tone] ?? t[m]
  const f = grammarChips.fidelity[fidelity]
  const sh = grammarChips.shape
  const texture =
    f.texture === 'speckle' ? { backgroundImage: `radial-gradient(${pct(c, '30%')} .6px, transparent .8px)`, backgroundSize: '5px 5px' }
    : f.texture === 'interference' ? { backgroundImage: `repeating-linear-gradient(60deg, ${pct(s.say ?? grammarChips.tones.say[m], '18%')} 0 1px, transparent 1px 4px), repeating-linear-gradient(-60deg, ${pct(s.limit ?? grammarChips.tones.limit[m], '14%')} 0 1px, transparent 1px 5px)` }
    : {}
  const d = base.depth
  const pk = grammarChips.skins.pocket[m]
  const pocket = material === 'pocket'
  const led = grammarChips.tones[tone].dark
  const L = grammarChips.led
  const ticks = (['left top', 'right top', 'left bottom', 'right bottom'] as const).flatMap((p) => [`linear-gradient(${c}, ${c}) ${p} / 7px 1px no-repeat`, `linear-gradient(${c}, ${c}) ${p} / 1px 7px no-repeat`]).join(', ')
  const hud: React.CSSProperties = { border: `1px solid ${s.border ?? base.border}`, background: `${ticks}, ${s.panel ?? base.panel}`, fontVariantNumeric: 'tabular-nums', ...(live ? { boxShadow: `inset 0 -1px 0 ${c}` } : {}) }
  const face: React.CSSProperties = material === 'hud' ? hud : pocket
    ? { borderRadius: grammarChips.skins.pocket.radius, border: `1px solid ${pk.keyEdge}`, background: pk.key, boxShadow: pk.keyShadow, padding: '6px 12px 6px 6px' }
    : { background: `linear-gradient(${pct(c, base.tint)}, ${pct(c, base.tint)}), ${s.panel ?? d.face}`, boxShadow: `${d.well}, ${d.underlit} ${pct(c, '30%')}` }
  const glyph: React.CSSProperties = pocket
    ? { display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 22, height: 22, borderRadius: 3, background: pk.ledWell, boxShadow: pk.ledWellShadow, border: `1px solid ${base.border}`, fontSize: '0.8em', color: led, textShadow: `0 0 6px ${pct(led, '60%')}` }
    : material === 'hud' ? { color: c, fontSize: '0.85em' }
    : { color: c, textShadow: `0 0 ${L.glowRest} ${pct(c, L.alpha)}` }
  return (
    <span data-tone={tone} data-fidelity={fidelity} style={{
      display: 'inline-flex', alignItems: 'center', gap: sh.gap, padding: `${sh.padY} ${sh.padX}`, maxWidth: '100%',
      borderRadius: sh.radius, border: `1px solid ${pct(c, base.edge)}`,
      ...texture,
      color: s.text ?? base.text, fontFamily: grammarChips.fonts.sans, fontSize: sh.bodySize, lineHeight: 1.3, whiteSpace: 'nowrap', ...face, ...style,
    }}>
      {live && material === 'field' && <style>{`@keyframes g-led{to{text-shadow:0 0 ${L.glowPeak} currentColor}}@media (prefers-reduced-motion: reduce){[data-g-live]{animation:none!important}}`}</style>}
      <span aria-hidden="true" data-g-live={live ? '' : undefined} style={{ lineHeight: 1, ...glyph, ...(live && material === 'field' ? { animation: `g-led ${L.period} cubic-bezier(0.2, 0.7, 0.2, 1) infinite alternate` } : {}) }}>{t.glyph}</span>
      <span style={{ color: c, fontFamily: grammarChips.fonts.mono, fontSize: sh.tagSize, fontWeight: 700, letterSpacing: '0.12em', lineHeight: 1 }}>{t.tag}</span>
      {children != null && <span style={{ whiteSpace: 'normal', fontWeight: f.weight, letterSpacing: f.tracking }}>{children}</span>}
    </span>
  )
}

// For MUI apps (arcs-mini @arcs/theme): MuiChip styleOverrides that give <Chip color="info|success|warning|error|secondary">
// the same grammar. Spread into createTheme({ components: { MuiChip: muiChipOverrides() } }).
export function muiChipOverrides() {
  const sh = grammarChips.shape
  const tint = (key: string) => ({ theme }: { theme: { palette: Record<string, any> } }) => {
    const c = theme.palette[key]?.main
    const m = (theme.palette.mode ?? 'dark') as GrammarMode
    return c ? { color: theme.palette.text?.primary, border: `1px solid ${pct(c, grammarChips.modes[m].edge)}`, backgroundColor: `color-mix(in srgb, ${c} ${grammarChips.modes[m].tint}, ${theme.palette.background?.paper})` } : {}
  }
  return {
    styleOverrides: {
      root: { borderRadius: sh.radius, fontFamily: grammarChips.fonts.sans, fontSize: sh.bodySize, height: 'auto', padding: `${sh.padY} 0` },
      label: { paddingLeft: sh.padX, paddingRight: sh.padX },
      colorInfo: tint('info'), colorSuccess: tint('success'), colorWarning: tint('warning'), colorError: tint('error'), colorSecondary: tint('secondary'),
    },
  }
}
