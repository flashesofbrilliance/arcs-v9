'use client'
import React from 'react'
import { font, signal, border, text } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { Badge } from '@/ui/Badge'
import type { TerrainPath } from '@/lib/mockCompass'

// TerrainPaths — Card listing decision paths with status-colored rails. Source: Brief.jsx.
export interface TerrainPathsProps {
  paths?: TerrainPath[]
}

export function TerrainPaths({ paths }: TerrainPathsProps) {
  const pathColor = (s: string) => s === 'selected' ? signal.cyan : s === 'blocked' ? `${signal.red}55` : border.subtle
  return (
    <Card>
      <Label style={{ marginBottom: '1rem' }}>Terrain Paths</Label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
        {paths?.map(p => (
          <div key={p.id} style={{ paddingLeft: '0.875rem', borderLeft: `2px solid ${pathColor(p.status)}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span style={{ fontFamily: font.sans, fontSize: '0.875rem', fontWeight: 600, color: p.status === 'selected' ? text.primary : text.dimmed, textDecoration: p.status === 'blocked' ? 'line-through' : 'none' }}>{p.title}</span>
              <Badge label={p.tag} color={p.status === 'selected' ? signal.cyan : signal.steel} register="light" />
              {p.status === 'selected' && <span style={{ fontFamily: font.mono, fontSize: '0.55rem', letterSpacing: '0.1em', color: signal.cyan }}>SELECTED LINE</span>}
            </div>
            <div style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed, lineHeight: 1.5 }}>{p.detail}</div>
          </div>
        ))}
      </div>
    </Card>
  )
}
