import Anthropic from "@anthropic-ai/sdk"

// One place for the model IDs the job routes call (migrated 2026-10-05 from
// claude-sonnet-4-6 and the dated claude-haiku-4-5-20251001). Change a model here,
// not in a route.
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
} as const

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

// Model-call failures, surfaced (2026-10-05). The routes used to let the SDK error
// escape, so callers saw a bare 500 with an empty body; the real cause ("You have
// reached your specified API usage limits ... regain access on 2026-11-01") was only
// in Vercel's logs. Now the caller gets 503 with the API's own message and a code it
// can act on. Never a retry loop here: a usage limit is a spending decision.
export function modelError(e: unknown): Response {
  const err = e as { status?: number; message?: string; error?: { error?: { type?: string; message?: string } } }
  const message = err?.error?.error?.message ?? err?.message ?? String(e)
  const status = err?.status ?? 0
  const code =
    /usage limit/i.test(message) ? "usage_limit"
    : status === 429 ? "rate_limited"
    : status === 529 || /overloaded/i.test(message) ? "overloaded"
    : status === 401 || status === 403 ? "auth"
    : status >= 500 ? "upstream_error"
    : "model_error"
  return Response.json({ error: `model unavailable: ${message}`, code, upstream_status: status || null, retryable: code === "rate_limited" || code === "overloaded" || code === "upstream_error" }, { status: 503 })
}
