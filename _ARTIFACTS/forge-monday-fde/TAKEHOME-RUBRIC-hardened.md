# Hardened grading rubric v0: monday.com take-home
Private. Built from: the invitation checklist (known), the pre-mortem failure modes (FM1 to FM13), monday's AI interview policy, the JD, and sensei's style of KPIs. **Reconcile after you read the real pre-read, video and checklist:** add or change rows, and mark each row's source (invitation, pre-read, JD, self). Until then every score is provisional.

## Protocol (dual bar raiser, as defined in .claude/arcs-dual-bar-raiser.md)
- **Implementer (you, with Claude Code)** drafts and edits. The Implementer never self-clears.
- **Bar-Raiser** is an independent reviewer (a fresh-context agent that has not seen your reasoning, a different model, or a human). It issues a verdict: CLEAR, CONDITIONAL CLEAR with annotated findings, or HOLD.
- **Annotation taxonomy** (from the protocol): IMPL_GAP (a requirement not met), CONSISTENCY (a claim disagrees with another claim), COLLISION (disagrees with a public page, resume or the brief), STYLE.
- **Kintsugi:** every break found after the first draft is booked in TAKEHOME-LOG.md as break, how found, repair, guard, before the fix. No silent patching.
- **Two audience bars** both must clear: **Bar A (customer outcome)** and **Bar B (builder defense).** A third, the **KILL bar**, covers hard gates.
- Deterministic gates and scored judgment stay separate: a gate fail is a kill, never averaged away.

## Hard gates (any fail = KILL; fix or cut, never average)
| # | Gate | Check | Source |
| --- | --- | --- | --- |
| H1 | On time | Submitted by Thu Oct 15 2026, 5pm ET. Internal target: Wed Oct 14 evening | invitation |
| H2 | Package | One ZIP under 10 MB; non-empty source/ and presentation/ (run takehome-workspace/package.sh) | invitation |
| H3 | Checklist | Every portal checklist item completed | invitation |
| H4 | Inputs consumed | Intro video watched in full and pre-read and materials reviewed; dated notes in the log | invitation |
| H5 | Session hygiene | Same browser and device; no incognito; no cookie clearing; no link forwarding | invitation |
| H6 | Confidentiality | No assignment text public; no secrets, client names or PII; ARCS private IP not embedded unless deliberately released | self, pre-mortem FM8 |
| H7 | AI disclosure | Every AI use logged and disclosed; every file explainable by you | monday AI guide |
| H8 | Provenance | Every number and claim cites a source; no contradiction with resume, case study or public pages (provenance and consistency gates pass) | pre-mortem FM5 |
| H9 | Brief answered | Acceptance criteria written before building; every one satisfied | pre-mortem FM1 |
| H10 | No silent repair | Kintsugi entry exists for each post-draft correction | pre-mortem FM13 |
| H11 | No unrun claim as fact | Any defect or gap claim about a third-party system is reproduced, or labeled "read in source, not run"; counts re-pulled the same day | forensic research critic |
| H12 | Respectful framing | Describe what a system needs next; never disparage or name maintainers; no personal contact details | forensic research critic

## Scored dimensions (0 to 3; weights are provisional)
| # | Dimension | 0 means | 3 means | Bar |
| --- | --- | --- | --- | --- |
| 1 | Outcome framing | no goal or measure | goal, OKR-style measure and stop criterion up front | A |
| 2 | Scoping and assumptions | hidden assumptions | assumptions stated, ambiguity questions asked, a not-doing list | A |
| 3 | Build quality and reproducibility | does not run or cannot be reproduced | runs from clean steps, small, readable | B |
| 4 | Evidence it works | no test | golden cases, a pass bar, failure modes shown | B |
| 5 | Defensibility | cannot explain choices | every choice has a rejected alternative and a reason | B |
| 6 | Adoption and rollout | none | phased rollout, owner, adoption measure, post-launch plan | A |
| 7 | Governance and change control (only if the scenario touches it) | ignored or overdone | right-sized evidence, PII, audit, one-way-door handling | A |
| 8 | Communication | jargon, no summary | executive summary, plain language, clear deck | A |
| 9 | Honest limits | overclaims | limits and repairs visible; nothing stronger than its evidence | A and B |
| 10 | Reusability | one-off | a pattern or asset another account could reuse | A |
| 11 | Time discipline | overran the cap | submitted at the cap with cuts documented | B |

Bar clears when every dimension on that bar scores at least 2 and the bar's average is at least 2.3. Both A and B must clear.

## Pathogen detection (run on the final draft)
- **Temporal paradox:** dates and sequence claims (when built, when decided) agree with git history, the log and the public pages.
- **Speaker provenance:** who said or decided what is stated correctly (what monday said versus what you inferred).
- **Unsupported numbers and "every/always/never" statements.**
- **Production, public, compliant, certified:** each word is checked against evidence.
- **Collision with:** the resume lines, the Ideal Protein case study, status.arcs.care, good.arcs.care, and the consistency sheet.

## Red team and blue team (bounded)
1. Round 1: a fresh agent receives only the brief, the rubric and the deliverable, and is told to refute and default to HOLD.
2. Blue: you fix, logging each seam first.
3. Round 2 only if round 1 returned a HOLD or a kill finding. Then stop. No open-ended polishing.
4. If a section still fails a gate and time is short: **cut it** rather than patch it.

## Mechanical gates to run (deterministic)
provenance_lint with a ledger; slop_lint; em-dash grep; package.sh; link check (HTTP 200) for every external URL; a secrets grep over source/ and presentation/; consistency check against STORY-CONSISTENCY-CHECK.md.

## Timeline (7 days)
Day 1: activate, watch the video, read the pre-read, reconcile this rubric, write acceptance criteria. Days 2 to 4: build in thin slices, log as you go. Day 5: draft the deck, mechanical gates. Day 6: red and blue round, rehearse the walkthrough aloud. Day 7 (Oct 14): final gates, package, submit the evening before the deadline.

## Simulation-informed priorities (Monte Carlo pre-mortem, Oct 8)
Model and priors: takehome-workspace/montecarlo_premortem.py (stdlib, seeded, 40,000 runs per estimate). **The priors are my subjective estimates, not data; these figures expose assumptions and rank pre-work, they do not predict outcomes.** Rerun after you read the brief with updated priors.
- Passing all bars with no pre-work: about 0.24. The KILL bar (process, pathogen, hardening, kintsugi) drives about 0.37 of failures and is the cheapest to fix.
- Best value per hour: log every repair first (0.5 h), the confidentiality rule (0.5 h), a one-time-link dry run (1.5 h), claim and consistency gates (2 h).
- Next: outcome-first framing (2 h) and acceptance criteria with a not-doing list (3 h), then rehearse the walkthrough (4 h).
- Red team: the weakest points are monday platform fluency and "engineering demo, not outcome"; the worst pair is those two together.
- With about 15.5 h of pre-work the model estimates about 0.52; reading the brief, rehearsing aloud, a packaging dry run, passing the gates, and an independent bar-raiser clear take it to about 0.65. Pre-work alone does not reach 0.65, so the evidence steps matter.
