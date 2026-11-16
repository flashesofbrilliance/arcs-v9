# Backlog work graph and fates packet (2026-11-16)

**Status:** GROOMED 2026-11-16. Zach answered sections 2 and 3 in the groom the same day. Below is what was applied and what was held.

## Groom record (2026-11-16, 25 minutes)

**Approved and applied** (`scrum.apply_fates`, under its lock):
- **Section 2, all seven items:**
  - rfp-ship: 2 rows DONE, 1 SUPERSEDED.
  - 4 rows HOLDING to READY.
  - 4 rows to BLOCKED with resolve_by 2026-11-30 (the 3 waiting on a ruling, plus `brooks-audit-proposal-send`).
  - `backlog-fate-triage-2026-10-18` SUPERSEDED, and `onchain-receipt-anchor-registry` COMPOSTED.
- **Claims released to OPEN:** `engagement-compounding-v0` and `gravity-eir-candidate-brief`. Not released, by Zach's choice: `gauntlet-brief-polyform` and `pr-design-brief-habit`.
- **Fates:**
  - 79 Phosphor rows renewed to 2026-12-14.
  - 13 filing rows renewed to 2026-11-30.
  - 19 more renewed to 2026-11-30: the scrum renew defaults, plus `warm-path-campaign-v0` and `role-lens-kaizen-loop`, which are kept.
  - 41 composted by the default.
- **Sprint** (logged in `_STATE/scrum/ledger.jsonl`): `filing-prior-filings`, `filing-audit-log`, `filing-who-saw-it`, `recoil-brian-ssot`, `cia-technical-screen-prep`.
  - Goal: settle the disclosure clock and land recoil wave 2's next step.
  - Queued for the next sprint: `recoil-hardstop-amend`, `seat-backlog-row-adapter`, `ready-now-door-decision-split`, `backlog-tiebreak-rule`. Zach asked for both sprint sets, and the cap is 5 a sprint.
- **Rule AGENTS gotcha 2** (inline styles only): verdict **move**, to a path-scoped rule. The edit is a separate small PR.

**Held, not composted, and back to Zach.** I found these after the approval: composting them would break a dependency chain or drop a safety task.
- **4 rows have live dependents,** so composting them leaves dead edges: `model-roles-upgrade-haiku-opus`, `rc-ops-001-graduation-ruling`, `svc-sage-should-it-exist-decision`, `tao-renders-regenerated-from-projection`.
- **3 more are their upstream rows,** restored after the dead-edge check: `model-outcome-eval-set`, `accountant-calibration-curve`, `accountant-external-cohort-nonzero`.
- `model-provider-adapter` is the parent of the 4 children added today. `doc-gates-blocking` is what rank 19 unblocks.
- `agent-readable-arcs-hosts` was committed in the last sprint (its first slip).
- **API key and spend safety:** `old-anthropic-callers-moved`, `revoke-old-anthropic-keys`, `anthropic-spend-monitor`.
- `cia-recoil-close-michael-intro` waits on whether the Michael call happened.

After the groom, both gates pass (`backlog_status_check --check` and `universe_jtbd_adapter.py --check`), and the graph shows 0 dead dependencies, 0 dangling and 0 cycles. Live rows: 344 before, 298 after.

*The sections below are the packet as proposed before the groom.*

## Why

The induced backlog holds 575 rows and 331 of them are live. Before this pass most active rows had no epic, 136 named their tool only in prose that no gate can match, and the groom had not run since 2026-11-05. So the graph could order the rows but not say who or what does each one. Sessions planned from scratch, and stale rows drifted away from reality. Example: the public `rfp-engine` repo has existed since 2026-11-02, and four rows still say it is OPEN.

## What

One pass over the active rows, using tools that already exist:

- **Epic:** every active row now names one. 292 came from the cluster index (`runtime/specs/backlog-index.json`, 2026-11-12) and 16 were already set. 1 came from its id family, and 22 I placed by hand: 15 `spec-*` decide or reconcile rows go to a new epic `spec-decide-reconcile`, and 7 others go to existing clusters.
- **Tool:** every active row now carries `tool_id` (`tool:<kind>:<name>`, an atom in the JTBD graph) or `tool_id: "missing"` with a `tool_gap` reason. 279 come from the graph's own serves and needs edges; where a row has several, the tool named first in its own `route.tool` wins. 79 Phosphor rows take `scripts/phosphor_build.py`, the cluster's only build path. I wired 20 by judgment against the catalog. 32 stay missing: 6 human decisions, 6 human acts, 5 that need only git or gh, 3 that need the uncatalogued `jobs_*.mjs` scripts (memory `tool-catalog-skips-mjs-scripts`), 11 builds and 1 speculative. Since then, 4 more active rows carry `tool_id: "missing"`: the 3 drift-classifier children, and `ds-artifact-sync-on-kit-merge`, which landed on main during this pass (PR 2280). Its script exists, but the tool catalog has not been regenerated since. That makes 36 in all.
- **Design dependencies:** 114 rows now carry `design_deps`, a list of `{ref, kind, state}` for each kit organism, token or spec they name. Every named dependency resolves in the repo (kit numbers 01 to 73 checked against `src/ui-kit/kit-manifest.json`), so each one is `unblocked`. Two rows needed an organism that does not exist, and each is now specified: `brief-problem-shape-layouts` gets the child row `brief-shape-organisms-spec`, and `phosphor-te-gauge-knobs` has its organism spec on the row, with the child to be cut when the row resumes (it is HELD). I cleared 9 rows where "kit" meant a sound kit or a build sheet.
- **Children:** three OPEN or HOLDING code rows were bigger than one PR, and each is now an epic with children: `jtbd-graph-s5-wider-sample` (3), `model-provider-adapter` (4), `drift-classifier-productive-destructive` (3). Each child depends on the one before it. The 20 filing rows are sized in days of Zach's time, not in PRs, and already form a chain, so I left them alone. `phosphor-pattern-text-box` is already built and waits only for the release checkpoint.
- **Edges:** I fixed the 2 `unblocks` and `depends_on` mismatches (`option-board-generator` is now a dependency of `seed-atomic-composer` and `seed-induced-render-engine`). The one dead dependency is a fate, so it is listed below.
- **Stack rank:** 30 rows carry `stack_rank` (1 to 30) and a one-line `rank_reason`.
- **JTBD graph:** the new `tool_id` keys gave 83 orphan jobs a tool. I removed those 83 from the baseline ratchet, which may only shrink (151 to 68 held). The three new drift-classifier children are held in `jtbd-graph-triage.json` until 2026-11-30, the same gap their parent is held for.

