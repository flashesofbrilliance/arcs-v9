import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

// Ripe-to-close selection — the capture-RATE lever (P1 keel).
//
// The outcome-capture MECHANISM already ships end to end (POST/GET
// /api/receipts/[id]/outcome · debriefEmail · cron/debrief · DebriefCard on
// /brief/[id] · reminders opt-in). What was missing is a PULL: nothing surfaces
// to a returning user the receipts most likely to have landed. Capture is
// behaviorally hard because people forget the fitting (real-user-def §8); this
// route feeds a low-friction, in-app nudge that fights the forgetting without
// depending on email deliverability (the current path reaches ~0 opted-in).
//
// NOTOMATION: this surfaces CANDIDATES only — receipts whose window has
// plausibly passed. It never asserts an outcome. The human supplies
// matched/regretScore at /debrief/[id]; a receipt cannot close itself (§5.1).
// No derivation plane is touched here — a read over the caller's own rows.

// Short-horizon windows only: a decision on a years-out horizon has not landed
// yet, so nudging to close it would be dishonest. (window is NOT NULL in schema;
// horizon can be null, so gate on window.)
const SHORT_WINDOWS = new Set(["TODAY", "THIS_WEEK", "THIS_QUARTER"])

// Days after creation before a window is "plausibly past" — the honest floor
// used only when no explicit reminderDate is set. Deliberately conservative:
// we would rather under-nudge than nudge a decision that has not resolved.
const PAST_FLOOR_DAYS: Record<string, number> = {
  TODAY: 2,
  THIS_WEEK: 10,
  THIS_QUARTER: 100,
}

const MAX_RIPE = 3

export async function GET() {
  const session = await auth()
  const userId = session?.user?.id ?? null
  // Auth-gated: ripe receipts are the caller's own to close. No session, nothing
  // to nudge (anonymous receipts have no owner and no email loop).
  if (!userId) return NextResponse.json({ ripe: [] })

  const now = Date.now()
  const todayStr = new Date(now).toISOString().slice(0, 10)

  // Candidate pool: the caller's own OPEN seed receipts with no outcome yet, on a
  // short window. Small (one user's own), so the past-window proxy is applied in
  // JS below rather than encoded as a per-window SQL OR.
  const candidates = await prisma.receipt.findMany({
    where: {
      userId,
      status: "OPEN",
      parentId: null,
      outcome: null,
      window: { in: [...SHORT_WINDOWS] },
    },
    orderBy: { createdAt: "asc" }, // oldest ripe first — most likely to have landed
    select: {
      id: true,
      decision: true,
      trueNorth: true,
      nciScore: true,
      window: true,
      reminderDate: true,
      createdAt: true,
    },
    take: 50,
  })

  const ripe = candidates
    .filter((r) => {
      // Explicit reminderDate wins: past its date → ripe.
      if (r.reminderDate) return r.reminderDate <= todayStr
      // Else fall back to the conservative per-window floor.
      const floor = PAST_FLOOR_DAYS[r.window] ?? 100
      const ageDays = (now - r.createdAt.getTime()) / 86400000
      return ageDays >= floor
    })
    .slice(0, MAX_RIPE)
    .map((r) => ({
      id: r.id,
      question: r.decision,
      trueNorth: r.trueNorth,
      nci: r.nciScore,
      createdAt: r.createdAt,
    }))

  return NextResponse.json({ ripe })
}
