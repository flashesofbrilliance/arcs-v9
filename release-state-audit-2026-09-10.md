# ARCS v9 Release-State Audit — 2026-09-10

Read-only audit. No state was changed by this run. All evidence collected via local `git` (read commands only), `gh` CLI (read-only queries), and the Vercel MCP `list_deployments` (read-only).

## Executive finding

Committed, pushed, PR open, preview deployed; not merged to main.

## Repository state

| Check | Observed value | Status | Evidence |
|---|---|---|---|
| Repository | `flashesofbrilliance/arcs-v9` (https remote `origin`) | ✅ matches expectation | `git remote -v` |
| Default branch | `main` | ✅ confirmed | `gh repo view --json defaultBranchRef` → `main` |
| Current local branch | `resume-tailors` (audit run from `/Users/zharris/arcs-v9`; candidate lives in worktree `.claude/worktrees/jobs-arcs-care-batch-trigger-3da902`) | ℹ️ note | `git branch --show-current`; Layer 0 summary worktree list |
| Working tree clean | No — main checkout has 3 modified + 19 untracked paths (pre-existing session state; untouched by this audit) | ⚠️ observed, not altered | `git status --short --branch` |
| Candidate commit | `43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc` exists locally: “fix(jobs): rubric v1.3 — undisclosed comp is neutral, single deep domain not zero [NCI:SKIP]”, Zach Harris, 2026-09-10T11:34:52-04:00 | ✅ verified | `git cat-file -t`; `git log -1 43bd2636` |
| Candidate reachable from main | **No** — `git merge-base --is-ancestor 43bd2636 origin/main` → NOT_REACHABLE_FROM_MAIN. Reachable only from `claude/jobs-arcs-care-batch-trigger-3da902` (local worktree branch + `remotes/origin/…`) | ✅ branch-only | `git branch -a --contains`; `git merge-base --is-ancestor` |
| Remote configured | Yes — `origin` → github.com/flashesofbrilliance/arcs-v9 (fetch+push) | ✅ | `git remote -v` |

Candidate branch pushed: `git ls-remote origin` shows `refs/heads/claude/jobs-arcs-care-batch-trigger-3da902` = `43bd2636…` (exact SHA match). GitHub `main` head = `065c7f3b11e8927c4ca9a5ee84a2ed1256e826a3` (does not contain the candidate).

## GitHub state

| Check | Observed value | Status | Evidence |
|---|---|---|---|
| Candidate branch | `claude/jobs-arcs-care-batch-trigger-3da902` exists on origin, head `43bd2636…` | ✅ pushed | `git ls-remote origin` |
| PR number | **#393** (matches expectation) | ✅ | `gh pr view 393` |
| PR title | “fix(jobs): rubric v1.3 — undisclosed comp neutral, single deep domain not zero” (matches expectation) | ✅ | `gh pr view 393 --json title` |
| PR state | **OPEN**, not draft | ✅ | `state: OPEN`, `isDraft: false` |
| PR merged | **No** — `mergedAt: null`, `mergeCommit: null` | ✅ unmerged | `gh pr view 393 --json mergedAt,mergeCommit` |
| PR base branch | `main` | ✅ | `baseRefName: main` |
| PR head SHA | `43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc` | ✅ matches candidate | `headRefOid` |
| Main head SHA | `065c7f3b11e8927c4ca9a5ee84a2ed1256e826a3` | ✅ candidate NOT in main | `gh api repos/…/branches/main` |
| GitHub lifecycle classification | **`pr_open_unmerged`** | ✅ | PR #393 open, head = candidate, no merge commit |

