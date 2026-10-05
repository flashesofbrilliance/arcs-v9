import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"
import { drift, weekdaysBetween, NO_SWIPE_WEEKDAYS } from "@/lib/board-drift"

// GET /api/jobs/drift — Job Factory slice 2. The backlog drift signal as one JSON
// object, so the 8:15 morning task can put a single line in its summary even when
// Zach has not opened the board (the signal keys on the backlog, not on sessions).
// Read-only; admin session or pipeline token, same posture as the rest of /api/jobs.
export const dynamic = "force-dynamic"

export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const spec = JSON.parse(fs.readFileSync(path.join(process.cwd(), "runtime", "specs", "target-role-scan.json"), "utf8"))
  const [rows, settings] = await Promise.all([
    prisma.jobOpportunity.findMany({ select: { jobid: true, band: true, composite: true, scoredAt: true, firstSeen: true, swipe: { select: { at: true } } } }),
    prisma.jobBoardSetting.findMany(),
  ])
  // Intake stall: a live source whose watermark has not advanced in NO_SWIPE_WEEKDAYS
  // weekdays. Found 2026-10-05: the LinkedIn source sat at 2026-09-11 for 3.5 weeks
  // while every morning run reported "succeeded" in ~15s. A run that does nothing
  // must not read as a run that worked.
  const now = new Date()
  const stalled = (await prisma.source.findMany({ where: { status: "live", adapter: { not: "manual" } } }))
    .map((src) => ({ key: src.key, since: src.watermark ?? src.lastRunAt }))
    .filter((x) => !x.since || weekdaysBetween(x.since, now) >= NO_SWIPE_WEEKDAYS)
    .map((x) => ({ key: x.key, since: x.since?.toISOString() ?? null, weekdays: x.since ? weekdaysBetween(x.since, now) : null }))
  const d = drift(
    rows.map((r) => ({ ...r, scoredAt: r.scoredAt?.toISOString() ?? null, firstSeen: r.firstSeen.toISOString(), swipe: r.swipe ? { at: r.swipe.at.toISOString() } : null })),
    Object.fromEntries(settings.map((s) => [s.key, s.value])),
    now,
    Number(spec?.rubric?.board_cutoff ?? 0.52),
  )
  const intakeLine = stalled.length ? `Intake stalled: ${stalled.map((x) => `${x.key} has not advanced since ${x.since?.slice(0, 10) ?? "never"}${x.weekdays != null ? ` (${x.weekdays} weekdays)` : ""}`).join("; ")}.` : null
  return NextResponse.json({ ...d, intakeStalled: stalled, intakeLine, fire: d.fire || stalled.length > 0 })
}
