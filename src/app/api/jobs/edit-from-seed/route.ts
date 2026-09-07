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

const SYSTEM = `You EDIT an existing tailored resume (the "seed") to fit a NEW role in the same archetype cluster, and you return a PATCH, not the document. This is a re-point, and the patch is the delta only.

HARD RULES (correctness over everything):
- Keep every factual claim, employer, date, figure, and the archetype headline from the seed EXACTLY. Never invent, inflate, add an employer/title, or add a skill the seed does not already contain. Never claim a job title the candidate did not hold; the headline names an ARCHETYPE, never the new req title.
- Change ONLY: (a) the target/role reference line, (b) which existing bullets lead and the summary emphasis, (c) light rewording of EXISTING bullets to mirror this JD's language WITHOUT adding new claims.
- No em-dashes. No scoring vocabulary (tier, band, composite, pursue). No counterpart names, comp talk, or hiring-manager names in the resume body.

Return the patch as a list of exact find/replace edits. Each "find" MUST be a verbatim substring copied EXACTLY from the seed HTML (whitespace and tags included) so it can be located by literal match; keep each "find" short and uniquely identifiable. "replace" is the edited text. 3 to 10 edits is typical.

Return ONLY JSON:
{"edits":[{"find":"<exact verbatim substring of the seed HTML>","replace":"<edited text>","why":"<short>"}],"assessment":"<=25 words fit read","hiringManager":{"kind":"explicit|implicit|unknown","text":"evidence quote from JD or null"},"contact":{"type":"portal|form|email|referral|unverified","detail":null}}`

export async function POST(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  const b = (await req.json().catch(() => null)) as Body | null
  if (!b?.jobid || !b?.jd || !b?.seedResumeHtml) return NextResponse.json({ error: "jobid, jd, seedResumeHtml required" }, { status: 400 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ error: "editor unavailable (no key)" }, { status: 503 })

  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  const msg = await anthropic.messages.create({
    model: "claude-sonnet-4-6", max_tokens: 3000, temperature: 0.2,
    system: [
      { type: "text", text: SYSTEM },
      { type: "text", text: `SEED RESUME HTML (copy find targets from here, verbatim):\n${b.seedResumeHtml.slice(0, 40000)}`, cache_control: { type: "ephemeral" } },
    ],
    messages: [{ role: "user", content: `NEW role: ${b.title} @ ${b.company} (jobid ${b.jobid}) · seed ${b.seedSlug}\n\n--- NEW JD ---\n${b.jd.slice(0, 6000)}\n\nReturn the patch (edits[]) that re-points the seed to this role.` }],
  })
  const txt = msg.content.map((c) => ("text" in c ? c.text : "")).join("")
  let out
  try { out = JSON.parse(txt.slice(txt.indexOf("{"), txt.lastIndexOf("}") + 1)) }
  catch { return NextResponse.json({ error: "editor returned unparseable output" }, { status: 502 }) }
  // air-gap guard on the returned resume (defence in depth; the driver checks too)
  const edits = Array.isArray(out.edits) ? out.edits : []
  if (!edits.length) return NextResponse.json({ error: "editor returned no edits" }, { status: 502 })
  for (const e of edits) {
    const r = String(e.replace ?? "")
    if (r.includes("—") || /\b(tier|band|composite|pursue)\b/i.test(r)) {
      return NextResponse.json({ error: "editor patch failed air-gap (em-dash or scoring vocab)" }, { status: 502 })
    }
  }
  return NextResponse.json({ edits, assessment: out.assessment, hiringManager: out.hiringManager, contact: out.contact, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } })
}
