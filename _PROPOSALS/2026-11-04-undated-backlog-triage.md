# Undated backlog triage, 2026-11-04

**Ruling (Zach, 2026-11-04): apply as written**, with one change: `autopilot-arcs-care-battle-card-ammo` is HELD, not composted, while Zach checks with Joe Schriner whether Autopilot is still hiring. The open questions below were settled by the proposal's defaults: Phosphor rows get a date only (the three HOLDING ones stay HOLDING), `req-reality-dim-board-and-champion` is held, `accountant-external-cohort-nonzero` is kept. Final counts: Keep 8, Hold 44, Compost 5, Date only 12, Leave 26. Rows that changed state open their `status_note` with the new state and date; the old note follows intact after `|| prior:`.

**Scope.** Live rows (OPEN, READY, HOLDING, HELD, BLOCKED, RUNNING) in `_QUEUE/induced-backlog.jsonl` with no `added` field, on branch `claude/status-reconcile-2026-11-04` at `f70c2226`: **95 rows** (37 OPEN, 35 HELD, 19 HOLDING, 3 READY, 1 RUNNING, 0 BLOCKED).

**Test used.** Does the row serve `five-person-outcome-test` (five outside people, real decisions, closed outcomes; F43 reads 0 outside outcomes in prod)? Until that test reads: no new scripts, agents, skills or gates. Phosphor stays HELD as Zach parked it. MyAlly, CIA and Dioptra rows are not in this set (they already carry dates).

**Dates.** Every `added` value is the date of the first commit that adds `"id": "<id>"` to the backlog (`git log --reverse -S`). All 95 matched exactly, none needed the looser fallback. 15 rows share `eb12ec08` (2026-09-27), a bulk induction commit, so their date is the induction date, not the date the idea came up.

**How it applies.** Keep: add `added`, and append a dated line to `status_note`. Hold: state to HELD, append `2026-11-04: HELD, resume <trigger>`. Compost: state to COMPOSTED, append `2026-11-04: COMPOSTED. Learning: ...`. Nothing is deleted and no old note is rewritten. Every row in this set gets an `added` date, including the Phosphor rows (a date only, no state change), unless Zach says to leave them fully untouched.

| fate | rows |
|---|---|
| Keep | 8 |
| Hold (to HELD) | 44 |
| Compost | 5 |
| Date only (already HELD with a trigger) | 12 |
| Leave (Phosphor) | 26 |

## Questions for Zach

1. **Phosphor: date only, or fully untouched?** Three Phosphor rows are HOLDING, not HELD (`phosphor-heading-light-rays`, `phosphor-optical-sensor-controller`, `phosphor-pad-mute-choke`). Move them to HELD to match the others?
2. **`req-reality-dim-board-and-champion`:** you promoted it to READY on 2026-10-18. It wires a gate into the jobs scripts, so the freeze says hold. Hold, or exempt it because the job search is live?
3. **`accountant-external-cohort-nonzero`:** same target as the five-person test. Keep and link, or mark it SUPERSEDED by that row?
4. **The six composts**: say which you'd rather hold.

## Keep (8)

| id | state now | proposed | added (git) | reason |
|---|---|---|---|---|
| `accountant-calibration-curve` | HOLDING | HOLDING | 2026-09-27 | Downstream read of the test's outcomes; stays HOLDING on its dependency. |
| `accountant-external-cohort-nonzero` | HOLDING | HOLDING | 2026-09-27 | Same target as the five-person test (external closed outcomes > 0); link it to that row. |
| `agent-readable-arcs-hosts` | RUNNING | RUNNING | 2026-10-30 | RUNNING and nearly done (PR merged); close the last check rather than park it. |
| `agent-receipts-audit-first-conversion` | HOLDING | HOLDING | 2026-09-27 | An outside paid audit with an ex-ante receipt is an outside outcome. |
| `echo-scheduled-receipts` | OPEN | OPEN | 2026-10-03 | The recall_at debrief nudge is how outside decisions get closed; product feature, not internal tooling. |
| `pressure-rotting-loops` | OPEN | OPEN | 2026-10-16 | This triage is a pass of it; cleanup, not new tooling. |
| `prod-db-onto-prisma-migrate-deploy` | OPEN | OPEN | 2026-09-24 | Outside users write to prod; schema drift there would lose their receipts. |
| `universe-outcome-capture` | READY | READY | 2026-10-17 | Raises the closed-outcome rate the test depends on. |

