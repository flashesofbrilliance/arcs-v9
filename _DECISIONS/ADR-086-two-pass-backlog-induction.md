# ADR-086 : Two-pass backlog induction: a first-order plan graph, then a hyperstition pass that repairs its cracks

**Status:** DRAFT / PROPOSAL (2026-10-15). Not decided. Zach reviews; nothing here is wired.
**Sequence:** allocated via `python3 scripts/oracle.py next adr` -> 86 (commit `_SEEDS/_oracle.json` with this file or the number is lost).
**Prior art read:** ADR-060 (hypercube gauntlet, arc weld), ADR-068 (verb x altitude gate matrix), ADR-070 (induction surface), `runtime/specs/forge-triggers.json` v1.1, `_QUEUE/induced-backlog.jsonl`, the 2026-10-14 role-lenses note (uncommitted in the scout worktree), `operators/docs/PERIODIC-TABLE.md`.
**Companion:** `runtime/specs/effort-policy.json` (v0.1 proposal).

## Context

The backlog is a flat list of rows. Order comes from `trigger` prose ("after role-lens-ssot-v0", "after the Wonderful reply is sent"). Two consequences, both visible in the 2026-10-14 rows (`role-lens-ssot-v0`, five `lens-*` packs, `warm-path-campaign-v0`, `resume-arcs-care-role-lens-page`, `role-lens-kaizen-loop`): the dependency graph exists only in prose, so nothing can compute a critical path; and a plan composed in one pass is never attacked before it runs. ADR-068 already says a stage without a gate and a fate gates nothing. The backlog itself is a stage that prints no gate.

## Decision (proposed)

Induce a backlog plan in **two passes**, each printing an artifact through a gate to a fate (ADR-068).

### Pass 1: first-order plan, mechanical

1. **Graph.** Add two optional row fields: `depends_on: [id]` and `unblocks: [id]`. `unblocks` is derivable from `depends_on`; keep only `depends_on` as source, emit `unblocks` in the plan. Migrate prose triggers by hand, once, for open rows; a trigger that names an event ("after the Wonderful reply is sent") stays prose and becomes `gate_event`, a node the human closes.
2. **Critical path.** A script (stdlib, proposed a backlog-plan script (proposed)) topologically sorts the OPEN/READY rows, weights each node by `cost_prior` (already on rows), and prints the longest weighted path plus slack per node. No LLM. Cycles are a hard error, shown, not repaired silently (Kintsugi).
3. **Pre-mortem and post-mortem per critical-path node.** For each node on the path the plan carries two short fields written at plan time: `premortem` ("it is done and it failed: the likeliest reason") and a pre-registered `postmortem_question` ("what will we check to learn whether the estimate held"). The post-mortem is filled when the row closes, by the closer, from receipts. Pre-registered before counting, never after.
4. **Print:** a dated plan print under the backlog-plan state folder (md + json). **Gate:** acyclic, every critical node has both fields, every row's `state` is in `runtime/specs/backlog-status.json`. **Fate:** `planned` or `held`.

### Pass 2: hyperstition, adversarial, bounded

Runs on the Pass 1 plan, using the existing pipeline (HYPERSTITION PIPELINE, ROM primitive 3):

| Step | Job | Output |
|---|---|---|
| Ethereal | State the plan as the world where it already worked; list the claims that world needs | claim list |
| Loki test | Try to break each claim (adversarial, before commit; memory `loki-test-before-not-after-commit`) | cracks, each with the evidence it rests on |
| Receipt evaluation | Score claims against real receipts, the backlog's own history and the Accountant's calibration (not vibes) | held / cracked / unknown |
| ROM | Only what survives and is durable is promoted into the plan as fixed structure | plan v2 |

**Repair rows.** Each crack emits one repair row. A repair row MUST cite the crack as evidence (`evidence: [file/receipt/row id]`, mechanically checked to exist); a crack with no citable evidence is recorded as `unknown` and emits NO row (a hunch is not a crack). Repair rows enter as `state: OPEN`, `origin: hyperstition-pass`, and are never `RUNNING` without a human claim.

