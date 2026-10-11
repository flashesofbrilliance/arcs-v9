# SSOT: monday.com take-home prep (single source of truth)
Updated Thu Oct 8 2026. Private. This file is canonical; PREP-BOARD.html is a view of it. Edit this first, then the board. Contains no credentials, no assignment content, no real names of team members.

## 1. Status
- Role: Forward Deployed Engineer, Strategic Deployments, monday.com. Hiring-manager call done Oct 8; advanced to the assignment stage.
- Assignment: invitation received; content (intro video, pre-read, materials, checklist) is behind a one-time secure link that has NOT been opened. Deadline confirmed with Sam: Thursday Oct 15 2026, 5pm ET. Internal target: submit Wed Oct 14 evening.
- Deliverable format (from the invitation): one ZIP under 10 MB with non-empty source/ and presentation/ folders.
- Open decision: which browser and device to finish on, and when to open the link (soon, so there is time to ask follow-ups).

## 2. Files and what each is for
| File | Purpose |
| --- | --- |
| ATLAS.html (built by atlas/build_atlas.py) | One-file Atlas of every prep document as a ziggurat (base: witnessed signal; apex: decision), with gates re-run on every build; atlas/atlas-data.json is the data object for HUD visualizers |
| TAKEHOME-LOG.md | Append-only dated log: reasoning, AI use, decisions, receipts |
| TAKEHOME-RUBRIC-hardened.md | 12 hard gates and 11 scored dimensions, dual bar raiser protocol, kintsugi, pathogen checks |
| PREMORTEM-takehome-blind.md | 17 failure modes with pre-work and guards |
| takehome-workspace/montecarlo_premortem.py and montecarlo-results.txt | Monte Carlo of the failure modes (priors are subjective) |
| takehome-workspace/package.sh | Builds and checks the ZIP (size, non-empty folders, secret-looking names) |
| research/monday-oss-forensics-report.md and -critic.md | Static research on monday's GitHub, Hugging Face and docs, with a completeness critic |
| research/team-roster-roles.md | Role-level roster read with pseudonyms (no names) |
| CHORUS-persona-gauntlet.md | Ten voices, altitude ladder, three-order dealbreakers, round-robin (strophe, antistrophe, epode) |
| ALTITUDE-FRICTION-AUDIT-method.md | Generalized discovery and friction-audit method |
| KAIROS-COMPOUNDING-layer.md | Time-signature questions and the compounding-asset menu |
| STORY-CONSISTENCY-CHECK.md | One wording per story and number |
| CUE-CARD, INTERVIEW-PREP, RETRO, STEFAN-VIBE-READ, TRANSLATABILITY-MAP | Call-stage prep and retro (reuse for later rounds) |
| page-monday-v3.html and one-sheet PDFs | Leave-behind; NOT send-ready until the gauntlet fixes are applied |

## 3. Decisions made
1. Do not open the link until the browser and device are chosen; no incognito, no cookie clearing, no forwarding; the link is a credential and is stored nowhere.
2. Pre-work is scaffolding, not pre-solving: log, rubric, deliverable skeleton, sandbox practice, rehearsal plan.
3. The deliverable is yours: every AI use logged and disclosed; every file explainable.
4. Respectful framing of monday's own projects: say what an eval needs next, never what is broken; no third-party names; counts re-pulled the same day.
5. ARCS is shown as a discipline built on honest evidence, not as a proven or certified system; keep private IP out of the ZIP unless deliberately released.
6. Only offer to compound one or two reusable assets, chosen after reading the brief.

## 4. Research findings (static reads; nothing was run)
- monday's own pages say little about this loop. The engineering interview guide dates from 2020 and covers software-engineering roles; the careers page says four to five weeks; the AI interview guide is the only current policy (disclose, own, explain).
- Adjacent customer-facing take-homes (Glassdoor, anecdotal): build a workflow in monday for a client scenario, present it, then defend it and sometimes extend it live; one candidate was told they "didn't build a deck." No report on this exact track.
- Open source (mondaycom): active MCP server and agent toolkit with a hosted MCP; sensei (agent qualification engine); agent-tool-protocol; agentic-monday (a Claude Code plugin marketplace); vibe design system; apps SDK and CLI. No official Hugging Face organization found.
- Sensei read in source: clean suite schema and scoring math; but the judge never sees fixtures, two of four adapters drop fixtures, the agent model name is fixed, judge controls are minimal, layers 2 and 3 are weak, and shipped suites are thin. Looks dormant since March 2026. These are source reads, not reproduced.
- Platform facts: MCP calls count against the daily API budget; MCP actions run under the user's permissions; no self-service per-tool-call audit export; read-only is a tool-registration filter; hosted MCP source is not public.
- Team (roles only): the deployment function looks formed from Professional Services and implementation, with two deeply technical voices. Titles in the deployment family date from Sept and Oct 2026. One strategist describes partnering with Sales on scoping, estimates and SOWs, which supports the before, during and after the sale hypothesis.

## 5. Risk model (Monte Carlo, subjective priors)
- No pre-work: P(pass all bars) about 0.24; the KILL bar drives about 0.37 of failures.
- With about 15.5 hours of mitigations: about 0.52; with evidence events (brief read, rehearsal, dry run, gates, independent clear): about 0.65.
- Biggest value per hour: log every repair (0.5 h), confidentiality rule (0.5 h), link dry run (1.5 h), claim and consistency gates (2 h), outcome framing (2 h), acceptance criteria (3 h), rehearsal (4 h).
- Red team: platform fluency gap is the weakest point; worst pair is "engineering demo, not outcome" plus platform fluency.
- Not yet modeled: failure modes 14 to 17 (criticizing monday's own repo, unrun claims stated as fact, stale counts, heavy ARCS vocabulary).

## 6. Runway
Oct 8: prep, confirm deadline. Oct 9: activate, watch the video, read the pre-read, reconcile the rubric, write acceptance criteria and a not-doing list. Oct 10 to 12: build in thin slices, log as you go. Oct 13: draft the deck, run mechanical gates. Oct 14: red and blue round, rehearse aloud, package, submit in the evening. Oct 15: buffer; deadline 5pm ET.

## 7. Open questions
1. Which browser and device?
2. What is the time guidance and AI policy inside the pre-read?
3. Which one or two compounding assets fit the brief?
4. Who owns take-home work afterward?
5. What does the real checklist add to the rubric?

## 8. Not done and not claimed
No monday code was run. Personas are hypotheses. Subjective priors are not predictions. The leave-behind one-sheet still needs the gauntlet fixes. No unrun defect claim about any third-party system should be stated as fact.