## Hold (44)

| id | state now | proposed | added (git) | reason |
|---|---|---|---|---|
| `adr-index-drift-repair` | HOLDING | HELD | 2026-09-27 | Doc hygiene; the 7 ADRs are still missing from the index (checked today). Resume after five-person-outcome-test reads. |
| `algorethics-in-scope-benchmark` | OPEN | HELD | 2026-09-15 | New benchmark build. Resume after five-person-outcome-test reads. |
| `asm-003-cold-molt-decided` | HOLDING | HELD | 2026-09-27 | Harness assumption test. Resume after five-person-outcome-test reads. |
| `asm-009-net-direction-decided` | OPEN | HELD | 2026-09-27 | Harness assumption test. Resume after five-person-outcome-test reads. |
| `autopilot-arcs-care-battle-card-ammo` | OPEN | HELD | 2026-09-17 | Ruled HELD (Zach): theoretically still live; held while Zach checks with Joe. Resume on a yes; compost on a no or no reply. |
| `case-squads-multiplayer` | OPEN | HELD | 2026-09-26 | Multiplayer needs single-player outside outcomes first. Resume after five-person-outcome-test reads with at least one closed outcome. |
| `choreographed-pickup` | HOLDING | HELD | 2026-09-27 | Pickup tooling. Resume after five-person-outcome-test reads. |
| `compass-model-agnostic-provider-abstraction` | OPEN | HELD | 2026-09-16 | Refactor; no outside user needs it yet. Resume after five-person-outcome-test reads or if a second provider is needed. |
| `conviction-chips-calibration` | OPEN | HELD | 2026-09-26 | Prototyped; staking needs closed outcomes to calibrate against. Resume after five-person-outcome-test reads. |
| `design-system-trueup-claude-design-magic-patterns` | OPEN | HELD | 2026-10-16 | Design true-up; needs a new dependency and an MCP not connected. Resume after five-person-outcome-test reads. |
| `embedding-storage-target-pgvector-vs-duckdb` | OPEN | HELD | 2026-09-16 | Storage decision with no caller yet. Resume after five-person-outcome-test reads. |
| `gauntlet-wargame-embedding-dedup` | OPEN | HELD | 2026-09-16 | Token-cost tooling. Resume after five-person-outcome-test reads. |
| `greenhouse-arcs-care-seedbank-surface` | OPEN | HELD | 2026-09-13 | New internal surface. Resume after five-person-outcome-test reads. |
| `harness-config-ssot` | OPEN | HELD | 2026-10-30 | Harness tooling. Resume after five-person-outcome-test reads. |
| `hud-evidence-grain-d4` | HOLDING | HELD | 2026-10-19 | HUD phase 3. Resume after five-person-outcome-test reads. |
| `hyperstition-pipeline-first-graduate` | HOLDING | HELD | 2026-09-27 | Canon pipeline. Resume after five-person-outcome-test reads. |
| `hypothesis-generator-plg-surface` | OPEN | HELD | 2026-09-25 | Second onramp spec; the first has no outside outcomes yet. Resume after five-person-outcome-test reads. |
| `identity-arcs-care-attraction-rules-parked` | HOLDING | HELD | 2026-10-19 | Zach parked it 2026-10-19 (tower D1); HOLDING to HELD makes that explicit. Resume on Zach's call. |
| `jsonl-ledgers-merge-union` | HOLDING | HELD | 2026-09-27 | Still absent (.gitattributes has no rule, checked today). Config, cheap, but not on the test's path. Resume after five-person-outcome-test reads or on the next ledger merge conflict. |
| `lore-tao-cross-cite` | HOLDING | HELD | 2026-09-27 | New check. Resume after five-person-outcome-test reads. |
| `mcp-connector-wrapper-adr-076` | OPEN | HELD | 2026-09-13 | New connector build. Resume after five-person-outcome-test reads. |
| `media-codex-atlas-ziggurat-seeds` | OPEN | HELD | 2026-10-16 | Emits from Phosphor, which is parked. Resume when Phosphor resumes. |
| `memory-seven-axis-scorecard` | OPEN | HELD | 2026-10-03 | New script. Resume after five-person-outcome-test reads. |
| `moral-to-gate-alchemy-pipeline` | OPEN | HELD | 2026-09-24 | Gate-making pipeline. Resume after five-person-outcome-test reads. |
| `nftt-monday-fde-takehome-build-log` | OPEN | HELD | 2026-10-10 | monday rejected 2026-11-02; a build-log post is content, not tooling. Resume if Zach wants the post (postmortem in _STATE/job-search/postmortem-monday.md). |
| `nftt-story-factory-index-instructions-stale` | OPEN | HELD | 2026-09-24 | Skill fix, needed only when the next NFTT post is written. Resume at the next NFTT post. |
| `nftt-template-kintsugi-contrast-and-label-heuristics` | OPEN | HELD | 2026-09-24 | Template fix, needed only for the next post. Resume at the next NFTT post. |
| `operator-13-choreographer-unblock` | HOLDING | HELD | 2026-09-27 | Dependency decision for pickup tooling. Resume after five-person-outcome-test reads. |
| `operator-25-first-catch` | HOLDING | HELD | 2026-09-27 | Operator graduation. Resume after five-person-outcome-test reads. |
| `operator21-gaussian-process-posterior-then-rt-core` | OPEN | HELD | 2026-09-16 | Operator math upgrade. Resume after five-person-outcome-test reads. |
| `pressure-red-checks-main` | OPEN | HELD | 2026-10-16 | The red checks named (twin T2, slice S3/S4, stage F-key) are Phosphor suite checks; no failed main runs on GitHub today. Resume when Phosphor resumes. |
| `pressure-test-fixtures` | OPEN | HELD | 2026-10-16 | Phosphor check fixtures. Resume when Phosphor resumes. |
| `prl-golive-empty-email-guard` | OPEN | HELD | 2026-10-09 | PRL is paused (Zach 2026-09-26). Resume with prl-phase-path-close, like the other PRL rows. |
| `rc-ops-001-graduation-ruling` | HOLDING | HELD | 2026-09-27 | Canon ruling. Resume after five-person-outcome-test reads. |
| `req-reality-dim-board-and-champion` | READY | HELD | 2026-09-11 | READY since 2026-10-18, but it wires a new gate into the jobs scoring scripts. Resume after five-person-outcome-test reads, or earlier on Zach's go since the job search is live. |
| `rfp-engine-public-good` | OPEN | HELD | 2026-10-30 | Page built on claude/good-rfp-engine; deploy waits on the rights check and real-model checks. Resume when the rights check clears. |
| `scan-huds-migrate-to-tokens-css` | OPEN | HELD | 2026-09-11 | One internal HUD left on private tokens. Resume after five-person-outcome-test reads. |
| `session-drift-detection-eval` | OPEN | HELD | 2026-09-14 | Harness eval. Resume after five-person-outcome-test reads. |
| `state-of-union-dashboard-ahmed-impeccable-pass` | OPEN | HELD | 2026-09-14 | Internal dashboard. Resume after five-person-outcome-test reads. |
| `svc-sage-should-it-exist-decision` | OPEN | HELD | 2026-09-23 | Waits on the calibration curve, which waits on outside outcomes. Resume when accountant-calibration-curve is DONE. |
| `tao-renders-regenerated-from-projection` | READY | HELD | 2026-09-27 | READY, but it regenerates internal canon renders. Resume after five-person-outcome-test reads. |
| `tokens-css-vs-ds-font-stack-drift` | OPEN | HELD | 2026-09-11 | Design token drift. Resume after five-person-outcome-test reads. |
| `universe-breakoff-conductor-gate` | HOLDING | HELD | 2026-10-17 | Repo decomposition tooling. Resume after five-person-outcome-test reads. |
| `universe-scenario-anonymizer` | OPEN | HELD | 2026-10-17 | Needs a shared pool, which needs outside outcomes. Resume after five-person-outcome-test reads with closed outcomes to anonymize. |

