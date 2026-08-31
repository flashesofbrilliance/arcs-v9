/**
 * audit-client.ts
 * ARCS v9 — Path A audit client (compass route → audit service fetch layer)
 *
 * PURPOSE
 *   Enriches the Claude L0–L5 compass pipeline with operator audit output
 *   (SAGE → LAB → BAR → KINTSUGI). Advisory only — never blocks, never decides.
 *
 * CONTRACT
 *   - Mirrors the existing SAGE_URL pattern: fetch with timeout, log on failure,
 *     inject advisory signal into Claude's context, persist audit trail as a side effect.
 *   - Never throws to the route. Errors are caught and recorded in the trace.
 *   - Audit fields are never returned to the client and never `include`d by any route.
 *     They exist for the with/without-audit efficacy study and internal review.
 *
 * SEAM
 *   - Reads from env: AUDIT_SERVICE_URL (default → no-op, same as SAGE_URL today).
 *   - Calls: /api/audit/sage, /api/audit/lab, /api/audit/bar, /api/audit/kintsugi
 *   - Each endpoint takes the compass context (question + horizon + stakes + prep + LLM output)
 *     and returns structured audit output for that operator.
 *
 * STATUS: SPECCED. Wired alongside audit-translator.ts. Read before touching the compass route.
 */

import {
  previewAuditOutput,
  operatorAdvisoryBlock,
} from "./audit-client-helpers"
import type { OperatorPrimitives } from "./audit-translator"
import { translateCompassReceipt } from "./audit-translator"

// ─── Types ─────────────────────────────────────────────────────────────────

/** What the compass route passes to the audit service for a single operator call */
export interface AuditRequest {
  question: string
  horizon: string
  stakes: string
  clarityMode: string
  doorClass: string
  llmOutput: Record<string, unknown>
  prep?: { confidence?: string; adversarialInput?: string } | null
  sessionVersion: number
  traceId: string
}

/** What the audit service returns for a single operator call */
export interface AuditResponse {
  /** Operator name: "SAGE" | "LAB" | "BAR" | "KINTSUGI" */
  operator: string
  /** Whether the call succeeded (falsy → audit service didn't run this operator) */
  ok: boolean
  /** Structured operator output. Shape varies by operator. */
  output: Record<string, unknown>
  /** Raw primitives sent to the operator (for the audit trail / reproducibility) */
  primitivesSent?: OperatorPrimitives
  /** Latency in ms */
  latencyMs: number
  /** Fidelity markers — which inputs were defaults vs real */
  fidelity: {
    somatic: "default" | "user_self_report"
    hci: "proxy" | "user_self_report"
    axioms: "llm_derived" | "default"
  }
}

/** Accumulated audit trace for one compass run — persisted to the receipt as a side effect */
export interface AuditTrace {
  traceId: string
  sessionVersion: number
  fired: boolean // did at least one operator actually respond?
  operators: {
    name: string
    fired: boolean
    latencyMs: number | null
    failureReason: string | null
    outputPreview: string // short human-readable summary of the output, for the context injection
  }[]
  /** Combined advisory signal injected into Claude's context */
  advisoryBlock: string
}

// ─── Constants ──────────────────────────────────────────────────────────────

const AUDIT_OPERATORS = ["SAGE", "LAB", "BAR", "KINTSUGI"] as const
const AUDIT_TIMEOUT_MS = 4000
const MAX_ADVISORY_BLOCK_LENGTH = 2200 // keep the injected block short — context is expensive

// ─── Public API ────────────────────────────────────────────────────────────

/**
 * runAudit — called from the compass route AFTER the LLM output is available.
 *
 * Returns an AuditTrace. The route uses:
 *   - trace.advisoryBlock → injected into the LLM context for downstream enrichment
 *     (same pattern as sageBlock today — advisory, not authoritative)
 *   - trace.operators → persisted to an invisible audit row, never returned to client
 *
 * FALLBACK: if AUDIT_SERVICE_URL is unset, or any operator call fails, we log and
 * continue. The route never blocks on the audit layer.
 */
export async function runAudit(
  request: AuditRequest,
  logFn: (msg: string, metadata?: Record<string, unknown>) => void,
): Promise<AuditTrace> {
  const baseUrl = process.env.AUDIT_SERVICE_URL
  const trace: AuditTrace = {
    traceId: request.traceId,
    sessionVersion: request.sessionVersion,
    fired: false,
    operators: [],
    advisoryBlock: "",
  }

  if (!baseUrl) {
    logFn("[AUDIT] AUDIT_SERVICE_URL unset — skipping operator audit")
    return trace
  }

  // Translate once — all four operators consume the same primitives
  const primitives = translateCompassReceipt({
    question: request.question,
    horizon: request.horizon,
    stakes: request.stakes,
    clarityMode: request.clarityMode,
    doorClass: request.doorClass,
    llmOutput: request.llmOutput,
    prep: request.prep,
  })

  const advisoryParts: string[] = []

  // D1/D2: parallelize the four operator calls (Promise.all), never sequential.
  // Each call has its own timeout; the slowest governs total latency, not the sum.
  const operatorPromises = AUDIT_OPERATORS.map(async (opName) => {
    const t0 = Date.now()
    const opTrace = {
      name: opName,
      fired: false,
      latencyMs: null as number | null,
      failureReason: null as string | null,
      outputPreview: "",
    }

    try {
      const res = await fetch(`${baseUrl}/api/audit/${opName.toLowerCase()}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          primitives,
          llmOutput: request.llmOutput,
          traceId: request.traceId,
          sessionVersion: request.sessionVersion,
        }),
        signal: AbortSignal.timeout(AUDIT_TIMEOUT_MS),
      })
      opTrace.latencyMs = Date.now() - t0

      if (!res.ok) {
        opTrace.failureReason = `non-200:${res.status}`
        logFn(`[AUDIT] ${opName}: non-200 ${res.status}`, {
          traceId: request.traceId,
          operator: opName,
          latencyMs: opTrace.latencyMs,
        })
        trace.operators.push(opTrace)
        return
      }

      const auditRes = (await res.json()) as AuditResponse
      opTrace.fired = auditRes.ok
      opTrace.outputPreview = previewAuditOutput(opName, auditRes.output)
      trace.fired = trace.fired || auditRes.ok

      if (auditRes.ok && auditRes.output) {
        advisoryParts.push(operatorAdvisoryBlock(opName, auditRes.output))
      }

      trace.operators.push(opTrace)
    } catch (err) {
      opTrace.latencyMs = Date.now() - t0
      opTrace.failureReason = `unreachable:${
        err instanceof Error ? err.message : String(err)
      }`
      logFn(`[AUDIT] ${opName}: unreachable`, {
        traceId: request.traceId,
        operator: opName,
        error: opTrace.failureReason,
      })
      trace.operators.push(opTrace)
    }
  })

  await Promise.all(operatorPromises)

  // Build the combined advisory block — short, structured, injected into context
  trace.advisoryBlock =
    advisoryParts.length > 0
      ? `\n\nOPERATOR AUDIT (advisory, not authoritative — for context enrichment):\n${advisoryParts.join("\n---\n")}`
      : ""

  // Truncate if the block grew too long (context budget)
  if (trace.advisoryBlock.length > MAX_ADVISORY_BLOCK_LENGTH) {
    trace.advisoryBlock = trace.advisoryBlock.slice(0, MAX_ADVISORY_BLOCK_LENGTH - 3) + "..."
  }

  return trace
}
