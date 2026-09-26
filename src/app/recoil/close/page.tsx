import { notFound, redirect } from "next/navigation"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"
import { prisma } from "@/lib/db"
import { CloseList, type CloseRow } from "./CloseList"

// Admin outcome close-list — the cheap lever for seeding the calibration corpus
// (induced-backlog: outcome-capture-rate-keel-gap). The 2/247 "keel gap" is a
// founder-QA artifact; the real unblock for sage_efficacy / svc-SAGE is enough
// PAIRED (nci vs matched/regret) rows spanning Y-states. This page lists the
// signed-in admin's OWN open, eligible receipts grouped by render state so they
// can be closed in one sitting. It never fabricates the signal — every row still
// requires the human to supply what/matched/regret (§5.1). It posts to the
// existing /api/receipts/[id]/outcome route (ownership gate satisfied: own rows).
// Internal surface, gated exactly like /recoil (src/lib/admin.ts + proxy cookie).
export const dynamic = "force-dynamic"

const RENDER_ORDER: Record<string, number> = { SHARP: 0, DEGRADED: 1, GRAIN: 2, MOIRE: 3 }

function renderOf(yGateScore: string | null): string {
  if (!yGateScore) return "?"
  try {
    const v = JSON.parse(yGateScore) as { render_resolution?: string }
    return v.render_resolution || "?"
  } catch {
    return "?"
  }
}

export default async function CloseListPage() {
  const session = await auth()
  // ADR-001 doctrine: prod enforces identity, dev passes through.
  if (process.env.NODE_ENV !== "development") {
    if (!session?.user?.email) redirect("/compass?next=/recoil/close")
    if (!isAdmin(session)) notFound()
  }

  // Own receipts in prod; dev pass-through has no session, so fall back to all
  // eligible open receipts for local QA (the POST route also skips the gate in dev).
  const userId = session?.user?.id ?? null
  const receipts = await prisma.receipt.findMany({
    where: { outcome: null, ...(userId ? { userId } : { userId: { not: null } }) },
    select: {
      id: true,
      decision: true,
      sharpQuestion: true,
      trueNorth: true,
      nciScore: true,
      yGateScore: true,
      createdAt: true,
    },
    orderBy: { createdAt: "desc" },
  })

  const rows: CloseRow[] = receipts.map((r) => ({
    id: r.id,
    question: (r.sharpQuestion || r.decision || "(untitled)").slice(0, 200),
    trueNorth: (r.trueNorth || "").slice(0, 240),
    nci: r.nciScore,
    render: renderOf(r.yGateScore),
    createdAt: r.createdAt.toISOString().slice(0, 10),
  }))

  rows.sort(
    (a, b) =>
      (RENDER_ORDER[a.render] ?? 9) - (RENDER_ORDER[b.render] ?? 9) || a.nci - b.nci,
  )

  return <CloseList rows={rows} />
}
