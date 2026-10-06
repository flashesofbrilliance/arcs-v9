import Anthropic from "@anthropic-ai/sdk"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { modelErrorResponse } from "@/lib/model-error"
import { clampText, clampTextArray } from "@/lib/sanitize"
import { scrubProse, scrubDeep, scrubReceiptProse } from "@/lib/prose"
import { BRIEF_SYSTEM } from "@/lib/briefPrompt"
import { rateLimit, clientIp } from "@/lib/ratelimit"

export const dynamic = "force-dynamic"
// Generates situation framing + entity analysis via Claude (parallel calls).
// Same timeout exposure as the compass route - without this the function can be
// killed mid-generation and the receipt page shows "Could not load receipt".
export const maxDuration = 60

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

// Situation Framing prompt lives in @/lib/briefPrompt (shared with the eval harness).
// Called lazily - brief is generated once and stored. Subsequent GETs return stored version.

const ENTITY_SYSTEM = `You are the ARCS Entity Intelligence layer. Given a decision context and a named entity (person, company, panel, or group), produce a structured intelligence read on that entity as it relates to this specific decision terrain.

STYLE: Never use em-dashes. Write short, plain, direct sentences. Use a period, comma, or colon instead of a dash. Dash-spliced prose reads as machine-generated.

Return ONLY this JSON object (no markdown, no preamble):
{
  "role": "one sentence - who/what this entity is in this specific terrain",
  "leverage_theirs": "one sentence - what power, leverage, or optionality they hold",
  "leverage_yours": "one sentence - what leverage, alternatives, or exit options you hold",
  "alignment": "ALIGNED | NEUTRAL | MISALIGNED | ADVERSARIAL",
  "alignment_read": "one sentence - why you read their alignment this way",
  "signal_to_watch": "one sentence - the leading indicator that their position is shifting",
  "risk_surface": "one sentence - the specific failure mode if this relationship goes wrong"
}`

function parseEntityAnalysis(raw: string): Record<string, string> | null {
  try {
    const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
    const o = JSON.parse(cleaned) as Record<string, unknown>
    return Object.fromEntries(Object.entries(o).map(([k, v]) => [k, typeof v === "string" ? scrubProse(v) : v])) as Record<string, string>
  } catch {
    return null
  }
}

