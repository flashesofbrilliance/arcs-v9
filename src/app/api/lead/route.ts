import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { waitlistEmail, advisoryEmail } from "@/lib/emails"

export const dynamic = "force-dynamic"

// Advisory funnel capture. Stores a Lead and fires a best-effort confirmation
// email (Resend REST — no new dependency). source: "waitlist" | "advisory".
// Also fires a best-effort internal alert to ADMIN_EMAIL so a submission
// doesn't just sit silently in the DB — there was previously no notification
// or review surface at all for this route.
const BOOKING_URL = process.env.NEXT_PUBLIC_CONSULT_BOOKING_URL ?? "https://calendar.app.google/r3eSwEE2HueXUBeC6"
const FROM = process.env.EMAIL_FROM ?? "ARCS <noreply@arcs.care>"
const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "zach.harris@gmail.com"

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
      ? `Thanks. We received your request for a 30-minute ARCS-powered advisory session.${cta}\n\nWe'll be in touch shortly.`
      : `You're on the list for full-service ARCS. We'll reach out as spots open.${cta}`
    const html = src === "advisory"
      ? advisoryEmail(typeof name === "string" ? name : null, BOOKING_URL || null)
      : waitlistEmail(BOOKING_URL || null)

    // Internal alert so a submission never just sits silently in the DB.
    const adminSubject = src === "advisory"
      ? `New advisory request: ${email.trim()}`
      : `New waitlist signup: ${email.trim()}`
    const adminLines = [
      `Source: ${src}`,
      `Email: ${email.trim()}`,
      ...(typeof name === "string" && name.trim() ? [`Name: ${name.trim()}`] : []),
      ...(typeof message === "string" && message.trim() ? [`Message: ${message.trim()}`] : []),
      ...(typeof receiptId === "string" && receiptId ? [`Receipt: ${receiptId}`] : []),
    ]

    // One send helper. fetch resolves even on HTTP error, so check res.ok and
    // LOG failures — the previous silent .catch() meant a dropped notification
    // was invisible.
    const send = (to: string, subj: string, txt: string, htmlBody?: string) =>
      fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from: FROM, to, subject: subj, text: txt, ...(htmlBody ? { html: htmlBody } : {}) }),
      })
        .then(async (r) => { if (!r.ok) console.error(`[lead] resend send to ${to} failed ${r.status}: ${await r.text().catch(() => "")}`) })
        .catch((e) => console.error(`[lead] resend send to ${to} threw:`, e))

    // AWAITED. An un-awaited fetch after the response is not guaranteed to run
    // on Vercel serverless (the function can be frozen before it fires), which
    // silently dropped signup alerts. allSettled keeps it best-effort: a
    // delivery failure logs but never fails the capture above.
    await Promise.allSettled([
      send(email.trim(), subject, text, html),
      send(ADMIN_EMAIL, adminSubject, adminLines.join("\n")),
    ])
  }

  return NextResponse.json({ ok: true, bookingUrl: BOOKING_URL || null })
}
