import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"

export const dynamic = "force-dynamic"

// Advisory funnel capture. Stores a Lead and fires a best-effort confirmation
// email (Resend REST — no new dependency). source: "waitlist" | "advisory".
const BOOKING_URL = process.env.NEXT_PUBLIC_CONSULT_BOOKING_URL ?? ""
const FROM = process.env.EMAIL_FROM ?? "ARCS <noreply@arcs.care>"

function isEmail(s: unknown): s is string {
  return typeof s === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.trim())
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}))
  const { email, name, message, source, receiptId } = body ?? {}

  if (!isEmail(email)) {
    return NextResponse.json({ error: "A valid email is required" }, { status: 400 })
  }
  const src = source === "advisory" ? "advisory" : "waitlist"

  await prisma.lead.create({
    data: {
      email: email.trim(),
      name: typeof name === "string" && name.trim() ? name.trim() : null,
      message: typeof message === "string" && message.trim() ? message.trim() : null,
      source: src,
      receiptId: typeof receiptId === "string" ? receiptId : null,
    },
  })

  // Confirmation email — best-effort; a delivery failure must not fail capture.
  const key = process.env.AUTH_RESEND_KEY
  if (key) {
    const subject = src === "advisory" ? "Your ARCS advisory consult" : "You're on the ARCS waitlist"
    const cta = BOOKING_URL ? `\n\nBook your 30-minute session: ${BOOKING_URL}` : ""
    const text = src === "advisory"
      ? `Thanks — we received your request for a 30-minute ARCS-powered advisory session.${cta}\n\nWe'll be in touch shortly.`
      : `You're on the list for full-service ARCS. We'll reach out as spots open.${cta}`
    fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM, to: email.trim(), subject, text }),
    }).catch(() => {})
  }

  return NextResponse.json({ ok: true, bookingUrl: BOOKING_URL || null })
}
