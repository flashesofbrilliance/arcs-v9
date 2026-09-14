# Worktree reconciliation audit — 2026-09-11 (Triune Stream A)

Base: `origin/main 0dc43d58` · method: `git rev-list --left-right` for ahead/behind, **`git cherry` (patch-id)
for real-unmerged vs ghost commits**, dirty count excludes hook-state files (`_INBOX/*.jsonl`,
`_STATE/pulse.json`, `_STATE/snapshot.json`, `_STATE/handoff-progress*`). Machine-readable twin:
`_STATE/worktree-audit-2026-09-11.json`. Nothing was pruned; this is the sweep, pruning stays human-owned
(bundle-before-remove via the `cruft-sweep` skill).

## Headline

| class | n | meaning |
|---|---|---|
| ACTIVE-recent | 18 | real unmerged commits, last commit on/after 2026-09-04 |
| UNMERGED-stale | 33 | real unmerged commits, last commit before 2026-09-04 (needs a keep/land/drop call each) |
| GHOST-history | 8 | 255-922 "ahead" commits are pre-rewrite duplicates already on main by patch-id; only 1-4 real commits each |
| MERGED-prunable | 14 | zero real unmerged commits, clean tree: safe to `git worktree remove` |
| MERGED-but-dirty | 1 | zero unmerged commits but uncommitted tracked edits |

**The "71 worktrees of unaudited work" fear is mostly false.** Of 74 worktrees, the naive `ahead`
count is inflated by the history rewrite; by patch-id only **397** real commits are off main,
and 296 of those sit on stale branches. The single largest is `chatbot-1-1-jtbd-blockers-edda33`
(118 real commits, 2026-08-29, pushed) which deserves its own review, not a sweep.

## ADR-collision hold branches — RESOLVED (PRs open)

| was | now | branch | PR |
|---|---|---|---|
| ADR-038 exogenous-forge | **ADR-078** | claude/harness-build-optimization-f52489 -> claude/renumber-exogenous-forge-adr078 | #409 |
| ADR-039 refusal-to-overclaim | **ADR-079** | claude/elastic-rubin-f22a6e -> claude/renumber-refusal-to-overclaim-adr079 | #410 |
| ADR-039 instance-to-class · ADR-040 kairos-detector · ADR-041 atomic-honesty | **ADR-080 · ADR-081 · 041 (kept, free on main)** | claude/decision-geometry-logo-81fb56 -> claude/renumber-decision-geometry-adr080-081 | #413 |

