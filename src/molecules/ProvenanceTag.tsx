'use client'
import { useCallback, useEffect, useState } from 'react'
import { font, text, signal, border } from '@/ui/tokens'
import { Card } from '@/ui/Card'
import { Label } from '@/ui/Label'
import { Button } from '@/ui/Button'

// ProvenanceTag: the owner's one control over Receipt.provenance ("real" | "test" | null).
// Reads and writes /api/receipts/[id]/provenance, which answers 404 to anyone but the
// owner, so this renders nothing for anonymous readers and other accounts. It never
// guesses: an untagged receipt stays untagged until the owner presses a button.

type Provenance = 'real' | 'test'

const COPY: Record<Provenance, { label: string; hint: string }> = {
  real: { label: 'Real', hint: 'a decision you actually faced; counts toward calibration' },
  test: { label: 'Test', hint: 'a probe or demo; never scored' },
}

export function ProvenanceTag({ receiptId }: { receiptId: string }) {
  const [state, setState] = useState<'loading' | 'hidden' | 'ready'>('loading')
  const [value, setValue] = useState<Provenance | null>(null)
  const [syntheticOutcome, setSyntheticOutcome] = useState(false)
  const [busy, setBusy] = useState<Provenance | null>(null)
  const [err, setErr] = useState<string | null>(null)

  const endpoint = `/api/receipts/${encodeURIComponent(receiptId)}/provenance`

  useEffect(() => {
    let cancelled = false
    fetch(endpoint)
      .then(async (r) => ({ status: r.status, data: await r.json().catch(() => ({})) }))
      .then(({ status, data }) => {
        if (cancelled) return
        if (status !== 200) { setState('hidden'); return }
        setValue(data.provenance === 'real' || data.provenance === 'test' ? data.provenance : null)
        setSyntheticOutcome(data.syntheticOutcome === true)
        setState('ready')
      })
      .catch(() => { if (!cancelled) setState('hidden') })
    return () => { cancelled = true }
  }, [endpoint])

  const tag = useCallback(async (provenance: Provenance) => {
    setBusy(provenance); setErr(null)
    try {
      const r = await fetch(endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provenance }),
      })
      const data = await r.json().catch(() => ({}))
      if (!r.ok) { setErr(data.error ?? 'Could not set provenance'); return }
      setValue(provenance)
    } catch {
      setErr('Could not set provenance')
    } finally {
      setBusy(null)
    }
  }, [endpoint])

  if (state !== 'ready') return null

  return (
    <Card padding="compact" style={{ padding: '1rem 1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
        <Label style={{ marginBottom: 0 }}>Provenance</Label>
        <span style={{ fontFamily: font.mono, fontSize: '0.6rem', letterSpacing: '0.08em', color: value ? signal.cyan : signal.gold, textTransform: 'uppercase' }}>
          {value ? value : 'untagged'}
        </span>
      </div>
      <div style={{ height: 1, background: border.subtle, margin: '0.75rem 0' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed, lineHeight: 1.5, flex: '1 1 16rem', minWidth: 0 }}>
          {value
            ? COPY[value].hint.charAt(0).toUpperCase() + COPY[value].hint.slice(1) + '.'
            : 'Only you can set this. Untagged receipts sit outside both the real and the test cohort.'}
        </span>
        <div role="group" aria-label="Provenance" style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          {(['real', 'test'] as Provenance[]).map((p) => (
            <Button
              key={p}
              variant={value === p ? 'outline-cyan' : 'ghost'}
              size="sm"
              aria-pressed={value === p}
              disabled={busy !== null || (p === 'real' && syntheticOutcome)}
              title={p === 'real' && syntheticOutcome ? 'Carries a synthetic outcome; remove it first' : COPY[p].hint}
              onClick={() => { if (value !== p) tag(p) }}
            >
              {busy === p ? '…' : COPY[p].label}
            </Button>
          ))}
        </div>
      </div>
      {err && <div role="alert" style={{ fontFamily: font.mono, fontSize: '0.65rem', color: signal.red, marginTop: '0.75rem' }}>{err}</div>}
    </Card>
  )
}
