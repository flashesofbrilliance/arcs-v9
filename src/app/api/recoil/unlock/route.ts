import { NextRequest, NextResponse } from "next/server"

const YEAR = 60 * 60 * 24 * 365

export async function POST(req: NextRequest) {
  const { password } = await req.json()
  const secret = process.env.RECOIL_PASSWORD

  if (!secret || password !== secret) {
    return NextResponse.json({ error: "denied" }, { status: 401 })
  }

  const res = NextResponse.json({ ok: true })
  res.cookies.set("recoil_session", secret, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: YEAR,
    path: "/",
  })
  return res
}
