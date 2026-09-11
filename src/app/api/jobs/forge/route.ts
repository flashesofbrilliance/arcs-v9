import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor, FORGE_STATUSES } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// GET /api/jobs/forge?status=queued — the watcher's queue read.
export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const status = req.nextUrl.searchParams.get("status")
  const runs = await prisma.forgeRun.findMany({
    where: status ? { status } : undefined,
    orderBy: { requestedAt: "asc" },
    include: { job: { select: { title: true, company: true, url: true, alertQuery: true } } },
  })
  return NextResponse.json({ runs })
}

// PATCH /api/jobs/forge  { jobid, status?, url?, resumeUrl?, hm?: {kind,text}, contact?: {type,detail,url}, notes? }
// Written by the pipeline (x-jobs-token) or an admin session as a forge moves
// queued → gathering → grading → rendering → built → live.
export async function PATCH(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const b = await req.json().catch(() => null)
  const jobid = String(b?.jobid ?? "")
  if (!jobid) return NextResponse.json({ error: "jobid required" }, { status: 400 })
  if (b.status && !(FORGE_STATUSES as readonly string[]).includes(b.status)) return NextResponse.json({ error: "bad status" }, { status: 400 })

  const data = {
    ...(b.status ? { status: b.status } : {}),
    ...(b.url !== undefined ? { url: b.url } : {}),
    ...(b.resumeUrl !== undefined ? { resumeUrl: b.resumeUrl } : {}),
    ...(b.hm ? { hmKind: b.hm.kind ?? null, hmText: b.hm.text ?? null } : {}),
    ...(b.contact ? { contactType: b.contact.type ?? null, contactDetail: b.contact.detail ?? null, contactUrl: b.contact.url ?? null } : {}),
    ...(b.notes !== undefined ? { notes: b.notes } : {}),
  }
  const run = await prisma.forgeRun.upsert({
    where: { jobid },
    create: { jobid, status: b.status ?? "queued", ...data },
    update: data,
  })
  // A sourced hiring manager or contact path also lands on the opportunity row,
  // so the board shows it even before the forge page exists.
  if (b.hm || b.contact) {
    await prisma.jobOpportunity.update({
      where: { jobid },
      data: {
        ...(b.hm ? { hmKind: b.hm.kind ?? null, hmText: b.hm.text ?? null } : {}),
        ...(b.contact ? { contactType: b.contact.type ?? null, contactDetail: b.contact.detail ?? null, contactUrl: b.contact.url ?? null } : {}),
      },
    })
  }
  return NextResponse.json({ run })
}
