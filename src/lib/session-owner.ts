import { prisma } from "@/lib/db"

// Resolve a client-supplied decision-thread id for a signed-in caller. The id
// is reused only when it is a sane string and no receipt in that thread
// belongs to anyone else (incl. legacy unowned rows); otherwise a fresh id is
// minted, so a caller cannot graft receipts onto another user's thread.
// Callers without a userId never persist, so their id is passed through.
export async function resolveOwnedSessionId(clientId: unknown, userId: string | null): Promise<string> {
  const id = typeof clientId === "string" && clientId.length > 0 && clientId.length <= 128 ? clientId : null
  if (!id) return crypto.randomUUID()
  if (!userId) return id
  const foreign = await prisma.receipt.findFirst({
    // Explicit null branch: SQL `userId <> x` skips NULL rows.
    where: { sessionId: id, OR: [{ userId: { not: userId } }, { userId: null }] },
    select: { id: true },
  })
  return foreign ? crypto.randomUUID() : id
}
