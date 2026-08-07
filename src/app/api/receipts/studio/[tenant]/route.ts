import { NextRequest, NextResponse } from "next/server"
import { z } from "zod"
import { auth } from "@/lib/auth"
import { STUDIO_TENANTS, isStudioTenant, studioPrisma, PUBLIC_SELECT, STUDIO_LIMITS } from "@/lib/receipt-studio"

export const dynamic = "force-dynamic"

// Registry-driven Receipt Studio (generalizes /api/louisville/receipts).
// tenant comes from the [tenant] PATH segment and is validated against the
// server-side registry; tenant + brand are set from the registry, NEVER the
// body. Anonymous surface, so the same bounds as the louisville route apply
// (body size, field lengths, rows per session, best-effort IP throttle) and
// reads/writes are session-scoped with an explicit field allowlist.
//
//   POST  file a bet (seal)
//   GET   ?sessionId=  read this session's receipts (bearer-token model)
//   PATCH close/score a receipt: OPEN -> SCORED|KILLED|SCALED (needs UPDATE grant)
//
// A receipt should be scored by external signal that arrives after T0 (§5.1);
// like the debrief outcome route, v1 does not hard-enforce a different-session
// check — the session's random id is the ownership gate.
//
// CISO/SRE review (2026-08-07): the sessionId bearer now grants WRITE (PATCH) and
// travels in the GET query string — acceptable for this tenant (Zach's own demo
// receipts) but must NOT generalize to a sensitive/user-attributable tenant
// without moving the token to a header/cookie (logged to the ADR-034 ledger).

const FIELD = z.string().max(4096)

const CreateSchema = z.object({
  sessionId: FIELD.min(1),
  author: FIELD.max(40).default("ZACH"),
  bet: FIELD.min(1),
  assumptions: FIELD.optional().nullable(),
  falsifier: FIELD.min(1),
  killScale: FIELD.optional().nullable(),
  atRisk: FIELD.optional().nullable(),
  scoreBackDate: z.coerce
    .date()
    .refine((d) => d.getFullYear() >= 2020 && d.getFullYear() <= 2100, "scoreBackDate out of range")
    .refine((d) => d.getTime() > Date.now() - 86_400_000, "scoreBackDate must be in the future"),
  parentId: FIELD.optional().nullable(),
  payload: z.unknown().optional(),
})

const UpdateSchema = z.object({
  sessionId: FIELD.min(1),
  id: FIELD.min(1),
  status: z.enum(["SCORED", "KILLED", "SCALED"]),
  outcome: FIELD.optional().nullable(),
  variance: FIELD.optional().nullable(),
  lesson: FIELD.optional().nullable(),
  payload: z.unknown().optional(),
})

// Best-effort per-instance throttle (serverless-local; row caps are the real
// bound). Opportunistically swept so a rotating-IP scraper cannot grow the Map
// for the instance lifetime (SRE finding F3).
const hits = new Map<string, { n: number; t: number }>()
function throttled(ip: string): boolean {
  const now = Date.now()
  if (hits.size > 5000) {
    for (const [k, v] of hits) if (now - v.t > STUDIO_LIMITS.THROTTLE_WINDOW_MS) hits.delete(k)
  }
  const h = hits.get(ip)
  if (!h || now - h.t > STUDIO_LIMITS.THROTTLE_WINDOW_MS) {
    hits.set(ip, { n: 1, t: now })
    return false
  }
  h.n++
  return h.n > STUDIO_LIMITS.THROTTLE_MAX
}

function clientIp(req: NextRequest): string {
  // x-real-ip is set by the Vercel proxy and cannot be spoofed by the client;
  // x-forwarded-for's first hop is attacker-controllable, so it is only a fallback.
  return (
    req.headers.get("x-real-ip")?.trim() ||
    req.headers.get("x-forwarded-for")?.split(",").pop()?.trim() ||
    "unknown"
  )
}

// Cheap tenant validation (no DB client build, so it cannot throw). The client
// is built inside each handler's try/catch, so an unset secret surfaces as a
// logged 503 rather than an opaque, un-instrumented 500 (SRE finding F2).
async function tenantConfig(params: Promise<{ tenant: string }>) {
  const { tenant } = await params
  if (!isStudioTenant(tenant)) return null
  const cfg = STUDIO_TENANTS[tenant]
  return { tenant, brand: cfg.brand, close: cfg.close }
}

