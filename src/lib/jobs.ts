import fs from "node:fs"
import path from "node:path"
import type { NextRequest } from "next/server"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

// jobs.arcs.care — the job-search board. Internal, single-user surface:
// the signed-in session must be an admin (ADMIN_EMAILS), or the caller must
// present the pipeline token (the scheduled task and the forge watcher write
// scores and forge status without a browser session). Dev passes through,
// matching src/lib/admin.ts doctrine.

export type Caller = { kind: "admin"; email: string } | { kind: "pipeline" } | { kind: "dev" } | null

export async function callerFor(req: NextRequest): Promise<Caller> {
  const token = req.headers.get("x-jobs-token")
  const expected = process.env.JOBS_PIPELINE_TOKEN
  if (token && expected && token === expected) return { kind: "pipeline" }
  const session = await auth()
  if (isAdmin(session)) return { kind: "admin", email: session!.user!.email! }
  if (process.env.NODE_ENV !== "production") return { kind: "dev" }
  return null
}

export async function pageViewerAllowed(): Promise<boolean> {
  if (process.env.NODE_ENV !== "production") return true
  const session = await auth()
  return isAdmin(session)
}

// The rubric is data: runtime/specs/target-role-scan.json (archetypes, quads,
// filter, dims, gates, bands, tiers). Read at request time so a docs-only
// change to the spec does not need a rebuild.
export type ScanSpec = {
  version: string
  archetypes: { id: string; title: string; rail: string; titles: string[] }[]
  quads: { id: string; label: string; headline: string; dims: string[]; proof: { company: string | null; claim: string } }[]
  rubric: {
    dims: { key: string; label: string; weight: number; anchor0: string; anchor3: string }[]
    max: number
    gates: string[]
    bands: { pursue: number; consider: number }
    board_cutoff: number
    tiers: { t1: number; t2: number; t3: number }
  }
}

let cached: { spec: ScanSpec; mtime: number } | null = null
export function loadScanSpec(): ScanSpec | null {
  const p = path.join(process.cwd(), "runtime", "specs", "target-role-scan.json")
  try {
    const mtime = fs.statSync(p).mtimeMs
    if (cached && cached.mtime === mtime) return cached.spec
    const spec = JSON.parse(fs.readFileSync(p, "utf8")) as ScanSpec
    cached = { spec, mtime }
    return spec
  } catch {
    return null
  }
}

export const FORGE_STATUSES = ["queued", "gathering", "grading", "rendering", "built", "live"] as const
export type ForgeStatus = (typeof FORGE_STATUSES)[number]
export const WHY_TAGS = ["comp", "location", "role shape", "seniority", "culture", "company", "timing", "other"] as const

export function tierOf(composite: number | null | undefined, spec: ScanSpec | null): 1 | 2 | 3 | null {
  if (composite == null) return null
  const t = spec?.rubric.tiers ?? { t1: 0.8, t2: 0.7, t3: 0.58 }
  if (composite >= t.t1) return 1
  if (composite >= t.t2) return 2
  if (composite >= t.t3) return 3
  return null
}
