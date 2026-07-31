import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

export const dynamic = "force-dynamic"

// Louisville Phase 2: persist Receipt Studio seals, tenant-scoped
// jeben → louisvillebrands. tenant/brand/userId are set server-side ONLY;
// sessionId comes from the request body (client localStorage, anon flow —
// same shape as the ADR-016 claim pattern).

const TENANT = "jeben"
const BRAND = "louisvillebrands"

export async function POST(req: NextRequest) {
  let body: Record<string, unknown>
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 })
  }

  const { sessionId, author, bet, assumptions, falsifier, killScale, atRisk, scoreBackDate, payload, parentId } = body

  if (!bet || typeof bet !== "string") {
    return NextResponse.json({ error: "bet is required" }, { status: 400 })
  }
  if (!falsifier || typeof falsifier !== "string") {
    return NextResponse.json({ error: "falsifier is required" }, { status: 400 })
  }
  const scoreBack = typeof scoreBackDate === "string" ? new Date(scoreBackDate) : null
  if (!scoreBack || isNaN(scoreBack.getTime())) {
    return NextResponse.json({ error: "scoreBackDate is required (ISO date)" }, { status: 400 })
  }
  if (!sessionId || typeof sessionId !== "string") {
    return NextResponse.json({ error: "sessionId is required" }, { status: 400 })
  }

  const session = await auth()
  const userId = session?.user?.id ?? null

  const receipt = await prisma.sessionReceipt.create({
    data: {
      tenant: TENANT,
      brand: BRAND,
      sessionId,
      author: typeof author === "string" && author ? author : "JUSTIN",
      bet,
      assumptions: typeof assumptions === "string" ? assumptions : null,
      falsifier,
      killScale: typeof killScale === "string" ? killScale : null,
      atRisk: typeof atRisk === "string" ? atRisk : null,
      scoreBackDate: scoreBack,
      parentId: typeof parentId === "string" ? parentId : null,
      payload: payload ?? undefined,
      userId,
      sealedAt: new Date(),
    },
  })

  return NextResponse.json({ id: receipt.id, status: receipt.status, sealedAt: receipt.sealedAt })
}

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("sessionId")

  const receipts = await prisma.sessionReceipt.findMany({
    where: {
      tenant: TENANT,
      brand: BRAND,
      ...(sessionId ? { sessionId } : {}),
    },
    orderBy: { createdAt: "desc" },
    take: 200,
  })

  return NextResponse.json({ receipts })
}
