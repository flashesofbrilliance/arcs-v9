import { NextResponse, type NextRequest } from "next/server"
import { prisma } from "@/lib/db"
import { callerFor, loadScanSpec } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// GET /api/jobs — everything the board renders: opportunities with their swipe
// and forge state, settings, and the scan spec (rubric as data).
export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const [rows, settings] = await Promise.all([
    prisma.jobOpportunity.findMany({
      include: { swipe: true, forge: true },
      orderBy: [{ composite: "desc" }, { firstSeen: "desc" }],
    }),
    prisma.jobBoardSetting.findMany(),
  ])
  const spec = loadScanSpec()
  return NextResponse.json({
    rows,
    settings: Object.fromEntries(settings.map((s) => [s.key, s.value])),
    spec,
    caller: caller.kind,
  })
}

// DELETE /api/jobs?jobid=<id> — only hand-added and eval rows (manual-*, eval-*)
// may be deleted; alert-sourced rows are the record and stay.
export async function DELETE(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const jobid = req.nextUrl.searchParams.get("jobid") ?? ""
  if (!/^(manual|eval)-/.test(jobid)) return NextResponse.json({ error: "only manual-* or eval-* rows can be deleted" }, { status: 400 })
  const r = await prisma.jobOpportunity.deleteMany({ where: { jobid } })
  return NextResponse.json({ deleted: r.count })
}

// POST /api/jobs — add a row by hand (a posting URL that did not come through
// the alert digests), or upsert scored rows from the pipeline (array body).
export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  if (!body) return NextResponse.json({ error: "Bad JSON" }, { status: 400 })

  // Pipeline upsert: [{jobid, title, company, ...}] — fields mirror the model.
  if (Array.isArray(body)) {
    if (caller.kind === "admin" && process.env.NODE_ENV === "production" && !req.headers.get("x-jobs-token")) {
      // admins may still bulk-upsert from a session; allowed, logged by nothing.
    }
    let n = 0
    for (const r of body) {
      if (!r?.jobid || !r?.title || !r?.company || !r?.url) continue
      const data = {
        title: String(r.title),
        company: String(r.company),
        location: r.location ?? null,
        url: String(r.url),
        alertQuery: r.alertQuery ?? r.alert_query ?? null,
        alertLocation: r.alertLocation ?? r.alert_location ?? null,
        source: r.source ?? "linkedin_alert_digest",
        firstSeen: new Date(r.firstSeen ?? r.first_seen_date ?? Date.now()),
        seenCount: Number(r.seenCount ?? r.seen_count ?? 1),
        salary: r.salary ?? null,
        composite: r.composite == null ? null : Number(r.composite),
        band: r.band ?? "UNSCORED",
        dims: r.dims ? (typeof r.dims === "string" ? r.dims : JSON.stringify(r.dims)) : null,
        gates: r.gates ? (typeof r.gates === "string" ? r.gates : JSON.stringify(r.gates)) : null,
        assessment: r.assessment ?? null,
        atsClass: r.atsClass ?? r.ats_class ?? null,
        atsName: r.atsName ?? r.ats_name ?? null,
        companyType: r.companyType ?? r.company_type ?? null,
        compBand: r.compBand ?? r.comp_band ?? null,
        workLocation: r.workLocation ?? r.work_location ?? null,
        hmKind: r.hmKind ?? r.hiring_manager?.kind ?? null,
        hmText: r.hmText ?? r.hiring_manager?.text ?? null,
        contactType: r.contactType ?? r.contact?.type ?? null,
        contactDetail: r.contactDetail ?? r.contact?.detail ?? null,
        contactUrl: r.contactUrl ?? r.contact?.url ?? null,
        nextStep: r.nextStep ?? r.next_step ?? null,
        jdHits: r.jdHits ? (typeof r.jdHits === "string" ? r.jdHits : JSON.stringify(r.jdHits)) : (r.jd_hits ? JSON.stringify(r.jd_hits) : null),
        unscoredWhy: r.unscoredWhy ?? r.why ?? null,
        scoredAt: r.scoredAt ? new Date(r.scoredAt) : (r.composite != null ? new Date() : null),
      }
      // A re-ingest that carries no score must not clobber a score already on the row
      // (2026-09-11: a bridge_scan re-upsert reset 64 scored rows to UNSCORED). On UPDATE,
      // scoring fields are only written when the payload actually carries a composite or band.
      const carriesScore = r.composite != null || (r.band && r.band !== "UNSCORED")
      const { composite, band, dims, gates, assessment, scoredAt, unscoredWhy, ...rest } = data
      const update = carriesScore ? data : rest
      await prisma.jobOpportunity.upsert({ where: { jobid: String(r.jobid) }, create: { jobid: String(r.jobid), ...data }, update })
      n++
    }
    return NextResponse.json({ upserted: n })
  }

  // Manual add from the page.
  const { url, title, company, composite, jobid: wanted } = body as { url?: string; title?: string; company?: string; composite?: number | null; jobid?: string }
  if (!url || !title || !company) return NextResponse.json({ error: "url, title, company required" }, { status: 400 })
  // eval-* ids may be supplied by the trigger eval so it can clean up after itself.
  const jobid = wanted && /^eval-[A-Za-z0-9_-]+$/.test(wanted) ? wanted : `manual-${Date.now()}`
  const row = await prisma.jobOpportunity.create({
    data: {
      jobid, title, company, url, source: "manual", alertQuery: "manual", firstSeen: new Date(),
      composite: composite == null || Number.isNaN(Number(composite)) ? null : Number(composite),
      band: composite == null ? "UNSCORED" : Number(composite) >= 0.7 ? "PURSUE" : Number(composite) >= 0.5 ? "CONSIDER" : "PASS",
      unscoredWhy: composite == null ? "added by hand, not yet scored" : null,
      atsClass: "unk", atsName: "unverified", contactType: "unverified", contactDetail: "resolves on swipe",
      hmKind: "unknown", nextStep: "Added by hand. Resolve ATS and hiring manager on swipe.",
    },
    include: { swipe: true, forge: true },
  })
  return NextResponse.json({ row }, { status: 201 })
}
