export const meta = {
  name: 'counterpart-gauntlet',
  description: 'Parameterized pre-send gauntlet for ANY counterpart artifact family: simulate the counterpart across N facets at high burden of proof, then adversarially verify + synthesize register-tuned fixes. Pass the counterpart via args.',
  phases: [
    { title: 'Counterpart reads it', detail: 'persona facets, high burden of proof' },
    { title: 'Verify + synthesize', detail: 'reject over-flags, dedup, rank, prescribe fixes' },
  ],
}

// ---------------------------------------------------------------------------
// args (all counterpart-specific context is passed in — nothing hardcoded):
// {
//   counterpart: "Yuri Kleban",
//   repo: "/abs/path/to/worktree",
//   transcript: "/abs/path/primary-transcript.txt",   // PRIMARY SOURCE (ground truth for what they said)
//   comms_thread: "/abs/path/full-comms-thread.txt",   // optional: the full LinkedIn/email thread (vibe)
//   surfaces: [ { label:"one-door", html:"public/yuri.html", ssot:"runtime/recoil/generated/..onedoor.json" }, ... ],
//   memory: ["/abs/path/mem.md", ...],                 // register + situational memory files
//   register: "one paragraph: who they are, how they talk, what loses them (from the transcript+memory)",
//   already_healed: "one paragraph: what was fixed this pass — do NOT re-flag unless regressed",
//   facets: [ {key, mandate}, ... ]                    // optional; defaults to the 6 below
// }
// ---------------------------------------------------------------------------
const A = args || {}
if (!A.counterpart || !A.transcript || !Array.isArray(A.surfaces) || !A.surfaces.length) {
  throw new Error('counterpart-gauntlet: args must include {counterpart, transcript, surfaces:[{label,html,ssot}]}. See the header.')
}
const REPO = A.repo || ''
const surfLines = A.surfaces.map(s => `- ${REPO}/${s.html}` + (s.ssot ? `  (+ SSOT ${REPO}/${s.ssot})` : '')).join('\n')
const memLines = (A.memory || []).map(m => `- ${m}`).join('\n') || '(none passed)'

// Mechanical baseline (optional): the deterministic defect classes already
// swept by scripts/gauntlet_prepass.py BEFORE this run (banned lexicon,
// cross-surface dup, false precision, employer over-exposure, leak_check
// verdict). Injected so facets do NOT re-hunt these classes and the synth
// dedupes against them — the token-savings-bank pre-pass lever (ADR-075,
// _SPECS/gauntlet-cba-v1.md). Additive only: no facet or judgment read is
// removed, so catch-rate cannot drop. Pass args.mechanical_baseline = the
// path the prepass wrote (--out), or inline the JSON as args.mechanical_baseline_json.
let baselineBlock = ''
const rawBaseline = A.mechanical_baseline_json ||
  (A.mechanical_baseline ? `(read the JSON at ${REPO ? REPO + '/' : ''}${A.mechanical_baseline})` : '')
if (rawBaseline) {
  baselineBlock = `
MECHANICAL BASELINE (already caught DETERMINISTICALLY by scripts/gauntlet_prepass.py):
${typeof rawBaseline === 'string' ? rawBaseline : JSON.stringify(rawBaseline)}
Do NOT re-flag anything already in this baseline — those classes (banned lexicon,
cross-surface duplication, false precision, employer over-exposure) were checked by
script and are covered. Spend your read on the JUDGMENT your facet is for. If the
baseline's leak_check.verdict is not "clean", escalate that as a pathogen.
`
}

const CTX = `
You are simulating ${A.counterpart} reading an artifact family that is about to be sent to them. This is a
HIGH-BURDEN-OF-PROOF adversarial gauntlet: assume the work is flawed and find what breaks. But you will be
verified — every crack must trace to their actual words (the transcript / comms thread) or a documented
fact (the memory). Hallucinated or already-healed flags are REJECTED, so do not pad.

READ THESE FIRST (ground truth):
- PRIMARY transcript (the ONLY source for what they actually said): ${A.transcript}
${A.comms_thread ? `- FULL comms thread (their real register + vibe, beyond one call): ${A.comms_thread}` : ''}
- Register + situational memory:
${memLines}

THE LIVE ARTIFACTS UNDER REVIEW (read the rendered HTML; skim the SSOTs for exact copy):
${surfLines}

WHO THEY ARE (register): ${A.register || '(derive from the transcript + comms thread + memory)'}

${A.already_healed ? `ALREADY HEALED (do NOT re-flag unless REGRESSED or a NEW problem appears):\n${A.already_healed}\n` : ''}${baselineBlock}
Your job for your assigned facet: read as THIS person, find the pathogens (trust-breakers), cracks
(register misfits, resonance failures), and breaks (things that would make you cool off, glaze, or feel
managed / sized as a lead). Ground each in a transcript/comms line or a memory fact. Prescribe a fix in
THEIR register. Also name what genuinely resonates so it is not over-cut.
`