// Anyone holding a brief link can read this response, so it carries only what
// the brief and receipt pages render: no owner id, no raw model output beyond
// the reasoning, and never the prep's "strongest argument against" notes.
// sessionId (the thread id) is returned only to the signed-in owner.
function publicReceipt(r: object | null | undefined, viewerId: string | null) {
  if (!r) return r
  const { userId: owner, sessionId, rawResponse, prep, ...rest } = r as Record<string, unknown>
  const isOwner = viewerId !== null && owner === viewerId
  let reasoning: unknown = undefined
  try { reasoning = typeof rawResponse === "string" ? (JSON.parse(rawResponse) as { reasoning?: unknown }).reasoning : undefined } catch { /* malformed: omit */ }
  const safePrep = prep && typeof prep === "object" ? (({ adversarialInput: _a, userId: _pu, ...p }) => p)(prep as Record<string, unknown>) : prep
  return { ...rest, ...(isOwner ? { sessionId } : {}), rawResponse: JSON.stringify(reasoning === undefined ? {} : { reasoning }), ...(prep !== undefined ? { prep: safePrep } : {}) }
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const { receiptId } = await params

  // Owner-only (Zach, 2026-10-05). The receipt id is no longer a capability:
  // anyone else reaches a brief only through an owner-minted share token
  // (/api/shared/brief/[token]). Anonymous receipts (userId null) have no owner
  // to match and are not served here; see src/lib/briefShare.ts. 404, never 403,
  // so an id never confirms it exists.
  const notFound = () => NextResponse.json({ error: "Receipt not found" }, { status: 404 })
  if (!userId) return notFound()
  const owned = await prisma.receipt.findUnique({ where: { id: receiptId }, select: { userId: true } })
  if (!owned || owned.userId !== userId) return notFound()

  // Serve from store if already generated
  // children = the tributary rounds spawned from this receipt (down-chain nav).
  // Scoped to the owner: compass takes parentReceiptId from the client, so another
  // account could parent its own receipt here and would otherwise surface in this list.
  const childrenInclude = {
    children: {
      where: { userId },
      select: { id: true, decision: true, trueNorth: true, yState: true, nciScore: true, version: true, createdAt: true },
      orderBy: { createdAt: "asc" as const },
    },
  }

  const existing = await prisma.brief.findUnique({ where: { receiptId }, include: { receipt: { include: childrenInclude } } })
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
    // Stored briefs predating the style rule render clean without rewriting the row.
    const brief = { ...existing, situationFraming: scrubProse(existing.situationFraming) }
    const entityClean = entityAnalysis
      ? Object.fromEntries(Object.entries(entityAnalysis as Record<string, unknown>).map(([k, v]) => [k, typeof v === "string" ? scrubProse(v) : v]))
      : null
    return NextResponse.json({ ok: true, brief, receipt: publicReceipt(scrubReceiptProse(existing.receipt), userId), tributaries: scrubDeep(tributaries), entityAnalysis: entityClean })
  }

  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    include: { prep: true, ...childrenInclude },
  })
  if (!receipt) return NextResponse.json({ error: "Receipt not found" }, { status: 404 })
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 503 })
  }
  // A cache miss spends model tokens and needs no session, so cap generations
  // per client. Stored briefs (above) are never limited.
  const rl = rateLimit(`brief-gen:${clientIp(req)}`, { limit: 20, windowMs: 10 * 60_000 })
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })
  }

  const why = JSON.parse(receipt.whyBullets) as string[]
  const protecting = receipt.prep ? (JSON.parse(receipt.prep.protecting) as string[]) : []
  const fated = receipt.fated ? (JSON.parse(receipt.fated) as Record<string, string>) : null

  // Defense-in-depth: clampText the untrusted receipt fields here too, so pre-existing
  // receipts (persisted before the compass-side sanitization) can't smuggle control chars
  // or overlong payloads into this second model call.
  const baseContext = [
    `DECISION: ${clampText(receipt.decision, 4000)}`,
    `TRUE NORTH: ${clampText(receipt.trueNorth, 2000)}`,
    `WHY: ${clampTextArray(why, 8, 2000).join(" | ")}`,
    `MODE: ${receipt.mode}  DOOR: ${receipt.doorClass ?? "TWO_WAY"}`,
    `NCI: ${receipt.nciScore}/100  Y STATE: ${receipt.yState}`,
    receipt.entity ? `ENTITY: ${clampText(receipt.entity, 500)}` : null,
    protecting.length > 0 ? `PROTECTING: ${clampTextArray(protecting, 12, 500).join(", ")}` : null,
    fated
      ? `FATED:\n  Facts: ${clampText(fated.facts, 1500)}\n  Assumptions: ${clampText(fated.assumptions, 1500)}\n  Tradeoffs: ${clampText(fated.tradeoffs, 1500)}\n  Direction: ${clampText(fated.direction, 1500)}`
      : null,
    receipt.prep?.adversarialInput ? `ADVERSARIAL VECTOR: ${clampText(receipt.prep.adversarialInput, 2000)}` : null,
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

  let results: Anthropic.Message[]
  try { results = await Promise.all(calls) }
  catch (e) { return modelErrorResponse("brief", e) }
  const situationFraming = scrubProse(results[0].content[0].type === "text" ? results[0].content[0].text.trim() : "")
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
    const children = (receipt as Record<string, unknown> & { children?: unknown[] }).children ?? []
    return NextResponse.json({ ok: true, brief, receipt: publicReceipt(scrubReceiptProse(receipt), userId), tributaries: scrubDeep(tributaries), entityAnalysis, children: scrubDeep(children) })
  } catch {
    const stored = await prisma.brief.findUnique({ where: { receiptId } })
    const storedEntity = (() => {
      try { return stored?.entityAnalysis ? JSON.parse(stored.entityAnalysis) : null }
      catch { return null }
    })()
    const children = (receipt as Record<string, unknown> & { children?: unknown[] }).children ?? []
    return NextResponse.json({ ok: true, brief: stored ? { ...stored, situationFraming: scrubProse(stored.situationFraming) } : stored, receipt: publicReceipt(scrubReceiptProse(receipt), userId), tributaries: scrubDeep(tributaries), entityAnalysis: storedEntity ? scrubDeep(storedEntity) : storedEntity, children: scrubDeep(children) })
  }
}
