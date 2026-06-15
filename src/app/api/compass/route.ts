import Anthropic from "@anthropic-ai/sdk"
import { Resend } from "resend"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { computeYGate } from "@/lib/ygate"
import { auth } from "@/lib/auth"

const resend = process.env.AUTH_RESEND_KEY ? new Resend(process.env.AUTH_RESEND_KEY) : null

export const dynamic = "force-dynamic"

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

function selectMode(horizon: string, stakes: string): "QUICKMOVE" | "PLAN" | "COURT" {
  if (stakes === "HIGH") return "COURT"
  if (horizon === "THIS_QUARTER" || horizon === "ONE_TO_THREE_YEARS") return "COURT"
  if (horizon === "TODAY" && stakes === "LOW") return "QUICKMOVE"
  return "PLAN"
}

function doorClass(horizon: string, stakes: string): string {
  return stakes === "HIGH" || horizon === "THIS_QUARTER" || horizon === "ONE_TO_THREE_YEARS"
    ? "ONE_WAY"
    : "TWO_WAY"
}

const SYSTEM = `You are the ARCS Question Compass — a boardroom-grade decision intelligence engine.
Your job is to run a user's decision through the L0–L5 pipeline and return a structured JSON response.

PIPELINE:
L0  Activation filter: is this a real decision? If noise/informational, redirect in true_north.
L1  Loki adversarial: 1–2 strongest objections or failure modes.
L2  Bayesian validation: what priors and evidence bear on this? P(success)?
L3  Kintsugi immune: anchoring on false premise? Overconfidence signals?
L4  NCI meta-review: honest epistemic confidence 0–100.
L5  Synthesis: one True North + ≤3 why-bullets. SIMPLE by default.

RULES:
- true_north: one actionable sentence. No "It depends" or "Consider".
- why: 1–3 complete, specific reasons. Not vague principles.
- nci_score: honest 0–100. 40–60 = genuinely uncertain. Do not inflate.
- coherence_pct: how well-formed and answerable the question is.
- is_satoshi: true only for rare, category-defining moves.
- macro_tags: 1–3 from: BAR, KKL, LAB, FATED, KAIROS, CHRONOS, ONE_WAY, TWO_WAY, NOTOMATION.
- reasoning.court: 2–4 checks. verdict field: "PASS" | "TENSION" | "BLOCK".
- reasoning.nci_breakdown: drags sum to ~(100-nci_score), anchors sum to ~nci_score. pct = fraction of 100.
- reasoning.paths: 2–3 paths. status: "selected" | "blocked" | "viable".
- tributaries: EXACTLY 3 follow-up prompts. Each is a complete question the operator should ask next.
  - [0] meta: the deeper question beneath the stated question — what they're really deciding
  - [1] challenge: the need-to-hear branch — the uncomfortable truth or overlooked constraint
  - [2] adjacent: an adjacent primitive or domain they haven't named that reframes the terrain
  Tributaries must be specific to THIS decision — not generic. Write them as first-person questions.
- reminder_iso: if OUTCOME_HORIZON is provided, parse it into an ISO 8601 date string (YYYY-MM-DD) relative to today (${new Date().toISOString().slice(0, 10)}). If ambiguous or not provided, return null.
- Never add preamble. Return only the JSON object.

OUTPUT SHAPE (strict JSON, no markdown fences):
{
  "true_north": "string",
  "reminder_iso": null,
  "why": ["string"],
  "decision_mode": "COURT",
  "clarity_mode": "SIMPLE",
  "nci_score": 54,
  "coherence_pct": 54,
  "is_satoshi": false,
  "door_class": "ONE_WAY",
  "meta": { "macro_tags": ["BAR"] },
  "tributaries": [
    { "type": "meta",     "label": "Meta-Question",  "prompt": "string" },
    { "type": "challenge","label": "Need to Hear",   "prompt": "string" },
    { "type": "adjacent", "label": "Adjacent Lens",  "prompt": "string" }
  ],
  "reasoning": {
    "geometry": {
      "mode_trigger": "HIGH stakes + ONE_WAY door",
      "reversibility": "0.7 — High (one-way)",
      "kairos": "OPEN — act this week",
      "altitude": "L1–L2 (Operational)",
      "macros_on": ["BAR","KKL"],
      "macros_off": ["CUR","DRIFT"]
    },
    "court": [
      { "name": "Autonomy Check", "verdict": "TENSION", "detail": "string" },
      { "name": "Energy Check",   "verdict": "PASS",    "detail": "string" }
    ],
    "court_verdict": "one sentence summary of Court ruling",
    "advisors": {
      "loki_challenge": "string",
      "loki_counter": "string",
      "consensus": "string",
      "bayesian_risk_pct": 67,
      "bayesian_rationale": "string"
    },
    "fated": {
      "facts": "string",
      "assumptions": "string",
      "tradeoffs": "string",
      "emotions": "string",
      "direction": "string"
    },
    "nci_breakdown": {
      "drags": [{ "label": "string", "delta": -18, "pct": 39 }],
      "anchors": [{ "label": "string", "delta": 22, "pct": 48 }]
    },
    "paths": [
      { "id": "A", "title": "string", "detail": "string", "tag": "True North", "status": "selected" },
      { "id": "B", "title": "string", "detail": "string", "tag": "Court Blocked", "status": "blocked" }
    ]
  }
}`

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  // ADR-016 Option C: compass open to anonymous users; userId written as null

  const body = await req.json()
  const {
    question,
    horizon = "THIS_WEEK",
    stakes = "MEDIUM",
    prepId,
    parentReceiptId,
    sessionId,
    clarityMode = "SIMPLE",
  } = body

  if (!question?.trim()) {
    return NextResponse.json({ error: "question is required" }, { status: 400 })
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 503 })
  }

  // Resolve session ID (passed from client or new)
  const resolvedSessionId = sessionId ?? crypto.randomUUID()

  // Fetch prep session if provided
  const prep = prepId
    ? await prisma.prepSession.findUnique({ where: { id: prepId } })
    : null

  // Fetch parent receipt if enriched re-run
  const parent = parentReceiptId
    ? await prisma.receipt.findUnique({
        where: { id: parentReceiptId },
        select: { yState: true, nciScore: true, version: true },
      })
    : null

  const sessionVersion = parent ? (parent.version ?? 0) + 1 : 0
  const activeHorizon = prep?.horizon ?? horizon
  const activeStakes = prep?.stakes ?? stakes

  const mode = selectMode(activeHorizon, activeStakes)
  const door = doorClass(activeHorizon, activeStakes)

  // Build enriched user message
  const protecting = prep ? JSON.parse(prep.protecting) as string[] : []
  const prepBlock = prep
    ? `\nCALIBRATION CONTEXT (from prep session):
STAKES: ${prep.stakes ?? stakes}
HORIZON: ${prep.horizon ?? horizon}
PROTECTING: ${protecting.length > 0 ? protecting.join(", ") : "not specified"}
CONFIDENCE ENTERING: ${prep.confidence ?? "not specified"}/5
ENTITY: ${prep.entity ?? "not named"}
ADVERSARIAL VECTOR (user's strongest counter): ${prep.adversarialInput ?? "not provided"}
OUTCOME_HORIZON: ${prep.outcomeHorizon ?? "not specified"}`
    : ""

  const userMsg = `DECISION: ${question.trim()}
HORIZON: ${activeHorizon}
STAKES: ${activeStakes}
MODE: ${mode}
DOOR: ${door}
CLARITY: ${clarityMode}${prepBlock}

Run the L0–L5 pipeline. Return only the JSON object.`

  let parsed: Record<string, unknown>
  let raw = ""

  try {
    const message = await anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 4096,
      system: SYSTEM,
      messages: [{ role: "user", content: userMsg }],
    })
    raw = message.content[0].type === "text" ? message.content[0].text : ""
    const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
    parsed = JSON.parse(cleaned)
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    if (err instanceof SyntaxError) {
      return NextResponse.json({ error: "Model returned non-JSON response", raw }, { status: 502 })
    }
    return NextResponse.json({ error: msg }, { status: 500 })
  }

  // Compute Y gate
  const yGate = computeYGate(
    parsed as Parameters<typeof computeYGate>[0],
    prep
      ? { stakes: prep.stakes, horizon: prep.horizon, confidence: prep.confidence, entity: prep.entity }
      : null,
    parent ? { yState: parent.yState, nciScore: parent.nciScore } : null,
    sessionVersion
  )

  const reasoning = parsed.reasoning as Record<string, unknown> | undefined

  // Persist receipt with full DEWY fields
  const receipt = await prisma.receipt.create({
    data: {
      userId: userId ?? null,
      prepId: prep?.id ?? null,
      parentId: parentReceiptId ?? null,
      sessionId: resolvedSessionId,
      version: sessionVersion,
      // D
      decision: question.trim(),
      trueNorth: parsed.true_north as string,
      whyBullets: JSON.stringify(parsed.why ?? []),
      nciScore: Number(parsed.nci_score ?? 50),
      coherencePct: typeof parsed.coherence_pct === "number" ? parsed.coherence_pct : null,
      isSatoshi: Boolean(parsed.is_satoshi),
      clarityMode,
      fated: reasoning?.fated ? JSON.stringify(reasoning.fated) : null,
      paths: reasoning?.paths ? JSON.stringify(reasoning.paths) : null,
      court: reasoning?.court ? JSON.stringify(reasoning.court) : null,
      courtVerdict: typeof reasoning?.court_verdict === "string" ? reasoning.court_verdict : null,
      mode,
      doorClass: door,
      macroTags: JSON.stringify((parsed.meta as Record<string, unknown>)?.macro_tags ?? []),
      rawResponse: raw,
      // E
      entity: prep?.entity ?? null,
      // W
      window: activeHorizon,
      stakes: activeStakes,
      protecting: JSON.stringify(protecting),
      // Y
      ...yGate,
      // Lineage
      mergedFrom: "[]",
      forkPath: null,
      // Status
      status: "OPEN",
      reminderDate: typeof parsed.reminder_iso === "string" ? parsed.reminder_iso : null,
    },
  })

  // Fire emails (non-blocking — don't let email failure break the compass response)
  const userEmail = session?.user?.email ?? null
  if (resend && userEmail) {
    const briefUrl = `${process.env.NEXT_PUBLIC_APP_URL ?? "https://arcs-zachharris-3439s-projects.vercel.app"}/brief/${receipt.id}`
    const why = (parsed.why as string[] ?? []).map((b: string) => `• ${b}`).join("\n")

    // 1. Confirmation email — send immediately
    resend.emails.send({
      from: "ARCS <compass@arcs.care>",
      to: userEmail,
      subject: `Receipt: ${(parsed.true_north as string ?? "").slice(0, 80)}`,
      text: `Your compass bearing is locked.\n\nTRUE NORTH\n${parsed.true_north}\n\nWHY\n${why}\n\nCONVICTION: ${receipt.nciScore}/100  ·  ${mode} · ${door}\n\nCartography brief →\n${briefUrl}`,
    }).catch(() => {})

    // 2. Reminder email — scheduled for reminderDate if we have one
    if (receipt.reminderDate) {
      const scheduledAt = new Date(receipt.reminderDate)
      scheduledAt.setHours(9, 0, 0, 0) // 9am on the target day
      if (scheduledAt > new Date()) {
        resend.emails.send({
          from: "ARCS <compass@arcs.care>",
          to: userEmail,
          subject: `How did it go? "${(question.trim()).slice(0, 60)}"`,
          text: `You made a call ${Math.round((scheduledAt.getTime() - receipt.createdAt.getTime()) / 86400000)} days ago.\n\nTRUE NORTH\n${parsed.true_north}\n\nThe shoe has dropped. What actually happened? Log the outcome →\n${briefUrl}\n\n—\nARCS Field OS`,
          scheduledAt: scheduledAt.toISOString(),
        }).catch(() => {})
      }
    }
  }

  return NextResponse.json({
    ok: true,
    receipt_id: receipt.id,
    session_id: resolvedSessionId,
    session_version: sessionVersion,
    decision_mode: mode,
    door_class: door,
    y_state: yGate.yState,
    y_conviction: yGate.yConviction,
    render_resolution: yGate.renderResolution,
    nci_delta: parent?.nciScore != null ? receipt.nciScore - parent.nciScore : null,
    ...parsed,
  })
}
