'use client'
import React from 'react'
import { border, space, text, font } from './tokens'

// Card — the primary content container in arcs-v9
//
// accent: optional signal color applied to the border (e.g. signal.cyan for True North)
// padding: 'default' (1.25rem 1.5rem) | 'compact' (0.875rem 1rem) | 'flush' (0 — host manages)

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  accent?: string
  padding?: 'default' | 'compact' | 'flush'
}

export function Card({ accent, padding = 'default', style, children, ...props }: CardProps) {
  const paddingStyle =
    padding === 'compact' ? { padding: `${space[3]} ${space[4]}` }
    : padding === 'flush'  ? {}
    : /* default */          { padding: '1.25rem 1.5rem' }

  // accent → signal glass with an underlit-LED finish (tight glow + inset
  // bottom-up bloom); default → neutral semi-opaque glass with a subtle bevel.
  const glass: React.CSSProperties = accent
    ? {
        border: `1px solid ${accent}45`,
        background: `linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${accent}1c, #0a1620)`,
        boxShadow: `inset 0 1px 0 ${accent}80, inset 0 -11px 17px -11px ${accent}55, 0 0 8px ${accent}26, 0 5px 16px rgba(0,0,0,.5)`,
      }
    : {
        border: '1px solid #1c2738',
        background: 'linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,.04), inset 0 -2px 8px rgba(0,0,0,.4)',
      }

  return (
    <div
      style={{
        borderRadius: 4,
        ...glass,
        ...paddingStyle,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  )
}

// CardHeader — optional label row at the top of a Card

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string
  accent?: string
}

export function CardHeader({ label, accent, style, children, ...props }: CardHeaderProps) {
  return (
    <div
      style={{
        display:       'flex',
        alignItems:    'center',
        justifyContent: children ? 'space-between' : 'flex-start',
        marginBottom:  space[3],
        ...style,
      }}
      {...props}
    >
      <span style={{
        fontSize:      font.size.xs,
        fontFamily:    font.mono,
        fontWeight:    font.weight.bold,
        letterSpacing: font.tracking.widest,
        textTransform: 'uppercase' as const,
        color:         accent ?? text.muted,
      }}>
        {label}
      </span>
      {children}
    </div>
  )
}

// CardDivider — horizontal rule inside a Card

export function CardDivider({ style, ...props }: React.HTMLAttributes<HTMLHRElement>) {
  return (
    <hr
      style={{
        border:     'none',
        borderTop:  `1px solid ${border.subtle}`,
        margin:     `${space[4]} 0`,
        ...style,
      }}
      {...props}
    />
  )
}