function unavailable(tenant: string, op: string, err: unknown) {
  console.error(`[studio ${op} ${tenant}]`, err instanceof Error ? err.message : String(err))
  return NextResponse.json({ error: "Studio temporarily unavailable" }, { status: 503 })
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await tenantConfig(ctx.params)
  if (!t) return NextResponse.json({ error: "Unknown tenant" }, { status: 404 })
  if (throttled(clientIp(req))) return NextResponse.json({ error: "Too many requests" }, { status: 429 })

  const raw = await req.text()
  if (raw.length > STUDIO_LIMITS.MAX_BODY_BYTES) {
    return NextResponse.json({ error: "Body too large" }, { status: 413 })
  }
  let parsed: z.infer<typeof CreateSchema>
  try {
    parsed = CreateSchema.parse(JSON.parse(raw))
  } catch (e) {
    const msg = e instanceof z.ZodError ? e.issues[0]?.message ?? "Invalid body" : "Invalid JSON"
    return NextResponse.json({ error: msg }, { status: 400 })
  }

  try {
    const prisma = studioPrisma(t.tenant)

    const rowCount = await prisma.sessionReceipt.count({
      where: { tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
    })
    if (rowCount >= STUDIO_LIMITS.MAX_ROWS_PER_SESSION) {
      return NextResponse.json({ error: "Session receipt limit reached" }, { status: 429 })
    }

    // Lineage: parent must exist in the same tenant/brand/session — no cross-session grafts.
    let parentId: string | null = null
    if (parsed.parentId) {
      const parent = await prisma.sessionReceipt.findFirst({
        where: { id: parsed.parentId, tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
        select: { id: true },
      })
      if (!parent) return NextResponse.json({ error: "parentId not found in this session" }, { status: 400 })
      parentId = parent.id
    }

    const session = await auth()
    const userId = session?.user?.id ?? null

    const receipt = await prisma.sessionReceipt.create({
      data: {
        tenant: t.tenant,
        brand: t.brand,
        sessionId: parsed.sessionId,
        author: parsed.author,
        bet: parsed.bet,
        assumptions: parsed.assumptions ?? null,
        falsifier: parsed.falsifier,
        killScale: parsed.killScale ?? null,
        atRisk: parsed.atRisk ?? null,
        scoreBackDate: parsed.scoreBackDate,
        parentId,
        payload: parsed.payload === undefined ? undefined : (parsed.payload as object),
        userId,
        sealedAt: new Date(),
      },
      select: { id: true, status: true, sealedAt: true },
    })
    return NextResponse.json(receipt)
  } catch (e) {
    return unavailable(t.tenant, "POST", e)
  }
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await tenantConfig(ctx.params)
  if (!t) return NextResponse.json({ error: "Unknown tenant" }, { status: 404 })
  const sessionId = req.nextUrl.searchParams.get("sessionId")
  if (!sessionId) return NextResponse.json({ error: "sessionId is required" }, { status: 400 })

  try {
    const prisma = studioPrisma(t.tenant)
    const receipts = await prisma.sessionReceipt.findMany({
      where: { tenant: t.tenant, brand: t.brand, sessionId },
      select: PUBLIC_SELECT,
      orderBy: { createdAt: "desc" },
      take: 200,
    })
    return NextResponse.json({ receipts })
  } catch (e) {
    return unavailable(t.tenant, "GET", e)
  }
}

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await tenantConfig(ctx.params)
  if (!t) return NextResponse.json({ error: "Unknown tenant" }, { status: 404 })
  // Reject close/score for tenants whose DB role has no UPDATE grant, up front
  // with a 405, instead of failing deep at the grant layer as a 500 (CISO D).
  if (!t.close) return NextResponse.json({ error: "This tenant is file-only" }, { status: 405 })
  if (throttled(clientIp(req))) return NextResponse.json({ error: "Too many requests" }, { status: 429 })

  const raw = await req.text()
  if (raw.length > STUDIO_LIMITS.MAX_BODY_BYTES) {
    return NextResponse.json({ error: "Body too large" }, { status: 413 })
  }
  let parsed: z.infer<typeof UpdateSchema>
  try {
    parsed = UpdateSchema.parse(JSON.parse(raw))
  } catch (e) {
    const msg = e instanceof z.ZodError ? e.issues[0]?.message ?? "Invalid body" : "Invalid JSON"
    return NextResponse.json({ error: msg }, { status: 400 })
  }

  try {
    const prisma = studioPrisma(t.tenant)

    // Ownership gate: the receipt must exist in this tenant/brand AND this session.
    const existing = await prisma.sessionReceipt.findFirst({
      where: { id: parsed.id, tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
      select: { id: true, status: true },
    })
    if (!existing) return NextResponse.json({ error: "receipt not found in this session" }, { status: 404 })
    // Append-only: a receipt is scored ONCE. Re-scoring would let a filed bet be
    // rewritten into a flattering outcome, defeating the whole contract (CISO A).
    if (existing.status !== "OPEN") {
      return NextResponse.json({ error: "receipt already scored" }, { status: 409 })
    }

    const updated = await prisma.sessionReceipt.update({
      where: { id: existing.id },
      data: {
        status: parsed.status,
        outcome: parsed.outcome ?? null,
        variance: parsed.variance ?? null,
        lesson: parsed.lesson ?? null,
        payload: parsed.payload === undefined ? undefined : (parsed.payload as object),
      },
      select: PUBLIC_SELECT,
    })
    return NextResponse.json({ receipt: updated })
  } catch (e) {
    return unavailable(t.tenant, "PATCH", e)
  }
}
