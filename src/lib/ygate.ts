// Compute Y gate — conviction trajectory layer.
// Evaluates the 12D manifold conditions from a compass Receipt + optional prep/parent context.
// Returns Y vector (polarity × conviction × stability → state) and kinematic fields.

interface ParsedCompass {
  nci_score?: number
  coherence_pct?: number
  decision_mode?: string
  door_class?: string
  reasoning?: {
    court?: Array<{ name: string; verdict: string; detail: string }>
    paths?: Array<{ id: string; title: string; detail: string; tag: string; status: string }>
    fated?: {
      facts?: string; assumptions?: string
      tradeoffs?: string; emotions?: string; direction?: string
    }
  }
}

interface PrepContext {
  stakes?: string | null
  horizon?: string | null
  confidence?: number | null
  entity?: string | null
}

interface ParentContext {
  yState?: string | null
  nciScore?: number | null
}

export interface YGateResult {
  yPolarity: string        // BINARY | NONBINARY | ENTANGLED
  yConviction: string      // HIGH | CONTESTED | LOW | EPHEMERAL | COLLAPSED
  yStability: string       // LOCKED | DRIFTING | VOLATILE
  yState: string           // GREEN | YELLOW | RED | FORK | MERGE | DRIFT | SCRATCH | PARADOX | DELTA
  yConvictionPrev: string | null
  yDeltaTrigger: string | null
  yConditions: string      // JSON: [{dim, label, severity}]
  gradientMagnitude: number
  gradientDirection: string // JSON
  flowTopology: string     // CONVERGENT | DIVERGENT | LOOPING | CLIFF
  manifoldCurvature: string // STEEP | MODERATE | FLAT | INVERTED
  renderResolution: string  // SHARP | DEGRADED | GRAIN | MOIRE
}

