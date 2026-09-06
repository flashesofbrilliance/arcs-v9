// ADR-020 Tribune Intelligence Layer — POST /api/tribune (generate one phase), GET ?receipt_id= (read).
//
// Implementation order (ADR-020): (1) this route with the Proactive silence gate,
// (2) the Tribune migration + Receipt.batonId, (3-5) per-phase generation, lazy/on-demand.
// Auth required (ADR-016 gate): the caller must own the receipt. Annotates, never mutates.
import Anthropic from "@anthropic-ai/sdk"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { rateLimit, clientIp } from "@/lib/ratelimit"
import { clampText } from "@/lib/sanitize"
import {
  PHASES,
  buildTribunePrompt,
  courtInvoked,
  nciDelta,
  parseTribuneContent,
  projectContent,
  riskTierOf,
  shouldSpeak,
  type ClarityMode,
  type TribuneContent,
  type TribunePhase,
} from "@/lib/tribune"

export const dynamic = "force-dynamic"

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
// Anterior/Proactive are short reads → Haiku; Posterior weighs an outcome record → Sonnet.
const MODEL: Record<TribunePhase, { model: string; max_tokens: number; temperature: number }> = {
  anterior: { model: "claude-haiku-4-5-20251001", max_tokens: 1800, temperature: 0.2 },
  proactive: { model: "claude-haiku-4-5-20251001", max_tokens: 1800, temperature: 0.2 },
  posterior: { model: "claude-sonnet-4-6", max_tokens: 2200, temperature: 0.3 },
}

const CLARITY = new Set<ClarityMode>(["SIMPLE", "RICH", "DEEP"])

async function ownedReceipt(receiptId: string, userId: string) {
  return prisma.receipt.findFirst({
    where: { id: receiptId, userId },
    include: { outcome: true, tribunes: true },
  })
}

