---
title: Backlog graph prior art (is the induced backlog novel?)
date: 2026-11-05
status: PROPOSED
question: Is a good part of the backlog graph built 2026-10-28 to 11-03 novel compared with how agent harnesses track work, and is any of it worth open sourcing?
method: features inventoried from code; one platform-standards-auditor pass (17 tool calls, docs fetched); 21 web searches and 4 page fetches by this session; one claims-skeptic round, whose downgrades are applied below
verdict: hunch not borne out; no feature survived with "no prior art found"
artifact: https://claude.ai/artifact/3ctxSCzCMsS6izUJzbMXsh
---

# Backlog graph prior art

**Short answer: no. Every mechanism in the backlog graph has prior art, and so does the way they fit together.**
The tracker (rows in git, a dependency graph, a ready list, claims, merge-safe ids) is what
[Beads](https://github.com/steveyegge/beads) and [Taskmaster](https://github.com/eyaltoledano/claude-task-master) do, and
GitHub ships [issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
natively. The layer on top (a trigger, a resolved tool, a door that calls for a human, a backout plan, a receipt that names the
work item) is an ITSM change record: ServiceNow requires an
[implementation plan, backout plan and risk assessment before CAB approval](https://www.servicenow.com/community/itsm-forum/change-management-in-servicenow-everything-you-need-to-know/m-p/3439058)
and reviews the change against them afterwards. What ARCS has is that change-record discipline **applied to an agent's own
backlog, in plain files, gated in pre-commit**. That is a fair thing to say. "A novel way to track agent work" is not.

My first draft graded two pieces "no prior art found" (the readiness card's evidence labels and the receipt-to-row join).
The skeptic round knocked both down with concrete systems (GSN assurance cases, verification matrices, SLSA, Jira deployments,
SOX change audits). It also found three places where the draft overstated what our own code does. Both are corrected below.

## How hard I looked

- Code read: `_QUEUE/induced-backlog.jsonl` (460 rows), `runtime/specs/backlog-status.json`, `scripts/backlog_status_check.py`,
  `backlog_graph.py`, `backlog_ripeness.py`, `readiness_packet.py`, `backlog_append.py`, `backlog_merge_by_id.py`,
  `universe_jtbd_adapter.py`, `jtbd_graph_gates.py`, `fates.py`, `open_loops.py`, `backlog_issue_sync.py`, `receipt_coverage.py`,
  the `/backlog-graph` command, and the [glass box explainer](https://claude.ai/artifact/QzRVPjLP4MdhZHzZuqL1jN).
- Native platforms (GitHub, Claude Code, Codex, Linear, git): one `platform-standards-auditor` pass with fetched docs.
- Agent trackers and adjacent fields: 21 searches and 4 fetches by this session. The skeptic added ITSM, assurance cases,
  supply-chain provenance and intelligence tradecraft from its own knowledge; I then searched for a citable URL for each.
- Not searched: Devin, OpenHands and SWE-agent internals (none publishes a persistent cross-session work tracker that I know
  of), academic work beyond two arXiv hits, Jira and Linear marketplaces beyond one app.

## Live numbers (2026-11-05, main at `fc07c1e5`)

| Measure | Value | Source |
|---|---|---|
| Rows | 460 (288 active) | `backlog_graph.py` |
| Ready now | 15, computed **without** `--gh`, so PR triggers were not checked | `backlog_graph.py` |
| Active rows whose named tool resolves (HAVE) | 116; 147 NOT-RESOLVED | `backlog_graph.py` |
| Rows with a `door` field | 105 of 460 (13 one-way) | row scan |
| Active rows with a `ruin` rating | 99 of 288 | `backlog_graph.py --lens risk` |
| Job and tool gate | PASS with 0 new and **506 held** in the baseline (352 orphan-tool, 151 orphan-job, 1 blocker, 2 probes); the 2026-11-03 pulse read 552 | `universe_jtbd_adapter.py --check`, run 2026-11-05 |
| Receipts since 2026-10-20 with both `job_id` and `tool_id` | 295 of 323 (91%) | SELECT on `public.decision_receipt` |
| Of the distinct `job_id` values on those receipts | 152 distinct; 86 are `job:backlog:*`; **80 of the 86 match a row in the file** (6 do not) | SELECT plus a scan of the file |

The receipt number measures filled-in fields, not resolved links: the CHECK constraint only requires the form
`job:<source>:<key>`, and two thirds of the job ids point at PRs, sessions or requests rather than backlog rows.

## Corrections to what the draft said our code does

1. **Ripeness does not only detect.** `backlog_ripeness.py --apply-closes` rewrites SECRETLY-DONE rows.
2. **A one-way door routes a person only on the assembly line.** `readiness_packet.py` prints "suggested tier 4 (a cue, not a
   rule)" and runs only when called. `scripts/line_triage.py` does send one-way rows to R3 (the parent drafts a decision card),
   so the skeptic's "does not route a human" was too strong. But `/backlog-graph` still lists
   `agent-receipts-audit-first-conversion` (one-way, abort plan still DRAFT) first under ready now, and its nudge points there.
   (Kintsugi seam: this item was itself overstated in the corrections list and is fixed here.)
3. **The state gate is narrower than "pre-commit and CI."** The hook runs only when the hooks path is set and the backlog files are
   staged; the CI step runs on pushes to main, and Actions are off. A stale claim is a warning, not a failure, unless `--strict`.
4. **Backlog fates are not enforced.** `fates.py` treats the backlog as a soft class (reported, never blocking) and is not wired to
   backlog edits.

## Per-feature grades (after the skeptic round)

**EXISTS** = the same mechanism ships elsewhere. **PARTIAL** = a relative covers most of it; the missing part is named.

| # | Feature | Closest prior art | Grade | What is ours, if anything |
|---|---|---|---|---|
| F1 | Row schema: `id`, `jtbd`, `route {session, tool, model}`, `gates`, `trigger`, `fates`, `depends_on`/`unblocks`, `cost_prior`, `ruin`, `door` | Beads issues; Taskmaster tasks (dependencies, priority, test strategy); [Backlog.md](https://github.com/MrLesk/Backlog.md) acceptance criteria; GitHub Projects [custom fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields) | PARTIAL | A typed `route` naming the session, tool and model for the work. |
| F2 | 9-state enum incl. COMPOSTED and SUPERSEDED; RUNNING needs `claimed_by` + `claimed_at`; stale claims and note-vs-state contradictions flagged | Beads atomic claim ("sets assignee + in_progress") and `supersedes` links; Taskmaster deferred and cancelled; Jira workflow validators that require fields on a transition; Claude Code [task tools](https://code.claude.com/docs/en/tools-reference) with `TaskCompleted` [hooks](https://code.claude.com/docs/en/hooks) | EXISTS | The gate runs on a file in git rather than in a tracker's UI. |
| F3 | Dependency graph, longest-path waves, ready now, biggest unblockers, cycle and dangling findings | Beads `bd ready` ("tasks with no open blockers"); Taskmaster `next`; GitHub issue dependencies | EXISTS | Waves and unblocker ranking are small extensions. |
| F4 | Ripeness: prose triggers parsed into checks ("PR #N merges", "after <date>", "ADR-N accepted"); SECRETLY-DONE | GitHub [closing keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) and Projects [PR-merged automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations); expiring TODOs ([todo-or-die-python](https://pypi.org/project/todo-or-die-python/), [todo_lint](https://rubygems.org/gems/todo_lint)); [Arnica snooze](https://www.arnica.io/announcement/new-feature-announcement-snooze---unblock-critical-pr-merges-without-losing-track-of-risk) | PARTIAL | One grammar over several event kinds. Each kind exists alone. |
| F5 | Tool fit: each row's `route.tool` resolved against repo files and the tool catalog | [agentskills required-tools proposal](https://github.com/agentskills/agentskills/discussions/392); [preflight tool detection](https://understandingdata.com/posts/agentic-tool-detection/); [Mem²Evolve](https://arxiv.org/pdf/2604.10923) gap detection; CMDB checks that a named configuration item exists | PARTIAL | Checking a persistent work item against the repo before it is picked. Today 147 of 288 active rows do not resolve. |
| F6 | Job and tool graph gates (ORPHAN-TOOL, ORPHAN-JOB, DEP-CYCLE, DEAD-FILE-REF, RUNTIME-DEP-NO-PROBE, BLOCKER-NO-RESOLVE-BY) with a shrink-only baseline | Ratchets: [imbue-ai/ratchets](https://docs.rs/crate/ratchets/latest/source/DESIGN.md), [pest-ratchets](https://packagist.org/packages/offset-smoker/pest-ratchets); orphans: Backstage [isOrphan](https://backstage.io/docs/reference/plugin-catalog.isorphan); JTBD orphan checks in the [TBD plugin](https://claudepluginhub.com/plugins/lagz0ne-tbd-skill) | PARTIAL | The rules applied to a graph of jobs and tools. Each rule is standard, and 506 known violations are held. |
| F7 | `door`, `abort`, `rollback` on the row; readiness card labels each line MEASURED, DECLARED, CUE or UNCONFIRMED | [agentops one-way-door skill](https://www.skills.sh/boshu2/agentops/one-way-door); [Revoco](https://github.com/rsh1k/revoco) rollback-before-act; [GSN assurance cases](https://scsc.uk/gsn-standard) (claims tied to evidence, undeveloped claims marked); NASA and DoD verification matrices (each requirement tagged by how it was verified, or open); [SLSA provenance](https://slsa.dev/provenance/v1) (claims a project makes vs claims the build platform attests); [ICD 203](https://www.dni.gov/files/documents/ICD/ICD-203.pdf) sourcing and confidence | PARTIAL | Four evidence labels on an agent's backlog item. An old idea in a new place, not a new mechanism. |
| F8 | Risk lens and tradeoff lens kept apart; unrated rows listed as unrated | PMBOK risk register kept separate from prioritization; SAFe ROAM board | EXISTS | Nothing to claim. |
| F9 | Append-only receipt ledger (UPDATE and DELETE refused, `supersedes` for corrections); each ship event names `job_id` and `tool_id`; coverage metric | Jira [deployments linked to issue keys](https://community.atlassian.com/t5/Jira-questions/What-makes-a-Deployment-appear-in-Jira-for-a-specific-issue/qaq-p/2589141); SOX and ITIL audits of production changes without an approved ticket; [SLSA](https://slsa.dev/provenance/v1) `builder.id`; [Agent Trace](https://github.com/cursor/agent-trace); [OpenTelemetry GenAI spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans); hash-chained agent logs ([VerityLedger](https://pypi.org/project/verityledger/), [omega-audit](https://pypi.org/project/omega-audit/)) | EXISTS | Weaker than SOX reconciliation today, because the coverage counts filled fields and does not resolve them. |
| F10 | Append-only row writes under a lock; merge conflicts resolved by row id | Beads hash ids "to prevent merge collisions" and Dolt cell-level merge; git [merge drivers](https://git-scm.com/docs/gitattributes) | EXISTS | Our merge script is run by hand; no `.gitattributes` wires it. |
| F11 | One read-only front door over PRs, backlog, handoffs, seeds, witness stubs | GitHub Projects views; the GTD weekly review | PARTIAL | Reaches repo-file stores. Not a claimable idea. |
| F12 | Create-only projection of rows to GitHub issues | `gh issue create` with native `--blocked-by` | EXISTS | Ours is behind native: it writes "Blocked by #N" as body text. |
| F13 | Fate registry: each artifact class declares its allowed terminal fates | Jira [resolution include and exclude per transition](https://community.atlassian.com/forums/Jira-questions/Can-we-have-seperate-resolution-fields-or-list-for-each-project/qaa-p/3014360); [Issue Type Resolutions app](https://marketplace.atlassian.com/plugins/net.brokenbuild.issue-type-resolutions/server/overview) | PARTIAL | One fate vocabulary across several ledgers. Soft for the backlog. |
| C | The combination: checked trigger, resolved tool, door, backout plan, receipt naming the item | ITSM change records ([ServiceNow change management](https://www.servicenow.com/community/itsm-forum/change-management-in-servicenow-everything-you-need-to-know/m-p/3439058); [Stanford risk assessment](https://uit.stanford.edu/service/changemgt/impacts_risks)) | PARTIAL | The change-record pattern applied to an agent backlog in plain files, with evidence labels. The door is not wired to a human today. |

Tally: 7 EXISTS, 7 PARTIAL (counting the combination), 0 with no prior art found.

## What the hunch got right and wrong

- **Wrong:** "the backlog graph is a novel approach to tracking agent work." Beads has the same shape and a public following;
  GitHub has the edges natively; ITSM has had the gating and the receipts for decades.
- **Right, narrowly:** the agent harnesses themselves (Claude Code, Codex, Taskmaster, Beads) do not ship the gating layer. None
  of them has a door, a backout plan, an evidence label or a ship receipt on a work item. The gap is real; the ideas to fill it
  are old. That is a positioning point ("change management for an agent's backlog"), not an invention.

## Hyperstition pass (ADR-086 pass 2, run 2026-11-05)

One pass, per ADR-086: state the world where the backlog graph already works as a gated change record for agent work, list
the claims that world needs, try to break each, and emit a repair row only for a crack with citable evidence. A crack with
no evidence emits no row. Pass 2 may add a gate, never remove one. No new dependency anywhere: every row is stdlib Python,
`gh` 2.97 (already used) or a git built-in.

| # | Claim the working world needs | Loki result | Evidence | Fate |
|---|---|---|---|---|
| K1 | The ready-now list names only rows safe to start | CRACK: a one-way row with a DRAFT abort ranks first | `scripts/backlog_graph.py`, row `agent-receipts-audit-first-conversion` | row `ready-now-door-decision-split` (P2) |
| K2 | Receipt coverage measures the link to planned work | CRACK: counts filled fields; 6 of 86 backlog ids match no row | `scripts/receipt_coverage.py`, `2026-10-20-job-tool-ids.sql` | row `receipt-coverage-resolved-split` (P3) |
| K3 | The GitHub projection carries the graph | CRACK: edges are body text; `gh` has `--add-blocked-by` | `scripts/backlog_issue_sync.py` | row `issue-sync-native-blocked-by` (P3) |
| K4 | Parallel sessions cannot lose backlog edits in a merge | CRACK: no `.gitattributes`; the one existing row proposes `union`, wrong for a file edited in place | `scripts/backlog_merge_by_id.py`, row `jsonl-ledgers-merge-union` | row `backlog-merge-driver-by-id` (P2); gate added to `jsonl-ledgers-merge-union` |
| K5 | One-way rows reach a person | HOLDS on the assembly line (`line_triage.py` gives R3); the gap is K1 | `scripts/line_triage.py` | no row |
| K6 | Ripeness never writes rows | HOLDS as declared: `--apply-closes` is opt-in, SECRETLY-DONE only, self-tested | `scripts/backlog_ripeness.py` | no row |
| K7 | The state gate always runs | HOLDS locally: session start arms the hook; CI off is a standing choice | `.claude/hooks/session-start.sh` | no row |
| K8 | Backlog fates are enforced | HOLDS by design: soft on purpose to avoid taxonomy overfit | `scripts/fates.py` | no row |
| K9 | The job and tool graph is clean | CRACK, already owned: 506 held | `universe_jtbd_adapter.py --check` | existing `jtbd-orphan-jobs-groom`, `jtbd-standing-tools` (count refreshed) |
| U1 | The readiness card is worth extracting | UNKNOWN: no evidence either way | this proposal | falsifier row `readiness-card-decision-test`, then `readiness-card-oss-extract` HOLDING behind it (one-way: public repo, Zach creates it) |

Cut at the Loki step (no row): a "real stop" hook for one-way rows (agents cannot send; Zach does, and K1 covers the nudge),
making backlog fates hard, a CI path for the state gate, a positioning note (this proposal is the write-up), and a new row for
the 147 NOT-RESOLVED tools (the assembly line already routes them to R-1, "fill it first"). Nothing existing was composted:
no open row was made obsolete by these findings.

Graph after the pass: 466 rows, 294 active; the five OPEN repair rows sit in wave 0 and are ready now; 0 new findings;
`backlog_status_check.py --check` and `universe_jtbd_adapter.py --check` both PASS.

## Worth open sourcing?

Measured against the open-source skills queue (resumeware: standalone, generic, MIT, no ARCS words, gauntlet before publish):

1. **Do not open source the tracker.** It would be a weaker Beads: private work rows, ARCS vocabulary (COMPOSTED, ripe,
   NOTOMATION), a 506-row held baseline, no installer.
2. **Maybe one small skill, only if a test earns it: `readiness-card`.** Input: any work item (Beads issue, GitHub issue, JSON row).
   Output: six lines (door, prepared, unconfirmed, trigger, abort and undo, evidence coverage), each labelled MEASURED, DECLARED,
   CUE or UNCONFIRMED. Pitch it honestly as verification-matrix labels for agent work items, built to sit beside Beads. Before
   building, run the card on 10 real Beads or GitHub issues and see whether it changes a single go or no-go decision. If not, drop it.
3. **No package for the receipt join.** It is a convention (two columns, a prefix CHECK, an append-only trigger, a coverage query)
   and Jira and SLSA already cover the idea. At most, a short pattern note.
4. **Fix our own gaps first; these are worth more than any release:**
   - wire the one-way door to a real stop (a ready-list rule or a hook), since a one-way row tops the ready list today;
   - make receipt coverage count only `job_id` values that resolve to a real row;
   - write native `--blocked-by` relationships in `backlog_issue_sync.py`;
   - register `backlog_merge_by_id.py` as a `.gitattributes` merge driver.

## Not verified

- Beads' docs describe Dolt as the store today and JSONL as an export; older forks say JSONL was the source of truth. No grade depends on which.
- Claude Code task tool dependency parameter names come from community pages; the official docs say only "dependencies".
- Codex: no official doc on task dependencies found; graded from third-party pages only.
- Several citations for the skeptic's systems are community threads or secondary pages (Jira deployments, ServiceNow change
  management), not vendor docs. The GSN, SLSA and ICD 203 links are primary. NASA verification matrices, SOX change audits,
  PMBOK and SAFe ROAM are named from general knowledge without a fetched URL.
- The TBD plugin's license and maturity were not checked.
- Receipt coverage was read by direct SELECT, not `scripts/receipt_coverage.py --export` (no local export present).
