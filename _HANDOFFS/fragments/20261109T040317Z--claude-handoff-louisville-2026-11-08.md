<!--
session: claude-handoff-louisville-2026-11-08
branch: claude/handoff-louisville-2026-11-08
head: d4d064cc
created_at: 2026-11-09T04:03:17Z
-->
### Shavasana — handoff pause, 2026-11-08 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 1 commits, 1 merges to main (scope: branch claude/allowlist-read-only-batch), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: manifesto (exhale, no inhale).
- **Sycophancy check**: agreement 7 / dissent 1 (ratio 3.5) → OK: dissent present.
- **Cold re-read (canary on the draft handoff-frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

- Attachment release: every claim cites a PR, merge sha, receipt id or file; kept. "Production deploy not checked" stays unconfirmed. Somatic: not asked. Disposition: release.

> Louisville proposal session, 2026-11-06 to 11-08: the build pipeline and PDF gate landed, the PDF was redesigned from the page's own parts, and the page was rewritten audit-first with a give/get time trade. Plus side work: a plain-verb /catalog table, backlog routing at induction, a sanity-check agent, an allowlist batch, and the main checkout moved onto origin/main.

## Goal
Get Brooks Thomas (CMO, Louisville Brands) a proposal that answers his own ask: an outside audit of the arc of their AI build. Then Zach sends it.

## Changed
- #2054 merged (`b0609c04`): `scripts/proposal_build.py` and the PDF checks in `page_gate.py`; receipt 2026-11-06--proposal-build-pipeline-pr2054--ZH
- #2062 merged (`6e12621e`): PDF redesign (cover with contents line, running header and footer, numbered sections); receipt 2026-11-08--louisville-pdf-design-pr2062--ZH
- #2064 merged (`ed76a041`): the three-part rule planted, then echoed on the RFP engine card; receipt 2026-11-08--louisville-rfp-tie-in-pr2064--ZH
- #2069 merged (`ca47d910`): give/get grid, trimmed list, H2 sections, audit-first rewrite through two decisions; receipt 2026-11-08--louisville-audit-first-give-get-pr2069--ZH
- #2082 merged (`d4d064cc`): read-only allowlist batch; receipt 2026-11-08--allowlist-read-only-batch-pr2082--ZH (job_id NULL, no backlog row)
- Child sessions: #2065 /catalog plain-verb table (`0807af01`), #2067 backlog rows need a route and a trigger (`b66b5bce`), #2079 sanity-check agent (`64796b29`), #2083 sanity-check sample 1 (`c37e0334`); each filed its own receipt.
- The main checkout was moved to detached origin/main (`d4d064cc`). Its four edits are saved on local branch `backup/main-checkout-wip-2026-11-08`.

## State
- louisville.arcs.care/proposal and its PDF (3 pages) are on main, behind a passcode. The production deploy and the live gated page were not checked by Claude.
- Page shape: cover subtitle in Brooks's words, then the questions grid, then "The two decisions" (technical, business; Brooks picks), the five deliverables, the give/get grid (kickoff 60, screen-share 90, readout 60, optional 45) and the $5,000 card at 50/50.
- Memory updated: project_brooks_thomas_louisville_brands (state 2026-11-08), payment-terms-new-vs-existing-clients, preflight-local-ci-deps-ask-to-open-orbstack (no silent fails).

## Decisions
- Zach: audit first. Adobo is one example decision, not the subject, because leading with it read as a disconnect from his ask.
- Zach: two decisions, one technical and one business ("decisions, not phone calls").
- Zach: no Justin session and no security session in the give list; the optional call is staffed by Brooks.
- Zach: keep 50/50 for Brooks. Default terms by size: about $2K or under 100% up front, larger fixed fee 50/50, multi-month monthly.
- Zach: no tiers or second lane on the page until a receipt exists (the Jeben-era tiers stay air-gapped).
- myAlly asks typed here by mistake went to the Sync MyAlly hub session (PR 2059 owner).

## Open
1. Zach: send Brooks the link, with the passcode in a separate message; delete stale Gmail drafts.
2. Zach: file the ex-ante receipt at send, scope line "two decisions, $5K, no tiers until a receipt".
3. Zach: check the live gated page and PDF after deploy.
4. Sanity-check agent has 1 of 3 fresh samples; run it before any future proposal polish round.
5. Open backlog rows from the verb table: decompose-page-atomic-params, catalog-verb-table-drift-check.

## Next action
Zach sends the Brooks link and files the ex-ante receipt at send.

## Cold-start
- Read memory project_brooks_thomas_louisville_brands (State 2026-11-08 block).
- Source: `_ARTIFACTS/louisville-proposal/source.html`. Build: `python3 scripts/proposal_build.py --louisville`. Gate: `python3 scripts/page_gate.py --counterpart public/louisville-proposal.html public/louisville-proposal.pdf`.
- Before any merge: `docker info`, then `scripts/safe_merge.sh <pr> <head-sha>`; show hook output and confirm the new HEAD after each commit.
