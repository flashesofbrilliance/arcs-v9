import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { computeYGate } from "@/lib/ygate"

export const dynamic = "force-dynamic"

// Phase 2 of the trust-contract conformance work (ADR-032): opt-in save for
// anonymous (ephemeral) bearings. Anonymous runs persist NOTHING server-side —
// the full compass response lives only in the visitor's browser. If they choose
// to keep it, they sign in and this endpoint persists the bearing they already
// have. The write happens strictly post-auth, so /privacy's "no auth = no
// write path" holds to the letter.
//
// Provenance: the payload is client-attested — it was minted by /api/compass,
// but the server can't re-verify that without re-running the pipeline, which
// would change the bearing the user chose to keep. Rows are therefore marked
// surface: "EPHEMERAL_SAVE" so corpus analytics can segment them (ADR-023
// baseline work should note the slice). Y-gate fields are recomputed
// server-side from the payload — never trusted from the client.

const MODES = new Set(["QUICKMOVE", "PLAN", "COURT"])
const DOORS = new Set(["ONE_WAY", "TWO_WAY"])
const WINDOWS = new Set(["TODAY", "THIS_WEEK", "THIS_QUARTER", "ONE_TO_THREE_YEARS"])

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const body = await req.json()
  const b = body?.bearing
  if (!b || typeof b !== "object") {
    return NextResponse.json({ error: "bearing is required" }, { status: 400 })
  }

  const question = typeof b.question === "string" ? b.question.trim() : ""
  const trueNorth = typeof b.true_north === "string" ? b.true_north.trim() : ""
  if (!question || !trueNorth) {
    return NextResponse.json({ error: "bearing is missing question/true_north" }, { status: 400 })
  }

  const prepIn = b.prep && typeof b.prep === "object" ? b.prep as Record<string, unknown> : null
  const prepCtx = prepIn
    ? {
        stakes: typeof prepIn.stakes === "string" ? prepIn.stakes : null,
        horizon: typeof prepIn.horizon === "string" ? prepIn.horizon : null,
        confidence: typeof prepIn.confidence === "number" ? prepIn.confidence : null,
        entity: typeof prepIn.entity === "string" ? prepIn.entity : null,
      }
    : null

  // Server-recomputed gate state — same function the compass route uses.
  const yGate = computeYGate(b as Parameters<typeof computeYGate>[0], prepCtx, null, 0)

  const reasoning = b.reasoning && typeof b.reasoning === "object" ? b.reasoning as Record<string, unknown> : undefined
  const nci = Math.max(0, Math.min(100, Math.round(Number(b.nci_score)) || 50))
  const protecting = Array.isArray(prepIn?.protecting)
    ? (prepIn.protecting as unknown[]).filter((p): p is string => typeof p === "string")
    : []

  const receipt = await prisma.receipt.create({
    data: {
      userId,
      surface: "EPHEMERAL_SAVE",
      sessionId: typeof b.session_id === "string" && b.session_id ? b.session_id : crypto.randomUUID(),
      version: 0,
      decision: question,
      trueNorth,
      whyBullets: JSON.stringify(Array.isArray(b.why) ? b.why : []),
      nciScore: nci,
      coherencePct: typeof b.coherence_pct === "number" ? b.coherence_pct : null,
      isSatoshi: Boolean(b.is_satoshi),
      clarityMode: typeof b.clarity_mode === "string" ? b.clarity_mode : "SIMPLE",
      fated: reasoning?.fated ? JSON.stringify(reasoning.fated) : null,
      paths: reasoning?.paths ? JSON.stringify(reasoning.paths) : null,
      court: reasoning?.court ? JSON.stringify(reasoning.court) : null,
      courtVerdict: typeof reasoning?.court_verdict === "string" ? reasoning.court_verdict : null,
      mode: MODES.has(String(b.decision_mode)) ? String(b.decision_mode) : "PLAN",
      doorClass: DOORS.has(String(b.door_class)) ? String(b.door_class) : "TWO_WAY",
      macroTags: JSON.stringify((b.meta as Record<string, unknown> | undefined)?.macro_tags ?? []),
      atgTributaries: Array.isArray(b.tributaries) ? JSON.stringify(b.tributaries) : null,
      // For pipeline-minted receipts rawResponse is Claude's raw text; here it
      // is the attested payload as received — distinguishable via `surface`.
      rawResponse: JSON.stringify(b),
      entity: prepCtx?.entity ?? null,
      window: WINDOWS.has(String(b.horizon)) ? String(b.horizon) : "THIS_WEEK",
      stakes: typeof b.stakes === "string" ? b.stakes : null,
      protecting: JSON.stringify(protecting),
      ...yGate,
      mergedFrom: "[]",
      forkPath: null,
      status: "OPEN",
      // Enter the debrief pipeline like any other receipt (T+7 default).
      reminderDate: new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10),
    },
  })

  return NextResponse.json({ ok: true, receipt_id: receipt.id })
}
