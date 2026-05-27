import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export async function GET() {
  const session = await auth()
  const userId = session?.user?.id ?? null
  if (!userId && process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const receipts = await prisma.receipt.findMany({
    where: {
      status: { not: "EXPIRED" },
      parentId: null, // seed receipts only (alpha questions)
      ...(userId ? { userId } : {}), // prod: filter to user's own receipts
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
