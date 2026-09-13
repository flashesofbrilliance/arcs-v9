import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

// POST /api/jobs/score — the JD-read + score worker's model half. LinkedIn JD
// fetches are blocked from datacenter IPs, so the CALLER fetches each JD as text
// (works from a residential path; scripts/jobs_score_sweep.mjs does this) and
// posts { rows:[{jobid,title,company,jd,salary?,notes?}], spec? } here. This
// route holds the prod ANTHROPIC_API_KEY, scores against the selected rubric
// (default runtime/specs/target-role-scan.json, the FDE lens; `spec:"bridge-scan"`
// selects runtime/specs/bridge-scan.json, the win-probability lens for the bridge
// lane; scripts/jobs_bridge_sweep.mjs drives that) with a cached rubric prefix,
// Haiku, temp 0, writes composite/band/dims/gates back onto JobOpportunity, and
// records a Score row keyed by the spec's score_version (so lanes never collide).
// Gated (admin or pipeline token).
export const dynamic = "force-dynamic"
export const maxDuration = 60

type Dim = { key: string; label: string; weight: number; anchor0: string; anchor3: string }
type Row = { jobid: string; title: string; company: string; jd: string; salary?: string | null; notes?: string | null }

// Allowlisted rubrics. Default is the FDE lens (unchanged behaviour); the bridge
// lens is opt-in per call. Anything else is a 400, never a filesystem path.
const SPECS: Record<string, string> = { "target-role-scan": "target-role-scan.json", "bridge-scan": "bridge-scan.json" }
const DEFAULT_SPEC = "target-role-scan"

function spec(name: string) {
  const p = path.join(process.cwd(), "runtime", "specs", SPECS[name])
  return JSON.parse(fs.readFileSync(p, "utf8"))
}

const FDE_FRAME = "The candidate is a forward-deployed / applied-AI product-and-engineering builder: regulated-domain fluency, breadth across product + GTM + data, ships LLM/agent systems on Claude + MCP in production, two decades across tech/data/commercial ops."

function systemPrompt(s: ReturnType<typeof spec>): string {
  const dims: Dim[] = s.rubric.dims
  const frame: string = s.candidate_frame ?? FDE_FRAME
  const archetypes = Array.isArray(s.archetypes) && s.archetypes.length ? ` Target archetypes: ${s.archetypes.map((a: { title: string }) => a.title).join("; ")}.` : ""
  const notes: string[] = Array.isArray(s.rubric.scoring_notes) ? s.rubric.scoring_notes : []
  return `You score a job posting for one candidate against a fixed rubric. ${frame}${archetypes}

Score EACH posting on these ${dims.length} dimensions, integer 0-3, using the anchors:
${dims.map((d) => `- ${d.key} (weight ${d.weight}): 0 = ${d.anchor0}; 3 = ${d.anchor3}`).join("\n")}
${notes.length ? `\nScoring notes:\n${notes.map((n) => `- ${n}`).join("\n")}\n` : ""}
Hard gates (list any that fire, by these exact strings): ${JSON.stringify(s.rubric.gates)}. A gate means auto-disqualify.
Extract a comp string if the JD states one (e.g. "$180K-$250K"), else null. Write a <=25 word assessment: the single sharpest fit-or-gap read.

Return ONLY a JSON array, one object per posting IN THE SAME ORDER, no prose:
[{"jobid":"...","dims":{${dims.map((d) => `"${d.key}":0`).join(",")}},"gates":[],"comp":null,"assessment":"..."}]`
}

