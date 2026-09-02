import { NextRequest, NextResponse } from "next/server"
import { AMMO_COOKIE, ammoToken } from "@/lib/ammo-gate"

// POST /api/recruithaus/unlock  { passcode }
// Validates the shared passcode against RECRUITHAUS_AMMO_PASSWORD and, on match,
// sets an httpOnly token cookie that the middleware (src/proxy.ts) checks before
// serving any /recruithaus-ammo* asset. The cookie holds a derived SHA-256 token,
// never the passcode. See src/lib/ammo-gate.ts for the full rationale.

export const runtime = "nodejs"

export async function POST(req: NextRequest) {
  let passcode = ""
  try {
    const body = await req.json()
    passcode = (body?.passcode ?? "").toString()
  } catch {
    // fall through to invalid
  }

  const secret = process.env.RECRUITHAUS_AMMO_PASSWORD
  if (!secret) {
    // Fail closed with a distinct signal so the gate page can say "not configured yet".
    return NextResponse.json({ error: "gate_unconfigured" }, { status: 503 })
  }

  if (!passcode || passcode !== secret) {
    return NextResponse.json({ error: "invalid" }, { status: 401 })
  }

  const token = await ammoToken(secret)
  const res = NextResponse.json({ ok: true })
  res.cookies.set(AMMO_COOKIE, token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  })
  return res
}
