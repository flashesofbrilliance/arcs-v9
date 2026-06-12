import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"

export const dynamic = "force-dynamic"

// Ungated demo mode: returns recent seed receipts globally (no auth, no userId
// filter) so the history ledger is populated for the end-to-end walkthrough.
// To restore per-user isolation (ADR-001), re-add the auth() gate + userId where.
export async function GET() {
  const receipts = await prisma.receipt.findMany({
    where: {
      status: { not: "EXPIRED" },
      parentId: null, // seed receipts only (alpha questions)
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
      children: { select: { id: true } }, // follow-up count
    },
  })

  return NextResponse.json({ receipts })
}
