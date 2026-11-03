import { NextRequest, NextResponse } from "next/server"
import { MONDAY_GATE, gateToken } from "@/lib/passcode-gate"

// POST /api/monday/unlock  { passcode }
// Checks the passcode against MONDAY_PASSCODE and, on match, sets the monday gate
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

  const secret = process.env[MONDAY_GATE.env]
  if (!secret) return NextResponse.json({ error: "gate_unconfigured" }, { status: 503 })
  if (!passcode || passcode !== secret) return NextResponse.json({ error: "invalid" }, { status: 401 })

  // One line per successful unlock, readable in Vercel runtime logs. No IP: country, city, user agent only.
  console.log("monday_access", JSON.stringify({ event: "unlock", country: req.headers.get("x-vercel-ip-country"), city: req.headers.get("x-vercel-ip-city"), ua: req.headers.get("user-agent")?.slice(0, 120) }))

  const res = NextResponse.json({ ok: true })
  res.cookies.set(MONDAY_GATE.cookie, await gateToken(MONDAY_GATE.ns, secret), {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  })
  return res
}
