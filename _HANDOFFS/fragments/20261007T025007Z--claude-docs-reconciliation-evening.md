<!--
session: claude-docs-reconciliation-evening (same session as 20261006T183213Z, resumed)
branch: claude/docs-reconciliation-next-06852d (worked from worktree orchestration-repo-cleanup-6f304f)
head: acd41a12
created_at: 2026-10-07T02:50:07Z
-->
> **Docs Reconciliation, evening round (2026-10-06): defaults approved, Librarian calibrated, lattice re-authored, ADR → Queue fixed. 5 tracker rows remain "needs a decision", all yours.** Continues fragment `20261006T183213Z--claude-docs-reconciliation-orchestration`. Tracker: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm; Issues are the source of truth.

## Goal / true north
Finish the judgment calls on the tracker with defaults and one-pass rulings, inside Zach's time budget.

## What changed
- **Defaults approved (10-06):** closed adr-citation-linter (stays manual), frontend-design (won't fix), conflicting-prs-811-854 and salvage-recoil-close-pr644 (#811 closed, #854 and #644 merged); parked nftt-index, culture-rescore, reading-room-lexicon; fixed the status-page row. 3 flagged ATS PDFs (aircall, comet, morgan-stanley) moved to Trash; 93 remain. GitHub issues relabelled and closed to match (debt push does not update existing issues).
- **#1050** ADR → Queue fix: multi-line output now uses the heredoc form, so a push touching 2+ ADRs no longer fails the job; template-only change is a no-op. First real multi-ADR push will prove the generate and commit steps.
- **Librarian (Op 21), #1052 + #1060:** picks carry band `likely` (p >= 0.6) or `maybe` (cut in `read-friction-tiers.json`); name-match bonus 0.2 (key-rotation memory now pick 3); take loop skips an unpayable item instead of stopping. All three knobs rest on 11 labelled picks (tentative). Still absent: `project_todd_hotes_prl_resins` on the strict-gate query (labelled useful). SAGE query returns 11 maybes.
- **Claim unit v1, #1054:** PROPOSED amendment in `runtime/specs/operator-25-shavasana-v0.md` (bullet or sentence instead of section). Same handoff scores 0.89 (section) vs 0.47 (claim). The confidence function exists only on closed PR #598's branch (`claude/zen-pasteur-85c635`).
- **Lattice, #1062:** eng, kai, echo (true to gate), lat, om re-authored; last_reviewed 2026-10-06; lattice_drift_check fresh. 23 other non-ok nodes not individually verified; hpipe unchecked.
- **Old Anthropic key, local files:** `arcs-v9/.env`, `~/.hermes/.env`, `arcs-care-local/.env.local` now hold the new key (fingerprint matches `.env.local`; hermes probe OK). Not touched: `~/.vercel/.env.preview.local` (auto-pulled), Vercel arcs-care and arcs production keys (last updated 131 and 134 days ago), GitHub arcs-care secret. `~/arcs/.env.local` and `~/question-compass/.env.local` hold valid keys of unknown org.
- **Sessions archived (harvested, clean):** Issues-as-SSOT, receipt-efficacy, DeFi review, plus six earlier. PM application session NOT archived: 2 untracked files (`_ARTIFACTS/forge-nous-hermes-pm/` resume + cover HTML).

## Current state
- main tip `acd41a12`; CI on it still running at handoff (the prior tip `4a05a4b2` passed). Deploy of the latest commits unconfirmed.
- Open PRs: #730 draft, #557 better-sqlite3 major.
- Tracker "needs a decision" now 5 rows: confidence-claim-unit-v1, lattice-regenerate, og-image-unfurl-check, old-anthropic-account, write-lock-adr-085.

## Decisions made
- Approve defaults; keep adr_cite_lint manual; Librarian: sample first, then bands, then name bonus 0.2 then loop fix; trash the 3 ATS PDFs; apply the lattice evidence table as a PR; stay in one session.

## Open decisions (waiting on Zach)
1. **Claim unit v1:** adopt (series breaks), keep v0, or run both. Adoption also needs the confidence function re-landed.
2. **Lattice:** kai status (aspirational vs partial); what the lat "100 receipts" gate counts (total about 267 vs external 10).
3. **og:image:** which of the 72 static subdomain pages should unfurl (they have no og or twitter tags).
4. **Old keys:** update Vercel arcs-care and arcs (production, check Preview/Development), GitHub arcs-care secret, then revoke the old key in the old org console. Check ~/arcs and ~/question-compass keys' org.
5. **ADR-085 about 2026-10-13:** accept and decide step 3 (default `--lock`) together.
6. PM session files: commit or keep local, then archive it. Also still open from the earlier fragment: 7 SECRETLY-DONE backlog rows (`backlog_ripeness.py --apply-closes`), disable frontend-design plugin at the stale clone (optional).

## Open (other)
1. Merge-train speedup: `changes` job treats scripts/ and .github/ as app code, so Python-only PRs wait about 8 minutes on fe-smoke. Restrict app code to src/, public/, prisma/, tests/, package files, next.config.
2. no-squash check failed 18:33Z on `1d4b35d3`, cause not diagnosed (local rerun only flagged unfetched merge commits).
3. Librarian: more labelled picks; todd_hotes miss; the maybe volume on broad queries.
4. status.arcs.care module mapping and a stale-number check; baseline-only-shrinks check; debt sync needs an update step.
5. hpipe lattice node: do stages 1-2 have a runtime representation? Unchecked.
6. Earlier fragment's list still stands (Actions cost measurement, ADR citation spot checks, cheap adds, fewer-permission-prompts, FieldOS explorer, Supabase billing).

## Next action
Confirm CI and the Vercel deploy are green on main `acd41a12`, then clear the 5 decision rows with Zach.

## Cold-start recipe
- Tracker link above (filter "Needs a decision"); `python3 scripts/release_notes.py --since 2026-10-06` for what landed.
- Librarian: `python3 operators/arcs_librarian.py "<query>" --stakes medium`; knobs live in `runtime/specs/read-friction-tiers.json`.
- Merge path: `scripts/merge_train.sh --lock --yes <PRs>` (refuses any PR with a failed or cancelled check; re-run stale reds first).
