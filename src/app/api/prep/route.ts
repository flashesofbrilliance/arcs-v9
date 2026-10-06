import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { PrepBody } from "@/lib/request-schemas"

export const dynamic = "force-dynamic"

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  // ADR-016 Option C: prep open to anonymous users

  const parsed = PrepBody.safeParse(await req.json().catch(() => null))
  if (!parsed.success) {
    return NextResponse.json({ error: "invalid prep body" }, { status: 400 })
  }
  const { stakes, horizon, protecting, confidence, entity, adversarialInput, outcomeHorizon } = parsed.data

  const fields = {
    stakes: stakes ?? null,
    horizon: horizon ?? null,
    protecting: protecting ?? [],
    confidence: confidence ?? null,
    entity,
    adversarialInput,
    outcomeHorizon,
  }

  // Trust-contract conformance (/trust §1, /privacy "no auth = no write
  // path"): anonymous prep is NEVER persisted. Echo the normalized fields
  // back so the client can pass them inline to /api/compass (`prep` body
  // field) — same enrichment, zero storage.
  if (!userId) {
    return NextResponse.json({ ok: true, prep_id: null, persisted: false, prep: fields })
  }

  const prep = await prisma.prepSession.create({
    data: { ...fields, protecting: JSON.stringify(fields.protecting), userId },
  })

  return NextResponse.json({ ok: true, prep_id: prep.id, persisted: true })
}
