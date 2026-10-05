import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"
import { effective, applyChange, SETTING_KEY } from "@/lib/autonomy"

// /api/jobs/autonomy — Job Factory slice 4. The autonomy dial as flags.
// GET: the effective mode per station (defaults overlaid by stored values; locked
// stations always show their fixed mode). The 8:15 morning task reads this first
// and obeys it: Off = skip the station, Ask = prepare and list for Zach, Auto = run.
// PATCH { autonomy: { station: mode } }: admin session ONLY. The pipeline token can
// read the dial but never write it, so the system cannot raise its own autonomy.
export const dynamic = "force-dynamic"

export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const row = await prisma.jobBoardSetting.findUnique({ where: { key: SETTING_KEY } })
  return NextResponse.json({ stations: effective(row?.value) })
}

export async function PATCH(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  if (caller.kind === "pipeline") return NextResponse.json({ error: "the dial is Zach's: sign in to change autonomy" }, { status: 403 })
  const body = await req.json().catch(() => null)
  const row = await prisma.jobBoardSetting.findUnique({ where: { key: SETTING_KEY } })
  const r = applyChange(row?.value, body?.autonomy)
  if ("error" in r) return NextResponse.json({ error: r.error }, { status: 400 })
  const value = JSON.stringify(r.next)
  await prisma.jobBoardSetting.upsert({ where: { key: SETTING_KEY }, create: { key: SETTING_KEY, value }, update: { value } })
  return NextResponse.json({ stations: effective(value) })
}
