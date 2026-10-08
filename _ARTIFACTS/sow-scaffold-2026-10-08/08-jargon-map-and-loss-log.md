# 08 Jargon map and loss log for the plain-language bundle (INTERNAL, 2026-10-08)

Companion to `07-plain-language-bundle.md`. Internal only: it names what the counterpart-facing text leaves out. Translation is not fully lossless across audiences, so this file names the loss channels instead of claiming none.

## Jargon map (scaffold term to what Kelly and Chelsea read)

| Scaffold term | Plain version in the bundle | Why this analogy |
|---|---|---|
| Premise: shared documentation is not shared understanding | A budget Finance and Marketing read differently | Both live in budgets and briefs |
| Audit, light discovery (Phase 0) | Look and listen | |
| Shareback, co-design, roadmap (Phase 1) | Agree the plan together; a campaign calendar | Dependency map becomes "what has to happen before what" |
| Foundational hardening, plan sync (Phase 2) | Make it solid; two sets of books that reconcile | Double-entry bookkeeping was Zach's own framing on the call |
| Strategy, scenarios, premortem, post-mortem (Phase 3) | Aim higher, then look back; "imagine it failed" | |
| Ex-ante receipt | Our own predictions written down before we start | |
| Decision receipt | A written record: what we chose, why, what would change our minds | |
| One-way door, write-lock | A decision you cannot easily undo, so it is written down first | Not used in the bundle by name |
| Premortem | The "imagine it failed" exercise | |
| Checkpoint, graduation, soft landing | Checkpoint you can check; "can run it yourselves"; "you keep a pack, lose nothing" | Gate names kept in spirit, not as a stage-gate vocabulary |
| Definition of done, user acceptance criteria | What "finished" looks like, in writing | |
| Falsification test, pre-registered | What result would tell us we are wrong, decided before | Marketing A/B test with a cap |
| Bet card, confidence, timebox and cap, ramifications | The four things the owner writes down before important work | Test budget in a media plan |
| Token, token cap, spend alert | AI usage meter, spending cap | |
| Model-agnostic wrapper, vendor lock-in, switch cost | Keep options open to change AI provider | |
| Role-based access | Who can see what: parent, child, practitioner | |
| Redaction, deterministic pass plus review | Automatic checks plus a parent review step | |
| BAA, HIPAA, COPPA | Not named; "counsel should confirm" | No legal conclusions in a counterpart-facing text |
| Data-flow map | Where children's information travels | |
| Claim audit of the spec | Not in the bundle; see exclusions | |
| Plan-to-build tether | "Nothing in one that the other cannot account for" | |
| Fidelity grades SHARP, DEGRADED, GRAIN | We know / we think / we are guessing | |
| Question Compass | Not named in this draft; Zach decides whether and when to name it | |

## The codex

`09-translation-codex.md` is the legend for the technical words, written in plain words with a picture and a reason to care. Legal terms (HIPAA, COPPA, BAA, accessibility standard) are described in one neutral line each and always routed to counsel; no sentence says any of them applies or is required. Round-trip addition: every technical word used in `07` appears in `09`.

## What was compressed

- 43 draft assumptions in `03-assumptions-draft.jsonl` collapse into the bundle's four questions, the three cost buckets and the trial option. The assumption ledger itself stays internal.
- The 30-odd line items in `02-sow-scaffold.md` appear as stage-level outcomes, not item lists.
- Acceptance tests appear as one example per stage, not the whole set.
- The per-phase charter's three-gates-per-phase rule is expressed as a checkpoint, what "worked" looks like, and the pack you keep.

## What was left out on purpose (air-gap)

Internal-only content, deliberately absent from the bundle:
- The transcript, in any wording, and any personal remarks from the call.
- Zach's hunches about the spec (hallucination, flattery, after-the-fact confirmation) and the claim audit step P0.A6 by name. A neutral version can be added once Zach decides how to frame it ("we will fact-check every document, ours included").
- The liability figure Zach recalled on the call (unverified), hourly rates floated aloud, and anything priced.
- The Lovable terms finding and other vendor-term findings; Zach decides whether and when to raise them. The bundle says only that we will map where the data travels and check each service's terms with counsel.
- The asset map, the repo paths, internal tool names, evidence citations and relayed behavioral-economics grades.
- Open questions for Zach, including the recording-consent and spec-verifier questions.

## Loss channels (rate, visibility, direction)

- **Rate:** method detail drops sharply: from a full scaffold to about one page per audience. A reader cannot rebuild the tests from the bundle.
- **Visibility:** the evidence behind each claim is hidden. The bundle keeps only the three-level honesty line.
- **Direction:** the bundle reads as more settled than the scaffold. The scaffold is a draft with many items still guessed. The last section of the bundle exists to counter that; keep it.

## Round-trip test (to run before sending)

1. Pick five statements in the bundle at random; for each, point to the scaffold line it came from. Any statement with no source is cut.
2. Pick five scaffold items marked as commitments or acceptance tests; for each, find its plain version in the bundle. Any missing one goes to the loss log above with a reason.
3. A reader who is not Zach restates the four stages and the three buckets without the jargon map. If they cannot, rewrite.

## Pre-send checklist (from ADR-068, none done yet)

- Ex-ante receipt filed for the send (`.claude/skills/recoil-new/SKILL.md`).
- Pre-send gauntlet run (`.claude/workflows/counterpart-gauntlet.js`), with a persona for Kelly and one for Chelsea.
- PII and internal-versus-external air-gap review of the final text.
- Counsel confirms the "sits beside your legal agreement" line and anything that could read as binding.
- Zach sends it himself. Claude drafts only.

## Honest limit

Two terms were taken from the call in Zach's own words and used here for resonance (the house-building picture, double-entry bookkeeping); both were said to Kelly and Chelsea directly. Whether either reads as a good fit for them is untested. The bundle should be read aloud to one non-technical person before it goes out.
