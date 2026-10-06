'use client'
import React, { useState } from 'react'
import { signal, text } from './tokens'

// CloseButton: the one dismiss control for bars, toasts and drawers.
// A drawn X (not a font glyph, so its weight and centering never depend on the
// fallback font), a 44px hit area, ink that passes 3:1 non-text contrast at
// rest (text.secondary on panel/obsidian is ~7:1), a hover tint in the host's
// signal color, and a cyan ring that shows for keyboard focus only.
export interface CloseButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  label: string          // specific accessible name, e.g. "Dismiss data notice"
  accent?: string        // hover ink; defaults to the bearing cyan
  size?: number          // drawn glyph size in px
}

export function CloseButton({ label, accent = signal.cyan, size = 12, style, onFocus, onBlur, onMouseEnter, onMouseLeave, ...rest }: CloseButtonProps) {
  const [hover, setHover] = useState(false)
  const [ring, setRing] = useState(false)
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onMouseEnter={(e) => { setHover(true); onMouseEnter?.(e) }}
      onMouseLeave={(e) => { setHover(false); onMouseLeave?.(e) }}
      onFocus={(e) => { setRing(e.currentTarget.matches(':focus-visible')); onFocus?.(e) }}
      onBlur={(e) => { setRing(false); onBlur?.(e) }}
      style={{
        width: 44, height: 44, flexShrink: 0, padding: 0,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        background: hover ? 'rgba(255,255,255,0.05)' : 'transparent',
        border: 'none', borderRadius: 6, cursor: 'pointer',
        color: hover ? accent : text.secondary,
        outline: ring ? `1px solid ${signal.cyan}` : 'none', outlineOffset: -6,
        transition: 'color .15s, background-color .15s',
        ...style,
      }}
      {...rest}
    >
      <svg width={size} height={size} viewBox="0 0 12 12" aria-hidden="true" focusable="false">
        <path d="M2 2L10 10M10 2L2 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    </button>
  )
}