## Compost (5)

| id | state now | proposed | added (git) | reason |
|---|---|---|---|---|
| `arcs-olympics-first-games` | HOLDING | COMPOSTED | 2026-09-27 | Ceremony two dependencies deep on an ungraduated pipeline. Learning: the graduation gate may want a ritual; revisit if a hyperstition candidate ever graduates. |
| `freshness-zeno-ceiling` | OPEN | COMPOSTED | 2026-10-03 | Refinement to an ADR candidate that has not been adopted. Learning: re-check pacing needs an upper bound; fold it in if the defeasible-freshness ADR is ever accepted. |
| `jobs-arcs-care-recruiter-workflow-fork` | OPEN | COMPOSTED | 2026-09-17 | Same Joe channel as Autopilot, no live lead. Learning: the swipe board forks cleanly to a recruiter flow; a beat-map is enough when a recruiter asks. |
| `lore-franchise-ephemera-surface` | OPEN | COMPOSTED | 2026-09-26 | Game layer spec with no user. Learning: WORLD.md already reads as a game bible; that is the asset, not a new surface. |
| `pond-etch-protocol-serialize-molt-test` | OPEN | COMPOSTED | 2026-09-25 | Theory test of accretion as an attractor; no consumer. Learning: write-drunk / edit-sober is the claim; test it only if molts start losing invariants. |

