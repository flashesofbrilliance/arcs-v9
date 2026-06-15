import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

export async function DELETE(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const session = await auth()
  const userId = session?.user?.id ?? null

  const annotation = await prisma.annotation.findUnique({ where: { id } })
  if (!annotation) return NextResponse.json({ error: "Not found" }, { status: 404 })

  // Allow delete if userId matches, or both are null (anonymous)
  if (annotation.userId !== userId) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 })
  }

  await prisma.annotation.delete({ where: { id } })
  return NextResponse.json({ ok: true })
}
