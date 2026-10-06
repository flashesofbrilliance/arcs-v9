import Anthropic from "@anthropic-ai/sdk"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { modelErrorResponse } from "@/lib/model-error"
import { z } from "zod"
import { clampText } from "@/lib/sanitize"
import { rateLimit, clientIp } from "@/lib/ratelimit"
import { MODELS } from "@/lib/claude-models"

export const dynamic = "force-dynamic"

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const GUIDE_SYSTEM = `You are the ARCS Field OS Guide Generator. Generate a structured field guide for entering a high-stakes interaction with a named entity.

MODE DEFINITIONS:
RECON - 5-minute read. Generate exactly 1 stage. Agenda = 2 items. PreWork = 2 items. Artifacts = 1.
ACTIVE - 20-minute prep. Generate exactly 2 stages. Agenda = 3 items each. Artifacts = 2 each.
LEAD - 60-minute deep prep. Generate 3–5 stages (Claude decides based on entity complexity). Full content.

PER STAGE FIELDS:
- id: T0, T1, T2...
- title: specific to THIS entity and stage (not generic)
- shortLabel: 2-3 words
- spineLabel: entity name/role at this stage (e.g. "Emma (HM)", "Panel", "Offer")
- questionCompass: core binary question - answerable Yes/No by end of stage. "Is..." or "Can I..."
- stageJTBD: what the operator MUST accomplish. 1 sentence.
- testingAboutThem: what the OTHER party is SILENTLY evaluating. 1 sentence. REQUIRED.
- agenda: action items the operator does/says IN the stage
- preWork: preparation tasks BEFORE the stage
- kycLens: intelligence reads. Each prefixed KYC:, KYT:, KYB:, or KYI:
- midcurveTripwire: warning sign of going generic. Starts with "If I..."
- writesIntoNextTable: { yes: "what advances if stage goes well", no: "what to do if it goes poorly" }
- artifacts: [{ title, abstract }] - title is specific doc name, abstract is one-line purpose

RULES:
- Every field must reference the specific entity, not generic interview advice
- If entity contains "panel" or "committee": expand kycLens to show per-role reads
- If entity has named affiliation: infer role archetype, label as [inferred]
- Never exceed 75 words in any single agenda or preWork item
- midcurveTripwire is always one sentence

OUTCOME TARGET RULES:
- outcome_statement: stage-specific and entity-specific. Format: "By end of [stage], [entity] has [specific observable action]"
- leading_indicator: behavioral, not attitudinal ("she schedules X" not "she seems interested")
- kpi_label: noun phrase, 5–8 words max (not a sentence)
- failure_signal: starts with a verb ("Asks for...", "Redirects to...", "Goes silent on...")

STYLE: Never use em-dashes. Write short, plain, direct sentences. Use a period, comma, or colon instead of a dash. Dash-spliced prose reads as machine-generated.

Return ONLY this JSON (no markdown, no preamble):
{
  "guide_title": "string",
  "bet_label": "string",
  "total_prep_hours": "string",
  "outcome_target": {
    "outcome_statement": "By end of [stage], [entity] has [specific observable action]",
    "leading_indicator": "one sentence - signal that appears before the outcome is confirmed",
    "kpi_label": "short measurable proxy (5–8 words max)",
    "failure_signal": "early warning the engagement is going wrong"
  },
  "stages": [
    {
      "id": "T0",
      "title": "string",
      "shortLabel": "string",
      "spineLabel": "string",
      "questionCompass": "string",
      "stageJTBD": "string",
      "testingAboutThem": "string",
      "agenda": ["string"],
      "preWork": ["string"],
      "kycLens": ["string"],
      "midcurveTripwire": "string",
      "writesIntoNextTable": { "yes": "string", "no": "string" },
      "artifacts": [{ "title": "string", "abstract": "string" }]
    }
  ]
}`

function buildContext(receipt: {
  decision: string
  trueNorth: string
  entity: string | null
  mode: string
  nciScore: number
  yState: string
  fated: string | null
  protecting: string
  prep?: {
    stakes: string | null
    horizon: string | null
    confidence: number | null
    adversarialInput: string | null
  } | null
}): string {
  const parts = [
    `Decision: ${receipt.decision}`,
    `True North: ${receipt.trueNorth}`,
    `Entity: ${receipt.entity ?? "Unknown"}`,
    `Mode: ${receipt.mode}`,
    `NCI Score: ${receipt.nciScore}`,
    `Y State: ${receipt.yState}`,
  ]
  if (receipt.fated) {
    try {
      const f = JSON.parse(receipt.fated)
      parts.push(`FATED - Facts: ${f.facts ?? ""} | Assumptions: ${f.assumptions ?? ""} | Tradeoffs: ${f.tradeoffs ?? ""} | Direction: ${f.direction ?? ""}`)
    } catch { /* ignore */ }
  }
  try {
    const protecting = JSON.parse(receipt.protecting)
    if (protecting.length) parts.push(`Protecting: ${protecting.join(", ")}`)
  } catch { /* ignore */ }
  if (receipt.prep) {
    const p = receipt.prep
    if (p.stakes) parts.push(`Stakes: ${p.stakes}`)
    if (p.horizon) parts.push(`Horizon: ${p.horizon}`)
    if (p.confidence) parts.push(`Confidence (1-5): ${p.confidence}`)
    if (p.adversarialInput) parts.push(`Adversarial input: ${p.adversarialInput}`)
  }
  return parts.join("\n")
}

