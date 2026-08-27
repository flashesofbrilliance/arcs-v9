# ADR-068 — The verb × altitude gate matrix: every stage cut prints an artifact, through a gate, to a fate

**Status:** DECIDED (doctrine — promotion of `_PATTERNS/2026-08-23-verb-altitude-gate-matrix.md`)
**Date:** 2026-08-23
**Y-state:** GREEN — the full arc ran end-to-end on the Wing engagement before it was named; the matrix describes what already happened, not what should
**Sequence:** allocated via oracle (`scripts/oracle.py next adr` → 68; counter reconciled 65→67 first, since 066/067 were minted off-oracle)
**Ladder position:** the invariant print of the ADR-066 ladder — wing.arcs.care (instance) → `.claude/skills/teardown-page-factory/` (class) → this matrix (invariant)

## D — The Decision

The five-verb arc (analyze → assess → evaluate → synthesize → recapitulate) is not a
narrative convention; it is a **print schedule**. Each verb's stage cut MUST print an
artifact, pass it through a named gate, and assign it a fate. A stage without a print
happened only in conversation and will be re-derived at full cost; a print without a gate
is decoration; a gate without a fate gates nothing.

| Verb | Artifact printed | Gate / filter | Fates |
|---|---|---|---|
| **Analyze** | Raw forensic teardown (research log → field report) | Source-traceability: every claim to a checkable record | sourced / unsourced (unsourced claims die here) |
| **Assess** | Readable report: claim-vs-record echo map, gauges, objection tables | Claim-vs-record check + severity chips | verified / gap / unresolved |
| **Evaluate** | Gauntlet run: LAB, BAR, KKL, funhouse, dual bar-raiser, pathogen, inverse, kintsugi | Dual bar-raiser (product-truth vs proof-truth) | pass / conditional pass / fail |
| **Synthesize** | The surface + deck (~1:5 compression) + any minted class (skill) | Ship gates: no-new-claims · em-dash 0 · tripwire · leak · four-width pixels · noindex | ship / hold |
| **Recapitulate** | Shavasana + the counterpart note (DRAFT) | Draft-first (human sends) · register fit · pre-send gauntlet · ex-ante receipt filed | sent / parked |

**Altitude is orthogonal**, embedded in every synthesis print: collapsed-H2 deks = exec ·
open sections = operational · PRESENT deck = guided middle · footnotes/forensics =
surgical. Earned fidelity binds fate to render: verified renders sharp, gaps degraded,
unresolved grain.

## E — What's in the terrain

The skills that run the arc: `teardown-page-factory`, `forge`, `omakase-pipeline`,
`recoil-new` / `recoil-prep` / `recoil-ship` / `recoil-close`. The forge pair
(`public/forge-pattern.html` = class print, `public/forge-cut.html` = instance print) is
the house precedent for stage-printing. Reference instance of the full arc:
the Sean Wing engagement (wing.arcs.care; ex-ante print
`runtime/recoil/generated/2026-08-23-sean-wing.json`, filed pre-response, commit fc024ba).

## W — The window

Wired now (2026-08-23), while Wing is the only complete run and the missing prints are
fresh. Revisit trigger: the first engagement that completes the arc under the wired gates —
if the mandatory prints below still get skipped, the wiring failed and this ADR overclaims.

## Context

The 2026-08-23 Wing audit found the arc's synthesis leg fully gated (ship gates existed in
`teardown-page-factory`) while the recapitulate leg leaked: notes could reach "sent"
without an ex-ante receipt (leaving `/recoil-close` nothing to score against — the
load-bearing hole), without a pre-send gauntlet, and with witness/handoff prints left to
reconstruction. ADR-044 already names reconstructed timing as dishonest; this ADR closes
the same hole for the whole print schedule.

## Decision — mandatory vs advisory prints

**Mandatory (BLOCKING, wired into the skills as explicit steps):**
1. **Ex-ante receipt before any counterpart send.** `/recoil-new` scaffold + Ex-Ante tab
   filed BEFORE the note leaves DRAFT. No receipt, no send. (Wing precedent: filed
   pre-response.)
2. **Pre-send gauntlet** (`counterpart-gauntlet` workflow) between recapitulated and sent.
   Its receipt is an artifact; fate = send-worthy / parked.
3. **Close-loop print** (`/recoil-close`): mandatory once the counterpart responds — a
   standing obligation logged at ship time, not a ship-time blocker (you cannot block on a
   reply that hasn't happened). Gated on #1 existing.

**Advisory (recited, never mechanized):**
4. **Witness stubs** for naming moments — fires on live signal only (NOTOMATION;
   mechanizing it would fake the timing ADR-044 protects).
5. **Handoff print** at session close — already mandatory via CLAUDE.md policy; skills
   recite it, they do not re-legislate it.

**Printed surface for the matrix itself: declined for now.** The forge-pattern precedent
is a hand-designed 39KB surface; doing the matrix to that bar is not cheap, and the ADR +
wired skills ARE the invariant print. Park as a candidate for the Alexandria reading room
alongside ADR-066.

## Consequences

- The seven skills above each carry the matrix recital and their verb's gates/fates as
  explicit steps (this commit).
- Falsifiable compounding claim: the next teardown/forge engagement must leave the full
  trail — ex-ante receipt filed pre-send, gauntlet receipt, close-loop scored — at spec
  cost, not session cost. A skipped mandatory print is a drift receipt.
- Every future engagement leaves the ADR-066 trail: an instance surface, a class artifact
  when the shape repeats, a doctrine line when the class repeats.

## Wisdom receipt

The arc was always running; what was missing was the discipline that each cut leaves
evidence. Print at the cut, gate the print, name the fate — or pay full price to re-derive
the stage next session.
