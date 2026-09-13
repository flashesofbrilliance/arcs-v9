import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import fs from "fs"
import path from "path"

export const dynamic = "force-dynamic"

// ADR index — read once at module load from _DECISIONS/ directory
//
// _DECISIONS/ holds real ADRs alongside two non-decision doc types that
// share the directory for convenience: _TEMPLATE.md (the scaffold new ADRs
// are copied from) and RECOIL-REPORT-*.md (call recoil reports). Neither is
// a decision record, so neither should surface as type ADR in link-search.
function isRealAdrFile(filename: string): boolean {
  if (!filename.endsWith(".md")) return false
  if (filename === "_TEMPLATE.md") return false
  if (/^RECOIL-REPORT-/.test(filename)) return false
  return true
}

function getAdrList(): Array<{ id: string; label: string }> {
  try {
    const dir = path.join(process.cwd(), "_DECISIONS")
    return fs.readdirSync(dir)
      .filter(isRealAdrFile)
      .map((f) => ({
        id: f,
        label: f.replace(/\.md$/, "").replace(/-/g, " "),
      }))
  } catch {
    return []
  }
}

export async function GET(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null

  const q = req.nextUrl.searchParams.get("q") ?? ""
  const type = req.nextUrl.searchParams.get("type") ?? "ALL"

  const results: Array<{ type: string; id: string; label: string; meta?: string }> = []

  if (type === "ALL" || type === "RECEIPT") {
    const receipts = await prisma.receipt.findMany({
      where: {
        userId,
        parentId: null,
        ...(q ? { decision: { contains: q } } : {}),
      },
      select: { id: true, decision: true, nciScore: true, mode: true, createdAt: true },
      orderBy: { createdAt: "desc" },
      take: 8,
    })
    receipts.forEach((r) => results.push({
      type: "RECEIPT",
      id: r.id,
      label: r.decision.slice(0, 80),
      meta: `NCI ${r.nciScore} · ${r.mode} · ${new Date(r.createdAt).toLocaleDateString()}`,
    }))
  }

  if (type === "ALL" || type === "ATG_TRIBUTARY") {
    const tributaries = await prisma.receipt.findMany({
      where: {
        userId,
        NOT: { parentId: null },
        ...(q ? { decision: { contains: q } } : {}),
      },
      select: { id: true, decision: true, version: true, createdAt: true },
      orderBy: { createdAt: "desc" },
      take: 6,
    })
    tributaries.forEach((r) => results.push({
      type: "ATG_TRIBUTARY",
      id: r.id,
      label: r.decision.slice(0, 80),
      meta: `Tributary L${r.version} · ${new Date(r.createdAt).toLocaleDateString()}`,
    }))
  }

  if ((type === "ALL" || type === "WISDOM") && userId) {
    const wisdom = await prisma.annotation.findMany({
      where: {
        userId,
        NOT: { kernel: null },
        ...(q ? { kernel: { contains: q } } : {}),
      },
      select: { id: true, kernel: true, createdAt: true },
      orderBy: { createdAt: "desc" },
      take: 6,
    })
    wisdom.forEach((a) => results.push({
      type: "WISDOM",
      id: a.id,
      label: (a.kernel ?? "").slice(0, 80),
      meta: new Date(a.createdAt).toLocaleDateString(),
    }))
  }

  if (type === "ALL" || type === "ADR") {
    const adrs = getAdrList()
    const filtered = q
      ? adrs.filter((a) => a.label.toLowerCase().includes(q.toLowerCase()))
      : adrs
    filtered.slice(0, 6).forEach((a) => results.push({
      type: "ADR",
      id: a.id,
      label: a.label,
    }))
  }

  return NextResponse.json({ ok: true, results })
}
