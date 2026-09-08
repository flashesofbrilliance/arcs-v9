import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

export const LANE_STAGES = ["research", "qualify", "apply", "interview", "outcome"] as const

// jobs.arcs.care/api/jobs/lane — Compass Lane surfaces backend.
// GET: sources + recent ingest requests (the Sources surface can refresh).
// POST: file an IngestRequest over a date range (the "run a search" control).
// The request is queued; the sweep executes it asynchronously. Admin session or
// the pipeline token (callerFor) required, same posture as the rest of /api/jobs.
export const dynamic = "force-dynamic"

export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const [sources, requests] = await Promise.all([
    prisma.source.findMany({ orderBy: [{ status: "asc" }, { key: "asc" }] }),
    prisma.ingestRequest.findMany({ orderBy: { requestedAt: "desc" }, take: 20 }),
  ])
  return NextResponse.json({ sources, requests, caller })
}

const SORT: Record<string, number> = { live: 0, detected: 1, proposed: 2, paused: 3 }

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  const sourceKey = String(body?.sourceKey ?? "")
  if (!sourceKey) return NextResponse.json({ error: "sourceKey required" }, { status: 400 })
  const src = await prisma.source.findUnique({ where: { key: sourceKey } })
  if (!src) return NextResponse.json({ error: "no such source" }, { status: 404 })
  const from = body?.fromDate ? String(body.fromDate) : null
  const to = body?.toDate ? String(body.toDate) : null
  const request = await prisma.ingestRequest.create({
    data: {
      sourceKey,
      fromDate: from,
      toDate: to,
      query: body?.query ? String(body.query) : null,
      status: "queued",
      note: `filed from the lane · window ${from ?? "…"} to ${to ?? "…"}`,
      requestedBy: caller.kind,
    },
  })
  return NextResponse.json({ ok: true, request, sort: SORT[src.status] ?? 9 })
}

// PATCH — move a card between kanban columns by hand (mark applied, advance the
// interview loop). laneStage overrides the derived bucket; null clears the
// override and the row falls back to its derived stage.
export async function PATCH(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  // Complete an IngestRequest: the consumer (scripts/jobs_ingest_consume.mjs +
  // Gmail read) calls this after posting new rows, to mark the request done and
  // advance the source watermark so the next sweep reads only newer mail.
  if (body?.requestId) {
    const id = String(body.requestId)
    const status = ["done", "failed", "running"].includes(body?.status) ? String(body.status) : "done"
    const rowsAdded = body?.rowsAdded != null ? Number(body.rowsAdded) : null
    const reqRow = await prisma.ingestRequest.update({
      where: { id }, data: { status, rowsAdded, completedAt: status === "running" ? null : new Date() },
    }).catch(() => null)
    if (!reqRow) return NextResponse.json({ error: "no such request" }, { status: 404 })
    if (status === "done" && body?.watermark) {
      await prisma.source.update({ where: { key: reqRow.sourceKey }, data: { watermark: new Date(String(body.watermark)), lastRunAt: new Date(), lastError: null } }).catch(() => {})
    }
    if (status === "failed" && body?.error) {
      await prisma.source.update({ where: { key: reqRow.sourceKey }, data: { lastRunAt: new Date(), lastError: String(body.error).slice(0, 300) } }).catch(() => {})
    }
    return NextResponse.json({ ok: true, requestId: id, status, rowsAdded })
  }

  const jobid = String(body?.jobid ?? "")
  if (!jobid) return NextResponse.json({ error: "jobid required" }, { status: 400 })

  const stage = body?.laneStage === null ? null : String(body?.laneStage ?? "")
  if (stage !== null && !(LANE_STAGES as readonly string[]).includes(stage)) {
    return NextResponse.json({ error: `laneStage must be one of ${LANE_STAGES.join(", ")} or null` }, { status: 400 })
  }
  const job = await prisma.jobOpportunity.findUnique({ where: { jobid } })
  if (!job) return NextResponse.json({ error: "no such job" }, { status: 404 })
  const updated = await prisma.jobOpportunity.update({
    where: { jobid },
    data: { laneStage: stage, laneStatus: body?.laneStatus != null ? String(body.laneStatus) : job.laneStatus, laneMovedAt: new Date() },
  })
  return NextResponse.json({ ok: true, jobid, laneStage: updated.laneStage, laneStatus: updated.laneStatus })
}
