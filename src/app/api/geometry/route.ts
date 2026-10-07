import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

export const dynamic = "force-dynamic"

// JTBD: feed the decision-geometry explorer with real receipts and their histories (lineage,
//       outcomes, briefs, parsed geometry) at earned fidelity, so the explorer renders the corpus
//       instead of a hand-typed dataset.
// TOOL-FIT: a dedicated read route over Receipt + Outcome + Brief + PrepSession, over reusing
//       /api/history. History returns seeds only (parentId null), caps at 50, always carries the
//       question text, and has no lineage depth, no rawResponse geometry parse and no outcome join.
//       The explorer needs the whole lineage and a text-free public shape.
// EX-ANTE: predict this fits because /api/receipts/ripe already reads the caller's own rows the
//       same way and the knowledge-lattice explorer already consumes one flat JSON document.
//       Scored ex-post by whether a second explorer (ziggurat, almanac) can reuse the feed unchanged.
//
// Earned fidelity, decided server-side (WORLD.md render scale: never more resolution than the
// data deserves, and here never more than the viewer has earned):
//   admin  (ADMIN_EMAILS allowlist; prod fail-closed, dev passthrough) -> every receipt, text included
//   owner  (any signed-in user)                                       -> the caller's own receipts, text included
//   public (anonymous; GEOMETRY_PUBLIC unset or "true")               -> every receipt, TEXT-FREE:
//          no question, no true north, no entity, no tributary prompts, no receipt or user ids,
//          time at day granularity. Same disclosure class as the status page counts.
//          Set GEOMETRY_PUBLIC=false to return 401 to anonymous callers instead.
// NOTOMATION: this is a read. It computes nothing about the decision itself; tiers, cells and
// basins are computed client-side from the stated rules so the explorer can show its work.

type Fidelity = "admin" | "owner" | "public"

const KAIROS_WORDS = ["OPEN", "CLOSED", "CLOSING", "CONDITIONAL", "URGENT", "ACUTE", "LATENT", "FORCED", "DEFERRED", "CRITICAL", "UNCERTAIN"]

function parseJson<T>(s: string | null | undefined): T | null {
  if (!s) return null
  try { return JSON.parse(s) as T } catch { return null }
}

// reasoning.geometry is free text written by the model (see the compass OUTPUT SHAPE). Parse the
// leading token only; keep the text for owner/admin fidelity, drop it for public.
function parseKairos(s: unknown): { st: string; txt: string | null } | null {
  if (typeof s !== "string" || !s.trim()) return null
  const up = s.trim().toUpperCase()
  const st = KAIROS_WORDS.find((w) => up.startsWith(w)) ?? (up.startsWith("N/A") ? "NA" : "OTHER")
  return { st, txt: s.trim().slice(0, 160) }
}
function parseAltitude(s: unknown): { lo: number; hi: number; txt: string | null } | null {
  if (typeof s !== "string") return null
  const m = s.match(/L(\d)(?:\s*[–—-]\s*L?(\d))?/)
  if (!m) return null
  const lo = Number(m[1]); const hi = m[2] ? Number(m[2]) : lo
  return { lo: Math.min(lo, hi), hi: Math.max(lo, hi), txt: s.trim().slice(0, 120) }
}
function parseReversibility(s: unknown): { v: number; txt: string | null } | null {
  if (typeof s !== "string") return null
  const m = s.match(/^\s*([01](?:\.\d+)?)/)
  if (!m) return null
  return { v: Number(m[1]), txt: s.trim().slice(0, 120) }
}

type Lens = { cl: number; cv: number; co: number; cq: number; ca: number }
function parseLens(raw: Record<string, unknown> | null, col: string | null): Lens | null {
  const src = (raw?.nci_by_lens as Record<string, unknown> | undefined) ?? parseJson<Record<string, unknown>>(col) ?? null
  if (!src) return null
  const n = (k: string) => (typeof src[k] === "number" ? (src[k] as number) : null)
  const cl = n("clarity"), cv = n("conviction"), co = n("coherence"), cq = n("consequence"), ca = n("cadence")
  if ([cl, cv, co, cq, ca].some((x) => x === null)) return null
  return { cl: cl!, cv: cv!, co: co!, cq: cq!, ca: ca! }
}

