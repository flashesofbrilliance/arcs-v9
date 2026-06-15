import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

export async function GET(_req: NextRequest, { params }: { params: Promise<{ receiptId: string }> }) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const { receiptId } = await params
  const annotations = await prisma.annotation.findMany({
    where: { receiptId, userId },
    orderBy: { createdAt: "asc" },
  })
  return NextResponse.json({ ok: true, annotations })
}
