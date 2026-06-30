// ScanSignal + ScanFeedback type contracts
//
// These interfaces define the shape of every TEXT JSON field in the ScanSignal
// and ScanFeedback Prisma models. Always JSON.stringify() before write,
// JSON.parse() after read — same pattern as the rest of this codebase.
//
// Vector field convention: signalEmbedding / feedbackEmbedding store a
// serialized float[] here. The Supabase pgvector companion column (raw migration,
// not managed by Prisma) holds the actual vector(1536) for cosine search.

// ─── Source blobs ─────────────────────────────────────────────────────────────

export type SourceBlobType = 'linkedin_pdf' | 'export_zip' | 'csv' | 'other'

export interface SourceBlob {
  type: SourceBlobType
  url: string
  uploadedAt: string // ISO8601
}

// ─── Genome threads ───────────────────────────────────────────────────────────

export interface GenomeThread {
  assessment: string
  evidence: string
  locked: boolean          // true = LOCK gate passed, thread confirmed by feedback
}

export interface GenomeThreads {
  red: GenomeThread        // Recurring risk / recurring question
  gold: GenomeThread       // Working asset / compounding advantage
  green: GenomeThread      // Conviction point / clearest expression
  vermillion: GenomeThread // Active constraint / packaging tension
}

// ─── Signal contrast ──────────────────────────────────────────────────────────

export interface SignalContrast {
  stated: string[]   // What the profile/document says
  observed: string[] // What the full signal actually contains
  gap: string        // The single sentence summarizing the delta
}

// ─── Archetype stack ──────────────────────────────────────────────────────────

export type ArchetypeType =
  | 'Builder' | 'Navigator' | 'Illuminator' | 'Curator'
  | 'Catalyst' | 'Steward' | 'Pioneer' | 'Synthesizer'

export interface ArchetypeEntry {
  type: ArchetypeType | string
  weight: number               // 0–1, dominant archetype highest
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
}

// ─── Evidence ledger ──────────────────────────────────────────────────────────

export interface EvidenceLedgerEntry {
  period: string     // "2013–2022"
  role: string
  domain: string
  expression: string // how the genome expressed in this role
  verified: boolean  // cross-checked against export dates
}

// ─── Platform inferences (LinkedIn ad-targeting model) ───────────────────────

export interface PlatformInference {
  category: string
  value: string
}

// ─── Network resonance (pair / network scan types) ────────────────────────────

export interface NetworkResonance {
  commonThreads: string[]
  divergencePoints: string[]
  combinedGap: string
}

// ─── Feedback payload ─────────────────────────────────────────────────────────

export type FeedbackValence =
  | 'resonates' | 'partial' | 'override'   // somatic
  | 'accurate'  | 'inaccurate'             // rational
  | 'current'   | 'stale'                 // contextual
  | 'lands'     | 'misses'                // rhetorical

export type FeedbackIntensity = 'strong' | 'moderate' | 'flat'

// Emotion taxonomy: the specific emotion carries diagnostic signal.
// Pride=confirmed; Grief=true-but-suppressed; Defensiveness=accurate-and-hard-to-see;
// Relief=names-unspoken-truth; Flatness=thread-missed-reframe-not-recalibrate.
export type DiagnosticEmotion =
  | 'pride' | 'grief' | 'defensiveness' | 'relief' | 'flatness' | string

export interface RationalCorrection {
  field: string      // which field in the signal this corrects
  correction: string
}

export interface FeedbackAxis<V extends string = string> {
  valence: V
  intensity: FeedbackIntensity
  note: string
}

export interface EmotionalAxis extends FeedbackAxis {
  emotion: DiagnosticEmotion
}

export interface RationalAxis extends FeedbackAxis<'accurate' | 'partial' | 'inaccurate'> {
  corrections: RationalCorrection[]
}

export interface FeedbackPayload {
  somatic:    FeedbackAxis<'resonates' | 'partial' | 'override'>
  emotional:  EmotionalAxis
  rational:   RationalAxis
  contextual: FeedbackAxis<'current' | 'partial' | 'stale'>
  rhetorical: FeedbackAxis<'lands' | 'partial' | 'misses'>
}

// ─── Delta gate logic ─────────────────────────────────────────────────────────
//
// Derived from the feedback payload at write time. Stored as a scalar in
// ScanFeedback.deltaGateDecision for queryability.
//
// strong + resonates  → LOCK (confirmed, advance thread)
// strong + disagrees  → LOCK (defensiveness confirms — intensity IS the signal)
// moderate + any      → WATCH (partial signal, accumulate more)
// flat + any          → REFRAME (thread missed entirely, not a recalibration)
// explicit override   → HOLD (contradicts genome read, requires Architect review)

export type DeltaGateDecision = 'LOCK' | 'WATCH' | 'HOLD' | 'REFRAME'

export function deriveDeltaGate(payload: FeedbackPayload): DeltaGateDecision {
  const intensities = [
    payload.somatic.intensity,
    payload.emotional.intensity,
    payload.rational.intensity,
    payload.contextual.intensity,
    payload.rhetorical.intensity,
  ]
  const hasOverride = [
    payload.somatic.valence,
    payload.emotional.valence,
    payload.contextual.valence,
    payload.rhetorical.valence,
  ].includes('override')

  const strongCount = intensities.filter(i => i === 'strong').length
  const flatCount   = intensities.filter(i => i === 'flat').length

  if (hasOverride && strongCount >= 3) return 'HOLD'
  if (strongCount >= 3) return 'LOCK'
  if (flatCount >= 4)   return 'REFRAME'
  return 'WATCH'
}

export function deriveOverallIntensity(payload: FeedbackPayload): FeedbackIntensity {
  const counts = { strong: 0, moderate: 0, flat: 0 }
  for (const axis of [payload.somatic, payload.emotional, payload.rational, payload.contextual, payload.rhetorical]) {
    counts[axis.intensity]++
  }
  if (counts.strong >= 3) return 'strong'
  if (counts.flat >= 4)   return 'flat'
  return 'moderate'
}

// ─── Annotation blobs ─────────────────────────────────────────────────────────

export interface AnnotationBlob {
  type: 'annotated_scan' | 'voice_memo' | string
  url: string
}

// ─── Convenience: parse helpers ───────────────────────────────────────────────

export function parseGenomeThreads(raw: string): GenomeThreads {
  return JSON.parse(raw || '{}') as GenomeThreads
}
export function parseArchetypeStack(raw: string): ArchetypeEntry[] {
  return JSON.parse(raw || '[]') as ArchetypeEntry[]
}
export function parseEvidenceLedger(raw: string): EvidenceLedgerEntry[] {
  return JSON.parse(raw || '[]') as EvidenceLedgerEntry[]
}
export function parseSignalContrast(raw: string): SignalContrast {
  return JSON.parse(raw || '{}') as SignalContrast
}
export function parseFeedbackPayload(raw: string): FeedbackPayload {
  return JSON.parse(raw || '{}') as FeedbackPayload
}
export function parseSourceBlobUrls(raw: string | null | undefined): SourceBlob[] {
  return JSON.parse(raw || '[]') as SourceBlob[]
}