Timestamps: created 2026-09-10T15:35:09Z · updated 2026-09-10T15:36:12Z · closedAt null · mergedAt null. `gh pr list --head claude/jobs-arcs-care-batch-trigger-3da902 --state all` returns exactly one PR (#393) — no closed/merged sibling.

## Vercel state

| Check | Observed value | Status | Evidence |
|---|---|---|---|
| Project | `arcs-v9` — `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`, team `arcs-care` (`team_narCbxUgS4eiieJKRv1QMfff`) | ✅ | `.vercel/project.json` + Vercel MCP `list_deployments` |
| Deployment ID | `dpl_Hu2V5sBsWjFSMM3mgZN9GSPkRuu5` | ✅ | deployment with `githubCommitSha` = candidate |
| Deployment state | **READY** (created 2026-09-10T15:34:57Z; `isRollbackCandidate: false`) | ✅ ready | `state: READY` |
| Deployment branch/ref | `claude/jobs-arcs-care-batch-trigger-3da902` (`githubCommitRef`); branch alias `arcs-v9-git-claude-jobs-arcs-care-batch-trigge-f64e4c-arcs-care.vercel.app` | ⚠️ feature branch, not main | deployment `meta` |
| Deployment Git SHA | `43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc` | ✅ matches candidate | `meta.githubCommitSha` |
| GitHub PR association | `githubPrId: 393` | ✅ | deployment `meta` |
| Environment/target | `target: null` (branch/preview deployment; URL `arcs-v9-44tsufpwe-arcs-care.vercel.app`). Production deployments in the same list carry `target: "production"` and `githubCommitRef: main` — this one does not | ⚠️ preview | deployment `target` field |
| Deployment classification | **`preview_or_branch_deployment_ready`** — READY state on a PR-branch deployment is NOT a mainline/production release | ✅ classified | branch ref + PR association + `target: null` |

Current production reference point (context only): latest `target: "production"` deployment is `dpl_BuoPvEYcpLt3X2JKXAidnj4XNknv` from `main` @ `065c7f3b…` (merge of PR #391) — i.e., production tracks main and does not include the candidate commit.

## Integrity assessment

```text
- Candidate SHA: 43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc (local + origin branch head)
- GitHub PR head SHA: 43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc (PR #393)
- GitHub main SHA: 065c7f3b11e8927c4ca9a5ee84a2ed1256e826a3 (candidate NOT an ancestor)
- Vercel deployment SHA: 43bd2636924b7abe7a62c3f1f7d7ff0b92f491cc (dpl_Hu2V5sBsWjFSMM3mgZN9GSPkRuu5)
- SHA alignment: true (candidate = PR head = deployment SHA, exact match on all three)
- Mainline alignment: false (candidate not in GitHub main; deployment is branch/preview, target null, not main/production)
- Release state: pr_open_unmerged + preview_or_branch_deployment_ready
- What is confirmed: code written and committed locally (worktree branch); pushed to origin; PR #393 open against main with head = candidate; Vercel built a READY preview deployment from exactly that commit, tagged to PR #393; production currently serves main @ 065c7f3b (PR #391 merge), which does not contain the candidate.
- What remains unconfirmed: nothing material for lifecycle state. PR mergeability/checks were not evaluated (out of audit scope); whether the preview deployment functions correctly is not asserted (READY ≠ validated).
```

## Required next action

`Review and merge PR #393; then verify the automatic main deployment.`

(Not executed. This audit changed no state.)

## Integrity check

```text
- Files changed: exactly one (`release-state-audit-2026-09-10.md`)
- Repository mutations: none
- GitHub mutations: none
- Vercel mutations: none
- Other external systems accessed or changed: none
- Base ledger modified: no
- Layer 0 modified: no
```

Read-only commands used: `git status/branch/log/remote/cat-file/ls-remote/merge-base --is-ancestor`, `gh pr view/list`, `gh repo view`, `gh api …/branches/main`, Vercel MCP `list_deployments`. No checkout, commit, push, merge, deploy, alias, or rollback performed.

Audit complete — release state: pr_open_unmerged + preview_or_branch_deployment_ready; next action: Review and merge PR #393; then verify the automatic main deployment.
