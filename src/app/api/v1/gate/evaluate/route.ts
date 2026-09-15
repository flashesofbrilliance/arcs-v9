/**
 * POST /api/v1/gate/evaluate  (Vercel Edge)
 *
 * ARCS Algor-ethics Decision Firewall: STRUCTURED TOOL-ACTION INTERCEPTOR.
 *
 * SCOPE. This gateway evaluates structured agent tool-call intents (`action_type`
 * plus `target_payload`) against the Rome Call / Dignitas Infinita invariants.
 * It is NOT a conversational moderation filter or a prompt-jailbreak detector:
 * measured 2026-09-15, it intercepts 0/200 JailBreakV-28k free-text queries by
 * design, not by defect. Do not describe it as a natural-language safety layer.
 *
 * AUTHENTICATION. Fail-closed shared secret: `x-arcs-gate-key` (or
 * `Authorization: Bearer <key>`) must equal `ARCS_GATE_KEY`. If the env var is
 * unset every POST is 401, so a deploy without the secret exposes nothing.
 * GET /healthz-style probe stays open and returns no secrets.
 *
 * ARCS Algor-ethics Decision Firewall gateway. Contract is byte-for-byte the one
 * served by `code/server.py` in flashesofbrilliance/arcs-algorethics, so the same
 * E2E suite (tests/e2e/test_live_pipeline.py) runs against either:
 *
 *   200 APPROVED / 423 LOCKED, body {status, risk_class, reason, reasons[],
 *   kairos_write_lock, requires_human_signature, receipt_hash, timestamp,
 *   persistence:{persisted,duplicate,error}, firmware}
 *   headers: x-arcs-latency-ms (gate evaluation only), x-arcs-receipt-persisted
 *
 * Fail-closed on the gate, fail-soft on persistence: a receipt that cannot be
 * written to algorethics.gate_receipts never turns a LOCK into an APPROVE.
 * Persistence needs SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL) + SUPABASE_SERVICE_ROLE_KEY
 * and the `algorethics` schema exposed to PostgREST; otherwise `persisted:false`
 * with the reason in the body. Patterns mirror EmergencyBrake v9.0-Omega verbatim;
 * keep them in lockstep with code/emergency_brake.py and bin/arcs.js.
 */
export const runtime = 'edge'

const FIRMWARE = 'v9.0-Omega'

// Sister Clare invariants: life, hospice, vital care, kinetic lethality (MORTAL)
const LETHAL_PATTERNS: RegExp[] = [
  /(fire|launch|discharge|dispatch).*?(weapon|kinetic|missile|strike|payload|artillery|drone)/,
  /(target|engage).*?(combatant|personnel|human|civilian|coordinates)/,
  /(terminate|cut_off|deprecate|ration).*?(life_support|ventilator|oxygen|dialysis|insulin|medicaid|hospice)/,
  /(deny|revoke).*?(vital_care|critical_care|emergency_response|food_ration)/,
  /(lethal|kill|assassinate|neutralize|destroy).*?(target|human|individual|subject)/,
]
// Brother Francis invariants: labor subsidiarity, livelihood, poverty (CARDINAL)
const LABOR_PATTERNS: RegExp[] = [
  /(displace|fire|terminate|sever|eliminate|attrit).*?(worker|staff|employee|workforce|cohort|headcount|labor)/,
  /(algorithmic|automated).*?(layoff|downsizing|redundancy|severance)/,
  /(deprecate|deplete|slash).*?(pension|livelihood|wage|shelter|unemployment_benefit)/,
  /(foreclose|evict).*?(tenant|resident|family|home)/,
]
const FORBIDDEN_KEY_PREFIXES = ['AGENT_', 'AUTO_', 'SYSTEM_AI_', 'SYNTHETIC_']

type Status = 'APPROVED' | 'LOCKED' | 'REJECTED'
type RiskClass = 'MORTAL' | 'CARDINAL' | 'VENIAL'

