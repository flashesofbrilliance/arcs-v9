import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { scrubProse, scrubDeep, scrubReceiptProse } from "@/lib/prose"
import { hashToken, isTokenShaped } from "@/lib/briefShare"
import { rateLimit, clientIp } from "@/lib/ratelimit"

export const dynamic = "force-dynamic"

// The shared view of a brief, reached only by an owner-minted token. The token
// travels in the page URL's fragment (/shared/brief#<token>) and arrives here in
// a POST body, so it never lands in a request path, server log, analytics
// pathname, or Referer header. It reads a
// stored brief (never generates), and the receipt comes back through a select
// ALLOWLIST: never userId, sessionId, prep, rawResponse, parentId or children.
// Tributaries and advisors are lifted out of rawResponse server-side.

const SHARED_RECEIPT_SELECT = {
  id: true,
  decision: true,
  trueNorth: true,
  whyBullets: true,
  nciScore: true,
  nciGrade: true,
  coherencePct: true,
  isSatoshi: true,
  mode: true,
  doorClass: true,
  yState: true,
  renderResolution: true,
  macroTags: true,
  fated: true,
  paths: true,
  court: true,
  courtVerdict: true,
  createdAt: true,
  rawResponse: true, // read here only to lift tributaries/advisors; never returned
} as const

async function resolveShare(token: string): Promise<string | null> {
  if (!isTokenShaped(token)) return null
  const row = await prisma.briefShare.findUnique({
    where: { tokenHash: hashToken(token) },
    select: { briefId: true, revokedAt: true },
  })
  return row && !row.revokedAt ? row.briefId : null
}

export async function POST(req: NextRequest) {
  // 256-bit tokens make guessing moot; this only caps junk traffic on the DB.
  const rl = rateLimit(`shared-brief:${clientIp(req)}`, { limit: 60, windowMs: 60_000 })
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })
  }
  const body = (await req.json().catch(() => null)) as { token?: unknown } | null
  const token = typeof body?.token === "string" ? body.token : ""
  const notFound = () => NextResponse.json({ error: "Brief not found" }, { status: 404, headers: { "Cache-Control": "no-store" } })
  const briefId = await resolveShare(token)
  if (!briefId) return notFound()

  const brief = await prisma.brief.findUnique({
    where: { id: briefId },
    select: { situationFraming: true, generatedAt: true, receipt: { select: SHARED_RECEIPT_SELECT } },
  })
  if (!brief?.receipt) return notFound()

  const { rawResponse, ...receipt } = brief.receipt
  let tributaries: unknown[] = []
  let advisors: unknown = undefined
  try {
    const raw = rawResponse ? (JSON.parse(rawResponse) as { tributaries?: unknown; reasoning?: { advisors?: unknown } }) : null
    if (Array.isArray(raw?.tributaries)) tributaries = raw.tributaries
    advisors = raw?.reasoning?.advisors
  } catch { /* malformed: omit */ }

  return NextResponse.json(
    {
      ok: true,
      brief: { situationFraming: scrubProse(brief.situationFraming), generatedAt: brief.generatedAt },
      receipt: scrubReceiptProse(receipt),
      tributaries: scrubDeep(tributaries),
      advisors: advisors === undefined ? null : scrubDeep(advisors),
    },
    { headers: { "Cache-Control": "no-store" } },
  )
}