How each row was edited: keys were appended at the end of the line, so every existing byte is unchanged except the two `depends_on` fixes. The children and this session's row went in through `scripts/backlog_append.py` (ADR-092). Both gates pass: `backlog_status_check.py --check` and `universe_jtbd_adapter.py --check`.

## Why now

The groom is 11 days overdue. RUNNING rows are at 9 against a cap of 3. The backlog grew by a net 46 rows last week. Tomorrow (2026-11-17) the jtbd-graph s5 quality check is scored and 32 triage holds expire. A ranked graph with tools attached makes that groom a 25-minute ritual rather than another hand pass.

## How

- **Before (done in this PR):** the row edits above, the ranking, and this packet. Nothing is merged.
- **During (Zach, one sitting, about 25 minutes):** answer sections 2 and 3 with yes, no or edit per line. Then `scripts/scrum.py fate` applies the fates you approve, line by line, under a lock.
- **After:** the next session pulls from the top of the rank. `backlog-tiebreak-rule` (rank 16) and `seat-backlog-row-adapter` (rank 13) let the graph compute this order itself next time.

**How to read this page:** section 1 is the rank, section 2 lists the state corrections where the rows disagree with reality, and section 3 lists the groom fates in groups. The appendix lists all 171 fate candidates by epic.

## 1. Stack rank, top 30

I ranked on four axes, in this order:
1. **Ruin:** irreversible loss, or a clock that closes a door.
2. **Reversibility:** two-way doors go before one-way doors.
3. **Readiness:** the trigger has fired and the dependencies are DONE.
4. **Leverage:** how many rows sit downstream.

There are only 21 READY rows. So the 30 also draws on the graph's "ready now" set and on HOLDING rows whose dependencies are all DONE. Those rows are flagged, and their state change is in section 2.

| # | Row | Lane | Tool | Reason |
|---|---|---|---|---|
| 1 | filing-prior-filings | Zach | filing_workback.py | Says whether a disclosure clock is already running; heads a 16-row chain |
| 2 | filing-audit-log | Zach | filing_workback.py | Dates the public windows; 16 downstream |
| 3 | filing-who-saw-it | Zach | filing_workback.py | Fixes the audience while memory is fresh; same sitting (bundle B1) |
| 4 | filing-anonymize-detail | Zach | filing_workback.py | Records history rewrites before they are forgotten |
| 5 | filing-conception | Zach | filing_workback.py | Conception dates anchor every mechanism claim; 13 downstream |
| 6 | filing-offrepo | Zach | filing_workback.py | Widest unknown in the ledger; 3 days |
| 7 | filing-select-counsel | Zach | filing_workback.py | 14-day lead time; start now to keep it off the critical path |
| 8 | recoil-brian-ssot | agent | recoil_service.py | Handoff's named next session; unblocks R12 |
| 9 | recoil-hardstop-amend | agent | recoil_service.py | READY on the recorded section 8 Q4 answer; widens autopilot, so the stop list shows in the diff |
| 10 | recoil-kairos-7s-test | agent | page_gate.py | Dependency DONE (HOLDING, see section 2); gates R12 |
| 11 | cia-technical-screen-prep | agent + Zach | /precall-brief | Time-bound by the Michael intro |
| 12 | harrison-followup-2026-11-09 | Zach sends | /recoil-ship | A week late; the draft exists |
| 13 | seat-backlog-row-adapter | agent | arcs_operator_contract.py | Lets the operators read rows, so the next groom is computed |
| 14 | ready-now-door-decision-split | agent | backlog_graph.py | Ruin reducer: one-way rows without a rollback leave "ready now" |
| 15 | line-triage-reads-gates-one-way | agent | line_triage.py | Same ruin family |
| 16 | backlog-tiebreak-rule | agent | backlog_graph.py | Makes this ordering computable |
| 17 | jtbd-graph-s5-feedback | agent | jtbd_drift_report.py | Check is scored tomorrow; 2 rows wait on it |
| 18 | seat-unbound-triage | agent | operator_binding_emit.py | 29 unbound seats; unblocks 2 rows |
| 19 | doc-gate-false-positive-cleanup | agent | canon_propagation_check.py | Unblocks doc-gates-blocking; starts with a recount |
| 20 | universe-outcome-capture | agent | receipt_outcome_queue.py | Closed outcomes are 2 of 247 |
| 21 | five-person-outcome-test | Zach | outcome_funnel.py | First external outcomes |
| 22 | receipt-real-interview-closes | agent + Zach | receipt_outcome_queue.py | Dependencies DONE; about 5 minutes per receipt |
| 23 | echo-fake-exit-audit | agent | /echo-scan | User-facing trap controls |
| 24 | echo-surface-restates-receipt-audit | agent | /echo-scan | Restated claims are the card-fact drift source |
| 25 | ci-orbstack-linux-vm-runners | agent | safe_merge.sh | Parallel Linux runners cut merge-queue wait |
| 26 | accountant-weekly-first-unattended | agent | accountant_weekly.py | Today's PR 2279 is a live sample |
| 27 | rfp-ship-resume-tailor-rebase | agent | resume-tailor surface | 15 minutes; branch on origin |
| 28 | arcs-mini-adopt-design-md-motion | agent | motion_policy_gate.py | 30 minutes; its tokens exist |
| 29 | open-loops-ssot-drift-line | agent | open_loops.py | Would have caught the rfp-ship lag |
| 30 | rfp-ship-skill-locate | agent | missing (human-act) | The public repo has no SKILL.md or plugin yet |

**Left out of the 30 on purpose:**
- `agent-receipts-audit-first-conversion` and `recoil-ship-twin` are one-way doors with high ruin. They need Zach's decision, not a slot.
- `merge-train-only-path` waits on the ADR-085 ruling.
- `rfp-ship-engine-branch-reconcile` looks ready, but it is likely moot (section 2, item 1).
- `backlog-fate-triage-2026-10-18` is replaced by this packet.

