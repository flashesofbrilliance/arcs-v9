import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"
import { loadChampions, CHAMPION_SPEC, CHAMP_SWIPE_PREFIX, type ChampionSwipe } from "@/lib/champions"

export const dynamic = "force-dynamic"

// GET /api/champions — the gated PII surface. Returns the scored champion rows, the
// rubric-as-data, and the persisted swipe state. Fail-closed: callerFor() requires
// an admin session (ADMIN_EMAILS) in production, the SAME gate as /api/jobs, so no
// unauthenticated request ever reaches the names/URLs. Dev passes through, matching
// src/lib/admin.ts doctrine. Nothing here is served to /public or a client bundle.
export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const rows = loadChampions()
  // The scored list comes from the file and needs no DB. The swipe overlay is the
  // only DB read; degrade to empty (list still renders) if the KV table is down.
  const swipes: Record<string, ChampionSwipe> = {}
  try {
    const settings = await prisma.jobBoardSetting.findMany({ where: { key: { startsWith: CHAMP_SWIPE_PREFIX } } })
    for (const s of settings) {
      try {
        swipes[s.key.slice(CHAMP_SWIPE_PREFIX.length)] = JSON.parse(s.value) as ChampionSwipe
      } catch {
        // ignore a malformed row rather than failing the whole board
      }
    }
  } catch {
    // settings store unavailable — serve the ranked list without the swipe overlay
  }

  return NextResponse.json({ rows, spec: CHAMPION_SPEC, swipes, caller: caller.kind })
}
