'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { surface, text, signal, font, border } from '@/ui/tokens'
import { useVw } from '@/ui/useVw'
import { useToastDrawer } from '@/ui/ToastDrawerContext'
import { FOOTER_H } from '@/ui/StickyFooter'

const TOAST_H = 36
const STORAGE_KEY = 'arcs-toast-dismissed'

const mono = font.mono
const sans = font.sans

type Depth = 'deal' | 'terms' | 'full'

const DEPTHS = [
  { id: 'deal' as Depth, label: 'The deal', sub: '30 sec' },
  { id: 'terms' as Depth, label: 'The terms', sub: '2 min' },
  { id: 'full' as Depth, label: 'Full contract', sub: 'Standalone pages' },
]

const CHIPS = [
  { label: 'Storage', body: 'Nothing stored without sign-in' },
  { label: 'Training', body: 'Input never trains a model' },
  { label: 'Autonomy', body: 'You decide. ARCS doesn\'t.' },
  { label: 'Source', body: 'Repo is public and forkable' },
]

const ROADMAP = [
  { name: 'Question Compass', desc: 'L0–L5 bearing + conviction grade + tributaries', badge: 'Live', bg: '#052e16', color: '#4ade80' },
  { name: 'Observatory', desc: 'Replay every decision as a kinematic trajectory', badge: 'Beta', bg: '#1c1917', color: signal.gold },
  { name: 'Kairos', desc: 'Detect momentum building toward a fork', badge: 'Roadmap', bg: '#0f172a', color: text.muted, bd: border.subtle },
  { name: 'Shared Court', desc: 'Multi-party deliberation, dissent on record', badge: 'Roadmap', bg: '#0f172a', color: text.muted, bd: border.subtle },
]

const COVENANT_GROUPS = [
  {
    group: 'On the product',
    rows: [
      { arcs: 'Directional clarity — not engagement optimization', you: 'Real questions with real stakes' },
      { arcs: "Surface honest limits when the terrain doesn't support confidence", you: 'Bring honest questions — rationalization breaks the compass' },
    ],
  },
  {
    group: 'On your data',
    rows: [
      { arcs: 'Never sell, share, or use decision content for advertising', you: "Don't enter data that puts others at legal risk" },
      { arcs: 'Delete within 30 days, permanently, no conditions', you: 'Understand deletion is one-way' },
    ],
  },
  {
    group: 'On the relationship',
    rows: [
      { arcs: 'Source code stays public — verify our claims yourself', you: "Don't extract from this community using our open source" },
    ],
  },
]

const FULL_SECTIONS = [
  { n: '§ 01', head: 'A navigation tool, not an answer machine', body: 'ARCS produces a directional bearing, a conviction grade, and tributaries. It does not make decisions. The bearing is an input to your judgment, not a replacement for it.' },
  { n: '§ 02', head: 'Two columns. Both matter.', body: 'ARCS commits to directional clarity, honest limits, open source, and data sovereignty. You commit to real questions and honest framing. Full covenant table at /terms.' },
  { n: '§ 03', head: 'Always. Sometimes. Never.', body: 'Input never trains a model. Anonymous sessions store nothing. Delete within 30 days, permanently. Full governance table at /privacy.' },
  { n: '§ 04', head: "What isn't built yet", body: 'Kairos detection is not live. Data export is on the roadmap. Audit log not built. The trust contract names every gap rather than hiding it.' },
]

