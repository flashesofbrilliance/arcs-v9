'use client'
import React from 'react'
import { surface, border, radius, space, text, font } from './tokens'

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
    : /* default */          { padding: `${space[5]} ${space[6]}` }

  return (
    <div
      style={{
        background:   surface.panel,
        border:       `1px solid ${accent ? `${accent}33` : border.subtle}`,
        borderRadius: radius.md,
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
