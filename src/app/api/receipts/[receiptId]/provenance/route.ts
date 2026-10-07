import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { ProvenanceBody } from "@/lib/request-schemas"

export const dynamic = "force-dynamic"

// Owner-set provenance tag: Receipt.provenance is "real" | "test" | null.
//
// The schema comment is the contract: set by the owner only; never guessed. The
// Accountant (operators/arcs_accountant.py) splits cohorts on it through
// operators/prod_receipt_to_accountant.py, so a wrong tag pollutes the real
// calibration set and a missing tag drops the receipt into the legacy
// founder/external/anonymous split. Measured 2026-10-06 in prod: real 0,
// test 189, null 78 of 267. Nothing here or anywhere else auto-tags.
//
// GET  → the current tag for a receipt the signed-in user owns.
// POST → set it to "real" or "test". Nothing else is accepted: no null (an owner
//        corrects a tag by re-tagging, never by un-knowing it), no third value.
//
// Owner-only on both verbs, same shape as ../outcome: no session, an ownerless
// (anonymous) receipt, or another account all get the same 404, never 403, so an
// id never confirms a receipt exists. Anonymous rows have no owner, so nobody can
// tag them until they are claimed.

const notFound = () => NextResponse.json({ error: "Receipt not found" }, { status: 404 })

function isOwner(ownerId: string | null, userId: string | null): boolean {
  return !!userId && ownerId === userId
}

const select = {
  id: true,
  userId: true,
  provenance: true,
  outcome: { select: { synthetic: true } },
} as const

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const { receiptId } = await params
  const session = await auth()
  const userId = session?.user?.id ?? null
  if (!userId) return notFound()
  const receipt = await prisma.receipt.findUnique({ where: { id: receiptId }, select })
  if (!receipt || !isOwner(receipt.userId, userId)) return notFound()
  return NextResponse.json({
    ok: true,
    receiptId: receipt.id,
    provenance: receipt.provenance,
    syntheticOutcome: receipt.outcome?.synthetic === true,
  })
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ receiptId: string }> }
) {
  const { receiptId } = await params
  const session = await auth()
  const userId = session?.user?.id ?? null
  if (!userId) return notFound()
  const receipt = await prisma.receipt.findUnique({ where: { id: receiptId }, select })
  if (!receipt || !isOwner(receipt.userId, userId)) return notFound()

  const parsed = ProvenanceBody.safeParse(await req.json().catch(() => null))
  if (!parsed.success) {
    return NextResponse.json({ error: 'provenance must be "real" or "test"' }, { status: 400 })
  }
  const { provenance } = parsed.data

  // A synthetic (plumbing-probe) outcome is only legal on a test receipt (see
  // ../outcome). Re-tagging such a receipt "real" would leave a fake outcome on
  // a real row; show the break instead of patching over it.
  if (provenance === "real" && receipt.outcome?.synthetic === true) {
    return NextResponse.json(
      { error: "this receipt carries a synthetic outcome; remove it before tagging the receipt real" },
      { status: 409 }
    )
  }

  if (receipt.provenance === provenance) {
    return NextResponse.json({ ok: true, receiptId: receipt.id, provenance, previous: provenance, changed: false })
  }

  // The where clause carries the owner, so a claim or transfer racing this
  // request cannot land a tag on a row this user no longer owns.
  const updated = await prisma.receipt.updateMany({ where: { id: receiptId, userId }, data: { provenance } })
  if (updated.count !== 1) return notFound()

  return NextResponse.json({ ok: true, receiptId: receipt.id, provenance, previous: receipt.provenance, changed: true })
}
