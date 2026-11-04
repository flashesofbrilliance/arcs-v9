import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { flags } from "@/lib/flags"

export const dynamic = "force-dynamic"

// History GET is gated by the `publicHistory` feature flag (src/lib/flags.ts):
//   OFF (default; PUBLIC_HISTORY unset) → per-user isolation (ADR-001).
//   ON  (PUBLIC_HISTORY=true, demo only) → ungated: recent receipts returned globally.
export async function GET() {
  let userId: string | null = null
  if (!flags.publicHistory) {
    const session = await auth()
    userId = session?.user?.id ?? null
    if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  // ARCS Pro keeps the full history (cap 500 so one account cannot stall the page).
  const tier = userId ? (await prisma.user.findUnique({ where: { id: userId }, select: { tier: true } }))?.tier : null
  const receipts = await prisma.receipt.findMany({
    where: {
      status: { not: "EXPIRED" },
      parentId: null, // seed receipts only (alpha questions)
      ...(userId ? { userId } : {}), // gated mode: caller's own receipts only
    },
    orderBy: { createdAt: "desc" },
    take: tier === "PRO" ? 500 : 50,
    select: {
      id: true,
      decision: true,
      trueNorth: true,
      nciScore: true,
      yState: true,
      yConviction: true,
      mode: true,
      doorClass: true,
      window: true,
      stakes: true,
      entity: true,
      createdAt: true,
      // Thread id: only on the caller's own rows.
      sessionId: userId !== null,
      brief: { select: { id: true } },
      children: {
        select: {
          id: true,
          // Which of the parent's three tributaries spawned this round (0 meta,
          // 1 challenge, 2 adjacent); null on rows written before it was recorded.
          parentTributaryIndex: true,
          decision: true,
          trueNorth: true,
          nciScore: true,
          yState: true,
          mode: true,
          doorClass: true,
          createdAt: true,
          brief: { select: { id: true } },
        },
        orderBy: { createdAt: 'asc' },
      },
    },
  })

  return NextResponse.json({ receipts })
}
