import Anthropic from "@anthropic-ai/sdk"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { modelErrorResponse } from "@/lib/model-error"
import { MODELS } from "@/lib/claude-models"

export const dynamic = "force-dynamic"

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

export async function POST(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await auth()
  // Signed-in only: a null userId would match every anonymous row.
  const userId = session?.user?.id
  if (!userId) return NextResponse.json({ error: "Sign in required" }, { status: 401 })

  const { id } = await params

  const annotation = await prisma.annotation.findUnique({ where: { id }, select: { userId: true, type: true, anchorText: true, body: true } })
  if (!annotation) return NextResponse.json({ error: "Not found" }, { status: 404 })
  if (annotation.userId !== userId) return NextResponse.json({ error: "Forbidden" }, { status: 403 })

  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 503 })
  }

  let message: Anthropic.Message
  try {
  message = await anthropic.messages.create({
    model: MODELS.fast,
    max_tokens: 256,
    system: "Extract the invariant kernel - the smallest truth that survives compression. One sentence. No hedges. Wuwei register: simple, direct, final.",
    messages: [{
      role: "user",
      content: `TYPE: ${annotation.type}\nANCHOR: "${annotation.anchorText}"\nNOTE: "${annotation.body}"`,
    }],
  })
  } catch (e) {
    return modelErrorResponse("annotations/shavasana", e)
  }



  const kernel = message.content[0].type === "text" ? message.content[0].text.trim() : ""

  await prisma.annotation.update({ where: { id }, data: { kernel } })

  return NextResponse.json({ ok: true, kernel })
}