## 2. State corrections (the row disagrees with reality)

1. **The rfp-ship chain lags the live repo.** `flashesofbrilliance/rfp-engine` is public, created 2026-11-02, head `c340f0ba`, with `mcp/server.py` but no SKILL.md or plugin. Proposal:
   - `rfp-ship-public-repo-decide` and `rfp-ship-public-repo-create` go to **DONE**, citing the repo.
   - `rfp-ship-engine-branch-reconcile` goes to **SUPERSEDED**: neither branch it names is on origin, and the repo shipped.
   - `rfp-ship-public-leak-gate` goes to **DONE only with proof** that the gate ran before the push. I found none, so it stays OPEN until you say otherwise.
2. **HOLDING rows whose dependencies are all DONE:**
   - Proposed **READY:** `jtbd-graph-s5-feedback`, `recoil-kairos-7s-test`, `receipt-real-interview-closes`, `seat-binding-design-log`, but only if its trigger (the option-board pick log) landed with PR 2227, which I have not checked.
   - Proposed **BLOCKED on Zach**, because their triggers are a ruling and not a dependency: `merge-train-only-path` (ADR-085), `agent-receipts-audit-first-conversion` (one-way first sale), `recoil-ship-twin` (one-way, counterpart-facing).
   - Ask: has the Michael intro call happened? If yes, `cia-recoil-close-michael-intro` goes to READY.
3. **HOLDING with nothing to wait on (9 rows):**
   - Rows: `lane-edge-existing-25`, `phosphor-heading-light-rays`, `phosphor-optical-sensor-controller`, `phosphor-pad-mute-choke`, `ex-ante-paired-paths-template`, `gravity-well-polarize-wiring`, `throughput-baseline-2026-10-20`, `brooks-audit-proposal-send`, `shadowed-routes-decision`.
   - HOLDING means waiting on a `depends_on` row, and these name none. Proposal: name the row each waits on, or move the row to OPEN (no wait) or HELD (paused by you). `brooks-audit-proposal-send` waits on your send, so I would make it BLOCKED.
4. **Stale RUNNING claims (more than 3 days):**
   - Rows: `engagement-compounding-v0`, `gravity-eir-candidate-brief`, `pr-design-brief-habit`, and `gauntlet-brief-polyform`.
   - `gauntlet-brief-polyform` is claimed by local_e19309e9, the session that started this one.
   - Proposal: release each claim to OPEN unless the owner confirms it is live. That brings RUNNING from 10 (9 plus this pass) toward the cap of 3.
5. **Rows that cite closed or merged PRs:**
   - `asm-009-net-direction-decided` cites PR 598, which was closed: re-point the row or compost it.
   - `phosphor-rc1-firefox-verify` cites PR 1619, which was merged. The row waits on a manual Nightly.app open, so keep it HELD with a review_by date.
6. **Dead dependency:** `onchain-receipt-anchor-registry` depends on `fc-derisk-wallet-funding`, which is COMPOSTED. Proposal: compost the anchor row too (speculative, cluster C17), or drop the dependency and keep it HELD.
7. **`backlog-fate-triage-2026-10-18`** goes to **SUPERSEDED** by this packet.

## 3. Groom fates (171 candidates, grouped)

`scripts/scrum.py board` lists 171 rows to fate. Each one is a HELD or HOLDING row with no review_by date, or with a review_by date that has passed. Its default is compost when there is no review_by and renew when the date has passed. I disagree with the default in two groups:

| Group | Rows | Scrum default | My proposal | Why |
|---|---|---|---|---|
| C01 Phosphor features | 79 | compost 76, renew 3 | Keep HELD with one review_by: the next Phosphor release checkpoint | Each row is a feature with a demander (kid and parent modes); composting them loses the spec text. One date fates all 79 |
| C02 IP filing chain | 13 | compost | **Renew**, review_by 2026-11-30 | They are HOLDING behind ranks 1 to 7 and carry the ruin clock; composting them breaks the chain |
| C13 job search | 14 | compost 12, renew 2 | Default, except keep `warm-path-campaign-v0` and `role-lens-kaizen-loop` | Those two close the outcome loop for the money lane |
| C12 PRL and revenue | 8 | compost 7, renew 1 | Compost the 6 PRL task rows (`prl-task*` and `prl-empty-email-e2e`); default for the other 2 | The tasks fold into `prl-phase-1-2`, which stays BLOCKED |
| All other clusters | 57 | mostly compost | Default | No demander or clock named in their rows |

One command per group applies the fates you approve, for example `scripts/scrum.py fate --renew <ids> --review-by 2026-11-30`.

## Appendix: the 171 fate candidates by epic

Source: `scripts/scrum.py` `fate_candidates()` on 2026-11-16. The default is scrum's rule, not my proposal (see section 3).

### C01-phosphor-instrument (79)

