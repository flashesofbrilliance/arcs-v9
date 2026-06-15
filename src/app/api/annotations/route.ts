import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const body = await req.json()
  const { receiptId, surface = "BRIEF", anchorText, preContext = "", postContext = "", type, body: annotationBody, linkedRef } = body

  if (!receiptId || !anchorText || !type || !annotationBody) {
    return NextResponse.json({ error: "receiptId, anchorText, type, and body are required" }, { status: 400 })
  }
  if (!["THOUGHT", "COMMENT", "REACTION"].includes(type)) {
    return NextResponse.json({ error: "type must be THOUGHT, COMMENT, or REACTION" }, { status: 400 })
  }

  const annotation = await prisma.annotation.create({
    data: {
      userId,
      receiptId,
      surface,
      anchorText,
      preContext,
      postContext,
      type,
      body: annotationBody,
      linkedRef: linkedRef ? JSON.stringify(linkedRef) : null,
    },
  })

  return NextResponse.json({ ok: true, annotation })
}
