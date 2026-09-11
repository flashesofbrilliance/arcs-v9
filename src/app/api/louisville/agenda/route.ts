import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { adminEmails } from "@/lib/admin"
import { louisvillePrisma as prisma } from "@/lib/db-louisville"

export const dynamic = "force-dynamic"

// Tenant-wide read = the sensitive surface (every session's bets in one call),
// so it is auth-gated: signed-in email must be on LOUISVILLE_VIEWER_EMAILS or
// ADMIN_EMAILS. Same doctrine as src/lib/admin.ts: prod fail-closed, dev
// pass-through. The per-session GET on /receipts stays anonymous — its random
// sessionId is effectively a bearer token and powers the Studio restore.
function viewerEmails(): string[] {
  const extra = (process.env.LOUISVILLE_VIEWER_EMAILS ?? "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean)
  return [...new Set([...adminEmails(), ...extra])]
}

async function authorized(): Promise<boolean> {
  if (process.env.NODE_ENV !== "production") return true
  const session = await auth()
  const email = session?.user?.email?.toLowerCase()
  return !!email && viewerEmails().includes(email)
}

// Louisville Phase 2: compose the next session's agenda from this tenant's
// open receipts + anything whose score-back lands inside the horizon.
// This is the receipt → agenda → session → receipt loop.

const TENANT = "jeben"
const BRAND = "louisvillebrands"
const DEFAULT_HORIZON_DAYS = 14

export async function GET(req: NextRequest) {
  if (!(await authorized())) {
    return NextResponse.json({ error: "Not found" }, { status: 404 })
  }
  const horizonParam = Number(req.nextUrl.searchParams.get("horizonDays"))
  const horizonDays = Number.isFinite(horizonParam) && horizonParam > 0 ? Math.min(horizonParam, 365) : DEFAULT_HORIZON_DAYS
  const horizon = new Date(Date.now() + horizonDays * 24 * 60 * 60 * 1000)

  const open = await prisma.sessionReceipt.findMany({
    where: {
      tenant: TENANT,
      brand: BRAND,
      OR: [{ status: "OPEN" }, { scoreBackDate: { lte: horizon } }],
    },
    orderBy: { scoreBackDate: "asc" },
    take: 100,
  })

  // Cross-session by design (the agenda composes the whole tenant's open loop),
  // but field-allowlisted: no payload, no userId.
  const now = new Date()
  const items = open.map((r) => ({
    id: r.id,
    author: r.author,
    bet: r.bet,
    falsifier: r.falsifier,
    killScale: r.killScale,
    scoreBackDate: r.scoreBackDate,
    status: r.status,
    sessionId: r.sessionId,
    due: r.scoreBackDate <= now ? "OVERDUE" : r.scoreBackDate <= horizon ? "DUE_SOON" : "OPEN",
  }))

  return NextResponse.json({
    tenant: TENANT,
    brand: BRAND,
    horizonDays,
    generatedAt: now.toISOString(),
    agenda: items,
  })
}
