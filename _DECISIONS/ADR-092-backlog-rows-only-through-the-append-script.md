# ADR-092: Backlog rows are added only through the validated append script

> **Status:** PROPOSED (2026-10-31). Not decided. Depends on open PR #1893 merging; if PR #1893 is closed, this ADR is withdrawn.
> **Date:** 2026-10-31
> **Author:** Claude Opus 5.5 (decision-record reconciliation sweep, 2026-10-14 to 2026-10-31)
> **Oracle:** number allocated via `python3 scripts/oracle.py next adr` (92); `_SEEDS/_oracle.json` committed with this file.

## D: The decision

**Sharp question:** How does a new row get into `_QUEUE/induced-backlog.jsonl` so that the file stays valid when many sessions write to it?

**Decision (as recorded by Zach in his Project receipts, 2026-10-31, and stated in PR #1893):** rows are added only through the append script that PR #1893 adds under scripts/ (named backlog_append there). No hand edits, no side files merged by copy.

## E: Entity / system

- `_QUEUE/induced-backlog.jsonl`, the backlog every planning skill reads.
- The append script (PR #1893, open, branch `claude/backlog-append`): validates the whole batch (one JSON object per line; non-empty id, state and jtbd; id unique in file and batch; every depends_on and unblocks id resolves; state in `runtime/specs/backlog-status.json`; RUNNING carries a claim), appends under flock in one write, never rewrites a line, refuses the whole batch on any failure; 14 self-test fixtures wired into the pre-commit self-test loop (per the PR body).
- `.claude/commands/backlog-graph.md`, which PR #1893 extends with the rule.

## W: Window

**Horizon:** YEAR
**Revisit trigger:** the backlog moves to another store; or the script refuses a valid row often enough that sessions route around it.

## Context

ADR-089's kill-condition check found a byte-identical duplicate row (`phosphor-slip-sync`, lines 164 and 214), which blocked JTBD graph s1 until fixed at source. On 2026-10-31, 14 `rfp-ship-*` rows sat in an untracked side file in the main checkout, one with a wrong gate text, until PR #1893 landed them through the script with the correction. Both are the failure the script prevents: rows written by hand, outside validation, by parallel sessions.

## Options considered

### Option A: one validated append path (chosen)
- Duplicate ids, dangling dependencies and bad states are refused before they land.
- Append-only under a lock suits parallel sessions.
- Cost: editing an existing row needs its own path; this rule covers adding only.

### Option B: hand edits plus a pre-commit validator
- No new habit.
- Cost: catches problems at commit time, after a session has built on a bad row; does not serialize concurrent writers.

### Option C: status quo
- Cost: the two incidents above repeat.

## Decision

**Chosen:** Option A.
**Rationale:** the backlog is shared state written by many sessions; one gated writer is cheaper than repairing the graph after the fact.
**Trade-offs accepted:** one more tool to know; row edits and state changes remain outside this rule.

## Y: Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE once PR #1893 merges

**Loki test:** a rule nothing enforces is a reflex. Unless the pre-commit hook also rejects backlog lines added outside the script, sessions will keep hand-appending and the rule exists only in a command doc.

## Consequences

- Planning skills and handoffs point to the script instead of telling sessions to append lines.
- Open question for Zach: should pre-commit block a staged backlog diff that did not come from the script?

**Implementation pointer:** PR #1893.

## Linked receipts / ADRs

- ADR-086: two-pass backlog induction (depends on: the depends_on and unblocks fields this script validates).
- ADR-089: JTBD graph schema and stable ids (relates to: SOURCE-DUP on backlog ids).
