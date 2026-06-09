import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

export const dynamic = "force-dynamic"

// ADR-016 Option C: migrate anonymous receipts to authenticated user on sign-in.
// sessionId comes from the request body (stored in localStorage pre-auth).
// userId is sourced from server-side auth() ONLY — never from the request body.

export async function PATCH(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const body = await req.json()
  const { sessionId } = body

  if (!sessionId || typeof sessionId !== "string") {
    return NextResponse.json({ error: "sessionId is required" }, { status: 400 })
  }

  // Only claim receipts that are still anonymous (userId: null) for this sessionId.
  // Never overwrite receipts that already belong to another user.
  const result = await prisma.receipt.updateMany({
    where: { sessionId, userId: null },
    data: { userId },
  })

  return NextResponse.json({ claimed: result.count })
}