export function EyebrowToast() {
  const [dismissed, setDismissed] = useState(false) // show on every page load
  const { open, setOpen } = useToastDrawer()
  const [depth, setDepth] = useState<Depth>('deal')
  const [copied, setCopied] = useState(false)
  const vw = useVw()
  const router = useRouter()
  const sm = vw < 640

  function dismiss(e: React.MouseEvent) {
    e.stopPropagation()
    setDismissed(true)
    setOpen(false)
  }

  function copyAddr() {
    navigator.clipboard.writeText('zachharris.eth')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function nav(path: string) {
    setOpen(false)
    router.push(path)
  }

  // Render a placeholder spacer always to avoid layout shift; zero-height when dismissed
  return (
    <>
      <div style={{ height: dismissed ? 0 : TOAST_H, flexShrink: 0 }} />

      {!dismissed && (
        <>
          {/* ── Toast bar ── */}
          <div
            role="banner"
            onClick={() => setOpen(o => !o)}
            style={{
              position: 'fixed', top: 0, left: 0, right: 0, zIndex: 110,
              height: TOAST_H,
              background: surface.panel,
              borderBottom: `0.5px solid ${border.subtle}`,
              display: 'flex', alignItems: 'center',
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            {/* Centered label */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7 }}>
              <span style={{ fontFamily: mono, fontSize: sm ? 9 : 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: signal.gold }}>
                What&apos;s the deal with my data?
              </span>
              <span style={{
                fontFamily: mono, fontSize: 9, color: `${signal.gold}77`,
                display: 'inline-block',
                transition: 'transform 0.2s',
                transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
              }}>▾</span>
            </div>

            {/* Dismiss ✕ */}
            <button
              onClick={dismiss}
              aria-label="Dismiss"
              style={{
                position: 'absolute', right: 0, top: 0, bottom: 0,
                minWidth: 44, padding: '0 12px',
                background: 'none', border: 'none', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <span style={{ fontFamily: mono, fontSize: 10, color: `${signal.gold}44`, lineHeight: 1 }}>✕</span>
            </button>
          </div>

          {/* ── Drawer ── */}
          {open && (
            <div
              style={{
                position: 'fixed', top: TOAST_H, left: 0, right: 0, zIndex: 109,
                background: surface.panel,
                borderBottom: `0.5px solid ${border.subtle}`,
                maxHeight: `calc(100vh - ${TOAST_H}px - ${FOOTER_H}px)`,
                overflowY: 'auto',
                WebkitOverflowScrolling: 'touch',
              }}
            >
              <div style={{ maxWidth: 680, margin: '0 auto', padding: sm ? '0.9rem 1rem 1.25rem' : '1rem 1.5rem 1.5rem' }}>

                {/* Depth selector */}
                <div style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                  border: `0.5px solid ${border.subtle}`, borderRadius: 8, overflow: 'hidden',
                  marginBottom: '1.1rem',
                }}>
                  {DEPTHS.map((d, i) => (
                    <button
                      key={d.id}
                      onClick={() => setDepth(d.id)}
                      style={{
                        padding: sm ? '0.55rem 0' : '0.6rem 0',
                        background: depth === d.id ? surface.bg : 'transparent',
                        border: 'none',
                        borderRight: i < 2 ? `0.5px solid ${border.subtle}` : 'none',
                        borderBottom: depth === d.id ? `2px solid ${signal.cyan}` : '2px solid transparent',
                        cursor: 'pointer',
                        textAlign: 'center',
                        transition: 'background 0.12s',
                      }}
                    >
                      <span style={{
                        display: 'block', fontFamily: mono,
                        fontSize: sm ? 8 : 10, fontWeight: 700, letterSpacing: '0.07em',
                        textTransform: 'uppercase',
                        color: depth === d.id ? '#ffffff' : text.secondary,
                        transition: 'color 0.12s',
                      }}>{d.label}</span>
                      <span style={{
                        display: 'block', fontFamily: mono,
                        fontSize: sm ? 7 : 8, fontWeight: 400, letterSpacing: '0.05em',
                        marginTop: 2,
                        color: depth === d.id ? `${signal.cyan}99` : text.muted,
                        transition: 'color 0.12s',
                      }}>{d.sub}</span>
                    </button>
                  ))}
                </div>

                {/* ─── Depth: The Deal ─── */}
                {depth === 'deal' && (
                  <div>
                    {/* Chips */}
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: sm ? '1fr 1fr' : 'repeat(4, 1fr)',
                      gap: 6, marginBottom: '1rem',
                    }}>
                      {CHIPS.map(c => (
                        <div key={c.label} style={{
                          background: surface.elevated, border: `0.5px solid ${border.subtle}`,
                          borderRadius: 7, padding: '0.55rem 0.7rem',
                        }}>
                          <div style={{ fontFamily: mono, fontSize: 8, textTransform: 'uppercase', letterSpacing: '0.1em', color: text.muted, marginBottom: '0.2rem' }}>{c.label}</div>
                          <div style={{ fontFamily: sans, fontSize: sm ? 11 : 12, color: text.primary, fontWeight: 500, lineHeight: 1.3 }}>{c.body}</div>
                        </div>
                      ))}
                    </div>

                    {/* Roadmap table */}
                    <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 7, overflow: 'hidden', marginBottom: '1rem' }}>
                      <div style={{ padding: '0.35rem 0.75rem', background: surface.elevated, borderBottom: `0.5px solid ${border.subtle}`, fontFamily: mono, fontSize: 8, letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted }}>
                        What you&apos;re entering into
                      </div>
                      {ROADMAP.map((r, i) => (
                        <div key={r.name} style={{
                          display: 'grid',
                          gridTemplateColumns: sm ? '1fr auto' : '120px 1fr auto',
                          alignItems: 'center', gap: 8,
                          padding: '0.45rem 0.75rem',
                          borderBottom: i < ROADMAP.length - 1 ? `0.5px solid ${border.subtle}` : 'none',
                        }}>
                          <div style={{ fontFamily: sans, fontSize: 12, fontWeight: 500, color: text.primary }}>{r.name}</div>
                          {!sm && <div style={{ fontFamily: sans, fontSize: 11, color: text.muted, lineHeight: 1.35 }}>{r.desc}</div>}
                          <div style={{
                            fontFamily: mono, fontSize: 8, letterSpacing: '0.05em',
                            padding: '2px 7px', borderRadius: 4, whiteSpace: 'nowrap',
                            background: r.bg, color: r.color,
                            ...(r.bd ? { border: `0.5px solid ${r.bd}` } : {}),
                          }}>{r.badge}</div>
                        </div>
                      ))}
                    </div>

                    <button
                      onClick={() => nav('/dashboard')}
                      style={{ width: '100%', padding: '0.6rem', background: 'none', border: `0.5px solid ${border.subtle}`, borderRadius: 7, fontFamily: mono, fontSize: 13, fontWeight: 700, letterSpacing: '0.06em', color: signal.cyan, cursor: 'pointer', marginBottom: '0.65rem' }}
                    >
                      Open the compass →
                    </button>
                    <div style={{ display: 'flex', gap: '1.25rem', justifyContent: 'center' }}>
                      <button onClick={() => setDepth('terms')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Read the terms</button>
                      <button onClick={() => setDepth('full')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Full contract</button>
                    </div>
                  </div>
                )}

                {/* ─── Depth: The Terms ─── */}
                {depth === 'terms' && (
                  <div>
                    {/* Covenant table */}
                    <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 7, overflow: 'hidden', marginBottom: '0.9rem' }}>
                      {!sm && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', background: surface.elevated, borderBottom: `0.5px solid ${border.subtle}` }}>
                          <div style={{ padding: '0.4rem 0.75rem', fontFamily: mono, fontSize: 8, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: signal.cyan, borderRight: `0.5px solid ${border.subtle}` }}>ARCS commits to you</div>
                          <div style={{ padding: '0.4rem 0.75rem', fontFamily: mono, fontSize: 8, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: text.primary }}>You commit to ARCS</div>
                        </div>
                      )}
                      {COVENANT_GROUPS.map(group => (
                        <div key={group.group}>
                          <div style={{ padding: '0.3rem 0.75rem', background: surface.bg, borderTop: `0.5px solid ${border.subtle}`, fontFamily: mono, fontSize: 8, letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted }}>
                            {group.group}
                          </div>
                          {group.rows.map((row, i) => (
                            sm ? (
                              <div key={i} style={{ borderTop: `0.5px solid ${border.subtle}`, padding: '0.5rem 0.75rem' }}>
                                <div style={{ fontFamily: mono, fontSize: 7, textTransform: 'uppercase', letterSpacing: '0.08em', color: signal.cyan, marginBottom: 2 }}>ARCS</div>
                                <div style={{ fontFamily: sans, fontSize: 11, color: text.secondary, lineHeight: 1.45, marginBottom: 6 }}>{row.arcs}</div>
                                <div style={{ fontFamily: mono, fontSize: 7, textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted, marginBottom: 2 }}>You</div>
                                <div style={{ fontFamily: sans, fontSize: 11, color: text.secondary, lineHeight: 1.45 }}>{row.you}</div>
                              </div>
                            ) : (
                              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderTop: `0.5px solid ${border.subtle}` }}>
                                <div style={{ padding: '0.5rem 0.75rem', fontFamily: sans, fontSize: 11, color: text.secondary, lineHeight: 1.45, borderRight: `0.5px solid ${border.subtle}` }}>{row.arcs}</div>
                                <div style={{ padding: '0.5rem 0.75rem', fontFamily: sans, fontSize: 11, color: text.secondary, lineHeight: 1.45 }}>{row.you}</div>
                              </div>
                            )
                          ))}
                        </div>
                      ))}
                    </div>

                    {/* Axiom */}
                    <div style={{ borderLeft: `2px solid ${signal.cyan}33`, paddingLeft: '0.75rem', marginBottom: '1rem' }}>
                      <div style={{ fontFamily: sans, fontSize: 13, fontWeight: 500, color: text.primary, lineHeight: 1.4 }}>Loyalty is earned through demonstrated reciprocity — not demanded through terms.</div>
                      <div style={{ fontFamily: sans, fontSize: 11, color: text.muted, marginTop: '0.2rem' }}>If ARCS breaks this covenant, you are released from it immediately.</div>
                    </div>

                    {/* ETH support */}
                    <SupportRow copied={copied} onCopy={copyAddr} sm={sm} />

                    <button
                      onClick={() => nav('/dashboard')}
                      style={{ width: '100%', padding: '0.6rem', background: 'none', border: `0.5px solid ${border.subtle}`, borderRadius: 7, fontFamily: mono, fontSize: 13, fontWeight: 700, letterSpacing: '0.06em', color: signal.cyan, cursor: 'pointer', marginBottom: '0.65rem' }}
                    >
                      Open the compass →
                    </button>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                      <button onClick={() => nav('/trust')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Trust contract</button>
                      <button onClick={() => nav('/privacy')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Privacy policy</button>
                      <button onClick={() => nav('/terms')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Terms of service</button>
                    </div>
                  </div>
                )}

                {/* ─── Depth: Full Contract ─── */}
                {depth === 'full' && (
                  <div>
                    {FULL_SECTIONS.map((s, i, arr) => (
                      <div key={s.n}>
                        <div style={{ marginBottom: '0.8rem' }}>
                          <div style={{ fontFamily: mono, fontSize: 8, letterSpacing: '0.12em', textTransform: 'uppercase', color: text.muted, marginBottom: '0.2rem' }}>{s.n}</div>
                          <div style={{ fontFamily: sans, fontSize: 13, fontWeight: 500, color: text.primary, marginBottom: '0.2rem' }}>{s.head}</div>
                          <div style={{ fontFamily: sans, fontSize: 11, color: text.secondary, lineHeight: 1.6 }}>{s.body}</div>
                        </div>
                        {i < arr.length - 1 && <div style={{ height: 1, background: border.subtle, marginBottom: '0.8rem' }} />}
                      </div>
                    ))}

                    <div style={{ height: 1, background: border.subtle, margin: '0.9rem 0' }} />
                    <SupportRow copied={copied} onCopy={copyAddr} sm={sm} />

                    <button
                      onClick={() => nav('/dashboard')}
                      style={{ width: '100%', padding: '0.6rem', background: 'none', border: `0.5px solid ${border.subtle}`, borderRadius: 7, fontFamily: mono, fontSize: 13, fontWeight: 700, letterSpacing: '0.06em', color: signal.cyan, cursor: 'pointer', marginBottom: '0.65rem' }}
                    >
                      Open the compass →
                    </button>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                      <button onClick={() => nav('/trust')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Trust contract →</button>
                      <button onClick={() => nav('/privacy')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Privacy policy →</button>
                      <button onClick={() => nav('/terms')} style={{ fontFamily: mono, fontSize: 9, color: text.muted, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Terms of service →</button>
                    </div>
                  </div>
                )}

              </div>
            </div>
          )}
        </>
      )}
    </>
  )
}

function SupportRow({ copied, onCopy, sm }: { copied: boolean; onCopy: () => void; sm: boolean }) {
  return (
    <div style={{
      border: `0.5px solid ${border.subtle}`, borderRadius: 7,
      padding: '0.6rem 0.8rem', marginBottom: '0.9rem',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem',
      flexWrap: sm ? 'wrap' : 'nowrap',
    }}>
      <div>
        <div style={{ fontFamily: mono, fontSize: 8, textTransform: 'uppercase', letterSpacing: '0.1em', color: text.muted, marginBottom: '0.2rem' }}>Support the project · USDC or ETH</div>
        <div style={{ fontFamily: mono, fontSize: sm ? 11 : 12, color: text.primary }}>zachharris.eth</div>
      </div>
      <button
        onClick={onCopy}
        style={{
          fontFamily: mono, fontSize: 9,
          color: copied ? signal.green : text.secondary,
          background: surface.elevated, border: `0.5px solid ${border.subtle}`,
          borderRadius: 5, padding: '4px 9px', cursor: 'pointer',
          whiteSpace: 'nowrap', transition: 'color 0.15s', flexShrink: 0,
        }}
      >
        {copied ? 'Copied ✓' : 'Copy address'}
      </button>
    </div>
  )
}
