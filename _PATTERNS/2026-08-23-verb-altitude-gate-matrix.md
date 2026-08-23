# The verb × altitude gate matrix — what gets printed at each cut, and what fate it assigns

> Minted 2026-08-23 from the Wing engagement (wing.arcs.care), per Zach's framing: "are we
> basically printing an artifact at each new stage cut?" Yes — and this document is the
> invariant print (ADR-066 ladder: Wing = instance, teardown-page-factory = class, this = invariant).

## The arc: five verbs, each cut prints an artifact through a gate to a fate

| Verb | Artifact printed | Gate / filter | Fates |
|---|---|---|---|
| **Analyze** | Raw forensic teardown (research log → field report) | Source-traceability: every claim to a checkable record | sourced / unsourced (unsourced claims die here) |
| **Assess** | Readable report: claim-vs-record echo map, gauges, objection tables | Claim-vs-record check + severity chips | verified / gap / unresolved (good / bad / ugly) |
| **Evaluate** | Gauntlet run: LAB, BAR, KKL, funhouse, dual bar-raiser, pathogen, inverse, kintsugi | Dual bar-raiser (product-truth vs proof-truth) | pass / conditional pass / fail |
| **Synthesize** | The surface + deck (compression ~1:5) + any minted class (skill) | Ship gates: no-new-claims · em-dash 0 · tripwire · leak · four-width pixels · noindex | ship / hold |
| **Recapitulate** | Shavasana + the counterpart note (DRAFT) | Draft-first (human sends) · register fit · pre-send gauntlet | sent / parked |

Altitude is orthogonal, embedded in every synthesis print: collapsed-H2 deks = exec ·
open sections = operational · PRESENT deck = guided middle · footnotes/forensics = surgical.
Earned fidelity binds them: verified renders sharp, gaps degraded, unresolved grain.

## The prints the arc is missing before "done" (found by this audit)

1. **Ex-ante receipt** (BEFORE the note is sent): expected counterpart response, filed as a
   recoil SSOT (`/recoil-new` → runtime/recoil/generated/<date>-<name>.json, Ex-Ante tab).
   Without it the close-loop has nothing to score against. This is the load-bearing hole.
2. **Pre-send gauntlet run** (counterpart-gauntlet workflow): simulate the counterpart
   reading the artifact + note at high burden of proof. The filter between recapitulated
   and sent. Its receipt is an artifact.
3. **Close-loop print** (`/recoil-close` equivalent): expected-vs-actual once the
   counterpart responds. Gated on #1 existing.
4. **Witness stubs** for naming moments (they otherwise get reconstructed at handoff, which
   ADR-044 treats as dishonest timing).
5. **Handoff print** at session close (CLAUDE.md policy — latest 1–2 live).

## Precedent: the forge pair is the existing shape of stage-printing

`public/forge-pattern.html` (forge.arcs.care) and `public/forge-cut.html`
(forge-cut.arcs.care) are the house precedent Zach named: the **pattern page is the class
print** (the reusable counterpart-forge shape) and the **cut page is the instance print**
(one engagement drilled to real fathoms). Wing repeats the pair one level up:
wing.arcs.care = instance, teardown-page-factory skill = class, this matrix = invariant.
Every future engagement should leave the same trail — an instance surface, a class artifact
when the shape repeats, and a doctrine line when the class repeats.

## Rule of thumb

A stage without a printed artifact is a stage that happened only in conversation — it will
be re-derived at full cost next time. A print without a gate is decoration. A gate without
a fate (ship/hold, sent/parked, pass/fail) doesn't gate anything.
