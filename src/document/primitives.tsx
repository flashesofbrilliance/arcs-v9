'use client'
// ARCS Document UIKit — shared helpers / primitive atoms.
// Faithful port of patterns.jsx: Pill, HR, MonoLabel, SectionHd, Sec, CodeBlock.

import React, { useState } from 'react'
import { T, DIM, BDR } from './tokens'

export function Pill({ children, accent, solid }: { children: React.ReactNode; accent: string; solid?: boolean }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', height: 22, padding: '0 10px',
      borderRadius: 4, fontFamily: T.mono, fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
      color: solid ? T.bg : accent,
      background: solid ? accent : DIM(accent),
      border: solid ? 'none' : `1px solid ${BDR(accent)}`,
    }}>{children}</span>
  )
}

export function HR({ accent }: { accent?: string }) {
  return <div style={{ height: 1, background: accent ? `linear-gradient(90deg,${accent}55,${T.border})` : T.border, margin: '0' }} />
}

export function MonoLabel({ children, accent }: { children: React.ReactNode; accent?: string }) {
  return (
    <span style={{ fontFamily: T.mono, fontSize: 9, fontWeight: 700, color: accent || T.fg4, letterSpacing: '0.14em', textTransform: 'uppercase' }}>
      {children}
    </span>
  )
}

export function SectionHd({ idx, label, title, accent = T.cyan }: { idx: string; label: string; title: React.ReactNode; accent?: string }) {
  return (
    <div style={{ paddingBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <MonoLabel accent={accent}>{idx} · {label}</MonoLabel>
        <div style={{ flex: 1, height: 1, background: T.border }} />
      </div>
      <h2 style={{ fontFamily: T.sans, fontSize: 20, fontWeight: 600, color: T.fg1, letterSpacing: '-0.015em', lineHeight: 1.25 }}>{title}</h2>
    </div>
  )
}

export function Sec({ id, idx, label, title, accent = T.cyan, children }: { id?: string; idx: string; label: string; title: React.ReactNode; accent?: string; children: React.ReactNode }) {
  return (
    <section id={id} style={{ padding: '40px 0 32px', borderBottom: `1px solid ${T.border}` }}>
      <SectionHd idx={idx} label={label} title={title} accent={accent} />
      {children}
    </section>
  )
}

export function CodeBlock({ code }: { code: string }) {
  const [cp, setCp] = useState(false)
  const copy = () => { navigator.clipboard?.writeText(code); setCp(true); setTimeout(() => setCp(false), 1800) }
  return (
    <div style={{ background: '#040810', border: `1px solid ${T.border}`, borderRadius: 8, marginTop: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 14px', borderBottom: `1px solid ${T.border}` }}>
        <span style={{ fontFamily: T.mono, fontSize: 9, color: T.fg4, letterSpacing: '.12em' }}>JSX · ARCS DOCUMENT UIKIT</span>
        <button onClick={copy} style={{ fontFamily: T.mono, fontSize: 9, color: cp ? T.green : T.fg4, background: 'transparent', border: 'none', cursor: 'pointer' }}>{cp ? 'COPIED ✓' : 'COPY'}</button>
      </div>
      <pre style={{ fontFamily: T.mono, fontSize: 12, color: '#94a3b8', lineHeight: 1.75, padding: '14px 16px', margin: 0, overflowX: 'auto', whiteSpace: 'pre' }}>{code}</pre>
    </div>
  )
}
