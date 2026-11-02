# Dreaming pass 3 (2026-11-02): the docs and memory corpus

`python3 scripts/dream_mine.py --corpus --stale-days 45`: 1,283 docs (tracked arcs-v9
Markdown outside `_ARCHIVE`, `_STATE` and handoff fragments, plus the 356 project memory
files), 0.75 seconds. Proposals only; mark each **ACCEPT / REJECT / EDIT**.

- **Found:** 117 backticked repo paths that no longer exist, 107 "verified / confirmed / as of"
  dates older than 45 days, 0 near-duplicate memory pairs (description word overlap of 0.45
  or more).
- **Judged this pass:** the memory slice only (45 dead cites, 41 stale dates). Memory loads
  into sessions, so a stale fact there misleads every one. `_PATTERNS` (27), `_DECISIONS` (9)
  and the rest wait for the next pass, by the `dream-scout` agent once it is on main.
- Evidence for every verdict: `git ls-files`, `git log --all -- <path>`, `git log origin/main
  --diff-filter=D`, and `git branch -r --contains`.

## D. Proposals

| # | Pattern | Prevalence | Proposal |
|---|---|---|---|
| D1 | **Memories describe tools that never landed on main.** `pull-not-push-pre-render-legibility-gate` (cold_reader_gate.py, pre_prep_gate.py: only on `claude/arcs-demo-ahmed-b0db74`), `model-tier-routing-locked-principle` (model_tier_router.py: `claude/kind-grothendieck-fd2df4`), `verify-flags-against-full-source` (gauntlet_logbook.py: `claude/gauntlet-60anchor-rerun`), `arcs-v9-deploy-blast-radius-guardrails` (deploy-smoke.mjs: `feat/resume-pwa-theming`), `lab-mint-factory` (lab-mint skill: `claude/awesome-chebyshev-41e7ef`), `seed-bank-germination-conditions` (sixty_second_read.py: no branch), `github-public-portfolio-vs-private-arcs-v9` (showcase_project.py: no branch), `text-wrapping-defect-class-and-gate` (artifact-text-qa skill: no branch) | 8 memories, 10 tools | **Add a dated "Current state: not on main" line to each memory** naming the branch (or "lost"), so no session reaches for a tool that is not there. Then, per tool, **ASK-ZACH**: merge the branch, or retire the claim. This is the described-vs-wired failure (`control-integrity-described-vs-wired`). |
| D2 | Renamed files, old path still cited | 3: `supabase-rls-hides-rows-from-new-roles` (`sage_efficacy.js` is now `.mjs`, commit 0f9a4207), `vercel-operations` (`vercel-debug.sh` is now in `scripts/_archive/`), `mcp-oversized-result-envelope-parse-from-disk` (`tributary_backfill_probe.py` is in `_ARCHIVE/scripts-retired-2026-10/`) | **Correct the cite** in each memory; for the two archived scripts add "(retired)". |
| D3 | Memories citing deleted artifacts as background (PRL deck, Todd handoffs, forge-pattern pages, case-study template) | about 25 cites in 10 memories, `project_todd_hotes_prl_resins` alone has 11 | **HISTORY-OK, no edit.** They record what existed then; nothing tells a session to run them. |
| D4 | Verifications of live systems older than 45 days | 41 lines; the oldest are domain consolidation (132 days), Supabase MCP org (112), the Resend key blocker (109) | **ASK-ZACH which to re-verify.** These are live-system claims (Vercel, Supabase, Resend) that only a live read can settle; a re-verify is cheap per item but touches accounts. Proposal: re-verify the 3 oldest now with the read-only MCP calls each memory names. |

## False-positive shapes (dropped from the scan in this PR)

- Example paths in docs (`public/foo/index.html`): left in the scan's output but never
  proposed; judged by hand.
- Rename detection on generic file names (`index`, `route`, `page`, `README`, `package`)
  matched unrelated files; now excluded, and a rename must stay in the same top folder.
- Ignored or local-only paths (`operators/.venv`, `.claude/worktrees`): real on Zach's disk,
  absent in a fresh worktree. Next tightening: check the main checkout's disk too.

## Not done

1. `_PATTERNS`, `_DECISIONS` and the remaining slices (about 70 dead cites, 66 stale dates).
2. The other repos (arcs-care-local, perplexity-mcp): only if this pass earns it.
3. Contradictions between docs (the same fact two ways). Not mechanical; it needs the
   `dream-scout` reading pairs that share a subject.
