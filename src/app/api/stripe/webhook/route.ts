import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { verifyStripeSignature } from "@/lib/paywall"

export const dynamic = "force-dynamic"

type StripeObject = {
  mode?: string
  client_reference_id?: string | null
  payment_status?: string
  customer?: string | null
  status?: string
}

// Stripe webhook. Fail-closed without the signing secret. Idempotent: a replayed
// event rewrites the same values. updateMany everywhere: an unknown id is a no-op,
// not a 500 that makes Stripe retry forever.
//  - checkout.session.completed, mode=payment: the brief Payment Link marks the
//    receipt paid (client_reference_id = receipt id).
//  - checkout.session.completed, mode=subscription: the ARCS Pro link sets the user
//    PRO (client_reference_id = user id), stores the customer id, turns on check-ins.
//  - customer.subscription.updated / .deleted: the customer id finds the user;
//    active or trialing keeps PRO, canceled / unpaid / ended drops to FREE.
export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET
  if (!secret) return NextResponse.json({ error: "Not configured" }, { status: 503 })

  const raw = await req.text()
  if (!verifyStripeSignature(raw, req.headers.get("stripe-signature"), secret)) {
    return NextResponse.json({ error: "Bad signature" }, { status: 400 })
  }

  let event: { type?: string; data?: { object?: StripeObject } }
  try { event = JSON.parse(raw) } catch { return NextResponse.json({ error: "Bad body" }, { status: 400 }) }
  const obj = event.data?.object

  if (event.type === "checkout.session.completed") {
    const ref = obj?.client_reference_id
    if (!ref || obj?.payment_status !== "paid") return NextResponse.json({ received: true })
    if (obj.mode === "subscription") {
      await prisma.user.updateMany({
        where: { id: ref },
        data: { tier: "PRO", debriefOptIn: true, ...(obj.customer ? { stripeCustomerId: obj.customer } : {}) },
      })
    } else {
      await prisma.receipt.updateMany({ where: { id: ref, paidAt: null }, data: { paidAt: new Date() } })
    }
    return NextResponse.json({ received: true })
  }

  if (event.type === "customer.subscription.updated" || event.type === "customer.subscription.deleted") {
    const customer = obj?.customer
    if (!customer) return NextResponse.json({ received: true })
    const live = event.type === "customer.subscription.updated" && (obj?.status === "active" || obj?.status === "trialing")
    // past_due is a grace window: Stripe is still retrying the card, so leave the tier alone.
    if (event.type === "customer.subscription.updated" && obj?.status === "past_due") return NextResponse.json({ received: true })
    await prisma.user.updateMany({ where: { stripeCustomerId: customer }, data: { tier: live ? "PRO" : "FREE" } })
  }

  return NextResponse.json({ received: true })
}
