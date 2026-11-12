---
title: Recoil call service, arc weld of recoil and recoil-skim
version: 0.1.0
status: PROPOSED (Zach reviews; nothing here is decided)
date: 2026-11-11
owner: Zach Harris
backlog: _QUEUE/induced-backlog.jsonl rows tagged `epic: recoil-call-service`
prior_art: ADR-060 (penteract), ADR-068 (print schedule), ADR-086 (two-pass induction), WORLD.md "THE HUD", src/app/hud/ZigguratLoader.tsx (arcs.atlas.v1), .claude/skills/recoil-new|prep|close|ship, PR 2145
---

# Recoil call service: one call in, a flyable atlas out

**Why.** A call with a counterpart produces evidence that today ends up in one of two pages that do not agree. The heavy war-room report (`/recoil/[reportId]`) has the method but no skim layer: 13 equal-weight dark pages. The light recoil-skim page (Zach x Brian, 2026-11-11) has the best reading design on either side (pull, not push: next move first, every section a closed fold that states its verdict), but its kit and generator exist on no branch. Neither turns the call into something you can navigate.

**What.** One standalone, composable call service. A call reference goes in (calendar event, Granola note). Out come, in order: a decomposed record, a five-verb read, a "why it works" hypercube cell set, a knowledge graph exploded into an atlas, and that atlas loaded into the HUD. In the HUD the ziggurat sharpens as edges are cut, the view orbits a full turn and scrubs time both ways, and kairos moments stand out at a glance.

**Why now.** Two reviews ran today on both pages (impeccable and brand line producer, both BLOCK). PR 2145 fixed the heavy page's print and module order today. The Brian page's glass box says its kit pieces landed, and they did not. That is the seam to repair before a third recoil format appears.

**How.**
- *Before (this document):* critique, reconcile, spec, induced backlog. Children start from this branch.
- *During:* child sessions build one row each, in dependency order, each in its own worktree, each ending in a PR that runs its gates. Autopilot covers every reversible step. It stops at every one-way door (merge, publish, send, paid call, canon change) and hands Zach the approvals list.
- *After:* the Brian call is the acceptance fixture. The service rebuilds it end to end with no hand edits, and both reviewers return PASS.

**How to read this page.** §1 shows where each page came from. §2 is the weld (what we keep, cut and leave open). §3 is the customer journey. §4 is the design spec, §5 the product requirements, §6 the service architecture and §7 the plan. §8 lists what waits on Zach. §9 is the status as of 2026-11-12.

---

## 1. Provenance: what made each page

| | Heavy: war-room recoil (`/recoil/2026-10-29-gasmi`) | Light: recoil-skim (Zach x Brian, artifact `RUNuc7zkSW9tPQhptnPCoY`) |
|---|---|---|
| Prompt of record | Three skills, run in order: `.claude/skills/recoil-new/SKILL.md` (scaffold the six-tab SSOT, the single source of truth), `recoil-prep` (gather calendar, Gmail, Granola, Gamma and profile, then fill Pre-Call and Ex-Ante), `recoil-close` (pull the transcript, score the ex-ante, fill Forge, Recoil, War Game and Defensibility). The SSOT carries the template text: "ARCS 6-TAB WAR-ROOM. The disciplined internal method behind ahmed.arcs.care, parameterized." | No prompt on this machine. A search of every Claude Code session transcript (active and archived) for `recoil-skim`, the artifact id, the Granola id `8000dd5f` and "cold molt v3" returns nothing. The page's own glass box records its method: a chat session ("agents were read from .claude/agents and run by hand, as BOOT 7a says chat sessions do"). That session ran a design gauntlet with impeccable conducting, plus a sanity check, a craft floor, grug and four chiefs (loki, bayesian, claims-skeptic, conductor), in that order. It was molted three times ("cold molt v3"). |
| Renderer | `src/document/screens/WarRoomReport.tsx` (React, inline styles, `src/document/tokens.ts`) | Single-file HTML with `_tokens.css` inlined, plus primitives labeled `@prim` from `src/ui-kit/recoil-report` |
| Claims checked against the repo | Renders from committed JSON; gates pass in CI | Tokens and primitives 24, 27 to 33 and 37 match the kit byte for byte. Primitives 42 to 50 (fold, ledger-row, toast, claim-check, heat-take, option, attributed-notes, operator-pass, kintsugi-seam) exist nowhere: on every branch (after `git fetch`), those numbers are other primitives (42 is shell-nav, 45 fact-tile). The glass box claims "B11 done: 42-fold, 43-ledger-row, templates.json registered" and "component_source_gate PASS"; here the gate fails with "unknown template 'recoil-skim'". |

