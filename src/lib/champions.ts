import fs from "node:fs"
import path from "node:path"

// Champions lane — the PEOPLE pipeline (distinct from the postings board). Source
// is Zach's own LinkedIn connections export, filtered to the 84-row Amy-shape
// shortlist (_STATE/job-search/champion-shortlist-v1). This module reads that TSV
// server-side ONLY and scores each row against the champion-fit rubric
// (_STATE/job-search/champion-fit-heuristic). PII (real names + LinkedIn URLs)
// never leaves a gated handler: the API route checks callerFor() before this runs,
// and nothing here is imported into a client bundle.
//
// Scoring is deterministic — pure regex over the row's position/company/lane, the
// same no-model technique the postings board uses for its Moat/Sleeper/flavor tags.
// warm_path is the DOMINANT dim here (weight 3): unlike postings, these are real
// warm values (every row is a 1st-degree connection; the sourced top tier is warmer
// still). If warm_path stops dominating the rank, the rubric was mis-weighted
// (the spec's falsifier).

export type ChampionLane = "EXT-search" | "INT-basin"
export type ChampionRow = {
  id: string
  lane: ChampionLane
  name: string
  position: string
  company: string
  url: string
  dims: Record<string, number> // 0-3 each, keyed by rubric dim
  composite: number // 0-1 normalized against spec weights
  tags: string[] // computed folksonomy badges
}

export type ChampionDim = { key: string; label: string; weight: number; anchor0: string; anchor3: string }
export type ChampionSpec = {
  version: string
  rubric: { dims: ChampionDim[]; max: number; board_cutoff: number; tiers: { t1: number; t2: number; t3: number } }
  lanes: Record<ChampionLane, { label: string; pitch: string; pattern: string; patternUrl: string }>
}

// The rubric, as data — mirrors champion-fit-heuristic Part 2 "Pre-contact" dims
// (the ones scorable from a distance). On-call dims (bet_on_person, advocacy_
// conversion, effortless_register, relational_carrier) are post-contact and are NOT
// scored here (spec "Not in v1"); they become the swipe-right acceptance test.
export const CHAMPION_SPEC: ChampionSpec = {
  version: "1.0",
  rubric: {
    dims: [
      { key: "crossover_recognition", label: "Crossover recognition", weight: 3, anchor0: "single-lane keyword matcher", anchor3: "values technical×operational×client spanning" },
      { key: "warm_path", label: "Warm path", weight: 3, anchor0: "cold / distant", anchor3: "sourced warm tie, own-book intro" },
      { key: "domain_fit", label: "Domain fit", weight: 2, anchor0: "off-basin staffing", anchor3: "places into agent-infra / applied-AI / crypto / regulated 0→1" },
      { key: "shape_over_title", label: "Shape over title", weight: 2, anchor0: "big-agency volume matcher", anchor3: "founder-led / independent, reads the shape" },
      { key: "org_design_literacy", label: "Org-design literacy", weight: 1, anchor0: "req-filler", anchor3: "ex-operator / team-builder register" },
    ],
    max: 3 * (3 + 3 + 2 + 2 + 1), // 33
    // These 84 are the survivors of an 11,233→84 warm-shortlist funnel — all worth
    // showing. The cutoff is inclusive (everyone renders); tiers set work order.
    // Calibrated to the realized composite range (~0.18–0.73) so the split is real,
    // not a threshold that hides three-quarters of the list.
    board_cutoff: 0.15,
    tiers: { t1: 0.52, t2: 0.36, t3: 0.15 },
  },
  lanes: {
    "EXT-search": {
      label: "External search",
      pitch: "Two-tier recruiter enablement — open positioning + gated ammo. They re-sell the pair across many roles.",
      pattern: "recruithaus.arcs.care",
      patternUrl: "https://recruithaus.arcs.care",
    },
    "INT-basin": {
      label: "Internal basin",
      pitch: "Founder-aimed forge for their company. Converts one basin-central company fast.",
      pattern: "blacksmith.arcs.care",
      patternUrl: "https://blacksmith.arcs.care",
    },
  },
}

// Sourced top tier + warm ties from champion-shortlist-v1.md — the names carrying
// a real warm signal above the 1st-degree baseline. Matched on a normalized key.
const WARM_TOP = [
  "rich roberts", "jordan barry", "tommy roberts", "kate stoughton berliner", "feargall kenny",
  "michael bajda", "alisha adams", "kelsey lawrie", "andrew green", "ryan watson", "leslie cormier",
  "ravi vijay", "gigi genkova", "daisy shen", "alex buder shapiro", "jen ayala",
  "matthew kendall clark", "younes renak", "andrew steinthal",
]
function nameKey(name: string): string {
  return name
    .toLowerCase()
    .replace(/\([^)]*\)/g, " ") // drop pronoun / parenthetical
    .replace(/,.*$/, " ") // drop credential suffixes
    .replace(/[^a-z\s]/g, " ") // drop emoji / punctuation
    .replace(/\s+/g, " ")
    .trim()
}

function hits(text: string, res: RegExp[]): number {
  return res.reduce((n, re) => n + (re.test(text) ? 1 : 0), 0)
}
const clamp3 = (n: number) => Math.max(0, Math.min(3, n))

