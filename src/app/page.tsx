'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { surface, text, font } from '@/ui/tokens'
import { Home, type HomeDemo } from '@/organisms/Home'
import { Button } from '@/ui/Button'

// Landing surface. Thin wrapper: routes the organism's callbacks and fetches the
// pinned featured brief for the demo card (public /api/brief — not the gated
// history). Falls back to the static sample inside Home when unavailable. The
// Home organism stays presentational (head/body F4).

// Pinned featured decision shown on the homepage + linked as the example brief.
const PINNED_BRIEF_ID = 'cmqbd3i3k000104lawptiz7x0'

export default function HomePage() {
  const router = useRouter()
  const [demo, setDemo] = useState<HomeDemo | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/brief/${PINNED_BRIEF_ID}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (cancelled || !data?.receipt) return
        const r = data.receipt
        setDemo({
          decision: r.decision ?? r.trueNorth ?? '',
          trueNorth: r.trueNorth ?? '',
          nciScore: r.nciScore ?? 50,
          coherence: r.coherencePct ?? null,
          mode: r.mode,
          doorClass: r.doorClass,
          yState: r.yState,
        })
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <Home
        demo={demo}
        demoLabel="Featured · what ARCS produces"
        onOpen={() => router.push('/dashboard')}
        onBrief={() => router.push(`/brief/${PINNED_BRIEF_ID}`)}
      />

      <div style={{ maxWidth: 620, margin: '0 auto', padding: '0 1.5rem 4rem', textAlign: 'center' }}>
        <p style={{ fontFamily: font.sans, fontSize: '0.95rem', color: text.secondary, lineHeight: 1.6, margin: '0 0 0.5rem' }}>
          Want ARCS to run with you on the decisions that matter most?
        </p>
        <p style={{ fontFamily: font.sans, fontSize: '0.85rem', color: text.dimmed, lineHeight: 1.6, margin: '0 0 1rem' }}>
          For founders and operators who want ARCS in the room when the stakes are high.
        </p>
        <Button variant="gold" size="md" glyph="◈" onClick={() => router.push('/waitlist')}>
          Work with ARCS directly →
        </Button>
      </div>
    </main>
  )
}
