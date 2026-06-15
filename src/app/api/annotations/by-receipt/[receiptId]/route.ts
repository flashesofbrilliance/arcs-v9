import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"

export const dynamic = "force-dynamic"

export async function GET(_req: NextRequest, { params }: { params: Promise<{ receiptId: string }> }) {
  const { receiptId } = await params
  const annotations = await prisma.annotation.findMany({
    where: { receiptId },
    orderBy: { createdAt: "asc" },
  })
  return NextResponse.json({ ok: true, annotations })
}
