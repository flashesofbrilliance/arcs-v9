import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"

export const dynamic = "force-dynamic"

export async function POST(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  // ADR-016 Option C: prep open to anonymous users

  const body = await req.json()
  const { stakes, horizon, protecting = [], confidence, entity, adversarialInput, outcomeHorizon } = body

  const fields = {
    stakes: stakes ?? null,
    horizon: horizon ?? null,
    protecting: Array.isArray(protecting) ? protecting : [],
    confidence: typeof confidence === "number" ? confidence : null,
    entity: entity?.trim() || null,
    adversarialInput: adversarialInput?.trim() || null,
    outcomeHorizon: outcomeHorizon?.trim() || null,
  }

  // Trust-contract conformance (/trust §1, /privacy "no auth = no write
  // path"): anonymous prep is NEVER persisted. Echo the normalized fields
  // back so the client can pass them inline to /api/compass (`prep` body
  // field) — same enrichment, zero storage.
  if (!userId) {
    return NextResponse.json({ ok: true, prep_id: null, persisted: false, prep: fields })
  }

  const prep = await prisma.prepSession.create({
    data: { ...fields, protecting: JSON.stringify(fields.protecting) },
  })

  return NextResponse.json({ ok: true, prep_id: prep.id, persisted: true })
}
