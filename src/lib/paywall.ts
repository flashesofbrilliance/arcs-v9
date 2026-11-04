import { createHmac, timingSafeEqual } from "crypto"

// Paid brief (2026-11-02). The receipt stays free; generating its brief costs one
// Stripe Payment Link purchase. Off unless STRIPE_PAYMENT_LINK is set, so the
// brief stays free in dev and until the link exists. No Stripe SDK: the link
// handles checkout, the webhook below needs only the signing secret.

export function paywallOn(): boolean {
  return !!process.env.STRIPE_PAYMENT_LINK || !!process.env.STRIPE_PRO_LINK
}

// ARCS Pro (2026-11-04): a subscription Payment Link. A PRO owner opens every brief.
// Display price: src/lib/paywall-copy.ts (client-safe).

export function briefLocked(r: { paidAt: Date | null }, ownerTier?: string | null): boolean {
  return paywallOn() && !r.paidAt && ownerTier !== "PRO"
}

// client_reference_id carries the user id through the subscription checkout.
export function proUrlFor(userId: string): string | null {
  const link = process.env.STRIPE_PRO_LINK
  if (!link) return null
  const u = new URL(link)
  u.searchParams.set("client_reference_id", userId)
  return u.toString()
}

// client_reference_id carries the receipt id through checkout to the webhook.
export function paymentUrlFor(receiptId: string): string | null {
  const link = process.env.STRIPE_PAYMENT_LINK
  if (!link) return null
  const u = new URL(link)
  u.searchParams.set("client_reference_id", receiptId)
  return u.toString()
}

// Stripe-Signature: "t=<ts>,v1=<hex>[,v1=...]"; HMAC-SHA256 of "<t>.<rawBody>".
export function verifyStripeSignature(rawBody: string, header: string | null, secret: string, toleranceSec = 300): boolean {
  if (!header) return false
  const parts = header.split(",").map((p) => p.split("=") as [string, string])
  const t = parts.find(([k]) => k === "t")?.[1]
  const sigs = parts.filter(([k]) => k === "v1").map(([, v]) => v)
  if (!t || sigs.length === 0) return false
  if (Math.abs(Date.now() / 1000 - Number(t)) > toleranceSec) return false
  const expected = createHmac("sha256", secret).update(`${t}.${rawBody}`).digest()
  return sigs.some((s) => {
    const got = Buffer.from(s, "hex")
    return got.length === expected.length && timingSafeEqual(got, expected)
  })
}
