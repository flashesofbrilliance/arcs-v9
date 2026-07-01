import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { flags } from "@/lib/flags"

export const dynamic = "force-dynamic"

// History GET is gated by the `publicHistory` feature flag (src/lib/flags.ts):
//   ON  (PLG/demo, default) → ungated: recent receipts returned globally.
//   OFF (PUBLIC_HISTORY=false, post-RBAC) → per-user isolation (ADR-001).
export async function GET() {
  let userId: string | null = null
  if (!flags.publicHistory) {
    const session = await auth()
    userId = session?.user?.id ?? null
    if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const receipts = await prisma.receipt.findMany({
    where: {
      status: { not: "EXPIRED" },
      parentId: null, // seed receipts only (alpha questions)
      ...(userId ? { userId } : {}), // gated mode: caller's own receipts only
    },
    orderBy: { createdAt: "desc" },
    take: 50,
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
      sessionId: true,
      brief: { select: { id: true } },
      children: {
        select: {
          id: true,
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