// Default 6 facets. These generalize; override per-counterpart via args.facets when their psychology differs.
const DEFAULT_FACETS = [
  { key: 'builder', mandate: `FACET: THE MOST TECHNICAL / REVERSE-ENGINEER version of them. Pull apart every mechanism, number, and visual; scrutinize any chart/precision hardest. Where is there false precision, an unfalsifiable claim, a fence claimed both ways, a number they'd hover and challenge, copy that contradicts the data beneath it? Does the "machine" billing point at the actual mechanism or the prettiest/shallowest surface?` },
  { key: 'practitioner', mandate: `FACET: THE PRACTITIONER who already does (part of) this. Does it RESPECT that they solved part of the problem, or explain their own value back to them / assert an unverifiable negative about their shop? Is the genuinely NEW thing named plainly, or buried? Is the core sequence legible to someone who lives in this?` },
  { key: 'skeptic', mandate: `FACET: THE HYPE-ALLERGIC SKEPTIC. Every oversell, every word they'd never say at dinner, every tell that a human "positioned" them, every place a single moment is inflated into more than it was. Where does a disclaimer protest too much and become the tell?` },
  { key: 'connector', mandate: `FACET: THE GENEROUS, NO-ASK version. Does it honor their nothing-to-sell energy or feel transactional / managed / paced? Does anything scope their world (org, partners, budget) as a rollout you get to plan — sizing them as a lead? Is any reciprocity/curiosity toward THEM present, or is it 100% my-read-of-you (one-directional)?` },
  { key: 'situational', mandate: `FACET: THEIR SITUATIONAL/STRATEGIC self (career arc, incentives, what they're hedging). Does it read their situation right? Does it over-anchor to a fragile/seat-dependent path, over-steer, or project a narrative onto their life they didn't ask for? Is the balance honest and light?` },
  { key: 'bitesize', mandate: `FACET: THE BUSIEST, MOST BITE-SIZE reader. Is it self-explanatory (what is this / who's it for / how do I use it) without work? Where does volume, density, or cross-surface repetition lose you? Would you actually reach the good part, or bounce? Would you forward it?` },
]
const FACETS = (Array.isArray(A.facets) && A.facets.length) ? A.facets : DEFAULT_FACETS

const FINDING_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    facet: { type: 'string' },
    cracks: { type: 'array', items: { type: 'object', additionalProperties: false, properties: {
      severity: { type: 'string', enum: ['pathogen', 'crack', 'break', 'nit'] },
      surface: { type: 'string' }, location: { type: 'string' }, quote: { type: 'string' },
      why_fails: { type: 'string' }, basis: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'surface', 'why_fails', 'basis', 'fix'] } },
    resonates: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
  }, required: ['facet', 'cracks', 'resonates', 'verdict'],
}
const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    verified: { type: 'array', items: { type: 'object', additionalProperties: false, properties: {
      rank: { type: 'number' }, severity: { type: 'string', enum: ['pathogen', 'crack', 'break', 'nit'] },
      surface: { type: 'string' }, location: { type: 'string' }, quote: { type: 'string' },
      issue: { type: 'string' }, basis: { type: 'string' }, fix: { type: 'string' },
      confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
      facets_that_flagged: { type: 'array', items: { type: 'string' } },
    }, required: ['severity', 'surface', 'issue', 'basis', 'fix', 'confidence'] } },
    rejected_overflags: { type: 'array', items: { type: 'object', additionalProperties: false, properties: {
      claim: { type: 'string' }, why_rejected: { type: 'string' },
    }, required: ['claim', 'why_rejected'] } },
    keep_dont_touch: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
  }, required: ['verified', 'rejected_overflags', 'keep_dont_touch', 'verdict'],
}

phase('Counterpart reads it')
const finds = (await parallel(FACETS.map(f => () =>
  agent(CTX + '\n\n=== YOUR ASSIGNED FACET ===\n' + f.mandate, { label: `read:${f.key}`, phase: 'Counterpart reads it', schema: FINDING_SCHEMA })
))).filter(Boolean)

phase('Verify + synthesize')
const synth = await agent(
  CTX + `\n\n=== YOUR JOB: ADVERSARIAL VERIFIER + SYNTHESIZER ===\n` +
  `The facets each produced findings (below). For EACH crack: independently verify it against the transcript` +
  ` / comms thread / memory. REJECT over-flags (hallucinated, already-healed, taste-not-defect, ungrounded) ` +
  `with a reason. For survivors: dedup across facets, rank by relationship-cost (pathogens first), assign ` +
  `confidence, write a concrete fix IN THEIR REGISTER. Consolidate keep_dont_touch so nothing strong is ` +
  `over-cut. A warm, technical, hype-allergic reader is the bar. ` +
  (rawBaseline ? `A MECHANICAL BASELINE was swept by script before this run (in the context above); any agent ` +
    `finding that merely repeats a baseline class is already-caught — fold it in, do not double-count it, ` +
    `and if the baseline's leak_check.verdict is not "clean" rank that FIRST as a pathogen. ` : '') +
  `Findings:\n` + JSON.stringify(finds),
  { label: 'verify+synthesize', phase: 'Verify + synthesize', schema: SYNTH_SCHEMA, effort: 'high' }
)

return { counterpart: A.counterpart, facet_count: finds.length, raw_findings: finds, synthesis: synth }