**Cap: one hyperstition pass per checkpoint.** A checkpoint is one of: a plan print, a critical-path node closing, or a calendar week, whichever comes first. A second pass inside the same checkpoint is refused by the script. Rationale: unbounded self-critique is the spin-cycle the Drift Sentinel exists to catch ("entropy masquerading as motion"); the cap is the stop-loss.

### Where this does NOT apply
Consent gates stay human (NOTOMATION): outreach, publishing and merges remain blocked rows no pass can unblock. Correctness gates on a row (`gates` field) are hard constraints in both passes and are never traded against cost or time. Pass 2 may add a gate; it may never remove one.

## C. Operator check-ins in lockstep (job pipeline)

Four checkpoints. At each, the named operators run and print one line into the job's ledger row. Verified 2026-10-15 against `operators/docs/PERIODIC-TABLE.md` and `operators/OPERATOR-REGISTRY.json` (generated).

| Checkpoint | Op 19 Accountant (Measure outcomes) | Op 20 Folksonomy (Discover emergent patterns) | Op 21 Librarian (Store and retrieve decisions) |
|---|---|---|---|
| **Ingest** | nothing to score yet | seed the row's features into the pattern corpus | retrieve prior decisions on this company or shape before any plan (`recommend(q, budget, stakes)`) |
| **After grade** | file the ex-ante prediction (level chosen, expected reply) | does this row sit in a known cluster or a new one? | store the grade and the level decision |
| **Before send** | confirm ex-ante receipt exists (hard gate) | flag if the shape matched an existing tool we did not use (feeds section D) | retrieve the disclosure rung and prior contact with this counterpart |
| **On outcome** | close the prediction: reply / screen / interview / offer or no-signal; update per-level calibration | re-cluster with the outcome joined | store the closed decision for the next retrieval |

Accountant discipline carries over: per-level calibration only at n >= 30 closed, else `sufficiency=insufficient` with n shown. Today the job loop has **n = 0 real-tagged outcomes** in this table, so every calibration claim is "insufficient" by construction. Say so; do not smooth it.

### Findings from verification (these are facts about the repo today)

1. **Numbering is reconciled, but the filename is a trap.** PERIODIC-TABLE: 19 Accountant, 20 Folksonomy, 21 Librarian. The registry binds 21 to `arcs_store.py` `ARCSStore.recommend` (self-test: "op21 Librarian recommend(q, budget) runs"). `operators/arcs_operator21.py` is the anterior/posterior **spline inference** module and is not the Librarian; it only shares the number in its filename (and `operator_registry_emit.py` mentions "Operator21 spline knots" as a stand-in note for the unbuilt Harmony atom). `AGENTS.md` labels `OPERATOR21` as spline inference in the Operators Library table. That row is the stale one: it names a file, not a periodic-table operator. **Proposed fix (separate small PR, not done here):** relabel the AGENTS.md row "Spline inference (file `arcs_operator21.py`; not periodic-table op 21)" so gotcha #16 and the table agree. Never rename the file; other code imports it.
2. **Self-test passes.** `operators/mcp-bridge.sh --self-test` -> `self-test: OK` (2026-10-15). Expected non-passes are reported as `blocked` by design: op9 Harmony UNBUILT, op13 BLOCKED (`pandas` undeclared), op18 Immune PARTIAL. None are in the 19/20/21 path. op19 ran with n=1 -> `sufficiency insufficient`; op20 returned a report on an under-corpus; op21 ran.
3. **No job-row adapter exists for Op 20.** `operators/prod_receipt_to_op20_seed.py` maps `Receipt` columns only (functions `adapt`, `load_rows`, `_fated_from_row`). Op 20 is gated at 100 receipts (registry note) and its `receipts_to_seeds` adapter takes receipts. Nothing maps `JobOpportunity` (title, band, dims, atsClass, companyType, hmKind, contactType) to a 54-dim seed. Same gap for Op 19: `prod_receipt_to_accountant.py` joins receipts to `Outcome`, while job outcomes live in `LaneOutcome` / `laneStage` / `laneStatus` on `JobOpportunity`. **Proposed build (not done):** a job-to-op20 seed adapter (proposed) and a LaneOutcome branch in the Accountant adapter, both read-only, faithful (unknown stays unknown; never fabricate somatic or axiom, same rule as the receipt adapter).
4. **The title-regex clustering in the 2026-10-14 role-lenses note (uncommitted in the scout worktree) is a stand-in for Op 20.** It is first-match-wins, misfiles (its own method-limits section says so), and excludes 375 unscored rows. It stays the baseline until finding 3 is built; then run both and report where they disagree (disagreement is the finding). Location note: that file and the 2026-10-14 backlog rows are uncommitted in worktree `scout-global-candidate-bundle-c430df`, not on main; this ADR cites them from there.

