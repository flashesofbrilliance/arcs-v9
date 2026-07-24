import { NextRequest, NextResponse } from "next/server"
import { handlers } from "@/lib/auth"
import { rateLimit, clientIp } from "@/lib/ratelimit"

export const dynamic = "force-dynamic"

export const { GET } = handlers

// Wallet/abuse guard (same interim limiter as /api/compass, ledger RL-001):
// every magic-link POST sends a Resend email, so an unthrottled endpoint lets
// a script burn the Resend quota and damage the domain's sender reputation.
// 5 sign-in attempts per IP per 10 minutes is generous for a human.
export async function POST(req: NextRequest) {
  if (req.nextUrl.pathname.includes("/signin")) {
    const rl = rateLimit(`auth-signin:${clientIp(req)}`, {
      limit: 5,
      windowMs: 600_000,
    })
    if (!rl.ok) {
      return new NextResponse("Too many sign-in attempts. Try again shortly.", {
        status: 429,
        headers: { "Retry-After": String(rl.retryAfterSec) },
      })
    }
  }
  return handlers.POST(req)
}
