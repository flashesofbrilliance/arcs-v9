# Chorus: persona-led gauntlet (private)
Goal: make one deliverable so legible and consonant that each reviewer can say yes in their own terms, within a minute or so of reading their entry point, so the team converges quickly **without skipping monday's process**. Do not try to bypass their steps (assignment, team walkthrough, leadership call, final). Reduce friction and surprise inside them.

## Guardrails
- Voices are **role archetypes built from professional titles**, not simulations of named people. They are hypotheses.
- Never reference an individual's background to them. No contact or outreach.
- Honesty rules still win: no claim stronger than its evidence (see the rubric gates H7 to H12). Persuasion comes from true, well-evidenced alignment.
- Run this on the real draft once the brief is read; today's version is anticipatory.

## The chorus (ten voices, in round-robin order; archetypes built from the full roster scan)
| # | Voice (archetype) | Lens | Likely objections | Evidence to be ready with |
| --- | --- | --- | --- | --- |
| 1 | Hiring manager (strategic FDE and CS lead) | Outcomes, builder credibility, frontier | "Show me you can build." "Is this adoption or a demo?" "Does it generalize across accounts?" | Public ARCS surfaces; the build; outcome-first structure |
| 2 | Services leader (AI-first services, KPIs, catalog) | Repeatable, margin, utilization | "Is this a one-off or a productized offering?" "What does delivery cost, and how many hours?" | Playbook, offering sketch, effort and utilization estimate |
| 3 | Integration architect | Architecture and failure modes | "Auth, rate limits, idempotency?" "What breaks at scale?" "MCP vs API?" | API budget facts, read-after-write checks, a failure-mode table |
| 4 | Agentic and vibe-coding practitioner (Claude Code, MCP) | Does the build show real fluency, and who wrote it | "Did you write this, or did AI?" "Why this tool shape?" "Where are your evals?" | AI-use log, rejected alternatives, evals with a pass bar, honest limits |
| 5 | Deployment strategist and engagement manager | Scoping, estimation, SOW, handoff | "How is this scoped, estimated and handed off?" "What are the assumptions?" | Discovery questions, phased plan, RACI, SOW-style assumptions |
| 6 | Platform-hands-on consultant | Does it work properly on monday | "Would a client admin adopt this?" "Did you use boards and automations correctly?" | Work in a real account, concepts used correctly, limits stated |
| 7 | Enterprise CSM / CX lead | Adoption, QBR and EBR, AI quality at scale | "How will customers feel it?" "Where is the ROI?" "How do you measure quality at full coverage?" | Success measure and stop criterion, EBR-style one-pager, a coverage plan |
| 8 | Product and GTM lead | Evidence to product, activation | "What does product learn?" "Where is time to first value?" | A feedback record with provenance, a time-to-value metric, a reusable pattern |
| 9 | Partner and enablement | Reuse and ecosystem | "Can partners reuse this?" | Reusable assets, plain-language documentation |
| 10 | Talent and culture | Communication, AI-policy adherence, humility | "Did they follow our AI policy?" "Do they communicate clearly and credit others?" | AI log, clear summary, limits stated, "we" credit |

## Altitude ladder and fidelity controls (full cast, 25 personas)
Altitude is orthogonal to department. The same deliverable must hold up at every level, with **fidelity controls**: each level sees only the detail it needs, numbers are identical across levels, nothing is more precise than its evidence, and every higher-level claim traces down to evidence at a lower level.

| Altitude | Decision they own | Read budget | Fidelity control (what satisfies them) | Maps to the ZIP |
| --- | --- | --- | --- | --- |
| Executive | Endorse, fund, sponsor | 60 to 90 seconds | Outcome in one sentence, one number with its source, risk in one line | presentation/ first page |
| Strategic | Is it coherent and scalable? | about 5 minutes | One page: strategy, tradeoffs, sequencing, KPIs, risks | presentation/ |
| Operational | Can we run and staff it? | about 10 minutes | Plan, RACI, estimate, assumptions, handoff, dependencies | presentation/ appendix |
| Tactical | Can I deploy, teach and adopt it? | about 15 minutes | Step-by-step, templates, configuration, FAQs | presentation/ and source/README |
| Surgical | Is it correct and safe? | 30 minutes or more | Code, tests, failure-mode table, evals, logs, reproduction steps | source/ |

