import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

// Outcome / debrief surface — closes the receipt loop (Book II Part V §5.6).
// GET  → the original bearing + any outcome already logged.
// POST → write the Outcome, flip the receipt to LOGGED, set the drift read.
//
// A receipt cannot be closed by the session that created it (§5.1). External
// signal has to arrive after T₀. In practice the debrief email fires N days
// later, so v1 does not hard-enforce a session check; ownership is the gate.

const isProd = process.env.NODE_ENV === "production"

function clampRegret(v: unknown): number | null {
  const n = typeof v === "number" ? v : Number(v)
  if (!Number.isFinite(n)) return null
  return Math.max(0, Math.min(10, Math.round(n)))
}

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const { receiptId } = await params
  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    select: {
      id: true,
      decision: true,
      trueNorth: true,
      nciScore: true,
      mode: true,
      doorClass: true,
      protecting: true,
      createdAt: true,
      reminderDate: true,
      status: true,
      driftState: true,
      outcome: {
        select: { what: true, matched: true, regretScore: true, learning: true, loggedAt: true },
      },
    },
  })
  if (!receipt) return NextResponse.json({ error: "Receipt not found" }, { status: 404 })

  let protecting: string[] = []
  try { protecting = JSON.parse(receipt.protecting) as string[] } catch { protecting = [] }

  return NextResponse.json({
    ok: true,
    receipt: {
      id: receipt.id,
      question: receipt.decision,
      trueNorth: receipt.trueNorth,
      nci: receipt.nciScore,
      mode: receipt.mode,
      door: receipt.doorClass,
      protecting,
      createdAt: receipt.createdAt,
      status: receipt.status,
      driftState: receipt.driftState,
    },
    outcome: receipt.outcome,
  })
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const { receiptId } = await params

  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    select: { id: true, userId: true },
  })
  if (!receipt) return NextResponse.json({ error: "Receipt not found" }, { status: 404 })

  // Ownership gate (ADR-001, app layer). Owned receipts may only be debriefed
  // by their owner in prod. Anonymous receipts stay open to the link holder.
  if (isProd && receipt.userId && receipt.userId !== userId) {
    return NextResponse.json({ error: "Not your receipt to close" }, { status: 403 })
  }

  const body = await req.json().catch(() => ({}))
  const what = typeof body.what === "string" ? body.what.trim() : ""
  const matched = body.matched
  const regretScore = clampRegret(body.regretScore)
  const learning = typeof body.learning === "string" && body.learning.trim() ? body.learning.trim() : null

  if (!what) return NextResponse.json({ error: "what actually happened is required" }, { status: 400 })
  if (what.length > 2000) return NextResponse.json({ error: "what is too long" }, { status: 400 })
  if (typeof matched !== "boolean") return NextResponse.json({ error: "matched (boolean) is required" }, { status: 400 })
  if (regretScore == null) return NextResponse.json({ error: "regretScore is required" }, { status: 400 })
  if (learning && learning.length > 2000) return NextResponse.json({ error: "learning is too long" }, { status: 400 })

  // Drift read: did reality land where the compass pointed?
  const driftState = matched ? "LANDED" : "DRIFTING"

  const outcome = await prisma.outcome.upsert({
    where: { receiptId },
    create: { receiptId, what, matched, regretScore, learning },
    update: { what, matched, regretScore, learning, loggedAt: new Date() },
  })
  await prisma.receipt.update({
    where: { id: receiptId },
    data: { status: "LOGGED", driftState },
  })

  // The loop closes here — emit the signal at the one server chokepoint every
  // close flows through (the "measure expected vs actual" arm producing telemetry,
  // not just DB state). Server-log convention matches compass's "[COMPASS] …";
  // greppable in Vercel logs + corpus analytics. Client fires the va() twin.
  console.log(
    `[OUTCOME] receipt_outcome_matched receipt=${receiptId} matched=${matched} drift=${driftState} regret=${regretScore} learning=${learning ? "y" : "n"} owner=${receipt.userId ? "user" : "anon"}`,
  )

  return NextResponse.json({ ok: true, outcome, driftState })
}
