import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { del } from "@vercel/blob"

// Trust contract §3 (ledger DEL-003): "Account deletion removes all receipts,
// outcomes, and personal data from the production database." This endpoint
// makes that commitment executable instead of an email promise. Auth-gated;
// deletes the signed-in user's own data only. One-way gate — no soft delete.
export async function POST() {
  const session = await auth()
  const userId = session?.user?.id
  const userEmail = session?.user?.email ?? null
  if (!userId) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 })
  }

  // Uploaded files live in Vercel Blob, not the database. Delete them first:
  // if this fails, nothing has been removed yet and the request can be retried,
  // rather than leaving files behind a deleted account.
  const upload = await prisma.profileUpload.findUnique({ where: { userId }, select: { pdfUrl: true, exportUrl: true } })
  const blobUrls = [upload?.pdfUrl, upload?.exportUrl].filter((u): u is string => !!u)
  if (blobUrls.length) {
    try {
      await del(blobUrls)
    } catch (e) {
      console.error("[account/delete] blob delete failed:", e instanceof Error ? e.name : "unknown")
      return NextResponse.json({ error: "Could not delete uploaded files. Nothing was removed; try again." }, { status: 500 })
    }
  }

  const receipts = await prisma.receipt.findMany({
    where: { userId },
    select: { id: true, prepId: true },
  })
  const receiptIds = receipts.map((r) => r.id)
  const prepIds = receipts.map((r) => r.prepId).filter((p): p is string => !!p)

  await prisma.$transaction(async (tx) => {
    if (receiptIds.length) {
      // Receipt-child tables first (FK order), then lineage: other receipts
      // (e.g. anonymous follow-ups) may point at a deleted receipt as parent —
      // detach them rather than orphan the FK.
      await tx.brief.deleteMany({ where: { receiptId: { in: receiptIds } } })
      await tx.sageTrace.deleteMany({ where: { receiptId: { in: receiptIds } } })
      await tx.prepGuide.deleteMany({ where: { receiptId: { in: receiptIds } } })
      await tx.outcome.deleteMany({ where: { receiptId: { in: receiptIds } } })
      await tx.annotation.deleteMany({ where: { receiptId: { in: receiptIds } } })
      await tx.receipt.updateMany({
        where: { parentId: { in: receiptIds } },
        data: { parentId: null },
      })
      await tx.receipt.deleteMany({ where: { id: { in: receiptIds } } })
    }
    if (prepIds.length) {
      await tx.prepSession.deleteMany({ where: { id: { in: prepIds } } })
    }
    await tx.annotation.deleteMany({ where: { userId } })

    const signals = await tx.scanSignal.findMany({
      where: { userId },
      select: { id: true },
    })
    const signalIds = signals.map((s) => s.id)
    if (signalIds.length) {
      await tx.scanFeedback.deleteMany({ where: { signalId: { in: signalIds } } })
      await tx.scanSignal.updateMany({
        where: { parentSignalId: { in: signalIds } },
        data: { parentSignalId: null },
      })
      await tx.scanSignal.deleteMany({ where: { id: { in: signalIds } } })
    }

    await tx.profileUpload.deleteMany({ where: { userId } })
    if (userEmail) {
      await tx.lead.deleteMany({ where: { email: { equals: userEmail, mode: "insensitive" } } })
    }
    // Account + Session rows cascade via schema onDelete: Cascade.
    await tx.user.delete({ where: { id: userId } })
  })

  return NextResponse.json({ deleted: true, receipts: receiptIds.length })
}
