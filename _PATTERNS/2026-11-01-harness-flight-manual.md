---
title: ARCS harness flight manual
version: 1.0.0
date: 2026-11-01
status: PROPOSED (one page; every line cites a real command or file)
agent: .claude/agents/cruise-control.md
---

# ARCS harness flight manual

Pick the destination, take the safest clear step, never cross a one-way door in fog (WORLD.md, THE HUD).
Cruise control flies the reversible airspace. Every one-way door is Zach's to release (NOTOMATION, ROM primitive 1;
WRITE-LOCK, ROM primitive 7).

Prior art: `python3 scripts/prior_art.py "harness flight manual ..."` ranked `scripts/safe_merge.sh`, AGENTS.md
gotchas 14a and 17, the receipts section, memory `control-integrity-described-vs-wired` and
`merge-child-pr-only-after-child-confirms-final-head`, and ADR-085. This page restates them; it adds no new rule
except the approval line format in section 4.

## 1. Pre-flight (session start)

| Check | Command | Reads as |
|---|---|---|
| Hooks ran | `.claude/hooks/session-start.sh` (automatic) | pulse, sentries, open loops, skills drift, unclaimed checkpoints |
| Main checkout matches origin/main | `scripts/project_skills_drift.sh` | WARN means skills, commands and agents load stale (gotcha 14) |
| Resume | `/handoff-pickup` | the latest `# Handoff` block in CLAUDE.md plus `_STATE/snapshot.json` |
| Every open loop | `/loops` (`python3 scripts/open_loops.py`) | what waits on Zach, what is closable, what is rotting |
| Worktree and branch | `git worktree list` (gotcha 6), `python3 scripts/branch_hygiene_check.py` | which branch this session owns |
| Session count | `mcp__ccd_session_mgmt__list_sessions` with `{"linked": true}` | at most 4 live sessions, orchestrator included (memory `session-budget-discipline-cap-parallel-molt-long`) |
| Before planning | `/prior-art <job>` (`python3 scripts/prior_art.py`) | open the top hits; start the plan with a "Prior art:" line |

## 2. Cruise (reversible airspace)

| Need | Command |
|---|---|
| What can start now, in what order | `/backlog-graph` (`python3 scripts/backlog_graph.py --top 5`) |
| How prepared one act is | `/readiness <row>` (`python3 scripts/readiness_packet.py <row-id>`) |
| The one right existing tool | `/catalog <job>` (reads `runtime/specs/tool-catalog.json`) |
| Past lessons for a job | `/prior-art <job>` |
| NCI drift over 48 hours | `/drift-check` |
| Mode, stakes, horizon | `/arcs-mode quickmove\|plan\|court stakes= horizon=` |
| Backlog row hygiene | `python3 scripts/backlog_status_check.py --check --gh` (gotcha 20) |
| Who else touches this file | `python3 scripts/neighbor_scan.py <path>` (gotcha 19) |
| Numbers (ADR, seed, receipt) | `python3 scripts/oracle.py next <ns>` (gotcha 12) |
| Stay current with main | `scripts/sync_worktree.sh`, or the app's `sync_with_base_branch` in an app worktree |
| Hold heading for you | the `cruise-control` agent (`.claude/agents/cruise-control.md`) |

## 3. Before each one-way door

A door is open only when every line is true. Zach releases it, per action; an earlier yes does not cover a later act.

