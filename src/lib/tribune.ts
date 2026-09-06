// ADR-020 Tribune Intelligence Layer — pure helpers (no I/O).
//
// The Tribune ANNOTATES a Receipt in three phases and never mutates it (ADR-019):
//   anterior   pre-mortem, before the needle moves
//   proactive  kinematic observation mid-session — SILENT unless a threshold fires
//   posterior  post-mortem after execution; baton-forward framing
//
// Everything here is deterministic and testable without a DB or a model:
// the silence gate, the risk-tier read, the NCI delta, the per-phase prompt.
// NOTOMATION: the Tribune scaffolds and sequences; it never decides for the navigator.

export type TribunePhase = "anterior" | "proactive" | "posterior"
export type RiskTier = "baseline" | "asymmetric" | "ruin"
export type ClarityMode = "SIMPLE" | "RICH" | "DEEP"

export const PHASES: readonly TribunePhase[] = ["anterior", "proactive", "posterior"] as const
export const BOARD_ROLES = ["detective", "accountant", "loki", "sentry", "alchemist", "elder"] as const
export type BoardRole = (typeof BOARD_ROLES)[number]

/** Proactive silence thresholds (ADR-020 §PROACTIVE). Exported so tests can pin them. */
export const SILENCE = {
  nciDeltaAbs: 15, // |NCI delta| within a session
  driftStates: ["DERAILMENT", "DRIFTING", "LOOPING"] as const, // ≥ DERAILMENT; DRIFTING/LOOPING are the ygate spellings today
  riskTier: "ruin" as RiskTier,
}

/** The subset of a Receipt the Tribune reads. Kept narrow on purpose. */
export type ReceiptView = {
  id: string
  decision: string
  sharpQuestion?: string | null
  trueNorth: string
  whyBullets: string // JSON string[]
  loki?: string | null
  bar?: string | null // JSON {ruin_risk, asymmetry, reversibility}
  nciScore: number
  nciByLens?: string | null
  clarityMode: string
  yState: string
  yConviction: string
  yStability: string
  yDeltaTrigger?: string | null
  flowTopology: string
  mode?: string | null
  doorClass?: string | null
  stakes?: string | null
  window?: string | null
  horizon?: string | null
  entity?: string | null
  sessionId: string
  version: number
  createdAt: Date
}

export type OutcomeView = { outcome?: string | null; note?: string | null; matched?: boolean | null } | null

/** Derive the risk-tier enum from the receipt's `bar` JSON (or the Y state as a fallback). */
export function riskTierOf(receipt: Pick<ReceiptView, "bar" | "yState">): RiskTier {
  try {
    const bar = receipt.bar ? (JSON.parse(receipt.bar) as Record<string, unknown>) : {}
    const ruin = String(bar.ruin_risk ?? "").toLowerCase()
    const rev = String(bar.reversibility ?? "").toLowerCase()
    if (ruin === "high" || ruin === "ruin" || ruin === "existential") return "ruin"
    if (rev === "irreversible" || rev === "none" || rev === "zero") return "ruin"
    if (ruin === "medium" || String(bar.asymmetry ?? "").toLowerCase() === "high") return "asymmetric"
  } catch {
    /* malformed bar JSON → fall through to Y state */
  }
  return receipt.yState === "RED" ? "ruin" : "baseline"
}

/** NCI at session open vs. at this receipt. `openScore` = the seed receipt's score in the session. */
export function nciDelta(openScore: number | null | undefined, currentScore: number): number | null {
  if (openScore == null) return null
  return currentScore - openScore
}

/**
 * The Proactive silence gate. Returns the reasons it should speak; empty = stay silent.
 * "Clarity before Curvature": commentary is earned by a threshold, not always-on.
 */
export function shouldSpeak(input: {
  riskTier: RiskTier
  driftState?: string | null
  nciDelta?: number | null
}): string[] {
  const reasons: string[] = []
  if (input.riskTier === SILENCE.riskTier) reasons.push("risk tier RUIN")
  const drift = (input.driftState ?? "").toUpperCase()
  if ((SILENCE.driftStates as readonly string[]).includes(drift)) reasons.push(`drift ${drift}`)
  if (input.nciDelta != null && Math.abs(input.nciDelta) > SILENCE.nciDeltaAbs)
    reasons.push(`NCI delta ${input.nciDelta > 0 ? "+" : ""}${input.nciDelta}`)
  return reasons
}

