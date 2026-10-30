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
    primary?: { main?: string }
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
    say: p.text?.primary, show: p.success?.main, request: p.info?.main, notyet: p.warning?.main, limit: p.warning?.main, fail: p.error?.main, shift: p.secondary?.main,
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
  // 'hud' = the instrument look (default): solid key face, hairline, tone corner ticks, a 6px LED, no glow; 'field' = recessed well, underlit
  material?: 'hud' | 'field'
  // a status light that breathes (glow radius, not opacity; stops under reduced motion)
  live?: boolean
  // a verdict chip announces itself when it changes (role=status, polite)
  verdict?: boolean
  style?: React.CSSProperties
}

export function GrammarChip({ tone, children, fidelity = 'sharp', mode = 'auto', skin, muiTheme, material = 'hud', live, verdict, style }: GrammarChipProps) {
  const system = useSystemMode()
  const m: GrammarMode = mode === 'auto' ? (muiTheme?.palette?.mode ?? system) : mode
  const base = grammarChips.modes[m]
  const s: GrammarSkin = { ...(muiTheme ? skinFromMuiTheme(muiTheme) : {}), ...skin }
  const t = grammarChips.tones[tone]
  const c = s[tone] ?? t[m]
  const f = grammarChips.fidelity[fidelity]
  const sh = grammarChips.shape
  // Texture layers, same recipes as the emitted CSS (speckle; two offset dot grids for moire). Kept as
  // background layers so they compose with the face instead of being reset by a background shorthand.
  const dots = (col: string, a: string, size: string) => ({ img: `radial-gradient(${pct(col, a)} .6px, transparent .8px)`, size: `${size} ${size}` })
  const tex =
    f.texture === 'speckle' ? [dots(c, '30%', '5px')]
    : f.texture === 'interference' ? [dots(s.request ?? grammarChips.tones.request[m], '28%', '4px'), dots(s.notyet ?? grammarChips.tones.notyet[m], '24%', '4.6px')]
    : []
  const d = base.depth
  const ins = grammarChips.instrument[m]
  const L = grammarChips.led
  // HUD restraint: at rest only the glyph carries the tone; ticks and tag light up when live.
  const lit = material !== 'hud' || !!live
  const tick = lit ? c : (s.textSecondary ?? base.textSecondary)
  const ticks = (['left top', 'right top', 'left bottom', 'right bottom'] as const).flatMap((p) => [`linear-gradient(${tick}, ${tick}) ${p} / 7px 1px no-repeat`, `linear-gradient(${tick}, ${tick}) ${p} / 1px 7px no-repeat`])
  const layers = (lead: string[], fill: string): React.CSSProperties => ({
    background: [...lead, ...tex.map((x) => `${x.img} 0 0 / ${x.size}`), fill].join(', '),
  })
  const hud: React.CSSProperties = { border: `1px solid ${s.border ?? base.border}`, ...layers(ticks, s.panel ?? ins.keyFace), boxShadow: `${ins.highlight}, ${ins.lip}`, fontVariantNumeric: 'tabular-nums' }
  const face: React.CSSProperties = material === 'hud' ? hud
    : { ...layers([`linear-gradient(${pct(c, base.tint)}, ${pct(c, base.tint)})`], s.panel ?? d.face), boxShadow: `${d.well}, ${d.underlit} ${pct(c, '30%')}` }
  const ledSize = grammarChips.instrument.led.size
  const glyph: React.CSSProperties = material === 'hud' ? { color: c, fontSize: '0.85em' }
    : { color: c, textShadow: `0 0 ${L.glowRest} ${pct(c, L.alpha)}` }
  return (
    <span data-tone={tone} data-fidelity={fidelity} role={verdict ? 'status' : undefined} style={{
      position: 'relative', display: 'inline-flex', alignItems: 'center', gap: sh.gap, padding: `${sh.padY} ${sh.padX}`, maxWidth: '100%',
      borderRadius: sh.radius, border: `1px solid ${pct(c, base.edge)}`,
      color: s.text ?? base.text, fontFamily: grammarChips.fonts.sans, fontSize: sh.bodySize, lineHeight: 1.3, whiteSpace: 'nowrap', ...face, ...style,
    }}>
      {live && material === 'field' && <style>{`@keyframes g-led{to{text-shadow:0 0 ${L.glowPeak} currentColor}}@media (prefers-reduced-motion: reduce){[data-g-live]{animation:none!important}}`}</style>}
      <span aria-hidden="true" data-g-live={live ? '' : undefined} style={{ lineHeight: 1, ...glyph, ...(live && material === 'field' ? { animation: `g-led ${L.period} cubic-bezier(0.2, 0.7, 0.2, 1) infinite alternate` } : {}) }}>{t.glyph}</span>
      <span style={{ color: lit ? c : (s.textSecondary ?? base.textSecondary), fontFamily: grammarChips.fonts.mono, fontSize: sh.tagSize, fontWeight: 700, letterSpacing: '0.14em', lineHeight: 1, textTransform: 'uppercase',
        ...(material === 'hud' ? { paddingRight: 8, borderRight: `1px solid ${s.border ?? base.border}` } : {}) }}>{t.tag}</span>
      <span style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clipPath: 'inset(50%)', whiteSpace: 'nowrap' }}>: </span>
      {children != null && <span style={{ whiteSpace: 'normal', fontWeight: f.weight, letterSpacing: f.tracking }}>{children}</span>}
      {live && material === 'hud' && <>
        <style>{`@keyframes g-blink{0%,${grammarChips.instrument.led.duty}{opacity:1}${grammarChips.instrument.led.duty},100%{opacity:0}}@media (prefers-reduced-motion: reduce){[data-g-led]{animation:none!important}}`}</style>
        <span aria-hidden="true" data-g-led="" style={{ width: ledSize, height: ledSize, borderRadius: '50%', background: c, flex: 'none', animation: `g-blink ${grammarChips.instrument.led.blink} steps(1, end) infinite` }} />
      </>}
    </span>
  )
}

// For MUI apps (arcs-mini @arcs/theme): MuiChip styleOverrides that give <Chip color="info|success|warning|error|secondary">
// the same grammar. Spread into createTheme({ components: { MuiChip: muiChipOverrides() } }).
export function muiChipOverrides() {
  const sh = grammarChips.shape
  type PaletteLike = { mode?: GrammarMode; text?: { primary?: string }; background?: { paper?: string } } & Record<string, unknown>
  const tint = (key: string) => ({ theme }: { theme: { palette: PaletteLike } }) => {
    const c = (theme.palette[key] as { main?: string } | undefined)?.main
    const m = theme.palette.mode ?? 'dark'
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