function guideShape(guide: {
  id: string
  receiptId: string
  mode: string
  guideTitle: string
  betLabel: string
  totalPrepHours: string
  stages: string
  stageLog: string
  outcomeStatement: string
  leadingIndicator: string
  kpiLabel: string
  failureSignal: string
  generatedAt: Date
  receipt: { entity: string | null; decision: string }
}) {
  return {
    ok: true,
    guide,
    meta: {
      guideTitle: guide.guideTitle,
      betLabel: guide.betLabel,
      totalPrepHours: guide.totalPrepHours,
    },
    entity: guide.receipt.entity,
    decision: guide.receipt.decision,
    outcomeStatement: guide.outcomeStatement,
    leadingIndicator: guide.leadingIndicator,
    kpiLabel: guide.kpiLabel,
    failureSignal: guide.failureSignal,
  }
}

// A guide is private prep on someone's receipt: only the receipt's owner may
// read, generate, or log against it. Anonymous receipts (userId null) have no
// owner to match, so they are reachable only through the dev bypass below.
// Returns null when allowed, else the response to send (404, never 403, so a
// receipt id never confirms it exists).
async function ownerGate(receiptId: string, userId: string | null): Promise<NextResponse | null> {
  if (!userId && process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  if (!userId) return null // dev only
  const r = await prisma.receipt.findUnique({ where: { id: receiptId }, select: { userId: true } })
  if (!r || r.userId !== userId) return NextResponse.json({ error: "Receipt not found" }, { status: 404 })
  return null
}

const GuideBody = z.object({
  mode: z.enum(["RECON", "ACTIVE", "LEAD"]),
  entityOverride: z.string().trim().min(1).max(500).optional(),
})

const StageLogBody = z.object({
  stageId: z.string().max(16),
  verdict: z.string().max(64),
  vibe: z.string().max(500).optional(),
  completedAt: z.string().max(64),
})

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const { receiptId } = await params
  const denied = await ownerGate(receiptId, userId)
  if (denied) return denied
  const guide = await prisma.prepGuide.findUnique({
    where: { receiptId },
    include: { receipt: { select: { entity: true, decision: true } } },
  })
  if (guide) {
    return NextResponse.json(guideShape(guide))
  }
  return NextResponse.json({ ok: false, guide: null })
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const { receiptId } = await params
  const denied = await ownerGate(receiptId, userId)
  if (denied) return denied
  const parsedBody = GuideBody.safeParse(await req.json().catch(() => null))
  if (!parsedBody.success) return NextResponse.json({ error: "Invalid body" }, { status: 400 })
  const { mode, entityOverride } = parsedBody.data
  const rl = rateLimit(`guide-gen:${userId ?? "dev"}:${clientIp(req)}`, { limit: 10, windowMs: 10 * 60_000 })
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })
  }

  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    include: { prep: true },
  })
  if (!receipt) {
    return NextResponse.json({ error: "Receipt not found" }, { status: 404 })
  }

  const receiptWithEntity = entityOverride
    ? { ...receipt, entity: clampText(entityOverride, 500) }
    : receipt
  const context = buildContext(receiptWithEntity)
  const userMsg = `Generate a ${mode} field guide for this decision context:\n\n${context}`

  let response: Anthropic.Message
  try {
    response = await anthropic.messages.create({
      model: MODELS.guide,
      max_tokens: 3000,
      system: GUIDE_SYSTEM,
      messages: [{ role: "user", content: userMsg }],
    })
  } catch (e) {
    return modelErrorResponse("guide", e)
  }

  const raw = response.content[0].type === "text" ? response.content[0].text : ""
  const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
  const parsed = JSON.parse(cleaned) as {
    guide_title: string
    bet_label: string
    total_prep_hours: string
    outcome_target?: {
      outcome_statement: string
      leading_indicator: string
      kpi_label: string
      failure_signal: string
    }
    stages: unknown[]
  }

  const ot = parsed.outcome_target

  const guide = await prisma.prepGuide.create({
    data: {
      receiptId,
      mode,
      guideTitle: parsed.guide_title,
      betLabel: parsed.bet_label,
      totalPrepHours: parsed.total_prep_hours,
      stages: JSON.stringify(parsed.stages),
      stageLog: "[]",
      outcomeStatement: ot?.outcome_statement ?? "",
      leadingIndicator: ot?.leading_indicator ?? "",
      kpiLabel: ot?.kpi_label ?? "",
      failureSignal: ot?.failure_signal ?? "",
    },
    include: { receipt: { select: { entity: true, decision: true } } },
  })

  return NextResponse.json(guideShape(guide))
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const { receiptId } = await params
  const denied = await ownerGate(receiptId, userId)
  if (denied) return denied
  const parsedLog = StageLogBody.safeParse(await req.json().catch(() => null))
  if (!parsedLog.success) return NextResponse.json({ error: "Invalid body" }, { status: 400 })
  const { stageId, verdict, vibe, completedAt } = parsedLog.data

  const existing = await prisma.prepGuide.findUnique({ where: { receiptId } })
  if (!existing) {
    return NextResponse.json({ error: "Guide not found" }, { status: 404 })
  }

  let log: { stageId: string; completedAt: string; verdict: string; vibe?: string }[] = []
  try {
    log = JSON.parse(existing.stageLog)
  } catch { /* ignore */ }

  const newLog = [...log.filter(e => e.stageId !== stageId), { stageId, completedAt, verdict, vibe }]

  await prisma.prepGuide.update({
    where: { receiptId },
    data: { stageLog: JSON.stringify(newLog) },
  })

  return NextResponse.json({ ok: true })
}
