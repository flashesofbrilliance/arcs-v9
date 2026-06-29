'use client'

import { useRouter } from 'next/navigation'
import { surface, text } from '@/ui/tokens'
import { Home, type HomeDemo } from '@/organisms/Home'

// Thin client wrapper — only exists to bind router callbacks (useRouter
// requires a client component). All data arrives as a prop, already
// resolved server-side by page.tsx; no fetch, no loading state, no flash.
export function HomePageClient({ demo, pinnedBriefId }: { demo: HomeDemo | null; pinnedBriefId: string }) {
  const router = useRouter()
  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <Home
        demo={demo}
        demoLabel="Featured · what ARCS produces"
        onOpen={() => router.push('/dashboard')}
        onBrief={() => router.push(`/brief/${pinnedBriefId}`)}
      />
    </main>
  )
}
