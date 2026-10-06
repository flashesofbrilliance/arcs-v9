// The model-failure codes /api/compass and the other Claude routes return
// (src/lib/model-error.ts). Dependency-free so the client can import it too:
// model-error.ts pulls in Resend, which must stay out of the browser bundle.
export const MODEL_ERROR_CODES = ["usage_limit", "rate_limited", "overloaded", "auth", "network", "upstream_error", "model_error"] as const

export type ModelErrorCode = (typeof MODEL_ERROR_CODES)[number]

export function isModelErrorCode(v: unknown): v is ModelErrorCode {
  return typeof v === "string" && (MODEL_ERROR_CODES as readonly string[]).includes(v)
}
