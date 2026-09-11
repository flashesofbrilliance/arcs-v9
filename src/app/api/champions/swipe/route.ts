import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"
import { loadChampions, CHAMP_SWIPE_PREFIX, CHAMPION_WHY, type ChampionSwipe } from "@/lib/champions"

export const dynamic = "force-dynamic"

// POST /api/champions/swipe  { id, direction: "r" | "l" | null, why?: string }
// direction null clears the swipe (undo). State is a single JobBoardSetting row per
// champion (key `champ_swipe:<id>`) — no migration needed, single-tenant (User0).
// A swipe-right is the acceptance-test marker: it does NOT auto-generate the lane
// bundle. Per ADR-077 the enablement/forge is a human-approved step (mirrors the
// postings board's gate: the full forge fires when a human responds, not on a swipe).
export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const body = await req.json().catch(() => null)
  const id = String(body?.id ?? "")
  const direction = body?.direction ?? null
  const why = body?.why ?? null
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 })
  if (direction !== null && direction !== "r" && direction !== "l") return NextResponse.json({ error: "direction must be r, l, or null" }, { status: 400 })
  if (why !== null && !(CHAMPION_WHY as readonly string[]).includes(why)) return NextResponse.json({ error: "unknown why tag" }, { status: 400 })

  // Reject an id that is not one of the sourced rows (the enum of valid champions).
  if (!loadChampions().some((r) => r.id === id)) return NextResponse.json({ error: "no such champion" }, { status: 404 })

  const key = `${CHAMP_SWIPE_PREFIX}${id}`
  if (direction === null) {
    await prisma.jobBoardSetting.deleteMany({ where: { key } })
    return NextResponse.json({ ok: true, cleared: true })
  }
  const value: ChampionSwipe = { direction, why: direction === "l" ? why : null, at: new Date().toISOString() }
  const json = JSON.stringify(value)
  await prisma.jobBoardSetting.upsert({ where: { key }, create: { key, value: json }, update: { value: json } })
  return NextResponse.json({ ok: true, swipe: value })
}
