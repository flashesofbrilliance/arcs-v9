import Anthropic from "@anthropic-ai/sdk"
import { Resend } from "resend"
import { NextRequest, NextResponse } from "next/server"
import { unstable_cache } from "next/cache"
import { prisma } from "@/lib/db"
import { computeYGate } from "@/lib/ygate"
import { auth } from "@/lib/auth"
import { APP_URL } from "@/lib/env"
import { debriefEmail } from "@/emails/debriefEmail"
import { receiptEmail } from "@/emails/receiptEmail"

const resend = process.env.AUTH_RESEND_KEY ? new Resend(process.env.AUTH_RESEND_KEY) : null

export const dynamic = "force-dynamic"
// The L0–L5 pipeline emits a large structured JSON object (up to max_tokens),
// which can take 20–40s on Sonnet. Without this, Vercel kills the function at
// the default timeout and drops the connection — the browser then reports the
// fetch as "Load failed" (COMPASS OFFLINE · L0 SIGNAL LOST). 60s is the Hobby
// ceiling and safe across plans.
export const maxDuration = 60

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

function selectMode(horizon: string, stakes: string): "QUICKMOVE" | "PLAN" | "COURT" {
  if (stakes === "HIGH") return "COURT"
  if (horizon === "THIS_QUARTER" || horizon === "ONE_TO_THREE_YEARS") return "COURT"
  if (horizon === "TODAY" && stakes === "LOW") return "QUICKMOVE"
  return "PLAN"
}

