import { Resend } from "resend"

// Model-call failures, mapped (2026-10-05). The live compass once rendered the raw
// Anthropic 400 body ("You have reached your specified API usage limits ...",
// request_id and all) to a visitor. Provider bodies stay server-side: the client gets
// a stable code + calm copy; the full upstream error and request_id go to the logs
// under one grep-able tag, [MODEL_OUTAGE]. Never a retry loop here: a usage limit
// is a spending decision.

export type ModelErrorCode = "usage_limit" | "rate_limited" | "overloaded" | "auth" | "network" | "upstream_error" | "model_error"

export interface ModelErrorInfo {
  code: ModelErrorCode
  upstreamStatus: number | null
  retryable: boolean
  message: string // client-safe copy; never contains provider text
}

const HELD = "Your fork is held. Nothing was lost."

const COPY: Record<ModelErrorCode, string> = {
  usage_limit: `The compass is resting while its model allowance resets. ${HELD}`,
  rate_limited: `Too many bearings at once. Give it a minute, then re-run. ${HELD}`,
  overloaded: `The model is under heavy load. Re-run in a moment. ${HELD}`,
  auth: `The compass lost its link to the model. The keeper has been signaled. ${HELD}`,
  network: `The signal dropped mid-run. Re-run in a moment. ${HELD}`,
  upstream_error: `The model stumbled on its side. Re-run in a moment. ${HELD}`,
  model_error: `The compass could not take a bearing this time. ${HELD}`,
}

type Shape = {
  status?: number
  message?: string
  name?: string
  code?: string
  requestID?: string | null
  error?: { type?: string; request_id?: string; error?: { type?: string; message?: string } }
  cause?: unknown
}

function upstreamText(e: unknown): string {
  const err = (e ?? {}) as Shape
  return err?.error?.error?.message ?? err?.message ?? String(e)
}

export function classifyModelError(e: unknown): ModelErrorInfo {
  const err = (e ?? {}) as Shape
  const msg = upstreamText(e)
  const type = err?.error?.error?.type ?? ""
  const status = typeof err?.status === "number" ? err.status : 0
  const code: ModelErrorCode =
    /usage limit/i.test(msg) || type === "billing_error" ? "usage_limit"
    : status === 429 || type === "rate_limit_error" ? "rate_limited"
    : status === 529 || type === "overloaded_error" || /overloaded/i.test(msg) ? "overloaded"
    : status === 401 || status === 403 || type === "authentication_error" || type === "permission_error" ? "auth"
    : !status && (err?.name === "APIConnectionError" || err?.name === "APIConnectionTimeoutError" || /ECONNRESET|ETIMEDOUT|ENOTFOUND|socket hang up|fetch failed|network/i.test(msg)) ? "network"
    : status >= 500 ? "upstream_error"
    : "model_error"
  return {
    code,
    upstreamStatus: status || null,
    retryable: code === "rate_limited" || code === "overloaded" || code === "network" || code === "upstream_error",
    message: COPY[code],
  }
}

function requestId(e: unknown): string | null {
  const err = (e ?? {}) as Shape
  return err?.requestID ?? err?.error?.request_id ?? null
}

// Early warning: an outage the visitor cannot fix (usage limit, bad key) mails the
// admins once per instance per window through the existing Resend channel, so the
// human hears it from the system, not from a dead page.
const ALERT_CODES: ReadonlySet<ModelErrorCode> = new Set(["usage_limit", "auth"])
const ALERT_WINDOW_MS = 6 * 60 * 60_000
const lastAlert = new Map<ModelErrorCode, number>()

function alertAdmins(route: string, info: ModelErrorInfo, upstream: string, rid: string | null) {
  if (!ALERT_CODES.has(info.code)) return
  const now = Date.now()
  if (now - (lastAlert.get(info.code) ?? 0) < ALERT_WINDOW_MS) return
  lastAlert.set(info.code, now)
  const to = (process.env.ADMIN_EMAILS ?? "").split(",").map((s) => s.trim()).filter(Boolean)
  const key = process.env.AUTH_RESEND_KEY
  if (!to.length || !key || process.env.NODE_ENV !== "production") return
  new Resend(key).emails.send({
    from: "ARCS <noreply@arcs.care>",
    to,
    subject: `[MODEL_OUTAGE] ${info.code} on ${route}`,
    text: `The Claude API refused a call from ${route}.\n\ncode: ${info.code}\nupstream_status: ${info.upstreamStatus ?? "none"}\nrequest_id: ${rid ?? "none"}\nupstream: ${upstream.slice(0, 500)}\n\nVisitors see calm copy; the compass stays down until this clears. Next alert for this code in 6h at the earliest (per instance).`,
  }).catch((err: unknown) => console.error("[MODEL_OUTAGE] alert email failed:", err instanceof Error ? err.message : String(err)))
}

// Log the full upstream error server-side, alert if warranted, return the safe info.
export function reportModelError(route: string, e: unknown): ModelErrorInfo {
  const info = classifyModelError(e)
  // Provider text only for SDK API errors; any other throw logs its name, so a future
  // exception carrying decision content cannot reach the logs (/trust:67).
  const err = (e ?? {}) as Shape
  const isApi = typeof err?.status === "number" || /^API/.test(err?.name ?? "")
  const upstream = isApi ? upstreamText(e) : `non-API ${err?.name ?? typeof e}`
  const rid = requestId(e)
  console.error(`[MODEL_OUTAGE] route=${route} code=${info.code} status=${info.upstreamStatus ?? "none"} request_id=${rid ?? "none"} upstream=${JSON.stringify(upstream.slice(0, 1000))}`)
  alertAdmins(route, info, upstream, rid)
  return info
}

// The client payload. Only fields built from our own copy table: no provider text.
export function modelErrorBody(info: ModelErrorInfo) {
  return { error: info.message, code: info.code, retryable: info.retryable }
}

export function modelErrorResponse(route: string, e: unknown): Response {
  const info = reportModelError(route, e)
  return Response.json(modelErrorBody(info), { status: info.code === "rate_limited" ? 429 : 503 })
}

// For tests only.
export function _resetAlertThrottle() { lastAlert.clear() }
