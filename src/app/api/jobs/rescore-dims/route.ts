import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { prisma } from "@/lib/db"
import { callerFor } from "@/lib/jobs"

// POST /api/jobs/rescore-dims - one-shot migration worker for the v1.1 -> v1.2
// rubric split. v1.1 scored a single `strength_leverage` (0-3); v1.2 replaces it
// with two axes: `rare_combination` (the operator-who-builds x transversal x 0->1
// moat) and `domain_breadth` (regulated / cross-domain reach). The full JD is not
// persisted, so this DECOMPOSES from what we have - title, company, assessment,
// and the old strength_leverage score - into the two new dims, keeps the other 7
// dims unchanged, recomputes composite against the live spec, and writes back a
// v1.2 Score row (the v1.1 Score row is preserved by version, so this is
// reversible). Caller posts stored rows; this route holds the prod key. Gated.
export const dynamic = "force-dynamic"
export const maxDuration = 60

type Dim = { key: string; label: string; weight: number; anchor0: string; anchor3: string }
type InRow = { jobid: string; title: string; company: string; assessment?: string | null; dims: Record<string, number>; gates?: string[]; compBand?: string | null }

function spec() {
  return JSON.parse(fs.readFileSync(path.join(process.cwd(), "runtime", "specs", "target-role-scan.json"), "utf8"))
}

function systemPrompt(dims: Dim[]): string {
  const rc = dims.find((d) => d.key === "rare_combination")!
  const db = dims.find((d) => d.key === "domain_breadth")!
  return `You re-score existing job-fit rows for one candidate after a rubric change. The candidate is a forward-deployed / applied-AI product-and-engineering builder: two decades across regulated domains (SEC/FINRA, HIPAA, gov), breadth across product + GTM + data + engineering, ships LLM/agent systems on Claude + MCP in production.

A single old dimension "strength_leverage" is being split into TWO independent dimensions. For each row, using its title, company, prior assessment, and old strength_leverage score, output BOTH new scores as integers 0-3:

- rare_combination (0 = ${rc.anchor0}; 3 = ${rc.anchor3}): does the ROLE'S SHAPE reward the candidate's rare combination - operator-who-also-builds, transversal cross-domain synthesizer, 0->1-under-ambiguity - such that few qualified applicants share the shape? Founding / first-hire / open-ended / GTM-engineer / forward-deployed roles score high; deep, well-staffed single-lane roles score low even when the candidate would do the job well.
- domain_breadth (0 = ${db.anchor0}; 3 = ${db.anchor3}): does the role sit in a regulated / high-stakes domain, or reward fluency across multiple such domains?

These are orthogonal: a role can be high on one and low on the other. Do not just copy the old score to both.

Return ONLY a JSON array, one object per row IN THE SAME ORDER, no prose:
[{"jobid":"...","rare_combination":0,"domain_breadth":0}]`
}

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const body = await req.json().catch(() => null)
  const rows: InRow[] = Array.isArray(body?.rows) ? body.rows : []
  if (!rows.length) return NextResponse.json({ error: "rows required" }, { status: 400 })
  if (rows.length > 12) return NextResponse.json({ error: "max 12 rows per call" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "scorer unavailable (no key)" }, { status: 503 })

  const s = spec()
  const dims: Dim[] = s.rubric.dims
  const MAX = s.rubric.max as number
  const B = s.rubric.bands as { pursue: number; consider: number }
  if (!dims.some((d) => d.key === "rare_combination") || !dims.some((d) => d.key === "domain_breadth")) {
    return NextResponse.json({ error: "spec is not v1.2 (missing split dims)" }, { status: 409 })
  }
  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

  const lines = rows.map((r) => `### jobid ${r.jobid} - ${r.title} @ ${r.company}\nold strength_leverage: ${r.dims?.strength_leverage ?? "n/a"}\nassessment: ${r.assessment ?? "none"}`).join("\n\n")
  const msg = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001", max_tokens: 1200, temperature: 0,
    system: [{ type: "text", text: systemPrompt(dims), cache_control: { type: "ephemeral" } }],
    messages: [{ role: "user", content: `Re-score these ${rows.length} rows:\n\n${lines}` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let parsed: Array<{ jobid: string; rare_combination: number; domain_breadth: number }>
  try { parsed = JSON.parse(txt.slice(txt.indexOf("["), txt.lastIndexOf("]") + 1)) }
  catch { return NextResponse.json({ error: "rescorer returned unparseable output" }, { status: 502 }) }

  const byId = Object.fromEntries(parsed.map((p) => [String(p.jobid), p]))
  const results: Array<{ jobid: string; composite: number; band: string; rare_combination: number; domain_breadth: number }> = []
  for (const r of rows) {
    const p = byId[r.jobid]; if (!p) continue
    // keep the 7 unchanged dims, drop the retired one, add the two new ones
    const nd: Record<string, number> = { ...r.dims }
    delete nd.strength_leverage
    nd.rare_combination = Math.max(0, Math.min(3, Number(p.rare_combination) || 0))
    nd.domain_breadth = Math.max(0, Math.min(3, Number(p.domain_breadth) || 0))
    let raw = 0; for (const d of dims) raw += (Number(nd[d.key]) || 0) * d.weight
    const composite = +(raw / MAX).toFixed(3)
    const gates: string[] = Array.isArray(r.gates) ? r.gates : []
    const gated = gates.length > 0
    const band = gated ? "PASS" : composite >= B.pursue ? "PURSUE" : composite >= B.consider ? "CONSIDER" : "PASS"
    const dimsJson = JSON.stringify(nd), gatesJson = JSON.stringify(gates)
    await prisma.jobOpportunity.update({
      where: { jobid: r.jobid },
      data: { composite, band, dims: dimsJson, scoredAt: new Date() },
    }).catch(() => {})
    await prisma.score.upsert({
      where: { jobid_targetVersion: { jobid: r.jobid, targetVersion: String(s.version) } },
      create: { jobid: r.jobid, targetVersion: String(s.version), composite, band, dims: dimsJson, gates: gatesJson, assessment: r.assessment ?? null, scoredAt: new Date() },
      update: { composite, band, dims: dimsJson, gates: gatesJson, scoredAt: new Date() },
    }).catch(() => {})
    results.push({ jobid: r.jobid, composite, band, rare_combination: nd.rare_combination, domain_breadth: nd.domain_breadth })
  }
  return NextResponse.json({ scored: results.length, results, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