Reviews behind this page (both read-only, full text in the session scratchpad, summarized here):
- **Impeccable (design):** the light page's pull-not-push design is the strongest on either surface. It loses all content in print (closed folds print as one-liners). Its provenance is false. It has no body measure (about 140 characters a line at 1440px). The heavy page has no skim layer, prints every section label twice, and its `fg4` text color is 3.67:1, under the 4.5:1 AA floor.
- **Brand line producer:** BLOCK on both. Earned fidelity is broken on both: grade-D forecasts render as sharp bars with a sweep, "not scored" renders red (which means fail), and the Y chip is gold for every state. The heavy template uses 11 type sizes. The light page has two font sets and leaves acronyms unexpanded (NCI, ADR-077, User1, SSOT, MPC). It also has one em-dash in the heavy PDF's Deeper Strata, and a personal email address in the light page's script.

## 2. The weld: Changed, Rejected, Held open

| | Decision | From |
|---|---|---|
| **Changed** | Skim layer first: header, then one glance table whose first row is the next move, then closed folds whose summary line states the verdict. | Light |
| **Changed** | The method stays the spine: Pre-Call, Ex-Ante, Forge, Recoil, War Game, Defensibility, in lifecycle order (PR 2145), as fold groups. | Heavy |
| **Changed** | "Where it stands" (opportunity and next steps) is the first section in both, as PR 2145 now does. | Both |
| **Changed** | One schema in, many renders out: React page, single-file HTML, PDF and counterpart-safe twin all come from one SSOT and one component set. | New |
| **Changed** | One token source: `src/ui-kit/recoil-report/_tokens.css`; `src/document/tokens.ts` is generated from it. Four type steps, with the label step at 12px or more. | Both reviews |
| **Changed** | Fidelity is set by code, never by hand: grade and Y state map to sharp, degraded, grain or moire, and a "not scored" item renders as grain with its sample size. | Brand |
| **Changed** | One meaning per color: red only for a failed check, gold only for a limit, green only for proven, steel for unknown. | Brand |
| **Changed** | The print target opens every fold, keeps rows whole, and offers a light palette. | Impeccable, PR 2145 |
| **Rejected** | Hand-built pages with copied CSS blocks. Every `@prim` block is diffed against a real kit file at build time, and a mismatch fails. | Light's failure |
| **Rejected** | Section labels printed twice ("02 · THE ANSWER" over "The answer"). | Heavy's defect |
| **Rejected** | Big-number hero tiles. The light page cut them in v2, and they stay cut. | Light |
| **Held open** | Dark versus light as the PDF default. | §8 |
| **Held open** | Whether the counterpart twin is the same component set with an audience filter, or its own template. | §8 |

## 3. Customer journey (Zach, 2026-11-11, verbatim order)

`decompose → analysis, assessment, evaluation, synthesis, recapitulation → deconstruct → why does it work (5D 5W 5H 5C 5R, a 5x5x5x5x5 hypercube explorer) → explode the knowledge graph into a terraformed atlas → load the atlas into the HUD`

Goal, verbatim: "clarity fidelity and resolution grow as new edges are cut into the polygon rendering of the ziggurat and that you can fly around 720º both forward and backwards in time and spot kairos moments at a glance".

