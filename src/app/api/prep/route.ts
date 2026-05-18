import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"

export async function POST(req: NextRequest) {
  const body = await req.json()
  const { stakes, horizon, protecting = [], confidence, entity, adversarialInput } = body

  const prep = await prisma.prepSession.create({
    data: {
      stakes: stakes ?? null,
      horizon: horizon ?? null,
      protecting: JSON.stringify(protecting),
      confidence: typeof confidence === "number" ? confidence : null,
      entity: entity?.trim() || null,
      adversarialInput: adversarialInput?.trim() || null,
    },
  })

  return NextResponse.json({ ok: true, prep_id: prep.id })
}
