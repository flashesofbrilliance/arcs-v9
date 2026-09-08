import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

// POST /api/jobs/score — the JD-read + score worker's model half. LinkedIn JD
// fetches are blocked from datacenter IPs, so the CALLER fetches each JD as text
// (works from a residential path; scripts/jobs_score_sweep.mjs does this) and
// posts { rows:[{jobid,title,company,jd,salary?}] } here. This route holds the
// prod ANTHROPIC_API_KEY, scores against runtime/specs/target-role-scan.json
// (cached rubric prefix, Haiku, temp 0), writes composite/band/dims/gates back
// onto JobOpportunity, and records a Score row. Gated (admin or pipeline token).
export const dynamic = "force-dynamic"
export const maxDuration = 60

type Dim = { key: string; label: string; weight: number; anchor0: string; anchor3: string }
type Row = { jobid: string; title: string; company: string; jd: string; salary?: string | null }

function spec() {
  const p = path.join(process.cwd(), "runtime", "specs", "target-role-scan.json")
  return JSON.parse(fs.readFileSync(p, "utf8"))
}

function systemPrompt(s: ReturnType<typeof spec>): string {
  const dims: Dim[] = s.rubric.dims
  return `You score a job posting for one candidate against a fixed rubric. The candidate is a forward-deployed / applied-AI product-and-engineering builder: regulated-domain fluency, breadth across product + GTM + data, ships LLM/agent systems on Claude + MCP in production, two decades across tech/data/commercial ops. Target archetypes: ${s.archetypes.map((a: { title: string }) => a.title).join("; ")}.

Score EACH posting on these ${dims.length} dimensions, integer 0-3, using the anchors:
${dims.map((d) => `- ${d.key} (weight ${d.weight}): 0 = ${d.anchor0}; 3 = ${d.anchor3}`).join("\n")}

Hard gates (list any that fire, by these exact strings): ${JSON.stringify(s.rubric.gates)}. A gate means auto-disqualify.
Extract a comp string if the JD states one (e.g. "$180K-$250K"), else null. Write a <=25 word assessment: the single sharpest fit-or-gap read.

Return ONLY a JSON array, one object per posting IN THE SAME ORDER, no prose:
[{"jobid":"...","dims":{${dims.map((d) => `"${d.key}":0`).join(",")}},"gates":[],"comp":null,"assessment":"..."}]`
}

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  const rows: Row[] = Array.isArray(body?.rows) ? body.rows : []
  if (!rows.length) return NextResponse.json({ error: "rows required" }, { status: 400 })
  if (rows.length > 12) return NextResponse.json({ error: "max 12 rows per call" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "scorer unavailable (no key)" }, { status: 503 })

  const s = spec()
  const dims: Dim[] = s.rubric.dims
  const MAX = s.rubric.max as number
  const B = s.rubric.bands as { pursue: number; consider: number }
  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

  const jds = rows.map((r) => `### jobid ${r.jobid} — ${r.title} @ ${r.company}\n${(r.jd || "").slice(0, 6000)}`).join("\n\n")
  const msg = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001", max_tokens: 1600, temperature: 0,
    system: [{ type: "text", text: systemPrompt(s), cache_control: { type: "ephemeral" } }],
    messages: [{ role: "user", content: `Score these ${rows.length} postings:\n\n${jds}` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let parsed: Array<{ jobid: string; dims: Record<string, number>; gates?: string[]; comp?: string | null; assessment?: string }>
  try { parsed = JSON.parse(txt.slice(txt.indexOf("["), txt.lastIndexOf("]") + 1)) }
  catch { return NextResponse.json({ error: "scorer returned unparseable output" }, { status: 502 }) }

  const byId = Object.fromEntries(parsed.map((p) => [String(p.jobid), p]))
  const results: Array<{ jobid: string; composite: number; band: string }> = []
  for (const r of rows) {
    const p = byId[r.jobid]; if (!p) continue
    let raw = 0; for (const d of dims) raw += (Number(p.dims?.[d.key]) || 0) * d.weight
    const composite = +(raw / MAX).toFixed(3)
    const gated = Array.isArray(p.gates) && p.gates.length > 0
    const band = gated ? "PASS" : composite >= B.pursue ? "PURSUE" : composite >= B.consider ? "CONSIDER" : "PASS"
    const dimsJson = JSON.stringify(p.dims), gatesJson = JSON.stringify(p.gates || [])
    await prisma.jobOpportunity.update({
      where: { jobid: r.jobid },
      data: { composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, compBand: p.comp ?? null, salary: r.salary ?? p.comp ?? undefined, unscoredWhy: null, scoredAt: new Date() },
    }).catch(() => {})
    await prisma.score.upsert({
      where: { jobid_targetVersion: { jobid: r.jobid, targetVersion: String(s.version) } },
      create: { jobid: r.jobid, targetVersion: String(s.version), composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, scoredAt: new Date() },
      update: { composite, band, dims: dimsJson, gates: gatesJson, assessment: p.assessment ?? null, scoredAt: new Date() },
    }).catch(() => {})
    results.push({ jobid: r.jobid, composite, band })
  }
  return NextResponse.json({ scored: results.length, results, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
