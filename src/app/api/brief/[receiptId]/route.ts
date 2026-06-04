import Anthropic from "@anthropic-ai/sdk"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

// Generates the Situation Framing section of a cartography brief.
// Called lazily — brief is generated once and stored. Subsequent GETs return stored version.
const BRIEF_SYSTEM = `You are the ARCS Brief Writer. Given a decision receipt from the ARCS Question Compass, write the Situation Framing section of a cartography brief.

Situation Framing is 2–3 paragraphs of intelligence-grade prose that:
- Narrates WHERE the decision-maker stands right now — current position in the terrain
- Describes WHAT FORCES are at work: what has momentum, what is resisted, what is open
- Names the entity if present, their role and what is specifically at stake for them
- Reads like a situation room brief: present tense, active voice, concrete details
- Does NOT restate the True North — that appears in a separate brief section
- Does NOT use bullet points, headers, or markdown

Return only the prose. No preamble, no labels, no formatting.`

const ENTITY_SYSTEM = `You are the ARCS Entity Intelligence layer. Given a decision context and a named entity (person, company, panel, or group), produce a structured intelligence read on that entity as it relates to this specific decision terrain.

Return ONLY this JSON object (no markdown, no preamble):
{
  "role": "one sentence — who/what this entity is in this specific terrain",
  "leverage_theirs": "one sentence — what power, leverage, or optionality they hold",
  "leverage_yours": "one sentence — what leverage, alternatives, or exit options you hold",
  "alignment": "ALIGNED | NEUTRAL | MISALIGNED | ADVERSARIAL",
  "alignment_read": "one sentence — why you read their alignment this way",
  "signal_to_watch": "one sentence — the leading indicator that their position is shifting",
  "risk_surface": "one sentence — the specific failure mode if this relationship goes wrong"
}`

function parseEntityAnalysis(raw: string): Record<string, string> | null {
  try {
    const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
    return JSON.parse(cleaned)
  } catch {
    return null
  }
}

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const { receiptId } = await params

  // Serve from store if already generated
  const existing = await prisma.brief.findUnique({ where: { receiptId }, include: { receipt: true } })
  if (existing) {
    const tributaries = (() => {
      try {
        const raw = existing.receipt?.rawResponse ? JSON.parse(existing.receipt.rawResponse) : null
        return Array.isArray(raw?.tributaries) ? raw.tributaries : []
      } catch { return [] }
    })()
    const entityAnalysis = (() => {
      try { return existing.entityAnalysis ? JSON.parse(existing.entityAnalysis) : null }
      catch { return null }
    })()
    return NextResponse.json({ ok: true, brief: existing, receipt: existing.receipt, tributaries, entityAnalysis })
  }

  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    include: { prep: true },
  })
  if (!receipt) return NextResponse.json({ error: "Receipt not found" }, { status: 404 })
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 503 })
  }

  const why = JSON.parse(receipt.whyBullets) as string[]
  const protecting = receipt.prep ? (JSON.parse(receipt.prep.protecting) as string[]) : []
  const fated = receipt.fated ? (JSON.parse(receipt.fated) as Record<string, string>) : null

  const baseContext = [
    `DECISION: ${receipt.decision}`,
    `TRUE NORTH: ${receipt.trueNorth}`,
    `WHY: ${why.join(" | ")}`,
    `MODE: ${receipt.mode}  DOOR: ${receipt.doorClass ?? "TWO_WAY"}`,
    `NCI: ${receipt.nciScore}/100  Y STATE: ${receipt.yState}`,
    receipt.entity ? `ENTITY: ${receipt.entity}` : null,
    protecting.length > 0 ? `PROTECTING: ${protecting.join(", ")}` : null,
    fated
      ? `FATED:\n  Facts: ${fated.facts ?? ""}\n  Assumptions: ${fated.assumptions ?? ""}\n  Tradeoffs: ${fated.tradeoffs ?? ""}\n  Direction: ${fated.direction ?? ""}`
      : null,
    receipt.prep?.adversarialInput ? `ADVERSARIAL VECTOR: ${receipt.prep.adversarialInput}` : null,
  ].filter(Boolean).join("\n")

  // Fire situation framing + entity analysis in parallel
  const calls: Promise<Anthropic.Message>[] = [
    anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 600,
      system: BRIEF_SYSTEM,
      messages: [{ role: "user", content: `${baseContext}\n\nWrite the Situation Framing section.` }],
    }),
  ]

  if (receipt.entity) {
    calls.push(
      anthropic.messages.create({
        model: "claude-sonnet-4-6",
        max_tokens: 512,
        system: ENTITY_SYSTEM,
        messages: [{ role: "user", content: `${baseContext}\n\nGenerate the entity intelligence read for: ${receipt.entity}` }],
      })
    )
  }

  const results = await Promise.all(calls)
  const situationFraming = results[0].content[0].type === "text" ? results[0].content[0].text.trim() : ""
  const entityAnalysis = receipt.entity && results[1]
    ? parseEntityAnalysis(results[1].content[0].type === "text" ? results[1].content[0].text : "")
    : null

  // Parse tributaries from rawResponse
  const tributaries = (() => {
    try {
      const raw = receipt.rawResponse ? JSON.parse(receipt.rawResponse) : null
      return Array.isArray(raw?.tributaries) ? raw.tributaries : []
    } catch { return [] }
  })()

  try {
    const brief = await prisma.brief.create({
      data: {
        receiptId,
        situationFraming,
        entityAnalysis: entityAnalysis ? JSON.stringify(entityAnalysis) : null,
      },
    })
    return NextResponse.json({ ok: true, brief, receipt, tributaries, entityAnalysis })
  } catch {
    const stored = await prisma.brief.findUnique({ where: { receiptId } })
    const storedEntity = (() => {
      try { return stored?.entityAnalysis ? JSON.parse(stored.entityAnalysis) : null }
      catch { return null }
    })()
    return NextResponse.json({ ok: true, brief: stored, receipt, tributaries, entityAnalysis: storedEntity })
  }
}
