import { NextRequest, NextResponse } from "next/server"
import { AMMO_COOKIE, ammoUnlocked } from "@/lib/ammo-gate"
import { prisma } from "@/lib/db"
import { applyTouch, scorecard, todayList, touchSchema, type DeskAccount } from "@/lib/lewoof-desk"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

// GET  /api/lewoof/desk  -> today's list + the group scorecard
// POST /api/lewoof/desk  { accountId, kind, result, note? } -> logs one call/email result
//
// The proxy leaves /api open on the lewoof host (the passcode form posts there), so this
// route checks the same passcode cookie itself and fails closed: an unset
// RECRUITHAUS_AMMO_PASSWORD or a missing cookie returns 401 before any query runs.
// Contacts are returned only from here, never from a file in public/.

const NO_STORE = { "Cache-Control": "no-store" }

async function authorized(req: NextRequest): Promise<boolean> {
  return ammoUnlocked(req.cookies.get(AMMO_COOKIE)?.value, process.env.RECRUITHAUS_AMMO_PASSWORD)
}

export async function GET(req: NextRequest) {
  if (!(await authorized(req))) return NextResponse.json({ error: "locked" }, { status: 401, headers: NO_STORE })
  const accounts = (await prisma.lewoofAccount.findMany()) as DeskAccount[]
  const touches = await prisma.lewoofTouch.findMany({ select: { accountId: true, result: true } })
  return NextResponse.json(
    { today: todayList(accounts, new Date()), scorecard: scorecard(accounts, touches), total: accounts.length },
    { headers: NO_STORE },
  )
}

export async function POST(req: NextRequest) {
  if (!(await authorized(req))) return NextResponse.json({ error: "locked" }, { status: 401, headers: NO_STORE })
  const raw = await req.text()
  if (raw.length > 4096) return NextResponse.json({ error: "too_large" }, { status: 413, headers: NO_STORE })
  let parsed
  try {
    parsed = touchSchema.safeParse(JSON.parse(raw))
  } catch {
    return NextResponse.json({ error: "invalid" }, { status: 400, headers: NO_STORE })
  }
  if (!parsed.success) return NextResponse.json({ error: "invalid" }, { status: 400, headers: NO_STORE })
  const { accountId, kind, result, note } = parsed.data

  const acct = await prisma.lewoofAccount.findUnique({ where: { id: accountId } })
  if (!acct) return NextResponse.json({ error: "not_found" }, { status: 404, headers: NO_STORE })

  const next = applyTouch(acct, result, new Date())
  await prisma.$transaction([
    prisma.lewoofTouch.create({ data: { accountId, kind, result, note: note ?? null } }),
    prisma.lewoofAccount.update({ where: { id: accountId }, data: next }),
  ])
  return NextResponse.json({ ok: true, nextTouch: next.nextTouch, stage: next.stage }, { headers: NO_STORE })
}