Numbers allocated through `scripts/oracle.py next adr` (counter 77 -> 81, PR #408; merge it first).
Each renumbered branch was merged with `origin/main`; the five churny state files (CLAUDE.md,
MEMORY.md, `_STATE/snapshot.json`, `.claude/arcs-session-state.md`, `_ARCHIVE/handoffs.md`) take
main's version so each PR's net diff is exactly the work. The three original hold worktrees are
now GHOST-safe to remove once their PR merges (their commits are on the renumbered branches).

## MERGED-prunable (14) — safe to remove

| worktree | branch | last_commit | on_origin |
|---|---|---|---|
| blacksmith-staff-engineer-role-7266bf | claude/blacksmith-staff-engineer-role-7266bf | 2026-09-07 | True |
| arcs-v9-nftt-pulp-code-fix | fix/nftt-pulp-inline-code | 2026-09-10 | True |
| arcs-v9-nftt-pulp-governance | content/nftt-pulp-governance-2026-09-11 | 2026-09-10 | True |
| arcs-v9-nftt-pulp-wrap-fix | fix/nftt-pulp-inline-code-wrap | 2026-09-10 | True |
| arcs-v9-receipts-standing-rule | docs/receipts-standing-rule | 2026-09-10 | True |
| jobsrun | (detached) | 2026-09-09 | False |
| book-of-arcs-surface-d5e217 | claude/book-of-arcs-surface-d5e217 | 2026-09-09 | False |
| l0-l5-question-compass-swap-e1d16c | claude/l0-l5-question-compass-swap-e1d16c | 2026-09-09 | False |
| nftt-gravity-wells | content/nftt-gravity-wells-2026-09-11 | 2026-09-10 | True |
| nftt-ledger-not-story | content/nftt-ledger-not-story-2026-09-10 | 2026-09-10 | True |
| recruiter-call-prep-56ea4e | claude/recruiter-call-prep-56ea4e | 2026-09-09 | True |
| recursing-brattain-190758 | claude/recursing-brattain-190758 | 2026-09-11 | True |
| relaxed-hellman-8b918d | claude/linkedin-alerts-scraper-a97535 | 2026-09-08 | True |
| serene-cohen-05e7fe | claude/serene-cohen-05e7fe | 2026-09-08 | True |

## GHOST-history (8) — 1-4 real commits each, none on origin, June-July

| worktree | branch | real_unmerged | ghost_rewritten | dirty_real | last_commit |
|---|---|---|---|---|---|
| inspiring-margulis-b8d8b4 | claude/inspiring-margulis-b8d8b4 | 4 | 539 | 1 | 2026-07-02 |
| profile-scan-overlap-demo-fe791d | claude/profile-scan-overlap-demo-fe791d | 2 | 669 | 1 | 2026-07-14 |
| relaxed-jackson-8ebc24 | claude/parameterized-artifacts-cli-41aff5 | 2 | 637 | 1 | 2026-07-10 |
| site-fit-principal-gtm-84b402 | claude/site-fit-principal-gtm-84b402 | 1 | 922 | 1 | 2026-07-20 |
| danny-quick-precall-3db098 | claude/danny-quick-precall-3db098 | 1 | 696 | 1 | 2026-07-15 |
| peaceful-roentgen-8a80cd | claude/recoil-report-hila-call-9c21b0 | 1 | 673 | 0 | 2026-07-15 |
| quizzical-boyd-f489b2 | claude/quizzical-boyd-f489b2 | 1 | 537 | 1 | 2026-07-02 |
| frosty-kepler-b69f51 | claude/frosty-kepler-b69f51 | 1 | 255 | 0 | 2026-06-19 |

Recommendation: `git cherry -v origin/main <branch> | grep '^+'` on each, cherry-pick anything
worth keeping onto a fresh branch, then remove. These predate the filter-repo rewrite and will
never merge cleanly as-is.

## UNMERGED-stale (33) — needs a per-branch keep/land/drop call

| worktree | branch | real_unmerged | dirty_real | on_origin | unpushed | last_commit |
|---|---|---|---|---|---|---|
| chatbot-1-1-jtbd-blockers-edda33 | claude/chatbot-1-1-jtbd-blockers-edda33 | 118 | 0 | True | 1 | 2026-08-29 |
| decision-geometry-logo-81fb56 | claude/decision-geometry-logo-81fb56 | 26 | 0 | False | None | 2026-08-01 |
| nervous-babbage-fae433 | claude/robin-daniels-profile-report-ae2d0a | 19 | 1 | False | None | 2026-08-06 |
| arcs-demo-ahmed-b0db74 | claude/arcs-demo-ahmed-b0db74 | 18 | 0 | True | 0 | 2026-09-03 |
| funny-meitner-b36bea | claude/funny-meitner-b36bea | 14 | 0 | False | None | 2026-08-28 |
| system-arcs-field-os-515d3e | claude/system-arcs-field-os-515d3e | 11 | 1 | True | 0 | 2026-08-23 |
| counterpart-forge-cli-build-a80612 | claude/counterpart-forge-cli-build-a80612 | 10 | 2 | True | 0 | 2026-08-11 |
| yuri-ahmed-communication-f2549e | claude/todd-work-continuation-1698a8 | 10 | 0 | True | 1 | 2026-08-28 |
| plugin-marketplace-arcs-skills-9622bd | claude/plugin-marketplace-arcs-skills-9622bd | 8 | 0 | True | 1 | 2026-08-28 |
| awesome-chebyshev-41e7ef | claude/awesome-chebyshev-41e7ef | 5 | 1 | True | 0 | 2026-08-11 |
| elastic-rubin-f22a6e | claude/elastic-rubin-f22a6e | 5 | 1 | False | None | 2026-08-01 |
| vp-data-ops-interview-prep-658fe3 | claude/vp-data-ops-interview-prep-658fe3 | 4 | 1 | True | 0 | 2026-09-03 |
| vigorous-lederberg-a6ca86 | claude/recoil-kinexys-sizing | 4 | 0 | True | 0 | 2026-08-29 |
| zachharris-website-design-bcb738 | claude/intelligent-nightingale-bc597c | 4 | 0 | False | None | 2026-08-29 |
| dazzling-khorana-efca37 | claude/festive-lichterman-a2b3cd | 4 | 0 | False | None | 2026-08-28 |
| heuristic-jemison-d8cb71 | claude/heuristic-jemison-d8cb71 | 4 | 1 | True | 0 | 2026-08-23 |
| wing-s-tier-diamond-ad4e8a | feat/operators-op20-op21-adapter | 4 | 1 | False | None | 2026-08-29 |
| gallant-mcclintock-12afb5 | claude/gallant-mcclintock-12afb5 | 3 | 0 | False | None | 2026-08-28 |
| mobile-portrait-button-wrap-d05201 | claude/mobile-portrait-button-wrap-d05201 | 3 | 0 | True | 1 | 2026-08-28 |
| pensive-mendel-40a4c4 | claude/elastic-driscoll-a80e72 | 3 | 1 | True | 0 | 2026-08-29 |
| realtime-updates-github-gate-46a82e | claude/realtime-updates-github-gate-46a82e | 3 | 0 | True | 1 | 2026-08-28 |
| token-consumption-improvement-6ba854 | claude/harness-build-optimization-f52489 | 3 | 0 | True | 0 | 2026-07-22 |
| happy-shamir-1c8b30 | chore/session-close-2026-08-29 | 2 | 1 | False | None | 2026-08-29 |
| omakase-arcs-site-349c0d | claude/omakase-arcs-site-349c0d | 2 | 0 | False | None | 2026-08-28 |
| arcs-commit-numbers-hyperlinks-7dddf1 | claude/arcs-commit-numbers-hyperlinks-7dddf1 | 1 | 0 | False | None | 2026-08-28 |
| status-page-day-count-cddf40 | claude/status-day-et-stamp | 1 | 0 | True | 1 | 2026-08-28 |
| arcs-demo-kam-4d760a | claude/arcs-demo-kam-4d760a | 1 | 0 | False | None | 2026-08-28 |
| elated-hawking-c08b93 | claude/elated-hawking-c08b93 | 1 | 0 | True | 17 | 2026-08-28 |
| kind-grothendieck-fd2df4 | claude/musing-pike-b7d222 | 1 | 0 | False | None | 2026-08-28 |
| musing-bell-a2485e | claude/jam-with-arcs-23d35c | 1 | 0 | False | None | 2026-08-28 |
| night-moves-work-digest-d9ca1e | claude/night-moves-work-digest-d9ca1e | 1 | 0 | False | None | 2026-08-28 |
| resume-tailoring-job-role-ef9d1c | claude/resume-tailoring-job-role-ef9d1c | 1 | 0 | False | None | 2026-08-28 |
| sugar-crm-state-prep-8f6420 | claude/sugar-crm-state-prep-8f6420 | 1 | 1 | False | None | 2026-08-13 |

Not on origin = the worktree is the only copy. Bundle before any removal.

## ACTIVE-recent (18) — leave alone

| worktree | branch | real_unmerged | unpushed | last_commit |
|---|---|---|---|---|
| arcs-v9 | fresh-starts | 43 | 0 | 2026-09-11 |
| agitated-feynman-b23c40 | feat/audit-service | 8 | 0 | 2026-09-08 |
| kaizen-weekly | claude/relaxed-hellman-8b918d | 5 | 1 | 2026-09-11 |
| zealous-golick-89e6e6 | claude/fanatics-postmortem-thread3 | 5 | 0 | 2026-09-11 |
| competent-kirch-7c6e0f | claude/epic-bardeen-94cce3 | 3 | 0 | 2026-09-08 |
| determined-lovelace-de940d | claude/bridge-employer-index | 3 | 0 | 2026-09-11 |
| high-leverage-routines-249613 | claude/high-leverage-routines-249613 | 3 | 0 | 2026-09-08 |
| hopeful-archimedes-759237 | claude/bridge-scan-rubric | 3 | 0 | 2026-09-11 |
| jobs-arcs-care-batch-trigger-3da902 | claude/jobs-arcs-care-batch-trigger-3da902 | 3 | 0 | 2026-09-11 |
| quirky-taussig-946b8d | claude/quirky-taussig-946b8d | 3 | 3 | 2026-09-08 |
| nftt-second-pass | content/nftt-second-pass-2026-09-11 | 2 | 0 | 2026-09-11 |
| vigorous-proskuriakova-3ae10f | claude/le-woof-better-better-58fdd8 | 1 | 0 | 2026-09-05 |
| progressive-handoffs-global-memory-8a98c4 | claude/progressive-handoffs-global-memory-8a98c4 | 1 | 0 | 2026-09-04 |
| vigilant-mirzakhani-575667 | claude/frustration-gate-pattern | 1 | 1 | 2026-09-08 |
| gracious-darwin-9c2c9c | claude/reader-wrap-fix | 1 | 0 | 2026-09-07 |
| priceless-goldwasser-6be46d | claude/priceless-goldwasser-6be46d | 1 | 0 | 2026-09-08 |
| priceless-hopper-fbdd55 | claude/1a-handoff-snapshot | 1 | 0 | 2026-09-07 |
| quizzical-dhawan-252fe5 | claude/quizzical-dhawan-252fe5 | 1 | 0 | 2026-09-07 |

## Other findings

- `fresh-starts` (main checkout) is 43 real commits ahead of main and 14 behind; not merged, not deployed (matches the 09-11 cross-harness handoff).
- `prl-chatbot-sugarcrm-605dbe` has `main` checked out with 2 dirty tracked files: a stray edit on main, look before discarding.
- 28 worktrees have branches never pushed to origin; 10 pushed branches carry unpushed commits (`elated-hawking-c08b93`: 17).

---

## Amendment 2026-09-13 — MERGED-prunable class pruned (bundle first)

Re-verified every MERGED-prunable row against `origin/main` by patch-id and clean tree **at prune
time**, not from the 09-11 numbers. Worktrees **72 → 62**. Branch refs kept for every removed tree
(double backup). Manifest: `~/arcs-worktree-bundles/MANIFEST-2026-09-13.tsv`. Receipt:
`2026-09-13--prune-merged-worktrees-bundle-first--ZH`.

### Removed (9) — `git bundle create` + `verify` ok, then `git worktree remove`

| worktree | branch | tip | bundle |
|---|---|---|---|
| arcs-v9-nftt-pulp-code-fix | `fix/nftt-pulp-inline-code` | 9b61ea6d | `arcs-v9-nftt-pulp-code-fix.bundle` |
| arcs-v9-nftt-pulp-governance | `content/nftt-pulp-governance-2026-09-11` | 62aa60ac | `arcs-v9-nftt-pulp-governance.bundle` |
| arcs-v9-nftt-pulp-wrap-fix | `fix/nftt-pulp-inline-code-wrap` | bce97ad3 | `arcs-v9-nftt-pulp-wrap-fix.bundle` |
| arcs-v9-receipts-standing-rule | `docs/receipts-standing-rule` | 860bac74 | `arcs-v9-receipts-standing-rule.bundle` |
| blacksmith-staff-engineer-role-7266bf | `claude/blacksmith-staff-engineer-role-7266bf` | 481433ff | `blacksmith-staff-engineer-role-7266bf.bundle` |
| book-of-arcs-surface-d5e217 | `claude/book-of-arcs-surface-d5e217` | 074b1120 | `book-of-arcs-surface-d5e217.bundle` |
| l0-l5-question-compass-swap-e1d16c | `claude/l0-l5-question-compass-swap-e1d16c` | 065c7f3b | `l0-l5-question-compass-swap-e1d16c.bundle` |
| relaxed-hellman-8b918d | `claude/linkedin-alerts-scraper-a97535` | 49c9c606 | `relaxed-hellman-8b918d.bundle` |
| serene-cohen-05e7fe | `claude/serene-cohen-05e7fe` | 50247ccd | `serene-cohen-05e7fe.bundle` |

### Not removed

| worktree | why |
|---|---|
| recruiter-call-prep-56ea4e | gained 1 real commit since the audit (Monstro AIME session close); reclassified ACTIVE-recent |
| recursing-brattain-190758 | gained 5 real commits since the audit (identity/brand prototypes (composite-identity map, identity-origami, five-fathom sounding, provenance chip, attraction rules)); reclassified ACTIVE-recent |
| nftt-gravity-wells, nftt-ledger-not-story | already removed by another session before this pass |
| jobsrun | detached at 074b1120 (on `origin/main`); directory already absent, entry dropped by `git worktree prune`; nothing to bundle |

### Lesson

The audit is a snapshot; two "prunable" trees became active within 48 hours. Re-verify at action
time, never prune from a stored classification. Remaining for a per-branch keep/land/drop call:
33 UNMERGED-stale + 8 GHOST-history + the 3 original hold worktrees (their work is on main via
#409/#410/#413; they are now candidates for the next prune pass).

### Pass 2 (same day) — the 3 original ADR-collision hold worktrees removed. Worktrees **62 → 59**

Verified at action time: each hold-branch tip is an **ancestor of `origin/main`** (the renumbered
branches were cut from these exact tips and merged via #409/#410/#413), `git cherry` real=0, and the
work-file diff against main is empty. Bundled + verified before removal; branch refs kept.
Receipt: `2026-09-13--prune-hold-worktrees-pass2--ZH`.

| worktree | branch | tip | landed via |
|---|---|---|---|
| token-consumption-improvement-6ba854 | `claude/harness-build-optimization-f52489` | 6a8010ad | #409 (ADR-078) |
| elastic-rubin-f22a6e | `claude/elastic-rubin-f22a6e` | 7744f565 | #410 (ADR-079); uncommitted .claude/launch.json (3 arcs-mini launch entries) saved as elastic-rubin-f22a6e.uncommitted.patch |
| decision-geometry-logo-81fb56 | `claude/decision-geometry-logo-81fb56` | eabee6f4 | #413 (ADR-080/081/041) |

PENDING.md "Worktree hold branches" note ("Do NOT remove these worktrees — they are the only copy
of the work") is now moot: the work is on main and in the bundles.

## Pass 3 (2026-09-13, separate session between the audit-doc update above and this one)

Between the "Pass 2" entry above and this session, an unrecorded intermediate sweep removed
**most of the remaining UNMERGED-stale + GHOST-history + ACTIVE-recent worktrees** — the repo
went from 59 worktrees to the 16 seen at the start of this session. Evidence: 70 bundles now sit
in `~/arcs-worktree-bundles/` (see `MANIFEST.tsv`, most stamped `Sep 13 12:07`), well beyond the
17 this doc's Pass 1/2 account for. **No content was lost** — spot-checked 11 of the removed
branches (`claude/progressive-handoffs-global-memory-8a98c4`, `claude/quirky-taussig-946b8d`
[3 unpushed commits], `feat/audit-service`, `claude/high-leverage-routines-249613`,
`claude/epic-bardeen-94cce3`, `claude/le-woof-better-better-58fdd8`, `claude/reader-wrap-fix`,
`claude/priceless-goldwasser-6be46d`, `claude/1a-handoff-snapshot`, `claude/quizzical-dhawan-252fe5`,
`claude/bridge-scan-rubric`) and every branch ref is still intact locally, not an ancestor of
`origin/main` (i.e. still carries real unmerged/unpushed commits), and each has a bundle too —
double backup held. **But several of these were previously classified ACTIVE-recent** in this
same doc (real unmerged work, last touched within days) — pruning the *worktree* for those was
premature by this doc's own rule ("ACTIVE-recent (18) — leave alone"). Nothing to restore
urgently since the branches+bundles are safe, but flagging: **a human should decide whether any
of that ACTIVE-recent work (e.g. `quirky-taussig-946b8d`'s 3 unpushed commits) needs a fresh
worktree recreated to finish landing it** (`git worktree add <path> <branch>` from the branch ref
— no bundle restore needed, the ref is live). Not investigated further this session; out of the
assigned scope (this session's brief was the 10 UNCLAIMED-handoff worktrees below).

## Pass 4 (2026-09-13, this session) — the 10 UNCLAIMED-handoff worktrees

A live SessionStart hook flagged 12 worktrees as unclaimed progressive-handoff checkpoints (last
session ended without `/handoff`). 2 were off-limits (active parallel sessions: `hopeful-archimedes-759237`
running bridge-scan-rubric scoring, `recursing-brattain-190758` running 720-brand-coherence pickup —
neither touched). The remaining 10 were classified by `git cherry` patch-id against `origin/main`
plus a manual read of every non-hook-state dirty/untracked file (hook-state churn —
`_STATE/handoff-progress*`, `_STATE/pulse.json`, `_STATE/snapshot.json`, `_INBOX/*.jsonl` — is
noise per this doc's own convention and ignored for classification):

| worktree | branch | real unmerged | verdict | why |
|---|---|---|---|---|
| jobs-arcs-care-scrape-status-2a9b9d | claude/jobs-arcs-care-scrape-status-2a9b9d | 0 | **PRUNED** | fully on origin/main, only hook-state dirt |
| zealous-golick-89e6e6 | claude/good-host-api-passthrough | 0 | **PRUNED** | merged via PR #428, only hook-state dirt |
| recruiter-call-prep-56ea4e | claude/recruiter-call-prep-56ea4e | 1 (state-only) | **PRUNED** | the 1 unmerged commit (`beec6752`) touches only `_STATE/handoff-progress.jsonl` + `_STATE/snapshot.json` and its own message says "All code merged to main via #384/#386/#390/#391; this branch is state-only" — verified true |
| determined-lovelace-de940d | claude/handoff-v3.61.0 | 0 | KEEP, mark claimed | the v3.61.0 handoff session itself; content already folded into CLAUDE.md; only dirty file is hook-state; left in place per task note, not acted on |
| cbs-anti-slop-engine | claude/cbs-anti-slop-engine | 1 | **NEEDS HUMAN CALL** | real net-new feature commit `e6875c40`, `src/lib/cbs.ts` (137 lines, zero-dep CBS anti-slop scoring engine, tsc-clean + smoke-tested); not on any PR yet — land or drop |
| modest-gauss-f40b89 | claude/modest-gauss-f40b89 | 1 | **NEEDS HUMAN CALL** | real 1-line typography fix (`a38a768d`, nbsp after lone "I" dropcap) on live `public/blog-nftt-schematic-scaffolds.html`; confirmed NOT on origin/main; trivial, low-risk cherry-pick candidate |
| jobs-arcs-care-batch-trigger-3da902 | claude/jobs-arcs-care-batch-trigger-3da902 | 0 | **NEEDS HUMAN CALL** | 2 uncommitted untracked files, real content: `_STATE/job-search/yuri-1-1-index-card.md` + `-vector-shift-ledger.md` (Yuri call prep, ~76 lines) — needs a commit, not a prune |
| linkedin-articles-export-9c494a | claude/linkedin-articles-export-9c494a | 0 | **NEEDS HUMAN CALL (small)** | all real work already shipped via PR #422/#426 per its own `_STATE/handoff-progress.md` delta; only remaining real artifact is one untracked witness stub (`_STATE/witness/2026-09-11.jsonl`, 1 line) — should be folded into the canonical witness log before the worktree is pruned, not discarded |
| memory-consolidation-handoffs-b852b1 | claude/memory-consolidation-handoffs-b852b1 | 0 | **NEEDS HUMAN CALL** | real uncommitted cross-harness handoff doc addressed to Hermes, `_STATE/handoff-2026-09-13-hermes-userN-productization-pickup.md` (72 lines, re: PROP-2026-09-12-USERN-EXTENSIBILITY-001) — needs to be committed/delivered, not discarded |
| prl-chatbot-sugarcrm-605dbe | `main` (unusual — checked out on main directly, not a feature branch) | 0 commits, but real staged diff | **NEEDS HUMAN CALL — highest priority** | real staged changes to `public/scott-cut.html` + `runtime/specs/knowledge-lattice-v1.json` (9 ins/11 del) plus ~1,900 lines of untracked real PRL client-engagement evidence docs under `_ARTIFACTS/prl-1-1-evidence/` and `_STATE/2026-09-08-prl-forensic-recoil.md` — none of this is on any branch; being checked out on bare `main` means a careless `git checkout` or worktree op here could strand it. Recommend: create a proper feature branch from this worktree's current state and commit before doing anything else with it. |

`python3 scripts/cruft_sweep.py survey` corroborates: 0 of these 10 came back `SAFE`, all 10 came
back `REVIEW` (the script's own uniq-file heuristic is noisier than the `git cherry` read above
but agrees on the verdict — nothing here is mechanically safe to auto-prune).

### Pruned this pass (3) — bundle-first, branch ref kept as second backup

| worktree | branch | tip | bundle |
|---|---|---|---|
| jobs-arcs-care-scrape-status-2a9b9d | `claude/jobs-arcs-care-scrape-status-2a9b9d` | e77b43d7 | `jobs-arcs-care-scrape-status-2a9b9d.bundle` |
| zealous-golick-89e6e6 | `claude/good-host-api-passthrough` | 96477731 | `zealous-golick-89e6e6.bundle` |
| recruiter-call-prep-56ea4e | `claude/recruiter-call-prep-56ea4e` | beec6752 | `recruiter-call-prep-56ea4e.bundle` |

All three: `git bundle verify` OK, branch ref confirmed still present after `git worktree remove`.

### Not pruned (7) — left alone, decision owed to Zach; nothing destructive done

`determined-lovelace-de940d`, `cbs-anti-slop-engine`, `modest-gauss-f40b89`,
`jobs-arcs-care-batch-trigger-3da902`, `linkedin-articles-export-9c494a`,
`memory-consolidation-handoffs-b852b1`, `prl-chatbot-sugarcrm-605dbe` — see table above for why
each one. `prl-chatbot-sugarcrm-605dbe` is the standout: real uncommitted client (PRL) evidence
work sitting on a bare `main` checkout, highest-priority human call of the batch.
