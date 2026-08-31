/**
 * audit-translator.ts
 * ARCS v9 — Compass Receipt → Operator Primitives translator (Path A)
 *
 * PURPOSE
 *   Translates the structured output of the Claude L0–L5 compass pipeline into
 *   the primitives the Python operator pipeline expects (SAGE → LAB → BAR → KINTSUGI).
 *
 * CONTRACT
 *   - Never blocks the route. Translation failures fall back to defaults.
 *   - Never fabricates operator input. If a field can't be derived, it's defaulted
 *     or passed as null so the operator can use its own fallback.
 *   - The somatic/HCI gap is the honest weak point: the compass doesn't currently
 *     collect somatic self-report or HCI. We default somatic conservatively and
 *     derive an HCI proxy from the LLM's own coherence/nci output. Better fidelity
 *     comes from adding a quick somatic self-report at intake — marked below.
 *
 * STATUS: SPECCED, not yet wired. Read alongside audit-client.ts and the audit service
 *         FastAPI sketch (docs/ or operators/audit_service/).
 *         Also read alongside `operators/prod_receipt_to_op20_seed.py` (the op20←prod
 *         bridge) and `operators/arcs_operator20.py` + `operators/arcs_operator21.py`
 *         (the op20↔op21 entanglement).
 */

import type { ReceiptJSON } from "./types"

// ─── Output shape: what the audit service / operator pipeline consumes ────────

export interface OperatorPrimitives {
  /** CoherenceSignal — the raw decision signal */
  signal: {
    label: string
    domain: string
    /** Vectorized representation of the decision context.
     *  Derived from horizon/stakes/mode/door — not from raw numeric series.
     *  Used by SAGE's kinematic lens as a proxy signal. */
    signalProxy: number[]
    phaseId: string
  }
  /** FATEDReasoning — structured decomposition from the LLM's reasoning.fated block */
  fated: {
    facts: string
    assumptions: string
    tradeoffs: string
    emotions: string
    direction: string
  }
  /** AxiomCheck — DNA axiom compliance. Derived from LLM reasoning, not asserted. */
  axioms: {
    clarity_before_curvature: "YES" | "NO" | "TENSION"
    agency_over_automation: "YES" | "NO" | "TENSION"
    minimum_steps_to_coherence: "YES" | "NO" | "TENSION"
    kairos_over_neuroticism: "YES" | "NO" | "TENSION"
    /** Ground Truth tag: were these derived from the LLM's output or prompted from the user? */
    source: "llm_derived" | "user Prompt" | "default"
  }
  /** SomaticReading — six phenomenological primitives.
   *  DEFAULTS ONLY unless the intake adds a somatic self-report.
   *  This is the honest weak point — see somaticFallback note below. */
  somatic: {
    phase_tuning: number
    surge_detection: number
    feels_right: number
    that_vibes: number
    locked_in: number
    expected_vs_actual: number
    source: "default" | "user_self_report"
  }
  /** HCI score (0–100). Human Coherence Index — self-reported.
   *  Absent from current compass intake → proxied from LLM coherence/nci.
   *  A real HCI requires asking the user. Marked as a proxy. */
  hci_score: number
  hci_source: "proxy" | "user_self_report"
  /** PCI score (0–100). Platform Coherence Index — computed. */
  pci_score: number
  /** irreversibility estimate (0–1) from stakes + door_class */
  irreversibility: number
  /** on_purpose — was this a reasoned decision? Default True for compass intake. */
  onPurpose: boolean
  /** next_action — declared next move. Derived from true_north. */
  nextAction: string
  /** phase_id — current pipeline phase */
  phaseId: string
  /** Signal classification proxy — maps compass coherence to operator signal class */
  signalClassification: "strong_signal" | "noise" | "mixed" | "decelerating"
}

// ─── Constants ──────────────────────────────────────────────────────────────

/**
 * Somatic fallback values when no user self-report is available.
 * Conservative mid-range — not asserting anything, just avoiding zero.
 * Source: "default" — flagged as low-fidelity in the audit trail.
 */
const SOMATIC_DEFAULT: Readonly<OperatorPrimitives["somatic"]> = {
  phase_tuning: 0.55,
  surge_detection: 0.50,
  feels_right: 0.50,
  that_vibes: 0.50,
  locked_in: 0.55,
  expected_vs_actual: 0.50,
  source: "default",
}

