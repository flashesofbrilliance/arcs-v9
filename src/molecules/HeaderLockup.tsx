'use client'
import React from 'react'
import { Wordmark } from '@/ui/Wordmark'
import { Button } from '@/ui/Button'
import { Rule } from '@/ui/Rule'

// HeaderLockup — Wordmark + action Button + Rule. Source: Home · Result · Compass.
export interface HeaderLockupProps {
  section?: string
  actionLabel?: string
  actionGlyph?: React.ReactNode
  onAction?: () => void
  ruleStyle?: React.CSSProperties
}

export function HeaderLockup({
  section = 'Receipt',
  actionLabel = 'New question',
  actionGlyph = '←',
  onAction,
  ruleStyle,
}: HeaderLockupProps) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
        <Wordmark section={section} />
        <Button variant="ghost" size="sm" glyph={actionGlyph} onClick={onAction}>{actionLabel}</Button>
      </div>
      <Rule style={ruleStyle} />
    </div>
  )
}