function queryRows(where: { userId?: string }) {
  return prisma.receipt.findMany({
    where,
    orderBy: { createdAt: "asc" },
    select: {
      id: true, userId: true, sessionId: true, parentId: true, parentTributaryIndex: true, version: true,
      createdAt: true, status: true, surface: true, provenance: true, validationState: true,
      decision: true, sharpQuestion: true, trueNorth: true, entity: true, whyBullets: true,
      nciScore: true, nciByLens: true, coherencePct: true, isSatoshi: true, clarityMode: true,
      mode: true, doorClass: true, macroTags: true, stakes: true, horizon: true, window: true,
      protecting: true, horizonLocked: true, driftState: true,
      yPolarity: true, yConviction: true, yStability: true, yState: true, yConditions: true,
      gradientMagnitude: true, flowTopology: true, manifoldCurvature: true, renderResolution: true,
      loki: true, bar: true, court: true, courtVerdict: true, nciSelfGrade: true, atgTributaries: true,
      rawResponse: true, reminderDate: true, fated: true, yConvictionPrev: true, yDeltaTrigger: true, reviewDate: true, nciGrade: true,
      forkPath: true, mergedFrom: true, batonId: true, yOverride: true, dewyVector: true,
      brief: { select: { id: true } },
      outcome: { select: { matched: true, regretScore: true, loggedAt: true, synthetic: true } },
      prep: { select: { stakes: true, horizon: true, confidence: true, adversarialInput: true } },
    },
  })
}

