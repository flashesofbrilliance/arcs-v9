import { NextRequest, NextResponse, after } from "next/server"
import { adminEmails } from "@/lib/admin"
import { prisma } from "@/lib/db"
import { waitlistEmail, advisoryEmail } from "@/lib/emails"
import { rateLimit, clientIp } from "@/lib/ratelimit"
import { z } from "zod"

export const dynamic = "force-dynamic"

// Advisory funnel capture. Stores a Lead and fires a best-effort confirmation
// email (Resend REST, no new dependency). source: "waitlist" | "advisory".
// Also fires a best-effort internal alert to ADMIN_EMAILS so a submission
// doesn't just sit silently in the DB.
//
// Abuse model (2026-10-03 hardening). This route sends mail FROM arcs.care TO
// whatever address is typed, so without limits it is an email cannon:
//   - per-IP rate limit (instance-local, see ratelimit.ts; gateway limit is GW-002)
//   - body capped at 8 KB and validated with zod before anything is read
//   - honeypot field `website`: bots fill it, humans never see it; we answer
//     ok and write nothing
//   - waitlist is idempotent per address (case-insensitive): a repeat join
//     writes no row and sends no mail, so one address gets one confirmation
//   - advisory keeps every request (each carries its own message) but the
//     requester confirmation AND the admin alert go out at most once per
//     address per 24h
//   - name and message are stored for advisory only; never echoed into mail
//     sent to the (unverified) requester address
// The response BODY is identical for a new or an existing address. Timing is
// not fully identical: a new address costs one extra DB write (a few ms). The
// mail send is in after(), so the large difference is gone; closing the last
// one needs a unique (source, lower(email)) index plus a single upsert.
const BOOKING_URL = process.env.NEXT_PUBLIC_CONSULT_BOOKING_URL ?? "https://calendar.app.google/r3eSwEE2HueXUBeC6"
const FROM = process.env.EMAIL_FROM ?? "ARCS <noreply@arcs.care>"

const MAX_BODY = 8 * 1024
const RECEIPT_ID = /^[A-Za-z0-9_-]{6,64}$/
const DAY_MS = 24 * 60 * 60 * 1000

const optText = (max: number) => z.string().max(max).optional().transform((t) => (t && t.trim() ? t.trim() : null))
const LeadBody = z.object({
  email: z.string().trim().max(254).regex(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
  name: optText(120),
  message: optText(2000),
  source: z.enum(["waitlist", "advisory"]).optional(),
  receiptId: z.string().regex(RECEIPT_ID).optional(),
  website: z.string().max(200).optional(),
})

export async function POST(req: NextRequest) {
  const rl = rateLimit(`lead:${clientIp(req)}`, { limit: 6, windowMs: 10 * 60_000 })
  if (!rl.ok) {
    return NextResponse.json(
      { error: "Too many attempts. Try again shortly.", retryAfterSec: rl.retryAfterSec },
      { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } },
    )
  }

  if (Number(req.headers.get("content-length") ?? 0) > MAX_BODY) {
    return NextResponse.json({ error: "Request too large" }, { status: 413 })
  }
  const raw = await req.text().catch(() => "")
  if (raw.length > MAX_BODY) return NextResponse.json({ error: "Request too large" }, { status: 413 })
  let json: unknown = {}
  try { json = JSON.parse(raw || "{}") } catch { /* falls through to validation */ }
  const parsed = LeadBody.safeParse(json)
  if (!parsed.success) {
    return NextResponse.json({ error: "A valid email is required" }, { status: 400 })
  }
  const { email, name, message, source, receiptId, website } = parsed.data
  const src = source === "advisory" ? "advisory" : "waitlist"
  const ok = NextResponse.json({ ok: true, bookingUrl: BOOKING_URL || null })

  // Honeypot tripped: look identical to success, store nothing, send nothing.
  if (website && website.trim()) return ok

  const addr = email
  const nm = src === "advisory" ? name : null
  const msg = src === "advisory" ? message : null
  const rid = receiptId ?? null

  const prior = await prisma.lead.findFirst({
    where: {
      source: src,
      email: { equals: addr, mode: "insensitive" },
      ...(src === "advisory" ? { createdAt: { gte: new Date(Date.now() - DAY_MS) } } : {}),
    },
    select: { id: true },
  })

  // Waitlist: already on the list. Same answer, no row, no mail.
  if (src === "waitlist" && prior) return ok

  await prisma.lead.create({
    data: { email: addr, name: nm, message: msg, source: src, receiptId: rid },
  })

  const key = process.env.AUTH_RESEND_KEY
  if (key) {
    // Nothing reaches this point for a repeat waitlist join, and a repeat
    // advisory request within 24h is stored but sends no mail at all.
    if (!prior) after(() => sendMail({ key, src, addr, nm, msg, rid }))
  }

  return ok
}

async function sendMail({ key, src, addr, nm, msg, rid }: {
  key: string; src: "waitlist" | "advisory"; addr: string; nm: string | null; msg: string | null; rid: string | null
}) {
  const subject = src === "advisory" ? "Your ARCS advisory consult" : "You're on the ARCS waitlist"
  const cta = BOOKING_URL ? `\n\nBook your 30-minute session: ${BOOKING_URL}` : ""
  const text = src === "advisory"
    ? `Thanks. We received your request for a 30-minute ARCS-powered advisory session.${cta}\n\nWe'll be in touch shortly.`
    : `You're on the list for full-service ARCS. We'll reach out as spots open.${cta}`
  const html = src === "advisory" ? advisoryEmail(BOOKING_URL || null) : waitlistEmail(BOOKING_URL || null)

  const adminSubject = src === "advisory" ? `New advisory request: ${addr}` : `New waitlist signup: ${addr}`
  const adminLines = [
    `Source: ${src}`,
    `Email: ${addr}`,
    ...(nm ? [`Name: ${nm}`] : []),
    ...(msg ? [`Message: ${msg}`] : []),
    ...(rid ? [`Receipt: ${rid}`] : []),
  ]

  // fetch resolves even on HTTP error, so check res.ok and LOG failures; a
  // silent .catch() once made dropped notifications invisible.
  const send = (to: string, subj: string, txt: string, htmlBody?: string) =>
    fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM, to, subject: subj, text: txt, ...(htmlBody ? { html: htmlBody } : {}) }),
    })
      .then((r) => { if (!r.ok) console.error(`[lead] resend send failed ${r.status}`) })
      .catch((e) => console.error("[lead] resend send threw:", e instanceof Error ? e.name : "unknown"))

  // after() keeps the function alive until these settle on Vercel (the old
  // un-awaited fetch was frozen mid-flight and dropped alerts). allSettled
  // keeps it best-effort: a delivery failure logs, the capture already stands.
  await Promise.allSettled([
    send(addr, subject, text, html),
    // Internal alert goes to the same allowlist that gates /admin/leads
    // (ADMIN_EMAILS via src/lib/admin.ts). The old singular ADMIN_EMAIL was never
    // set in prod, so alerts rode a hardcoded fallback address.
    ...adminEmails().map((to) => send(to, adminSubject, adminLines.join("\n"))),
  ])
  if (adminEmails().length === 0) console.error("[lead] ADMIN_EMAILS unset: no internal alert sent")
}