| Stage | What the user gets | Built on (exists today) | Missing |
|---|---|---|---|
| J1 Decompose | The call split into atoms: utterances with timestamps and speakers, claims, promises, owners, numbers | recoil-new/prep/close skills, the SSOT `beliefs`, `kinematic_series`, `next_steps` | One `call.atoms` list with stable ids, so every later stage cites atoms, not prose |
| J2 Five verbs | One fold per verb (analyze, assess, evaluate, synthesize, recapitulate), each with a verdict line | ADR-060 Verb axis; the Glass box passes on the light page | A verb pass that writes into the SSOT, not into page HTML |
| J3 Deconstruct | Each claim taken apart into premise, mechanism and evidence | Forge claim adjudication (GROUNDED, INFERENCE, STRUCK) | Premise and mechanism fields per claim |
| J4 Why it works: hypercube | An explorer over five axes of five. Lens D, W, H, C, R (Decision, Window, Human, Coherence, Risk) × Resolution × Operator × Verb × L-stack = 3,125 cells. Only filled cells light up, each linked to its atoms | ADR-060 penteract (the axes and values are already defined there) | A cell index built from the SSOT, and an explorer view (a 2D slice picker plus a filled-cell list, not a 3D toy) |
| J5 Explode to atlas | A knowledge graph of atoms, claims, people, beliefs and decisions, terraformed into tiers (the terraces) | `arcs.atlas.v1` (tiers with docs and a gate); the Atlas Loader at jobs.arcs.care/atlas | **`arcs.atlas.v2`**: nodes, typed edges, timestamps per node and edge, kairos marks, and evidence per edge |
| J6 Load into HUD | The ziggurat on `/hud`, built from the atlas, one terrace per tier | `src/app/hud/ZigguratLoader.tsx` (v1, at most 12 tiers, admin-only, local file only) | A v2 loader: edges drawn as cuts in the polygon, plus orbit, time scrub and kairos |
| J7 Fidelity grows with edges | Each new evidenced edge adds a facet. A tier's render state follows its evidence count: grain under the threshold, then degraded, then sharp | Earned fidelity (WORLD.md render scale); kit primitive 37 fidelity-grain | A rule from edge count and evidence grade to render state, with thresholds written down before counting (memory `pre-register-rule-before-counting`) |
| J8 Fly 720° and kairos | A full orbit in space and a full scrub in time, both directions; kairos moments as markers visible at every angle and every time | WORLD.md HUD "Time: belief change, scrubbed by date"; `kairos` fields in the SSOTs | Time-indexed edges, a scrubber, and a kairos marker layer. "720°" is defined in §8 for Zach to confirm |

## 4. Design spec

### 4.1 Page anatomy (every render, every surface)

1. **Header** (one grammar): eyebrow, title, a `Y · STATE` chip in its own state color, NCI as "prior → post" or "not scored" in grain. NCI is the Net Coherence Index, expanded on first use on each page.
2. **Skim:** one glance table, at most five rows. Row one is the next move (option picker, draft note, copy; nothing is sent from the page). The rest are signal, owed, numbers and pre-call, each with an anchor to its fold.
3. **Folds**, in groups: Decide (options, forecasts), Evidence (method tabs in lifecycle order), System (seams, wiring), Method (glass box). Each fold summary carries its verdict and a grade chip.
4. **Appendix:** Deeper Strata (provenance), collapsed on screen and expanded in print.

### 4.2 Component set (atoms → organisms), one prop schema per component

