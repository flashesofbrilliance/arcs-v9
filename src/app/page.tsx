import { prisma } from '@/lib/db'
import type { HomeDemo } from '@/organisms/Home'
import { HomePageClient } from './HomePageClient'

// Landing surface. Server component: fetches the pinned featured receipt
// directly via Prisma at render time, so the correct content is in the HTML
// before it ever reaches the browser — no client fetch, no loading state, no
// flash-then-swap. (Previously this was a client component that fetched
// /api/brief/[id] after mount; that always painted Home's static fallback
// sample first and swapped once the fetch resolved, which is the flash Zach
// kept seeing — confirmed via live console tracing, not guessed.) Falls back
// to the static sample inside Home only if the pinned receipt is missing.

// Pinned featured decision shown on the homepage + linked as the example brief.
const PINNED_BRIEF_ID = 'cmqbd3i3k000104lawptiz7x0'

// Direct DB read at request time, not build time — without this Next would
// try to statically prerender the page (running the Prisma query once at
// build, baking whatever it returned into a static HTML shell forever).
export const dynamic = 'force-dynamic'

// Stored receipts are frozen records and some predate the no-em-dash rule, so the
// landing copy is scrubbed at render time instead of rewriting the row.
const noDash = (t: string) => t.replace(/\s*\u2014\s*/g, ': ')

async function getPinnedDemo(): Promise<HomeDemo | null> {
  try {
    const r = await prisma.receipt.findUnique({ where: { id: PINNED_BRIEF_ID } })
    if (!r) return null
    let tributaries = undefined
    try {
      if (r.atgTributaries) tributaries = JSON.parse(r.atgTributaries)
    } catch { /* malformed — omit */ }
    return {
      decision: noDash(r.decision ?? r.trueNorth ?? ''),
      trueNorth: noDash(r.trueNorth ?? ''),
      nciScore: r.nciScore ?? 50,
      coherence: r.coherencePct ?? null,
      mode: r.mode,
      doorClass: r.doorClass,
      yState: r.yState,
      tributaries,
    }
  } catch {
    return null
  }
}

export default async function HomePage() {
  const demo = await getPinnedDemo()
  return <HomePageClient demo={demo} pinnedBriefId={PINNED_BRIEF_ID} />
}
