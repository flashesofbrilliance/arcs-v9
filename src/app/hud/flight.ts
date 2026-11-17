// HUD v2 flight (row hud-atlas-v2-flight): pure geometry and fidelity for an arcs.atlas.v2 file.
// No React, so tests/unit/hud-flight.test.ts can run it. Spec: _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md
// section 4.5, with Zach's answer to section 8 question 1 (2026-11-12): "720 degrees" is a 360 degree orbit
// in space plus a full scrub in time, forward and back.
//
// Contract read from runtime/specs/arcs-atlas-v2.schema.json: nodes and edges carry s (seconds into the
// call); edges point from the newer node to the older one and s is when the edge was cut; beliefs sit at
// s = 0; a node with t null has no s and no edges. The fidelity rule is the file's own `fidelity` copy of
// x-fidelity: this module applies it, it never sets a threshold of its own.

export type Grade = { letter?: string; basis?: string; n?: number }
export type FNode = { id: string; tier: number; kind: string; t: string | null; s?: number; label: string; ref: string; grade?: Grade }
export type FEdge = { id: string; from: string; to: string; kind: string; t: string; s: number; evidence: string[]; grade: Grade }
export type FKairos = { id: string; node: string; atom: string; t: string; s: number; what: string; from: number | null; to: number | null; grade: Grade }
export type FTier = { name: string; kind?: string; docs: number; render?: string }
export type Rule = { countable_letters: string[]; sharp_letters: string[]; degraded_min_edges: number; sharp_min_edges: number; sharp_min_share: number }
export type Flight = { title: string; tiers: FTier[]; nodes: FNode[]; edges: FEdge[]; kairos: FKairos[]; rule: Rule; unanchored: string[]; maxS: number }
export type Render = "SHARP" | "DEGRADED" | "GRAIN" | "FLAT"
export type TierRead = { render: Render; edges: number; sharp: number; nodes: number }

const arr = <T>(v: unknown): T[] => (Array.isArray(v) ? (v as T[]) : [])
const num = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : undefined)
const s40 = (v: unknown, n = 80) => (typeof v === "string" ? v.slice(0, n) : "")

// Returns null for anything that is not a v2 graph: a v1 file keeps the terrace-only loader.
export function toFlight(d: unknown): Flight | null {
  const a = d as Record<string, unknown> | null
  if (!a || a.schema !== "arcs.atlas.v2" || !Array.isArray(a.tiers) || !a.fidelity) return null
  const r = a.fidelity as Record<string, unknown>
  const rule: Rule = {
    countable_letters: arr<string>(r.countable_letters),
    sharp_letters: arr<string>(r.sharp_letters),
    degraded_min_edges: num(r.degraded_min_edges) ?? 0,
    sharp_min_edges: num(r.sharp_min_edges) ?? 0,
    sharp_min_share: num(r.sharp_min_share) ?? 1,
  }
  const tiers = arr<Record<string, unknown>>(a.tiers).slice(0, 12).map((t) => ({ name: s40(t.name, 24) || "tier", kind: s40(t.kind, 12), docs: num(t.docs) ?? 0, render: s40(t.render, 10) }))
  const nodes = arr<FNode>(a.nodes).filter((n) => n && typeof n.id === "string" && num(n.tier) !== undefined && n.tier < tiers.length)
  const ids = new Set(nodes.map((n) => n.id))
  const edges = arr<FEdge>(a.edges).filter((e) => e && ids.has(e.from) && ids.has(e.to) && num(e.s) !== undefined)
  const kairos = arr<FKairos>(a.kairos).filter((k) => k && ids.has(k.node) && num(k.s) !== undefined).slice().sort((x, y) => x.s - y.s)
  const times = [...nodes.map((n) => num(n.s) ?? 0), ...edges.map((e) => e.s), ...kairos.map((k) => k.s)]
  return { title: s40(a.title, 120) || "Atlas", tiers, nodes, edges, kairos, rule, unanchored: arr<string>(a.unanchored).map((u) => s40(u, 160)), maxS: Math.max(0, ...times) }
}

