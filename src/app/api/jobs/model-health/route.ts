import { NextResponse, type NextRequest } from "next/server"
import Anthropic from "@anthropic-ai/sdk"
import { callerFor } from "@/lib/jobs"
import { MODELS, modelError } from "@/lib/claude-models"

// GET /api/jobs/model-health: the morning task's preflight. One 1-token Haiku call, so a
// usage limit, bad key, or outage fails the run up front with the API's own reason
// (code usage_limit | rate_limited | overloaded | auth | ...) instead of failing mid-run.
// Cost: a few input tokens. Admin session or pipeline token, like the rest of /api/jobs.
export const dynamic = "force-dynamic"

export async function GET(req: NextRequest) {
  const caller = await callerFor(req)
  if (!caller) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  if (!process.env.ANTHROPIC_API_KEY) return NextResponse.json({ ok: false, code: "no_key", error: "ANTHROPIC_API_KEY not set" }, { status: 503 })
  const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  const t0 = Date.now()
  const msg = await anthropic.messages.create({ model: MODELS.scorer, max_tokens: 1, messages: [{ role: "user", content: "ok" }] }).catch((e: unknown) => modelError(e))
  if (msg instanceof Response) return msg
  return NextResponse.json({ ok: true, model: MODELS.scorer, ms: Date.now() - t0 })
}
