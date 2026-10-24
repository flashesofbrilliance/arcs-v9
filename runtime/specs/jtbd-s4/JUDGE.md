# Sprint 4 judging sheet (blind)

For each item write **E** (essential: the job fails without it), **U** (useful) or **W** (wrong) after the arrow. Optionally name a missing essential piece on the `Missing:` line. Item order is random per job.

## Job 1: check if the scheduled ones are hung

1. `watchdog.sh`: scripts/watchdog.sh , Default stop-rule for any long-running task (J21).  ->  
2. `leak_check.sh`: scripts/leak_check.sh , External-surface leak check (J24).  ->  
3. `claim_check.py`: Governance claim-check scaffold.  ->  
4. `canon-review`: description: Batch-review the canon-propagation queue , quick yes/no multi-picker over DEROT / ESCALATE / FORK items, then apply the yes'd ones  ->  
5. `press_run.py`: press_run: stage the weekly go/no-go digest. Schedules the staging, never the publishing.  ->  
6. `tao_print_check.py`: tao_print_check.py: pre-registered kill checks for the Tao silkscreen print (K1-K4).  ->  

Missing: 

## Job 2: check them for half-written state

1. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  
2. `echo-scan`: Turn an outside field of research (a paper, a viral post, a screenshot, a domain name like "stopped light" or "mycorrhizal networks") into ARCS design rules...  ->  
3. `prior-art`: The retrieval half of "capture what you learned." Lessons get written to memory,  ->  
4. `fold`: Serialize half-written state and scattered shards into clean sessions, and cut handoff landing drag. Reverse-ATG session decomposition. When a session has gr...  ->  
5. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  

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

1. `reconcile_epoch.py`: reconcile_epoch: run the existing drift, stale and debt detectors once, classify every finding, rank them.  ->  
2. `design_debt_sweep.py`: design_debt_sweep.py: the design-debt burn-down for every page surfaces.arcs.care serves.  ->  

Missing: 

## Job 7: non-obvious insights / counter-intuitive signals - how to make sense of them

1. `hud_signal_audit.py`: hud_signal_audit.py: mechanical baseline of what the field HUD actually reads. Read-only, stdlib.  ->  
2. `risk_sweep.py`: risk_sweep.py - deterministic breaking / non-idempotent change sweep.  ->  
3. `Operator 10 NoiseFilter`: Separate signal from noise (status UNBUILT)  ->  

Missing: 

## Job 8: arcs primitives and atomic elements snap together upon induced current

1. `arcs_primitives.py`: arcs_primitives.py  ->  

Missing: 

## Job 9: contour of shape of problem emerges and jobs to be done magnetically attract to the loadbearing edges of the problem space; tools snap to jobs as more current is induced; backlog prioritizes on electromagnetic principles and creates a dynamo effect

1. `backlog_freshness.py`: backlog_freshness.py: list induced-backlog rows past their review_by date.  ->  
2. `night-moves`: End-of-day work digest. Sweeps the day's commits (all branches/worktrees), net-new tools, ADRs/DEWY receipts, and memory writes, then synthesizes a five-part...  ->  
3. `backlog_ripeness.py`: backlog_ripeness.py: which induced-backlog rows have RIPENED (their spark plug fired).  ->  
4. `backlog_graph.py`: backlog_graph.py: the induced backlog as a computational graph. Read-only, stdlib, no model calls.  ->  
5. `backlog_status_check.py`: Read-only gate over _QUEUE/induced-backlog.jsonl `state` (enum in runtime/specs/backlog-status.json).  ->  
6. `jtbd_graph_edges.py`: jtbd_graph_edges: Sprint 2 edges for the JTBD graph (backlog row jtbd-graph-s2-edges).  ->  

Missing: 

## Job 10: vector collision engine v2 and orthogonal echo detector start firing to look out for rare earth arcs periodic elements and we ensure that our conditions are dialed in

1. `echo_ridgeline_feed.py`: echo_ridgeline_feed.py , feed ridgeline-shaped texts to the Orthogonal Echo Detector and run the  ->  
2. `echo_detector_dogfood.py`: echo_detector_dogfood.py , falsifiable seaworthiness test for the Orthogonal Echo  ->  

Missing: 

## Job 11: reverse look up index, catalog, state, memory, handoff files to date and piece together well inferred hypotheses with source quality grading and explainable provenance

1. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
2. `memory_index_sync.py`: memory_index_sync.py , self-cataloging inchworm for the memory index.  ->  
3. `recoil-report`: Multi-agent recoil report: gather signals, analyze through ARCS operator lenses, adversarially verify every claim, synthesize a provenance-graded report  ->  
4. `handoff_excavate.py`: handoff_excavate , mechanical index of every handoff block ever committed (no LLM).  ->  
5. `memory_catalog_emit.py`: memory_catalog_emit.py , the ½ punch: mechanical, declared-edges-only backfill.  ->  

Missing: 

## Job 12: sweep for seed candidates and night moves and check if any memories conflict or need to be updated