export async function GET(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const receiptId = clampText(req.nextUrl.searchParams.get("receipt_id"), 64)
  if (!receiptId) return NextResponse.json({ error: "receipt_id required" }, { status: 400 })
  const receipt = await ownedReceipt(receiptId, userId)
  if (!receipt) return NextResponse.json({ error: "Not found" }, { status: 404 })
  const mode = (CLARITY.has(receipt.clarityMode as ClarityMode) ? receipt.clarityMode : "SIMPLE") as ClarityMode
  return NextResponse.json({
    receipt_id: receipt.id,
    baton_id: receipt.batonId,
    tribunes: receipt.tribunes.map((t) => ({
      phase: t.phase,
      risk_tier: t.riskTier,
      drift_state: t.driftState,
      nci_delta: t.nciDelta,
      court_invoked: t.courtInvoked,
      created_at: t.createdAt,
      content: projectContent(JSON.parse(t.content) as TribuneContent, mode),
    })),
  })
}

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const rl = rateLimit(`tribune:${userId}:${clientIp(req)}`, { limit: 20, windowMs: 60_000 })
  if (!rl.ok) return NextResponse.json({ error: "Rate limited" }, { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } })

  let body: Record<string, unknown>
  try {
    body = (await req.json()) as Record<string, unknown>
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 })
  }
  const receiptId = clampText(body.receipt_id, 64)
  const phase = clampText(body.phase, 16) as TribunePhase
  const batonId = clampText(body.baton_id, 64) || null
  const force = body.force === true
  if (!receiptId || !PHASES.includes(phase)) {
    return NextResponse.json({ error: "receipt_id and phase (anterior|proactive|posterior) required" }, { status: 400 })
  }

  const receipt = await ownedReceipt(receiptId, userId)
  if (!receipt) return NextResponse.json({ error: "Not found" }, { status: 404 })
  const clarityMode = (CLARITY.has(receipt.clarityMode as ClarityMode) ? receipt.clarityMode : "SIMPLE") as ClarityMode

  // Lazy: an existing phase row is returned, not regenerated, unless force.
  const existing = receipt.tribunes.find((t) => t.phase === phase)
  if (existing && !force) {
    return NextResponse.json({
      phase,
      cached: true,
      content: projectContent(JSON.parse(existing.content) as TribuneContent, clarityMode),
    })
  }

  // Kinematic signals — intra-session only (ADR-020 v1): NCI delta vs the session's seed receipt.
  const seed = await prisma.receipt.findFirst({
    where: { sessionId: receipt.sessionId, parentId: null },
    orderBy: { createdAt: "asc" },
    select: { nciScore: true },
  })
  const delta = nciDelta(seed?.nciScore, receipt.nciScore)
  const tier = riskTierOf(receipt)
  // Drift Sentinel state is persisted on Receipt by the compass write (ygate.driftState); topology is the fallback for pre-schema rows.
  const drift = receipt.driftState ?? (receipt.flowTopology === "LOOPING" ? "LOOPING" : null)
  const court = courtInvoked(receipt, tier)

  // Proactive silence gate: below threshold the Tribune stays silent and persists nothing.
  let speakReasons: string[] = []
  if (phase === "proactive") {
    speakReasons = shouldSpeak({ riskTier: tier, driftState: drift, nciDelta: delta })
    if (speakReasons.length === 0 && !force) {
      return NextResponse.json({ phase, silent: true, risk_tier: tier, drift_state: drift, nci_delta: delta })
    }
  }
  if (phase === "posterior" && !receipt.outcome && !force) {
    return NextResponse.json({ error: "Posterior needs an Outcome on the receipt first (or force:true)" }, { status: 409 })
  }

  // Prior phase output feeds the next (anterior → proactive → posterior).
  const priorRow = receipt.tribunes
    .filter((t) => PHASES.indexOf(t.phase as TribunePhase) < PHASES.indexOf(phase))
    .sort((a, b) => PHASES.indexOf(b.phase as TribunePhase) - PHASES.indexOf(a.phase as TribunePhase))[0]
  const priorTribune = priorRow ? (JSON.parse(priorRow.content) as TribuneContent) : null

  const prompt = buildTribunePrompt({
    phase,
    receipt,
    riskTier: tier,
    driftState: drift,
    nciDelta: delta,
    clarityMode,
    speakReasons,
    priorTribune,
    outcome: receipt.outcome
      ? { outcome: (receipt.outcome as Record<string, unknown>).outcome as string | null, note: (receipt.outcome as Record<string, unknown>).note as string | null }
      : null,
  })

  const cfg = MODEL[phase]
  let content: TribuneContent
  try {
    const msg = await anthropic.beta.messages.create({
      model: cfg.model,
      max_tokens: cfg.max_tokens,
      temperature: cfg.temperature,
      betas: ["prompt-caching-2024-07-31"],
      system: [{ type: "text" as const, text: prompt.system, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: prompt.user }],
    })
    const raw = msg.content[0]?.type === "text" ? msg.content[0].text : ""
    if (!raw.trim()) return NextResponse.json({ error: "Model returned empty response" }, { status: 502 })
    if (msg.stop_reason === "max_tokens") return NextResponse.json({ error: "Model response truncated" }, { status: 502 })
    content = parseTribuneContent(raw, phase)
  } catch (err) {
    const m = err instanceof Error ? err.message : String(err)
    return NextResponse.json({ error: err instanceof SyntaxError ? "Model returned non-JSON response" : m }, { status: 502 })
  }

  const row = await prisma.tribune.upsert({
    where: { receiptId_phase: { receiptId: receipt.id, phase } },
    create: {
      receiptId: receipt.id,
      phase,
      riskTier: tier,
      labResult: JSON.stringify(content.lab),
      courtInvoked: court,
      driftState: drift,
      nciDelta: delta,
      clarityMode,
      batonId,
      boardVotes: JSON.stringify(content.board),
      content: JSON.stringify(content),
      model: cfg.model,
    },
    update: {
      riskTier: tier,
      labResult: JSON.stringify(content.lab),
      courtInvoked: court,
      driftState: drift,
      nciDelta: delta,
      clarityMode,
      ...(batonId ? { batonId } : {}),
      boardVotes: JSON.stringify(content.board),
      content: JSON.stringify(content),
      model: cfg.model,
    },
  })
  // Baton hand-off is the one additive write on the Receipt (nullable column, ADR-020 schema).
  if (batonId && batonId !== receipt.batonId) {
    await prisma.receipt.update({ where: { id: receipt.id }, data: { batonId } })
  }

  return NextResponse.json({
    phase,
    tribune_id: row.id,
    risk_tier: tier,
    drift_state: drift,
    nci_delta: delta,
    court_invoked: court,
    fired_on: speakReasons,
    coalition_readiness: content.coalition_readiness,
    content: projectContent(content, clarityMode),
  })
}
