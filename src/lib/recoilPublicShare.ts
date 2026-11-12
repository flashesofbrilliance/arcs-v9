import fs from "node:fs"
import path from "node:path"

// One-report public shares for /recoil/<id> (runtime/recoil/public-shares.json).
// A listed report opens without sign-in, with named lines stripped server-side so
// they never reach the client payload. Everything else on /recoil stays admin-only.
export type PublicShare = {
  strip_markers: string[]
  strip_block_types?: string[]
  drop_kinematic_series?: boolean
}

export function publicShare(reportId: string): PublicShare | null {
  try {
    const file = path.join(process.cwd(), "runtime", "recoil", "public-shares.json")
    const all = JSON.parse(fs.readFileSync(file, "utf-8")) as Record<string, unknown>
    const entry = all[reportId]
    if (!entry || typeof entry !== "object" || !Array.isArray((entry as PublicShare).strip_markers)) return null
    return entry as PublicShare
  } catch {
    return null
  }
}

// Drop the smallest unit that holds a marker: a string in a list, a whole table
// row (an array under "rows", so columns never shift), a list item object whose
// marker is not inside a deeper list, or a string field.
function strip(value: unknown, markers: string[], key = ""): unknown {
  const has = (v: unknown) => markers.some((m) => JSON.stringify(v).includes(m))
  if (Array.isArray(value)) {
    return value
      .filter((el) => {
        if (!has(el)) return true
        if (typeof el === "string") return false
        if (key === "rows" && Array.isArray(el)) return false
        if (el && typeof el === "object" && !Array.isArray(el)) return deeper(el, markers)
        return true
      })
      .map((el) => strip(el, markers))
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(value)) {
      if (k.startsWith("_")) continue // authoring notes (_doc, _METHOD, _TEMPLATE) never reach a public payload
      if (typeof v === "string" && markers.some((m) => v.includes(m))) continue
      out[k] = strip(v, markers, k)
    }
    return out
  }
  return value
}

// True when every marker in this object sits inside one of its lists, so
// recursion can remove just those lines and keep the object.
function deeper(obj: object, markers: string[]): boolean {
  return !Object.values(obj).some((v) => typeof v === "string" && markers.some((m) => v.includes(m)))
}

export function applyPublicShare<T>(data: T, share: PublicShare): T {
  const raw = JSON.parse(JSON.stringify(data)) as Record<string, unknown>
  const page = raw.page as { blocks?: { type?: string }[] } | undefined
  if (page?.blocks && share.strip_block_types?.length) {
    page.blocks = page.blocks.filter((b) => !share.strip_block_types!.includes(b.type ?? ""))
  }
  // Source ids (Gmail threads, Granola notes) and twin settings are internal; the
  // page renders none of them unless a provenance block asks, and then only on
  // the admin view.
  if (raw.meta && typeof raw.meta === "object") {
    const { closed_call: _c, provenance: _p, external_sets: _e, ...meta } = raw.meta as Record<string, unknown>
    void _c; void _p; void _e
    raw.meta = meta
  }
  if (share.drop_kinematic_series && raw.kinematic_series && typeof raw.kinematic_series === "object") {
    raw.kinematic_series = { ...(raw.kinematic_series as object), series: [] }
  }
  return strip(raw, share.strip_markers) as T
}
