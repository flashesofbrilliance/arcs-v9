import { NextRequest, NextResponse } from "next/server"
import { z } from "zod"
import { auth } from "@/lib/auth"
import { louisvillePrisma as prisma } from "@/lib/db-louisville"

export const dynamic = "force-dynamic"

// Louisville Phase 2: persist Receipt Studio seals, tenant-scoped
// jeben → louisvillebrands. tenant/brand/userId are set server-side ONLY;
// sessionId comes from the request body (client localStorage, anon flow —
// same shape as the ADR-016 claim pattern). Anonymous surface, so writes are
// capped (body size, field lengths, rows per session, best-effort IP throttle)
// and reads are session-scoped with an explicit field allowlist.

const TENANT = "jeben"
const BRAND = "louisvillebrands"
const MAX_BODY_BYTES = 32_768
const MAX_ROWS_PER_SESSION = 100

const FIELD = z.string().max(4096)
const CreateSchema = z.object({
  sessionId: FIELD.min(1),
  author: z.enum(["JUSTIN", "JEBEN", "ZACH"]).catch("JUSTIN"),
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

// Best-effort per-instance throttle (serverless-local; row caps are the real
// bound). Opportunistically swept so a rotating-IP scraper cannot grow the Map
// for the instance lifetime (ledger STU-016; mirrors the studio route).
const hits = new Map<string, { n: number; t: number }>()
function throttled(ip: string): boolean {
  const now = Date.now()
  if (hits.size > 5000) {
    for (const [k, v] of hits) if (now - v.t > 60_000) hits.delete(k)
  }
  const h = hits.get(ip)
  if (!h || now - h.t > 60_000) {
    hits.set(ip, { n: 1, t: now })
    return false
  }
  h.n++
  return h.n > 30
}

// Fields the Studio actually consumes — never the raw row (strips userId).
const PUBLIC_SELECT = {
  id: true,
  sessionId: true,
  author: true,
  bet: true,
  assumptions: true,
  falsifier: true,
  killScale: true,
  atRisk: true,
  scoreBackDate: true,
  status: true,
  parentId: true,
  payload: true,
  createdAt: true,
  sealedAt: true,
} as const

export async function POST(req: NextRequest) {
  // x-real-ip is set by the Vercel proxy and cannot be spoofed by the client;
  // x-forwarded-for's first hop is attacker-controllable, so it is only a fallback.
  const ip =
    req.headers.get("x-real-ip")?.trim() ||
    req.headers.get("x-forwarded-for")?.split(",").pop()?.trim() ||
    "unknown"
  if (throttled(ip)) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429 })
  }

  const raw = await req.text()
  if (raw.length > MAX_BODY_BYTES) {
    return NextResponse.json({ error: "Body too large" }, { status: 413 })
  }
  let parsed: z.infer<typeof CreateSchema>
  try {
    parsed = CreateSchema.parse(JSON.parse(raw))
  } catch (e) {
    const msg = e instanceof z.ZodError ? e.issues[0]?.message ?? "Invalid body" : "Invalid JSON"
    return NextResponse.json({ error: msg }, { status: 400 })
  }

  const rowCount = await prisma.sessionReceipt.count({
    where: { tenant: TENANT, brand: BRAND, sessionId: parsed.sessionId },
  })
  if (rowCount >= MAX_ROWS_PER_SESSION) {
    return NextResponse.json({ error: "Session receipt limit reached" }, { status: 429 })
  }

  // Lineage: parent must exist in the same tenant/brand/session — no cross-session grafts.
  let parentId: string | null = null
  if (parsed.parentId) {
    const parent = await prisma.sessionReceipt.findFirst({
      where: { id: parsed.parentId, tenant: TENANT, brand: BRAND, sessionId: parsed.sessionId },
      select: { id: true },
    })
    if (!parent) {
      return NextResponse.json({ error: "parentId not found in this session" }, { status: 400 })
    }
    parentId = parent.id
  }

  const session = await auth()
  const userId = session?.user?.id ?? null

  const receipt = await prisma.sessionReceipt.create({
    data: {
      tenant: TENANT,
      brand: BRAND,
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

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("sessionId")
  if (!sessionId) {
    return NextResponse.json({ error: "sessionId is required" }, { status: 400 })
  }

  const receipts = await prisma.sessionReceipt.findMany({
    where: { tenant: TENANT, brand: BRAND, sessionId },
    select: PUBLIC_SELECT,
    orderBy: { createdAt: "desc" },
    take: 200,
  })

  return NextResponse.json({ receipts })
}