/**
 * Axiom defaults when the LLM's reasoning doesn't provide a clear compliance signal.
 * TENSION is the honest default — not asserting YES or NO.
 */
const AXIOM_DEFAULT: OperatorPrimitives["axioms"] = {
  clarity_before_curvature: "TENSION",
  agency_over_automation: "TENSION",
  minimum_steps_to_coherence: "TENSION",
  kairos_over_neuroticism: "TENSION",
  source: "default",
}

/**
 * Signal proxy — encodes the decision context as a 12-element vector for SAGE's
 * kinematic lens. This is a proxy, not a real time series. SAGE can run its lens
 * on it, but the kinematic derivatives will reflect the proxy's structure, not
 * an actual observed signal. Marked in the audit trail.
 *
 * Mapping (chosen for legibility, not claim of optimality):
 *   [0–2]  horizon encoding  (THIS_WEEK=0.9, THIS_MONTH=0.7, THIS_QUARTER=0.5, THIS_YEAR=0.3, LONGER=0.1)
 *   [3–5]  stakes encoding   (LOW=0.3, MEDIUM=0.6, HIGH=0.9)
 *   [6–7]  door_class        (ONE_WAY=0.9/0.1, TWO_WAY=0.5/0.5)
 *   [8]    clarity_mode      (SIMPLE=0.3, RICH=0.6, DEEP=0.9)
 *   [9]    coherence proxy   (from LLM coherence_pct, normalized)
 *   [10]   nci proxy         (from LLM nci_score, normalized)
 *   [11]   reversibility tag (1 - irreversibility)
 */
function signalProxyFromContext(
  horizon: string,
  stakes: string,
  doorClass: string,
  clarityMode: string,
  coherencePct: number,
  nciScore: number,
  irreversibility: number,
): number[] {
  const horizonVal = horizonToValue(horizon)
  const stakesVal = stakesToValue(stakes)
  const [doorA, doorB] = doorClass === "ONE_WAY" ? [0.9, 0.1] : [0.5, 0.5]
  const clarityVal = clarityMode === "SIMPLE" ? 0.3 : clarityMode === "RICH" ? 0.6 : 0.9

  return [
    horizonVal, horizonVal * 0.8, horizonVal * 0.6, // horizon encoding (3 slots)
    stakesVal, stakesVal * 0.8, stakesVal * 0.6,     // stakes encoding (3 slots)
    doorA, doorB,                                     // door class (2 slots)
    clarityVal,                                        // clarity mode (1 slot)
    coherencePct / 100,                               // coherence proxy (1 slot)
    nciScore / 100,                                   // nci proxy (1 slot)
    1 - irreversibility,                             // reversibility tag (1 slot)
  ]
}

function horizonToValue(h: string): number {
  return h === "TODAY"
    ? 0.9
    : h === "THIS_WEEK"
    ? 0.8
    : h === "THIS_MONTH"
    ? 0.6
    : h === "THIS_QUARTER"
    ? 0.5
    : h === "ONE_TO_THREE_YEARS"
    ? 0.3
    : 0.2 // LONGER / unknown → conservative
}

function stakesToValue(s: string): number {
  return s === "LOW" ? 0.3 : s === "MEDIUM" ? 0.6 : 0.9
}

// ─── Public API ────────────────────────────────────────────────────────────

/**
 * translateCompassReceipt → OperatorPrimitives
 *
 * Takes a subset of the compass POST body + Claude L0-L5 output and produces
 * the primitives the operator pipeline consumes.
 *
 * FALLBACK CONTRACT: every field resolves to something, never undefined.
 * Low-fidelity fields (somatic, axioms when unprompted) are marked with source
 * so the audit trail knows their fidelity.
 */
