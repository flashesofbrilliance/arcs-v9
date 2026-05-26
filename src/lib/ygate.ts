// Compute Y gate — conviction trajectory layer.
// Evaluates manifold conditions from a compass Receipt + optional prep/parent context.
// Returns canonical DEWY Y-vector: polarity × conviction × stability → yGateScore.
//
// Canonical enums (dewy-receipt-schema-v1.json):
//   polarity:   SCRATCH | YELLOW | PARADOX | FORK | DELTA | GREEN | LOCKED
//   conviction: LOW | MEDIUM | HIGH
//   stability:  SHIFTING | CONTESTED | STABLE
//   driftState: ON_TRACK | DRIFTING | LOCKED | LANDED

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
  yState?: string | null   // holds yPolarity value of parent receipt
  nciScore?: number | null
}

export interface YGateResult {
  // ── Canonical Y-vector (dewy-receipt-schema-v1.json) ──────────────────────
  yPolarity: string        // SCRATCH | YELLOW | PARADOX | FORK | DELTA | GREEN | LOCKED
  yConviction: string      // LOW | MEDIUM | HIGH
  yStability: string       // SHIFTING | CONTESTED | STABLE
  yState: string           // mirrors yPolarity (kept for backward compat + indexed queries)
  yGateScore: string       // JSON: {polarity, conviction, stability, render_resolution, visual_treatment}
  driftState: string       // ON_TRACK | DRIFTING | LOCKED | LANDED
  // ── Delta tracking ────────────────────────────────────────────────────────
  yConvictionPrev: string | null
  yDeltaTrigger: string | null
  yConditions: string      // JSON: [{dim, label, severity}]
  // ── Override (set externally, not computed here) ───────────────────────────
  // yOverride / yOverrideAt / yOverrideNote — Prisma defaults handle these
  // ── Kinematic ─────────────────────────────────────────────────────────────
  gradientMagnitude: number
  gradientDirection: string // JSON
  flowTopology: string     // CONVERGENT | DIVERGENT | LOOPING | CLIFF
  manifoldCurvature: string // STEEP | MODERATE | FLAT | INVERTED
  renderResolution: string  // SHARP | DEGRADED | GRAIN | MOIRE
}

