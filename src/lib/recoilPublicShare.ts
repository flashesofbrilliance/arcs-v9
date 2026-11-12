import fs from "node:fs"
import path from "node:path"

// One-report public shares for /recoil/<id> (runtime/recoil/public-shares.json).
// A listed report opens without sign-in. The public view is an ALLOW-LIST
// projection, never the internal war room minus a strip list (PR 2194 showed a
// signed-out reader everything its ten markers missed): only page blocks tagged
// audience "both" survive, plus the page header and a few meta fields. Every
// other top-level key (beliefs, insights, redaction_policy, ...) is dropped,
// because the war-room screen's Deeper Strata fold renders unknown keys raw.
// strip_markers can only remove more. An entry without a `gauntlet` reference
// (the counterpart-gauntlet run that cleared it) is not a share at all.
// scripts/recoil_public_share_gate.py scans this projection in pre-commit.
export type PublicShare = {
  approved: string
  gauntlet: string
  strip_markers?: string[]
}

export function publicShare(reportId: string): PublicShare | null {
  try {
    const file = path.join(process.cwd(), "runtime", "recoil", "public-shares.json")
    const all = JSON.parse(fs.readFileSync(file, "utf-8")) as Record<string, unknown>
    return validShare(all[reportId])
  } catch {
    return null
  }
}

export function validShare(entry: unknown): PublicShare | null {
  if (!entry || typeof entry !== "object" || Array.isArray(entry)) return null
  const e = entry as Record<string, unknown>
  if (typeof e.approved !== "string" || !e.approved.trim()) return null
  if (typeof e.gauntlet !== "string" || !e.gauntlet.trim()) return null
  if (e.strip_markers !== undefined && !Array.isArray(e.strip_markers)) return null
  return entry as PublicShare
}

type Rec = Record<string, unknown>
const isRec = (v: unknown): v is Rec => typeof v === "object" && v !== null && !Array.isArray(v)

const META_KEEP = ["report_id", "date", "counterpart", "company"]
const HEADER_KEEP = ["eyebrow", "title", "sub"]

// Drop every nested object tagged audience "internal" and every authoring note (_doc, _METHOD).
function scrub(v: unknown): unknown {
  if (Array.isArray(v)) return v.filter((el) => !(isRec(el) && el.audience === "internal")).map(scrub)
  if (isRec(v)) {
    const out: Rec = {}
    for (const [k, x] of Object.entries(v)) {
      if (k.startsWith("_")) continue
      if (isRec(x) && x.audience === "internal") continue
      out[k] = scrub(x)
    }
    return out
  }
  return v
}

// Remove the smallest string that holds a marker (extra subtraction on top of the allow-list).
function strip(v: unknown, markers: string[]): unknown {
  if (!markers.length) return v
  const hit = (s: string) => markers.some((m) => s.includes(m))
  if (Array.isArray(v)) return v.filter((el) => !(typeof el === "string" && hit(el))).map((el) => strip(el, markers))
  if (isRec(v)) {
    const out: Rec = {}
    for (const [k, x] of Object.entries(v)) {
      if (typeof x === "string" && hit(x)) continue
      out[k] = strip(x, markers)
    }
    return out
  }
  return v
}

export function applyPublicShare<T>(data: T, share: PublicShare): T {
  const raw = (isRec(data) ? data : {}) as Rec
  const meta: Rec = {}
  if (isRec(raw.meta)) for (const k of META_KEEP) if (typeof raw.meta[k] === "string") meta[k] = raw.meta[k]
  const page = isRec(raw.page) ? raw.page : {}
  const blocks = (Array.isArray(page.blocks) ? page.blocks : []).filter((b) => isRec(b) && b.audience === "both")
  const used = new Set(blocks.map((b) => (b as Rec).tab))
  const header: Rec = {}
  if (isRec(page.header)) for (const k of HEADER_KEEP) if (typeof page.header[k] === "string") header[k] = page.header[k]
  const tabs = (Array.isArray(page.tabs) ? page.tabs : []).filter((t) => isRec(t) && used.has(t.id))
  const out: Rec = {
    meta,
    page: { ...(typeof page.layout === "string" ? { layout: page.layout } : {}), header, tabs, blocks: scrub(blocks) },
  }
  return strip(out, share.strip_markers ?? []) as T
}