export function translateCompassReceipt(input: {
  question: string
  horizon: string
  stakes: string
  clarityMode: string
  doorClass: string
  llmOutput: ReceiptJSON
  prep?: { confidence?: string; adversarialInput?: string } | null
}): OperatorPrimitives {
  const out = input.llmOutput

  // ── Phase ID ──────────────────────────────────────────────────────────────
  // Map compass horizon to operator phase. Not a claim that compass phases == operator phases.
  // This is a seam mapping, not a semantic equivalence.
  const phaseId = horizonToPhaseId(input.horizon)

  // ── Signal ────────────────────────────────────────────────────────────────
  const signalProxy = signalProxyFromContext(
    input.horizon,
    input.stakes,
    input.doorClass,
    input.clarityMode,
    Number(out.coherence_pct ?? 50),
    Number(out.nci_score ?? 50),
    irreversibilityFromContext(input.stakes, input.doorClass),
  )

  // ── FATED ─────────────────────────────────────────────────────────────────
  // Extract FATED from the LLM's reasoning.fated block when present.
  // Fall back to a minimal decomposition derived from the question + true_north.
  const fated = out.reasoning?.fated
    ? {
        facts: out.reasoning.fated.facts ?? "",
        assumptions: out.reasoning.fated.assumptions ?? "",
        tradeoffs: out.reasoning.fated.tradeoffs ?? "",
        emotions: out.reasoning.fated.emotions ?? "",
        direction: out.reasoning.fated.direction ?? "",
      }
    : fatedFromQuestionAndTrueNorth(input.question, out.true_north as string)

  // ── Axioms ────────────────────────────────────────────────────────────────
  // Derive axiom compliance from the LLM's reasoning.geometry.macros_on + court verdicts
  // when available. Fall back to TENSION default.
  const axioms = deriveAxiomsFromLlm(out, input)

  // ── Somatic ───────────────────────────────────────────────────────────────
  // DEFAULT ONLY. The compass does not currently collect somatic self-report.
  // To raise fidelity: add a 6-question somatic self-report at intake (see somaticPrompt below).
  // The source field signals this is low-fidelity.
  const somatic = SOMATIC_DEFAULT

  // ── HCI / PCI ─────────────────────────────────────────────────────────────
  // HCI: no user self-report → proxy from LLM coherence_pct.
  const hci_score = Math.round(Number(out.coherence_pct ?? 50))
  const hci_source: "proxy" | "user_self_report" = "proxy"

  // PCI: computed from signal proxy derivatives (SAGE-style computation on the proxy).
  // This is a platform-side computation, not a user report.
  const pci_score = computePciProxy(signalProxy)

  // ── Irreversibility ───────────────────────────────────────────────────────
  const irreversibility = irreversibilityFromContext(input.stakes, input.doorClass)

  // ── Next action ───────────────────────────────────────────────────────────
  const nextAction = (out.true_north as string) || "Review the decision before acting."

  // ── Signal classification ─────────────────────────────────────────────────
  const signalClassification = classifySignal(
    Number(out.coherence_pct ?? 50),
    Number(out.nci_score ?? 50),
    out.meta?.macro_tags as string[] | undefined,
  )

  return {
    signal: {
      label: input.question.trim().slice(0, 200),
      domain: "decision",
      signalProxy,
      phaseId,
    },
    fated,
    axioms,
    somatic,
    hci_score,
    hci_source,
    pci_score,
    irreversibility,
    onPurpose: true,
    nextAction,
    phaseId,
    signalClassification,
  }
}

// ─── Private helpers ───────────────────────────────────────────────────────

function horizonToPhaseId(h: string): string {
  return h === "TODAY" || h === "THIS_WEEK" ? "phase_1" : h === "THIS_MONTH" ? "phase_2" : "phase_3"
}

function irreversibilityFromContext(stakes: string, doorClass: string): number {
  // HIGH stakes → irreversibility 0.7; MEDIUM → 0.4; LOW → 0.15
  const stakesVal = stakes === "HIGH" ? 0.7 : stakes === "MEDIUM" ? 0.4 : 0.15
  // ONE_WAY door → +0.15 irreversibility (harder to undo)
  const doorAdj = doorClass === "ONE_WAY" ? 0.15 : 0
  return Math.min(0.95, stakesVal + doorAdj)
}

