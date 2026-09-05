import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor, WHY_TAGS } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// POST /api/jobs/swipe  { jobid, direction: "r" | "l" | null, why?: string }
// direction null clears the swipe (undo). A right swipe files the forge request
// (status queued) if none exists; clearing a right swipe withdraws a still-queued
// request. A why tag only attaches to a left swipe.
export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  const jobid = String(body?.jobid ?? "")
  const direction = body?.direction ?? null
  const why = body?.why ?? null
  if (!jobid) return NextResponse.json({ error: "jobid required" }, { status: 400 })
  if (direction !== null && direction !== "r" && direction !== "l") return NextResponse.json({ error: "direction must be r, l, or null" }, { status: 400 })
  if (why !== null && !(WHY_TAGS as readonly string[]).includes(why)) return NextResponse.json({ error: "unknown why tag" }, { status: 400 })

  const job = await prisma.jobOpportunity.findUnique({ where: { jobid }, include: { forge: true } })
  if (!job) return NextResponse.json({ error: "no such job" }, { status: 404 })

  if (direction === null) {
    await prisma.jobSwipe.deleteMany({ where: { jobid } })
    if (job.forge?.status === "queued") await prisma.forgeRun.delete({ where: { jobid } })
  } else {
    await prisma.jobSwipe.upsert({
      where: { jobid },
      create: { jobid, direction, why: direction === "l" ? why : null, userId: caller.kind === "admin" ? caller.email : null },
      update: { direction, why: direction === "l" ? why : null, at: new Date() },
    })
    if (direction === "r" && !job.forge) {
      await prisma.forgeRun.create({ data: { jobid, status: "queued" } })
    }
    if (direction === "l" && job.forge?.status === "queued") {
      await prisma.forgeRun.delete({ where: { jobid } })
    }
  }
  const row = await prisma.jobOpportunity.findUnique({ where: { jobid }, include: { swipe: true, forge: true } })
  return NextResponse.json({ row })
}
