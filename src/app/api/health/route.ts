import { NextRequest, NextResponse } from "next/server"
import { Prisma } from "@prisma/client"
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
  const delegates = prisma as unknown as Record<string, { findFirst: (args: unknown) => Promise<unknown> }>
  for (const m of CORE_MODELS) {
    try {
      await delegates[m].findFirst({ take: 1 })
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

  // 4. Outcome-capture funnel — the P1 keel gap (induced-backlog: outcome-capture-rate-keel-gap).
  //    Read-only aggregate over the full drop-off chain so the number is VISIBLE on the
  //    always-run path (Frustration Gate, AGENTS.md #15), not rediscovered via ad-hoc SQL.
  //    Anonymous receipts can't be closed (§5.1, human-supplied only), so the denominator
  //    is signed-in receipts, not total. Two mechanical leaks are surfaced explicitly:
  //    eligible-never-sent, and reminders scheduled beyond Resend's 30-day cap (silently dropped).
  //    CRITICAL: the operator (ADMIN_EMAILS) is ~95% of eligible receipts — QA traffic, not
  //    organic. A blended capture rate is a measurement artifact. So we report an `external`
  //    segment (non-admin) as the honest funnel, and `operator` separately. Optimizing the
  //    blended number would tune against the founder's own test behavior (counterfeit signal).
  let outcomeCapture: Record<string, unknown> = { ok: false }
  try {
    const admins = (process.env.ADMIN_EMAILS ?? "")
      .split(",").map((e) => e.trim().toLowerCase()).filter(Boolean)
    // <> ALL($1) is true when the list is empty too, so no admins configured ⇒ everyone external.
    const seg = async (isExternal: boolean) => {
      const today = new Date().toISOString().slice(0, 10)
      const rows = await prisma.$queryRaw<Array<Record<string, bigint>>>`
        SELECT
          count(*)                                                                AS eligible,
          count(*) FILTER (WHERE r."debriefSentAt" IS NOT NULL)                   AS sent,
          -- past-due, never sent, no outcome: the real leak (should have gone out, didn't).
          count(*) FILTER (WHERE r."debriefSentAt" IS NULL AND o.id IS NULL
                           AND r."reminderDate" <= ${today})                      AS past_due_never_sent,
          -- future reminderDate, not yet sent: the long-horizon cron will sweep these. Not a bug.
          count(*) FILTER (WHERE r."debriefSentAt" IS NULL AND r."reminderDate" > ${today}) AS waiting_for_cron,
          count(o.id)                                                             AS closed,
          count(o.id) FILTER (WHERE o.matched IS TRUE)                            AS closed_matched,
          count(o.id) FILTER (WHERE o.matched IS FALSE)                           AS closed_drifted,
          count(DISTINCT r."userId")                                              AS users
        FROM "Receipt" r
        JOIN "User" u ON u.id = r."userId"
        LEFT JOIN "Outcome" o ON o."receiptId" = r.id
        WHERE ${isExternal
          ? Prisma.sql`lower(u.email) <> ALL(${admins})`
          : Prisma.sql`lower(u.email) = ANY(${admins})`}`
      const r = rows[0]
      const n = (v: bigint | undefined) => Number(v ?? 0)
      const eligible = n(r.eligible), closed = n(r.closed)
      const matched = n(r.closed_matched), drifted = n(r.closed_drifted)
      return {
        users: n(r.users),
        eligible,
        sent: n(r.sent),
        closed,
        captureRate: eligible > 0 ? Math.round((closed / eligible) * 1000) / 1000 : 0,
        pastDueNeverSent: n(r.past_due_never_sent),   // the real leak — debrief owed but never sent
        waitingForCron: n(r.waiting_for_cron),        // future reminderDate; long-horizon cron will sweep. not a bug
        distribution: { matched, drifted },
      }
    }
    const total = await prisma.receipt.count()
    const anonymous = await prisma.receipt.count({ where: { userId: null } })
    const external = await seg(true)
    const operator = await seg(false)
    outcomeCapture = {
      ok: true,
      total,
      anonymous,                                     // can't be closed by design (§5.1)
      external,                                      // the honest funnel — optimize THIS, not blended
      operator,                                      // ADMIN_EMAILS = QA traffic, reported for transparency
      // Calibration needs paired nci-vs-outcome rows across Y-states; a handful of all-matched
      // operator closures validates nothing (ticket meta-question). External is where organic
      // signal must come from — and today it is starved (distribution gap, not a closure-UX gap).
      calibrationUsable: external.closed >= 5 && external.distribution.matched > 0 && external.distribution.drifted > 0,
      note: external.eligible < 20
        ? "external n too small to infer a conversion lever — this is a distribution problem, not a nudge problem"
        : undefined,
    }
  } catch (err) {
    outcomeCapture = { ok: false, error: err instanceof Error ? err.message.slice(0, 300) : String(err) }
  }

  // 5. Required env presence — names only, never values.
  const env: Record<string, boolean> = {}
  for (const k of REQUIRED_ENV) env[k] = !!process.env[k]

  const modelsOk = Object.values(models).every((m) => m.ok)
  const envOk = Object.values(env).every(Boolean)
  const status = !dbOk || !modelsOk ? "down" : (lastReceipt.stale || sage.reachable === false || !envOk) ? "degraded" : "ok"

  return NextResponse.json(
    { status, ts: new Date().toISOString(), db: dbOk, models, lastReceipt, sage, outcomeCapture, env },
    { status: status === "down" ? 503 : 200 },
  )
}
