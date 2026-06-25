'use client'
import { useState } from 'react'
import { ProfileScanZach, type ScanDepth } from '@/document/screens/ProfileScan'
import { T } from '@/document/tokens'

const DEPTHS: { id: ScanDepth; label: string }[] = [
  { id: 'simple', label: 'Simple' },
  { id: 'rich', label: 'Rich' },
  { id: 'deep', label: 'Deep' },
]

export function ScanClient() {
  const [depth, setDepth] = useState<ScanDepth>('deep')
  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {DEPTHS.map((d) => (
          <button
            key={d.id}
            onClick={() => setDepth(d.id)}
            style={{
              fontFamily: T.mono, fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase',
              padding: '7px 16px', borderRadius: 6, cursor: 'pointer',
              background: depth === d.id ? T.green : 'transparent',
              color: depth === d.id ? T.bg : T.fg2,
              border: `1px solid ${depth === d.id ? T.green : T.border}`,
            }}
          >
            {d.label}
          </button>
        ))}
      </div>
      <ProfileScanZach depth={depth} />
    </div>
  )
}
