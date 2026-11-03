import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { verifyStripeSignature } from "@/lib/paywall"

export const dynamic = "force-dynamic"

// Stripe webhook: checkout.session.completed from the brief Payment Link marks
// the receipt paid (client_reference_id = receipt id). Fail-closed without the
// signing secret. Idempotent: a replayed event only rewrites the same paidAt.
export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET
  if (!secret) return NextResponse.json({ error: "Not configured" }, { status: 503 })

  const raw = await req.text()
  if (!verifyStripeSignature(raw, req.headers.get("stripe-signature"), secret)) {
    return NextResponse.json({ error: "Bad signature" }, { status: 400 })
  }

  let event: { type?: string; data?: { object?: { client_reference_id?: string | null; payment_status?: string } } }
  try { event = JSON.parse(raw) } catch { return NextResponse.json({ error: "Bad body" }, { status: 400 }) }

  if (event.type !== "checkout.session.completed") return NextResponse.json({ received: true })
  const obj = event.data?.object
  const receiptId = obj?.client_reference_id
  if (!receiptId || obj?.payment_status !== "paid") return NextResponse.json({ received: true })

  // updateMany: an unknown id is a no-op, not a 500 that makes Stripe retry forever.
  await prisma.receipt.updateMany({ where: { id: receiptId, paidAt: null }, data: { paidAt: new Date() } })
  return NextResponse.json({ received: true })
}
