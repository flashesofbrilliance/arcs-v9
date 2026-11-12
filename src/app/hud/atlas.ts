import type { ZigTier } from "@/organisms/Scope"

// Atlas file contract for the HUD ziggurat loader (pure, no React, so the unit tests can run it).
// arcs.atlas.v1 (jobs.arcs.care/atlas) and arcs.atlas.v2 (runtime/specs/arcs-atlas-v2.schema.json,
// exported by scripts/recoil_stage_j5.py) both carry tiers with name, docs and gate, so both load
// their terraces here. The v2 graph (edges, time scrub, kairos) is drawn by the HUD v2 flight view
// (row hud-atlas-v2-flight), not by this loader.

export type AtlasTier = { name?: unknown; docs?: unknown; gate?: unknown }
export type Atlas = { schema: string; built?: unknown; gate?: unknown; tiers: AtlasTier[] }

export const ATLAS_SCHEMAS = ["arcs.atlas.v1", "arcs.atlas.v1.public", "arcs.atlas.v2"]

const str = (v: unknown, n: number) => (typeof v === "string" ? v.slice(0, n) : "")

export function parseAtlas(text: string): { atlas: Atlas } | { error: string } {
  let d: Atlas
  try { d = JSON.parse(text) } catch { return { error: "Not valid JSON." } }
  if (!d || !ATLAS_SCHEMAS.includes(d.schema) || !Array.isArray(d.tiers)) return { error: "Not an arcs.atlas.v1 or v2 object." }
  if (!d.tiers.length) return { error: "The atlas has no tiers." }
  return { atlas: d }
}

export function toZigTiers(d: Atlas): ZigTier[] {
  return d.tiers.slice(0, 12).map((t) => ({
    name: str(t.name, 24) || "tier",
    gate: t.gate === "fail" ? "fail" : t.gate === "warn" ? "warn" : "pass",
    docs: Array.isArray(t.docs) ? t.docs.length : Number(t.docs) || 0,
  }))
}
