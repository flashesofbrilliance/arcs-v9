import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// PATCH /api/jobs/settings  { cap?: number }  — the forge concurrency cap today;
// any future board setting goes through the same key/value row.
export async function PATCH(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const b = await req.json().catch(() => null)
  if (!b || typeof b !== "object") return NextResponse.json({ error: "Bad JSON" }, { status: 400 })
  const allowed: Record<string, (v: unknown) => string | null> = {
    cap: (v) => (Number.isInteger(Number(v)) && Number(v) > 0 && Number(v) <= 99 ? String(Number(v)) : null),
  }
  const written: Record<string, string> = {}
  for (const [k, fn] of Object.entries(allowed)) {
    if (b[k] === undefined) continue
    const v = fn(b[k])
    if (v === null) return NextResponse.json({ error: `bad value for ${k}` }, { status: 400 })
    await prisma.jobBoardSetting.upsert({ where: { key: k }, create: { key: k, value: v }, update: { value: v } })
    written[k] = v
  }
  return NextResponse.json({ settings: written })
}
