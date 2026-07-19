export const meta = {
  name: 'recoil-report',
  description: 'Multi-agent recoil report: gather signals, analyze through ARCS operator lenses, adversarially verify every claim, synthesize a provenance-graded report',
  whenToUse: 'Building a recoil/pre-call report on a person or call. Fans out ~12+ agents (~350k tokens); run only on explicit opt-in.',
  phases: [
    { title: 'Gather', detail: 'parallel signal collectors — Gmail, Granola, calendar, git telemetry, LinkedIn (Haiku)', model: 'haiku' },
    { title: 'Profile', detail: 'merge blind signals into one read (Sonnet)', model: 'sonnet' },
    { title: 'Lenses', detail: 'LAB / BAR / SAGE / CURATOR operator lenses (Sonnet)', model: 'sonnet' },
    { title: 'Verify', detail: 'N skeptics per claim, refute-mode (Opus)', model: 'opus' },
    { title: 'Synthesize', detail: 'provenance-graded report (Opus)', model: 'opus' },
  ],
}

// ---- Schemas (force structured returns) ----
const SIGNALS = {
  type: 'object',
  properties: {
    source: { type: 'string' },
    available: { type: 'boolean' },
    signals: { type: 'array', items: { type: 'string' } },
    raw_notes: { type: 'string' },
  },
  required: ['source', 'available', 'signals'],
}
const PROFILE = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    entities: { type: 'array', items: { type: 'string' } },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary'],
}
const CLAIMS = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          evidence: { type: 'string' },
          confidence: { type: 'number' },
        },
        required: ['claim', 'evidence'],
      },
    },
  },
  required: ['lens', 'claims'],
}
const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted'],
}

// ---- Config ----
const subject = (args && args.subject) || 'the subject of this recoil report'
const GATHER = [
  { key: 'gmail', tool: 'Gmail MCP (search_threads / get_thread)', what: 'email history, thread cadence, who-forwarded-to-whom' },
  { key: 'granola', tool: 'Granola MCP (list_meetings / get_meeting_transcript)', what: 'call transcripts, verbatim quotes at the close' },
  { key: 'calendar', tool: 'Google Calendar MCP (search_events / list_events)', what: 'meeting frequency, prep calls, timing' },
  { key: 'git', tool: 'git log / commit trailers (Bash)', what: 'which model authored which week, commit cadence, receipts' },
  { key: 'linkedin', tool: 'WebFetch on the public LinkedIn/profile URL if provided in args', what: 'stated self-concept, founding myth, career formation' },
]
const LENSES = [
  { key: 'LAB', prompt: 'Loki / Advisors / Bayesian — three-lens adversarial reasoning. Surface the uncomfortable read and the base rates.' },
  { key: 'BAR', prompt: 'Risk / ruin assessment — boundary conditions, tail risks, where being wrong is unrecoverable.' },
  { key: 'SAGE', prompt: 'Somatic + epistemic — what the affect proposes vs what the receipts dispose. Separate feeling from evidence.' },
  { key: 'CURATOR', prompt: 'Multi-perspective synthesis — reconcile the other lenses; find the non-obvious throughline.' },
]
const SKEPTICS = 3 // refute-mode verifiers per claim

// ---- 1. Gather (Haiku, parallel roots) ----
phase('Gather')
const gathered = (await parallel(GATHER.map(g => () =>
  agent(
    `Gather signals about ${subject} from ${g.tool}. Focus: ${g.what}. ` +
    `Use ToolSearch to load the tool if needed. If the source is unavailable or empty, return available:false — do not fabricate. ` +
    `Return raw observed signals only, no interpretation.`,
    // Least-privilege: gather must read external systems (MCP/git/web) but is
    // scoped read-only — Explore has no Write/Edit and cannot spawn subagents.
    { label: `gather:${g.key}`, phase: 'Gather', agentType: 'Explore', model: 'haiku', effort: 'low', schema: SIGNALS }
  ).then(r => (r ? { ...r, source: g.key } : null))
))).filter(Boolean).filter(r => r.available)

log(`gathered ${gathered.length}/${GATHER.length} sources`)

// ---- 2. Profile synthesis (Sonnet, barrier) ----
phase('Profile')
const profile = await agent(
  `Merge these blind, independently-gathered signal sets about ${subject} into one coherent read. ` +
  `Note where sources corroborate vs conflict. Do not over-interpret single-source signals.\n\n` +
  JSON.stringify(gathered, null, 2),
  { label: 'profile', phase: 'Profile', agentType: 'recoil-reason', model: 'sonnet', effort: 'medium', schema: PROFILE }
)

// ---- 3. Lenses (Sonnet, parallel) → 4. Verify (Opus, per claim) ----
// pipeline so each lens's claims verify as soon as that lens completes.
const verified = await pipeline(
  LENSES,
  lens => agent(
    `Analyze ${subject} through the ${lens.key} lens: ${lens.prompt}\n\nProfile:\n${JSON.stringify(profile)}\n\n` +
    `Produce specific, falsifiable claims with evidence. Confidence 0-1. No flattery, no hedging.`,
    { label: `lens:${lens.key}`, phase: 'Lenses', agentType: 'recoil-reason', model: 'sonnet', effort: 'high', schema: CLAIMS }
  ),
  (result) => {
    const lens = result && result.lens ? result.lens : '?'
    const claims = (result && result.claims) || []
    return parallel(claims.map(c => () =>
      parallel(Array.from({ length: SKEPTICS }, (_, i) => () =>
        agent(
          `Try hard to REFUTE this claim about ${subject}. Default to refuted:true if the evidence is thin, single-source, ` +
          `affect-driven, or an over-generalization. Claim: "${c.claim}"\nEvidence: "${c.evidence}"`,
          { label: `verify:${lens}#${i}`, phase: 'Verify', agentType: 'recoil-reason', model: 'opus', effort: 'high', schema: VERDICT }
        )
      )).then(votes => {
        const refutations = votes.filter(Boolean).filter(v => v.refuted).length
        return { lens, claim: c, survived: refutations < Math.ceil(SKEPTICS / 2), refutations }
      })
    ))
  }
)

const flat = verified.flat().filter(Boolean)
const confirmed = flat.filter(v => v.survived).map(v => ({ lens: v.lens, ...v.claim }))
const dropped = flat.filter(v => !v.survived).map(v => ({ lens: v.lens, claim: v.claim.claim, refutations: v.refutations }))
log(`claims: ${confirmed.length} confirmed, ${dropped.length} refuted-out`)

// ---- 5. Synthesize (Opus) ----
phase('Synthesize')
const report = await agent(
  `Write a provenance-graded recoil report on ${subject}. Use ONLY the confirmed claims below — each survived ${SKEPTICS} ` +
  `refutation attempts. Render at earned fidelity: state confidence, cite which lens and evidence backs each point, and ` +
  `explicitly note what was dropped and why. Tone: calm, precise, instrument-register (WORLD.md).\n\n` +
  `CONFIRMED:\n${JSON.stringify(confirmed, null, 2)}\n\nDROPPED (for the audit trail):\n${JSON.stringify(dropped, null, 2)}`,
  { label: 'synthesize', phase: 'Synthesize', agentType: 'recoil-reason', model: 'opus', effort: 'high' }
)

return { subject, report, confirmed, dropped, sources: gathered.map(g => g.source) }