const CROSSOVER = [/executive search/, /talent partner/, /principal/, /founder|founding/, /fractional/, /\bgtm\b|go[- ]to[- ]market/, /strateg/, /applied ai|blockchain|web3/, /chief talent|head of talent/]
const BASIN = [/\bai\b|applied ai|\.ai\b|artificial intelligence/, /agent|infra|devtool|dev tool|platform/, /crypto|web3|blockchain|solana|polymarket|phantom|token/, /fintech|bank|payments|affirm|carta|block\b/, /\byc\b|founding|founder|0 ?to ?1|startup/, /notion|webflow|clay|github|airtable|coreweave|dropbox|helm|merge|datavant|userflow/]
const FOUNDER = [/founder|founding|co[- ]?found/, /\bowner\b|self[- ]employed|independent/, /principal|partner\b/, /fractional/, /managing (partner|director)/]
const BIG_AGENCY = /korn ferry|kforce|nbcuniversal|restaurant brands|cybercoders|riviera|robert half|randstad|adecco|aerotek|insight global/
const ORG_DESIGN = [/head of people|people (strateg|platform|development|operations)/, /organizational|org (design|effectiveness)/, /talent (development|enablement|strateg|systems)/, /culture/, /advisor|coach|\bacc\b|\bpcc\b/, /fractional|owner|founder/]

function scoreRow(lane: ChampionLane, name: string, position: string, company: string): Record<string, number> {
  const t = `${position} ${company}`.toLowerCase()

  // crossover_recognition — language/placements that value the spanning pair
  const crossover = clamp3(hits(t, CROSSOVER) - 1)

  // warm_path (DOMINANT) — every row is 1st-degree (base 2); sourced top tier = 3
  const warm = WARM_TOP.includes(nameKey(name)) ? 3 : 2

  // domain_fit — basin centrality. INT-basin rows are basin by construction (floor 2)
  const basinHits = hits(t, BASIN)
  const domain = clamp3(lane === "INT-basin" ? Math.max(2, basinHits) : basinHits)

  // shape_over_title — founder-led / independent, not big-agency volume
  const shape = clamp3(hits(t, FOUNDER) - (BIG_AGENCY.test(t) ? 3 : 0))

  // org_design_literacy — ex-operator / team-builder register
  const org = clamp3(hits(t, ORG_DESIGN))

  return { crossover_recognition: crossover, warm_path: warm, domain_fit: domain, shape_over_title: shape, org_design_literacy: org }
}

export function compositeOf(dims: Record<string, number>, spec: ChampionSpec = CHAMPION_SPEC): number {
  let raw = 0
  for (const d of spec.rubric.dims) raw += (dims[d.key] ?? 0) * d.weight
  return +(raw / spec.rubric.max).toFixed(3)
}

export function championTier(c: number | null, spec: ChampionSpec = CHAMPION_SPEC): 1 | 2 | 3 | null {
  if (c == null) return null
  const t = spec.rubric.tiers
  return c >= t.t1 ? 1 : c >= t.t2 ? 2 : c >= t.t3 ? 3 : null
}

function rowTags(lane: ChampionLane, dims: Record<string, number>): string[] {
  const tags: string[] = []
  if (dims.warm_path >= 3) tags.push("Warm")
  if (dims.crossover_recognition >= 3) tags.push("Crossover")
  if (dims.domain_fit >= 3) tags.push("Basin")
  if (dims.shape_over_title >= 2) tags.push("Founder-led")
  return tags
}
export const CHAMPION_TAGS = ["Warm", "Crossover", "Basin", "Founder-led"] as const

let cache: { rows: ChampionRow[]; mtime: number } | null = null
export function loadChampions(): ChampionRow[] {
  const p = path.join(process.cwd(), "runtime", "data", "champion-shortlist-v1.tsv")
  const mtime = fs.statSync(p).mtimeMs
  if (cache && cache.mtime === mtime) return cache.rows
  const text = fs.readFileSync(p, "utf8")
  const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0)
  const rows: ChampionRow[] = []
  for (let i = 1; i < lines.length; i++) {
    const [lane, name, position, company, url] = lines[i].split("\t")
    if (!lane || !name) continue
    // Standing exclusion (spec): Fanatics is never a target. Defense in depth — it is
    // already absent from the source, but guard so a future refresh can't reintroduce it.
    if (/fanatics/i.test(company ?? "")) continue
    const l = lane as ChampionLane
    const dims = scoreRow(l, name, position ?? "", company ?? "")
    rows.push({
      id: `champ-${i}`,
      lane: l,
      name: name.trim(),
      position: (position ?? "").trim(),
      company: (company ?? "").trim(),
      url: (url ?? "").trim(),
      dims,
      composite: compositeOf(dims),
      tags: rowTags(l, dims),
    })
  }
  cache = { rows, mtime }
  return rows
}

// Swipe state lives in JobBoardSetting (key/value) — the table already exists in
// prod, so the champions lane needs no migration. One row per champion, keyed
// `champ_swipe:<id>`, value = JSON { direction, why, at }. Single-tenant (User0).
export const CHAMP_SWIPE_PREFIX = "champ_swipe:"
export type ChampionSwipe = { direction: "r" | "l"; why: string | null; at: string }
// Left-swipe reasons tuned to the champion anti-champion gates (heuristic Part 2).
export const CHAMPION_WHY = ["keyword matcher", "big-agency down-seller", "single-lane filter", "title-flattener", "off-basin", "cold", "timing", "other"] as const
