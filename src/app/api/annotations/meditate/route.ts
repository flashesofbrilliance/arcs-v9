import { NextRequest, NextResponse } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

const client = new Anthropic()

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const { receiptId } = await req.json()
  if (!receiptId) return NextResponse.json({ error: "receiptId required" }, { status: 400 })

  const annotations = await prisma.annotation.findMany({
    where: { receiptId, userId },
    orderBy: { createdAt: "asc" },
    take: 40,
    select: { type: true, anchorText: true, body: true, kernel: true },
  })

  if (annotations.length === 0) {
    return NextResponse.json({ ok: true, held: [], falsified: [], elevated: [] })
  }

  const annotationDump = annotations
    .map((a) => `[${a.type}] anchor: "${a.anchorText}" | note: "${a.body}"${a.kernel ? ` | kernel: "${a.kernel}"` : ""}`)
    .join("\n")

  const msg = await client.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 512,
    temperature: 0,
    system: `You are a belief-diff analyzer. Given a set of annotations made while reading a decision document, identify:
- held: beliefs or assumptions the author held firm under scrutiny (max 3 short phrases)
- falsified: beliefs that were challenged, contradicted, or shown to be incomplete (max 3 short phrases)
- elevated: beliefs or considerations that rose in priority through the reading (max 3 short phrases)

Return ONLY valid JSON: { "held": [...], "falsified": [...], "elevated": [...] }
Each item is a short, declarative phrase (under 12 words). No hedges. No markdown.`,
    messages: [{ role: "user", content: annotationDump }],
  })

  const raw = msg.content[0].type === "text" ? msg.content[0].text.trim() : "{}"
  let result: { held: string[]; falsified: string[]; elevated: string[] }
  try {
    result = JSON.parse(raw)
  } catch {
    result = { held: [], falsified: [], elevated: [] }
  }

  return NextResponse.json({ ok: true, ...result })
}
