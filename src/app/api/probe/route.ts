import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { rateLimit, clientIp } from "@/lib/ratelimit"

export const dynamic = "force-dynamic"

// POST /api/probe — record a demand-probe interaction in a table we own.
// GET  /api/probe?probe=mcp-connector — counts for the ADR-076 build gate.
//
// Why: the "I'd use this" button on good.arcs.care/blog/nftt fired only a Vercel
// custom event. That count lives in Vercel, cannot be deduped, and vanishes for
// any visitor whose blocker eats /_vercel/insights. A signal that gates a build
// belongs in our own table ("receipts or it didn't happen"). The Vercel event
// still fires alongside this; the two should roughly agree.
//
// Privacy: no IP or user agent is stored. `vid` is a random id the page keeps in
// localStorage; it exists only so repeat clicks from one browser count once.

const PROBES = new Set(["mcp-connector"])
const ACTIONS = new Set(["view", "interest"])
const VID_RE = /^[a-z0-9-]{8,64}$/
const CORS: Record<string, string> = { "Access-Control-Allow-Origin": "*" }

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: { ...CORS, "Access-Control-Allow-Methods": "POST, GET, OPTIONS", "Access-Control-Allow-Headers": "content-type" },
  })
}

export async function POST(req: NextRequest) {
  const rl = rateLimit(`probe:${clientIp(req)}`, { limit: 30, windowMs: 60_000 })
  if (!rl.ok) return NextResponse.json({ error: "slow down" }, { status: 429, headers: { ...CORS, "Retry-After": String(rl.retryAfterSec) } })

  const body = await req.json().catch(() => ({}))
  const probe = typeof body?.probe === "string" ? body.probe : ""
  const action = typeof body?.action === "string" ? body.action : ""
  const surface = typeof body?.surface === "string" ? body.surface.slice(0, 32) : "nftt"
  const vid = typeof body?.vid === "string" && VID_RE.test(body.vid) ? body.vid : null
  const path = typeof body?.path === "string" ? body.path.slice(0, 200) : null
  if (!PROBES.has(probe) || !ACTIONS.has(action)) {
    return NextResponse.json({ error: "unknown probe or action" }, { status: 400, headers: CORS })
  }

  // One "interest" per visitor id: a reload-and-click-again counts once.
  if (action === "interest" && vid) {
    const dup = await prisma.demandSignal.findFirst({ where: { probe, action, vid }, select: { id: true } })
    if (dup) return new NextResponse(null, { status: 204, headers: CORS })
  }

  await prisma.demandSignal.create({ data: { probe, action, surface, vid, path } })
  return new NextResponse(null, { status: 204, headers: CORS })
}

export async function GET(req: NextRequest) {
  const rl = rateLimit(`probe-read:${clientIp(req)}`, { limit: 60, windowMs: 60_000 })
  if (!rl.ok) return NextResponse.json({ error: "slow down" }, { status: 429, headers: CORS })
  const probe = req.nextUrl.searchParams.get("probe") ?? "mcp-connector"
  if (!PROBES.has(probe)) return NextResponse.json({ error: "unknown probe" }, { status: 400, headers: CORS })

  const [views, interest, interestVisitors, first, last] = await Promise.all([
    prisma.demandSignal.count({ where: { probe, action: "view" } }),
    prisma.demandSignal.count({ where: { probe, action: "interest" } }),
    prisma.demandSignal.findMany({ where: { probe, action: "interest", vid: { not: null } }, distinct: ["vid"], select: { vid: true } }),
    prisma.demandSignal.findFirst({ where: { probe }, orderBy: { createdAt: "asc" }, select: { createdAt: true } }),
    prisma.demandSignal.findFirst({ where: { probe }, orderBy: { createdAt: "desc" }, select: { createdAt: true } }),
  ])
  return NextResponse.json(
    { probe, views, interest, interestVisitors: interestVisitors.length, first: first?.createdAt ?? null, last: last?.createdAt ?? null },
    { headers: { ...CORS, "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300" } },
  )
}
