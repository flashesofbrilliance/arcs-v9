# Retro: monday.com hiring-manager call (Oct 8, 2026): what the prep did and did not do
Private. Sources: your account after the call; Gmail; the board; public pages you showed. Granola captured only "Hello?", so there is no transcript. Everything about what Stefan said comes from you.

## Outcome
- Advanced to the next stage. Board row moved to the interview lane; scored 0.852 PURSUE after the fact.
- Stefan challenged your builder credibility; you showed rather than told.
- Opening: Tito and Me, then yoga, streetwear and parenthood, lightly.

## What you showed, in order, and what each proves
| Order | Surface | What it proves | Status |
| --- | --- | --- | --- |
| 1 | status.arcs.care | A real, dated build history of ARCS: 3,575 commits over 180 days, work items, risk register, evals marked NOT RUN | 200, public |
| 2 | status.arcs.care/beliefs | How you reason and what you commit to | 200, public (arcs.care/beliefs is 404; use the status URL) |
| 3 | good.arcs.care/blog/nftt | Writing from the build, with receipts | 200, public |
| 4 | good.arcs.care | Public tools and the field notes; says plainly the ARCS connector "does not exist yet" | 200, public |
| 5 | arcs.care/case-study | Ideal Protein outcome: "Qualified leads up 40 percent" | 200, public |

## What probably carried it (best evidence first)
1. **Showing live, public, honest surfaces under challenge.** Those pages state their own limits: every eval NOT RUN, "0 of 30" closed outcomes from outside users, no connector yet. That reads as a real journey, which monday's interview guide asks for.
2. **The gauntlet predicted the challenge** (builder credibility, Claude Code as pair, the private repo, "MCP in production") and corrected the claims you would have been probed on.
3. **The pace and framing rules** drawn from the Sam call (short opener, result first). Confirm if you kept to them.
4. **Real rapport.** It worked because the interests are yours.

## What was probably overbuilt for a 30-minute informal call
The monday-skinned page and hosting idea, the Letter print work, and a 4-page cue card you could not use live. The load-bearing core was three things: corrected claims, honest gaps, and proof you could show on demand.

## Consistency to hold next round (he and his team can revisit those pages)
- **MCP:** the public site says an ARCS connector for Claude and other agents "does not exist yet." Your Sept 6 resume says the MCP layer is "live and in production." Align on this wording: "a private MCP tool layer for my own agent work; no public connector yet."
- **Outcome closure:** the public status page says "0 of 30 closed outcomes from outside users." The repo handbook says 2 of 247 receipts closed. Different cohorts; if asked, use the public page's wording.
- **Units:** "800+ merged pull requests" (GitHub) versus 3,575 commits (status page). Say which unit.
- **Ideal Protein:** say "qualified leads up 40 percent," the published wording.
- **Resume:** correct the "public repo" and "in production" lines before the team sees it.

## Rapport lesson
One genuine connection beats four. In rounds with his team and leadership, do not repeat the same opener; use only overlaps that are real and let them lead. Do not refer in writing to personal news unless he told you directly.

## Next stage plan (take-home about a week, team walkthrough, leadership call, NYC behavioral deep dive)
1. **Take-home:** build on monday's own surface (agents, vibe apps or MCP); that closes the gap he probed. Disclose how you used AI and be able to defend every choice.
2. **Follow-up note:** send the corrected external one-sheet via Sam, with a short thank-you. One genuine line at most on rapport.
3. **Behavioral deep dive:** reuse the five stories; fill the blanks (WTA recovery outcome, Squat after launch, what the monday tenant changed).
4. **Resume:** fix the public/production lines first.

## Open questions for you
- Which links did he react to most, and what did he say?
- What did he ask that we did not prepare?
- What did he say about the take-home, timeline and next steps?

## Throughline you were showing: regulated-industry discipline, made visible
Why those surfaces mattered: they show how you plan and ship when evidence, privacy and audit matter. Map of what each practice looks like, in your words, with what is yours to claim:

| Practice | Regulated-industry version (your Grayscale and Squat work) | How the ARCS surfaces show the same discipline |
| --- | --- | --- |
| Evidence | Claims trace to a source; release decisions are documented | Every metric cites evidence; public evals marked NOT RUN until run; "four overclaims killed by a challenge review" |
| PII | Customer and patient data kept out of non-production and out of public artifacts | A privacy gate before anything is published; internal and external versions kept apart; counterpart names pseudonymized |
| Non-public information (material non-public information) | Information barriers; what can and cannot be shared outside | Private repository; an air gap between internal prep and external artifacts |
| Audit trail (for example Global Relay archiving of communications) | Communications and approvals retained and reviewable | Append-only ledgers, dated receipts, a decision record on each merge or deploy |
| Change control | Release gates, approvals, rollback plans | Pre-commit gates, merge commits, a decision receipt per publish |
| One-way-door decisions | Material, hard-to-reverse choices need explicit sign-off | A declared write-lock before irreversible decisions; irreversibility is stated, not assumed |

Rules for saying it:
- Say what you personally did at Grayscale and Squat (for example, which gates, which approvals, what you archived or reviewed). I do not know the specifics of your Global Relay work, so do not claim more than you did.
- ARCS is a design analogue of those practices, not a compliant system and not certified. Say "built on the same discipline," never "compliant."
- This is your differentiator for monday: their launch stresses governance, and an FDE who has shipped under evidence, privacy and change-control constraints is rare.
- Next stage: prepare one concrete story in the shape: situation, the one-way-door decision, the control you put in, and the result.

## Intel from the call (your account, Oct 8)
- monday is building FDE discipline from scratch. The team is about five, mostly engineering and solution-architecture backgrounds.
- Stefan repeated that he wants to keep pushing the frontier and building at the edge, and seemed open to running local models such as Qwen for some engagements, depending on client constraints.
- You think he could value your range. Pair it with credible building: the take-home and engineer peers will test the build.

### What you can honestly claim on local models (checked Oct 8)
- Ollama is installed with Llama 2, 3.1 and 3.2 pulled; no Qwen pulled; server not running; 16 GB Apple M1.
- Hermes is model-agnostic; your Hermes default points to a Qwen model served through the Nous provider (hosted, not local).
- ARCS routes models by role, blocks model IDs outside one file, and requires an eval before changing a role's model (private repo).
- blindsat (public repo): a prototype where "the LLM never sees your variable names." Call it a design and prototype.
- Do not say you have run Qwen locally unless you do.

## Decision: wait for the assignment
No local-vs-hosted comparison yet. We will see the assignment first, then build and log as we go (see TAKEHOME-LOG.md).
