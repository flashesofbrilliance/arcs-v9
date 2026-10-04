import { Landing } from '@/organisms/Landing'

// Front door (2026-10-03): the survey landing, compass first, waitlist second.
// Replaced the split pitch + featured-receipt home; the featured receipt lives
// on as the "See an example brief" link. The old Home organism remains only
// for /design-test.

// Pinned featured decision, linked as the example brief.
const PINNED_BRIEF_ID = 'cmqbd3i3k000104lawptiz7x0'

export default function HomePage() {
  return <Landing variant="home" exampleBriefHref={`/brief/${PINNED_BRIEF_ID}`} />
}
