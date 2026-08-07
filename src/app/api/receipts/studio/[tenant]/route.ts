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
//   PATCH close/score a receipt: OPEN -> SCORED|KILLED|SCALED (robin_app has UPDATE)
//
// A receipt should be scored by external signal that arrives after T0 (§5.1);
// like the debrief outcome route, v1 does not hard-enforce a different-session
// check — the session's random id is the ownership gate.

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

// Best-effort per-instance throttle (serverless-local; row caps are the real bound).
const hits = new Map<string, { n: number; t: number }>()
function throttled(ip: string): boolean {
  const now = Date.now()
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

async function resolveTenant(params: Promise<{ tenant: string }>) {
  const { tenant } = await params
  if (!isStudioTenant(tenant)) return null
  return { tenant, brand: STUDIO_TENANTS[tenant].brand, prisma: studioPrisma(tenant) }
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await resolveTenant(ctx.params)
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

  const rowCount = await t.prisma.sessionReceipt.count({
    where: { tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
  })
  if (rowCount >= STUDIO_LIMITS.MAX_ROWS_PER_SESSION) {
    return NextResponse.json({ error: "Session receipt limit reached" }, { status: 429 })
  }

  // Lineage: parent must exist in the same tenant/brand/session — no cross-session grafts.
  let parentId: string | null = null
  if (parsed.parentId) {
    const parent = await t.prisma.sessionReceipt.findFirst({
      where: { id: parsed.parentId, tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
      select: { id: true },
    })
    if (!parent) return NextResponse.json({ error: "parentId not found in this session" }, { status: 400 })
    parentId = parent.id
  }

  const session = await auth()
  const userId = session?.user?.id ?? null

  const receipt = await t.prisma.sessionReceipt.create({
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
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await resolveTenant(ctx.params)
  if (!t) return NextResponse.json({ error: "Unknown tenant" }, { status: 404 })
  const sessionId = req.nextUrl.searchParams.get("sessionId")
  if (!sessionId) return NextResponse.json({ error: "sessionId is required" }, { status: 400 })

  const receipts = await t.prisma.sessionReceipt.findMany({
    where: { tenant: t.tenant, brand: t.brand, sessionId },
    select: PUBLIC_SELECT,
    orderBy: { createdAt: "desc" },
    take: 200,
  })

  return NextResponse.json({ receipts })
}

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ tenant: string }> }) {
  const t = await resolveTenant(ctx.params)
  if (!t) return NextResponse.json({ error: "Unknown tenant" }, { status: 404 })
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

  // Ownership gate: the receipt must exist in this tenant/brand AND this session.
  const existing = await t.prisma.sessionReceipt.findFirst({
    where: { id: parsed.id, tenant: t.tenant, brand: t.brand, sessionId: parsed.sessionId },
    select: { id: true, status: true },
  })
  if (!existing) return NextResponse.json({ error: "receipt not found in this session" }, { status: 404 })

  const updated = await t.prisma.sessionReceipt.update({
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
}