interface TaskContext {
  task_id: string
  action_type: string
  target_payload: Record<string, unknown>
  confidence: number
  entropy: number
  operator_role: string | null
  signature: string | null
}

interface Verdict {
  status: Status
  risk_class: RiskClass
  reasons: string[]
  kairos_write_lock: boolean
  requires_human_signature: boolean
  receipt_hash: string
  timestamp: string
}

/** Python's str(dict) lowercased is what the daemon matches against; mirror it closely enough. */
function payloadText(p: Record<string, unknown>): string {
  return JSON.stringify(p).replace(/"/g, "'").replace(/:/g, ': ').replace(/,/g, ', ')
}

function lock(ctx: TaskContext, risk: RiskClass, tag: string, reason: string, now: string): Verdict {
  return {
    status: 'LOCKED', risk_class: risk, reasons: [reason], kairos_write_lock: true,
    requires_human_signature: true, receipt_hash: `lock-${tag}-${ctx.task_id}`, timestamp: now,
  }
}

export function evaluate(ctx: TaskContext): Verdict {
  const now = new Date().toISOString()
  const text = `${ctx.action_type} ${payloadText(ctx.target_payload)}`.toLowerCase()

  if (ctx.entropy > 0.85 || ctx.confidence < 0.6) {
    return lock(ctx, 'CARDINAL', 'entropy',
      'HIGH_ENTROPY_UNCERTAINTY: Task parameters ambiguous or unverified. Fail-closed engaged.', now)
  }
  for (const p of LETHAL_PATTERNS) {
    if (p.test(text)) {
      return lock(ctx, 'MORTAL', 'mortal',
        `CARMELITE_LIFE_DEFENSE (Sister Clare Invariant): Action matches lethal/vital pattern '${p.source}'. ` +
        'Vatican LAWS & Dignitas Infinita Invariant: No machine may take human life or terminate vital care.', now)
    }
  }
  for (const p of LABOR_PATTERNS) {
    if (p.test(text)) {
      return lock(ctx, 'CARDINAL', 'cardinal',
        `FRANCISCAN_SOLIDARITY (Brother Francis Invariant): Action matches livelihood harm pattern '${p.source}'. ` +
        'Rome Call Subsidiarity: Labor decisions require pastoral human presence.', now)
    }
  }
  if (ctx.signature && FORBIDDEN_KEY_PREFIXES.some((pre) => ctx.signature!.startsWith(pre))) {
    return lock(ctx, 'CARDINAL', 'forgery',
      `AGENT_SELF_SIGN_PROHIBITED: Attestation signed by non-human principal '${ctx.signature}'.`, now)
  }
  return {
    status: 'APPROVED', risk_class: 'VENIAL',
    reasons: ['TWO_WAY_OPERATION: No life, livelihood, or vital welfare boundary violated. Low irreversibility.'],
    kairos_write_lock: false, requires_human_signature: false,
    receipt_hash: `approved-venial-${ctx.task_id}`, timestamp: now,
  }
}

async function persist(ctx: TaskContext, v: Verdict): Promise<{ persisted: boolean; duplicate: boolean; error: string | null }> {
  const url = (process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? '').replace(/\/+$/, '')
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ''
  if (!url || !key) return { persisted: false, duplicate: false, error: 'SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not configured' }
  const row = {
    receipt_hash: v.receipt_hash, task_id: ctx.task_id, action_type: ctx.action_type,
    target_payload: ctx.target_payload, status: v.status, risk_class: v.risk_class, reasons: v.reasons,
    kairos_write_lock: v.kairos_write_lock, requires_human_signature: v.requires_human_signature,
    confidence: ctx.confidence, entropy: ctx.entropy, operator_role: ctx.operator_role,
    gateway: 'edge', evaluated_at: v.timestamp,
  }
  try {
    const r = await fetch(`${url}/rest/v1/gate_receipts`, {
      method: 'POST',
      headers: {
        apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json',
        'Content-Profile': 'algorethics', Prefer: 'return=minimal',
      },
      body: JSON.stringify(row),
      signal: AbortSignal.timeout(3000),
    })
    if (r.status === 409) return { persisted: true, duplicate: true, error: null }
    if (r.ok) return { persisted: true, duplicate: false, error: null }
    return { persisted: false, duplicate: false, error: `HTTP ${r.status}: ${(await r.text()).slice(0, 200)}` }
  } catch (e) {
    return { persisted: false, duplicate: false, error: `transport: ${e instanceof Error ? e.message : String(e)}` }
  }
}

function parseContext(raw: unknown): TaskContext | string {
  if (!raw || typeof raw !== 'object') return 'body must be a JSON object'
  const b = raw as Record<string, unknown>
  if (typeof b.task_id !== 'string' || !b.task_id) return 'task_id (string) is required'
  if (typeof b.action_type !== 'string') return 'action_type (string) is required'
  const num = (v: unknown, d: number) => (typeof v === 'number' && Number.isFinite(v) ? v : d)
  return {
    task_id: b.task_id,
    action_type: b.action_type,
    target_payload: b.target_payload && typeof b.target_payload === 'object' ? (b.target_payload as Record<string, unknown>) : {},
    confidence: num(b.confidence, 1.0),
    entropy: num(b.entropy, 0.0),
    operator_role: typeof b.operator_role === 'string' ? b.operator_role : null,
    signature: typeof b.signature === 'string' ? b.signature : null,
  }
}

/** Constant-time string compare so the key cannot be recovered byte-by-byte from timing. */
function keysMatch(a: string, b: string): boolean {
  const enc = new TextEncoder()
  const x = enc.encode(a)
  const y = enc.encode(b)
  let diff = x.length ^ y.length
  for (let i = 0; i < Math.max(x.length, y.length); i++) diff |= (x[i] ?? 0) ^ (y[i] ?? 0)
  return diff === 0
}

function authorized(req: Request): boolean {
  const expected = process.env.ARCS_GATE_KEY
  if (!expected) return false
  const provided = req.headers.get('x-arcs-gate-key')
    ?? req.headers.get('authorization')?.replace(/^Bearer\s+/i, '')
    ?? ''
  return keysMatch(provided, expected)
}

export async function POST(req: Request): Promise<Response> {
  if (!authorized(req)) {
    return Response.json(
      { error: 'UNAUTHORIZED', message: 'Valid x-arcs-gate-key header required. Gate is fail-closed.' },
      { status: 401, headers: { 'cache-control': 'no-store', 'x-arcs-firmware': FIRMWARE } },
    )
  }
  let raw: unknown
  try {
    raw = await req.json()
  } catch {
    return Response.json({ error: 'invalid JSON body' }, { status: 400 })
  }
  const ctx = parseContext(raw)
  if (typeof ctx === 'string') return Response.json({ error: ctx }, { status: 422 })

  const t0 = performance.now()
  const verdict = evaluate(ctx)
  const latencyMs = performance.now() - t0

  const persistence = await persist(ctx, verdict)

  const body = {
    ...verdict,
    reason: verdict.reasons.join(' | '),
    persistence,
    firmware: FIRMWARE,
  }
  return Response.json(body, {
    status: verdict.status === 'APPROVED' ? 200 : 423,
    headers: {
      'x-arcs-latency-ms': latencyMs.toFixed(3),
      'x-arcs-receipt-persisted': persistence.persisted ? 'true' : 'false',
      'x-arcs-firmware': FIRMWARE,
      'cache-control': 'no-store',
    },
  })
}

export function GET(): Response {
  return Response.json({ status: 'HEALTHY', engine: 'ARCS_v9_DIAMOND', firmware: FIRMWARE, gate_status: 'READY', runtime: 'edge' })
}