type GateRule = { title?: string; jd?: string }
export function applyGateRules(rubric: { gate_rules?: Record<string, GateRule>; mechanical_gates?: Record<string, GateRule> }, modelGates: string[], title: string, jd: string): string[] {
  const hit = (rule: GateRule) => (rule.title && new RegExp(rule.title, "i").test(title)) || (rule.jd && new RegExp(rule.jd, "i").test(jd))
  const rules = rubric.gate_rules || {}
  const kept = modelGates.filter((g) => !rules[g] || hit(rules[g]))
  for (const [g, rule] of Object.entries(rubric.mechanical_gates || {})) if (hit(rule) && !kept.includes(g)) kept.push(g)
  return kept
}

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  const rows: Row[] = Array.isArray(body?.rows) ? body.rows : []
  if (!rows.length) return NextResponse.json({ error: "rows required" }, { status: 400 })
  if (rows.length > 12) return NextResponse.json({ error: "max 12 rows per call" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "scorer unavailable (no key)" }, { status: 503 })
  const specName: string = typeof body?.spec === "string" && body.spec ? body.spec : DEFAULT_SPEC
  if (!SPECS[specName]) return NextResponse.json({ error: `unknown spec; one of ${Object.keys(SPECS).join(", ")}` }, { status: 400 })

  const s = spec(specName)
  const dims: Dim[] = s.rubric.dims
  const MAX = s.rubric.max as number
  const B = s.rubric.bands as { pursue: number; consider: number }
  const scoreVersion = String(s.score_version ?? s.version)
  const STRICT = s.rubric.strict_gates === true
  const GATE_SET = new Set<string>(Array.isArray(s.rubric.gates) ? s.rubric.gates : [])
  const JD_CHARS = Number(s.rubric.jd_chars) || 6000 // spec may widen the JD window (bridge JDs carry a long company preamble)
  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

  const jds = rows.map((r) => `### jobid ${r.jobid} — ${r.title} @ ${r.company}${r.notes ? `\nCaller notes: ${String(r.notes).slice(0, 400)}` : ""}\n${(r.jd || "").slice(0, JD_CHARS)}`).join("\n\n")
  const msg = await anthropic.messages.create({
    // ~200 output tokens per row on average (9 dims + gates + assessment) with real variance; 8 rows at a flat 1600
    // truncated mid-array and came back unparseable, so size the cap to the batch with headroom.
    model: "claude-haiku-4-5-20251001", max_tokens: Math.max(1600, 300 * rows.length), temperature: 0,
    system: [{ type: "text", text: systemPrompt(s), cache_control: { type: "ephemeral" } }],
    messages: [{ role: "user", content: `Score these ${rows.length} postings:\n\n${jds}` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let parsed: Array<{ jobid: string; dims: Record<string, number>; gates?: string[]; comp?: string | null; assessment?: string }>
  try { parsed = JSON.parse(txt.slice(txt.indexOf("["), txt.lastIndexOf("]") + 1)) }
  catch { return NextResponse.json({ error: "scorer returned unparseable output", stop_reason: msg.stop_reason, tail: txt.slice(-160) }, { status: 502 }) }

  const byId = Object.fromEntries(parsed.map((p) => [String(p.jobid), p]))
  const results: Array<{ jobid: string; composite: number; band: string; dims: Record<string, number>; gates: string[]; assessment: string | null }> = []
  for (const r of rows) {
    const p = byId[r.jobid]; if (!p) continue
    let raw = 0; for (const d of dims) raw += (Number(p.dims?.[d.key]) || 0) * d.weight
    const composite = +(raw / MAX).toFixed(3)
    // strict_gates (spec opt-in): only allowlisted gate strings can auto-PASS; the model sometimes invents one.
    // gate_rules (spec opt-in): a model gate stands only if its title/JD regex matches; mechanical_gates add
    // title-driven gates the model never sees. Free-text gate judgment misfired twice in a row (2026-09-13).
    const gates: string[] = applyGateRules(s.rubric, Array.isArray(p.gates) ? p.gates.filter((g) => typeof g === "string" && (!STRICT || GATE_SET.has(g))) : [], r.title, r.jd || "")
    const gated = gates.length > 0
    const band = gated ? "PASS" : composite >= B.pursue ? "PURSUE" : composite >= B.consider ? "CONSIDER" : "PASS"
    const dimsJson = JSON.stringify(p.dims), gatesJson = JSON.stringify(gates)
    await prisma.jobOpportunity.update({
      where: { jobid: r.jobid },
      data: { composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, compBand: p.comp ?? null, salary: r.salary ?? p.comp ?? undefined, unscoredWhy: null, scoredAt: new Date() },
    }).catch(() => {})
    await prisma.score.upsert({
      where: { jobid_targetVersion: { jobid: r.jobid, targetVersion: scoreVersion } },
      create: { jobid: r.jobid, targetVersion: scoreVersion, composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, scoredAt: new Date() },
      update: { composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, scoredAt: new Date() },
    }).catch(() => {})
    results.push({ jobid: r.jobid, composite, band, dims: p.dims ?? {}, gates, assessment: p.assessment ?? null })
  }
  return NextResponse.json({ scored: results.length, spec: specName, score_version: scoreVersion, results, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