function safeParseArray(v: string): string[] {
  try {
    const a = JSON.parse(v)
    return Array.isArray(a) ? a.filter((x): x is string => typeof x === "string") : []
  } catch {
    return []
  }
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
- nci_score: honest 0–100. 40–60 = genuinely uncertain. Do not inflate. This composite is authoritative.
- nci_by_lens: decompose nci_score into 5 lenses, each 0–20 — clarity (is the question well-formed/atomic?), conviction (how strong/directional is the signal?), coherence (do the stated reasons cohere?), consequence (are downstream effects understood?), cadence (is the timing right — not too early/late?). They should track nci_score (their sum ≈ nci_score) and expose WHICH lens is weakest. Do not force an exact arithmetic sum at the cost of an honest per-lens read.
- nci_grade: one short human-readable grade naming the weak lens, e.g. "B+ — Conviction is the weak lens."
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
- nci_self_grade: REQUIRED self-assessment, four boolean checks. Be honest — a false here is more useful than a false "true". Never fabricate a source, stat, or urgency signal to make a check pass.
  - factual: are the claims in true_north/why/fated.facts verifiable from what the user actually provided (the question + prep context), not invented?
  - sources: if you reference any external fact, stat, or precedent not given by the user, is it something you actually know with confidence — not a plausible-sounding fabrication? If you made no external claims, this is true by default.
  - honesty: did you state uncertainty explicitly where it exists, rather than projecting false confidence?
  - action: does true_north give one concrete next step, not a hedge?
  - notes: if ANY of the above is false, explain which claim/section is unsupported. Otherwise "".
- Never add preamble. Return only the JSON object.

OUTPUT SHAPE (strict JSON, no markdown fences):
{
  "true_north": "string",
  "reminder_iso": null,
  "why": ["string"],
  "decision_mode": "COURT",
  "clarity_mode": "SIMPLE",
  "nci_score": 54,
  "nci_by_lens": { "clarity": 12, "conviction": 9, "coherence": 11, "consequence": 12, "cadence": 10 },
  "nci_grade": "B — Conviction is the weak lens.",
  "coherence_pct": 54,
  "is_satoshi": false,
  "door_class": "ONE_WAY",
  "nci_self_grade": { "factual": true, "sources": true, "honesty": true, "action": true, "notes": "" },
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
  const t0 = Date.now()
  const session = await auth()
  const userId = session?.user?.id ?? null
  // ADR-016 Option C: compass open to anonymous users; userId written as null

  const body = await req.json()
  const {
    question,
    horizon = "THIS_WEEK",
    stakes = "MEDIUM",
    prepId,
    prep: inlinePrepBody,
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

  // Fetch prep session if provided (signed-in flow persists prep rows)
  const prepRow = prepId
    ? await prisma.prepSession.findUnique({ where: { id: prepId } })
    : null

  // Unified prep context. Anonymous clients pass prep inline in the request
  // body instead of a prepId — trust-contract conformance (/trust §1,
  // /privacy "no auth = no write path"): anonymous prep is never written to
  // the DB (see /api/prep), so it arrives here as plain request data.
  const inlinePrep = !prepRow && inlinePrepBody && typeof inlinePrepBody === "object"
    ? inlinePrepBody as Record<string, unknown>
    : null
  const prep = prepRow
    ? { ...prepRow, protecting: safeParseArray(prepRow.protecting) }
    : inlinePrep
      ? {
          stakes: typeof inlinePrep.stakes === "string" ? inlinePrep.stakes : null,
          horizon: typeof inlinePrep.horizon === "string" ? inlinePrep.horizon : null,
          protecting: Array.isArray(inlinePrep.protecting)
            ? inlinePrep.protecting.filter((p): p is string => typeof p === "string").slice(0, 4)
            : [],
          confidence: typeof inlinePrep.confidence === "number" ? inlinePrep.confidence : null,
          entity: typeof inlinePrep.entity === "string" ? inlinePrep.entity.trim() || null : null,
          adversarialInput: typeof inlinePrep.adversarialInput === "string" ? inlinePrep.adversarialInput.trim() || null : null,
          outcomeHorizon: typeof inlinePrep.outcomeHorizon === "string" ? inlinePrep.outcomeHorizon.trim() || null : null,
        }
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

  // SAGE pre-screen: advisory-only operator signal (NCI/court/axioms) from the
  // Python pipeline. Never blocks the route — if SAGE_URL is unset or the
  // service is down, we log and proceed with Claude alone. NOTOMATION: this
  // enriches Claude's context; it never decides or persists on its own.
  //
  // sageTraceData below feeds an invisible SageTrace row (written after the
  // receipt is created) — never returned to the client, never `include`d by
  // any client-facing route. Exists only for the with/without-SAGE efficacy
  // study once enough paired Outcomes accumulate (see scripts/sage_efficacy.py).
  let sageBlock = ""
  let sageTraceData: { fired: boolean; signal: string | null; failureReason: string | null; latencyMs: number | null } = {
    fired: false,
    signal: null,
    failureReason: process.env.SAGE_URL ? null : "SAGE_URL unset",
    latencyMs: null,
  }
  if (process.env.SAGE_URL) {
    const sageT0 = Date.now()
    try {
      const sageRes = await fetch(`${process.env.SAGE_URL}/api/sage-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), horizon: activeHorizon, stakes: activeStakes }),
        signal: AbortSignal.timeout(3000),
      })
      sageTraceData.latencyMs = Date.now() - sageT0
      if (sageRes.ok) {
        const sage = await sageRes.json()
        sageBlock = `\nOPERATOR SIGNAL (SAGE pipeline — advisory, not authoritative):
NCI: ${sage.nci_score} | VERDICT: ${sage.verdict} | COURT: ${sage.court_verdict ?? "n/a"}
SIGNAL CLASS: ${sage.signal_classification} | SATOSHI: ${sage.is_satoshi}`
        sageTraceData.fired = true
        sageTraceData.signal = JSON.stringify(sage)
      } else {
        console.error("[SAGE] non-200 response:", sageRes.status)
        sageTraceData.failureReason = `non-200:${sageRes.status}`
      }
    } catch (err) {
      sageTraceData.latencyMs = Date.now() - sageT0
      const msg = err instanceof Error ? err.message : String(err)
      console.error("[SAGE] unreachable, proceeding without operator signal:", msg)
      sageTraceData.failureReason = `unreachable:${msg}`
    }
  }

  // Build enriched user message
  const protecting = prep?.protecting ?? []
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
CLARITY: ${clarityMode}${prepBlock}${sageBlock}

Run the L0–L5 pipeline. Return only the JSON object.`

  // Model routing: COURT needs Sonnet's adversarial depth; QUICKMOVE/PLAN use Haiku (~5x faster)
  // min viable JSON for this schema is ~1800 tokens; give each mode headroom above that
  const MODEL_MAP = {
    QUICKMOVE: { model: "claude-haiku-4-5-20251001", max_tokens: 2048, temperature: 0 },
    PLAN:      { model: "claude-haiku-4-5-20251001", max_tokens: 3072, temperature: 0.3 },
    COURT:     { model: "claude-sonnet-4-6",          max_tokens: 4096, temperature: 0.5 },
  } as const
  const modelConfig = MODEL_MAP[mode]

  const t1 = Date.now()
  let t2 = t1
  let parsed: Record<string, unknown>
  let raw = ""

  // Prompt caching: SYSTEM prefix cached server-side — 90% cost reduction after first request.
  // unstable_cache: deduplicates identical questions within a 1-hour window.
  // COURT not cached (temp=0.5, adversarial variation intentional).
  const callClaude = (betas: string[]) => anthropic.beta.messages.create({
    model: modelConfig.model,
    max_tokens: modelConfig.max_tokens,
    temperature: modelConfig.temperature,
    betas,
    system: [{ type: "text" as const, text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages: [{ role: "user", content: userMsg }],
  })

  const runInference = mode === "COURT"
    ? () => callClaude(["prompt-caching-2024-07-31"])
    : unstable_cache(
        () => callClaude(["prompt-caching-2024-07-31"]),
        [modelConfig.model, String(modelConfig.max_tokens), mode, activeHorizon, activeStakes, clarityMode, question.trim().toLowerCase()],
        { revalidate: 3600 }
      )

  try {
    const message = await runInference()
    t2 = Date.now()

    if (!message.content || message.content.length === 0) {
      return NextResponse.json({ error: "Claude returned empty response", raw }, { status: 502 })
    }

    raw = message.content[0].type === "text" ? message.content[0].text : ""

    if (!raw || raw.trim().length === 0) {
      return NextResponse.json({ error: "Claude returned empty text content", raw }, { status: 502 })
    }

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

  // Persist receipt with full DEWY fields — SIGNED-IN ONLY. Trust-contract
  // conformance (/trust §1 "anonymous sessions: nothing is stored", /privacy
  // "no auth = no write path"): anonymous runs are never written to the DB.
  // The client renders them ephemerally from this response (sessionStorage,
  // `eph_` receipt ids) and they cease to exist when the tab closes.
  let receipt: Awaited<ReturnType<typeof prisma.receipt.create>> | null = null
  if (userId) {
  try {
    const receiptData = {
      userId: userId ?? null,
      prepId: prepRow?.id ?? null,
      parentId: parentReceiptId ?? null,
      sessionId: resolvedSessionId,
      version: sessionVersion,
      // D
      decision: question.trim(),
      trueNorth: parsed.true_north as string,
      whyBullets: JSON.stringify(parsed.why ?? []),
      nciScore: Number(parsed.nci_score ?? 50),
      nciByLens: parsed.nci_by_lens ? JSON.stringify(parsed.nci_by_lens) : null,
      nciGrade: typeof parsed.nci_grade === "string" ? parsed.nci_grade : null,
      coherencePct: typeof parsed.coherence_pct === "number" ? parsed.coherence_pct : null,
      isSatoshi: Boolean(parsed.is_satoshi),
      clarityMode,
      fated: reasoning?.fated ? JSON.stringify(reasoning.fated) : null,
      paths: reasoning?.paths ? JSON.stringify(reasoning.paths) : null,
      court: reasoning?.court ? JSON.stringify(reasoning.court) : null,
      courtVerdict: typeof reasoning?.court_verdict === "string" ? reasoning.court_verdict : null,
      nciSelfGrade: parsed.nci_self_grade ? JSON.stringify(parsed.nci_self_grade) : null,
      mode,
      doorClass: door,
      macroTags: JSON.stringify((parsed.meta as Record<string, unknown>)?.macro_tags ?? []),
      atgTributaries: parsed.tributaries ? JSON.stringify(parsed.tributaries) : null,
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
      // ADR-026 Bug 1: without a PrepSession outcomeHorizon, parsed.reminder_iso
      // is always null and the receipt is permanently ineligible for the debrief
      // email. Default to T+7 so every receipt enters the delivery pipeline.
      reminderDate: typeof parsed.reminder_iso === "string"
        ? parsed.reminder_iso
        : new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10),
    }

    // Check for undefined values before creating receipt
    const undefinedFields = Object.entries(receiptData)
      .filter(([_, v]) => v === undefined)
      .map(([k]) => k)
    if (undefinedFields.length > 0) {
      console.error("[COMPASS DATA CHECK] Undefined fields:", undefinedFields)
    }

    receipt = await prisma.receipt.create({ data: receiptData })

    // Invisible trace write — never blocks or affects the response. See the
    // sageTraceData comment above for why this is a separate, never-`include`d
    // table. Signed-in only: the trace embeds signal derived from user input,
    // so it falls under the same no-anonymous-write rule as the receipt.
    prisma.sageTrace.create({
      data: { receiptId: receipt.id, ...sageTraceData },
    }).catch((err) => console.error("[SAGE TRACE] failed to write:", err instanceof Error ? err.message : String(err)))
  } catch (err) {
    console.error("[COMPASS ERROR] Failed to create receipt:", err instanceof Error ? err.message : String(err))
    throw err
  }
  } else {
    if (process.env.NODE_ENV !== "production") {
      console.log("[COMPASS] anonymous run — nothing persisted (trust contract: no auth = no write path)")
    }
  }
  const t3 = Date.now()

  if (process.env.NODE_ENV !== "production") {
    console.log(`[COMPASS PROFILE] Setup: ${t1-t0}ms | Claude: ${t2-t1}ms | Prisma: ${t3-t2}ms | Total: ${t3-t0}ms`)
  }

  // Fire emails (non-blocking — don't let email failure break the compass
  // response). Requires a persisted receipt — anonymous runs have none.
  const userEmail = session?.user?.email ?? null
  if (resend && userEmail && receipt) {
    // Stable alias for use inside async callbacks below — `receipt` is a
    // `let`, so TS narrowing doesn't survive into closures.
    const rid = receipt.id
    const briefUrl = `${APP_URL}/brief/${rid}`

    // 1. Receipt confirmation email — the T₀ "bearing locked" artifact.
    const receiptMail = receiptEmail({
      question: question.trim(),
      trueNorth: parsed.true_north as string ?? "",
      why: (parsed.why as string[]) ?? [],
      nci: receipt.nciScore,
      mode,
      door,
      briefUrl,
      token: receipt.id,
    })
    resend.emails.send({
      from: "ARCS <noreply@arcs.care>",
      to: userEmail,
      subject: receiptMail.subject,
      text: receiptMail.text,
      html: receiptMail.html,
    }).catch((err) => console.error("[EMAIL] receipt confirmation failed:", err instanceof Error ? err.message : String(err)))

    // 2. Debrief (calibration) email — the §5.6 close-the-loop touchpoint,
    //    scheduled for reminderDate. Reflects the original bearing back and
    //    routes to logging the outcome. A receipt can't close itself.
    if (receipt.reminderDate) {
      const scheduledAt = new Date(receipt.reminderDate)
      // setHours() uses the SERVER's local timezone, not the user's — Vercel
      // functions run in UTC, so this was computing 9am UTC = 5am Eastern,
      // blasting users at 5am instead of the intended morning hour. No
      // per-user timezone is stored yet, so this is a fixed approximation
      // (14:00 UTC ≈ 9-10am US Eastern depending on DST), not a real fix —
      // revisit properly once timezone is captured at signup/prep.
      scheduledAt.setUTCHours(14, 0, 0, 0)
      // Resend's scheduledAt supports a maximum of 30 days out. Beyond that,
      // the send call fails outright — silently, if not logged. Found via a
      // real audit: 14 of 74 eligible receipts had reminderDate >30 days out,
      // every one of which would have failed this way with zero visibility.
      // No cron-based long-horizon scheduler exists yet (see arcs-session-state.md);
      // for now just make the gap loud instead of silent.
      const RESEND_MAX_SCHEDULE_DAYS = 30
      const daysOut = (scheduledAt.getTime() - Date.now()) / 86400000
      // Progressive disclosure: the first debrief a user ever gets is sent
      // unconditionally (the close-the-loop promise). Every later one needs
      // debriefOptIn — set via the link in that first email — so receipt
      // volume doesn't translate 1:1 into unrequested email volume.
      const debriefUser = userId ? await prisma.user.findUnique({
        where: { id: userId },
        select: { firstDebriefSentAt: true, debriefOptIn: true },
      }) : null
      const isFirstDebrief = !!debriefUser && debriefUser.firstDebriefSentAt === null
      const eligible = isFirstDebrief || debriefUser?.debriefOptIn === true

      if (daysOut > RESEND_MAX_SCHEDULE_DAYS) {
        console.error(`[EMAIL] debrief for receipt ${receipt.id} is ${Math.round(daysOut)} days out — exceeds Resend's ${RESEND_MAX_SCHEDULE_DAYS}-day scheduling limit, not attempting (would fail silently otherwise)`)
      } else if (!eligible) {
        if (process.env.NODE_ENV !== "production") {
          console.log(`[EMAIL] debrief for receipt ${receipt.id} skipped — user has not opted in to repeat reminders`)
        }
      } else if (scheduledAt > new Date()) {
        const debrief = debriefEmail({
          question: question.trim(),
          trueNorth: parsed.true_north as string ?? "",
          daysElapsed: (scheduledAt.getTime() - receipt.createdAt.getTime()) / 86400000,
          conviction: receipt.nciScore,
          protecting,
          debriefUrl: `${APP_URL}/debrief/${receipt.id}`,
          token: receipt.id,
          isFirstDebrief,
          optInUrl: isFirstDebrief && userId ? `${APP_URL}/api/account/reminders?action=opt-in&uid=${userId}` : undefined,
          optOutUrl: !isFirstDebrief && userId ? `${APP_URL}/api/account/reminders?action=opt-out&uid=${userId}` : undefined,
        })
        resend.emails.send({
          from: "ARCS <noreply@arcs.care>",
          to: userEmail,
          subject: debrief.subject,
          text: debrief.text,
          html: debrief.html,
          scheduledAt: scheduledAt.toISOString(),
        }).then(async (res) => {
          // Log the Resend email id so a scheduled send can actually be
          // cancelled later if needed — the prior version discarded this,
          // which is why a bad-timezone batch couldn't be cancelled and had
          // to be left to fire.
          if (process.env.NODE_ENV !== "production") {
            console.log(`[EMAIL] debrief for receipt ${rid} scheduled, resend id: ${res.data?.id ?? "unknown"}`)
          }
          // Mark sent so the long-horizon cron (ADR-026 Bug 2) doesn't pick
          // this receipt up again once its reminderDate enters its own sweep window.
          await prisma.receipt.update({ where: { id: rid }, data: { debriefSentAt: new Date() } })
          if (isFirstDebrief && userId) {
            await prisma.user.update({ where: { id: userId }, data: { firstDebriefSentAt: new Date() } })
          }
        }).catch((err) => console.error(`[EMAIL] debrief for receipt ${rid} failed:`, err instanceof Error ? err.message : String(err)))
      }
    }
  }

  const response = NextResponse.json({
    ...parsed,
    // Deterministic fields win — Claude's own JSON echoes decision_mode and
    // door_class per the OUTPUT SHAPE schema, but those are advisory text,
    // not authoritative. The route's selectMode()/doorClass() output is what
    // was actually used for routing, Y-gate computation, and persistence —
    // these must always override whatever Claude echoed back.
    ok: true,
    // null for anonymous runs — nothing was persisted (trust contract).
    // The client renders the result ephemerally and mints an `eph_` id.
    receipt_id: receipt?.id ?? null,
    persisted: !!receipt,
    session_id: resolvedSessionId,
    session_version: sessionVersion,
    decision_mode: mode,
    door_class: door,
    y_state: yGate.yState,
    y_conviction: yGate.yConviction,
    render_resolution: yGate.renderResolution,
    nci_delta: parent?.nciScore != null && receipt ? receipt.nciScore - parent.nciScore : null,
  })

  // NOTE (2026-07-13, trust-contract conformance): the anonymous
  // `arcs_session_id` claim cookie is no longer set here — with no anonymous
  // persistence there is nothing to claim. ClaimAnonymousReceipts.tsx stays
  // in place (harmless no-op for new sessions) until Phase 2's opt-in save
  // flow decides its future.

  return response
}
