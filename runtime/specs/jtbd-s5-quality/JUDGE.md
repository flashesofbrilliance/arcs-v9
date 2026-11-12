# JTBD s5 quality rerun judging sheet (blind)

For each item write **E** (essential: the job fails without it), **U** (useful) or **W** (wrong) after the arrow. Optionally name a missing essential piece on the `Missing:` line. Item order is random per job.

## Job 1: check if the scheduled ones are hung

1. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
2. `press_run.py`: press_run: stage the weekly go/no-go digest. Schedules the staging, never the publishing.  ->  
3. `night-moves`: Housekeeping: day's work is scattered, or a scheduled run hung or never produced a digest? End-of-day work digest. Sweeps the day's commits (all branches/wor...  ->  

Missing: 

## Job 2: check them for half-written state

1. `backlog_status_check.py`: Read-only gate over _QUEUE/induced-backlog.jsonl `state` (enum in runtime/specs/backlog-status.json).  ->  
2. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  
3. `prior-art`: The retrieval half of "capture what you learned." Lessons get written to memory,  ->  
4. `fold`: Serialize half-written state and scattered shards into clean sessions, and cut handoff landing drag. Reverse-ATG session decomposition. When a session has gr...  ->  
5. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  

Missing: 

## Job 3: molt the handoff fragments now

1. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  
2. `cold_molt_lint.py`: cold_molt_lint.py , is this chip prompt FLAWLESS (self-contained for a 100% lossless  ->  
3. `handoff_cluster.py`: handoff_cluster , deterministic domain clustering of excavated handoff units (no LLM).  ->  
4. `handoff_excavate.py`: handoff_excavate , mechanical index of every handoff block ever committed (no LLM).  ->  

Missing: 

## Job 4: I closed a bunch of stuff - check again?

1. `claim_check.py`: Governance claim-check scaffold.  ->  
2. `fork_lineage_check.sh`: Fork Lineage drift check (J17) , conditional action.  ->  
3. `tao_print_check.py`: tao_print_check.py: pre-registered kill checks for the Tao silkscreen print (K1-K4).  ->  
4. `handoff`: Runs the ARCS handoff protocol. Execute this at the END of every session before closing.  ->  
5. `loops`: Zach (2026-10-04): "my memory goes faster than my mind can index." Capture is not the gap; ARCS  ->  
6. `leak_check.sh`: scripts/leak_check.sh , External-surface leak check (J24).  ->  

Missing: 

## Job 5: measure landing drag on the last three handoffs (tokens to first useful action, re-derivation count)

1. `handoff_cluster.py`: handoff_cluster , deterministic domain clustering of excavated handoff units (no LLM).  ->  
2. `handoff_excavate.py`: handoff_excavate , mechanical index of every handoff block ever committed (no LLM).  ->  
3. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
4. `fold`: Serialize half-written state and scattered shards into clean sessions, and cut handoff landing drag. Reverse-ATG session decomposition. When a session has gr...  ->  
5. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  

Missing: 

## Job 6: pre-flight checklist of surfaces, drift, tech-debt, design-debt, blockers, P0 triage

1. `jtbd_drift_report.py`: jtbd_drift_report: weekly read-only drift report for the JTBD graph (row jtbd-graph-s5-feedback). Stdlib.  ->  
2. `reconcile_epoch.py`: reconcile_epoch: run the existing drift, stale and debt detectors once, classify every finding, rank them.  ->  
3. `design_debt_sweep.py`: design_debt_sweep.py: the design-debt burn-down for every page surfaces.arcs.care serves.  ->  

Missing: 

## Job 7: non-obvious insights / counter-intuitive signals - how to make sense of them

1. `risk_sweep.py`: risk_sweep.py - deterministic breaking / non-idempotent change sweep.  ->  
2. `hud_signal_audit.py`: hud_signal_audit.py: mechanical baseline of what the field HUD actually reads. Read-only, stdlib.  ->  
3. `idea-curator`: [CANDIDATE] Seat for the Curator (orthogonal reframe): offer ONE reframe perpendicular to the current framing. Not a keep or cut filter, not the Taxonomist.  ->  
4. `Operator 10 NoiseFilter`: Separate signal from noise (status UNBUILT)  ->  

Missing: 

## Job 8: arcs primitives and atomic elements snap together upon induced current

1. `arcs_primitives_bridge.py`: arcs_primitives_bridge.py  ->  
2. `arcs_primitives.py`: arcs_primitives.py  ->  

Missing: 

## Job 9: contour of shape of problem emerges and jobs to be done magnetically attract to the loadbearing edges of the problem space; tools snap to jobs as more current is induced; backlog prioritizes on electromagnetic principles and creates a dynamo effect

1. `jtbd_edge_weights.py`: jtbd_edge_weights: outcome-weighted (job, tool) edges for the JTBD graph (row jtbd-graph-s5-feedback). Stdlib, read-only.  ->  
2. `backlog_ripeness.py`: backlog_ripeness.py: which induced-backlog rows have RIPENED (their spark plug fired).  ->  
3. `backlog_graph.py`: backlog_graph.py: the induced backlog as a computational graph. Read-only, stdlib, no model calls.  ->  
4. `tool_catalog_emit.py`: tool_catalog_emit.py , flat tool-catalog emitter (atomic first slice, ADR-070 induction surface).  ->  
5. `universe_jtbd_adapter.py`: universe_jtbd_adapter: emit the JTBD graph's nodes (Sprint 1, backlog row jtbd-graph-s1-nodes).  ->  

Missing: 

## Job 10: vector collision engine v2 and orthogonal echo detector start firing to look out for rare earth arcs periodic elements and we ensure that our conditions are dialed in

1. `echo_ridgeline_feed.py`: echo_ridgeline_feed.py , feed ridgeline-shaped texts to the Orthogonal Echo Detector and run the  ->  
2. `echo_detector_dogfood.py`: echo_detector_dogfood.py , falsifiable seaworthiness test for the Orthogonal Echo  ->  

Missing: 

## Job 11: reverse look up index, catalog, state, memory, handoff files to date and piece together well inferred hypotheses with source quality grading and explainable provenance

1. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
2. `memory_catalog_emit.py`: memory_catalog_emit.py , the ½ punch: mechanical, declared-edges-only backfill.  ->  
3. `memory_index_sync.py`: memory_index_sync.py , self-cataloging inchworm for the memory index.  ->  
4. `prior-art`: The retrieval half of "capture what you learned." Lessons get written to memory,  ->  
5. `handoff_excavate.py`: handoff_excavate , mechanical index of every handoff block ever committed (no LLM).  ->  

Missing: 

## Job 12: sweep for seed candidates and night moves and check if any memories conflict or need to be updated

1. `night-moves`: Housekeeping: day's work is scattered, or a scheduled run hung or never produced a digest? End-of-day work digest. Sweeps the day's commits (all branches/wor...  ->  

Missing: 

## Job 13: audit priors and see if any net-new data requires changes in belief or adaptive time signature detection

1. `chief-bayesian`: [CANDIDATE] Staff of Chiefs, Bayesian: audit every prior and update for evidence.  ->  
2. `audit_report_build.py`: Build an Agent Receipts Audit report page from one audit data file.  ->  
3. `hud_signal_audit.py`: hud_signal_audit.py: mechanical baseline of what the field HUD actually reads. Read-only, stdlib.  ->  
4. `belief_log_emit.py`: belief_log_emit.py , render the consolidated ARCS belief-change log.  ->  
5. `time_machine_data.py`: time_machine_data: the numbers behind _ARTIFACTS/arcs-time-machine.html, regenerated from git (and Downloads when present).  ->  
6. `thread-recoil`: Produce a belief-update ledger (audit log) for the CURRENT thread/session , the open→close belief-diff plus, for each prior that moved, the external data tha...  ->  

Missing: 

## Job 14: run a forensic recoil report on the thread and map out the full kinematic manifold between null, om and infinite

1. `recoil-report`: Multi-agent recoil report: gather signals, analyze through ARCS operator lenses, adversarially verify every claim, synthesize a provenance-graded report  ->  
2. `gen_recoil_artifact.py`: Render an ARCS-canon Recoil Report HTML artifact from a generated report JSON.  ->  
3. `thread-recoil`: Produce a belief-update ledger (audit log) for the CURRENT thread/session , the open→close belief-diff plus, for each prior that moved, the external data tha...  ->  
4. `recoil_induce.py`: recoil_induce.py: induce candidate backlog rows from a recoil report or war room. Stdlib only, no model calls.  ->  
5. `recoil-report`: Generates an ARCS Recoil Report from a Granola call transcript, builds it into a deployed  ->  

Missing: 

## Job 15: sweep the housekeeping night-moves chore, including whether scheduled runs are hung

1. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
2. `night-moves`: Housekeeping: day's work is scattered, or a scheduled run hung or never produced a digest? End-of-day work digest. Sweeps the day's commits (all branches/wor...  ->  

Missing: 

## Job 16: check head / tail / ephemeral memory shards and cross-reference the oracle and GitHub source of truth

1. `beat_truth_tracks.py`: beat_truth_tracks.py: synthetic tracks with KNOWN tempo and downbeat for testing the page's beat detection (stdlib plus numpy).  ->  
2. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
3. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  
4. `beat_reference.py`: beat_reference.py: an independent tempo estimate (numpy only) to cross-check the page. It does NOT share code with the page:  ->  

Missing: 

## Job 17: compare cold molt against handoff pickup for efficacy and cold retrieval, evidence only (receipts or it didn't happen)

1. `cold_molt_lint.py`: cold_molt_lint.py , is this chip prompt FLAWLESS (self-contained for a 100% lossless  ->  
2. `cold-recon`: A self-contained, parameterized CLI for the ARCS **cold-reconstruction** post-mortem method:  ->  
3. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
4. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  

Missing: 

## Job 18: cross-reference surfaces.arcs.care, status.arcs.care, status.arcs.care/beliefs, arcs.care/reading-room and the docs reconciliation sync state to see which loops are open, what is drifting and where tech debt is arising

1. `open_loops.py`: open_loops.py: one front door over the stores ARCS already keeps. Read-only, no new store.  ->  
2. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  
3. `design_debt_sweep.py`: design_debt_sweep.py: the design-debt burn-down for every page surfaces.arcs.care serves.  ->  
4. `reconcile_epoch.py`: reconcile_epoch: run the existing drift, stale and debt detectors once, classify every finding, rank them.  ->  

Missing: 