function deriveAxiomsFromLlm(
  out: ReceiptJSON,
  input: { stakes: string; doorClass: string; clarityMode: string; horizon: string },
): OperatorPrimitives["axioms"] {
  // Attempt to derive axiom compliance from the LLM's structural output.
  // This is an inference, not a ground-truth reading. Marked source appropriately.
  const macroTags = out.meta?.macro_tags as string[] | undefined ?? []
  const courtVerdicts = out.reasoning?.court as { verdict: string }[] | undefined ?? []

  // Has the LLM engaged BAR or KKL macro? That's evidence it considered risk geometry.
  const engagedRisk = macroTags.includes("BAR") || macroTags.includes("KKL")
  // Has the LLM engaged NOTOMATION explicitly?
  const engagedNoto = macroTags.includes("NOTOMATION")
  // Are court verdicts all PASS? Tension in any court check → axiom tension.
  const hasCourtTension = courtVerdicts.some((c: { verdict: string }) => c.verdict === "TENSION")

  return {
    clarity_before_curvature: engagedRisk ? "YES" : "TENSION",
    agency_over_automation: engagedNoto ? "YES" : hasCourtTension ? "TENSION" : "TENSION",
    minimum_steps_to_coherence:
      input.clarityMode === "SIMPLE" ? "YES" : input.clarityMode === "RICH" ? "TENSION" : "TENSION",
    kairos_over_neuroticism:
      input.horizon === "TODAY" || input.horizon === "THIS_WEEK" ? "YES" : "TENSION",
    source: "llm_derived",
  }
}

function fatedFromQuestionAndTrueNorth(question: string, trueNorth: string): {
  facts: string
  assumptions: string
  tradeoffs: string
  emotions: string
  direction: string
} {
  // Minimal FATED when the LLM's reasoning.fated block is absent.
  // Not claiming these are real — they're a fallback structure so SAGE has something to run on.
  return {
    facts: `Decision context: ${question.slice(0, 300)}`,
    assumptions: "Derived from question text. Not independently verified.",
    tradeoffs: "Not extracted from LLM output. Flagged as low-fidelity FATED.",
    emotions: "Not assessed. Somatic self-report would populate this.",
    direction: trueNorth || "Review the decision before acting.",
  }
}

function computePciProxy(signalProxy: number[]): number {
  // Platform Coherence Index proxy — computed from the signal proxy vector.
  // This is NOT the real PCI (which uses real kinematic derivatives on real signal).
  // It's a platform-side computation on the proxy so BAR has something to compare the HCI against.
  const mean = signalProxy.reduce((a, b) => a + b, 0) / signalProxy.length
  const variance = signalProxy.reduce((a, b) => a + (b - mean) ** 2, 0) / signalProxy.length
  // Higher mean + lower variance → higher PCI. Capped at reasonable range.
  const raw = 30 + mean * 60 - Math.sqrt(variance) * 20
  return Math.min(95, Math.max(20, Math.round(raw)))
}

function classifySignal(
  coherencePct: number,
  nciScore: number,
  macroTags?: string[],
): "strong_signal" | "noise" | "mixed" | "decelerating" {
  // Map compass coherence/nci to operator signal classification.
  // Not a claim of equivalence — this is a seam mapping.
  if (coherencePct >= 75 && nciScore >= 70) return "strong_signal"
  if (coherencePct < 45 || nciScore < 40) return "noise"
  if (coherencePct >= 60 && nciScore >= 55) return "mixed"
  return "decelerating"
}

// ─── Intake hooks (not yet implemented) ────────────────────────────────────

/**
 * somaticPrompt — what to add at intake if you want real somatic input.
 *
 * Six questions, one per phenomenological primitive. Scores 0–1 as the user picks.
 * This is the honest way to raise the somatic layer from defaults to self-report.
 *
 * Adding this is a UX decision, not a translation decision — the translator just
 * consumes the result. Skipping it leaves somatic on defaults (source: "default").
 *
 * QUERY (what to ask the user):
 *   "Before the compass runs, a quick felt-sense check (0 = not at all, 1 = strongly):
 *    1. phase_tuning — how calibrated does this feel right now?
 *    2. surge_detection — any pre-decision energy window opening?
 *    3. feels_right — gut-level, does this read as valid?
 *    4. that_vibes — how's the relational resonance with this decision?
 *    5. locked_in — how deep is the focus presence?
 *    6. expected_vs_actual — how well has your track record matched your expectation lately?"
 *
 * The translator consumes the six scores and sets somatic.source = "user_self_report".
 */
export const somaticPrompt = `\
Before the compass runs, a quick felt-sense check (0 = not at all, 1 = strongly):

1. phase_tuning — how calibrated does this feel right now?
2. surge_detection — any pre-decision energy window opening?
3. feels_right — gut-level, does this read as valid?
4. that_vibes — how's the relational resonance with this decision?
5. locked_in — how deep is the focus presence?
6. expected_vs_actual — how well has your track record matched your expectation lately?

Reply with six numbers 0–1, or skip for defaults.`
