import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

export async function GET(_req: NextRequest, { params }: { params: Promise<{ receiptId: string }> }) {
  const session = await auth()
  // Signed-in only: a null userId would match every anonymous row.
  const userId = session?.user?.id
  if (!userId) return NextResponse.json({ error: "Sign in required" }, { status: 401 })

  const { receiptId } = await params
  const annotations = await prisma.annotation.findMany({
    where: { receiptId, userId },
    orderBy: { createdAt: "asc" },
  })
  return NextResponse.json({ ok: true, annotations })
}
