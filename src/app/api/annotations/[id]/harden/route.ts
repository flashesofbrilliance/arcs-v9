import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export async function POST(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const { id } = await params
  const annotation = await prisma.annotation.findUnique({ where: { id }, select: { kernel: true, userId: true } })
  if (!annotation) return NextResponse.json({ error: "Not found" }, { status: 404 })
  if (annotation.userId !== userId) return NextResponse.json({ error: "Forbidden" }, { status: 403 })
  if (!annotation.kernel) return NextResponse.json({ error: "Distill a kernel first" }, { status: 400 })

  await prisma.annotation.update({ where: { id }, data: { hardened: true } })
  return NextResponse.json({ ok: true })
}
