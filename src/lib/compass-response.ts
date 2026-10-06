import { isModelErrorCode } from "@/lib/model-error-codes"

// How the dashboard settles a non-OK /api/compass answer. Any HTTP response is a
// definitive server answer: the route returns a receipt only on 200, so the
// receipt-recovery poll (for timeouts and dropped connections) is never needed
// and would only add ~20s of dead time before the card. Pure, so it is testable.
export const FALLBACK = "The compass could not take a bearing this time. Your fork is held. Nothing was lost."

export function compassFailure(ok: boolean, data: unknown): { message: string; code: string | null; poll: false } | null {
  if (ok) return null
  const d = (data ?? {}) as { error?: unknown; code?: unknown }
  const error = typeof d.error === "string" && d.error.trim() ? d.error : null
  return {
    message: error ?? FALLBACK,
    code: isModelErrorCode(d.code) ? d.code : typeof d.code === "string" ? d.code : null,
    poll: false,
  }
}
