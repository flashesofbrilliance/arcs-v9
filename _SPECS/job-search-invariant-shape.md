# Job-Search Invariant Shape (the constitution)

> Doc: SPEC-2026-09-12-JOB-SEARCH-INVARIANT-001
> Status: DRAFT, ratified-in-principle via triune convergence 2026-09-12 (Claude Code / Hermes / Perplexity)
> Governs: PROP-2026-09-12-USERN-EXTENSIBILITY-001 (the topology conforms to this; this does not conform to it)
> Companion: `_STATE/job-search/architect-review-triune-productization.md` (grounded verdict)

## 0. Why this is canon

The productization proposal is an org chart: which repo runs which layer. This is the constitution:
the shape that must hold for the system to work for User0 (Zach) AND to ripple to UserN. When the two
conflict, this wins. The proposal's layers are a lawful deployment of the loop below; they are not the
loop. This exists because four prior front-end studies (`job-tracker-pro`, `jobflow-pwa`,
`job-search-optimizer-v2`, `job-search-tracker-pro`) drew the dashboard before the substrate existed.
They were requirement-discovery, not failures. This spec is the compiled form of what they kept reaching for.

## 1. The invariant shape

**Z. Sovereign Zero (the only per-user part).** Each user declares their own frame: real *evidence*
(receipts: resume, LinkedIn export, work), a *target shape* (what they aim at), and *constraints*
(their DEWY state). No canonical origin. Zach's zero is not anyone's zero.

Then one loop, identical for User0 and UserN:

| Stage | Invariant primitive | User0 instance (this session) | Topology owner |
|-------|---------------------|-------------------------------|----------------|
| 1. Ingest | heterogeneous sources to one normalized, deduped, watermarked opportunity record | LinkedIn digests + Greenhouse/Ashby/Lever JSON; Perplexity scout dossiers | Perplexity (sensor) + arcs-v9 pipeline |
| 2. Prior | versioned, pluggable rubric scores fit as a lawful transform, never a global truth | `target-role-scan.json` v1.3 (mission lens) + `bridge-scan.json` (bridge lens) | resume-tailor-skill / arcs-v9 |
| 3. Gate | fit x winnability (req-reality x competition-density x warm-path); a shot counts only where the gate is real | the Fanatics lesson; the shoot-to-win quadrant; the scout ternary ATTAINABLE/TRAP/UNDECIDABLE | Perplexity verdict + scorer |
| 4. Act (HITL) | human fires; machine scaffolds, never overrules revealed preference | swipe + forge / resume-tailor; UNDECIDABLE routes to human premortem | Hermes (actuator) + human |
| 5. Posterior | every shot gets an evidence-backed receipt; no inferred closes | laneStatus outcomes backfilled from the inbox, never guessed; Supabase decision_receipt | Hermes + arcs-v9 |
| 6. Falsify | pre-registered hypotheses test the map against the terrain; outcomes recalibrate the instrument | the hypothesis ledger (H1-H4 + NULL ruin-check); H4 audits the rubric itself | Claude Code (architect) |

## 2. The six preserved invariants (non-negotiable across every change of basis)

1. **Sovereign zero.** Each user's own frame; no imposed origin.
2. **Falsifiable prior.** The rubric is a testable hypothesis, pre-registered before counting, never a
   self-validating oracle. (This is the primitive the proposal omitted; it is added here.)
3. **Winnability gate.** Fit is necessary, not sufficient. The gate must be real. (The anti-Fanatics invariant.)
4. **Evidence-backed posterior.** Receipts, not vibes. A shot without a captured outcome did not happen.
5. **HITL sovereignty.** Scaffold cognition; never compress or overrule revealed preference. UNDECIDABLE
   goes to a human, not an auto-score.
6. **Instance/class seam.** Tenant data stays private to its zero; the engine is the shared class;
   extraction to the shared class graduates on proof, never decree.

Everything else (which sources, which rubric weights, which UI, LinkedIn vs Lever) is a lawful transform
that is allowed to vary. That variance is the line between what ripples and what is yours alone.

## 3. Ripple property

Only **Z** is instance. Stages 1-6 are the class. Change the zero, run it through the same lawful
transforms, get a different atlas. UserN is not a rebuild; it is a new zero. The four studies could not
ripple because they *were* the zero: front-end hard-coded to Zach with no class beneath. The seam is
what they were missing.

**Extraction is gated, not decreed.** The class graduates to its shared home (hermes-agent, composing
resume-tailor-skill) only after User0's own loop shows a real conversion attributable to the pipeline
(at least one screen/interview). Extracting before proof is how the fifth study joins the graveyard.

## 4. Mapping to the Triune topology (PROP-...-001)

- Perplexity = sensor: Stage 1 intake + Stage 3 verdict. Writes `_INBOX/evidence/` only.
  Output contract: `role-dossier-schema.json` (the sensor owns its own output shape).
- resume-tailor-skill = the portable class core (Stage 2). Verified User0-clean (0 hardcoded refs).
- Hermes = actuator: Stage 4 render + Stage 5 receipt. Local-first; PII boundary enforced by gate.
- arcs-v9 = presentation + the User0 tenant instance (the board, the ledger, the outcomes).
- Claude Code = architect: Stage 6 (the ledger / falsification) + contracts + this constitution.

## 5. Design lineage (throwaway context, durable learning)

| Prior artifact | What it reached for | Maps to |
|---|---|---|
| job-tracker-pro / job-search-tracker-pro | tracking the pipeline | Stage 1 + 5 (never closed the falsification loop) |
| jobflow-pwa | the surface / client shell | Stage 4 presentation |
| job-search-optimizer-v2 | scoring / ranking | Stage 2 prior (no winnability gate) |
| resume-tailor-skill | honesty-graded tailoring | Stage 2, extracted correctly (field-tested first) |
| arcs-field-scan | LinkedIn/PDF to scan report | Stage Z (evidence intake) |
| arcs-intel-protocol | forkable per-person protocol | the ripple property itself |

The convergence across four independent studies on the same shape is the strongest evidence the
invariant is real and not imposed.

## 6. Convergence record

Ratified-in-principle 2026-09-12 by three nodes, each grounding against runtime state (not the draft):
Claude Code (this spec + Stage 6), Hermes (topology + schema + PII gate), Perplexity (Stage 1/3 sensor
contract). Grounded verdict, open refinements, and verified-vs-described findings: see the companion.
