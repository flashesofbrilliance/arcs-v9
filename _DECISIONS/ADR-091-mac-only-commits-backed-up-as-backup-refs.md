# ADR-091: Mac-only commits are backed up as backup refs, not branches

> **Status:** PROPOSED (2026-10-31). Not decided. Zach accepts or rejects.
> **Date:** 2026-10-31
> **Author:** Claude Opus 5.5 (decision-record reconciliation sweep, 2026-10-14 to 2026-10-31)
> **Oracle:** number allocated via `python3 scripts/oracle.py next adr` (91); `_SEEDS/_oracle.json` committed with this file.

## D: The decision

**Sharp question:** How do commits that exist only on Zach's Mac get an off-machine copy without each one becoming a branch that starts a build?

**Decision (as recorded by Zach in his Project receipts, 2026-10-31; not read from a primary source by this session):** push each such branch to the private remote as `refs/backup/<date>/<branch>`, never as `refs/heads/<branch>`.

## E: Entity / system

- arcs-v9 origin (flashesofbrilliance/arcs-v9, PRIVATE per `gh repo view`) and ret-rfp-intelligence origin (PRIVATE).
- Measured 2026-10-31 with `git ls-remote origin 'refs/backup/*'`: arcs-v9 has 162 refs, all under `refs/backup/2026-10-31/`; ret-rfp-intelligence has 2 (`refs/backup/2026-10-31/claude/monday-agent-2d7edc`, `refs/backup/2026-10-31/claude/suspicious-austin-8898c4`).
- Branch-triggered automation: Vercel preview builds and GitHub Actions on branch pushes.

## W: Window

**Horizon:** YEAR
**Revisit trigger:** a backup ref is found to have started a build or a check run; the number of backup refs slows `git fetch`; or a restore from a backup ref fails.

## Context

Many local branches across worktrees had commits that existed nowhere else. Pushing them as branches would protect them but would create one preview build per branch and add noise to branch lists and PR tooling. Nothing on main documented the convention before this ADR (`git grep "refs/backup"` on main returned no hits on 2026-10-31).

## Options considered

### Option A: backup refs under refs/backup/<date>/ (chosen)
- Off-machine copy on the private remote; not a branch, so branch-push automation should not see it.
- Dated namespace keeps each sweep separate and auditable.
- Cost: invisible in the GitHub branch UI; restore needs an explicit fetch of the refspec.

### Option B: push as branches
- Visible and easy to restore.
- Cost: one build per branch; clutters branch lists and tools that scan branches.

### Option C: local bundle or Time Machine only
- No remote noise.
- Cost: still on one machine or one disk.

## Decision

**Chosen:** Option A.
**Rationale:** the goal is durability without side effects; refs outside `refs/heads/` give the first without the second.
**Trade-offs accepted:** discoverability. A restore is `git fetch origin 'refs/backup/<date>/<branch>:refs/heads/<branch>'`.

## Y: Conviction

**Polarity:** GREEN on the convention; the "no builds trigger" premise is NOT-CHECKED.
**Conviction:** MEDIUM
**Stability:** STABLE

**Loki test:** this sweep did not check whether any of the 162 pushes created a Vercel deployment or an Actions run. If GitHub or Vercel act on non-branch refs, the main rationale is gone.

## Consequences

- Backup sweeps write only under `refs/backup/<date>/`; nothing deletes them without Zach.
- A follow-up check (deployments and check runs for one backup sha) would move the premise from NOT-CHECKED to YES or NO.

**Implementation pointer:** the refs themselves on both private remotes; no script on main yet.

## Linked receipts / ADRs

- ADR-085: main write-lock and hot-file leases on git refs (relates to: git refs as state outside branches).