## D. Shape-card per job, and the magnetization-miss log

**Shape-card** (one per job, written at grade time, appended to at each checkpoint). Schema proposal: `runtime/specs/shape-card.json`.

```
verb        analyze | assess | evaluate | synthesize | recapitulate   (ADR-068)
altitude    exec | operational | surgical  (what the artifact must serve)
inputs      files / rows the job reads
output      the artifact printed
gates       blocking gates (named, from the repo's own gate list)
counterpart none | recruiter | hiring-manager | peer | unknown
tool_chosen the tool actually used (id from runtime/specs/tool-catalog.json) or "one-off"
tool_best   what /catalog would have recommended for this shape
reused      true | false
```

`scripts/tool_catalog_emit.py` already makes the catalog; the new work is one append-only log (the shape-cards log (proposed)) and a `/catalog <shape>` call at ingest whose answer is stored as `tool_best`. Mechanical: if `tool_best != tool_chosen` the card is a **miss**.

**Night-moves section: "magnetization misses"** (added to the `night-moves` skill digest, read-only, git + jsonl):
- jobs whose shape matched an existing tool that was not used (`tool_best` exists, `tool_chosen = one-off` or different);
- one-off scripts used twice (same normalized shape key, `tool_chosen = one-off`, count >= 2): candidates for `tool-forge`, per memory `lesson-banked-when-it-can-stop-you` and `jtbd-reuse-existing-tool-before-inventing`.
A miss is information, not blame. It prompts "promote or retire", never an automatic build.

## E. The alternating drive: making the Golden Inchworm move (proposal)

**Problem, measured at session start 2026-10-15.** The detectors fire; nothing contracts. Baseline: pulse flatline on commits (5 beats over a 1-beat budget), 47 seedbank-drift findings 11 days stale, 22 rotting loops, 5 days since the last night-moves digest. A detector that only extends (senses ahead) with no step that closes a finding is a worm stretched with its rear still anchored: DC, no net motion. ADR-052 already gave orphans an OPEN (orient) and CLOSE (advance) pair at session boundaries; that covers two artifacts, not the findings backlog as a whole.

**Mechanism.** The clock already exists: `scripts/pulse.py` counts beats (global_beat 37) from git timestamps. Drive it as a two-phase cycle, one phase per beat:

| Phase | Gait | Inchworm pass | Work |
|---|---|---|---|
| EXTEND beat | front reaches | Red Thread | detect, ingest, plan (Pass 1 above), surface new findings |
| CONTRACT beat | rear is pulled up | Golden Thread then Needle | give each oldest finding a FATE (owner + due beat, or compost with a supersessor), then the smallest fix that closes at least one |

