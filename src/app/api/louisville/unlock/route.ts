import { NextRequest, NextResponse } from "next/server"
import { LOUISVILLE_GATE, gateToken } from "@/lib/passcode-gate"

// POST /api/louisville/unlock  { passcode }
// Checks the passcode against LOUISVILLE_PASSCODE and, on match, sets the louisville gate
// cookie (a derived token, never the passcode). Fail-closed when the env var is unset.

export const runtime = "nodejs"

export async function POST(req: NextRequest) {
  let passcode = ""
  try {
    const body = await req.json()
    passcode = (body?.passcode ?? "").toString()
  } catch {
    // fall through to invalid
  }

  const secret = process.env[LOUISVILLE_GATE.env]
  if (!secret) return NextResponse.json({ error: "gate_unconfigured" }, { status: 503 })
  // The two Louisville gates are separate only if their passcodes differ.
  if (process.env.LOUISVILLE_PASSCODE === process.env.LOUISVILLE_PROPOSAL_PASSCODE) {
    return NextResponse.json({ error: "gate_unconfigured" }, { status: 503 })
  }
  if (!passcode || passcode !== secret) return NextResponse.json({ error: "invalid" }, { status: 401 })

  const res = NextResponse.json({ ok: true })
  res.cookies.set(LOUISVILLE_GATE.cookie, await gateToken(LOUISVILLE_GATE.ns, secret), {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  })
  return res
}
