---
title: Rollback and disaster-recovery plan, arcs-v9
version: 0.1 (draft, not adopted)
date: 2026-11-17
owner: Zach
status: PROPOSED
---

# Rollback and disaster-recovery plan, arcs-v9

**Why.** Every counterpart page and the product ride on one repo and one Vercel production deployment that serves every arcs.care host at once. Today a bad change can be undone, but only by someone who already knows the steps, and two layers (off-machine backups, the database) have no recent proof that a restore works.

**What.** One recovery recipe per layer (git, deploy, database, governance and policy rules, local state), a named rollback point before any client-facing change, and a monthly restore drill that proves each recipe still works.

**Why now.** On 2026-11-17 Zach asked that the MyAlly hub change (PR 2068) stay reversible "in case they want to see the previous version". That rollback point was made by hand; this plan makes it the default. The newest off-machine backups are dated 2026-09-26, 52 days old.

**How to read this.** The layer table shows what exists and what is missing. Sections 1 to 3 are before, during and after a change. Section 4 is the gap list, ranked. Nothing here is adopted until Zach says so.

## Layers: what can be restored today

| Layer | Control that exists (verified 2026-11-17) | Restore path | Gap |
|---|---|---|---|
| Git history on main | Merge commits only: squash and rebase are disabled in repo settings; `scripts/safe_merge.sh` pins the head SHA; the daily squash detector | `git revert -m 1 <merge>` in a PR, merged with `safe_merge.sh` | No server-side protection on main (branch protection and rulesets need GitHub Pro for a private repo; the API returns 403). A force push to main is possible. |
| Named rollback points | Tags exist only ad hoc (3 in total, e.g. `myally-hub-pre-2068`) | `git checkout <tag> -- <path>` then a PR | No rule that a client-facing change gets a tag before merge. |
| Production deploy | Vercel keeps prior production deployments; prior ones stay Ready | `vercel promote <last-good-url>` re-points every alias (memory `arcs-v9-deploy-blast-radius-guardrails`) | The `DEPLOY.md` that memory names is not on main. The recipe lives only in memory. |
| Database (Supabase `xbbpiryokswwvcrcutge`) | `decision_receipt` is append-only by trigger | Supabase backups: plan tier and point-in-time recovery not checked | Unknown restore window; no restore ever tested. |
| Governance and policy rules | Hooks in `scripts/git-hooks`, CI workflows, `.claude/` settings, all in git | Revert like any other file | `core.hooksPath` points at the main checkout (`/Users/zharris/arcs-v9/scripts/git-hooks`), so every worktree runs whatever branch the main checkout is parked on (it was 57 commits stale earlier today). Repo settings (merge methods) are not in git, so they cannot be reverted or diffed. |
| Off-machine backups | Encrypted bundles of memory and dirty worktrees; release assets in private repo `arcs-memory-backup`; iCloud copies; passphrase in Passwords (memory `offmachine-encrypted-backups-location-and-restore`) | Decrypt, `git clone <bundle>` | Last run 2026-09-26. No schedule. |
| Local untracked state | Per-move backups, e.g. `_STATE/backup-main-checkout-2026-11-17/`, branch `backup/main-checkout-2026-11-17` | Copy back | Ad hoc. |

## 1. Before a change (the rollback point)

For any merge that changes what a counterpart sees (a `*.arcs.care` host other than internal admin pages), or touches a gate, hook, workflow or repo setting:

1. Tag the main commit just before the merge: `git tag -a <surface>-pre-<pr> origin/main -m "<why>"`, then push the tag.
2. Record the current production deployment URL in the decision receipt (`refs`).
3. For a repo setting, write the current value into the receipt before changing it (settings are not in git).

Proposed mechanism: `safe_merge.sh` does steps 1 and 2 itself when the PR touches `public/`, `src/proxy.ts`, `next.config.ts`, `scripts/git-hooks/`, `.github/workflows/` or `.claude/settings*.json`. It already prints the receipt template, so it can add the tag and the deployment URL there.

## 2. During an incident (the recipes)

| Situation | First move (minutes) | Then |
|---|---|---|
| One page wrong, rest fine | Revert PR: `git revert -m 1 <merge>`, merge with `safe_merge.sh` | Receipt with `supersedes` |
| Client wants the previous version of a page back | `git checkout <tag> -- <file>` in a branch, PR, merge | Keep the tag; note it on the engagement |
| Whole production broken | `vercel promote <last-good-production-url>` (newest Ready production from main before the bad merge) | Then revert on main so the next deploy does not bring it back |
| A gate or hook blocks every commit | Revert the gate change; never disable the hook path | Gate fix gets its own PR and receipt |
| Main rewritten or lost | Restore from any worktree or the newest bundle; `git push` the known-good SHA after Zach's go | Rotate in the missing commits from PR refs |
| Database bad write | Append a correcting row (`decision_receipt`); for other tables, the Supabase restore path (to be confirmed) | Record what window was lost |

## 3. After (proof it still works)

A monthly restore drill, about 20 minutes, writes one receipt:

1. Restore one tagged page to a scratch branch and diff it against the tag.
2. Promote-then-repromote check on a preview, not production: confirm `vercel promote` syntax still works.
3. Decrypt the newest off-machine bundle and clone it.
4. Read the Supabase backup list and note the oldest restorable point.

## 4. Gaps, ranked by risk times effort

1. **Off-machine backups are 52 days old.** Re-run them and schedule them weekly (memory and dirty-worktree bundles). Low effort, high value.
2. **No server-side protection on main.** Options: GitHub Pro (branch protection and rulesets: block force push and deletion of main), or a daily check that main's head only moves forward (cheap and runs on any plan). Zach's call: it costs money.
3. **Hooks run from the main checkout.** Point `core.hooksPath` at a path relative to each worktree (`scripts/git-hooks`), so a stale main checkout cannot run old gates. Small change; it touches every worktree's behavior, so it needs Zach's go.
4. **Rollback point is manual.** Add the tag and deployment URL to `safe_merge.sh` (section 1).
5. **Deploy rollback recipe only in memory.** Land a short `DEPLOY.md` (or a `runtime/specs/` page) with the promote recipe.
6. **Repo settings not in git.** A small script that dumps merge-method and similar settings to a JSON file in git, with a `--check` in CI.
7. **Database restore window unknown.** Check the Supabase plan and point-in-time recovery; record it here.

## Not in scope

No change to how merges are approved, and no new paid service without Zach's go.
