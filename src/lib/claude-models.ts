import Anthropic from "@anthropic-ai/sdk"
import { modelErrorResponse } from "@/lib/model-error"

// THE one place a Claude model id lives (app routes, scripts/, operators/). Callers name
// a role; scripts/model_id_gate.py (pre-commit) blocks an id anywhere else, and Python
// reads this same block via scripts/arcs_models.py. Changing a role's model changes
// product output: do it on Zach's go, after an eval (scripts/model_drift_check.py flags
// a newer model per role). Job routes migrated 2026-10-05 off Sonnet 4.6 / dated Haiku.
//
// Sonnet 5.5 differences that matter to these routes:
//  - sampling params: a non-default temperature is a 400, so writer calls send none;
//  - thinking is adaptive by default and counts toward max_tokens, so caps are raised
//    and depth is set with output_config.effort (low for edits, medium for prose);
//  - safety classifiers can decline (stop_reason "refusal"); the server-side fallback
//    re-runs the request on another model inside the same call, and a final refusal
//    is surfaced as an error, never parsed as empty output.
export const MODELS = {
  writer: "claude-sonnet-5-5", // cover letters, application answers, resume edits
  scorer: "claude-haiku-4-5",  // JD scoring + dim rescoring (temperature 0 is still allowed on Haiku)
  fast: "claude-haiku-4-5",    // compass QUICKMOVE/PLAN, tribune anterior/proactive, annotations, health probe, operators/arcs_lte
  deep: "claude-sonnet-5-5",   // compass COURT, tribune posterior, brief, scripts/slop_eval (2026-10-06, off 4.6 after scripts/deep_model_eval.mjs).
                               // Same 5.5 rules as writer: send no temperature, set depth with output_config.effort.
  guide: "claude-opus-4-5",    // guide route (kept as found)
  max: "claude-opus-4-7",      // scripts/network_scan
} as const

export type ModelRole = keyof typeof MODELS

type WriterParams = {
  max_tokens: number
  effort: "low" | "medium" | "high"
  system: Anthropic.Messages.TextBlockParam[]
  messages: Anthropic.Messages.MessageParam[]
}

export type WriterResult =
  | { ok: true; text: string; usage: { input: number; output: number; cache_read: number } }
  | { ok: false; refusal: string | null }

// Writer call on Sonnet 5.5 with the "default" refusal fallback (beta, Claude API only).
// The request is cast because the pinned SDK's types predate the fallbacks field; the
// wire shape follows the Claude API docs for server-side-fallback-2026-07-01.
export async function writerCall(anthropic: Anthropic, p: WriterParams): Promise<WriterResult> {
  const req = {
    model: MODELS.writer,
    max_tokens: p.max_tokens,
    output_config: { effort: p.effort },
    system: p.system,
    messages: p.messages,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
  }
  const msg = (await anthropic.beta.messages.create(req as unknown as Anthropic.Beta.Messages.MessageCreateParamsNonStreaming)) as unknown as {
    content: { type: string; text?: string }[]
    stop_reason: string | null
    stop_details?: { category?: string | null } | null
    usage: { input_tokens: number; output_tokens: number; cache_read_input_tokens?: number | null }
  }
  if (msg.stop_reason === "refusal") return { ok: false, refusal: msg.stop_details?.category ?? null }
  const text = msg.content.filter((c) => c.type === "text").map((c) => c.text ?? "").join("")
  return { ok: true, text, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens, cache_read: msg.usage.cache_read_input_tokens ?? 0 } }
}

// Model-call failures: one shared mapper (src/lib/model-error.ts). The caller gets a
// stable code + calm copy; the provider's own message and request_id stay in the logs
// under [MODEL_OUTAGE]. Kept as a named export so the job routes need no change.
export function modelError(e: unknown, route = "jobs"): Response {
  return modelErrorResponse(route, e)
}
