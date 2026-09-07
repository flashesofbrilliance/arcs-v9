import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

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
