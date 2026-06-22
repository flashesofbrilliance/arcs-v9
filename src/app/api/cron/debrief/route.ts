import { Resend } from "resend"
import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { APP_URL } from "@/lib/env"
import { debriefEmail } from "@/emails/debriefEmail"

// ADR-026 Bug 2 — long-horizon scheduler. Resend's scheduledAt rejects any
// send >30 days out, so a receipt with a far reminderDate can't be scheduled
// at compass-creation time (see the daysOut guard in api/compass/route.ts).
// This cron sweeps daily for receipts that have now entered the 30-day
// window and queues their debrief send, so they don't sit permanently
// unscheduled. debriefSentAt is the dedupe marker shared with the
// compass-time send path — set once, checked by both, never double-sent.
export const dynamic = "force-dynamic"
export const maxDuration = 60

const resend = process.env.AUTH_RESEND_KEY ? new Resend(process.env.AUTH_RESEND_KEY) : null
const RESEND_MAX_SCHEDULE_DAYS = 30

export async function GET(req: NextRequest) {
  // Vercel sets CRON_SECRET automatically when a vercel.json cron is
  // configured and the project has the var set; verify it if present so this
  // route isn't a public trigger for arbitrary debrief sends. Unset in dev.
  if (process.env.CRON_SECRET) {
    const auth = req.headers.get("authorization")
    if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
      return NextResponse.json({ error: "unauthorized" }, { status: 401 })
    }
  }

  if (!resend) {
    return NextResponse.json({ error: "AUTH_RESEND_KEY not configured" }, { status: 503 })
  }

  const windowEnd = new Date(Date.now() + RESEND_MAX_SCHEDULE_DAYS * 86400000)
  const windowEndStr = windowEnd.toISOString().slice(0, 10)

  // Candidates: never sent, has a reminderDate now inside the 30-day Resend
  // window, no Outcome logged yet, and a real user/email to send to.
  // (Anonymous receipts have no userId and can't be debriefed by email.)
  const candidates = await prisma.receipt.findMany({
    where: {
      debriefSentAt: null,
      reminderDate: { not: null, lte: windowEndStr },
      outcome: null,
      userId: { not: null },
    },
    include: { user: { select: { email: true } } },
  })

  const results: { receiptId: string; ok: boolean; detail: string }[] = []

  for (const receipt of candidates) {
    const userEmail = receipt.user?.email
    if (!userEmail || !receipt.reminderDate) {
      results.push({ receiptId: receipt.id, ok: false, detail: "missing email or reminderDate" })
      continue
    }

    const scheduledAt = new Date(receipt.reminderDate)
    scheduledAt.setUTCHours(14, 0, 0, 0)
    // If the reminder date has already passed by the time the cron catches
    // it, send immediately rather than scheduling in the past (Resend
    // rejects past scheduledAt values).
    const sendAt = scheduledAt > new Date() ? scheduledAt.toISOString() : undefined

    let why: string[] = []
    try {
      why = JSON.parse(receipt.whyBullets) as string[]
    } catch {
      why = []
    }
    let protecting: string[] = []
    try {
      protecting = JSON.parse(receipt.protecting) as string[]
    } catch {
      protecting = []
    }

    const debrief = debriefEmail({
      question: receipt.decision,
      trueNorth: receipt.trueNorth,
      daysElapsed: (scheduledAt.getTime() - receipt.createdAt.getTime()) / 86400000,
      conviction: receipt.nciScore,
      protecting,
      debriefUrl: `${APP_URL}/debrief/${receipt.id}`,
      token: receipt.id,
    })

    try {
      const res = await resend.emails.send({
        from: "ARCS <noreply@arcs.care>",
        to: userEmail,
        subject: debrief.subject,
        text: debrief.text,
        html: debrief.html,
        ...(sendAt ? { scheduledAt: sendAt } : {}),
      })
      await prisma.receipt.update({
        where: { id: receipt.id },
        data: { debriefSentAt: new Date() },
      })
      results.push({ receiptId: receipt.id, ok: true, detail: res.data?.id ?? "sent" })
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      console.error(`[CRON DEBRIEF] receipt ${receipt.id} failed:`, msg)
      results.push({ receiptId: receipt.id, ok: false, detail: msg })
    }
  }

  console.log(`[CRON DEBRIEF] swept ${candidates.length} candidates, ${results.filter((r) => r.ok).length} sent/scheduled`)

  return NextResponse.json({ ok: true, swept: candidates.length, results })
}