// Visual treatment per render resolution (WORLD.md Render Scale)
const VISUAL_TREATMENT: Record<string, { opacity: number; font_weight: number; tracking: string }> = {
  SHARP:    { opacity: 1.0,  font_weight: 500, tracking: "normal" },
  DEGRADED: { opacity: 0.85, font_weight: 400, tracking: "+0.01em" },
  GRAIN:    { opacity: 0.70, font_weight: 300, tracking: "+0.02em" },
  MOIRE:    { opacity: 0.60, font_weight: 300, tracking: "+0.03em" },
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

  // 4. PARADOX: paths exist but none clearly dominant (viable === 2 and nci < 60)
  if (viable.length === 2 && nci < 60) {
    conditions.push({ dim: 4, label: "Two paths, low coherence — options may be non-separable", severity: "PARADOX" })
  }

  // 5. Today + HIGH stakes → irreversibility check
  if (prep?.horizon === "TODAY" && prep?.stakes === "HIGH") {
    conditions.push({ dim: 5, label: "Same-day commitment at high stakes — irreversibility check", severity: "YELLOW" })
  }

  // 6. Parent was at existential/cliff state
  if (parent?.yState && ["YELLOW", "DELTA", "SCRATCH"].includes(parent.yState)) {
    conditions.push({ dim: 6, label: "Parent receipt unresolved — re-evaluate before advancing", severity: "YELLOW" })
  }

  // 9. Ruin language in FATED
  const fatedText = [fated?.tradeoffs, fated?.direction, fated?.emotions]
    .filter(Boolean).join(" ").toLowerCase()
  if (fatedText.includes("ruin") || fatedText.includes("catastrophic") || fatedText.includes("irreversible loss")) {
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

  // Drift: 5+ session versions without artifact (time-quality-attribution-rom.json §drift_sentinel)
  if (sessionVersion >= 5) {
    conditions.push({ dim: 8, label: "Session v5+ — land the plane or keep exploring?", severity: "YELLOW" })
  }

  // ── Compute Y-vector ──────────────────────────────────────────────────────
  const hasParadox = conditions.some(c => c.severity === "PARADOX")
  const hasFork    = conditions.some(c => c.severity === "FORK")
  const hasRed     = conditions.some(c => c.severity === "RED")
  const hasYellow  = conditions.some(c => c.severity === "YELLOW")

  // Polarity (canonical schema: SCRATCH|YELLOW|PARADOX|FORK|DELTA|GREEN|LOCKED)
  let yPolarity = "GREEN"
  if (prep?.confidence === 1 || (nci < 40 && !hasFork && !hasParadox)) {
    yPolarity = "SCRATCH"
  } else if (hasParadox) {
    yPolarity = "PARADOX"
  } else if (hasFork) {
    yPolarity = "FORK"
  } else if (hasRed) {
    // Existential risk → DELTA (inflection point); BAR macro handles ruin signaling
    yPolarity = "DELTA"
  } else if (hasYellow || nci < 65) {
    yPolarity = "YELLOW"
  }

  // Conviction (LOW | MEDIUM | HIGH)
  let yConviction = "HIGH"
  if (prep?.confidence === 1 || hasRed || nci < 40) {
    yConviction = "LOW"
  } else if (hasYellow || nci < 65) {
    yConviction = "MEDIUM"
  }

  // Delta: conviction shifted from parent
  let yConvictionPrev: string | null = null
  let yDeltaTrigger: string | null = null
  if (parent?.nciScore !== undefined && parent.nciScore !== null) {
    const prev = parent.nciScore >= 65 ? "HIGH" : parent.nciScore >= 40 ? "MEDIUM" : "LOW"
    if (prev !== yConviction) {
      yConvictionPrev = prev
      yDeltaTrigger = "Conviction shifted after prep calibration"
      // If conviction moved and no stronger polarity signal, mark DELTA
      if (yPolarity === "GREEN" || yPolarity === "YELLOW") yPolarity = "DELTA"
    }
  }

  // Stability (SHIFTING | CONTESTED | STABLE)
  let yStability = "STABLE"
  if (hasRed || hasParadox || hasFork) {
    yStability = "SHIFTING"
  } else if (hasYellow || sessionVersion >= 3) {
    yStability = "CONTESTED"
  }

  // Drift state (time-quality-attribution-rom.json §drift_sentinel)
  let driftState = "ON_TRACK"
  if (yPolarity === "GREEN" && yConviction === "HIGH" && yStability === "STABLE") {
    driftState = "LOCKED"
  } else if (sessionVersion >= 5) {
    driftState = "DRIFTING"
  }

  // yState mirrors yPolarity (backward compat for indexed queries and compass response)
  const yState = yPolarity

  // ── Render resolution (WORLD.md Render Scale) ─────────────────────────────
  let renderResolution = "SHARP"
  if (yPolarity === "PARADOX") {
    renderResolution = "MOIRE"
  } else if (yPolarity === "SCRATCH" || yPolarity === "DELTA" || yStability === "SHIFTING") {
    renderResolution = "GRAIN"
  } else if (yPolarity === "YELLOW" || yPolarity === "FORK" || yStability === "CONTESTED" || nci < 60) {
    renderResolution = "DEGRADED"
  }

  const yGateScore = JSON.stringify({
    polarity: yPolarity,
    conviction: yConviction,
    stability: yStability,
    render_resolution: renderResolution,
    visual_treatment: VISUAL_TREATMENT[renderResolution],
  })

  // ── Kinematic fields ──────────────────────────────────────────────────────
  const gradientMagnitude = nci / 100

  let flowTopology = "CONVERGENT"
  if (hasRed && court.length > 0)            flowTopology = "CLIFF"
  else if (hasFork)                          flowTopology = "DIVERGENT"
  else if (sessionVersion >= 3 && !hasFork && !hasRed) flowTopology = "LOOPING"

  let manifoldCurvature = "MODERATE"
  if (hasRed || yPolarity === "DELTA")  manifoldCurvature = "INVERTED"
  else if (nci >= 70)                   manifoldCurvature = "STEEP"
  else if (nci < 40)                    manifoldCurvature = "FLAT"

  return {
    yPolarity,
    yConviction,
    yStability,
    yState,
    yGateScore,
    driftState,
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
