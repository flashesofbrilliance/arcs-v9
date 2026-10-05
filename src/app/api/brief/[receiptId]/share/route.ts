import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { rateLimit } from "@/lib/ratelimit"
import { MAX_ACTIVE_SHARES, hashToken, mintToken, sharePath } from "@/lib/briefShare"

export const dynamic = "force-dynamic"

// Mint (POST) and revoke (DELETE) share links for a brief the caller owns.
// The raw token is returned once, in the POST response, and never stored.

async function ownedBrief(receiptId: string): Promise<{ userId: string; briefId: string | null } | null> {
  const session = await auth()
  const userId = session?.user?.id ?? null
  if (!userId) return null
  const r = await prisma.receipt.findUnique({
    where: { id: receiptId },
    select: { userId: true, brief: { select: { id: true } } },
  })
  if (!r || r.userId !== userId) return null
  return { userId, briefId: r.brief?.id ?? null }
}

const notFound = () => NextResponse.json({ error: "Receipt not found" }, { status: 404 })

export async function POST(_req: NextRequest, { params }: { params: Promise<{ receiptId: string }> }) {
  const { receiptId } = await params
  const owned = await ownedBrief(receiptId)
  if (!owned) return notFound()
  // Only a stored brief can be shared, so the shared route never spends tokens.
  if (!owned.briefId) return NextResponse.json({ error: "Open the brief once before sharing it" }, { status: 409 })

  const rl = rateLimit(`brief-share:${owned.userId}`, { limit: 20, windowMs: 10 * 60_000 })
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })
  }

  const active = await prisma.briefShare.count({ where: { briefId: owned.briefId, revokedAt: null } })
  if (active >= MAX_ACTIVE_SHARES) {
    return NextResponse.json({ error: "Too many active share links. Revoke them and mint a new one." }, { status: 409 })
  }

  const token = mintToken()
  await prisma.briefShare.create({ data: { briefId: owned.briefId, tokenHash: hashToken(token), createdBy: owned.userId } })
  return NextResponse.json({ ok: true, path: sharePath(token) }, { headers: { "Cache-Control": "no-store" } })
}

export async function DELETE(_req: NextRequest, { params }: { params: Promise<{ receiptId: string }> }) {
  const { receiptId } = await params
  const owned = await ownedBrief(receiptId)
  if (!owned) return notFound()
  if (!owned.briefId) return NextResponse.json({ ok: true, revoked: 0 })
  // Shares the mint bucket, so a revoke-then-mint loop cannot grow the table fast.
  const rl = rateLimit(`brief-share:${owned.userId}`, { limit: 20, windowMs: 10 * 60_000 })
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })
  }
  const { count } = await prisma.briefShare.updateMany({
    where: { briefId: owned.briefId, revokedAt: null },
    data: { revokedAt: new Date() },
  })
  return NextResponse.json({ ok: true, revoked: count })
}