Atoms: `chip{tone: cyan|green|gold|red|steel|magenta, label}`, `led{state: on|off|alert}`, `ref{text, href?}`, `button{variant, pressed?}`, `grade{A..E, basis}`.
Molecules: `ledgerRow{key, chips[], body, ref, state}`, `claim{said, state: sharp|degraded|grain|slip|moire, value, note, ref}`, `take{heat: mild..loco, text}`, `option{id, name, cost, do, head, heart, wallet, lead?}`, `seam{key, rows{break, cause, repair}}`, `probRow{label, p, grade, basis}`, `pass{lens, found, ruling: held|changed|broke}`.
Organisms: `header`, `glance`, `fold{id, title, verdict, chip, group, body[]}`, `nextMove{options[], draft, links}`, `table{columns, rows}`, `chart{series[]}`, `beliefLog`, `kinematics`, `rosetta`, `unknownBlock` (the heavy side's fallback, kept).

Mapping from today's heavy block types: `prose → fold body text`, `list → ledgerRow[]`, `keyvalue/receipt → ledger`, `table/rosetta → table`, `belief_log → claim[]` (the impeccable review: a near-exact fit), `worked_example → chart`, `kinematics_table → kinematics`, `insights → ledgerRow[]`, `provenance → ref + quote`.

### 4.3 Tokens, type, color, fidelity

- One source: `_tokens.css`. `tokens.ts` is generated, and a check fails on drift.
- Four type steps: label 12px, body, headline, display. No 9, 10.5, 11 or 13.5.
- Text colors: `fg4 #5e6975` is retired for text (3.67:1). The text floor is `fg3`.
- Colors: red = failed check; gold = limit; green = proven; cyan = action or focus; steel = unknown; magenta = paradox (MOIRE).
- Fidelity: grade A or B is sharp; C is degraded; D, E and not scored are grain, with "n = k" printed. No sweep animation on grain.
- One px `--measure` for body text; ledes span full width; em-dashes 0.

### 4.4 Print

Every fold opens and rows never split (PR 2145 rules, generalized). The site chrome is hidden. Light versus dark is Zach's call (§8).

### 4.5 HUD (J6 to J8)

- **Ziggurat polygon:** one terrace per atlas tier. Each evidenced edge between nodes on different terraces cuts a facet into the polygon. Facet count is the visible proof of work, and the render state per terrace follows §4.3.
- **Orbit and time:** drag to orbit; a time scrubber under the field; play forward and back. Scrubbing shows only the edges that existed at that time, so fidelity visibly grows and shrinks with history.
- **Kairos:** a gold ring marker at the node and time where a belief moved, readable from any angle. A list of kairos moments sits beside the field, each jumping the scrubber to it.
- **Earned:** an empty or thin atlas renders flat and grain with its sample size. A visual that cannot go flat on empty data is decoration (WORLD.md).

## 5. Product requirements

**User:** Zach, as operator. Later a counterpart sees the counterpart-safe twin through `/recoil-ship`.
**Job:** after a call, see in one screen what to do next, be able to prove why, and navigate how this call changed the terrain over time.

Functional:
- F1. `recoil run --call <granola-id|calendar-event-id> [--until J1..J8] [--dry-run]` runs the journey, writing each stage's print (ADR-068).
- F2. One SSOT schema v2 (a superset of today's six-tab SSOT plus `call.atoms`, verbs, claims with premise and mechanism, hypercube cells and atlas refs). Old SSOTs still render, through an adapter.
- F3. Renders: React page, single-file HTML, PDF and counterpart twin, all from one component set.
- F4. Atlas v2 export and HUD v2 loader.
- F5. A receipt draft at the end of every run (never auto-inserted; Zach approves).

Non-functional:
- N1. Every stage is idempotent and resumable. A rerun with no new input changes nothing.
- N2. Autopilot runs only reversible steps and stops at one-way doors (§6.3).
- N3. No counterpart PII in committed files beyond what the SSOT already holds. The counterpart twin passes the redaction policy.
- N4. A full run on the Brian fixture takes under 10 minutes of agent time, with token spend logged.

Success (pre-registered; counted only after it is fixed in writing):
- S1. The Brian fixture rebuilt end to end with zero hand edits. Both reviewers PASS.
- S2. The Gasmi and Schriner SSOTs render through the v2 path with no visual regression in print.
- S3. At least one kairos moment in the Brian atlas is findable from the HUD in under 7 seconds by a cold reader (memory `catch-in-seven-reel-with-curiosity`).

Non-goals: no auto-send, no public HUD, and no new npm dependencies without asking (the HUD stays SVG or canvas). No L6 or L7 engine.

## 6. Service architecture

### 6.1 Stages and prints

| Stage | Input | Output (print) | Gate |
|---|---|---|---|
| J1 decompose | Granola transcript, calendar event | `runtime/recoil/generated/<id>.json` with `call.atoms` | schema valid; every atom has a timestamp and a speaker |
| J2 verbs | SSOT | `verbs{}` with verdicts | each verdict cites at least one atom id |
| J3 deconstruct | SSOT claims | claims with premise and mechanism | claims-skeptic: every GROUNDED claim quotes an atom |
| J4 hypercube | SSOT | `cells[]` (lens, resolution, operator, verb, L) | cells reference existing atoms; no cell is invented |
| J5 atlas | SSOT | `<id>.atlas.json` (`arcs.atlas.v2`) | edges have evidence; acyclic within the time order |
| J6 to J8 HUD | atlas v2 | loaded in `/hud` (admin, local file) | flat on empty; kairos list matches the SSOT |
| Render | SSOT | page, HTML, PDF, twin | page_gate, artifact_wrap_lint, component_source_gate, token_source_gate, impeccable detect, brand-line-producer |

### 6.2 Composable

Each stage is a separate script that reads the SSOT and writes back only its own keys, so any stage can run alone (`--only J4`). The skills `recoil-prep` and `recoil-close` become thin callers of J1 to J3.

### 6.3 Autopilot until it passes

- Loop per stage: run, then gate. On FAIL, run one repair pass and gate again. At most three molts per stage per run; then stop and report the failing gate verbatim.
- "S-tier", "diamond cut", "superionic" and "flawless" mean one thing here: every gate in §6.1 passes, and both reviewers return PASS on the same head. Nothing more is claimed, and nothing less ships.
- Hard stops (never autopiloted): merge, publish or deploy, send to a counterpart, a paid voice or API call beyond the run budget, a canon or ADR change, and inserting a receipt row.

## 7. Implementation plan (induced backlog, ADR-086 pass 1)

Rows live in `_QUEUE/induced-backlog.jsonl` with `epic: recoil-call-service`. Critical path: R1 → R2 → R5 → R7 → R9 → R11.

| Row | Job | Depends on | Lane |
|---|---|---|---|
| R1 `recoil-kit-reconcile` | Land the light page's nine missing primitives in the kit under free numbers (56 to 64), with specimens. Register the `recoil-skim` template. Make component_source_gate pass. Rebuild the Brian page from the kit. | none | kit |
| R2 `recoil-ssot-v2-schema` | JSON schema v2 plus a validator and a v1 adapter; validate all generated SSOTs | none | schema |
| R3 `recoil-token-unify` | Generate `tokens.ts` from `_tokens.css`; four type steps; `fg4` off text | PR 2145 merged | heavy |
| R4 `recoil-service-cli` | `scripts/recoil_service.py` stage runner: `--call`, `--until`, `--only`, `--dry-run`, the molt loop and hard stops | R2 | service |
| R5 `recoil-component-set` | One component set rendering the §4.1 anatomy from SSOT v2 in React and single-file HTML | R1, R2, R3 | render |
| R6 `recoil-print-target` | Print opens folds, light or dark per §8, for both renders | R5 | render |
| R7 `recoil-decompose-verbs` | J1 to J3 stages: atoms, verb verdicts, claim premise and mechanism | R2, R4 | service |
| R8 `recoil-hypercube-index` | J4: a cell index from the SSOT plus the explorer view (slice picker and filled-cell list) | R7 | explorer |
| R9 `atlas-v2-schema-export` | `arcs.atlas.v2` (nodes, typed edges, time, kairos, evidence) and the SSOT-to-atlas export | R7 | atlas |
| R10 `forecast-base-rates` | Base rates for peer follow-up forecasts from past receipts (the light page's B9) | none | data |
| R11 `hud-atlas-v2-flight` | The HUD v2 loader: edge facets on the ziggurat, orbit, time scrub, kairos layer, flat on empty | R9 | hud |
| R12 `recoil-brian-acceptance` | Run the service on the Brian fixture end to end, both reviewers on the result, and the S1 to S3 count | R5, R6, R8, R11 | acceptance |

Child sessions: R1, R2 and R10 start now (independent, separate files). R4 starts once R2's schema lands on its branch. R3 waits on PR 2145. The rest follow the graph. At most four live sessions at a time.

## 8. Waiting on Zach

1. **"720°":** proposed as a 360° orbit in space plus a full scrub in time, forward and back. Or did you mean two full rotations, or yaw plus pitch?
2. PDF default palette: dark, as on screen, or light, to save ink and suit a printed read?
3. Counterpart twin: the same component set with an audience filter, or its own template?
4. Approve the hard-stop list in §6.3 as the autopilot boundary.
5. The light page holds a personal email address and a sensitive fact about the counterpart, behind only its artifact link. Keep it, or redact it now?

## 9. Status, 2026-11-12

**Merged (each with one decision receipt).** Spec and backlog PR 2146 (a09381ca). R1 kit reconcile PR 2150 (ac7ab355). R2 SSOT v2 schema PR 2151 (d568e4f2). R3 token unify PR 2155 (e157c8c9), plus PR 2161 (fg4 text sweep, c904fa1e). R4 stage runner PR 2154 (b3196ff8). R5 component set PR 2164 (b6485191). R7 J1 to J3 PR 2158 (36d18b25). R8 J4 hypercube index PR 2166 (101eeb1c). R9 atlas v2 and J5 export PR 2165 (2560d09b). R10 forecast base rates PR 2152 (af08123b). The print fix that started the arc is PR 2145 (50e8b80e).

**Critical path now.** R6 print target and R11 HUD flight are READY and independent of each other. R12 Brian acceptance waits on both. Nothing else in the epic is open.

| Row | State | Waits on |
|---|---|---|
| R6 `recoil-print-target` | READY | §8 question 2 (palette) decides its default |
| R11 `hud-atlas-v2-flight` | READY | §8 question 1 (720°) decides its orbit and scrub |
| R12 `recoil-brian-acceptance` | HOLDING | R6, R11; the Brian call has no SSOT yet (R5 hand-over) |

**Still open in §8.** All five: 720°, PDF palette, counterpart twin, the §6.3 hard-stop list, and the personal email and sensitive fact on the live Brian artifact. Questions 1 and 2 now gate a ready row each.

**Friction seen.** `_QUEUE/induced-backlog.jsonl` conflicted on nearly every PR in this epic. The READY row `backlog-merge-driver-by-id` (register `scripts/backlog_merge_by_id.py` as a git merge driver) removes that class.


## 10. Wave 2 (induced 2026-11-12, ADR-086 two passes)

Wave 1 built every stage and proved it on fake model answers. Wave 2 gets the first ground truth: one real call, one real model run, and acceptance on that run, not on fixtures. Rows carry `epic: recoil-call-service-wave2`. Prior art ran first (`/prior-art`, then the catalog per job): every row reuses an existing tool; only the cards skill may add one, and only if `/fold` and `backlog_graph.py` cannot already do it.

### 10.1 Pass 1: the candidates, each kept, cut or merged

| Candidate | Fate | Row | Why |
|---|---|---|---|
| Run J2 to J4 with a real model on one real call | Kept, split in two | `recoil-brian-ssot`, `recoil-real-model-run` | No SSOT exists for the Brian call, so the real run needs one first. The run is a paid step: Zach's go, cap 2 USD, local only. |
| R12 Brian acceptance and the S1 to S3 count | Merged into the existing row | `recoil-brian-acceptance` | The row already exists. Pass 2 adds two dependencies to it. |
| Backlog file conflicts on nearly every PR | Merged into the existing row | `backlog-merge-driver-by-id` | The row already names the tool and rejects union merge, since rows are edited in place. Promoted to READY, with a frustration gate added. |
| Backlog-to-session-cards skill (card task_7114301a) | Kept | `backlog-session-cards-skill` | Briefs drifted twice when written by hand. A brief built from the row's own fields removes that. It runs a reuse check against `/fold` first. |
| Counterpart twin for recoil-ship | Kept, HOLDING | `recoil-ship-twin` | Waits on §8 Q3. This is a one-way door, so the PII gate and the gauntlet run before anything is sent. |
| Wire `/recoil-prep` and `/recoil-close` onto the runner | Kept, after the real run | `recoil-skills-on-runner` | Neither skill calls the runner today. Wiring them onto stages that have only seen fake answers would lock in paths nobody has tested. |
| Kairos and time-scrub acceptance in under 7 seconds | Kept, HOLDING | `recoil-kairos-7s-test` | R11 builds J6 to J8. A person times the read. A headless check covers flat on empty. |
| Catalog and JTBD-graph entries for the epic's tools | Kept, READY | `recoil-epic-tool-catalog` | `jtbd-graph --check` fails with 3 new orphan tools, and J4 and J5 are missing from the catalog. |

### 10.2 Pass 2: Loki repairs (evidence in each row)

1. **Acceptance on fake answers proves only the plumbing.** R12 now also depends on `recoil-real-model-run` and `recoil-kairos-7s-test`.
2. **A merge driver does not change what GitHub shows.** GitHub's server-side mergeability ignores local drivers, so PRs will still show CONFLICTING. The driver removes the hand resolution, not the round trip. Measure set in advance: count hand-resolved backlog conflicts over the next 10 PRs.
3. **The real run spends from the shared API cap.** It is capped at 2 USD, runs locally and never in CI, and does a dry run first.
4. **The Brian SSOT carries PII.** It stays internal and waits on §8 Q5. Counterpart quotes carry no source tags without the notetaker's consent.
5. **The cards skill may duplicate `/fold`.** The reuse check is its first gate.

### 10.3 Order

READY now: `recoil-epic-tool-catalog`, `backlog-merge-driver-by-id`. OPEN with no dependency: `backlog-session-cards-skill`. §8 Q5 gates `recoil-brian-ssot`, which leads to `recoil-real-model-run` (a spend go), then `recoil-skills-on-runner` and R12. R11 leads to `recoil-kairos-7s-test`, then R12. §8 Q3 gates `recoil-ship-twin`.

**Merge queue.** One session, recoil-wave2, merges every recoil PR, one at a time, with `scripts/safe_merge.sh`, and only on Zach's own go. Owners merge main into their own branches when the backlog file conflicts. The merge-train session keeps the non-recoil PRs.

### 10.4 First real run, 2026-11-12 (Gasmi)

On Zach's "go ahead" for the spend, the runner ran J1 to J4 on the Gasmi SSOT with the deep-role model and a 1 USD cap. The run used Gasmi because its SSOT is on main and Brian has none. Every stage passed. Measured against R8's bar, set before the run:

| Bar | Result |
|---|---|
| 0 invented cells | Met. The gate allows none. |
| At least 3 filled cells on one real call | Met. 9 cells of 3,125. |
| A rerun shows J4 UNCHANGED at no new cost | Met. J1 to J4 UNCHANGED, no new calls. |
| A cold reader agrees with at least 2 of 3 sampled cells | Not run yet. This needs a person. |

What real answers showed:
- J3 dropped 8 of the model's 14 claims because they cite no atom. The gate did its job.
- J2 graded every verb C or D on only 7 atoms, so this run sits at grain.
- J4 ran at version 1, with the fixed operator mapping. PR 2177 replaces that mapping with a judged axis, so J4 runs once more after 2177 merges.
- The runner prints no spend figure. That is a gap for the budget gate's audit.
