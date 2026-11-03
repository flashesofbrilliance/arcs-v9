'use client'
import React from 'react'
import { font, text, signal, border, surface, resStyle } from '@/ui/tokens'
import type { TerrainPath, Tributary } from '@/lib/mockCompass'

// Verdict-first panel (Zach, 2026-11-02): the call, the one move, and what would
// change it, above everything else on the receipt and the brief.
//
// Earned fidelity (WORLD.md): text stays at full opacity at every depth. Fog is
// shown by the fidelity meter, the grain overlay and the weight of the call,
// never by dimming the words. A fogged call says what it is missing instead of
// apologizing in prose.

const FIDELITY: Record<string, { step: number; label: string; color: string }> = {
  SHARP:    { step: 4, label: 'Sharp',    color: signal.green },
  DEGRADED: { step: 3, label: 'Degraded', color: signal.gold },
  GRAIN:    { step: 2, label: 'Grain',    color: signal.red },
  MOIRE:    { step: 1, label: 'Moire',    color: signal.magenta },
}

// Fine noise for fogged calls. Inline SVG turbulence, no asset, no stylesheet.
const GRAIN_BG = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.09'/%3E%3C/svg%3E")`

export interface VerdictPanelProps {
  trueNorth: string
  resolution: string
  weather: { icon: string; label: string; color: string }
  verdictLabel: string
  paths: TerrainPath[]
  questions: Tributary[]
  /** Inputs the call was made without (e.g. "Facts", "Moves"). Rendered as the fog line. */
  missing: string[]
  facts: [string, string][]
}

export function VerdictPanel({ trueNorth, resolution, weather, verdictLabel, paths, questions, missing, facts }: VerdictPanelProps) {
  const fid = FIDELITY[resolution] ?? FIDELITY.GRAIN
  const rs = resStyle[resolution] ?? resStyle.GRAIN
  const move = paths.find((p) => p.status === 'selected') ?? paths.find((p) => p.status !== 'blocked') ?? null
  const changer = questions.find((q) => q.type === 'challenge') ?? null
  const fogged = fid.step < 3

  return (
    <section
      aria-labelledby="slot-verdict"
      style={{
        position: 'relative',
        border: `1px solid ${border.subtle}`,
        borderTop: `2px solid ${fid.color}`,
        borderRadius: 6,
        background: surface.panel,
        backgroundImage: fogged ? GRAIN_BG : undefined,
        padding: 'clamp(1.1rem, 3.5vw, 1.75rem)',
      }}
    >
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.6rem 1rem', marginBottom: '1rem' }}>
        <div id="slot-verdict" style={{ fontFamily: font.mono, ...font.tier.t6, textTransform: 'uppercase', color: signal.cyan }}>{verdictLabel}</div>
        <FidelityMeter step={fid.step} label={fid.label} color={fid.color} weather={weather} />
      </div>

      <h1 style={{ fontFamily: font.sans, fontSize: 'clamp(1.3rem, 3.2vw, 1.9rem)', lineHeight: 1.3, color: text.primary, margin: 0, textWrap: 'pretty', letterSpacing: rs.letterSpacing, fontWeight: Math.max(Number(rs.fontWeight ?? 400), 400) + 100 }}>
        {trueNorth}
      </h1>

      {facts.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem 1.25rem', marginTop: '0.9rem' }}>
          {facts.map(([k, v]) => (
            <span key={k} style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.muted, whiteSpace: 'nowrap' }}>
              {k} <span style={{ color: text.primary }}>{v}</span>
            </span>
          ))}
        </div>
      )}

      {(move || changer) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(240px, 100%), 1fr))', gap: '1px', marginTop: '1.5rem', background: border.subtle, border: `1px solid ${border.subtle}`, borderRadius: 4, overflow: 'hidden' }}>
          {move && <Cell kicker="First move" color={signal.green} title={move.title} body={move.detail} />}
          {changer && <Cell kicker="What would change this" color={signal.gold} body={changer.prompt} />}
        </div>
      )}

      {missing.length > 0 && (
        <p style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: text.muted, margin: '1rem 0 0' }}>
          Called without: <span style={{ color: fid.color }}>{missing.join(' · ')}</span>
        </p>
      )}
    </section>
  )
}

function FidelityMeter({ step, label, color, weather }: { step: number; label: string; color: string; weather: { icon: string; label: string; color: string } }) {
  return (
    <div role="img" aria-label={`Fidelity ${label}, ${step} of 4. Y state ${weather.label}.`} style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.4rem 0.6rem' }}>
      <span style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: weather.color, whiteSpace: 'nowrap' }}>{weather.icon} {weather.label}</span>
      <span aria-hidden style={{ display: 'flex', gap: 3 }}>
        {[1, 2, 3, 4].map((i) => (
          <span key={i} style={{ width: 14, height: 6, borderRadius: 1, background: i <= step ? color : 'transparent', border: `1px solid ${i <= step ? color : text.muted}` }} />
        ))}
      </span>
      <span style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color: text.primary, whiteSpace: 'nowrap' }}>{label}</span>
    </div>
  )
}

function Cell({ kicker, color, title, body }: { kicker: string; color: string; title?: string; body: string }) {
  return (
    <div style={{ background: surface.bg, padding: '0.9rem 1rem', minWidth: 0 }}>
      <div style={{ fontFamily: font.mono, ...font.tier.t3, textTransform: 'uppercase', color, marginBottom: '0.4rem' }}>{kicker}</div>
      {title && <div style={{ fontFamily: font.sans, fontSize: '0.95rem', fontWeight: 600, color: text.primary, lineHeight: 1.4, marginBottom: '0.25rem', textWrap: 'pretty' }}>{title}</div>}
      <p style={{ fontFamily: font.sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.55, margin: 0, textWrap: 'pretty' }}>{body}</p>
    </div>
  )
}
