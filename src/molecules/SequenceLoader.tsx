'use client'
import React from 'react'
import { font, signal, text } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'

// SequenceLoader — staged "engine thinking" loader. Each stage's connector bar
// actually fills left-to-right while that stage is active, advancing down the
// list; completed stages show a check, the last stage holds an indeterminate
// fill until the real work returns and the loader unmounts. Self-animating —
// no external progress signal needed. Shared by the compass pipeline takeover
// and the brief cartography render.

export interface SequenceStage {
  id?: string   // optional short marker, e.g. "L0"
  name: string
}

export interface SequenceLoaderProps {
  title: string
  stages: SequenceStage[]
  footer?: string
  stepMs?: number   // dwell per stage before advancing
}

type RowState = 'done' | 'active' | 'last' | 'pending'

function FillBar({ state, stepMs }: { state: RowState; stepMs: number }) {
  const [w, setW] = React.useState(state === 'done' ? 100 : 0)
  React.useEffect(() => {
    if (state === 'done') { setW(100); return }
    if (state === 'pending') { setW(0); return }
    // active / last → animate from 0 toward the target on the next frame so the
    // width transition actually runs. The last stage eases to 90% and holds,
    // signalling "still working" rather than a premature complete.
    setW(0)
    const r = requestAnimationFrame(() => setW(state === 'last' ? 90 : 100))
    return () => cancelAnimationFrame(r)
  }, [state])
  const dur = state === 'last' ? stepMs * 6 : stepMs
  return (
    <div style={{ flex: 1, height: 2, borderRadius: 2, background: '#141e2e', overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${w}%`, background: signal.cyan, transition: `width ${dur}ms linear`, boxShadow: `0 0 6px ${signal.cyan}99` }} />
    </div>
  )
}

export function SequenceLoader({ title, stages, footer, stepMs = 800 }: SequenceLoaderProps) {
  const last = stages.length - 1
  const [active, setActive] = React.useState(0)
  React.useEffect(() => {
    if (active >= last) return
    const t = setTimeout(() => setActive(a => a + 1), stepMs)
    return () => clearTimeout(t)
  }, [active, last, stepMs])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2.25rem', width: '100%' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
        <Wordmark />
        <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: signal.cyan }}>{title}</span>
      </div>

      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {stages.map((s, i) => {
          const state: RowState = i < active ? 'done' : i === active ? (i === last ? 'last' : 'active') : 'pending'
          const lit = state !== 'pending'
          return (
            <div key={s.name} style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
              <span style={{ fontFamily: font.mono, fontSize: '0.85rem', width: 16, textAlign: 'center', color: lit ? signal.cyan : text.muted, textShadow: lit ? `0 0 10px ${signal.cyan}88` : 'none' }}>{lit ? '▸' : '·'}</span>
              {s.id && <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', color: lit ? text.primary : text.muted, minWidth: 26 }}>{s.id}</span>}
              <span style={{ fontFamily: font.mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', color: lit ? text.secondary : text.muted, minWidth: 0, whiteSpace: 'nowrap' }}>{s.name}</span>
              <FillBar state={state} stepMs={stepMs} />
              {state === 'done' && <span style={{ fontFamily: font.mono, fontSize: '0.7rem', color: signal.green }}>✓</span>}
              {(state === 'active' || state === 'last') && <span style={{ fontFamily: font.mono, fontSize: '0.625rem', letterSpacing: '0.08em', color: signal.cyan }}>◂ active</span>}
            </div>
          )
        })}
      </div>

      {footer && (
        <span style={{ fontFamily: font.sans, fontSize: '0.8rem', color: text.dimmed, fontStyle: 'italic' }}>{footer}</span>
      )}
    </div>
  )
}