export async function GET(req: NextRequest) {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const admin = process.env.NODE_ENV !== "production" ? true : isAdmin(session)
  const publicOn = process.env.GEOMETRY_PUBLIC !== "false"

  let fidelity: Fidelity
  if (admin) fidelity = "admin"
  else if (userId) fidelity = "owner"
  else if (publicOn) fidelity = "public"
  else return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  // ?scope=own lets an admin look at their own corpus only (the founder's view of the founder).
  const scopeOwn = req.nextUrl.searchParams.get("scope") === "own" && userId

  // A database the route cannot reach (bad credentials, missing migration) is an honest 503 with a
  // code, never an unhandled 500: the explorer renders the no-feed state from the body.
  let rows: Awaited<ReturnType<typeof queryRows>>
  try { rows = await queryRows(fidelity === "owner" || scopeOwn ? { userId: userId! } : {}) }
  catch (err) {
    const code = (err as { code?: string })?.code ?? "UNKNOWN"
    console.error("[geometry] feed unavailable", code)
    return NextResponse.json({ error: "feed unavailable", code }, { status: 503 })
  }

  // Lineage depth (0 = seed) and per-parent child counts, computed over the fetched set.
  const byId = new Map(rows.map((r) => [r.id, r]))
  const depthOf = new Map<string, number>()
  const depth = (id: string): number => {
    if (depthOf.has(id)) return depthOf.get(id)!
    const r = byId.get(id)
    const d = r?.parentId && byId.has(r.parentId) ? depth(r.parentId) + 1 : 0
    depthOf.set(id, d)
    return d
  }
  const kids = new Map<string, number>()
  for (const r of rows) if (r.parentId) kids.set(r.parentId, (kids.get(r.parentId) ?? 0) + 1)

  // Public fidelity never exposes ids: receipts, sessions and users become dense indexes.
  const idx = new Map(rows.map((r, i) => [r.id, i]))
  const sessIdx = new Map<string, number>()
  const userIdx = new Map<string, number>()
  for (const r of rows) {
    if (!sessIdx.has(r.sessionId)) sessIdx.set(r.sessionId, sessIdx.size)
    if (r.userId && !userIdx.has(r.userId)) userIdx.set(r.userId, userIdx.size)
  }
  const text = fidelity !== "public"

  const receipts = rows.map((r, i) => {
    const raw = parseJson<Record<string, unknown>>(r.rawResponse)
    const reasoning = (raw?.reasoning as Record<string, unknown> | undefined) ?? {}
    const geo = (reasoning.geometry as Record<string, unknown> | undefined) ?? {}
    const courtArr = Array.isArray(reasoning.court) ? (reasoning.court as Array<{ verdict?: string }>) : parseJson<Array<{ verdict?: string }>>(r.court) ?? []
    const courtV = { pass: 0, tension: 0, block: 0 }
    for (const c of courtArr) {
      const v = String(c?.verdict ?? "").toUpperCase()
      if (v === "PASS") courtV.pass++; else if (v === "TENSION") courtV.tension++; else if (v === "BLOCK") courtV.block++
    }
    const advisors = (reasoning.advisors as Record<string, unknown> | undefined) ?? {}
    const bar = parseJson<Record<string, unknown>>(r.bar)
    const why = parseJson<string[]>(r.whyBullets)
    const trib = parseJson<Array<{ type?: string; label?: string; prompt?: string }>>(r.atgTributaries)
    const selfGrade = parseJson<Record<string, unknown>>(r.nciSelfGrade)
    const kairos = parseKairos(geo.kairos)
    const alt = parseAltitude(geo.altitude)
    const rev = parseReversibility(geo.reversibility)
    const paths = Array.isArray(reasoning.paths) ? (reasoning.paths as Array<{ status?: string }>) : []
    const fated = (reasoning.fated as Record<string, unknown> | undefined) ?? parseJson<Record<string, unknown>>(r.fated) ?? {}
    const fatedN = ["facts", "assumptions", "tradeoffs", "emotions", "direction"].filter((k) => typeof fated[k] === "string" && (fated[k] as string).trim()).length
    const breakdown = (reasoning.nci_breakdown as Record<string, unknown> | undefined) ?? {}
    const dragsN = Array.isArray(breakdown.drags) ? (breakdown.drags as unknown[]).length : 0
    const anchorsN = Array.isArray(breakdown.anchors) ? (breakdown.anchors as unknown[]).length : 0

    const base = {
      i,
      t: text ? r.createdAt.toISOString() : r.createdAt.toISOString().slice(0, 10),
      s: text ? r.sessionId : sessIdx.get(r.sessionId)!,
      u: r.userId ? userIdx.get(r.userId)! : null,
      p: r.parentId && idx.has(r.parentId) ? idx.get(r.parentId)! : null,
      d: depth(r.id),
      k: kids.get(r.id) ?? 0,
      ti: r.parentTributaryIndex,
      v: r.version,
      st: r.status, surf: r.surface, prov: r.provenance, val: r.validationState,
      nci: r.nciScore, lens: parseLens(raw, r.nciByLens), coh: r.coherencePct, sat: r.isSatoshi, cm: r.clarityMode,
      mode: r.mode, door: r.doorClass, macros: parseJson<string[]>(r.macroTags) ?? [],
      stakes: r.stakes ? r.stakes.toUpperCase() : null, hor: r.horizon, win: r.window,
      prot: parseJson<string[]>(r.protecting) ?? [], lock: r.horizonLocked, drift: r.driftState,
      y: { pol: r.yPolarity, conv: r.yConviction, stab: r.yStability, state: r.yState },
      ycond: (parseJson<unknown[]>(r.yConditions) ?? []).length,
      grad: r.gradientMagnitude, topo: r.flowTopology, curv: r.manifoldCurvature, rr: r.renderResolution,
      geo: {
        kairos: kairos ? { st: kairos.st, txt: text ? kairos.txt : null } : null,
        alt: alt ? { lo: alt.lo, hi: alt.hi, txt: text ? alt.txt : null } : null,
        rev: rev ? { v: rev.v, txt: text ? rev.txt : null } : null,
        trig: text && typeof geo.mode_trigger === "string" ? (geo.mode_trigger as string).slice(0, 120) : null,
        on: Array.isArray(geo.macros_on) ? (geo.macros_on as string[]) : [],
        off: Array.isArray(geo.macros_off) ? (geo.macros_off as string[]) : [],
      },
      court: courtV,
      bayes: typeof advisors.bayesian_risk_pct === "number" ? (advisors.bayesian_risk_pct as number) : null,
      lokiN: r.loki ? 1 : 0,
      barN: bar ? Object.keys(bar).length : 0,
      whyN: why ? why.length : 0,
      tribN: trib ? trib.length : 0,
      pathsN: paths.length,
      pathsBlocked: paths.filter((p) => String(p?.status ?? "") === "blocked").length,
      pathsSel: paths.filter((p) => String(p?.status ?? "") === "selected").length,
      fatedN, dragsN, anchorsN,
      courtN: courtArr.length,
      yPrev: r.yConvictionPrev, yTrig: !!r.yDeltaTrigger, rev: !!r.reviewDate, grade: !!r.nciGrade,
      fork: !!r.forkPath, merged: r.mergedFrom !== "[]", baton: !!r.batonId, yov: r.yOverride,
      dewy: !!r.dewyVector, sq: !!r.sharpQuestion, advN: [advisors.loki_challenge, advisors.loki_counter, advisors.consensus].filter((x) => typeof x === "string" && (x as string).trim()).length,
      self: selfGrade ? { f: !!selfGrade.factual, s: !!selfGrade.sources, h: !!selfGrade.honesty, a: !!selfGrade.action } : null,
      brief: !!r.brief,
      out: r.outcome ? { m: r.outcome.matched, r: r.outcome.regretScore, at: r.outcome.loggedAt.toISOString().slice(0, 10), syn: r.outcome.synthetic } : null,
      prep: r.prep ? { stakes: r.prep.stakes, hor: r.prep.horizon, conf: r.prep.confidence, adv: !!r.prep.adversarialInput } : null,
      rem: !!r.reminderDate,
    }
    if (!text) return base
    return {
      ...base,
      id: r.id,
      q: (r.sharpQuestion || r.decision || "").slice(0, 280),
      tn: (r.trueNorth || "").slice(0, 280),
      ent: r.entity,
      trib: (trib ?? []).slice(0, 3).map((t) => ({ type: t.type ?? null, prompt: (t.prompt ?? "").slice(0, 200) })),
    }
  })

  const res = NextResponse.json({
    v: "0.1.0",
    fidelity,
    scope: scopeOwn ? "own" : "all",
    generated: new Date().toISOString(),
    n: receipts.length,
    sessions: sessIdx.size,
    users: userIdx.size,
    receipts,
  })
  // Public shape is text-free and id-free; a short shared cache keeps a popular explorer from
  // re-reading 267 rows per visitor. Owner and admin shapes are private.
  res.headers.set("Cache-Control", fidelity === "public" ? "public, s-maxage=300, stale-while-revalidate=600" : "private, no-store")
  return res
}