export function computeYGate(
  parsed: ParsedCompass,
  prep: PrepContext | null,
  parent: ParentContext | null,
  sessionVersion = 0
): YGateResult {
  const nci = parsed.nci_score ?? 50
  const court = parsed.reasoning?.court ?? []
  const paths = parsed.reasoning?.paths ?? []
  const fated = parsed.reasoning?.fated
  const mode = parsed.decision_mode ?? "PLAN"

  const conditions: Array<{ dim: number; label: string; severity: string }> = []

  // 1. NCI < 40 → low coherence
  if (nci < 40) {
    conditions.push({ dim: 1, label: "Low coherence — signal below action threshold", severity: "YELLOW" })
  }

  // 2. Court populated
  if (court.length > 0) {
    const hasBlock = court.some(c => c.verdict === "BLOCK")
    conditions.push({
      dim: 2,
      label: hasBlock ? "Court: blocking condition detected" : "Court: tension flagged",
      severity: hasBlock ? "RED" : "YELLOW",
    })
  }

  // 3. 2+ viable paths → FORK
  const viable = paths.filter(p => p.status !== "blocked")
  if (viable.length >= 2) {
    conditions.push({ dim: 3, label: `${viable.length} viable paths above threshold`, severity: "FORK" })
  }

  // 5. Today + HIGH stakes → irreversibility check
  if (prep?.horizon === "TODAY" && prep?.stakes === "HIGH") {
    conditions.push({ dim: 5, label: "Same-day commitment at high stakes — irreversibility check", severity: "YELLOW" })
  }

  // 6. Parent was RED → still blocked
  if (parent?.yState === "RED") {
    conditions.push({ dim: 6, label: "Parent receipt blocked — re-author constraints before advancing", severity: "RED" })
  }

  // 9. Ruin language in FATED
  const fatadText = [fated?.tradeoffs, fated?.direction, fated?.emotions]
    .filter(Boolean).join(" ").toLowerCase()
  if (fatadText.includes("ruin") || fatadText.includes("catastrophic") || fatadText.includes("irreversible loss")) {
    conditions.push({ dim: 9, label: "Ruin risk detected in FATED decomposition", severity: "RED" })
  }

  // 10. Prep confidence = 1 (lost) + no Court
  if (prep?.confidence === 1 && court.length === 0) {
    conditions.push({ dim: 10, label: "Entering decision lost — orient before committing", severity: "YELLOW" })
  }

  // 12. COURT mode + no prep → request calibration
  if (mode === "COURT" && !prep) {
    conditions.push({ dim: 12, label: "High-stakes mode without calibration — dial up resolution", severity: "YELLOW" })
  }

  // Drift: 5+ session versions without artifact
  if (sessionVersion >= 5) {
    conditions.push({ dim: 8, label: "Session v5+ — land the plane or keep exploring?", severity: "YELLOW" })
  }

  // ── Compute Y vector ──────────────────────────────────────────────────────
  const hasFork = conditions.some(c => c.severity === "FORK")
  const hasRed  = conditions.some(c => c.severity === "RED")
  const hasYellow = conditions.some(c => c.severity === "YELLOW")

  // Polarity
  let yPolarity = "BINARY"
  if (hasFork && hasRed) yPolarity = "ENTANGLED"
  else if (hasFork) yPolarity = "NONBINARY"

  // Conviction
  let yConviction = "HIGH"
  if (prep?.confidence === 1)         yConviction = "EPHEMERAL"
  else if (hasRed || nci < 40)        yConviction = "LOW"
  else if (hasYellow || nci < 65)     yConviction = "CONTESTED"

  // Delta: conviction shifted from parent
  let yConvictionPrev: string | null = null
  let yDeltaTrigger: string | null = null
  if (parent?.nciScore !== undefined && parent.nciScore !== null) {
    const prev = parent.nciScore >= 65 ? "HIGH" : parent.nciScore >= 40 ? "CONTESTED" : "LOW"
    if (prev !== yConviction) {
      yConvictionPrev = prev
      yDeltaTrigger = "Conviction shifted after prep calibration"
    }
  }

  // Stability
  let yStability = "LOCKED"
  if (hasRed || hasFork)            yStability = "VOLATILE"
  else if (hasYellow || sessionVersion >= 3) yStability = "DRIFTING"

  // State
  let yState = "GREEN"
  if (sessionVersion >= 5)            yState = "DRIFT"
  else if (hasRed)                    yState = "RED"
  else if (hasFork)                   yState = "FORK"
  else if (yConviction === "EPHEMERAL") yState = "SCRATCH"
  else if (yConvictionPrev && yConviction !== yConvictionPrev) yState = "DELTA"
  else if (hasYellow)                 yState = "YELLOW"

  // ── Kinematic fields ──────────────────────────────────────────────────────
  const gradientMagnitude = nci / 100

  let flowTopology = "CONVERGENT"
  if (hasRed && court.length > 0)   flowTopology = "CLIFF"
  else if (hasFork)                 flowTopology = "DIVERGENT"
  else if (sessionVersion >= 3 && !hasFork && !hasRed) flowTopology = "LOOPING"

  let manifoldCurvature = "MODERATE"
  if (hasRed)       manifoldCurvature = "INVERTED"
  else if (nci >= 70) manifoldCurvature = "STEEP"
  else if (nci < 40)  manifoldCurvature = "FLAT"

  let renderResolution = "SHARP"
  if (yPolarity === "ENTANGLED")              renderResolution = "MOIRE"
  else if (nci < 40 || yStability === "VOLATILE")  renderResolution = "GRAIN"
  else if (nci < 60 || yStability === "DRIFTING")  renderResolution = "DEGRADED"

  return {
    yPolarity,
    yConviction,
    yStability,
    yState,
    yConvictionPrev,
    yDeltaTrigger,
    yConditions: JSON.stringify(conditions),
    gradientMagnitude,
    gradientDirection: JSON.stringify({ nci: nci / 100, mode, door: parsed.door_class }),
    flowTopology,
    manifoldCurvature,
    renderResolution,
  }
}
