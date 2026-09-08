import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { callerFor } from "@/lib/jobs"

// POST /api/jobs/cover-letter — writes a tailored cover letter for one role in
// Zach's voice, modeled on the platinum reference cover (voice + structure), and
// grounded in THIS role's JD. It is a voice-modeled generation, not a diff:
// the constant beats (the opener, the ARCS / CI-for-decisions overlap, the "on me"
// credentials) carry across; the delta is 2-3 observations specific to this JD.
// Short output (~350 + ~180 words) so no timeout. The caller fetches the JD and
// reads the reference cover locally and posts them. Gated.
export const dynamic = "force-dynamic"
export const maxDuration = 60

type Body = { jobid: string; title: string; company: string; jd: string; seedCover: string; resumeText?: string }

function seedVoice() {
  // fallback voice notes if no seed passed
  return "Opener: 'I build the tool, then become its most demanding user.' Then 2-3 observations specific to THIS company's product/moat, grounded in the JD. Then the quiet overlap: ARCS is a CI for decisions (state the bet, keep the receipt, check if it panned out). Then 'on me': in the code reviews, sprint planning, incident response; framework-agnostic; zero-to-one under SEC/FINRA and HIPAA; army of one punching above weight. Sign off as Zach Harris, zachharris.xyz."
}

const SYSTEM = `You write a cover letter for Zach Harris for ONE role, in his voice, modeled on a reference cover you are given. This is voice-modeled, not copied: keep his constant beats, write the role-specific middle fresh from THIS job description.

HARD RULES (correctness over polish):
- Never fabricate an employer, title, figure, or credential. Only claims consistent with the reference cover and the resume text may appear. If unsure, leave it out.
- Never claim a title Zach did not hold; he is a forward-deployed product-and-AI builder, army of one, two decades across tech/data/commercial ops, ships an LLM-native platform (ARCS) on Claude with a live MCP server.
- Do NOT include any medical, injury, surgery, or personal-availability note. That is situational and Zach adds it by hand per application. Omit it entirely.
- Plain language. NO em-dashes anywhere (use commas or periods). No scoring vocabulary (tier, band, composite, pursue). Address the company by name; never invent a hiring manager's name.
- Ground the 2-3 middle observations in the JD: name the company's actual product, moat, or problem, and connect it to Zach's real experience. Specific beats flattering.

Return ONLY JSON:
{"coverMd":"<full cover, ~300-380 words, greeting to sign-off, plain text paste-ready>","coverShort":"<compressed ~160-190 word version for a form field, same beats>","hook":"<one line: the single sharpest reason-to-call-back this letter makes>"}`

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const b = (await req.json().catch(() => null)) as Body | null
  if (!b?.jobid || !b?.jd) return NextResponse.json({ error: "jobid, jd required" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "writer unavailable (no key)" }, { status: 503 })

  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  const msg = await anthropic.messages.create({
    model: "claude-sonnet-4-6", max_tokens: 2000, temperature: 0.4,
    system: [
      { type: "text", text: SYSTEM },
      { type: "text", text: `REFERENCE COVER (voice + structure model; do not copy its company-specific content):\n${(b.seedCover || seedVoice()).slice(0, 12000)}`, cache_control: { type: "ephemeral" } },
    ],
    messages: [{ role: "user", content: `Role: ${b.title} @ ${b.company} (jobid ${b.jobid})\n\n--- JD ---\n${b.jd.slice(0, 6000)}\n\n--- Zach's resume text for this role (claims must stay consistent with this) ---\n${(b.resumeText || "").slice(0, 8000)}\n\nWrite the cover for ${b.company}.` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let out
  try { out = JSON.parse(txt.slice(txt.indexOf("{"), txt.lastIndexOf("}") + 1)) }
  catch { return NextResponse.json({ error: "writer returned unparseable output" }, { status: 502 }) }
  for (const k of ["coverMd", "coverShort"]) {
    const v = String(out[k] ?? "")
    if (!v) return NextResponse.json({ error: `writer omitted ${k}` }, { status: 502 })
    if (v.includes("—") || /\b(tier|band|composite|pursue)\b/i.test(v)) return NextResponse.json({ error: "cover failed air-gap (em-dash or scoring vocab)" }, { status: 502 })
    if (/surgery|acl|meniscus|injur/i.test(v)) return NextResponse.json({ error: "cover leaked the personal medical note" }, { status: 502 })
  }
  return NextResponse.json({ ...out, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
