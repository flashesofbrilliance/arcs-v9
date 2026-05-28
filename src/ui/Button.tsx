'use client'
import React from 'react'
import { font, radius, signal, surface, text, border } from './tokens'

// variant controls visual intent:
//   primary  — filled, high-contrast; use for the single main action
//   ghost    — transparent border; secondary actions, nav-level controls
//   danger   — red-signal fill; destructive or irreversible actions

export type ButtonVariant = 'primary' | 'ghost' | 'danger'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled,
  style,
  children,
  ...props
}: ButtonProps) {
  const sizeStyle: React.CSSProperties =
    size === 'sm'
      ? { fontSize: font.size.sm, padding: '4px 12px', borderRadius: radius.sm }
      : size === 'lg'
      ? { fontSize: font.size.base, padding: '10px 24px', borderRadius: radius.md }
      : /* md */ { fontSize: font.size.md, padding: '7px 18px', borderRadius: radius.sm }

  const variantStyle: React.CSSProperties =
    variant === 'ghost'
      ? {
          background:  'transparent',
          border:      `1px solid ${border.subtle}`,
          color:       text.secondary,
        }
      : variant === 'danger'
      ? {
          background:  `${signal.red}18`,
          border:      `1px solid ${signal.red}50`,
          color:       signal.red,
        }
      : /* primary */ {
          background:  signal.cyan,
          border:      `1px solid ${signal.cyan}`,
          color:       surface.bg,
        }

  return (
    <button
      disabled={disabled}
      style={{
        display:        'inline-flex',
        alignItems:     'center',
        justifyContent: 'center',
        gap:            '0.4em',
        fontFamily:     font.sans,
        fontWeight:     font.weight.bold,
        letterSpacing:  font.tracking.wide,
        cursor:         disabled ? 'not-allowed' : 'pointer',
        opacity:        disabled ? 0.45 : 1,
        transition:     'opacity 0.15s ease',
        whiteSpace:     'nowrap',
        lineHeight:     1,
        ...sizeStyle,
        ...variantStyle,
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  )
}