Three rules make the alternation bite instead of decorate:
1. **Stretch limit (WIP cap).** First run is LOOSE (Zach, 2026-10-15): the cap is advisory, not enforcing. An EXTEND beat prints a warning, not a refusal, while open findings older than 3 beats exceed a cap. Run 14 days to record the real baseline (opened, closed, oldest age), then set the enforcing cap from the observed numbers, pre-registered before the next run. The worm cannot reach further than its body length once the cap enforces.
2. **Step size.** A CONTRACT beat must close at least 1 finding or print why none could close (a seam, not silence). One is the unit; more is allowed.
3. **Non-blocking.** Per the Inchworm primitive, a refused EXTEND never stops work on a live job; it only stops opening new findings.

**Who supplies the force.** The machine proposes the fate as ghost text (see `anticipation` in `effort-policy.json`); the human rules it (NOTOMATION). The clock supplies only the alternation.

**Measure (fixed now, before counting).** Net displacement per week = findings closed minus findings opened; stretch = age in beats of the oldest open finding; flatline = displacement 0 for longer than the pulse budget. Report n and the window.

**Honesty.** "Alternating current" names the intent. The mechanisms are the two-phase clock, the WIP cap and the step size; those are testable. **Kill:** if after the 14-day loose run net displacement is not positive, or if CONTRACT beats are routinely skipped, the drive is ceremony: keep the fate fields and drop the cycle.

**Pacing: a marathon, not a sprint (Zach, 2026-10-15).** The alternating beat is run/walk intervals, and the race has a plan: the findings-gait plan command (--days N) fixes the field (open findings) and the finish beat. Rules:
- **Even split, slow first quarter.** Target closes follow an even split of the starting field over the horizon, discounted to 60 percent in the first quarter so the loose run does not go out too fast.
- **Aid stations at 25, 50, 75 and 100 percent** are the check-in points. At each, the operators check in: Accountant (closed versus predicted, n stated), Folksonomy (what pattern do the stuck findings share), Librarian (retrieve and store the lessons). A station prints one line and may reset the plan; it never silently re-bases it (null point rule in `tenancy.null_points`).
- **The wall.** Past halfway and more than a quarter of the field behind pace raises WALL RISK. The prescribed response is a shorter stride (close small things), never a sprint.
- **Built (2026-10-15, uncommitted):** the findings-gait script with open, ingest, fate, close, plan and status, event-sourced in the findings ledger file, self-tested. Not yet wired into `pulse.py` or the session-start hook.

**Not built (superseded above for the ledger; still true for the hook wiring).** Needs a `findings` ledger that the existing detectors append to (they currently write receipts under `_INBOX/` that nothing reads), and a small extension to `pulse.py`. Neither exists today.

## Kill conditions for this ADR (pre-registered)

- If after 3 plan prints the critical path never changed an actual ordering decision, Pass 1 is ceremony: withdraw `depends_on`.
- If Pass 2 emits repair rows and fewer than 1 in 3 are later closed as useful (post-mortem field), the pass is noise: halve its cap to once per two checkpoints, then withdraw.
- If a hyperstition pass ever removes or weakens a row's `gates`, the ADR is violated: revert and file a seam.

## Alternatives rejected
- **Single-pass plan with a review step.** Review by the author anchors on the plan; the Loki step must be adversarial and evidence-citing to be worth its cost.
- **Uncapped hyperstition.** Becomes the spin cycle.
- **Weighting correctness gates against token cost.** Rejected outright: gates are constraints, cost is a tiebreaker among plans that all pass them.

## Open questions for Zach
1. Accept `depends_on` on backlog rows (needs `backlog_status_check.py` to allow the field)?
2. Checkpoint definition: week, node close, or plan print, whichever first; right?
3. Build order for finding 3: job adapter for Op 20 first, or LaneOutcome branch for the Accountant first? (Recommendation: Accountant first; it makes the effort-policy calibration real.)

## Not done in this proposal
No script written, no backlog row edited, no AGENTS.md edit, no PR, no merge. Only the three files named in the handoff below exist.
