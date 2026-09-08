import { redirect } from "next/navigation"
import { prisma } from "@/lib/db"
import { pageViewerAllowed } from "@/lib/jobs"
import { signal } from "@/ui/tokens"
import { LaneSurfaces, type LaneData, type Stage, type StageItem } from "./LaneSurfaces"

// jobs.arcs.care/jobs/lane — the three wired Compass Lane surfaces (Lane view,
// Sources, Debrief) over the live job-search lane. Server-rendered from Prisma,
// gated (admin session in prod), inline styles. The board (/jobs) is the swipe
// UI; this is the pipeline view of the same rows across the five verb-stages.
export const dynamic = "force-dynamic"
export const metadata = { title: "Compass Lane", robots: { index: false, follow: false } }

const fmt = (n: number | null) => (n == null ? "—" : n.toFixed(3))
const bandTone = (b: string) => (b === "PURSUE" ? signal.green : b === "CONSIDER" ? signal.gold : b === "PASS" ? signal.red : signal.steel)

export default async function LanePage() {
  if (!(await pageViewerAllowed())) redirect("/compass?next=/jobs/lane")

  const [rows, sources, requests, outcomes, corrections] = await Promise.all([
    prisma.jobOpportunity.findMany({ include: { swipe: true, forge: true, laneOutcome: true }, orderBy: [{ composite: "desc" }, { firstSeen: "desc" }] }),
    prisma.source.findMany({ orderBy: [{ status: "asc" }, { key: "asc" }] }),
    prisma.ingestRequest.findMany({ orderBy: { requestedAt: "desc" }, take: 12 }),
    prisma.laneOutcome.findMany({ include: { job: true }, orderBy: { closedAt: "desc" } }),
    prisma.correction.findMany({ orderBy: { createdAt: "desc" }, take: 8 }),
  ])

  const item = (r: (typeof rows)[number], extra?: Partial<StageItem>): StageItem => ({
    jobid: r.jobid, company: r.company, title: r.title, stage: stageOf(r), manual: r.laneStage != null,
    score: r.composite != null ? fmt(r.composite) : undefined, tone: bandTone(r.band), ...extra,
  })

  // Derived stage is the floor; a manual laneStage overrides it (mark applied,
  // advance the interview loop). Each row lands in exactly one column.
  const derived = (r: (typeof rows)[number]): string =>
    r.laneOutcome ? "outcome"
    : r.band === "UNSCORED" ? "research"
    : (r.forge || r.swipe?.direction === "r") ? "apply"
    : "qualify"
  const stageOf = (r: (typeof rows)[number]): string => r.laneStage ?? derived(r)
  const inStage = (k: string) => rows.filter((r) => stageOf(r) === k)
  const research = inStage("research"), qualify = inStage("qualify"), apply = inStage("apply"), interview = inStage("interview"), closed = inStage("outcome")

  const stages: Stage[] = [
    { verb: "analyze", label: "Research", print: "JD read + record graded", sla: "2d", count: research.length,
      items: research.slice(0, 4).map((r) => item(r, { score: undefined, meta: r.unscoredWhy ?? "awaiting score" })),
      empty: "Every row is scored. New ingest lands here first." },
    { verb: "assess", label: "Qualify", print: "band, tier, one-line read", count: qualify.length,
      items: qualify.slice(0, 4).map((r) => item(r, { meta: "unswiped" })), empty: "No scored rows awaiting a swipe." },
    { verb: "evaluate", label: "Apply and screen", print: "resume cut, tailor notes, landing page", sla: "7d", count: apply.length,
      items: apply.slice(0, 5).map((r) => item(r, { meta: r.forge ? r.forge.status : "swiped" })), empty: "Swipe right to move a role here." },
    { verb: "synthesize", label: "Interview loop", print: "pre-call brief, full-tier artifacts", sla: "21d", count: interview.length,
      items: interview.slice(0, 4).map((r) => item(r)), empty: "A row moves here when a recruiter or hiring manager responds. The full forge unlocks then." },
    { verb: "recapitulate", label: "Outcome and correction", print: "outcome vs receipt + correction", count: closed.length,
      items: closed.slice(0, 4).map((r) => item(r)), empty: "Nothing closed yet. Offer, reject, or withdrawn lands here and scores the prediction." },
  ]

  const data: LaneData = {
    stages,
    sources: sources.map((s) => ({ key: s.key, label: s.label, adapter: s.adapter, status: s.status, lastRunAt: s.lastRunAt?.toISOString() ?? null, pollWindow: s.pollWindow, note: s.note })),
    requests: requests.map((r) => ({ fromDate: r.fromDate, toDate: r.toDate, status: r.status, rowsAdded: r.rowsAdded, requestedAt: r.requestedAt.toISOString(), note: r.note })),
    outcomes: outcomes.map((o) => ({ jobid: o.jobid, company: o.job.company, fate: o.fate, predicted: fmt(o.predictedComposite), actual: o.actualNote ?? o.fate, honesty: o.honestyLabel ?? "—" })),
    corrections: corrections.map((c) => ({ learned: c.learned, pattern: c.pattern, avoid: c.avoid, logic: c.logic })),
    live: new Date().toISOString(),
  }

  return <LaneSurfaces data={data} />
}