/** Court auto-escalation (ADR-020 canonical mappings): irreversibility ≥ 0.7, RUIN, or identity conflict. */
export function courtInvoked(receipt: Pick<ReceiptView, "bar" | "mode">, tier: RiskTier): boolean {
  if (tier === "ruin") return true
  if (receipt.mode === "COURT") return true
  try {
    const bar = receipt.bar ? (JSON.parse(receipt.bar) as Record<string, unknown>) : {}
    const irr = Number(bar.irreversibility)
    if (!Number.isNaN(irr) && irr >= 0.7) return true
  } catch {
    /* ignore */
  }
  return false
}

// ── Generated content shape (what `Tribune.content` holds, per phase) ────────
export type TribuneContent = {
  phase: TribunePhase
  /** SIMPLE mode surfaces exactly this one line. */
  one_line: string
  /** RICH/DEEP: 2–5 short bullets. */
  bullets: string[]
  /** anterior: premortem; proactive: trajectory read; posterior: actual-vs-predicted. */
  detail: Record<string, unknown>
  /** LAB pass — Loki / Advisors / Bayesian. */
  lab: { loki: string; advisors: string; bayesian: string; posterior_probability?: number }
  /** Six Board roles → green | red, with the one-line objection when red. */
  board: Record<BoardRole, { vote: "green" | "red"; objection?: string }>
  /** Proportion of Board roles GREEN after the LAB pass. */
  coalition_readiness: number
}

const BOARD_LIST = BOARD_ROLES.join(", ")

const COMMON_RULES = `You are the ARCS Tribune — a detached observer that annotates a decision receipt. You never decide for the navigator (NOTOMATION). You do not restate the receipt; you add what it cannot see about itself.
Return ONLY a JSON object with keys: phase, one_line, bullets (2-5 strings), detail (object), lab {loki, advisors, bayesian, posterior_probability (0-1)}, board (object keyed by ${BOARD_LIST}, each {vote: "green"|"red", objection?: string}), coalition_readiness (0-1 = share of green votes).
Register: calm, precise, non-fiction. No praise. No hedging filler. one_line ≤ 160 chars.`

const PHASE_BRIEF: Record<TribunePhase, string> = {
  anterior: `PHASE: ANTERIOR (pre-mortem, before the needle moves).
detail must contain: breaks_on (what this CLASS of decision typically breaks on — 2-4 items), frame_gaps (planning-frame gaps the receipt does not name), premortem (one paragraph: "it is six months later and this failed — here is why"), first_tripwire (the earliest observable signal that the premortem is coming true).`,
  proactive: `PHASE: PROACTIVE (kinematic, mid-session). You are speaking only because a silence threshold fired; name it.
detail must contain: fired_on (the threshold reasons given), trajectory (where conviction is heading and whether the motion is progress or looping), fork_or_reinvent ("fork" if an existing path/asset should be forked, "reinvent" if genuinely net-new, with one sentence why), sell_through (how to frame this to the stakeholder most likely to object), meta_tooling (one net-new skill/agent/check that would collapse the current 0→1, or "none").`,
  posterior: `PHASE: POSTERIOR (post-mortem, after execution).
detail must contain: predicted (what the receipt's True North and premortem expected), actual (what the outcome record says happened), recoil (the gap, named plainly; what the navigator over- or under-weighted), baton (the one framing the SUCCESSOR decision should inherit), kintsugi (what to repair visibly, not silently).`,
}

