import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

// Admin health / diagnostics endpoint (ADR-006 direction; built 2026-09-24 after
// a ~6-week silent persistence outage — prod was missing Receipt.batonId because
// a migration shipped in code but never reached the DB via `prisma migrate deploy`).
// This turns that class of RCA (which took 20 min of Vercel log-diving) into one
// request. It is READ-ONLY and NEVER returns env values — only presence booleans.
//
// Two modes:
//   GET /api/health            → shallow liveness {status, db}. Public — safe for
//                                uptime monitors. No internals leaked.
//   GET /api/health?deep=1     → full diagnostics. Gated: admin session (ADMIN_EMAILS)
//                                OR `Authorization: Bearer <CRON_SECRET>` (so a future
//                                staleness cron can call it). Fail-closed in prod.
export const dynamic = "force-dynamic"

// The exact drift that caused the outage: Prisma's create/read returns ALL model
// columns, so a single missing column 500s the whole route. Probing findFirst on
// each core model reproduces that failure and names the offending column (P2022).
const CORE_MODELS = ["receipt", "brief", "outcome", "prepSession", "sageTrace", "tribune"] as const

// Presence only — values are NEVER read or returned.
const REQUIRED_ENV = [
  "DATABASE_URL", "ANTHROPIC_API_KEY", "AUTH_SECRET", "AUTH_RESEND_KEY", "SAGE_URL",
] as const

const STALE_RECEIPT_DAYS = 7

async function deepAuthorized(req: NextRequest): Promise<boolean> {
  if (process.env.NODE_ENV !== "production") return true // dev pass-through (matches admin.ts doctrine)
  const bearer = req.headers.get("authorization")
  if (process.env.CRON_SECRET && bearer === `Bearer ${process.env.CRON_SECRET}`) return true
  return isAdmin(await auth())
}

export async function GET(req: NextRequest) {
  // Shallow liveness — always available, no internals.
  let dbOk = false
  try {
    await prisma.$queryRaw`SELECT 1`
    dbOk = true
  } catch {
    dbOk = false
  }

  const deep = req.nextUrl.searchParams.get("deep")
  if (!deep) {
    return NextResponse.json(
      { status: dbOk ? "ok" : "down", db: dbOk, ts: new Date().toISOString() },
      { status: dbOk ? 200 : 503 },
    )
  }

  if (!(await deepAuthorized(req))) {
    return NextResponse.json({ error: "deep diagnostics require admin or bearer token" }, { status: 401 })
  }

  // 1. Per-model schema probe — catches missing columns (the batonId class).
  const models: Record<string, { ok: boolean; error?: string }> = {}
  for (const m of CORE_MODELS) {
    try {
      // @ts-expect-error dynamic model access is intentional here
      await prisma[m].findFirst({ take: 1 })
      models[m] = { ok: true }
    } catch (err) {
      models[m] = { ok: false, error: err instanceof Error ? err.message.split("\n").slice(-3).join(" ").slice(0, 300) : String(err) }
    }
  }

  // 2. Persistence freshness — a stale newest-receipt is the signal that would
  //    have caught this outage in days, not weeks.
  let lastReceipt: { at: string | null; ageDays: number | null; stale: boolean } = { at: null, ageDays: null, stale: false }
  try {
    const r = await prisma.receipt.findFirst({ orderBy: { createdAt: "desc" }, select: { createdAt: true } })
    if (r) {
      const ageDays = (Date.now() - r.createdAt.getTime()) / 86400000
      lastReceipt = { at: r.createdAt.toISOString(), ageDays: Math.round(ageDays * 10) / 10, stale: ageDays > STALE_RECEIPT_DAYS }
    }
  } catch { /* covered by models.receipt */ }

  // 3. SAGE pre-screen reachability + last successful fire.
  const sage: Record<string, unknown> = { configured: !!process.env.SAGE_URL }
  if (process.env.SAGE_URL) {
    const t0 = Date.now()
    try {
      const res = await fetch(`${process.env.SAGE_URL}/api/health`, { signal: AbortSignal.timeout(3000) })
      sage.reachable = res.ok
      sage.latencyMs = Date.now() - t0
    } catch (err) {
      sage.reachable = false
      sage.error = err instanceof Error ? err.message : String(err)
    }
    try {
      const t = await prisma.sageTrace.findFirst({ where: { fired: true }, orderBy: { createdAt: "desc" }, select: { createdAt: true } })
      sage.lastFiredAt = t?.createdAt.toISOString() ?? null
    } catch { /* covered by models.sageTrace */ }
  }

  // 4. Required env presence — names only, never values.
  const env: Record<string, boolean> = {}
  for (const k of REQUIRED_ENV) env[k] = !!process.env[k]

  const modelsOk = Object.values(models).every((m) => m.ok)
  const envOk = Object.values(env).every(Boolean)
  const status = !dbOk || !modelsOk ? "down" : (lastReceipt.stale || sage.reachable === false || !envOk) ? "degraded" : "ok"

  return NextResponse.json(
    { status, ts: new Date().toISOString(), db: dbOk, models, lastReceipt, sage, env },
    { status: status === "down" ? 503 : 200 },
  )
}
