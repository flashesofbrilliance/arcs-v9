import React from 'react'
import { border, space } from './tokens'

// Panel — flat, bordered section container. Distinct from Card: Card carries the
// glass/bevel/glow "instrument" treatment (built for receipt-grade content);
// Panel is the plain structural wrapper for grouping form fields, settings rows,
// or layout sections that shouldn't compete visually with a Card on the same screen.

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'default' | 'compact' | 'flush'
}

export function Panel({ padding = 'default', style, children, ...props }: PanelProps) {
  const paddingStyle =
    padding === 'compact' ? { padding: `${space[3]} ${space[4]}` }
    : padding === 'flush'  ? {}
    : /* default */          { padding: `${space[4]} ${space[5]}` }

  return (
    <div
      style={{
        borderRadius: 6,
        border: `1px solid ${border.subtle}`,
        background: 'transparent',
        ...paddingStyle,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  )
}