export function buildTribunePrompt(args: {
  phase: TribunePhase
  receipt: ReceiptView
  riskTier: RiskTier
  driftState?: string | null
  nciDelta?: number | null
  clarityMode: ClarityMode
  speakReasons?: string[]
  priorTribune?: TribuneContent | null
  outcome?: OutcomeView
}): { system: string; user: string } {
  const r = args.receipt
  let why: string[] = []
  try {
    why = JSON.parse(r.whyBullets)
  } catch {
    why = [r.whyBullets]
  }
  const lines = [
    `RECEIPT ${r.id} (session ${r.sessionId}, version ${r.version}, ${r.createdAt.toISOString()})`,
    `Sharp question: ${r.sharpQuestion ?? r.decision}`,
    `True North: ${r.trueNorth}`,
    `Why: ${why.map((w) => `- ${w}`).join("\n")}`,
    r.loki ? `Loki (strongest counter): ${r.loki}` : "",
    r.bar ? `BAR: ${r.bar}` : "",
    `NCI ${r.nciScore}${r.nciByLens ? ` by lens ${r.nciByLens}` : ""}`,
    `Y: ${r.yState} · conviction ${r.yConviction} · stability ${r.yStability}${r.yDeltaTrigger ? ` · delta trigger: ${r.yDeltaTrigger}` : ""}`,
    `Flow topology: ${r.flowTopology} · mode ${r.mode ?? "?"} · door ${r.doorClass ?? "?"} · stakes ${r.stakes ?? "?"} · window ${r.window ?? r.horizon ?? "?"}`,
    r.entity ? `Entity: ${r.entity}` : "",
    `Risk tier: ${args.riskTier} · drift ${args.driftState ?? "n/a"} · NCI delta ${args.nciDelta ?? "n/a"} · clarity ${args.clarityMode}`,
    args.speakReasons?.length ? `Silence threshold fired on: ${args.speakReasons.join("; ")}` : "",
    args.priorTribune ? `PRIOR TRIBUNE (${args.priorTribune.phase}): ${JSON.stringify(args.priorTribune).slice(0, 2500)}` : "",
    args.outcome ? `OUTCOME RECORD: ${JSON.stringify(args.outcome)}` : "",
    "",
    PHASE_BRIEF[args.phase],
    "",
    "Return only the JSON object.",
  ].filter(Boolean)
  return { system: COMMON_RULES, user: lines.join("\n") }
}

/** Defensive parse of the model's JSON into TribuneContent; throws on shape violation. */
export function parseTribuneContent(raw: string, phase: TribunePhase): TribuneContent {
  const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
  const obj = JSON.parse(cleaned) as Partial<TribuneContent>
  if (typeof obj.one_line !== "string" || !Array.isArray(obj.bullets)) throw new Error("tribune: missing one_line/bullets")
  const board = {} as TribuneContent["board"]
  let green = 0
  for (const role of BOARD_ROLES) {
    const v = (obj.board as Record<string, { vote?: string; objection?: string }> | undefined)?.[role]
    const vote: "green" | "red" = v?.vote === "red" ? "red" : "green"
    if (vote === "green") green++
    board[role] = v?.objection ? { vote, objection: String(v.objection).slice(0, 300) } : { vote }
  }
  const lab = obj.lab ?? { loki: "", advisors: "", bayesian: "" }
  return {
    phase,
    one_line: obj.one_line.slice(0, 200),
    bullets: obj.bullets.slice(0, 5).map((b) => String(b).slice(0, 400)),
    detail: (obj.detail && typeof obj.detail === "object" ? obj.detail : {}) as Record<string, unknown>,
    lab: {
      loki: String(lab.loki ?? ""),
      advisors: String(lab.advisors ?? ""),
      bayesian: String(lab.bayesian ?? ""),
      ...(typeof lab.posterior_probability === "number" ? { posterior_probability: lab.posterior_probability } : {}),
    },
    board,
    coalition_readiness: Math.round((green / BOARD_ROLES.length) * 100) / 100,
  }
}

/** Project content to the clarity mode: SIMPLE = one line per phase, never a transcript. */
export function projectContent(c: TribuneContent, mode: ClarityMode) {
  if (mode === "SIMPLE") return { phase: c.phase, one_line: c.one_line, coalition_readiness: c.coalition_readiness }
  if (mode === "RICH") return { phase: c.phase, one_line: c.one_line, bullets: c.bullets, coalition_readiness: c.coalition_readiness, board: c.board }
  return c
}
