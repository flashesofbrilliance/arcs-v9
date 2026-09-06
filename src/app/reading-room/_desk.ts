// The Desk — server-side data access for /reading-room (brief: _SPECS/desk-shape-brief-v1.md).
// Intents + shelf slots are DATA (runtime/specs/reading-room-manifest.json), never hardcoded
// here, so a second tool can consume the same shelf. Freshness comes from the atlas cache
// manifest (_ARTIFACTS/atlas/cache-manifest.spec.md); a MISSING manifest degrades to "unknown".
import fs from "node:fs"
import path from "node:path"
import { notFound, redirect } from "next/navigation"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

export const DESK_MANIFEST = path.join(process.cwd(), "runtime", "specs", "reading-room-manifest.json")
export const CACHE_MANIFEST = path.join(process.cwd(), "_ARTIFACTS", "atlas", "cache-manifest.json")

export interface ShelfEntry {
  tenant: string
  question: string
  work: string
  built: boolean
  frame?: string
  render?: string
  domains: string[]
}

export interface DeskManifest {
  route: string
  shelf: ShelfEntry[]
}

interface CacheSlice {
  domain: string
  node_count: number
  graded_at: string
  fresh: boolean
  dirty_files?: string[]
}

interface CacheManifest {
  generated?: string
  slices: CacheSlice[]
}

export interface Freshness {
  graded: string          // "YYYY-MM-DD" or "unknown"
  dirty: boolean
  known: boolean
}

export interface Readout {
  nodeCount: number | null
  lastGraded: string      // "YYYY-MM-DD" or "unknown"
  dirtySlices: number | null
}

// Same doctrine as /recoil: a session is always required; isAdmin() (src/lib/admin.ts) is
// fail-closed in prod when ADMIN_EMAILS is unset and passes through only in dev. No NODE_ENV
// shortcut here, so a self-hosted server started with NODE_ENV=development still needs a session.
// No session -> sign in; signed-in non-admin -> 404 (do not reveal the room).
export async function gateDesk(next: string): Promise<void> {
  const session = await auth()
  if (!session?.user?.email) redirect(`/compass?next=${encodeURIComponent(next)}`)
  if (!isAdmin(session)) notFound()
}

// A malformed or missing desk manifest degrades to an empty shelf (the page renders the readout
// line with "shelf manifest unreadable"), never a 500. Every slot is normalized: a frame is only
// honored when it is a same-origin /api/reading-room/ path, so a bad merge cannot point the
// tenant iframe anywhere else.
export const FRAME_PREFIX = "/api/reading-room/"

export function readDesk(): DeskManifest & { error?: string } {
  let raw: Partial<DeskManifest>
  try {
    raw = JSON.parse(fs.readFileSync(DESK_MANIFEST, "utf-8")) as Partial<DeskManifest>
  } catch (e) {
    return { route: "/reading-room", shelf: [], error: "shelf manifest unreadable" }
  }
  const shelf: ShelfEntry[] = (Array.isArray(raw.shelf) ? raw.shelf : [])
    .filter((s): s is ShelfEntry => !!s && typeof s === "object" && typeof (s as ShelfEntry).tenant === "string")
    .map((s) => {
      const frame = typeof s.frame === "string" && s.frame.startsWith(FRAME_PREFIX) && !s.frame.includes("..") ? s.frame : undefined
      return {
        tenant: s.tenant.replace(/[^a-z0-9-]/gi, ""),
        question: typeof s.question === "string" ? s.question : "",
        work: typeof s.work === "string" ? s.work : s.tenant,
        built: s.built === true && !!frame,
        frame,
        render: typeof s.render === "string" ? s.render : undefined,
        domains: Array.isArray(s.domains) ? s.domains.filter((d): d is string => typeof d === "string") : [],
      }
    })
  const route = typeof raw.route === "string" && raw.route.startsWith("/") ? raw.route : "/reading-room"
  return { route, shelf }
}

export function readCache(): CacheManifest | null {
  try {
    const raw = JSON.parse(fs.readFileSync(CACHE_MANIFEST, "utf-8")) as CacheManifest
    return Array.isArray(raw?.slices) ? raw : null
  } catch {
    return null
  }
}

function isDirty(s: CacheSlice): boolean {
  return s.fresh === false || (Array.isArray(s.dirty_files) && s.dirty_files.length > 0)
}

// Most recent graded_at across the slot's domains, plus dirty if any of those slices is dirty.
export function freshnessFor(cache: CacheManifest | null, domains: string[]): Freshness {
  if (!cache) return { graded: "unknown", dirty: false, known: false }
  const slices = cache.slices.filter((s) => domains.includes(s.domain))
  if (slices.length === 0) return { graded: "unknown", dirty: false, known: false }
  const graded = slices.map((s) => s.graded_at ?? "").sort().at(-1) || "unknown"
  return { graded, dirty: slices.some(isDirty), known: graded !== "unknown" }
}

export function readoutFor(cache: CacheManifest | null): Readout {
  if (!cache) return { nodeCount: null, lastGraded: "unknown", dirtySlices: null }
  const nodeCount = cache.slices.reduce((n, s) => n + (Number(s.node_count) || 0), 0)
  const lastGraded = cache.slices.map((s) => s.graded_at ?? "").sort().at(-1) || "unknown"
  return { nodeCount, lastGraded, dirtySlices: cache.slices.filter(isDirty).length }
}
