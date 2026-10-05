import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// PATCH /api/jobs/settings  { cap?, clearMissed?, revive?, dismissDrift? } — the forge concurrency cap,
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
  // Slice 2 board actions (never a JobSwipe, so no preference is written for Zach):
  // clearMissed marks every row scored before now "not reviewed"; revive puts one
  // row back in the live queue; dismissDrift silences the current drift signature.
  const set = async (k: string, v: string) => { await prisma.jobBoardSetting.upsert({ where: { key: k }, create: { key: k, value: v }, update: { value: v } }); written[k] = v }
  if (b.clearMissed === true) await set("missed_cleared_at", new Date().toISOString())
  if (typeof b.revive === "string" && b.revive) {
    const cur = await prisma.jobBoardSetting.findUnique({ where: { key: "missed_revived" } })
    let list: string[] = []; try { list = JSON.parse(cur?.value ?? "[]") } catch { list = [] }
    if (!list.includes(b.revive)) list.push(b.revive)
    await set("missed_revived", JSON.stringify(list.slice(-500)))
  }
  if (typeof b.dismissDrift === "string" && /^[a-z<>=|0-9]{1,64}$/.test(b.dismissDrift)) await set("drift_dismissed", b.dismissDrift)
  for (const [k, fn] of Object.entries(allowed)) {
    if (b[k] === undefined) continue
    const v = fn(b[k])
    if (v === null) return NextResponse.json({ error: `bad value for ${k}` }, { status: 400 })
    await prisma.jobBoardSetting.upsert({ where: { key: k }, create: { key: k, value: v }, update: { value: v } })
    written[k] = v
  }
  return NextResponse.json({ settings: written })
}
