'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { surface, text } from '@/ui/tokens'
import { Home, type HomeDemo } from '@/organisms/Home'

// Landing surface. Thin wrapper: routes the organism's callbacks and fetches the
// pinned featured brief for the demo card (public /api/brief — not the gated
// history). Falls back to the static sample inside Home when unavailable. The
// Home organism stays presentational (head/body F4).

// Pinned featured decision shown on the homepage + linked as the example brief.
const PINNED_BRIEF_ID = 'cmqbd3i3k000104lawptiz7x0'
const DEMO_CACHE_KEY = `arcs_home_demo_${PINNED_BRIEF_ID}`

// Per toolbar feedback (JqKzfbYZdK1-): the real pinned brief loads async, so
// the first paint always starts from Home's static fallback sample and swaps
// once the fetch resolves — a visible flash on every fresh load, and on a
// slow/flaky connection it can look like it "reverts" if the swap is still
// pending when someone glances back at the tab. Caching the last successful
// fetch in sessionStorage lets repeat views in the same tab paint the real
// card immediately, with no fallback-then-swap flash at all.
function readCachedDemo(): HomeDemo | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.sessionStorage.getItem(DEMO_CACHE_KEY)
    return raw ? (JSON.parse(raw) as HomeDemo) : null
  } catch {
    return null
  }
}

export default function HomePage() {
  const router = useRouter()
  const [demo, setDemo] = useState<HomeDemo | null>(() => {
    const cached = readCachedDemo()
    // TEMP DEBUG (remove after diagnosis) — trace exactly what each render
    // paints and why, to catch the flash/revert without guessing.
    console.log('[HOME DEBUG] init state:', cached ? `cached:${cached.decision.slice(0, 30)}` : 'null (fallback)')
    return cached
  })

  useEffect(() => {
    console.log('[HOME DEBUG] HomePage mounted')
    let cancelled = false
    fetch(`/api/brief/${PINNED_BRIEF_ID}`)
      .then((r) => {
        console.log('[HOME DEBUG] fetch status:', r.status, 'cancelled:', cancelled)
        return r.ok ? r.json() : null
      })
      .then((data) => {
        console.log('[HOME DEBUG] fetch resolved, has receipt:', !!data?.receipt, 'cancelled:', cancelled)
        if (cancelled || !data?.receipt) return
        const r = data.receipt
        const next: HomeDemo = {
          decision: r.decision ?? r.trueNorth ?? '',
          trueNorth: r.trueNorth ?? '',
          nciScore: r.nciScore ?? 50,
          coherence: r.coherencePct ?? null,
          mode: r.mode,
          doorClass: r.doorClass,
          yState: r.yState,
        }
        console.log('[HOME DEBUG] setDemo (real):', next.decision.slice(0, 30))
        setDemo(next)
        try { window.sessionStorage.setItem(DEMO_CACHE_KEY, JSON.stringify(next)) } catch {}
      })
      .catch((err) => console.log('[HOME DEBUG] fetch error:', err))
    return () => {
      console.log('[HOME DEBUG] HomePage cleanup (cancelled=true)')
      cancelled = true
    }
  }, [])

  useEffect(() => {
    console.log('[HOME DEBUG] demo state changed:', demo ? demo.decision.slice(0, 30) : 'null (will render fallback)')
  }, [demo])

  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <Home
        demo={demo}
        demoLabel="Featured · what ARCS produces"
        onOpen={() => router.push('/dashboard')}
        onBrief={() => router.push(`/brief/${PINNED_BRIEF_ID}`)}
      />
    </main>
  )
}