// What exists at time s: nodes with no s (unanchored) are shown at every time; the rest appear at their s.
export const nodeAt = (n: FNode, s: number) => n.s === undefined || n.s <= s
export const edgeAt = (e: FEdge, s: number) => e.s <= s

// The x-fidelity rule at time s. Only cross-tier edges cut a facet, so only they count (spec 4.5).
export function tierReads(f: Flight, s: number): TierRead[] {
  const tierOf = new Map(f.nodes.map((n) => [n.id, n.tier]))
  const out = f.tiers.map(() => ({ edges: 0, sharp: 0, nodes: 0 }))
  for (const n of f.nodes) if (nodeAt(n, s)) out[n.tier].nodes++
  for (const e of f.edges) {
    if (!edgeAt(e, s)) continue
    const a = tierOf.get(e.from)!, b = tierOf.get(e.to)!
    const L = e.grade?.letter ?? "NS"
    if (a === b || !f.rule.countable_letters.includes(L)) continue
    const sharp = f.rule.sharp_letters.includes(L) ? 1 : 0
    for (const t of [a, b]) { out[t].edges++; out[t].sharp += sharp }
  }
  return out.map((o) => {
    let render: Render
    if (!o.nodes) render = "FLAT"
    else if (o.edges < f.rule.degraded_min_edges) render = "GRAIN"
    else if (o.edges >= f.rule.sharp_min_edges && o.sharp / o.edges >= f.rule.sharp_min_share) render = "SHARP"
    else render = "DEGRADED"
    return { render, ...o }
  })
}

// Count of facets cut at time s: the visible proof of work.
export const facetsAt = (f: Flight, s: number) => {
  const tierOf = new Map(f.nodes.map((n) => [n.id, n.tier]))
  return f.edges.filter((e) => edgeAt(e, s) && tierOf.get(e.from) !== tierOf.get(e.to)).length
}

// ---- Geometry. A terrace is a square slab; node i of k on a terrace sits on a ring on its top face.
// The camera orbits around the vertical axis (yaw, a full 360 and wrapping) at a fixed pitch.
export type P3 = [number, number, number]
export type P2 = { x: number; y: number; z: number }
export const PITCH = 0.5

export const wrapDeg = (d: number) => ((d % 360) + 360) % 360

export function terrace(i: number, n: number) {
  const half = 1 - (0.62 * i) / Math.max(n - 1, 1)
  return { half, y: i * 0.34, top: i * 0.34 + 0.22 }
}

export function project([x, y, z]: P3, yawDeg: number, scale: number, cx: number, cy: number, pitch = PITCH): P2 {
  const a = (yawDeg * Math.PI) / 180
  const xr = x * Math.cos(a) - z * Math.sin(a)
  const zr = x * Math.sin(a) + z * Math.cos(a)
  return { x: cx + xr * scale, y: cy - y * Math.cos(pitch) * scale + zr * Math.sin(pitch) * scale, z: zr }
}

export function nodePoints(f: Flight): Map<string, P3> {
  const byTier = f.tiers.map((_, i) => f.nodes.filter((n) => n.tier === i))
  const m = new Map<string, P3>()
  byTier.forEach((list, i) => {
    const { half, top } = terrace(i, f.tiers.length)
    // On the exposed ledge: midway between this terrace's rim and the one above (the apex uses its own lid).
    const r = i < f.tiers.length - 1 ? (half + terrace(i + 1, f.tiers.length).half) / 2 : half * 0.6
    list.forEach((n, j) => {
      const th = (2 * Math.PI * j) / Math.max(list.length, 1) + i * 0.7
      m.set(n.id, [Math.cos(th) * r, top, Math.sin(th) * r])
    })
  })
  return m
}

// A facet is the triangle an edge cuts: its two node points plus the upper node's bearing carried down
// to the lower terrace's rim, so the face lies on the ziggurat's flank rather than floating in the air.
export function facet(a: P3, b: P3, lowerHalf: number): P3[] {
  const [lo, hi] = a[1] <= b[1] ? [a, b] : [b, a]
  const th = Math.atan2(hi[2], hi[0])
  return [lo, hi, [Math.cos(th) * lowerHalf, lo[1], Math.sin(th) * lowerHalf]]
}

export const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`