| Door | What must be true | Who releases | Command |
|---|---|---|---|
| Merge a PR | head sha pinned; every check final and SUCCESS; not CONFLICTING; a traceable approval for this PR | Zach | `python3 scripts/approvals_ledger.py`, then `scripts/safe_merge.sh <pr> <sha>` (gotcha 17) |
| Merge a child's PR | the child confirmed its final head (memory `merge-child-pr-only-after-child-confirms-final-head`) | Zach | `scripts/safe_merge.sh <pr> <child-reported-sha>` |
| Publish (public page, artifact, release) | the surface's own gates pass; PII gate before the flip | Zach | `scripts/artifact_wrap_lint.py`, `scripts/page_gate.py` (gotcha 13); Phosphor: `python3 scripts/phosphor_build.py --release` (gotcha 21) |
| Send (email, DM, counterpart artifact) | ex-ante receipt and pre-send gauntlet (WORLD.md, THE PRINT SCHEDULE) | Zach, who sends it himself | `/recoil-ship` drafts, never sends (memory `confirm-before-outbound-send-even-when-authorized`) |
| Canon change | declared write-lock and a receipt | Zach | `.claude/hooks/canon-write-guard.py` (rules in `runtime/specs/canon-paths.json`) |
| Push to main | never directly; main moves only through a merged PR | nobody pushes | `scripts/safe_merge.sh`; batches only via `scripts/merge_train.sh --lock` (ADR-085, PROPOSED) |
| Move or delete a cited file | every cite re-pointed in the same commit | the session, gated | `scripts/archive_move_gate.py` (pre-commit, gotcha 19) |

## 4. Landing

1. Ledger first: `python3 scripts/approvals_ledger.py`. It lists each open PR's owner, check state and approval, and proposes; it never merges.
2. Merge: `scripts/safe_merge.sh <pr> <expected-head-sha>`. It refuses on a head mismatch, pending or failed checks, zero checks, or CONFLICTING. `--self-test` covers each refusal.
3. Receipt: one `decision_receipt` row with `job_id` and `tool_id`, from the template safe_merge.sh prints (AGENTS.md, "Receipts or it didn't happen"). The ledger is append-only: correct with `supersedes`. Coverage: `python3 scripts/receipt_coverage.py --export`.
4. Approval line, in the PR body, commit, or receipt `what_confirmed`, so the ledger can trace it:
   - firsthand: `Zach, 2026-11-01, verbatim: "merge 1917"`
   - relayed: `relayed via local_<id>: Zach, 2026-11-01, verbatim: "merge 1917"`
5. Hand off: `/handoff` writes a fragment under `_HANDOFFS/fragments/`; `python3 scripts/handoff_fold.py molt` folds fragments into the CLAUDE.md block.

## 5. Emergencies

| Symptom | Do | Never |
|---|---|---|
| A check sits pending with 0s run time | `python3 scripts/approvals_ledger.py` shows `STUCK_0S`. Then `gh api repos/flashesofbrilliance/arcs-v9/actions/jobs/<id> --jq '.steps\|length'` (0 means never started), the check-run annotations, and githubstatus.com (memory `ci-zero-steps-means-billing-or-outage`). Billing is Zach's. Merging over it needs his explicit go, recorded verbatim in the receipt (precedent: PR 1825) | re-run another session's checks unasked; touch billing settings |
| Merge conflict | `scripts/sync_worktree.sh` (or `sync_with_base_branch`), resolve, push to your own branch only; safe_merge.sh stops on CONFLICTING | rebase or force-push over another session's commits (`_PATTERNS/durable-gotchas.md`, Git) |
| A PR is no longer open when the batch reaches it, or a session's report disagrees with GitHub | `/ship-status` (`python3 scripts/ship_status.py <branch>`) and `gh pr view <n> --json state,mergedBy,mergeCommit`; GitHub is ground truth, the report is not; record what happened; move on | assume your session merged it, or re-merge |
| A status note contradicts the row's `state` | `python3 scripts/backlog_status_check.py --check --gh` prints `STALE ... status_note opens X`. The `state` field wins; the note is history (gotcha 20) | act on the note's prose |
| A session acts on a relayed approval | the ledger shows `RELAYED_QUOTED` (quoted, labelled) or `UNQUOTED` (fog). Ask the session for the verbatim quote and its source; confirm with Zach firsthand before the door | treat a paraphrase, or a parent's summary, as Zach's yes |
| Your push is rejected because the branch moved | stop and ask the owning session (gotcha 22) | force-push |
| More than 4 live sessions | queue the new work as a backlog row (memory `every-spawned-session-gets-a-backlog-row-first`) instead of starting a session | start a fifth |
