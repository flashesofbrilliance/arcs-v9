import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { callerFor } from "@/lib/jobs"

// POST /api/jobs/edit-from-seed — the token-saving half of the edit-from-seed
// worker. A role in an already-seeded shape cluster does not need a fresh forge:
// this takes a BUILT bundle's resume HTML (the seed) plus the new role's JD and
// returns an EDITED resume that re-points only the role-specific hooks, keeping
// the archetype headline, structure, and every factual claim from the seed
// unchanged (they trace to the record of record). Far cheaper than a full forge:
// no reference-bundle read, output is an edit not a from-scratch generation.
// The caller fetches the JD + reads the seed HTML locally and renders the PDF;
// this route only holds the key and does the model edit. Gated.
export const dynamic = "force-dynamic"
export const maxDuration = 60

type Body = { jobid: string; title: string; company: string; jd: string; seedSlug: string; seedResumeHtml: string }

const SYSTEM = `You EDIT an existing tailored resume (the "seed") so it fits a NEW role in the same archetype cluster. This is a re-point, not a rewrite.

HARD RULES (correctness over everything):
- Keep every factual claim, employer, date, figure, and the archetype headline from the seed EXACTLY. They trace to a vetted record of record. Never invent, inflate, add a new employer/title, or add a skill the seed does not already contain.
- Never claim a job title the candidate did not hold. The headline names an ARCHETYPE, never the new req title.
- Change ONLY: (a) the "Target"/role reference line to the new role, (b) which existing bullets lead and the summary emphasis, to match this JD's top hooks, (c) light rewording of existing bullets to mirror the JD's language WITHOUT adding new claims.
- Plain language. No em-dashes. No scoring vocabulary (tier, band, composite, pursue). No counterpart names, no comp talk, no hiring-manager names in the resume body.
- Keep it TWO pages of content and valid, self-contained HTML with the same <style> the seed used.

Return ONLY JSON:
{"resumeHtml":"<full edited resume HTML>","tailorDelta":"<=120 words: what you re-pointed and why","assessment":"<=25 words fit read","hiringManager":{"kind":"explicit|implicit|unknown","text":"evidence quote from JD or null"},"contact":{"type":"portal|form|email|referral|unverified","detail":null}}`

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const b = (await req.json().catch(() => null)) as Body | null
  if (!b?.jobid || !b?.jd || !b?.seedResumeHtml) return NextResponse.json({ error: "jobid, jd, seedResumeHtml required" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "editor unavailable (no key)" }, { status: 503 })

  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  const msg = await anthropic.messages.create({
    model: "claude-sonnet-4-6", max_tokens: 16000, temperature: 0.2,
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages: [{ role: "user", content: `NEW role: ${b.title} @ ${b.company} (jobid ${b.jobid})\nSeed bundle: ${b.seedSlug}\n\n--- NEW JD ---\n${b.jd.slice(0, 6000)}\n\n--- SEED RESUME HTML (edit this) ---\n${b.seedResumeHtml.slice(0, 40000)}` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let out
  try { out = JSON.parse(txt.slice(txt.indexOf("{"), txt.lastIndexOf("}") + 1)) }
  catch { return NextResponse.json({ error: "editor returned unparseable output" }, { status: 502 }) }
  // air-gap guard on the returned resume (defence in depth; the driver checks too)
  const html = String(out.resumeHtml || "")
  if (html.includes("—") || /\b(tier|band|composite|pursue)\b/i.test(html)) {
    return NextResponse.json({ error: "editor output failed air-gap (em-dash or scoring vocab)" }, { status: 502 })
  }
  return NextResponse.json({ ...out, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
