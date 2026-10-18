<!--
session: claude-handoff-public-claim-fix
branch: claude/handoff-public-claim-fix
head: 37d66c79
created_at: 2026-10-18T00:19:35Z
-->
> ### Shavasana — handoff pause, 2026-10-17 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
> 
> - **Exhale** (what went out): 2 commits, 1 merges to main (scope: branch claude/zealous-grothendieck-73e154), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 2 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 5 / dissent 2 (ratio 1.67) → OK: dissent present.
> - **Cold re-read (canary on the draft draft.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> 
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: every claim kept; each cites a PR, commit, receipt id or deploy id. Somatic: not asked. Disposition: release.

> Removed false "public repo / public commit trail" claims (arcs-v9 and perplexity-mcp are private) from resumes, ATS copies, forge pages, notes and served public/ pages; added a pre-commit gate; merged PR 1300 on local gates; deploy verified live.

## Goal / true north
No outward-facing resume or page calls the ARCS repo or commit trail public; the wording is "live app (app.arcs.care), commit history and traces on request".

## What changed
- PR 1300 merged with --merge (`6d51bd3b`), about 60 files: forge-* resumes, ATS html/txt, page.html, TAILOR-NOTES, recoil-schriner, resume-blacksmith, vico-vp-wargame, and served public/ pages (vico, schriner, squad, blacksmith, success-academy, growth-ai, mercury, sentilink).
- New `scripts/public_claim_gate.py`, wired into `scripts/git-hooks/pre-commit`; allows germinate, rosetta-shell, resume-tailor-skill, arcs-skills. Proven fail-on-bad (caught a stale norm-ai ATS txt) and pass-on-good.
- Receipts: 2026-10-17--public-claim-fix-pr1300--ZH and 2026-10-17--public-claim-fix-deploy-verify--ZH (the first could not be updated, UPDATE was declined, so the second records the deploy check).
- Vercel dpl_qqH5EGXkXMGCqPkhxyA7PnwyvEiJ READY from 6d51bd3b; vico-resume, blacksmith-resume, squad-resume live with new wording.

## Current state
- Merged on local gates; CI changes and gates failed in 3 s (Actions billing block).
- 3 of 8 edited public/ pages fetched live; forge-* not served.

## Decisions made
- Zach: merge on local gates; add a second receipt row instead of editing the first.

## Open decisions (waiting on Zach)
1. Zach: which resumes or PDFs were already sent (monday, oxenham, blacksmith, others); sent copies still say "public" and need a corrected re-send.
2. Zach: whether status.arcs.care shows commits; its "live commit trail" footers on forge page.html files were left as is.

## Open (other)
1. Fix Actions spending limit so CI runs again.

## Next action
Zach names the sent resumes so corrected copies can be prepared.

## Cold-start recipe
`python3 scripts/public_claim_gate.py $(git ls-files '_ARTIFACTS/*/*resume*' '_ARTIFACTS/*/page.html' 'public/*resume*')` should exit 0.
