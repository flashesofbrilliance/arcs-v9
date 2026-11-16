# Handoff to the PR 2034 session (branch claude/louisville-brooks-send-9dcc6b)

From the contract-work session, 2026-11-05. Zach ruled the narrow page canonical for the Brooks send.

**Canonical source:** `/Users/zharris/arcs-v9/.claude/worktrees/contract-work-applied-ai-cf1cde/_ARTIFACTS/brooks-audit-onepager.html`.
The send copy beside it, `brooks-audit-onepager.send.html`, is the same page with comments stripped.
Both files are untracked in the contract-work worktree. The email-safe body is in `brooks-audit-onepager-DRAFT.md`.

**What it replaces:** the 11-05 "A second opinion on your AI tools" copy on your branch (head 6d0eb5de).
That copy brings back five errors that were fixed on 11-04:
1. "$20,000 of bags": he meant 20,000 bags, not dollars.
2. A "We agreed" sunk-cost row: those were Zach's words, not Brooks's.
3. "You said your team can build these tools themselves": "it" was the audit.
4. "I check whether the trend ... has peaked": the audit checks his criteria, it does not compete with it.
5. "Forecast": his word was "simulation."

**State of the canonical page:**
- It was rebuilt to Zach's bar: narrow, specific, no pressure, value first.
- It went through the counterpart gauntlet, run wf_e463aed1-61d, and all 14 verified fixes are applied apart from the four left for Zach.
- `artifact_wrap_lint` is clean.
- `page_gate --counterpart --matrix full` passes.
- There are no em-dashes.

**Asks for you (your branch, your call on mechanics):**
1. Port the canonical page onto your branch. Keep your US Letter print stylesheet. The page has its own `@media print` rule that shows all three adobo cases, so merge the two print rules rather than dropping one.
2. Re-cut the PDF and check that page 1 shows all three adobo cases.
3. Re-run the repo gates on your branch.
4. The backlog row `brooks-audit-proposal-send` still holds on Jeben's read. Jeben's draft carries the old copy, so it needs the new page.

**Left for Zach, not for either session:**
- Rewriting the Gmail draft `r-8072641161534280614`: subject, ask and body. The narrow page's close is "tell me where adobo stands."
- An access line (no logins, no copies).
- A stop-after-kickoff clause.
- Deleting the stale 11-04 drafts.
- The superseding ex-ante receipt, filed at send.