1. `night-moves`: End-of-day work digest. Sweeps the day's commits (all branches/worktrees), net-new tools, ADRs/DEWY receipts, and memory writes, then synthesizes a five-part...  ->  
2. `universe_sweep.py`: universe_sweep: night-moves contamination sweep over every registered universe.  ->  
3. `night_moves_gather.sh`: night_moves_gather.sh , deterministic raw material for the /night-moves digest.  ->  
4. `seedbank_drift_check.py`: seedbank_drift_check , an inchworm drift detector for the _SEEDS bank.  ->  

Missing: 

## Job 13: audit priors and see if any net-new data requires changes in belief or adaptive time signature detection

1. `belief_log_emit.py`: belief_log_emit.py , render the consolidated ARCS belief-change log.  ->  
2. `hud_signal_audit.py`: hud_signal_audit.py: mechanical baseline of what the field HUD actually reads. Read-only, stdlib.  ->  
3. `thread-recoil`: Produce a belief-update ledger (audit log) for the CURRENT thread/session , the open→close belief-diff plus, for each prior that moved, the external data tha...  ->  
4. `time_machine_data.py`: time_machine_data: the numbers behind _ARTIFACTS/arcs-time-machine.html, regenerated from git (and Downloads when present).  ->  

Missing: 

## Job 14: run a forensic recoil report on the thread and map out the full kinematic manifold between null, om and infinite

1. `recoil-report`: Multi-agent recoil report: gather signals, analyze through ARCS operator lenses, adversarially verify every claim, synthesize a provenance-graded report  ->  
2. `gen_recoil_artifact.py`: Render an ARCS-canon Recoil Report HTML artifact from a generated report JSON.  ->  
3. `thread-recoil`: Produce a belief-update ledger (audit log) for the CURRENT thread/session , the open→close belief-diff plus, for each prior that moved, the external data tha...  ->  
4. `page_gate.py`: page_gate.py: one gate for any standalone HTML page (public/, _ARTIFACTS/, _PROPOSALS/).  ->  
5. `recoil-report`: Generates an ARCS Recoil Report from a Granola call transcript, builds it into a deployed  ->  

Missing: 

## Job 15: sweep the housekeeping night-moves chore, including whether scheduled runs are hung

1. `night_moves_gather.sh`: night_moves_gather.sh , deterministic raw material for the /night-moves digest.  ->  
2. `night-moves`: End-of-day work digest. Sweeps the day's commits (all branches/worktrees), net-new tools, ADRs/DEWY receipts, and memory writes, then synthesizes a five-part...  ->  
3. `catalog`: Given a stated job, recommend THE one right existing tool and (with consent) run it.  ->  
4. `universe_sweep.py`: universe_sweep: night-moves contamination sweep over every registered universe.  ->  

Missing: 

## Job 16: check head / tail / ephemeral memory shards and cross-reference the oracle and GitHub source of truth

1. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  
2. `beat_truth_tracks.py`: beat_truth_tracks.py: synthetic tracks with KNOWN tempo and downbeat for testing the page's beat detection (stdlib plus numpy).  ->  
3. `beat_reference.py`: beat_reference.py: an independent tempo estimate (numpy only) to cross-check the page. It does NOT share code with the page:  ->  

Missing: 

## Job 17: compare cold molt against handoff pickup for efficacy and cold retrieval, evidence only (receipts or it didn't happen)

1. `handoff_fold.py`: handoff_fold: cold-molt half-written handoff shards into ONE arc a cold session resumes from fast (cuts landing drag). ADR-085 (d).  ->  
2. `cold_molt_lint.py`: cold_molt_lint.py , is this chip prompt FLAWLESS (self-contained for a 100% lossless  ->  
3. `handoff-pickup`: Runs at the START of a new session to orient quickly without re-reading everything.  ->  
4. `unfold.py`: unfold.py , the pickup-side atomizer. The fold sweeps residue OUT at close; the unfold sweeps  ->  

Missing: 

## Job 18: cross-reference surfaces.arcs.care, status.arcs.care, status.arcs.care/beliefs, arcs.care/reading-room and the docs reconciliation sync state to see which loops are open, what is drifting and where tech debt is arising

1. `state_sync_check.py`: State-sync drift check , advisory only, never fails the build.  ->  
2. `belief_log_emit.py`: belief_log_emit.py , render the consolidated ARCS belief-change log.  ->  
3. `reconcile_epoch.py`: reconcile_epoch: run the existing drift, stale and debt detectors once, classify every finding, rank them.  ->  
4. `seedbank_drift_check.py`: seedbank_drift_check , an inchworm drift detector for the _SEEDS bank.  ->  
5. `design_debt_sweep.py`: design_debt_sweep.py: the design-debt burn-down for every page surfaces.arcs.care serves.  ->  
6. `open_loops.py`: open_loops.py: one front door over the stores ARCS already keeps. Read-only, no new store.  ->  

Missing: 