## Date only (12)

| id | state now | proposed | added (git) | reason |
|---|---|---|---|---|
| `onchain-receipt-anchor-registry` | HELD | HELD | 2026-11-02 | Already HELD 2026-11-02 with a resume trigger (Farcaster wallet track). |
| `onchain-stakes-write-locked` | HELD | HELD | 2026-09-26 | Already HELD and write-locked (real money is a one-way door); append the trigger: resume only on Zach's write-lock declaration. |
| `op20-somatic-axiom-real-signal-source` | HELD | HELD | 2026-08-28 | Already HELD; blocked on an upstream signal source. |
| `prl-empty-email-e2e` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `prl-phase-path-close` | HELD | HELD | 2026-09-26 | Already HELD (PRL paused 2026-09-26, resume on Zach's signal). |
| `prl-task10-zoominfo-email` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `prl-task3-sla-zap` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `prl-task4-rep-notify` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `prl-task7-parser-install` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `prl-task9-unassigned-digest` | HELD | HELD | 2026-08-26 | Already HELD, resumes with prl-phase-path-close. |
| `recoil-kit-onto-design-md` | HELD | HELD | 2026-10-19 | Already HELD. |
| `tap-pin-portable-seed-key` | HELD | HELD | 2026-11-03 | Already HELD 2026-11-03. |

## Leave (26)

| id | state now | proposed | added (git) | reason |
|---|---|---|---|---|
| `phosphor-acoustic-sync-test` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-aesthetic-constitution` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-beam-controller` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-consonance-shavasana` | HELD | HELD | 2026-10-17 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-controller-zoo` | HELD | HELD | 2026-10-17 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-deck-dj-core` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-freeze-dance-coop` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-genre-kits` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-heading-light-rays` | HOLDING | HOLDING | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. Note: this one is HOLDING, not HELD. |
| `phosphor-light-controls` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-numpad-finger-drum-map` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-optical-sensor-controller` | HOLDING | HOLDING | 2026-10-17 | Phosphor, parked by Zach 2026-11-04; untouched. Note: this one is HOLDING, not HELD. |
| `phosphor-pad-mute-choke` | HOLDING | HOLDING | 2026-10-18 | Phosphor, parked by Zach 2026-11-04; untouched. Note: this one is HOLDING, not HELD. |
| `phosphor-parent-kid-access` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-platter-speed` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-player-dock-states` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-player-waveform-hotcuts` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-rc1-firefox-verify` | HELD | HELD | 2026-10-18 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-remote-pads` | HELD | HELD | 2026-10-17 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-render-surface` | HELD | HELD | 2026-10-18 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-simulated-user-pretest` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-slip-sync` | HELD | HELD | 2026-10-15 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-tempo-detector-v2` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-tempo-map-slice3` | HELD | HELD | 2026-10-17 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-virtual-pad-mapping` | HELD | HELD | 2026-10-16 | Phosphor, parked by Zach 2026-11-04; untouched. |
| `phosphor-webkit-eject-lock` | HELD | HELD | 2026-10-18 | Phosphor, parked by Zach 2026-11-04; untouched. |