- `phosphor-303-bass-lane` HELD, no review_by, added 2026-10-15. Default **compost**. TB-303 style lane: pitch, gate, accent and slide per step mapped to color, zoom and wobble
- `phosphor-audio-retro-buffer` HELD, no review_by, added 2026-10-15. Default **compost**. Rolling 32 bar audio ring of the output bus (about 11 MB mono at 44.1 kHz), in memory only
- `phosphor-auto-loop-catch` HELD, no review_by, added 2026-10-15. Default **compost**. Auto-loop: 'Loop this' picks the best matching stretch with downbeat and zero-crossing edg
- `phosphor-back-panel-cables` HELD, no review_by, added 2026-10-15. Default **compost**. Object interface: Grown-up controls become the back panel of the player (flip it over to s
- `phosphor-band-triggers` HELD, no review_by, added 2026-10-15. Default **compost**. Band-pass triggers: low, mid and high band hits arpeggiate color, zoom and wobble, synced
- `phosphor-codes-ladder` HELD, no review_by, added 2026-10-15. Default **compost**. Codes as lessons: a ladder of short musical codes (rhythm, three-note pitch on a pentatoni
- `phosphor-consonance-dissonance-budget` HELD, no review_by, added 2026-10-15. Default **compost**. Consonance-aware matching and auto slice (chroma profile and key, roughness, shared partia
- `phosphor-copy-me-game` HELD, no review_by, added 2026-10-15. Default **compost**. Copy me: the page plays a short pattern, the child repeats it; a match lengthens and speed
- `phosphor-detect-suite` HELD, no review_by, added 2026-10-15. Default **compost**. Song analysis for pitch, key, time signature, melody and lead, with drum and addition sugg
- `phosphor-dj-hard-parts` HELD, no review_by, added 2026-10-15. Default **compost**. Hard DJ features to decide on later: key lock (needs real time-stretch such as a phase voc
- `phosphor-dj-style-presets` HELD, no review_by, added 2026-10-15. Default **compost**. DJ style presets, each a tempo, groove, one or two effects and one signature Move button:
- `phosphor-dj-table-stakes` HELD, no review_by, added 2026-10-15. Default **compost**. DJ table stakes for Phosphor, local only: 3-band EQ with kill switches (isolator), a filte
- `phosphor-drum-machine-rows` HELD, no review_by, added 2026-10-15. Default **compost**. Add synthesized drum rows (Kick, Snare, Clap, Hat) with per-step accent to the Phosphor st
- `phosphor-earned-automagic` HELD, no review_by, added 2026-10-15. Default **compost**. Mastery-gated Magic offers on the patch board: tap in time then auto tempo and snap; hand
- `phosphor-edge-functions-stance` HELD, no review_by, added 2026-10-15. Default **compost**. Decision note: edge functions are request and response with a network round trip and cold
- `phosphor-embedded-lyrics-karaoke` HELD, no review_by, added 2026-10-15. Default **compost**. Read embedded lyrics (ID3 USLT or MP4 lyrics tag) from the song file and show them as kara
- `phosphor-first-minute-ritual` HELD, no review_by, added 2026-10-15. Default **compost**. A first-minute ritual in the vocabulary of the creative habit: a one-key first move the ch
- `phosphor-flying-faders` HELD, no review_by, added 2026-10-15. Default **compost**. Automation lanes with flying controls: knobs and faders move on their own on playback and
- `phosphor-four-resolution-dials` HELD, no review_by, added 2026-10-15. Default **compost**. Four independent resolution dials, each a physics lesson and a creative crush: pixels (spa
- `phosphor-gesture-grab-preset` HELD, no review_by, added 2026-10-15. Default **compost**. Rolling 32 bar gesture buffer (control changes as small events, not audio) with Grab: choo
- `phosphor-gesture-set` HELD, no review_by, added 2026-10-15. Default **compost**. Build the six gestures on the picture with synthetic-touch checks: tap play and pause, swi
- `phosphor-glass-grow` HELD, no review_by, added 2026-10-15. Default **compost**. Glass style additive process: a cell loops and one note is added or removed each turn (Gro
- `phosphor-granular-engine` HELD, no review_by, added 2026-10-15. Default **compost**. One granular time-stretch and pitch-shift engine in plain JavaScript (no dependencies), of
- `phosphor-hardware-link` HELD, no review_by, added 2026-10-15. Default **compost**. Let a small pad and knob device drive the page over Web MIDI or Web HID (same UI, hardware
- `phosphor-kid-pattern-promote` HELD, no review_by, added 2026-10-15. Default **compost**. Promote _PATTERNS/2026-10-15-kid-play-surface-pattern.md after a real child session: add t
- `phosphor-kintsugi-seams` HELD, no review_by, added 2026-10-15. Default **compost**. Gold seam on Tidy and repair: when order is restored the repair shows as a visible gold li
- `phosphor-latency-worklet` HELD, no review_by, added 2026-10-15. Default **compost**. Measure end-to-end latency (key press to sound) with outputLatency, baseLatency and a loop
- `phosphor-life-lane` HELD, no review_by, added 2026-10-15. Default **compost**. Experiment: a Life lane where a cellular automaton grows the step pattern, seeded from his
- `phosphor-lock-a-bar` HELD, no review_by, added 2026-10-15. Default **compost**. Write-lock for a bar: Lock this bar makes a pocket of order that holds exact while its sur
- `phosphor-loudness-chain` HELD, no review_by, added 2026-10-15. Default **compost**. Loudness chain: measure the loudness of a song on load (a K-weighted or plain RMS estimate
- `phosphor-moon-water-presets` HELD, no review_by, added 2026-10-15. Default **compost**. Moon (Satie corner) and Water (Debussy corner) presets plus a whole-tone scale option for
- `phosphor-my-loops-shelf` HELD, no review_by, added 2026-10-15. Default **compost**. A local 'my loops' shelf of kept moments (receipts) with a parent-controlled delete; store
- `phosphor-note-repeat-swing` HELD, no review_by, added 2026-10-15. Default **compost**. Note Repeat (hold a pad to retrigger at 1/8, 1/16, 1/32 locked to tempo) and Swing (every
- `phosphor-notomation-check` HELD, no review_by, added 2026-10-15. Default **compost**. Invariant and check: no suggestion, preset or quantize applies itself silently; offers onl
- `phosphor-order-decay-pockets` HELD, no review_by, added 2026-10-15. Default **compost**. Order level, decay rate and pockets of order for Phosphor patterns: seeded deterministic j
- `phosphor-parent-learning-summary` HELD, no review_by, added 2026-10-15. Default **compost**. Plain weekly summary for a parent of what the child is learning (rhythm, pitch, intervals,
- `phosphor-patch-bay-real-graph` HELD, no review_by, added 2026-10-15. Default **compost**. Back panel patch bay that draws the real audio graph (nodes and their actual connections)
- `phosphor-phase-field-viz` HELD, no review_by, added 2026-10-15. Default **compost**. Phase field visual mode (fluid and thermal): a small own solver (Stable Fluids smoke and h
- `phosphor-queued-pattern-song` HELD, no review_by, added 2026-10-15. Default **compost**. Next pattern queued to the next bar line (pattern memory sync) and Song mode chaining patt
- `phosphor-real-piano-bridge` HELD, no review_by, added 2026-10-15. Default **compost**. Map the melody strip one to one to a real keyboard over Web MIDI (a MIDI piano), and a Rea
- `phosphor-realtime-fx-rack` HELD, no review_by, added 2026-10-15. Default **compost**. Real-time effects rack on the existing effect-stage framework: echo and delay, chorus, rev
- `phosphor-reverse-tape-stop` HELD, no review_by, added 2026-10-15. Default **compost**. Reverse (hold, slip optional), tape-stop slide down, spin-up slide, and nudge push for Pho
- `phosphor-rhythm-pattern-detect` HELD, no review_by, added 2026-10-15. Default **compost**. Detect rhythmic patterns: quantize each bar's hits to 16 steps in low, mid and high bands,
- `phosphor-scratch-wheel` HELD, no review_by, added 2026-10-15. Default **compost**. Jog wheel that follows the hand: scratch with audio following velocity, backward and forwa
- `phosphor-seed-mash` HELD, no review_by, added 2026-10-15. Default **compost**. Seed extraction (best loopable one-bar cells), auto reseed remix, and Mash (voice as targe
- `phosphor-slip-sync` HELD, no review_by, added 2026-10-15. Default **compost**. Slip sync: nudge the song against the grid while playing (and a per-song memory of the cor
- `phosphor-smart-replay-note` HELD, no review_by, added 2026-10-15. Default **compost**. Smart replay at runtime is the gesture buffer plus flying faders built together: record tw
- `phosphor-song-memory` HELD, no review_by, added 2026-10-15. Default **compost**. Song memory: key the page's settings per song by the Suno id in the file comment (fall bac
- `phosphor-sparse-defaults` HELD, no review_by, added 2026-10-15. Default **compost**. Make Phosphor's glitch sparse and post-minimal by default: one effect at a time (chords un
- `phosphor-te-gauge-knobs` HELD, no review_by, added 2026-10-15. Default **compost**. Teenage Engineering style single-gauge knob and slider as one accessible SVG component in
- `phosphor-te-sequencer-skin` HELD, no review_by, added 2026-10-15. Default **compost**. Teenage Engineering look for the sequencer (square keys, LED row, functional labels) exten
- `phosphor-tempo-swing` HELD, no review_by, added 2026-10-15. Default **compost**. Tempo slider (turtle to rabbit) and swing (every second sixteenth late) for the Phosphor s
- `phosphor-timing-correct-strength` HELD, no review_by, added 2026-10-15. Default **compost**. Timing correct for recorded pad hits: quantize to 1/8, 1/16 or 1/32 at a strength from 0 t
- `phosphor-voice-effects` HELD, no review_by, added 2026-10-15. Default **compost**. Voice effects on the Sing loop: Robot (auto-tune to a scale), Choir (harmony voices), Mons
- `phosphor-web-midi` HELD, no review_by, added 2026-10-15. Default **compost**. Web MIDI input for Phosphor (notes to steps and pads, clock to tempo)
- `phosphor-wheel-island` HELD, no review_by, added 2026-10-15. Default **compost**. Wheel Island: a persistent foreground pill over the picture (compact: play and level ring)
- `phosphor-acoustic-sync-test` HELD, no review_by, added 2026-10-16. Default **compost**. An acoustic sync check: render both decks offline, find onsets in the rendered mix, and me
- `phosphor-aesthetic-constitution` HELD, no review_by, added 2026-10-16. Default **compost**. Aesthetic judgment as rules: a short constitution of constraints and policies (sparse, wab
- `phosphor-beam-controller` HELD, no review_by, added 2026-10-16. Default **compost**. Virtual D-Beam: a beam strip you break with the mouse, a finger or a keyboard arrow, in th
- `phosphor-binaural-beats` HELD, no review_by, added 2026-10-16. Default **compost**. Binaural beats as an optional ambient layer: a slightly different pure tone in each ear (f
- `phosphor-deck-dj-core` HELD, no review_by, added 2026-10-16. Default **compost**. Finish the DJ core on the mixer: (1) deck loops with beat-length in and out snapped to the
- `phosphor-euclid-polyrhythm-quantize` HELD, no review_by, added 2026-10-16. Default **compost**. Smart quantization that is more rhythmic and less random, built on algorithmic polyrhythms
- `phosphor-freeze-dance-coop` HELD, no review_by, added 2026-10-16. Default **compost**. Freeze Dance co-creation game for parent and child, like the dance game in Bluey: music pl
- `phosphor-genre-kits` HELD, no review_by, added 2026-10-16. Default **compost**. A few genre kits for kids, each one tap: a look, an effect preset and a pad kit (for examp
- `phosphor-heading-light-rays` HOLDING, no review_by, added 2026-10-16. Default **compost**. Pointer-following light rays behind the word 'light' in the heading (the pointer is the li
- `phosphor-light-controls` HELD, no review_by, added 2026-10-16. Default **compost**. Light controls: Exposure, Aperture (pinhole size), Shutter angle, pose rate. A strobe is t
- `phosphor-numpad-finger-drum-map` HELD, no review_by, added 2026-10-16. Default **compost**. Finger-drumming map for the right-hand keypad block, for a kid with small hands and for a
- `phosphor-parent-kid-access` HELD, no review_by, added 2026-10-16. Default **compost**. Real Kid/Parent toggle: parents unlock with a passkey (or a parent phrase where passkeys a
- `phosphor-platter-speed` HELD, no review_by, added 2026-10-16. Default **compost**. Platter speed and reverse for the main player: speeds 33 1/3, 45 and 78 relative to a chos
- `phosphor-player-dock-states` HELD, no review_by, added 2026-10-16. Default **compost**. The bottom player gets three states: full, hidden (drag it down off screen to a small bump
- `phosphor-player-waveform-hotcuts` HELD, no review_by, added 2026-10-16. Default **compost**. The bottom player grows an edit mode: the scrubber becomes a waveform of the song where ho
- `phosphor-simulated-user-pretest` HELD, no review_by, added 2026-10-16. Default **compost**. Simulated-user pre-test harness: Playwright personas (child, parent, DJ) driving the direc
- `phosphor-tempo-detector-v2` HELD, no review_by, added 2026-10-16. Default **compost**. Tempo detector v2: real-song agreement with the independent estimator is poor on several s
- `phosphor-virtual-pad-mapping` HELD, no review_by, added 2026-10-16. Default **compost**. Virtual pad MPC modality: a large 4x4 touch pad grid (56 px or more, spaced for gross and
- `phosphor-tempo-map-slice3` HELD, past review_by 2026-11-08. Default **renew**. Finish the tempo map: slicing sync rates per segment, mixer deck phase, genome windows on
- `phosphor-pad-mute-choke` HOLDING, past review_by 2026-11-08. Default **compost**. Pad mute and choke groups for the pad block (a pad can silence others in its group, a pad
- `phosphor-render-surface` HELD, past review_by 2026-11-08. Default **renew**. Make the offline render usable and complete: a Render to WAV button for grown-ups (downloa
- `phosphor-webkit-eject-lock` HELD, past review_by 2026-11-08. Default **renew**. On the WebKit engine (the engine behind iPhone and iPad), after entering the Kid lock, hol
- `phosphor-pattern-text-box` HOLDING, past review_by 2026-11-06. Default **compost**. Pattern text box (Parent mode only) that fills the existing 16-step sequencer lanes from a

### C02-ip-filing-chain (13)

- `filing-counsel-intake` HOLDING, no review_by, added 2026-10-15. Default **compost**. Hand counsel the ledger, conception evidence and the mechanism list
- `filing-draft` HOLDING, no review_by, added 2026-10-15. Default **compost**. Draft provisional(s) for tier 1
- `filing-file` HOLDING, no review_by, added 2026-10-15. Default **compost**. FILE tier-1 provisionals
- `filing-foreign-decision` HOLDING, no review_by, added 2026-10-15. Default **compost**. Foreign filing decision (PCT or direct) per tier
- `filing-inventory` HOLDING, no review_by, added 2026-10-15. Default **compost**. Invention disclosure write-up per mechanism (Y-gate, receipt diff, ARCS Law, kintsugi, wri
- `filing-ledger-final` HOLDING, no review_by, added 2026-10-15. Default **compost**. Ledger v2: every date VERIFIED or explicitly open
- `filing-nonprov` HOLDING, no review_by, added 2026-10-15. Default **compost**. Non-provisional / PCT due (12 months after the provisional filing date)
- `filing-outreach` HOLDING, no review_by, added 2026-10-15. Default **compost**. Institutes and grant programs with dated filing in hand
- `filing-preprint` HOLDING, no review_by, added 2026-10-15. Default **compost**. arXiv / SSRN preprint
- `filing-prereg` HOLDING, no review_by, added 2026-10-15. Default **compost**. Pre-register the six falsifiable claims (OSF or AsPredicted)
- `filing-prioritize` HOLDING, no review_by, added 2026-10-15. Default **compost**. Tier the mechanisms with counsel: file now, file later, trade secret
- `filing-public-surface-decision` HOLDING, no review_by, added 2026-10-15. Default **compost**. Decide what to do with pages still serving enabling detail (pf-12d-orbital, pf-knowledge-l
- `filing-review` HOLDING, no review_by, added 2026-10-15. Default **compost**. Zach review and corrections of drafts

### C05-recoil-adjacent (2)

- `debrief-vox-capture` OPEN, no review_by, added 2026-10-15. Default **compost**. The vox step sits BETWEEN /recoil-close and the recoil report: pipeline recoil-prep > call
- `cia-recoil-close-michael-intro` HOLDING, past review_by 2026-11-05. Default **compost**. After the intro call with Michael Lederman, run /recoil-close: score the ex-ante expectati

### C07-outcomes-calibration (9)

- `conviction-chips-calibration` HELD, past review_by 2026-11-08. Default **renew**. Ex-ante conviction staking on every claim in ARCS cases (and later the compass): the playe
- `accountant-calibration-curve` HOLDING, past review_by 2026-11-08. Default **compost**. With external n at or above the operator's stated threshold, draw the first NCI-vs-regret
- `accountant-external-cohort-nonzero` HOLDING, past review_by 2026-11-08. Default **compost**. The external cohort in the Accountant's scoreboard reads n > 0 closed outcomes (today: 10
- `tributary-answers-eval` OPEN, no review_by, added 2026-10-05. Default **compost**. Resolve Ahmed-order C4: tributaries carry a short honest answer + answer_basis inside atgT
- `accountant-real-cohort-calibration` HOLDING, no review_by, added 2026-10-06. Default **compost**. Run Accountant NCI-vs-outcome calibration on the real-tagged cohort once it has n>=30 clos
- `accountant-weekly-first-unattended` OPEN, past review_by 2026-10-25. Default **compost**. Prove the arcs-accountant-weekly scheduled task completes one run unattended.
- `receipt-real-interview-closes` HOLDING, no review_by, added 2026-10-06. Default **compost**. File real interview receipts with resolve-by dates and close them when outcomes land, buil
- `sharp-render-real-data` OPEN, no review_by, added 2026-10-06. Default **compost**. Verify the SHARP render on the first real GREEN/RED/LOCKED receipt in prod.
- `model-outcome-eval-set` OPEN, past review_by 2026-11-06. Default **compost**. Export receipt+outcome pairs from _STATE/receipt-outcomes.jsonl into a frozen eval set tha

### C08-backlog-jtbd-machinery (3)

- `gauntlet-wargame-embedding-dedup` HELD, past review_by 2026-11-08. Default **renew**. War Game / counterpart-gauntlet / FUN-HOUSE simulations are token-expensive because much o
- `choreographed-pickup` HELD, past review_by 2026-11-08. Default **renew**. Pickup orders the bench's stones by Operator 13's topological sort over depends_on/unblock
- `taxonomy-conflict-ledger-and-atlas-edges` OPEN, no review_by, added 2026-10-15. Default **compost**. Make operators 19, 20 and 21 the maintainers of one indexed, cross-referenced vocabulary i

### C09-session-handoff-memory (7)

- `session-drift-detection-eval` HELD, past review_by 2026-11-01. Default **renew**. Bigger frame (Zach, 2026-09-14): "applying ARCS first-class primitives is a big design goa
- `asm-003-cold-molt-decided` HELD, past review_by 2026-11-08. Default **renew**. Decide assumption asm-003 (a cold child's first tool call reveals a leak): classify the fi
- `memory-seven-axis-scorecard` HELD, no review_by, added 2026-10-03. Default **compost**. Stdlib script scoring ARCS memory surfaces (handoff blocks, MEMORY.md, witness stubs, Libr
- `archive-proposal-after-salvage` HOLDING, no review_by, added 2026-10-06. Default **compost**. Propose archiving the stale docs only after the salvage pass has promoted its unique items
- `salvage-pass-promote-two` OPEN, no review_by, added 2026-10-06. Default **compost**. Running chip: promote the 2 salvage items to memory/_PATTERNS and collapse the 6 exact/nea
- `context-routing-and-ask-gate` OPEN, no review_by, added 2026-10-15. Default **compost**. Route always-loaded context to the task (AGENTS.md agents/operators tables and WORLD.md on
- `pressure-rotting-loops` OPEN, no review_by, added 2026-10-16. Default **compost**. Close, compost or promote the 27 rotting items in /loops, a few per sitting

### C10-repo-integrity-ci (10)

- `prod-db-onto-prisma-migrate-deploy` OPEN, past review_by 2026-10-25. Default **compost**. Durable fix for the prod schema-drift class (option B to the 2026-09-24 batonId P0). Prod
- `adr-index-drift-repair` HELD, past review_by 2026-11-08. Default **renew**. Add the 7 ADR files missing from _DECISIONS/index.json (041, 077-081, 083) so the integrit
- `jsonl-ledgers-merge-union` HELD, past review_by 2026-11-08. Default **renew**. Add a .gitattributes merge=union rule for the append-only jsonl ledgers (legend, lore, ass
- `doc-gate-false-positive-cleanup` OPEN, no review_by, added 2026-10-06. Default **compost**. Clean the existing false positives the 4 doc gates report (e.g. _ARCHIVE/handoffs.md unmer
- `doc-gates-blocking` HOLDING, no review_by, added 2026-10-06. Default **compost**. Promote the 4 doc gates from advisory to blocking in CI.
- `merge-train-only-path` HOLDING, no review_by, added 2026-10-06. Default **compost**. Make the locked merge train the only merge path (enforce, not advise), so direct gh merges
- `prisma-8-upgrade-plan` OPEN, past review_by 2026-11-06. Default **compost**. Plan the Prisma 7 -> 8 major upgrade once 8.0 is final; do not take the RC.
- `claims-atom-seed-gate` OPEN, no review_by, added 2026-10-15. Default **compost**. Harden seeds so descendants inherit correct premises: claims as atoms (id, text, verify co
- `pressure-red-checks-main` HELD, no review_by, added 2026-10-16. Default **compost**. Triage the three known-red checks on main: twin T2 pixel match, slice S3 and S4, the stage
- `pressure-test-fixtures` HELD, no review_by, added 2026-10-16. Default **compost**. Generate the synthetic test songs from scripts/beat_truth_tracks.py inside the checks so g

### C11-model-and-spend (6)

- `embedding-storage-target-pgvector-vs-duckdb` HELD, past review_by 2026-11-08. Default **renew**. Decide the storage target for the now-live /api/embed endpoint (operators/arcs_api.py, sen
- `anthropic-spend-monitor` BLOCKED, no review_by, added 2026-10-05. Default **compost**. Stop one runaway caller from draining the shared Anthropic API budget, and see daily spend
- `old-anthropic-callers-moved` BLOCKED, no review_by, added 2026-10-06. Default **compost**. Move every remaining caller of the capped old-org Anthropic key to the new key, or delete
- `revoke-old-anthropic-keys` HOLDING, no review_by, added 2026-10-06. Default **compost**. Revoke the old-org Anthropic keys in the old org console.
- `model-provider-adapter` OPEN, past review_by 2026-11-06. Default **compost**. Make model roles provider-agnostic: role -> {provider, model}, one complete(role, request)
- `model-roles-upgrade-haiku-opus` OPEN, past review_by 2026-11-06. Default **compost**. Move fast/scorer off Haiku 4.5 to Haiku 5.5 (drops temperature 0) and max off Opus 4.7, ea

### C12-revenue-engagements (8)

- `prl-empty-email-e2e` HELD, no review_by, added 2026-08-26. Default **compost**. Final e2e proof of the v5 guard: one real empty-email chat through the Tidio widget must c
- `prl-task10-zoominfo-email` HELD, no review_by, added 2026-08-26. Default **compost**. Does ZoomInfo return business email on this plan? closes a 1.2 acceptance line
- `prl-task3-sla-zap` HELD, no review_by, added 2026-08-26. Default **compost**. Finish draft Zap 376815688 per kit build-sheet (staleness filter, email, threshold-editabl
- `prl-task4-rep-notify` HELD, no review_by, added 2026-08-26. Default **compost**. Notification email also to info@prlresins.com per kit sheet
- `prl-task7-parser-install` HELD, no review_by, added 2026-08-26. Default **compost**. Install hardened state parser (55/55 tests) into Zap 376827315 code step
- `prl-task9-unassigned-digest` HELD, no review_by, added 2026-08-26. Default **compost**. Daily 7AM unassigned-leads digest (safety net for the 12 no-rep states)
- `mcp-connector-wrapper-adr-076` HELD, past review_by 2026-11-01. Default **renew**. Build the ARCS MCP connector as a thin MCP WRAPPER over what already exists (NFTT posts +
- `demand-signal-purge-adr-076` OPEN, past review_by 2026-11-01. Default **compost**. Honor the /privacy + trust-contract retention promise: once the ADR-076 mcp-connector buil

### C13-job-search-counterparts (14)

- `req-reality-dim-board-and-champion` HELD, past review_by 2026-10-25. Default **renew**. Wire req_reality (0..3) as a GATE into the jobs board bridge rubric (scripts/jobs_score_sw
- `scan-huds-migrate-to-tokens-css` HELD, past review_by 2026-10-25. Default **renew**. Migrate _ARTIFACTS/profile-scan-hud.html and target-role-scan-hud.html off their private -
- `lens-applied-ai-engineer-pack` OPEN, no review_by, added 2026-10-14. Default **compost**. Applied-AI-engineer lens: same pack, leading with MCP server + agentic harness + build his
- `lens-deployment-strategist-pack` OPEN, no review_by, added 2026-10-14. Default **compost**. Deployment-strategist / solutions lens. Thin in fit-lens data (15 rows), 82 in bridge-scan
- `lens-embedded-product-pack` OPEN, no review_by, added 2026-10-14. Default **compost**. Embedded PM / product lens. Fit 0.741 (34 rows) but bridge-scan winnability is the worst c
- `lens-forward-deployed-pack` OPEN, no review_by, added 2026-10-14. Default **compost**. Forward-deployed lens pack: designed + ATS resume, positioning brief and per-company note
- `resume-arcs-care-role-lens-page` HELD, no review_by, added 2026-10-14. Default **compost**. Public role-lens view on resume.arcs.care (toggle: Deployment Strategist / Forward Deploye
- `role-lens-kaizen-loop` OPEN, no review_by, added 2026-10-14. Default **compost**. Close the loop: weekly re-cluster of the board by lens, and join outcomes (reply, screen,
- `role-lens-ssot-v0` OPEN, no review_by, added 2026-10-14. Default **compost**. Define the role-lens model as data: one candidate SSOT (facts, evidence grade, link) proje
- `warm-path-campaign-v0` OPEN, no review_by, added 2026-10-14. Default **compost**. The universal bottleneck is warm_path: mean about 0 in every cluster in both lenses. For t
- `profile-scan-strength-gap-card` OPEN, no review_by, added 2026-10-15. Default **compost**. Add an assumptions-first STRENGTH/GAP card to the profile scan (_ARTIFACTS/profile-scan-hu
- `cia-technical-screen-prep` OPEN, past review_by 2026-11-03. Default **compost**. Prep the CIA technical screen (former colleague of Michael): Dynamics 365 vs Salesforce no
- `agent-readable-arcs-hosts` BLOCKED, past review_by 2026-11-12. Default **compost**. Agents and AI recruiters read profiles first and guess when facts are missing: give arcs.c
- `harrison-recoil-close-score` HOLDING, past review_by 2026-11-16. Default **compost**. Score the ex-ante odds filed 2026-11-08 for the Harrison follow-up (reply in 7 days 0.70,

### C14-public-writing-canon (8)

- `moral-to-gate-alchemy-pipeline` HELD, no review_by, added 2026-09-24. Default **compost**. Build the moral-to-gate pipeline: sweep decision stories/receipts (night-moves), INDUCE th
- `nftt-story-factory-index-instructions-stale` HELD, no review_by, added 2026-09-24. Default **compost**. Fix the nftt-story-factory skill's stale index-update instructions. Step 3 says 'add a car
- `nftt-template-kintsugi-contrast-and-label-heuristics` HELD, no review_by, added 2026-09-24. Default **compost**. Fix the NFTT literary template so new posts pass the kintsugi design gate cleanly instead
- `hyperstition-pipeline-first-graduate` HELD, past review_by 2026-11-08. Default **renew**. The Hyperstition pipeline is operationalized for the first time: one candidate has walked
- `lore-tao-cross-cite` HELD, past review_by 2026-11-08. Default **renew**. Every LORE parable cites the proverb(s) distilled from it and every proverb cites its LORE
- `tao-renders-regenerated-from-projection` HELD, no review_by, added 2026-09-27. Default **compost**. Regenerate _ARTIFACTS/arcs-tao-corpus.html and arcs-tao-views.html from the projected runt
- `essay-tribes-vibes-lies` OPEN, no review_by, added 2026-10-04. Default **compost**. Ship the long-form demand essay 'Tribes, Vibes, Lies' (subtitle 'The Exoskeleton, Not the
- `nftt-monday-fde-takehome-build-log` HELD, no review_by, added 2026-10-10. Default **compost**. NFTT build log of the FDE take-home (public copy says 'a work-management platform'), T0 (b

### C15-design-system (5)

- `tokens-css-vs-ds-font-stack-drift` HELD, past review_by 2026-11-01. Default **renew**. Reconcile src/ui-kit/recoil-report/_tokens.css font stacks (GeistMono/InstrumentSans/Brico
- `state-of-union-dashboard-ahmed-impeccable-pass` HELD, past review_by 2026-11-01. Default **renew**. A "State of the Union" dashboard (reading-mode toggle: FOCUS-one-at-a-time / EXPAND-ALL se
- `lane-edge-existing-25` HOLDING, no review_by, added 2026-10-15. Default **compost**. Triage the existing pages that end short of their siblings: fix real defects, add data-mea
- `ui-kit-reconcile-legacy-tokens` HELD, no review_by, added 2026-10-15. Default **compost**. Decide whether the legacy _tokens.css values move to DESIGN.md or DESIGN.md changes; about
- `media-codex-atlas-ziggurat-seeds` HELD, no review_by, added 2026-10-16. Default **compost**. Build the media codex (runtime/specs/media-codex-spec.md): emit media-atlas.v1 from Phosph

### C16-operator-registry (5)

- `operator21-gaussian-process-posterior-then-rt-core` HELD, no review_by, added 2026-09-16. Default **compost**. OPERATOR21 (operators/arcs_operator21.py) is currently a 5-point linear interpolation betw
- `svc-sage-should-it-exist-decision` HELD, no review_by, added 2026-09-23. Default **compost**. DECISION (not a refactor): resolve whether the /svc/sage operator service should exist at
- `operator-13-choreographer-unblock` HELD, past review_by 2026-11-08. Default **renew**. Declare or remove the two undeclared imports (pandas, loguru) in operators/core/operators.
- `operator-25-first-catch` HELD, past review_by 2026-11-08. Default **renew**. Operator 25 catches one real over-momentum act before it lands (the Fun.xyz autosend class
- `rc-ops-001-graduation-ruling` HELD, no review_by, added 2026-09-27. Default **compost**. Zach rules on RC-OPS-001's four criteria from the audit + the improved detector report; cr

### C17-speculative-holds (2)

- `hypothesis-generator-plg-surface` HELD, no review_by, added 2026-09-25. Default **compost**. Spec and VALIDATE (not build) a possible 2nd ARCS PLG onramp surface, 'Hypothesis Generato
- `onchain-stakes-write-locked` HELD, no review_by, added 2026-09-26. Default **compost**. Real-money or on-chain staking (prediction-market style, e.g. Hyperliquid or similar chain