### Persona map (hypotheses from titles and careers; names are placeholders)
Dealbreaker, then the path as first-order, second-order and third-order consequences.

**Executive (department heads and leaders)**
| Persona | Dealbreaker | 1st, 2nd, 3rd order | Fidelity control |
| --- | --- | --- | --- |
| Sasha V. (AI-first services leader) | Not a repeatable, costed offering | Reads as a one-off, then does not fit the services roadmap, then cannot scale or be priced | Offering sketch, effort and utilization estimate, one number |
| Emerson C. (GTM head, AI suite) | No time-to-first-value story | Value unclear, then activation and pricing arguments fail, then no pull from sales | Time-to-value baseline and target, plain-language outcome |
| Rowan G. (enterprise product alignment lead) | Anecdotes instead of evidence for product | Feedback unusable, then roadmap ignores it, then you are seen as a doer, not a sensor | Feedback record with provenance, a reusable pattern |
| Blake E. (strategic partnerships head) | Cannot be reused by partners | One-off integration, then no co-sell story, then ecosystem value lost | Reusable assets and a plain-language partner note |

**Strategic**
| Persona | Dealbreaker | Path | Fidelity control |
| --- | --- | --- | --- |
| Hiring manager | Cannot show real building, or a vague outcome | Doubt on builder credibility, then the team doubts the whole story, then no consensus | Public proof, outcome-first page, honest limits |
| Avery L. (deployment strategy manager) | Not scoped to a methodology | Unclear phasing, then overruns, then time-to-live slips | Phased plan tied to time to live |
| Harper W. (cloud alliance lead) | No ecosystem fit | Isolated solution, then no alliance advantage, then limited expansion | One slide on ecosystem fit |
| Sage I. (CEO's office program and ops) | No portfolio or ROI view | Hard to prioritize, then deprioritized, then no executive air cover | ROI and prioritization table |
| Lennox U. (org design, people partner) | Ignores how the team is shaped or learns | Process nobody can adopt, then enablement burden, then friction | A note on roles and skills needed |

**Operational**
| Persona | Dealbreaker | Path | Fidelity control |
| --- | --- | --- | --- |
| Taylor S. (engagement manager) | No estimate, assumptions or SOW logic | Scope creep, then margin loss, then credibility loss in the sale | SOW-style assumptions and estimate |
| Riley D. (technical PM roots) | No dependencies, owners or blockers | Plan unrealistic, then slips, then escalation | Dependency and owner table |
| Drew N. (CX team lead, AI quality metrics) | Quality sampled, not covered or calibrated | Hidden failures, then CSAT drop, then cost of rework | Coverage plan, pass bar, calibration note |
| Parker J. (revenue enablement lead) | Unteachable | No ramp for others, then inconsistent delivery, then low reuse | Short enablement outline |
| Skyler P. (partner program manager) | No onboarding path for partners | Partners stall, then low reuse, then program loses value | Onboarding checklist |
| Reese F. (regional partner enablement) | Jargon-heavy materials | Not adopted regionally, then uneven results | Plain-language one-pager |
| Finley O. (program lead, startups) | Cannot be packaged or scaled | Boutique effort, then not offered widely | Packaging note |

**Tactical**
| Persona | Dealbreaker | Path | Fidelity control |
| --- | --- | --- | --- |
| Jordan T. (forward deployed consultant) | Misuses monday concepts or is not adoptable by an admin | Awkward config, then low adoption, then escalations | Steps tested in a real account, defaults, admin notes |
| Casey R. (strategic product consultant) | No value story for the buyer | Weak expansion case, then stalled deal | Value talking points |
| Jamie H. (executive adoption advisor) | No executive narrative | Sponsor not engaged, then rollout stalls | Exec summary and sponsor ask |
| Robin A. (enterprise CSM) | No ROI or risk framing | Renewal risk unaddressed | Risk list and ROI measure |
| Kai B. (enterprise CSM) | No adoption evidence for a review | Weak QBR or EBR, then renewal doubt | EBR-style one-pager |
| Dakota Y. (enterprise AE) | Cannot be explained to a buyer in a sentence | Lost deal momentum | One-sentence value statement |

**Surgical**
| Persona | Dealbreaker | Path | Fidelity control |
| --- | --- | --- | --- |
| Morgan K. (integration architect) | Ignores auth, rate limits or failure modes | Breaks at scale, then support burden, then trust loss with the engineers | Failure-mode table, read-after-write checks, quota facts |
| Quinn M. (agentic and vibe-coding practitioner) | Cannot show who built it, why this tool shape, or evals | "AI wrote it" suspicion, then the walkthrough collapses, then the whole loop loses credibility | AI-use log, rejected alternatives, evals with a pass bar, reproducible source |

**Process gatekeeper:** Recruiter. Dealbreaker: a policy breach (undisclosed AI use, forwarding the link, wrong packaging). Path: disqualification before anyone reads it. Control: the rubric's hard gates H1 to H12.

## Round-robin protocol: the Greek chorus as two passes and a reconcile
- **Strophe (top-down pass):** read the draft from Executive to Surgical. Does the story stay coherent as detail increases, and does each level get what it needs?
- **Antistrophe (bottom-up pass):** read from Surgical to Executive. Is every higher-level claim supported by evidence one level down? Build a **claim ladder**: each executive claim, the strategic argument beneath it, the operational plan, the tactical steps, and the surgical evidence.
- **Epode (reconcile):** list conflicts (executives want brevity, surgical readers want depth), resolve them by layering and linking, and book each change as a kintsugi seam.
- **Per voice:** objection, response with evidence, change to the deliverable.
- **Order of depth for first, second, third order:** for each dealbreaker, test the first-order consequence, then ask what that causes next, then what it causes after that. If the third-order consequence is severe, fix the first-order cause now.
- Stop after two full rounds. Log every change.

## Design for fast consensus (inside their process)
- **One spine, ten entry points.** A one-page executive summary leads: outcome, approach, proof, rollout, risks, next step. Then short role-labeled sections ("If you care about architecture, read here") so each voice finds its answer fast.
- **Show, don't tell:** link proof the reader can open in seconds.
- **No surprises:** state assumptions, limits and what you did not do.
- **Same numbers everywhere:** one source per claim.
- **Respect the 10 MB and two-folder format;** put the spine in presentation/ and the build in source/.

## Anticipatory objections to your candidacy (answer ahead)
1. "Is the engineering depth enough?" About a year and a half of daily TypeScript, all on ARCS; the take-home is the proof.
2. "Is this a founder who will leave?" Applying for a full-time role; ARCS is how you learn the technology.
3. "Is the governance talk real?" Show the practice: evidence rules, audit trail, change control, in your own words from Grayscale and Squat.
4. "Is AI doing the work?" The log: every AI use disclosed, every choice explainable, rejected alternatives recorded.
5. "Will it generalize?" The reusable-pattern section.

## Next
After you read the brief: write the outline, run round 1, build, run round 2, then package. I can run the rounds with separate agents per voice; it costs several hundred thousand tokens, so I'd run it only on a real draft.

## Consonance spine (from the roster scan)
Where many voices want the same thing, put it first:
1. **Time to first value** with a baseline and a target.
2. **A repeatable playbook or offering** another account could reuse.
3. **An EBR-style one-pager** showing adoption and outcome.
4. **Quality measured at full coverage,** with a stated pass bar.
5. **Governance proportionate to the scenario** (evidence, PII, audit, change control).
6. **AI-assisted building shown plainly,** with your reasoning and rejected alternatives logged.

## Cast list (pseudonyms from research/team-roster-roles.md; archetypes, not individuals)
| Voice | Primary persona(s) |
| --- | --- |
| 1 Hiring manager | Hiring manager |
| 2 Services leader | Sasha V. |
| 3 Integration architect | Morgan K. |
| 4 Agentic and vibe-coding practitioner | Quinn M. |
| 5 Deployment strategist and engagement manager | Taylor S., Avery L., Riley D. |
| 6 Platform-hands-on consultant | Jordan T., Casey R. |
| 7 Enterprise CSM and CX lead | Robin A., Kai B., Drew N. |
| 8 Product and GTM lead | Emerson C., Rowan G. |
| 9 Partner and enablement | Harper W., Blake E., Skyler P., Reese F., Parker J. |
| 10 Talent and culture | Recruiter |
Also present, not reviewers of the build: Jamie H., Finley O., Dakota Y., Sage I., Lennox U. Names are placeholders. Use them only inside this file.

## Kairos and compounding pass
After the epode, run the five time-signature questions (why now, why this instrument, can you play it, does it make my life easier, what compounds) against each altitude. Details, the honest-limits table and the compounding-asset menu are in KAIROS-COMPOUNDING-layer.md.
