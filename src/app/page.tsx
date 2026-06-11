'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { surface, text } from '@/ui/tokens'
import { Home, type HomeDemo } from '@/organisms/Home'

// Landing surface. Thin wrapper: routes the organism's callbacks and fetches the
// latest real receipt for the demo card (falls back to the static sample inside
// Home when none exists). The Home organism stays presentational (head/body F4).

export default function HomePage() {
  const router = useRouter()
  const [demo, setDemo] = useState<HomeDemo | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch('/api/history')
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (cancelled || !data?.receipts?.length) return
        const r = data.receipts[0]
        setDemo({
          decision: r.decision ?? r.trueNorth ?? '',
          trueNorth: r.trueNorth ?? '',
          nciScore: r.nciScore ?? 50,
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
      <Home demo={demo} onOpen={() => router.push('/dashboard')} />
    </main>
  )
}
